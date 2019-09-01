"""
df_utils.py
~~~~~~~~~~~~~~~
This module contains utilities used to check spreadsheet, dataframe properties
or to accommodate reading of different spreadsheet files
"""

import os
import fleep
import pandas as pd
import re


def is_file_ext_xl(file_path: str) -> bool:
    with open(file_path, 'rb') as file:
        info = fleep.get(file.read(128))
    if info.extension_matches('xlsx'):
        return True


def get_file_name_ext(file_name: str, ext: str) -> bool:
    if file_name.rsplit('.')[-1].lower() == ext:
        return True
    else:
        return False

def read_spreadsheet(file_path: str, idx_cols: list = None,
                     use_cols: int = None) -> pd.DataFrame:
    if is_file_ext_xl(file_path):
        return pd.read_excel(file_path, index_col=idx_cols, usecols=use_cols)
    elif get_file_name_ext(file_name=file_path, ext='csv'):
        return pd.read_csv(file_path, index_col=idx_cols, usecols=use_cols)
    else:
        raise TypeError(
            'Only Excel and CSV types supported. File given: {}'.format(file_path))

def get_col_names(file_path: str) -> list:
    return list(read_spreadsheet(file_path=file_path).columns)

def is_df_cols_matching(file_path_1: str, file_path_2: str) -> bool:
    if get_col_names(file_path_1) == get_col_names(file_path_2):
        return True
    else:
        raise pd.errors.ParserError(
            """Mismatch between columns of the dataframes given. These probably 
            are not similar query outputs. Check the dataframe arguments."""
        )

if __name__ == "__main__":
    pass
