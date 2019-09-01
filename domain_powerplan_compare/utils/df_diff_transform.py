"""
df_diff_transform.py
~~~~~~~~~~~~~~~
This module helps to transform the dataframes used
"""
import pandas as pd
import ast
import re
from deepdiff import DeepDiff


def df_diff_to_df(df1: pd.DataFrame,
                  df2: pd.DataFrame) -> pd.DataFrame:
    """Takes two pandas dataframes and checks the difference, returned 
    as a dataframe"""
    ddiff = DeepDiff(df1.to_dict(), df2.to_dict(), ignore_order=True)
    if ddiff:
        return pd.DataFrame(ddiff['values_changed'])
    else:
        return
        # TODO: either return another dataframe that says "no changes"
        # or return something else, figure it out


def add_parsed_cols_to_df(df: pd.DataFrame) -> pd.DataFrame:
    # Regex finding parenthesis for powerplan, phase and sequence
    # must be greedy because there are some PowerPlan names
    # that do have parenthesis
    df['field_change'] = df.index.str.extract(
        r'root\[\'(.*?)\'\]', expand=False)
    try:
        df['powerplan'] = df.index.str.extract(
            r'\[(\(.*\))', expand=False).map(lambda x: ast.literal_eval(x)[0])
        df['phase'] = df.index.str.extract(
            r'\[(\(.*\))', expand=False).map(lambda x: ast.literal_eval(x)[1])
        df['sequence'] = df.index.str.extract(
            r'\[(\(.*\))', expand=False).map(lambda x: ast.literal_eval(x)[2])
        df['order_sent_sequence'] = df.index.str.extract(
            r'\[(\(.*\))', expand=False).map(lambda x: ast.literal_eval(x)[3])
    except SyntaxError:
        print('There is an issue with regex parsing into literal_eval')
    return df


def df_diff_transform(df1: pd.DataFrame,
                      df2: pd.DataFrame) -> pd.DataFrame:
    """transforms two versions of a similar dataframe to give a
    dataframe of what columns and values changed"""
    df_diff = df_diff_to_df(df1, df2)
    df_diff = df_diff.transpose()
    return df_diff