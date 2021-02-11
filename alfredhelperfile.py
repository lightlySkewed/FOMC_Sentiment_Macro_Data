import pandas as pd
import numpy as np
import datetime as dt

def find_new_vintage_percent_chg(dframe1, FOMC_date_list, column_A_name='lag', column_B_name='coincident', annualize_pct_chg=0, pct_chg_year_ago=0):
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
    for col in dframe1:
        i = dframe1.columns.get_loc(col)
        if i > 0:
            col_last_index = dframe1.iloc[:, i].last_valid_index()
            prev_col_last_index = dframe1.iloc[:, i - 1].last_valid_index()
            if col_last_index < prev_col_last_index:
                dframe1.drop(columns=col, inplace = True)

    # export dframe1 to csv
    # dframe1.to_csv('dframe1.csv')
    
    # create a list to store associated column dates 
    temp_coin_column_dates_list = []
    
    # for each FOMC meeting
    for meet in FOMC_date_list:
        
        # clear list after previous iteration
        temp_coin_column_dates_list.clear()
        
        # create a list to store associated column dates for the second loop
        temp_prev_column_dates_list = []
        
        # capture the FRED column prefix including '_'
        FRED_prefix = dframe1.columns[-1][:len(dframe1.columns[-1])-len(dframe1.columns[-1][-8:])]
        
        # find the vintages before the current meeting
        for col in dframe1.columns:
            
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
        last_coincident_index = dframe1[coincident_col_ref].last_valid_index()
        
        # find the last value of the data preceeding the meeting
        last_coincident_value = dframe1[coincident_col_ref].loc[last_coincident_index]
        
        # find the date index's index integer value 
        last_coincident_index_int = dframe1.index.get_loc(last_coincident_index)
        
        # find the preceeding observation's int index value
        if pct_chg_year_ago == 0:
            prev_coincident_index_int = last_coincident_index_int - 1
        elif pct_chg_year_ago == 1:
            prev_coincident_index_int = last_coincident_index_int - 12
        
        # find the second to last value of the data immediately preceeding the meeting
        prev_coincident_value = dframe1[coincident_col_ref].iloc[prev_coincident_index_int]
        
        # find the lagged coincident index
        if pct_chg_year_ago == 0:
            lag_coincident_index_int = prev_coincident_index_int - 1
        elif pct_chg_year_ago == 1:
            lag_coincident_index_int = prev_coincident_index_int - 12
        
        #grab the lagged value of the coincident column
        lag_coincident_value = dframe1[coincident_col_ref].iloc[lag_coincident_index_int]
        
        # calculate the percent change in the variable immediately preceeding the meeting
        if annualize_pct_chg == 0:
            coincident_percent_change = (last_coincident_value - prev_coincident_value)/prev_coincident_value*100
        elif annualize_pct_chg == 1:
            coincident_percent_change = (last_coincident_value - prev_coincident_value)/prev_coincident_value*100*4        
        elif annualize_pct_chg == 2:
            coincident_percent_change = (last_coincident_value - prev_coincident_value)/prev_coincident_value*100*12
        
        # calculate the lagged percent change
        if annualize_pct_chg == 0:
            coincident_lag_percent_change = (prev_coincident_value - lag_coincident_value)/lag_coincident_value*100
        elif annualize_pct_chg == 1:
            coincident_lag_percent_change = (prev_coincident_value - lag_coincident_value)/lag_coincident_value*100*4
        elif annualize_pct_chg == 2:
            coincident_lag_percent_change = (prev_coincident_value - lag_coincident_value)/lag_coincident_value*100*12
        
        # append meeting and coincident percent change to coincident_results dict
        coincident_results[meet] = coincident_percent_change
        
        # append meeting and lagged percent change to previous_results dict
        previous_results[meet] = coincident_lag_percent_change
        

    # combine results into a single dataframe
    results = pd.DataFrame({column_A_name:pd.Series(previous_results),column_B_name:pd.Series(coincident_results)})
    
    # return dataframe
    return results

