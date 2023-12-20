from csv_to_json import csv_to_json, find_key_val_idx_in_list
from pathlib import Path
import csv
import lcs
import io
import os
import argparse

STRING_ENCODING = 'utf-8'


def parse_arguments_powerplan_comp_csvs():
    parser = argparse.ArgumentParser(
        description="Process CSV files"
    )

    parser.add_argument('b0783_csv', type=str,
                        help='PowerPlan components and order comments in B0783')
    parser.add_argument('p0783_csv', type=str,
                        help='PowerPlan components and order comments in P0783')

    args = parser.parse_args()

    return args.b0783_csv, args.p0783_csv


def load_files():
    script_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_path, 'data')

    # b0783_component_path, p0783_component_path = \
    # parse_arguments_powerplan_comp_csvs()

    b0783_component_path = os.path.join(data_path, "ONCP_comp_b0783.csv")
    p0783_component_path = os.path.join(data_path, "ONCP_comp_p0783.csv")

    b0783_order_sentence_path = os.path.join(data_path, 'os_detail_b0783.csv')
    p0783_order_sentence_path = os.path.join(data_path, 'os_detail_p0783.csv')

    b0783_order_sentence_filter_path = os.path.join(data_path, 'os_filter_b0783.csv')
    p0783_order_sentence_filter_path = os.path.join(data_path, 'os_filter_p0783.csv')

    p0783 = csv_to_json(order_sentence_file=p0783_order_sentence_path,
                        order_comment_file=p0783_component_path,
                        os_filter_file=p0783_order_sentence_filter_path)
    b0783 = csv_to_json(order_sentence_file=b0783_order_sentence_path,
                        order_comment_file=b0783_component_path,
                        os_filter_file=b0783_order_sentence_filter_path)

    return b0783, p0783


def is_key_val_len_equal(dict_1: dict, dict_2: dict, key: str) -> bool:
    try:
        if len(dict_1.get(key)) != len(dict_2.get(key)):
            return False
    except AttributeError:
        return False
    else:
        return True


def append_to_output_file(s: str):
    with open('output.txt', 'a', newline='\n') as f:
        f.write(s)


def initialize_output_file():
    with open('output.txt', 'w') as f:
        f.write('')


def initialize_csv_file():
    with open('output.csv', 'w', newline='\n') as f:
        headers = ['PowerPlan', 'Phase', 'synonym', 'key', 'val_1', 'val_2']
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()


def find_synonym_idx_in_list(li: list, synonym: str, start_idx=0) -> int:
    """
    Given a list of components, finds given synonym, returns the index
    """
    for idx, comp in enumerate(li):
        if comp.get('synonym') == synonym:
            if start_idx is None:
                return idx
            if idx > start_idx:
                return idx


def append_to_output_csv(s: dict):
    """
    Writes a dictionary to a CSV

    Headers:
        PowerPlan
        Phase
        synonym
        key
        val_1
        val_2
    """
    with open('output.csv', 'a', newline='\n', encoding=STRING_ENCODING) as f:
        headers = ['PowerPlan', 'Phase', 'synonym', 'key', 'val_1', 'val_2']
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
        writer.writerow(s)


