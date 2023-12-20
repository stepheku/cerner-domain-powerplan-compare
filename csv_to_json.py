# -*- coding: ISO-8859-1 -*-

import collections
import unicodedata
import os.path
import csv
import pandas as pd
from pathlib import Path

STRING_ENCODING = 'cp437'


def find_key_val_idx_in_list(lst, key, value):
    """
    Returns the list index of a list of dictionaries, given its value
    :param lst:
    :param key:
    :param value:
    :return:
    """
    for i, dic in enumerate(lst):
        if not lst:
            return None
        elif dic.get(key) == value:
            return i


def return_csv_or_xl_to_df(s: str, n: list=None) -> pd.DataFrame:
    str_path = Path(s)
    if "CSV" in str_path.suffix.upper():
        df = pd.read_csv(str_path, encoding=STRING_ENCODING, header=0)
    elif "XLSX" in str_path.suffix.upper():
        df = pd.read_excel(str_path, dtype=d)

    df.fillna("", inplace=True)

    return df


def create_os_details_dict(os_file: str, comp_file: str, os_filter_file: str=None) -> dict:
    """
    Creates order sentence details dictionary to be embedded in
    another dictionary

    :param os_file: order sentence file path
    :param comp_file: powerplan component file path
    :return: dictionary
    """

    details_dict = collections.OrderedDict()
    os_field_names = ['ORDER_SENTENCE_ID', 'OE_FIELD_DISPLAY_VALUE',
                      'ORDER_ENTRY_FIELD']

    os_file_num_fields = ['ORDER_SENTENCE_ID']
    reader = return_csv_or_xl_to_df(os_file, n=os_file_num_fields)
    for _, row in reader.iterrows():
        if row['ORDER_SENTENCE_ID'] != '':
            order_sent_id = row['ORDER_SENTENCE_ID']
            oe_field = row['ORDER_ENTRY_FIELD']
            oe_field_display_value = row['OE_FIELD_DISPLAY_VALUE']

        else:
            continue

        if order_sent_id not in details_dict.keys():
            details_dict[order_sent_id] = {}

        details_dict[order_sent_id][oe_field] = oe_field_display_value
    

    reader = return_csv_or_xl_to_df(comp_file)
    for _, row in reader.iterrows():
        if row['ORDER_SENTENCE_ID']:
            order_sentence_id = int(float(row['ORDER_SENTENCE_ID']))
        else:
            order_sentence_id = 0
        if row['ORDER_COMMENT']:
            order_comment = row['ORDER_COMMENT']
        else:
            order_comment = ''
        if order_sentence_id in details_dict:
            details_dict[order_sentence_id]['order_comments'] = order_comment


    if os_filter_file is not None:
        reader = return_csv_or_xl_to_df(os_filter_file)
        for _, row in reader.iterrows():
            order_sent_id = int(float(row['ORDER_SENTENCE_ID']))
            if order_sent_id not in details_dict:
                continue
            for k, v in row.items():
                if k.endswith("VALUE") and float(v) > 0:
                    details_dict[order_sent_id][k] = str(float(v.strip()))
                elif k.endswith("DISPLAY") and v:
                    details_dict[order_sent_id][k] = v

    return details_dict


