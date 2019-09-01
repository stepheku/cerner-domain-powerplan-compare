"""
add_del_rename.py
~~~~~~~~~~~~~~~
This module helps to track PowerPlan additions, deletions or renames 
(specifically, reversal of U- designation on protocols, such as ULUAVPMTN
to LUAVPMTN)
"""

import re
import pandas as pd


def get_pplan_set_from_df(df: pd.DataFrame, col_name=None) -> set:
    """Given a dataframe, this will create a set of all of the PowerPlan
    names in the dataframe"""
    return set(df[col_name])


def get_protocol_code_dict_from_df(df: pd.DataFrame) -> tuple:
    """Creates a tuple of dictionaries

    dictionary[protocol_code] = [list of powerplan names]
    dictionary[powerplan name] = [protocol_code]
    """
    protocol_code_dict = {}
    pplan_protocol_dict = {}

    powerplan_set = get_pplan_set_from_df(df, 'POWERPLAN_DESCRIPTION')
    for elem in powerplan_set:
        try:
            protocol_code = re.findall(r'ONCP \w{2} ([A-Z]{3,})', elem)[0]
            if not protocol_code_dict.get(protocol_code):
                protocol_code_dict[protocol_code] = [elem]
            else:
                protocol_code_dict.get(protocol_code).append(elem)

            pplan_protocol_dict[elem] = protocol_code

        except IndexError:
            pass

    return (protocol_code_dict, pplan_protocol_dict)


def redesignate_uprotocol_codes(protocol_codes: set = None) -> set:
    """Given a set of protocol codes, reverse the U- designation on protocol
    codes and return a set with the reversed codes (with exception to CAP
    template powerplans)"""
    new_uprotocol_codes = set()
    for elem in protocol_codes:
        if '0' in elem:
            new_uprotocol_codes.add(elem)
        elif elem[0] == 'U':
            new_uprotocol_codes.add(elem[1:])
        else:
            new_uprotocol_codes.add('U{}'.format(elem))
    return new_uprotocol_codes


def get_redesignated_uprotocols(set_1: set, set_2: set) -> list:
    """Given two sets of protocol codes between domains, return which protocols
    have been redesignated between domains (such as from U- to non-U- or
    vice-versa"""
    return list(redesignate_uprotocol_codes(set_2).intersection(set_1).union(
        redesignate_uprotocol_codes(set_1).intersection(set_2)
    )
    )


def remove_dict_keys_from_list(protocol_code_dict: dict,
                               protocol_code_list: list) -> dict:
    """Given a list of protocol codes, and a protocol code dictionary, remove
    the keys in the dictionary from the codes in the list"""
    for elem in protocol_code_list:
        if protocol_code_dict.get(elem):
            protocol_code_dict.pop(elem)
    return protocol_code_dict


def get_pplan_del_list(protocol_code_list: list, *protocol_code_dicts) -> list:
    """Given a list of protocol codes, and protocol code dictionary(ies), obtain
    a list of the PowerPlan names to remove. This will be used on the original 
    dataframes"""
    powerplan_del_list = []
    for d in protocol_code_dicts:
        for elem in protocol_code_list:
            if d.get(elem):
                powerplan_del_list.extend(d.get(elem))
    return powerplan_del_list


def remove_list_ele_from_sets(li: list = None, *sets):
    """Removes elements within a list from multiple sets"""
    for s in sets:
        s -= set(li)
    return tuple(s for s in sets)


def filter_pplan_list_from_df(col_name: str,
                              pplan_list: list, *dataframes) -> tuple:
    """Given a dataframe, column name and a powerplan list, filters out
    powerplans in that dataframe"""
    return (df[~df[col_name].isin(pplan_list)] for df in dataframes)


"""
Notes section:
Stuff to do:
1. Reverse the U- designation of all protocols in a given set/list
2. Given 2 protocol sets between two domains, reversing the U- designation, 
    the intersection between the reversed set and non-reversed set of the 
    reversed domain
3. Given the intersections in both directions, remove those protocols from 
    both dataframes from the two different domains (priority on the user should
    be to properly rename those protocols first before additional checks 
    should be done)
4. Obtain a list of the powerplans that need to be removed from the initial 
    dataframes because they've had their U- designation reversed
5. Remove the list of powerplans to be removed from the original dataframes

4. Since we now have the dataframes without protocols where the U- designation
    was reversed, that means we can find whatever stuff was added or deleted
"""
