#define helper functions for FOMC Paper Project
def find_target_columns(dframe, target_start_char, target_end_char, target):
    '''returns a list of columns containing a target in the column name'''
    cols_list = []
    for cols in dframe.columns:
        if type(target) == str:
            if cols[target_start_char:target_end_char] == target:
                cols_list.append(cols)
        elif type(target) == int:
            if int(cols[target_start_char:target_end_char]) >= target:
                cols_list.append(cols)
    return cols_list

def find_new_obs_percent_chg(dframe, starting_column, annualize_pct_chg=0):
    '''returns a list of percent change values from vintage levels'''
    results = [0,]
    
    for col in dframe.columns[starting_column:]:
        
        curr_col_loc = dframe.columns.get_loc(col)
        curr_col_len = dframe[dframe.columns[curr_col_loc]].count()
        prev_col_len = dframe[dframe.columns[curr_col_loc-1]].count()
    
        if curr_col_len > prev_col_len:

            last_obs_index = dframe[col].last_valid_index()
            last_obs_loc = dframe[col].index.get_loc(last_obs_index)
            last_obs_value = dframe[col].iloc[last_obs_loc]
            prev_obs_value = dframe[col].iloc[last_obs_loc - 1]
            #print("If Pass: ", j)
            #print("Column:", curr_col_loc)
            #print("Last Observation Val = ", last_obs_value)
            #print("Prev Observation Val = ", prev_obs_value)
            if annualize_pct_chg == 0:
                quarterly_percent_change = (last_obs_value-prev_obs_value)/prev_obs_value*100
            elif annualize_pct_chg == 1:
                quarterly_percent_change = (last_obs_value-prev_obs_value)/prev_obs_value*100*4
            results.append(quarterly_percent_change)
        
    return results
    
# find index of any dict item in EPU_dict
def find_index_in_Excel_File_dict(dic):
    for key in dic.keys():
        if key[0:7]=='Vintage':
            df_ind = dic[key].index
    return df_ind