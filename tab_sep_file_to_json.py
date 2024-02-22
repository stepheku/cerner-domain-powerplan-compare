from pathlib import Path
import csv
import argparse

STRING_ENCODING = "utf-8"
SCRIPT_PATH = Path(__file__).parent
SUFFIX_FLOAT_COL = "_ID"
SUFFIX_NUM_COL = "_IND"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--data-folder",
        type=str,
        default=None,
        help="folder that contains spreadsheets",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        nargs="?",
        default=None,
        help="output file name",
    )

    return parser.parse_args()


def strip_all_str_in_dict(d: dict) -> dict:
    return {k: v.strip() for k, v in d.items() if "None" not in k}


def convert_num_in_dict(d: dict) -> dict:
    d2 = {}
    for k, v in d.items():
        if k.upper().endswith(SUFFIX_FLOAT_COL):
            d2[k] = float(v)
        elif k.upper().endswith(SUFFIX_NUM_COL):
            d2[k] = int(v)
        else:
            d2[k] = v
    return d2


def create_ord_sent_details_dict(
    os_detail_file_path: Path, comp_file_path: Path
) -> dict:
    os_details_dict = {}

    with open(os_detail_file_path, "r", encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            row = strip_all_str_in_dict(row)
            row = convert_num_in_dict(row)
            order_sentence_id = row.get("ORDER_SENTENCE_ID")
            order_entry_field = row.get("ORDER_ENTRY_FIELD")
            oe_field_display_value = row.get("OE_FIELD_DISPLAY_VALUE")

            if order_sentence_id not in os_details_dict:
                os_details_dict[order_sentence_id] = {}

            os_details_dict[order_sentence_id][
                order_entry_field
            ] = oe_field_display_value

    with open(comp_file_path, "r", encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            row = strip_all_str_in_dict(row)
            row = convert_num_in_dict(row)
            order_sentence_id = row.get("ORDER_SENTENCE_ID")
            order_comment = row.get("ORDER_COMMENT")

            if order_sentence_id not in os_details_dict:
                os_details_dict[order_sentence_id] = {}

            os_details_dict[order_sentence_id]["order_comment"] = order_comment

    return os_details_dict


def create_ord_sent_filters_dict(os_filter_file_path: Path) -> dict:
    os_filters_dict = {}

    with open(os_filter_file_path, "r", encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            row = strip_all_str_in_dict(row)
            row = convert_num_in_dict(row)
            order_sentence_id = row.get("ORDER_SENTENCE_ID")

            if order_sentence_id not in os_filters_dict:
                os_filters_dict[order_sentence_id] = {
                    k.lower(): v
                    for k, v in row.items()
                    if not k.upper().endswith(("_ID", "DOMAIN"))
                }

    return os_filters_dict


def create_components_dict(
    comp_file_path: Path, os_detail_file_path: Path, output_file_path: Path = None
) -> dict:
    output_comp_dict = {
        "seq_powerplans": {},
        "clin_cat_powerplans": {},
    }

    ord_sent_details_dict = create_ord_sent_details_dict(
        os_detail_file_path=os_detail_file_path, comp_file_path=comp_file_path
    )

    with open(comp_file_path, "r", encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            output_comp_dict["domain"] = row["DOMAIN"]
            row = strip_all_str_in_dict(row)
            row = convert_num_in_dict(row)
            powerplan = row["POWERPLAN_DESCRIPTION"]
            phase = row["PHASE"]
            powerplan_display_method = row["PLAN_DISPLAY_METHOD"]
            phase_display_method = row["PHASE_DISPLAY_METHOD"]
            dcp_clin_cat = row["DCP_CLIN_CAT"]
            dcp_clin_sub_cat = row["DCP_CLIN_SUB_CAT"]
            synonym_type = row["SYNONYM_TYPE"]
            sequence = int(row["SEQUENCE"])
            bgcolor_red = row["BGCOLOR_RED"]
            bgcolor_green = row["BGCOLOR_GREEN"]
            bgcolor_blue = row["BGCOLOR_BLUE"]
            component = row["COMPONENT"]
            iv_component = row["IV_COMPONENT"]
            orderable_type_flag = int(row["ORDERABLE_TYPE_FLAG"])
            target_duration = row["TARGET_DURATION"]
            start_offset = row["START_OFFSET"]
            link_duration_to_phase = row["LINK_DURATION_TO_PHASE"]
            required_ind = row["REQUIRED_IND"]
            include_ind = row["INCLUDE_IND"]
            chemo_ind = row["CHEMO_IND"]
            chemo_related_ind = row["CHEMO_RELATED_IND"]
            persistent_ind = row["PERSISTENT_IND"]
            linking_rule = row["LINKING_RULE"]
            linking_rule_quantity = row["LINKING_RULE_QUANTITY"]
            linking_rule_flag = row["LINKING_RULE_FLAG"]
            linking_override_reason = row["LINKING_OVERRIDE_REASON"]
            assigned_dots = row["ASSIGNED_DOTS"]
            order_sentence_id = row["ORDER_SENTENCE_ID"]
            order_sentence_seq = row["ORDER_SENTENCE_SEQ"]

            if phase_display_method in ("Sequenced", "Outcome Intervention") or (
                powerplan_display_method in ("Sequenced", "Outcome Intervention")
                and phase_display_method == ""
            ):
                comp_dict = output_comp_dict["seq_powerplans"]

            elif phase_display_method == "Clinical Category" or (
                powerplan_display_method == "Clinical Category"
                and phase_display_method == ""
            ):
                comp_dict = output_comp_dict["clin_cat_powerplans"]

            if powerplan not in comp_dict:
                comp_dict[powerplan] = {
                    "display_method": powerplan_display_method,
                    "phases": {},
                }

            phases_dict = comp_dict.get(powerplan).get("phases")
            if phase not in phases_dict:
                phases_dict[phase] = {
                    "phase_display_method": phase_display_method,
                }

                phase_dict = phases_dict[phase]

                if phase_display_method in ("Sequenced", "Outcome Intervention") or (
                    powerplan_display_method in ("Sequenced", "Outcome Intervention")
                    and phase_display_method == ""
                ):
                    phase_dict["components"] = []

                elif phase_display_method == "Clinical Category" or (
                    powerplan_display_method == "Clinical Category"
                    and phase_display_method == ""
                ):
                    phase_dict["categories"] = {}

            seq_components_list = phase_dict.get("components")
            clin_cat_categories_dict = phase_dict.get("categories")

            if phase_display_method in ("Sequenced", "Outcome Intervention") or (
                powerplan_display_method in ("Sequenced", "Outcome Intervention")
                and phase_display_method == ""
            ):
                existing_seq_list = [x.get("sequence", 0) for x in seq_components_list]

                if sequence not in existing_seq_list:
                    seq_components_list.append(
                        {
                            "sequence": sequence,
                            "bgcolor_red": bgcolor_red,
                            "bgcolor_green": bgcolor_green,
                            "bgcolor_blue": bgcolor_blue,
                            "synonym_type": synonym_type,
                            "component": component,
                            "orderable_type_flag": orderable_type_flag,
                            "target_duration": target_duration,
                            "start_offset": start_offset,
                            "link_duration_to_phase": link_duration_to_phase,
                            "required_ind": required_ind,
                            "include_ind": include_ind,
                            "chemo_ind": chemo_ind,
                            "chemo_related_ind": chemo_related_ind,
                            "persistent_ind": persistent_ind,
                            "linking_rule": linking_rule,
                            "linking_rule_quantity": linking_rule_quantity,
                            "linking_rule_flag": linking_rule_flag,
                            "linking_override_reason": linking_override_reason,
                            "assigned_dots": assigned_dots,
                            "order_sentences": [],
                        }
                    )

                idx = [
                    idx
                    for idx, x in enumerate(seq_components_list)
                    if x.get("sequence") == sequence
                ][0]

                if order_sentence_id > 0:
                    seq_components_list[idx]["order_sentences"].append(
                        {
                            "order_sentence_seq": order_sentence_seq,
                            "order_sentence_id": order_sentence_id,
                            "iv_synonym": iv_component,
                            "order_sentence_details": ord_sent_details_dict.get(
                                order_sentence_id
                            ),
                        }
                    )

            elif phase_display_method == "Clinical Category" or (
                powerplan_display_method == "Clinical Category"
                and phase_display_method == ""
            ):
                clin_cat_sub = f"{dcp_clin_cat}-{dcp_clin_sub_cat}"
                if clin_cat_sub not in clin_cat_categories_dict:
                    clin_cat_categories_dict[clin_cat_sub] = []

                clin_cat_components_list = clin_cat_categories_dict[clin_cat_sub]

                existing_seq_list = [
                    x.get("sequence", 0) for x in clin_cat_components_list
                ]

                if sequence not in existing_seq_list:
                    clin_cat_components_list.append(
                        {
                            "sequence": sequence,
                            "bgcolor_red": bgcolor_red,
                            "bgcolor_green": bgcolor_green,
                            "bgcolor_blue": bgcolor_blue,
                            "synonym_type": synonym_type,
                            "component": component,
                            "orderable_type_flag": orderable_type_flag,
                            "target_duration": target_duration,
                            "start_offset": start_offset,
                            "link_duration_to_phase": link_duration_to_phase,
                            "required_ind": required_ind,
                            "include_ind": include_ind,
                            "chemo_ind": chemo_ind,
                            "chemo_related_ind": chemo_related_ind,
                            "persistent_ind": persistent_ind,
                            "linking_rule": linking_rule,
                            "linking_rule_quantity": linking_rule_quantity,
                            "linking_rule_flag": linking_rule_flag,
                            "linking_override_reason": linking_override_reason,
                            "assigned_dots": assigned_dots,
                            "order_sentences": [],
                        }
                    )

                idx = [
                    idx
                    for idx, x in enumerate(clin_cat_components_list)
                    if x.get("sequence") == sequence
                ][0]

                if order_sentence_id > 0:
                    clin_cat_components_list[idx]["order_sentences"].append(
                        {
                            "order_sentence_seq": order_sentence_seq,
                            "order_sentence_id": order_sentence_id,
                            "iv_synonym": iv_component,
                            "order_sentence_details": ord_sent_details_dict.get(
                                order_sentence_id
                            ),
                        }
                    )

    if output_file_path is not None:
        import json

        with open(output_file_path, "w") as f:
            json.dump(c, f)

    return output_comp_dict


def create_pathways_dict(pathway_file_path: Path) -> dict:
    pathway_dict = {}

    with open(pathway_file_path, "r", encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            row = strip_all_str_in_dict(row)
            row = convert_num_in_dict(row)

            powerplan = row["DESCRIPTION"]

            if powerplan not in pathway_dict and powerplan:
                pathway_dict[powerplan] = {
                    k.lower(): v
                    for k, v in row.items()
                    if not k.startswith("PHASE") and not k.startswith("DOT")
                }

                pathway_dict[powerplan]["phases"] = {}

            phase = row["PHASE_DESCRIPTION"]

            if phase not in pathway_dict[powerplan]["phases"]:
                pathway_dict[powerplan]["phases"][phase] = {
                    k.lower(): v for k, v in row.items() if k.startswith("PHASE")
                }

                # pathway_dict[powerplan]["phases"][phase]["dots"] = {}

            # dot = row["DOT_DESCRIPTION"]

            # if phase:
            #     if dot not in pathway_dict[powerplan]["phases"][phase]["dots"] and dot:
            #         pathway_dict[powerplan]["phases"][phase]["dots"][dot] = {
            #             k.lower(): v for k, v in row.items() if k.startswith("DOT")
            #         }
    return pathway_dict


if __name__ == "__main__":
    d = create_ord_sent_details_dict(
        os_detail_file_path=Path(SCRIPT_PATH, "data", "c3034", "os_detail_c3034.txt"),
        comp_file_path=Path(SCRIPT_PATH, "data", "c3034", "comp_c3034.txt"),
    )

    f = create_ord_sent_filters_dict(
        os_filter_file_path=Path(SCRIPT_PATH, "data", "c3034", "os_filter_c3034.txt")
    )

    args = parse_args()
    for path in Path(SCRIPT_PATH, "data", args.data_folder).glob("*.txt"):
        if "comp" in str(path.name):
            PLAN_COMPONENTS_PATH = path
        elif "os_detail" in str(path.name):
            OS_DETAIL_PATH = path
        elif "os_filter" in str(path.name):
            OS_FILTER_PATH = path
        elif "pathway" in str(path.name):
            PATHWAY_PATH = path

    c = create_components_dict(
        comp_file_path=PLAN_COMPONENTS_PATH,
        os_detail_file_path=OS_DETAIL_PATH,
    )

    p = create_pathways_dict(
        pathway_file_path=Path(SCRIPT_PATH, "data", "c3034", "pathways_c3034.txt")
    )
