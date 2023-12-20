# -*- coding: ISO-8859-1 -*-

from pathlib import Path
import csv

STRING_ENCODING = "utf_8_sig"


def get_columns_from_csv(file_path: Path) -> list:
    with open(file_path, "r", ) as f:
        reader = csv.DictReader(f)
        row = next(reader)
        return list(row.keys())


def csv_to_json(file_path: Path) -> dict:
    """
    Conversion of CSV to dictionary/JSON for sequenced PowerPlans
    """

    output = {}

    with open(file_path, "r", ) as f:
        columns = get_columns_from_csv(file_path)
        reader = csv.DictReader(f, fieldnames=columns)
        next(reader, None)
        for row in reader:
            powerplan = row["DESCRIPTION"]

            if powerplan not in output and powerplan:
                output[powerplan] = {
                    k: v
                    for k, v in row.items()
                    if not k.startswith("PHASE") and not k.startswith("DOT")
                }

                output[powerplan]["phases"] = {}

            phase = row["PHASE_DESCRIPTION"]

            if phase not in output[powerplan]["phases"] and phase:
                output[powerplan]["phases"][phase] = {
                    k: v for k, v in row.items() if k.startswith("PHASE")
                }

                output[powerplan]["phases"][phase]["dots"] = {}

            dot = row["DOT_DESCRIPTION"]

            if phase:
                if dot not in output[powerplan]["phases"][phase]["dots"] and dot:
                    output[powerplan]["phases"][phase]["dots"][dot] = {
                        k: v for k, v in row.items() if k.startswith("DOT")
                    }
    return output


def compare_key_val(
    d1: dict, d2: dict, plan_name: str = None, phase_name: str = None
) -> list:

    output = []

    for k, v in d1.items():
        if not isinstance(v, dict) and not k.endswith("_ID"):
            val1 = v
            val2 = d2.get(k)
            if val1 != val2:
                output.append(
                    {
                        "plan": plan_name,
                        "phase": phase_name,
                        "key": k,
                        "value1": val1,
                        "value2": val2,
                    }
                )

    return output


def main():
    script_path = Path(__file__).parent
    b0783 = csv_to_json(Path(script_path, "data", "b0783_pathway.csv"))
    p0783 = csv_to_json(Path(script_path, "data", "p0783_pathway.csv"))

    output = []

    for plan_desc, plan_dict in b0783.items():
        b0783_plan_dict = plan_dict
        p0783_plan_dict = p0783.get(plan_desc)

        if b0783_plan_dict and p0783_plan_dict is not None:
            output.extend(
                compare_key_val(
                    d1=b0783_plan_dict, 
                    d2=p0783_plan_dict,
                    plan_name=plan_desc,
                )
            )

        else:
            # PowerPlan doesn't exist in the other dictionary, so just skip
            continue

        # Phases exist
        if b0783_plan_dict.get("phases"):
            for phase_desc, phase_dict in b0783_plan_dict.get("phases").items():
                b0783_phase_dict = phase_dict
                p0783_phase_dict = p0783_plan_dict.get("phases").get(phase_desc)

                if b0783_phase_dict and p0783_phase_dict is not None:
                    output.extend(
                        compare_key_val(
                            d1=b0783_phase_dict,
                            d2=p0783_phase_dict,
                            plan_name=plan_desc,
                            phase_name=phase_desc,
                        )
                    )
                    # DOTs exist (phases must exist)
                    if b0783_phase_dict.get("dots"):
                        for dot_desc, dot_dict in b0783_phase_dict.get("dots", {}).items():
                            b0783_dot_dict = dot_dict
                            p0783_dot_dict = p0783_phase_dict.get("dots", {}).get(dot_desc)

                            if b0783_dot_dict and p0783_dot_dict is not None:
                                output.extend(
                                    compare_key_val(
                                        d1=b0783_dot_dict,
                                        d2=p0783_dot_dict,
                                        plan_name=plan_desc,
                                        phase_name=phase_desc,
                                    )
                                )
                            elif b0783_dot_dict and p0783_dot_dict is None:
                                output.append(
                                    {
                                        "plan": plan_desc,
                                        "phase": phase_desc,
                                        "key": f"DOT is missing: {dot_desc}",
                                        "value1": "Exists",
                                        "value2": "Does not exist",
                                    }
                                )
                elif b0783_phase_dict and p0783_phase_dict is None:
                    output.append(
                        {
                            "plan": plan_desc,
                            "phase": phase_desc,
                            "key": f"Phase is missing: {phase_desc}",
                            "value1": "Exists",
                            "value2": "Does not exist",
                        }
                    )


    with open("output_pathway_compare.csv", "w", encoding=STRING_ENCODING, newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["plan", "phase", "key", "value1", "value2"]
        )
        writer.writeheader()
        for row in output:
            writer.writerow(row)


if __name__ == "__main__":
    main()