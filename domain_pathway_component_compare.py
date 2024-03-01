import pandas as pd
import json
from pathlib import Path
from utils import find_component_idx_in_list
from utils import find_component_seq_in_list
import constants
import lcs
import tab_sep_file_to_json
import argparse

SCRIPT_PATH = Path(__file__).parent
EXCLUDED_SEQ_COMP_FIELDS = ["sequence", "dcp_clin_cat", "dcp_clin_sub_cat"]
EXCLUDED_CLIN_CAT_COMP_FIELDS = ["sequence"]


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a", type=str, default=None, help="folder name that contains domain 1 spreadsheets"
    )

    parser.add_argument(
        "-b", type=str, default=None, help="folder name that contains domain 2 spreadsheets"
    )

    return parser.parse_args()

def main(comp_dict_1: dict, comp_dict_2: dict):

    # Debugging: Loading dictionaries from a JSON file just so we don't have to wait each time
    # with open(Path(SCRIPT_PATH, "BLDIH.json")) as f:
    #     comp_dict_1 = json.load(f)
    # with open(Path(SCRIPT_PATH, "c3034.json")) as f:
    #     comp_dict_2 = json.load(f)

    # comp_dict_1 = xlsx_to_json.main(input_folder_path=Path(SCRIPT_PATH, "data", args.a))
    # comp_dict_2 = xlsx_to_json.main(input_folder_path=Path(SCRIPT_PATH, "data", args.b))

    domain_1 = comp_dict_1.get("domain")
    domain_2 = comp_dict_2.get("domain")

    output_list = []
    """
    Output list dictionary element:
    {
        "PowerPlan": powerplan,
        "Phase": phase,
        "Clinical Category/Sub-Category": value
        "Component": component,
        "Component Seq": 0,
        "Key": key,
        domain_1: value,
        domain_2: value,
        "Additional_Comments": str
    }
    """

    missing_powerplans = {
        f"in_{domain_1}_not_{domain_2}": [
            x
            for x in comp_dict_1["seq_powerplans"].keys()
            if x not in comp_dict_2["seq_powerplans"].keys()
        ],
        f"in_{domain_2}_not_{domain_1}": [
            x
            for x in comp_dict_2["seq_powerplans"].keys()
            if x not in comp_dict_1["seq_powerplans"].keys()
        ],
    }

    for k, v in missing_powerplans.items():
        for x in v:
            if f"in_{domain_1}" in k:
                domain_1_val = x
                domain_2_val = ""
            elif f"in_{domain_2}" in k:
                domain_1_val = ""
                domain_2_val = x
            output_list.append(
                {
                    "PowerPlan": x,
                    "Phase": "",
                    "Clinical Category/Sub-Category": None,
                    "Component": "",
                    "Component Seq": None,
                    "Key": "",
                    domain_1: domain_1_val,
                    domain_2: domain_2_val,
                    "Additional_Comments": constants.MISSING_POWERPLAN,
                }
            )


    # Remove the PowerPlans that don't exist
    # I'm not going to use set().difference just because that method won't let me know
    # which domain the PowerPLan exists in and which it doesn't
    [
        comp_dict_1["seq_powerplans"].pop(k, None)
        for k in [x for v in missing_powerplans.values() for x in v]
    ]

    [
        comp_dict_2["seq_powerplans"].pop(k, None)
        for k in [x for v in missing_powerplans.values() for x in v]
    ]

    # TODO: Check parent PowerPlan attributes if the description matches


    # Check phases
    # First check that the phase names match
    # levels:
    # - domain_x_powerplan_attr
    #   - domain_x_phase_attr
    #       - domain_x_phase_components_list
    #          - domain_x_comp_attr
    for powerplan, domain_1_powerplan_attr in comp_dict_1.get("seq_powerplans").items():
        domain_2_powerplan_attr = comp_dict_2.get("seq_powerplans").get(powerplan)

        combined_phase_list = lcs.diff_wrapper(
            list(domain_1_powerplan_attr.get("phases").keys()),
            list(domain_2_powerplan_attr.get("phases").keys()),
        )

        if any(x.startswith(("+", "-")) for x in combined_phase_list):
            diff_phases_1 = [x[2:] for x in combined_phase_list if "+" in x[0]]
            diff_phases_2 = [x[2:] for x in combined_phase_list if "-" in x[0]]

            for phase in diff_phases_1:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": "",
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: phase,
                        domain_2: "",
                        "Additional_Comments": constants.PHASE_MISMATCH_OR_MISSING,
                    }
                )
            for phase in diff_phases_2:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": "",
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: "",
                        domain_2: phase,
                        "Additional_Comments": constants.PHASE_MISMATCH_OR_MISSING,
                    }
                )

            # Remove the differing phase names from each dictionaries
            [
                domain_1_powerplan_attr.get("phases").pop(x, None)
                for x in diff_phases_1 + diff_phases_2
            ]
            [
                domain_2_powerplan_attr.get("phases").pop(x, None)
                for x in diff_phases_1 + diff_phases_2
            ]

        # TODO: Check the attributes of PowerPlan phases

        # TODO: Check missing PowerPlan components

        for phase_name, domain_1_phase_attr in domain_1_powerplan_attr.get(
            "phases"
        ).items():
            domain_2_phase_attr = domain_2_powerplan_attr.get("phases").get(phase_name)

            domain_1_phase_components_list = sorted(
                domain_1_phase_attr.get("components"), key=lambda i: i.get("sequence")
            )
            domain_2_phase_components_list = sorted(
                domain_2_phase_attr.get("components"), key=lambda i: i.get("sequence")
            )
            combined_components_list = lcs.diff_wrapper(
                [x.get("component") for x in domain_1_phase_components_list],
                [x.get("component") for x in domain_2_phase_components_list],
            )

            # Find missing or mismatched components
            if domain_1_phase_components_list != domain_2_phase_components_list:
                domain_1_diff_components = [
                    x[2:] for x in combined_components_list if "+" in x[0]
                ]
                domain_2_diff_components = [
                    x[2:] for x in combined_components_list if "-" in x[0]
                ]
                for component in domain_1_diff_components:
                    output_list.append(
                        {
                            "PowerPlan": powerplan,
                            "Phase": phase_name,
                            "Clinical Category/Sub-Category": None,
                            "Component": "",
                            "Component Seq": find_component_seq_in_list(
                                li=domain_2_phase_components_list, component=component
                            ),
                            "Key": "",
                            domain_1: "",
                            domain_2: component,
                            "Additional_Comments": constants.COMPONENT_MISMATCH_OR_MISSING,
                        }
                    )
                for component in domain_2_diff_components:
                    output_list.append(
                        {
                            "PowerPlan": powerplan,
                            "Phase": phase_name,
                            "Clinical Category/Sub-Category": None,
                            "Component": "",
                            "Component Seq": find_component_seq_in_list(
                                li=domain_1_phase_components_list, component=component
                            ),
                            "Key": "",
                            domain_1: component,
                            domain_2: "",
                            "Additional_Comments": constants.COMPONENT_MISMATCH_OR_MISSING,
                        }
                    )

            # Go through the combined components list so we can compare the component
            # level attributes
            idx_domain_1 = 0
            idx_domain_2 = 0
            if any(combined_components_list):
                for component in combined_components_list:
                    idx_domain_1 = find_component_idx_in_list(
                        li=domain_1_phase_components_list,
                        component=component,
                        start_idx=idx_domain_1,
                    )
                    idx_domain_2 = find_component_idx_in_list(
                        li=domain_2_phase_components_list,
                        component=component,
                        start_idx=idx_domain_2,
                    )
                    if not component:
                        continue
                    # Skip components that are missing or mismatched
                    if component[0] != "+" and component[0] != "-":
                        # Loop through the component-level attributes
                        for attr, val in domain_1_phase_components_list[idx_domain_1].items():
                            # Skip this part of the loop if the field is excluded
                            if attr in EXCLUDED_SEQ_COMP_FIELDS:
                                continue

                            # Skip any key:value pair that is a collection
                            # because we're just looking at true attributes
                            if not isinstance(val, (dict, list)):
                                domain_1_comp_attr = val
                                domain_2_comp_attr = domain_2_phase_components_list[
                                    idx_domain_2
                                ].get(attr)

                                if domain_1_comp_attr != domain_2_comp_attr:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": None,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": attr,
                                            domain_1: domain_1_comp_attr,
                                            domain_2: domain_2_comp_attr,
                                            "Additional_Comments": constants.COMPONENT_ATTR_DIFF,
                                        }
                                    )

                        # Establish the order sentence sorting for an IV set versus non-IV set
                        # Because IV sets can only have 1 order set, sequence by the IV synonym
                        # If not an IV set, go by the order sentence sequence instead
                        if (
                            domain_1_phase_components_list[idx_domain_1].get(
                                "orderable_type_flag"
                            )
                            == 8
                        ):
                            domain_1_order_sentences = sorted(
                                domain_1_phase_components_list[idx_domain_1].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("iv_synonym"),
                            )
                        else:
                            domain_1_order_sentences = sorted(
                                domain_1_phase_components_list[idx_domain_1].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("order_sentence_seq"),
                            )

                        if (
                            domain_2_phase_components_list[idx_domain_2].get(
                                "orderable_type_flag"
                            )
                            == 8
                        ):
                            domain_2_order_sentences = sorted(
                                domain_2_phase_components_list[idx_domain_2].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("iv_synonym"),
                            )
                        else:
                            domain_2_order_sentences = sorted(
                                domain_2_phase_components_list[idx_domain_2].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("order_sentence_seq"),
                            )

                        # TODO: Loop through the order sentences
                        for idx, domain_1_os in enumerate(domain_1_order_sentences):
                            if domain_1_os.get("order_sentence_details") is None:
                                continue
                            else:
                                try:
                                    domain_2_os = domain_2_order_sentences[idx]
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": None,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_2: "",
                                            domain_1: f"order_sentence_sequence: {domain_1_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )
                                    continue

                            for key, domain_1_val in domain_1_os.get(
                                "order_sentence_details"
                            ).items():
                                try:
                                    if (
                                        domain_2_order_sentences[idx].get(
                                            "order_sentence_details", {}
                                        )
                                        is None
                                    ):
                                        domain_2_val = ""
                                    else:
                                        domain_2_val = (
                                            domain_2_order_sentences[idx]
                                            .get("order_sentence_details", {})
                                            .get(key, "")
                                        )

                                    if isinstance(domain_1_val, str) and isinstance(
                                        domain_2_val, str
                                    ):
                                        if domain_1_val.lower() == domain_2_val.lower():
                                            continue

                                        else:
                                            output_list.append(
                                                {
                                                    "PowerPlan": powerplan,
                                                    "Phase": phase_name,
                                                    "Clinical Category/Sub-Category": None,
                                                    "Component": component,
                                                    "Component Seq": find_component_seq_in_list(
                                                        li=domain_1_phase_components_list,
                                                        component=component,
                                                    ),
                                                    "Key": key,
                                                    domain_1: domain_1_val,
                                                    domain_2: domain_2_val,
                                                    "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                                }
                                            )
                                    elif domain_1_val != domain_2_val:
                                        output_list.append(
                                            {
                                                "PowerPlan": powerplan,
                                                "Phase": phase_name,
                                                "Clinical Category/Sub-Category": None,
                                                "Component": component,
                                                "Component Seq": find_component_seq_in_list(
                                                    li=domain_1_phase_components_list,
                                                    component=component,
                                                ),
                                                "Key": key,
                                                domain_1: domain_1_val,
                                                domain_2: domain_2_val,
                                                "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                            }
                                        )
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": None,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: f"order_sentence_sequence: {domain_1_os.get('order_sentence_seq')}",
                                            domain_2: "",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )

                        # Look in reverse from domain_2 to domain_1 to look for missing order
                        # sentences
                        for idx, domain_2_os in enumerate(domain_2_order_sentences):
                            if domain_2_os.get("order_sentence_details") is None:
                                continue
                            else:
                                try:
                                    domain_1_os = domain_1_order_sentences[idx]
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": None,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: "",
                                            domain_2: f"order_sentence_sequence: {domain_2_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )
                                    continue

                            for key, domain_2_val in domain_2_os.get(
                                "order_sentence_details"
                            ).items():
                                try:
                                    if (
                                        domain_1_order_sentences[idx].get(
                                            "order_sentence_details", {}
                                        )
                                        is None
                                    ):
                                        domain_1_val = ""
                                    else:
                                        domain_1_val = (
                                            domain_1_order_sentences[idx]
                                            .get("order_sentence_details", {})
                                            .get(key)
                                        )

                                    if isinstance(domain_1_val, str) and isinstance(
                                        domain_2_val, str
                                    ):
                                        if domain_1_val.lower() == domain_2_val.lower():
                                            continue

                                        else:
                                            output_list.append(
                                                {
                                                    "PowerPlan": powerplan,
                                                    "Phase": phase_name,
                                                    "Clinical Category/Sub-Category": None,
                                                    "Component": component,
                                                    "Component Seq": find_component_seq_in_list(
                                                        li=domain_1_phase_components_list,
                                                        component=component,
                                                    ),
                                                    "Key": key,
                                                    domain_1: domain_1_val,
                                                    domain_2: domain_2_val,
                                                    "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                                }
                                            )
                                    elif domain_1_val != domain_2_val:
                                        output_list.append(
                                            {
                                                "PowerPlan": powerplan,
                                                "Phase": phase_name,
                                                "Clinical Category/Sub-Category": None,
                                                "Component": component,
                                                "Component Seq": find_component_seq_in_list(
                                                    li=domain_1_phase_components_list,
                                                    component=component,
                                                ),
                                                "Key": key,
                                                domain_1: domain_1_val,
                                                domain_2: domain_2_val,
                                                "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                            }
                                        )
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": None,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: "",
                                            domain_2: f"order_sentence_sequence: {domain_2_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )

        # TODO: Check missing PowerPlan component attributes


    # Clinical Category PowerPlans
    missing_powerplans = {
        f"in_{domain_1}_not_{domain_2}": [
            x
            for x in comp_dict_1["clin_cat_powerplans"].keys()
            if x not in comp_dict_2["clin_cat_powerplans"].keys()
        ],
        f"in_{domain_2}_not_{domain_1}": [
            x
            for x in comp_dict_2["clin_cat_powerplans"].keys()
            if x not in comp_dict_1["clin_cat_powerplans"].keys()
        ],
    }

    for k, v in missing_powerplans.items():
        for x in v:
            if f"in_{domain_1}" in k:
                domain_1_val = x
                domain_2_val = ""
            elif f"in_{domain_2}" in k:
                domain_1_val = ""
                domain_2_val = x
            output_list.append(
                {
                    "PowerPlan": x,
                    "Phase": "",
                    "Clinical Category/Sub-Category": None,
                    "Component": "",
                    "Component Seq": None,
                    "Key": "",
                    domain_1: domain_1_val,
                    domain_2: domain_2_val,
                    "Additional_Comments": constants.MISSING_POWERPLAN,
                }
            )


    # Remove the PowerPlans that don't exist
    # I'm not going to use set().difference just because that method won't let me know
    # which domain the PowerPLan exists in and which it doesn't
    [
        comp_dict_1["clin_cat_powerplans"].pop(k, None)
        for k in [x for v in missing_powerplans.values() for x in v]
    ]

    [
        comp_dict_2["clin_cat_powerplans"].pop(k, None)
        for k in [x for v in missing_powerplans.values() for x in v]
    ]

    # TODO: Check parent PowerPlan attributes if the description matches


    # Check phases
    # First check that the phase names match
    # levels:
    # - domain_x_powerplan_attr
    #   - domain_x_phase_attr
    #       - domain_x_phase_components_list
    #          - domain_x_comp_attr
    for powerplan, domain_1_powerplan_attr in comp_dict_1.get(
        "clin_cat_powerplans"
    ).items():
        domain_2_powerplan_attr = comp_dict_2.get("clin_cat_powerplans").get(powerplan)

        combined_phase_list = lcs.diff_wrapper(
            list(domain_1_powerplan_attr.get("phases").keys()),
            list(domain_2_powerplan_attr.get("phases").keys()),
        )

        if any(x.startswith(("+", "-")) for x in combined_phase_list):
            diff_phases_1 = [x[2:] for x in combined_phase_list if "+" in x[0]]
            diff_phases_2 = [x[2:] for x in combined_phase_list if "-" in x[0]]

            for phase in diff_phases_1:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": "",
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: "",
                        domain_2: phase,
                        "Additional_Comments": constants.PHASE_MISMATCH_OR_MISSING,
                    }
                )
            for phase in diff_phases_2:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": "",
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: phase,
                        domain_2: "",
                        "Additional_Comments": constants.PHASE_MISMATCH_OR_MISSING,
                    }
                )

            # Remove the differing phase names from each dictionaries
            [
                domain_1_powerplan_attr.get("phases").pop(x, None)
                for x in diff_phases_1 + diff_phases_2
            ]
            [
                domain_2_powerplan_attr.get("phases").pop(x, None)
                for x in diff_phases_1 + diff_phases_2
            ]

        # TODO: Check the attributes of PowerPlan phases

        # TODO: Check missing PowerPlan components

        for phase_name, domain_1_phase_attr in domain_1_powerplan_attr.get(
            "phases"
        ).items():
            domain_2_phase_attr = domain_2_powerplan_attr.get("phases").get(phase_name)

            # longest common substring will not work here because the clinical
            # categories are not ordered (or they're not ordered based on
            # users in dcptools)
            diff_clin_cat_1 = [
                x for x in domain_1_phase_attr.get("categories").keys() if
                x not in domain_2_phase_attr.get("categories")
            ]

            diff_clin_cat_2 = [
                x for x in domain_2_phase_attr.get("categories").keys() if
                x not in domain_1_phase_attr.get("categories")
            ]

            [
                domain_1_phase_attr.get("categories").pop(x, None)
                for x in diff_clin_cat_1 + diff_clin_cat_2
            ]
            [
                domain_2_phase_attr.get("categories").pop(x, None)
                for x in diff_clin_cat_1 + diff_clin_cat_2
            ]

            for clin_cat in diff_clin_cat_1:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": phase_name,
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: clin_cat,
                        domain_2: "",
                        "Additional_Comments": constants.CLIN_CAT_MISMATCH_OR_MISSING,
                    }
                )
            for clin_cat in diff_clin_cat_2:
                output_list.append(
                    {
                        "PowerPlan": powerplan,
                        "Phase": phase_name,
                        "Clinical Category/Sub-Category": None,
                        "Component": "",
                        "Component Seq": None,
                        "Key": "",
                        domain_1: "",
                        domain_2: clin_cat,
                        "Additional_Comments": constants.CLIN_CAT_MISMATCH_OR_MISSING,
                    }
                )

            for clin_cat in domain_1_phase_attr.get("categories").keys():
                domain_2_phase_attr = domain_2_powerplan_attr.get("phases").get(phase_name)

                domain_1_phase_components_list = sorted(
                    domain_1_phase_attr.get("categories").get(clin_cat),
                    key=lambda i: i.get("sequence"),
                )
                domain_2_phase_components_list = sorted(
                    domain_2_phase_attr.get("categories").get(clin_cat),
                    key=lambda i: i.get("sequence"),
                )
                combined_components_list = lcs.diff_wrapper(
                    [x.get("component") for x in domain_1_phase_components_list],
                    [x.get("component") for x in domain_2_phase_components_list],
                )

                # Find missing or mismatched components
                if domain_1_phase_components_list != domain_2_phase_components_list:
                    domain_1_diff_components = [
                        x[2:] for x in combined_components_list if "+" in x[0]
                    ]
                    domain_2_diff_components = [
                        x[2:] for x in combined_components_list if "-" in x[0]
                    ]
                    for component in domain_1_diff_components:
                        output_list.append(
                            {
                                "PowerPlan": powerplan,
                                "Phase": phase_name,
                                "Clinical Category/Sub-Category": clin_cat,
                                "Component": "",
                                "Component Seq": find_component_seq_in_list(
                                    li=domain_2_phase_components_list, component=component
                                ),
                                "Key": "",
                                domain_1: "",
                                domain_2: component,
                                "Additional_Comments": constants.COMPONENT_MISMATCH_OR_MISSING,
                            }
                        )
                    for component in domain_2_diff_components:
                        output_list.append(
                            {
                                "PowerPlan": powerplan,
                                "Phase": phase_name,
                                "Clinical Category/Sub-Category": clin_cat,
                                "Component": "",
                                "Component Seq": find_component_seq_in_list(
                                    li=domain_1_phase_components_list, component=component
                                ),
                                "Key": "",
                                domain_1: component,
                                domain_2: "",
                                "Additional_Comments": constants.COMPONENT_MISMATCH_OR_MISSING,
                            }
                        )

                # Go through the combined components list so we can compare the component
                # level attributes
                idx_domain_1 = 0
                idx_domain_2 = 0
                for component in combined_components_list:
                    idx_domain_1 = find_component_idx_in_list(
                        li=domain_1_phase_components_list,
                        component=component,
                        start_idx=idx_domain_1,
                    )
                    idx_domain_2 = find_component_idx_in_list(
                        li=domain_2_phase_components_list,
                        component=component,
                        start_idx=idx_domain_2,
                    )
                    if not component:
                        continue
                    # Skip components that are missing or mismatched
                    if component[0] != "+" and component[0] != "-":
                        # Loop through the component-level attributes
                        for attr, val in domain_1_phase_components_list[
                            idx_domain_1
                        ].items():
                            # Skip this part of the loop if the field is excluded
                            if attr in EXCLUDED_SEQ_COMP_FIELDS:
                                continue

                            # Skip any key:value pair that is a collection
                            # because we're just looking at true attributes
                            if not isinstance(val, (dict, list)):
                                domain_1_comp_attr = val
                                domain_2_comp_attr = domain_2_phase_components_list[
                                    idx_domain_2
                                ].get(attr)

                                if domain_1_comp_attr != domain_2_comp_attr:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": clin_cat,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": attr,
                                            domain_1: domain_1_comp_attr,
                                            domain_2: domain_2_comp_attr,
                                            "Additional_Comments": constants.COMPONENT_ATTR_DIFF,
                                        }
                                    )

                        # Establish the order sentence sorting for an IV set versus non-IV set
                        # Because IV sets can only have 1 order set, sequence by the IV synonym
                        # If not an IV set, go by the order sentence sequence instead
                        if (
                            domain_1_phase_components_list[idx_domain_1].get(
                                "orderable_type_flag"
                            )
                            == 8
                        ):
                            domain_1_order_sentences = sorted(
                                domain_1_phase_components_list[idx_domain_1].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("iv_synonym"),
                            )
                        else:
                            domain_1_order_sentences = sorted(
                                domain_1_phase_components_list[idx_domain_1].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("order_sentence_seq"),
                            )

                        if (
                            domain_2_phase_components_list[idx_domain_2].get(
                                "orderable_type_flag"
                            )
                            == 8
                        ):
                            domain_2_order_sentences = sorted(
                                domain_2_phase_components_list[idx_domain_2].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("iv_synonym"),
                            )
                        else:
                            domain_2_order_sentences = sorted(
                                domain_2_phase_components_list[idx_domain_2].get(
                                    "order_sentences"
                                ),
                                key=lambda i: i.get("order_sentence_seq"),
                            )

                        # TODO: Loop through the order sentences
                        for idx, domain_1_os in enumerate(domain_1_order_sentences):
                            if domain_1_os.get("order_sentence_details") is None:
                                continue
                            else:
                                try:
                                    domain_2_os = domain_2_order_sentences[idx]
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": clin_cat,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_2: "",
                                            domain_1: f"order_sentence_sequence: {domain_1_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )
                                    continue

                            for key, domain_1_val in domain_1_os.get(
                                "order_sentence_details"
                            ).items():
                                try:
                                    if (
                                        domain_2_order_sentences[idx].get(
                                            "order_sentence_details", {}
                                        )
                                        is None
                                    ):
                                        domain_2_val = ""
                                    else:
                                        domain_2_val = (
                                            domain_2_order_sentences[idx]
                                            .get("order_sentence_details", {})
                                            .get(key)
                                        )

                                    if isinstance(domain_1_val, str) and isinstance(
                                        domain_2_val, str
                                    ):
                                        if domain_1_val.lower() == domain_2_val.lower():
                                            continue

                                        else:
                                            output_list.append(
                                                {
                                                    "PowerPlan": powerplan,
                                                    "Phase": phase_name,
                                                    "Clinical Category/Sub-Category": clin_cat,
                                                    "Component": component,
                                                    "Component Seq": find_component_seq_in_list(
                                                        li=domain_1_phase_components_list,
                                                        component=component,
                                                    ),
                                                    "Key": key,
                                                    domain_1: domain_1_val,
                                                    domain_2: domain_2_val,
                                                    "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                                }
                                            )
                                    elif domain_1_val != domain_2_val:
                                        output_list.append(
                                            {
                                                "PowerPlan": powerplan,
                                                "Phase": phase_name,
                                                "Clinical Category/Sub-Category": clin_cat,
                                                "Component": component,
                                                "Component Seq": find_component_seq_in_list(
                                                    li=domain_1_phase_components_list,
                                                    component=component,
                                                ),
                                                "Key": key,
                                                domain_1: domain_1_val,
                                                domain_2: domain_2_val,
                                                "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                            }
                                        )
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": clin_cat,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: f"order_sentence_sequence: {domain_1_os.get('order_sentence_seq')}",
                                            domain_2: "",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )

                        # Look in reverse from domain_2 to domain_1 to look for missing order
                        # sentences
                        for idx, domain_2_os in enumerate(domain_2_order_sentences):
                            if domain_2_os.get("order_sentence_details") is None:
                                continue
                            else:
                                try:
                                    domain_1_os = domain_1_order_sentences[idx]
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": clin_cat,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: "",
                                            domain_2: f"order_sentence_sequence: {domain_2_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )
                                    continue

                            for key, domain_2_val in domain_2_os.get(
                                "order_sentence_details"
                            ).items():
                                try:
                                    if (
                                        domain_1_order_sentences[idx].get(
                                            "order_sentence_details", {}
                                        )
                                        is None
                                    ):
                                        domain_1_val = ""
                                    else:
                                        domain_1_val = (
                                            domain_1_order_sentences[idx]
                                            .get("order_sentence_details", {})
                                            .get(key)
                                        )

                                    if isinstance(domain_1_val, str) and isinstance(
                                        domain_2_val, str
                                    ):
                                        if domain_1_val.lower() == domain_2_val.lower():
                                            continue

                                        else:
                                            output_list.append(
                                                {
                                                    "PowerPlan": powerplan,
                                                    "Phase": phase_name,
                                                    "Clinical Category/Sub-Category": clin_cat,
                                                    "Component": component,
                                                    "Component Seq": find_component_seq_in_list(
                                                        li=domain_1_phase_components_list,
                                                        component=component,
                                                    ),
                                                    "Key": key,
                                                    domain_1: domain_1_val,
                                                    domain_2: domain_2_val,
                                                    "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                                }
                                            )
                                    elif domain_1_val != domain_2_val:
                                        output_list.append(
                                            {
                                                "PowerPlan": powerplan,
                                                "Phase": phase_name,
                                                "Clinical Category/Sub-Category": clin_cat,
                                                "Component": component,
                                                "Component Seq": find_component_seq_in_list(
                                                    li=domain_1_phase_components_list,
                                                    component=component,
                                                ),
                                                "Key": key,
                                                domain_1: domain_1_val,
                                                domain_2: domain_2_val,
                                                "Additional_Comments": constants.ORD_SENT_DETAIL_DIFF,
                                            }
                                        )
                                except IndexError:
                                    output_list.append(
                                        {
                                            "PowerPlan": powerplan,
                                            "Phase": phase_name,
                                            "Clinical Category/Sub-Category": clin_cat,
                                            "Component": component,
                                            "Component Seq": find_component_seq_in_list(
                                                li=domain_1_phase_components_list,
                                                component=component,
                                            ),
                                            "Key": "",
                                            domain_1: "",
                                            domain_2: f"order_sentence_sequence: {domain_2_os.get('order_sentence_seq')}",
                                            "Additional_Comments": constants.MISSING_ORD_SENT,
                                        }
                                    )


    # Spit out the final spreadsheet
    pd.DataFrame().from_records(output_list).to_excel("output.xlsx", index=False)


if __name__ == "__main__":
    args = parse_args()

    if not args.a.lower().endswith("json") and not args.b.lower().endswith("json"):
        for path in Path(SCRIPT_PATH, "data", args.a).glob("*.txt"):
            if "comp" in str(path.name):
                A_PLAN_COMPONENTS_PATH = path
            elif "os_detail" in str(path.name):
                A_OS_DETAIL_PATH = path
            elif "os_filter" in str(path.name):
                A_OS_FILTER_PATH = path
            elif "pathway" in str(path.name):
                A_PATHWAY_PATH = path

        for path in Path(SCRIPT_PATH, "data", args.b).glob("*.txt"):
            if "comp" in str(path.name):
                B_PLAN_COMPONENTS_PATH = path
            elif "os_detail" in str(path.name):
                B_OS_DETAIL_PATH = path
            elif "os_filter" in str(path.name):
                B_OS_FILTER_PATH = path
            elif "pathway" in str(path.name):
                B_PATHWAY_PATH = path
    
        comp_dict_a = tab_sep_file_to_json.create_components_dict(
            comp_file_path=A_PLAN_COMPONENTS_PATH,
            os_detail_file_path=A_OS_DETAIL_PATH,
        )

        comp_dict_b = tab_sep_file_to_json.create_components_dict(
            comp_file_path=B_PLAN_COMPONENTS_PATH,
            os_detail_file_path=B_OS_DETAIL_PATH,
        )

    main(comp_dict_1=comp_dict_a, comp_dict_2=comp_dict_b)