def find_log_pct_chg_gdps(gdp_frame, pot_gdp_frame, FOMC_date_list, column_A_name='gdp', column_B_name='pot'):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    
    # take the natural log of both real gdp and real potential gdp
    gdp_frame = (np.log(gdp_frame))
    pot_gdp_frame = (np.log(pot_gdp_frame))
    
    # create a dictionary to store the conincident vintages' percent changes
    gdp_results = {}
    
    # create a dictionary to store the previous vintages' percent changes
    pot_gdp_results = {}
    
    # create a dataframe to store and return the results
    rDf = pd.DataFrame(index=FOMC_date_list)
    
    # remove benchmark revisions where last observation is left uncalculated/ unreported
    # for example, see GDPC1 from FRED, 20031210 vintage, last obs ~07/01/2003 
    for col in gdp_frame:
        # get location of current column
        i = gdp_frame.columns.get_loc(col)
        # if it isn't the first column
        if i > 0:
            # find the index of the current column's last observation
            col_last_index = gdp_frame.iloc[:, i].last_valid_index()
            # find the index of the previous column's last observation
            prev_col_last_index = gdp_frame.iloc[:, i - 1].last_valid_index()
            # if the current column is shorter than the previous column
            if col_last_index < prev_col_last_index:
                # drop the current column
                gdp_frame.drop(columns=col, inplace = True)
    
    for col in pot_gdp_frame:
        # get location of current column
        i = pot_gdp_frame.columns.get_loc(col)
        # if it isn't the first column
        if i > 0:
            # find the index of the current column's last observation
            col_last_index = pot_gdp_frame.iloc[:, i].last_valid_index()
            # find the index of the previous column's last observation
            prev_col_last_index = pot_gdp_frame.iloc[:, i - 1].last_valid_index()
            # if the current column is shorter than the previous column
            if col_last_index < prev_col_last_index:
                # drop the current column
                pot_gdp_frame.drop(columns=col, inplace = True)
                    

    # create a list to store associated column dates 
    temp_gdp_column_dates_list = []
    temp_pot_gdp_column_dates_list = []

    # capture the FRED column prefix including '_'
    gdp_FRED_prefix = gdp_frame.columns[-1][:len(gdp_frame.columns[-1])-len(gdp_frame.columns[-1][-8:])]
    pot_gdp_FRED_prefix = pot_gdp_frame.columns[-1][:len(pot_gdp_frame.columns[-1])-len(pot_gdp_frame.columns[-1][-8:])]
    
    # for each FOMC meeting
    for meet in FOMC_date_list:
        
        # clear list after previous iteration
        temp_gdp_column_dates_list.clear()
        temp_pot_gdp_column_dates_list.clear()
        
        # find the gdp vintages before the current meeting
        for col in gdp_frame.columns:
                          
            # capture the date of the column being referenced as a datetime
            col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')
            
            # if the current column's date is before the meeting's date
            if col_date < meet:

                # add the column date to a temporary list of column dates
                temp_gdp_column_dates_list.append(col_date)
                
        # find the pot gdp vintages before the current meeting
        for col in pot_gdp_frame.columns:
                          
            # capture the date of the column being referenced as a datetime
            col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')
            
            # if the current column's date is before the meeting's date
            if col_date < meet:

                # add the column date to a temporary list of column dates
                temp_pot_gdp_column_dates_list.append(col_date)

        # find the largest date in the temporary list. this should be the date of the vintage that immediately preceeds the meeting being referenced
        gdp_vintage = max(temp_gdp_column_dates_list)
        pot_gdp_vintage = max(temp_pot_gdp_column_dates_list)

        # construct the name of the appropriate FRED data column
        gdp_col_ref = gdp_FRED_prefix + dt.datetime.strftime(gdp_vintage, '%Y%m%d')
        pot_gdp_col_ref = pot_gdp_FRED_prefix + dt.datetime.strftime(pot_gdp_vintage, '%Y%m%d')
        
        # find the date index of the last non-missing observation in the GDP vintage
        last_valid_gdp_index = gdp_frame[gdp_col_ref].last_valid_index()
        
        # find the date index's index integer value 
        last_valid_gdp_index_int = gdp_frame.index.get_loc(last_valid_gdp_index)        
        
        # find the last value of real gdp and real potential gdp preceeding the meeting
        # prev_valid_gdp_value = gdp_frame[gdp_col_ref].iloc[last_valid_gdp_index_int - 1]
        last_valid_gdp_value = gdp_frame[gdp_col_ref].iloc[last_valid_gdp_index_int]
        # prev_valid_pot_gdp_value = pot_gdp_frame[pot_gdp_col_ref].iloc[last_valid_gdp_index_int - 1]
        last_valid_pot_gdp_value = pot_gdp_frame[pot_gdp_col_ref].iloc[last_valid_gdp_index_int]
        # vintage_output_gap = last_valid_gdp_value - last_valid_pot_gdp_value
      
        # append meeting and coincident percent change to gdp_results dict
        gdp_results[meet] = last_valid_gdp_value
        
        # append meeting and lagged percent change to pot_gdp_results dict
        pot_gdp_results[meet] = last_valid_pot_gdp_value
        
    # combine results into a single dataframe
    results = pd.DataFrame({column_A_name:pd.Series(pot_gdp_results),column_B_name:pd.Series(gdp_results)})
    
    return results