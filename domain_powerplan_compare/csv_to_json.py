# -*- coding: ISO-8859-1 -*-

import collections
import unicodedata
import os.path
import csv

STRING_ENCODING = 'ISO-8859-1'
INVALID_CHARS = [
    '\xc3\xaf', 'xc2\xbb', '\xc2\xbf'
]


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


def create_os_details_dict(os_file: str, comp_file: str) -> dict:
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

    with open(os_file, 'r', encoding=STRING_ENCODING) as f:
        reader = csv.DictReader(f, fieldnames=os_field_names)
        next(reader)
        for row in reader:
            if row['ORDER_SENTENCE_ID'] != '':
                order_sent_id = int(float(row['ORDER_SENTENCE_ID']))
                oe_field = row['ORDER_ENTRY_FIELD']
                oe_field_display_value = row['OE_FIELD_DISPLAY_VALUE']
                
            else:
                continue

            if order_sent_id not in details_dict.keys():
                details_dict[order_sent_id] = {}

            details_dict[order_sent_id][oe_field] = oe_field_display_value

    with open(comp_file, 'r', encoding=STRING_ENCODING) as f:
        reader = csv.DictReader(f)
        for row in reader:
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

    return details_dict


def csv_to_json(order_sentence_file: str, order_comment_file: str) -> dict:
    """
    Conversion of CSV to dictionary/JSON for sequenced PowerPlans and clinical
    category

    :param order_sentence_file:
    :param order_comment_file:

    :return:
    """
    output_dict = collections.defaultdict()
    details_dict = create_os_details_dict(os_file=order_sentence_file,
                                          comp_file=order_comment_file)
    field_names = [
        'POWERPLAN_DESCRIPTION', 'PHASE', 'PLAN_DISPLAY_METHOD',
        'PHASE_DISPLAY_METHOD', 'SEQUENCE', 'DCP_CLIN_CAT',
        'DCP_CLIN_SUB_CAT', 'BGCOLOR_RED', 'BGCOLOR_GREEN',
        'BGCOLOR_BLUE', 'COMPONENT', 'TARGET_DURATION',
        'START_OFFSET', 'LINK_DURATION_TO_PHASE', 'REQUIRED_IND',
        'INCLUDE_IND', 'CHEMO_IND', 'CHEMO_RELATED_IND',
        'PERSISTENT_IND', 'ORDER_SENTENCE_SEQ', 'ORDER_SENTENCE_ID',
        'ORDER_COMMENT'
    ]

    with open(order_comment_file, 'r', encoding=STRING_ENCODING) as f:
        reader = csv.DictReader(f, fieldnames=field_names)
        next(reader)
        for row in reader:
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
            target_duration = row['TARGET_DURATION']
            start_offset = row['START_OFFSET']
            link_duration_to_phase = row['LINK_DURATION_TO_PHASE']
            required_ind = row['REQUIRED_IND']
            include_ind = row['INCLUDE_IND']
            chemo_ind = row['CHEMO_IND']
            chemo_related_ind = row['CHEMO_RELATED_IND']
            persistent_ind = row['PERSISTENT_IND']
            if row['ORDER_SENTENCE_ID'] is not None:
                order_sentence_id = int(float(row['ORDER_SENTENCE_ID']))
            else:
                order_sentence_id = 0
            if row['ORDER_SENTENCE_SEQ'] is not None:
                sent_seq = int(row['ORDER_SENTENCE_SEQ'].strip())
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
                    'bgcolor_red': bgcolor_red,
                    'bgcolor_green': bgcolor_green,
                    'bgcolor_blue': bgcolor_blue,
                    'order_sentences': []
                })

                component_idx = -1

            sent_list = comp_dict[component_idx].get('order_sentences')

            sentence_idx = find_key_val_idx_in_list(
                lst=sent_list, key='sequence', value=sent_seq
            )

            order_sentence_details = details_dict.get(order_sentence_id)

            if sentence_idx is None and order_sentence_id > 0:
                sent_list.append({
                    'sequence': sent_seq,
                    'order_sentence_id': order_sentence_id,
                    'order_sentence_details': order_sentence_details
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
    component_path = os.path.join(data_path, 'HN_comp_b0783.csv')
    a = csv_to_json(order_sentence_file=order_sentence_path,
                    order_comment_file=component_path)