def main():
    comp_properties = ['bgcolor_red', 'bgcolor_green', 'bgcolor_blue']
    b0783, p0783 = load_files()
    initialize_output_file()
    initialize_csv_file()

    for powerplan, p0783_powerplan_attr in p0783.get('powerplans').items():
        b0783_powerplan_attr = b0783.get('powerplans').get(powerplan)
        if b0783_powerplan_attr is None:
            append_to_output_csv({
                'PowerPlan': powerplan,
                'Phase': '',
                'synonym': '',
                'key': 'PowerPlan is missing or name has been changed',
                'val_1': '',
                'val_2': '',
            })
            continue

        # Checking number of phases is the same
        if not is_key_val_len_equal(p0783_powerplan_attr, b0783_powerplan_attr, 'phases'):
            print('Mismatch between number of phases in PowerPlan {}'.format(powerplan))

        # Checking phase names is the same
        p0783_phase_names = set(p0783_powerplan_attr.get('phases').keys())
        b0783_phase_names = set(b0783_powerplan_attr.get('phases').keys())
        if p0783_phase_names.difference(b0783_phase_names):
            print('Mismatched names within PowerPlan {}'.format(powerplan))

        for phase in p0783_powerplan_attr.get('phases'):
            p0783_phase_attr = p0783_powerplan_attr \
                .get('phases') \
                .get(phase)
            p0783_components = sorted(p0783_phase_attr.get(
                'components'), key=lambda i: i.get('sequence'))
            b0783_phase_attr = b0783_powerplan_attr \
                .get('phases') \
                .get(phase)
            if b0783_phase_attr is None:
                append_to_output_csv({
                    'PowerPlan': powerplan,
                    'Phase': phase,
                    'synonym': '',
                    'key': 'PowerPlan phase does not exist or has been changed',
                    'val_1': '',
                    'val_2': '',
                })
                continue
            b0783_components = sorted(b0783_phase_attr.get(
                'components'), key=lambda i: i.get('sequence'))

            b0783_synonyms = [x.get('synonym') for x in sorted(
                b0783_components, key=lambda i: i.get('sequence'))]
            p0783_synonyms = [x.get('synonym') for x in sorted(
                p0783_components, key=lambda i: i.get('sequence'))]
            combined_synonym_list = lcs.diff_wrapper(
                b0783_synonyms, p0783_synonyms)
            if b0783_synonyms != p0783_synonyms:
                diff_synonyms = [
                    x for x in combined_synonym_list if '+' in x[0] or '-' in x[0]]
                # print('PowerPlan: {}, Phase: {}, LCS: {}'.format(powerplan, phase,  diff_synonyms))
                diff_synonyms_1 = [
                    x for x in combined_synonym_list if '+' in x[0]]
                diff_synonyms_2 = [
                    x for x in combined_synonym_list if '-' in x[0]]
                for synonym in diff_synonyms_1:
                    append_to_output_csv({
                        'PowerPlan': powerplan,
                        'Phase': phase,
                        'synonym': '',
                        'key': 'Synonym mismatch or missing',
                        'val_1': synonym[1:],
                        'val_2': '',
                    })
                for synonym in diff_synonyms_2:
                    append_to_output_csv({
                        'PowerPlan': powerplan,
                        'Phase': phase,
                        'synonym': '',
                        'key': 'Synonym mismatch or missing',
                        'val_1': '',
                        'val_2': synonym[1:],
                    })
            idx_p0783 = None
            idx_b0783 = None
            for synonym in combined_synonym_list:
                idx_p0783 = find_synonym_idx_in_list(p0783_components, synonym, 
                    idx_p0783)
                idx_b0783 = find_synonym_idx_in_list(b0783_components, synonym,
                    idx_b0783)
                if idx_p0783 is not None and idx_b0783 is not None:
                    for attr, val in p0783_components[idx_p0783].items():
                        if not isinstance(val, (dict, list)):
                            p0783_comp_attr = val
                            b0783_comp_attr = b0783_components[idx_b0783].get(attr)
                            if p0783_comp_attr != b0783_comp_attr and attr not in \
                                ['dcp_clin_cat', 'dcp_clin_sub_cat', 'sequence']:
                                append_to_output_csv({
                                    'PowerPlan': powerplan,
                                    'Phase': phase,
                                    'synonym': synonym,
                                    'key': attr,
                                    'val_1': p0783_comp_attr,
                                    'val_2': b0783_comp_attr,
                                })
                    
                    if p0783_components[idx_p0783].get('orderable_type_flag') == 8:
                        p0783_order_sentences = sorted(p0783_components[idx_p0783].get(
                            'order_sentences'),
                            key=lambda i: i.get('iv_synonym'))
                    else:
                        p0783_order_sentences = sorted(p0783_components[idx_p0783].get(
                            'order_sentences'),
                            key=lambda i: i.get('sequence'))

                    if b0783_components[idx_b0783].get('orderable_type_flag') == 8:
                        b0783_order_sentences = sorted(b0783_components[idx_b0783].get(
                            'order_sentences'),
                            key=lambda i: i.get('iv_synonym'))
                    else:
                        b0783_order_sentences = sorted(b0783_components[idx_b0783].get(
                            'order_sentences'),
                            key=lambda i: i.get('sequence'))

                    for idx, os in enumerate(p0783_order_sentences):
                        if os.get('order_sentence_details') is None:
                            continue
                        for key, val in os.get('order_sentence_details').items():
                            try:
                                if key in ["Difference in Minutes", "Patient's Own Meds", "Adhoc Frequency Instance"]:
                                    continue
                                if b0783_order_sentences[idx].get(
                                    'order_sentence_details', {}) is None:
                                    b0783_val = ""
                                else:
                                    b0783_val = b0783_order_sentences[idx].get(
                                        'order_sentence_details', {}).get(key)
                                if isinstance(val, str) and isinstance(b0783_val, str):
                                    if val.lower() == b0783_val.lower():
                                        continue
                                    else:
                                        append_to_output_csv({
                                            'PowerPlan': powerplan,
                                            'Phase': phase,
                                            'synonym': synonym,
                                            'key': key,
                                            'val_1': val,
                                            'val_2': b0783_val,
                                        })
                                elif val != b0783_val:
                                    append_to_output_csv({
                                        'PowerPlan': powerplan,
                                        'Phase': phase,
                                        'synonym': synonym,
                                        'key': key,
                                        'val_1': val,
                                        'val_2': b0783_val,
                                    })
                            except IndexError:
                                    append_to_output_csv({
                                        'PowerPlan': powerplan,
                                        'Phase': phase,
                                        'synonym': synonym,
                                        'key': 'Missing order sentence',
                                        'val_1': '',
                                        'val_2': '',
                                    })                                

                    # Look in reverse from b0783 to p0783 to see if there are 
                    # missing order sentences
                    for idx, os in enumerate(b0783_order_sentences):
                        if os.get('order_sentence_details') is None:
                            continue
                        else:
                            try:
                                p0783_os = p0783_order_sentences[idx]
                            except IndexError:
                                append_to_output_csv({
                                        'PowerPlan': powerplan,
                                        'Phase': phase,
                                        'synonym': synonym,
                                        'key': 'Missing order sentence',
                                        'val_1': f'order sentence sequence: {os.get("sequence")}',
                                        'val_2': '',
                                    })    
                                continue       
                        for key, val in os.get('order_sentence_details').items():
                            try:
                                if key in ["Difference in Minutes", "Patient's Own Meds", "Adhoc Frequency Instance"]:
                                    continue
                                if p0783_order_sentences[idx].get(
                                    'order_sentence_details', {}) is None:
                                    p0783_val = ""
                                else:
                                    p0783_val = p0783_order_sentences[idx].get(
                                        'order_sentence_details', {}).get(key)
                                if isinstance(val, str) and isinstance(p0783_val, str):
                                    if val.lower() == p0783_val.lower():
                                        continue
                                    else:
                                        append_to_output_csv({
                                            'PowerPlan': powerplan,
                                            'Phase': phase,
                                            'synonym': synonym,
                                            'key': key,
                                            'val_1': p0783_val,
                                            'val_2': val,
                                        })
                                elif val != b0783_val:
                                    append_to_output_csv({
                                        'PowerPlan': powerplan,
                                        'Phase': phase,
                                        'synonym': synonym,
                                        'key': key,
                                        'val_1': p0783_val,
                                        'val_2': val,
                                    })
                            except IndexError:
                                    append_to_output_csv({
                                        'PowerPlan': powerplan,
                                        'Phase': phase,
                                        'synonym': synonym,
                                        'key': 'Missing order sentence',
                                        'val_1': '',
                                        'val_2': '',
                                    })                                


if __name__ == "__main__":
    main()