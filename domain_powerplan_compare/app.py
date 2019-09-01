import argparse
import pandas as pd
import re
import ast
from deepdiff import DeepDiff
import domain_powerplan_compare.utils.df_diff_transform as df_diff_transform
import domain_powerplan_compare.utils.df_utils as df_utils
import domain_powerplan_compare.utils.add_del_rename as add_del_rename


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


output_file = input('Output file name (CSV format): ')
if not output_file:
    output_file = 'output.csv'

# if __name__ == "__main__":
args = parse_arguments()
if df_utils.is_df_cols_matching(args.spreadsheet_1, args.spreadsheet_2):
    cols = df_utils.get_col_names(args.spreadsheet_1)
# idx_cols = prompt_column_nums(cols)
idx_cols = [0, 2, 9, 12]
df1 = df_utils.read_spreadsheet(args.spreadsheet_1)
df2 = df_utils.read_spreadsheet(args.spreadsheet_2)

# TODO:
# Catch PowerPlans that don't exist between domains (removed or added to dictionary)
# detect any name changes

# b domain
protocol_d1, pplan_d1 = add_del_rename.get_protocol_code_dict_from_df(df1)
# TODO: Need to create dict that goes from [PowerPlan]: [Protocol code]
# pplan_to_protocol_d1
pplan_set_1 = add_del_rename.get_pplan_set_from_df(
    df1, 'POWERPLAN_DESCRIPTION')
#c domain
protocol_d2, pplan_d2 = add_del_rename.get_protocol_code_dict_from_df(df2)
pplan_set_2 = add_del_rename.get_pplan_set_from_df(
    df2, 'POWERPLAN_DESCRIPTION')
# pplan_to_protocol_d2

# U- redesignated protocols
renamed_protocols = add_del_rename.get_redesignated_uprotocols(
    set_1=set(protocol_d1.keys()), set_2=set(protocol_d2.keys())
)

# TODO: RESULT: U- redesignated powerplans, to be on the final output
# PowerPlans that are affected by a U-redesignation and to be checked
plans_to_del = add_del_rename.get_pplan_del_list(renamed_protocols,
                                                 protocol_d1, protocol_d2)

pplan_set_1, pplan_set_2 = add_del_rename.remove_list_ele_from_sets(
    plans_to_del, pplan_set_1, pplan_set_2
)

df1, df2 = add_del_rename.filter_pplan_list_from_df('POWERPLAN_DESCRIPTION',
                                                    plans_to_del, df1, df2)

df1, df2 = add_del_rename.filter_pplan_list_from_df('POWERPLAN_DESCRIPTION',
                                                    plans_to_del, df1, df2)

# Exist in set_1/c0783 but not set_2/b0783
exists_1 = pplan_set_1.difference(pplan_set_2)

# Exist in set_1/c0783 but not set_2/b0783
exists_2 = pplan_set_2.difference(pplan_set_1)

# Remove from both dataframes PowerPlans that have issues with
# being in one domain and not the other (add/remove)
df1, df2 = add_del_rename.filter_pplan_list_from_df('POWERPLAN_DESCRIPTION',
                                                    list(
                                                        exists_1.union(exists_2)),
                                                    df1, df2)

# TODO: Reindex dataframes for deepdiff to work
# df.set_index(list(df.columns[[0,2,8]]), inplace=True)
df1.set_index(list(df1.columns[idx_cols]), inplace=True)
df2.set_index(list(df2.columns[idx_cols]), inplace=True)

ddiff = DeepDiff(df1.to_dict(), df2.to_dict(),
                 ignore_order=True, ignore_numeric_type_changes=True)

# values_changed
values_changed_df = pd.DataFrame(ddiff['values_changed']).transpose()
values_changed_df = df_diff_transform.add_parsed_cols_to_df(values_changed_df)
values_changed_df['change_description'] = 'PowerPlan component has been modified'
# TODO: Rename all functions and stuff from "powerplan" to "pplan" for consistency

# PowerPlan component updated or removed
# re.findall(r'root\[\'(.*?)\'\]', ddiff['dictionary_item_added'][2])[0]

powerplan_components_removed = set()
for x in ddiff['dictionary_item_removed']:
    a = ast.literal_eval(re.findall(r'\[(\(.*\))', x)[0])
    # root = re.findall(r'root\[\'(.*?)\'\]', x)[0]
    # Root is not needed because the field changed is always going to be the
    # same 11 items
    powerplan_components_removed.add(a)

for tup in powerplan_components_removed:
    values_changed_df = values_changed_df.append(
        {
            'old_value': 'exists',
            'powerplan': tup[0],
            'phase': tup[1],
            'sequence': tup[2],
            'order_sent_sequence': tup[3],
            'change_description': 'PowerPlan component exists in one domain and not the other'
        }, ignore_index=True
    )

powerplan_components_added = set()
for x in ddiff['dictionary_item_added']:
    a = ast.literal_eval(re.findall(r'\[(\(.*\))', x)[0])
    powerplan_components_removed.add(a)

for tup in powerplan_components_added:
    values_changed_df = values_changed_df.append(
        {
            'new_value': 'exists',
            'powerplan': tup[0],
            'phase': tup[1],
            'sequence': tup[2],
            'order_sent_sequence': tup[3],
            'change_description': 'PowerPlan component exists in one domain and not the other'
        }, ignore_index=True
    )

values_changed_df.sort_values(
    ['powerplan', 'phase', 'sequence', 'order_sent_sequence'], inplace=True)

values_changed_df.to_excel('output.xlsx')
