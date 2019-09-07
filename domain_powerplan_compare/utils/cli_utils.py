"""
cli_utils.py
~~~~~~~~~~~~~~~
This module contains utilities used to turn this into a cli utility
"""

import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process a spreadsheet file')
    parser.add_argument('spreadsheet_1', type=str,
                        help='Path to the first (before) spreadsheet file')
    parser.add_argument('spreadsheet_2', type=str,
                        help='Path to the second (after) spreadsheet file')
    return parser.parse_args()


def prompt_column_nums(cols: list, num_of_cols: int = 3) -> list:
    output = ''
    for idx, val in enumerate(cols):
        #print('{}. {}'.format(idx, val))
        if idx % num_of_cols == (num_of_cols - 1):
            output += '{}. {}\n'.format(idx, val)
        else:
            output += '{}. {}\t\t'.format(idx, val).expandtabs(10)
    print(output)
    idx_cols_str = input(
        'Select column numbers for the index (separated by a comma): ')
    return [int(x) for x in idx_cols_str.split(',')]