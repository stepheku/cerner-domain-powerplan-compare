# -*- coding: ISO-8859-1 -*-

from pathlib import Path
import csv
import lcs

# this is only needed 
# STRING_ENCODING = "utf_8_sig"
STRING_ENCODING = "cp1252"

REGIMEN_COMP_FIELD_NAMES = [
    "POWERPLAN_BASE_NAME", "REGIMEN_DETAIL_SEQUENCE", "COMPONENT",
    "OFFSET_VALUE", "OFFSET_UNIT", "ANCHOR_ELEMENT",
]


def get_columns_from_csv(file_path: Path) -> list:
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        row = next(reader)
        return list(row.keys())


def csv_to_json(file_path: Path) -> dict:
    """
    Conversion of CSV to dictionary/JSON for sequenced Regimens
    """

    output = {}

    with open(file_path, "r", encoding=STRING_ENCODING) as f:
        columns = get_columns_from_csv(file_path)
        reader = csv.DictReader(f, fieldnames=columns)
        next(reader, None)
        for row in reader:
            regimen = row["REGIMEN"]

            if regimen not in output and regimen:
                output[regimen] = {
                    k: v
                    for k, v in row.items()
                    if not k in REGIMEN_COMP_FIELD_NAMES
                }

                output[regimen]["components"] = {}

            regimen_seq = int(row["REGIMEN_DETAIL_SEQUENCE"])

            if regimen_seq not in output[regimen]["components"] and regimen_seq >= 0:
                output[regimen]["components"][regimen_seq] = {
                    k: v for k, v in row.items()
                    if k in REGIMEN_COMP_FIELD_NAMES
                }

    return output


def compare_key_val(
        d1: dict, d2: dict, regimen_name: str = None, regimen_det_seq: str = None) -> list:

    output = []

    for k, v in d1.items():
        if not isinstance(v, dict) and not k.endswith("_ID"):
            val1 = v
            val2 = d2.get(k)
            if val1 != val2:
                output.append(
                    {
                        "regimen": regimen_name,
                        "key": k,
                        "regimen_detail_sequence": regimen_det_seq,
                        "value1": val1,
                        "value2": val2,
                    }
                )

    return output


def find_regimen_detail_seq_from_component(d: dict, component: str, start_seq=0) -> int:
    for k, v in d.items():
        if v.get("COMPONENT") == component and k >= start_seq:
            return k
    return None


def main():
    script_path = Path(__file__).parent
    b0783 = csv_to_json(Path(script_path, "data", "b0783_regimens.csv"))
    p0783 = csv_to_json(Path(script_path, "data", "p0783_regimens.csv"))

    output = []

    for regimen_desc, regimen_dict in b0783.items():
        b0783_regimen_dict = regimen_dict
        p0783_regimen_dict = p0783.get(regimen_desc)

        if b0783_regimen_dict and p0783_regimen_dict is not None:
            output.extend(compare_key_val(
                d1=b0783_regimen_dict, d2=p0783_regimen_dict))

        elif b0783_regimen_dict and p0783_regimen_dict is None:
            output.append(
                {
                    "regimen": regimen_desc,
                    "key": "Regimen available in one domain, but not the other",
                    "value1": "Present",
                    "value2": "Not present",
                }
            )
            continue

        # Components exist
        if b0783_regimen_dict.get("components"):

            b0783_regimen_comp_dict = b0783_regimen_dict.get("components")
            p0783_regimen_comp_dict = p0783_regimen_dict.get("components")

            b0783_regimen_components = [
                x.get("COMPONENT") for x in b0783_regimen_dict.get("components").values()]
            p0783_regimen_components = [
                x.get("COMPONENT") for x in p0783_regimen_dict.get("components").values()]
            combined_components_list = lcs.diff_wrapper(
                b0783_regimen_components, p0783_regimen_components)
            if b0783_regimen_components != p0783_regimen_components:
                diff_components = [
                    x for x in combined_components_list if "+" in x[0] or "-" in x[0]]
                diff_components_1 = [
                    x for x in combined_components_list if '+' in x[0]]
                diff_components_2 = [
                    x for x in combined_components_list if '-' in x[0]]
                for component in diff_components_1:
                    output.append(
                        {
                            "regimen": regimen_desc,
                            "key": f"Regimen components is missing",
                            "value1": component[1:],
                            "value2": "",
                        }
                    )
                for component in diff_components_2:
                    output.append(
                        {
                            "regimen": regimen_desc,
                            "key": f"Regimen components is missing",
                            "value1": "",
                            "value2": component[1:],
                        }
                    )
            
            idx_b0783 = 0
            idx_p0783 = 0

            for component in [x for x in combined_components_list if not x.startswith("+") and not x.startswith("-")]:
                idx_b0783 = find_regimen_detail_seq_from_component(
                    b0783_regimen_comp_dict, component, idx_b0783)
                idx_p0783 = find_regimen_detail_seq_from_component(
                    p0783_regimen_comp_dict, component, idx_p0783)

                if idx_b0783 is not None and idx_p0783 is not None:
                    for k, v in b0783_regimen_comp_dict.get(idx_b0783).items():
                        b0783_val = v
                        p0783_val = p0783_regimen_comp_dict.get(
                            idx_p0783).get(k)
                        if b0783_val != p0783_val and k != "REGIMEN_DETAIL_SEQUENCE":
                            output.append(
                                {
                                    "regimen": regimen_desc,
                                    "key": k,
                                    "component": component,
                                    "value1": b0783_val,
                                    "value2": p0783_val,
                                }
                            )

                if idx_p0783 is None:
                    idx_p0783 = 0
                
                if idx_b0783 is None:
                    idx_b0783 = 0

    with open("output_domain_regimen_compare.csv", "w", encoding=STRING_ENCODING, newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["regimen", "key",
                           "regimen_detail_sequence", "component", "value1", "value2"]
        )
        writer.writeheader()
        for row in output:
            writer.writerow(row)


if __name__ == "__main__":
    main()