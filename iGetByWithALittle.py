import pandas as pd
import datetime as dt

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

def find_new_vintage_percent_chg(dframe, FOMC_date_list, column_A_name='lag', column_B_name='coincident', annualize_pct_chg=0):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    # create a dictionary to store the conincident vintages' percent changes
    coincident_results = {}
    
    # create a dictionary to store the previous vintages' percent changes
    previous_results = {}
    
    # create a dataframe to store and return the results
    rDf = pd.DataFrame(index=FOMC_date_list)
    
    # remove benchmark revisions where last observation is left uncalculated
    # for example, see GDPC1 from FRED, 20031210 vintage, last obs ~07/01/2003 
    for col in dframe:
        i = dframe.columns.get_loc(col)
        if i > 0:
            col_last_index = dframe.iloc[:, i].last_valid_index()
            prev_col_last_index = dframe.iloc[:, i - 1].last_valid_index()
            if col_last_index < prev_col_last_index:
                dframe.drop(columns=col, inplace = True)

        # export dframe to csv
    dframe.to_csv('dframe.csv')
    
    # create a list to store associated column dates 
    temp_coin_column_dates_list = []
    
    # for each FOMC meeting
    for meet in FOMC_date_list:
        
        # clear list after previous iteration
        temp_coin_column_dates_list.clear()
        
        # create a list to store associated column dates for the second loop
        temp_prev_column_dates_list = []
        
        # capture the FRED column prefix including '_'
        FRED_prefix = dframe.columns[-1][:len(dframe.columns[-1])-len(dframe.columns[-1][-8:])]
        
        # find the vintages before the current meeting
        for col in dframe.columns:
            
            # capture the date of the column being referenced as a datetime
            col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')

            # # if the current column's date is before the meeting's date
            if col_date < meet:

                # # add the column date to a temporary list of column dates
                temp_coin_column_dates_list.append(col_date)

        # find the largest date in the temporary list. this should be the date of the vintage that immediately preceeds the meeting being referenced
        coincident_vintage = max(temp_coin_column_dates_list)
        
        # construct the name of the appropriate FRED data column
        coincident_col_ref = FRED_prefix + dt.datetime.strftime(coincident_vintage, '%Y%m%d')
        
        # find the date index of the last non-missing 
        last_coincident_index = dframe[coincident_col_ref].last_valid_index()
        
        # find the last value of the data preceeding the meeting
        last_coincident_value = dframe[coincident_col_ref].loc[last_coincident_index]
        
        # find the date index's index integer value 
        last_coincident_index_int = dframe.index.get_loc(last_coincident_index)
        
        # find the preceeding observation's int index value
        prev_coincident_index_int = last_coincident_index_int - 1
        
        # find the second to last value of the data immediately preceeding the meeting
        prev_coincident_value = dframe[coincident_col_ref].iloc[prev_coincident_index_int]
        
        # calculate the percent change in the variable immediately preceeding the meeting
        coincident_percent_change = (last_coincident_value - prev_coincident_value)/prev_coincident_value*100
        
        # append meeting and coincident percent change to coincident_results dict
        coincident_results[meet] = coincident_percent_change
        
        # for each column in the dataframe
        for col in dframe.columns:
            
            # find the last valid index of the current column
            int_loc_of_columns_last_index = dframe.index.get_loc(dframe[col].last_valid_index())
            
            # if the last valid integer index of the current column is equal to one less than the 
            # last valid integer index of the coincident column, then
            if int_loc_of_columns_last_index == last_coincident_index_int - 1:
                
                # capture the date of the column being referenced as a datetime
                col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')
            
                # append the date to a temporary list
                temp_prev_column_dates_list.append(col_date)
                
        # find the maximum date of this list
        previous_vintage = max(temp_prev_column_dates_list)
        
        # construct the name of the appropriate previous FRED data column
        previous_col_ref = FRED_prefix + dt.datetime.strftime(previous_vintage, '%Y%m%d')
        
        # find the last valid index of the appropriate previous FRED data column
        last_previous_index = dframe[previous_col_ref].last_valid_index()
        
        # find the last valid integer index of the appropriate previous FRED data column
        last_previous_index_int = dframe.index.get_loc(last_previous_index)
        
        # find the second to last valid integer index of the appropriate previous FRED data column
        prev_previous_index_int = last_previous_index_int - 1

        # find the last value of the previous data preceeding the meeting
        last_previous_value = dframe[previous_col_ref].loc[last_previous_index]
        
        # grab the second-to-last value of the column referenced above
        prev_previous_value = dframe[previous_col_ref].iloc[prev_previous_index_int]
        
        # calculate the percent change in the values
        prev_percent_change = (last_previous_value - prev_previous_value)/prev_previous_value*100

        # save the value to the 'previous' dict
        previous_results[meet] = prev_percent_change

        # print("Meeting Date: ", meet)
        # print("Coincident Percent Change: ", coincident_percent_change)
        # print("Previous Percent Change: ", prev_percent_change)

    # combine results into a single dataframe
    results = pd.DataFrame({column_A_name:pd.Series(previous_results),column_B_name:pd.Series(coincident_results)})
    
    # return dataframe
    return results


# find index of any dict item in EPU_dict
def find_index_in_Excel_File_dict(dic):
    for key in dic.keys():
        if key[0:7]=='Vintage':
            df_ind = dic[key].index
    return df_ind