def csv_to_json(order_sentence_file: str, order_comment_file: str, os_filter_file: str=None) -> dict:
    """
    Conversion of CSV to dictionary/JSON for sequenced PowerPlans and clinical
    category

    :param order_sentence_file:
    :param order_comment_file:

    :return:
    """
    output_dict = collections.defaultdict()
    details_dict = create_os_details_dict(os_file=order_sentence_file,
                                          comp_file=order_comment_file,
                                          os_filter_file=os_filter_file)
    with open(order_comment_file, "r", encoding=STRING_ENCODING) as f:
        reader = csv.DictReader(f)
        row = next(reader)
        field_names = list(row.keys())
    

    with open(order_comment_file, 'r', encoding=STRING_ENCODING, newline="") as f:
        reader = csv.DictReader(f, fieldnames=field_names)
        next(reader)
        for idx, row in enumerate(reader):
            powerplan = row['POWERPLAN_DESCRIPTION']

            if not powerplan:
                continue

            phase = row['PHASE']
            powerplan_display_method = row['PLAN_DISPLAY_METHOD']
            phase_display_method = row['PHASE_DISPLAY_METHOD']
            dcp_clin_cat = row['DCP_CLIN_CAT']
            dcp_clin_sub_cat = row['DCP_CLIN_SUB_CAT']
            sequence = int(row['SEQUENCE'].strip())
            bgcolor_red = row['BGCOLOR_RED']
            bgcolor_green = row['BGCOLOR_GREEN']
            bgcolor_blue = row['BGCOLOR_BLUE']
            synonym = row['COMPONENT']
            iv_synonym = row.get("IV_COMPONENT")
            orderable_type_flag = int(float(row.get("ORDERABLE_TYPE_FLAG")))
            target_duration = row['TARGET_DURATION']
            start_offset = row['START_OFFSET']
            link_duration_to_phase = row['LINK_DURATION_TO_PHASE']
            required_ind = row['REQUIRED_IND']
            include_ind = row['INCLUDE_IND']
            chemo_ind = row['CHEMO_IND']
            chemo_related_ind = row['CHEMO_RELATED_IND']
            persistent_ind = row['PERSISTENT_IND']
            linking_rule = row.get("LINKING_RULE")
            linking_rule_quantity = row.get("LINKING_RULE_QUANTITY")
            linking_rule_flag = row.get("LINKING_RULE_FLAG")
            linking_override_reason = row.get("LINKING_OVERRIDE_REASON")
            assigned_dots = row.get("ASSIGNED_DOTS")

            if row['ORDER_SENTENCE_ID'] is not None:
                order_sentence_id = int(float(row['ORDER_SENTENCE_ID']))
            else:
                order_sentence_id = 0
            if row['ORDER_SENTENCE_SEQ'] is not None and row['ORDER_SENTENCE_SEQ']:
                sent_seq = int(float(row['ORDER_SENTENCE_SEQ'].strip()))
            else:
                sent_seq = 0

            if powerplan not in output_dict:
                output_dict[powerplan] = {
                    'display_method': powerplan_display_method,
                    'phases': {}
                }

            phase_dict = output_dict.get(powerplan).get('phases')

            if not phase:
                phase = powerplan
                phase_display_method = powerplan_display_method

            if phase not in phase_dict:
                phase_dict[phase] = {
                    'phase_display_method': phase_display_method,
                    'components': []
                }

            comp_dict = phase_dict.get(phase).get('components')

            component_idx = find_key_val_idx_in_list(
                lst=comp_dict, key='sequence', value=sequence
            )

            if component_idx is None:
                comp_dict.append({
                    'synonym': synonym,
                    'orderable_type_flag': orderable_type_flag,
                    'dcp_clin_cat': dcp_clin_cat,
                    'dcp_clin_sub_cat': dcp_clin_sub_cat,
                    'sequence': sequence,
                    'target_duration': target_duration,
                    'start_offset': start_offset,
                    'link_duration_to_phase': link_duration_to_phase,
                    'required_ind': required_ind,
                    'include_ind': include_ind,
                    'chemo_ind': chemo_ind,
                    'chemo_related_ind': chemo_related_ind,
                    'persistent_ind': persistent_ind,
                    'linking_rule': linking_rule,
                    'linking_rule_quantity': linking_rule_quantity,
                    'linking_rule_flag': linking_rule_flag,
                    'linking_override_reason': linking_override_reason,
                    'assigned_dots': assigned_dots,
                    'bgcolor_red': bgcolor_red,
                    'bgcolor_green': bgcolor_green,
                    'bgcolor_blue': bgcolor_blue,
                    'order_sentences': []
                })

                component_idx = -1

            sent_list = comp_dict[component_idx].get('order_sentences')

            # sentence_idx = find_key_val_idx_in_list(
            #     lst=sent_list, key='sequence', value=sent_seq
            # )

            order_sentence_details = details_dict.get(order_sentence_id)

            if order_sentence_id > 0:
                sent_list.append({
                    'sequence': sent_seq,
                    'order_sentence_id': order_sentence_id,
                    'order_sentence_details': order_sentence_details,
                    'iv_synonym': iv_synonym
                })

                sentence_idx = -1

    # TODO: Refactor this to have a domain key and a powerplans key that
    # will hold the powerplans dictionary
    if 'b0783' in order_comment_file.lower():
        domain = 'b0783'
    elif 'p0783' in order_comment_file.lower():
        domain = 'p0783'

    output = dict()
    output['domain'] = domain
    output['powerplans'] = output_dict

    return output


def sort_dict_by_key(d: dict) -> collections.OrderedDict:
    """
    Sorts a dictionary by key
    :param d: Dictionary
    :return: Returns an OrderedDict
    """
    return collections.OrderedDict(
        {
            k: v for k, v in sorted(d.items())
        }
    )


if __name__ == "__main__":
    """
    Test run
    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_path, 'data')
    order_sentence_path = os.path.join(data_path, 'os_detail_b0783.csv')
    component_path = os.path.join(data_path, 'ONCP_comp_b0783.csv')
    order_sentence_filter_path = os.path.join(data_path, 'os_filter_b0783.csv')
    a = csv_to_json(order_sentence_file=order_sentence_path,
                    order_comment_file=component_path,
                    os_filter_file=order_sentence_filter_path)
    print("")