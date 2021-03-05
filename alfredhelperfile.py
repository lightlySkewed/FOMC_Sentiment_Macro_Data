import pandas as pd
import numpy as np
import datetime as dt
import statsmodels.formula.api as smf

def find_new_vintage_percent_chg(dframe1, FOMC_date_list, column_A_name='lag', column_B_name='coincident'):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    # create a dictionary to store the conincident vintages' percent changes
    coincident_results = {}
    
    # create a dictionary to store the previous vintages' percent changes
    previous_results = {}
    
    # export dframe1 to csv
    dframe1.to_csv('dframe1.csv')
    
    # remove benchmark revisions where last observation is left uncalculated
    # for example, see GDPC1 from FRED, 20031210 vintage, last obs ~07/01/2003 
    for col in dframe1:
        i = dframe1.columns.get_loc(col)
        # make sure there is a previous column to compare to
        if i > 0:
            # get the current column's last index
            col_last_index = dframe1.iloc[:, i].last_valid_index()
            
            # get the previous column's last index
            prev_col_last_index = dframe1.iloc[:, i - 1].last_valid_index()
            
            if col_last_index < prev_col_last_index:
                dframe1.drop(columns=col, inplace = True)

    # export dframe1 to csv
#     dframe1.to_csv('dframe1.csv')
    
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
        
        # find the date index of the last non-missing observation
        last_coincident_index = dframe1[coincident_col_ref].last_valid_index()

        # find the date index's index integer value so we can calculate lags
        last_coincident_index_int = dframe1.index.get_loc(last_coincident_index)
        
        # find the last value of the data preceeding the meeting
        last_coincident_value = dframe1[coincident_col_ref].iloc[last_coincident_index_int]
                
        # find the one-year-ago observation's int index value
        one_year_ago_coincident_index_int = last_coincident_index_int - 4
        
        # find the one-year-ago obsesrvation's value 
        one_year_ago_coincident_value = dframe1[coincident_col_ref].iloc[one_year_ago_coincident_index_int]
        
        # find the one period lagged coincident index
        lag_coincident_index_int = last_coincident_index_int - 1
        
        #grab the one period lagged value of the coincident column
        lag_coincident_value = dframe1[coincident_col_ref].iloc[lag_coincident_index_int]
        
        #grab the lagged index from one year before in the coincident column
        lag_one_year_ago_coincident_index_int = lag_coincident_index_int - 4
        
        #grab the value from one year before in the coincident column
        lag_one_year_ago_coincident_value = dframe1[coincident_col_ref].iloc[lag_one_year_ago_coincident_index_int]
        
        # calculate the percent change in the variable immediately preceeding the meeting
        coincident_percent_change = (last_coincident_value - one_year_ago_coincident_value)/one_year_ago_coincident_value*100

       # calculate the one period lagged percent change
        lag_coincident_percent_change = (lag_coincident_value - lag_one_year_ago_coincident_value)/lag_one_year_ago_coincident_value*100
#         print("Meeting:", meet)
#         print("Lagged Value:", lag_coincident_value)
#         print("Prev Value:", prev_coincident_value)
        
        # append meeting and coincident percent change to coincident_results dict
        coincident_results[meet] = coincident_percent_change
        
        # append meeting and lagged percent change to previous_results dict
        previous_results[meet] = lag_coincident_percent_change
        

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
    
def find_growth_gap(gdp_frame, FOMC_date_list, column_A_name='trend', column_B_name='actual', column_C_name='spread'):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    
    # take the natural log of both real gdp and real potential gdp
#     gdp_frame = (np.log(gdp_frame))
    
    # create a dictionary to store the 
    trend_dict = {}
    
    # create a dictionary to store the 
    actual_dict = {}
    
    # create a dictionary to store the 
    spread_dict = {}
    
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
    
    # create a list to store associated column dates 
    temp_gdp_column_dates_list = []

    # capture the FRED column prefix including '_'
    gdp_FRED_prefix = gdp_frame.columns[-1][:len(gdp_frame.columns[-1])-len(gdp_frame.columns[-1][-8:])]

    # for each FOMC meeting
    for meet in FOMC_date_list:

        # clear list after previous iteration
        temp_gdp_column_dates_list.clear()

        # find the gdp vintages before the current meeting
        for col in gdp_frame.columns:

            # capture the date of the column being referenced as a datetime
            col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')

            # if the current column's date is before the meeting's date
            if col_date < meet:

                # add the column date to a temporary list of column dates
                temp_gdp_column_dates_list.append(col_date)

        # find the largest date in the temporary list. this should be the date of the vintage that immediately preceeds the meeting being referenced
        gdp_vintage = max(temp_gdp_column_dates_list)

        # construct the name of the appropriate FRED data column
        gdp_col_ref = gdp_FRED_prefix + dt.datetime.strftime(gdp_vintage, '%Y%m%d')

        # find the needed range of data
        last_valid_gdp_index = gdp_frame[gdp_col_ref].last_valid_index()
        first_valid_gdp_index = gdp_frame[gdp_col_ref].first_valid_index()
        
        # create a df of the needed range of data
        growth_df = gdp_frame.loc[first_valid_gdp_index:last_valid_gdp_index , gdp_col_ref]

        # create an empty df for recursive regressions
        reg_df = pd.DataFrame
        
        # create empty lists for trend and actual growth
        trend_growth = []
        actual_growth = []
        
        # loop through observations for trend regressions -- ln(gdp) ~ t + e
        for obs in growth_df.index:
            
            # if statement to allow for actual growth calculations
            if growth_df.index.get_loc(obs) > 5:
                
                # set start and end of df for linear regression and trend estimation
                df_start = 6
                df_end = growth_df.index.get_loc(obs)
                
                # build the df for the growth trend regression
                t = pd.Series(range(0,df_end-5))
                gdp = growth_df.iloc[df_start:df_end+1]
                gdp.name = 'gdp'
                t.name = 't'
                t.index = gdp.index
                reg_df = pd.concat([gdp, t], axis=1)
                reg_df['ln.gdp'] = np.log(reg_df['gdp'])
                
                # setup regression variables
                predictors = ['t']
                X = reg_df[predictors]
                y = reg_df['ln.gdp']
                
                # Initialise and fit linear regression model using `statsmodels`
                model = smf.ols('y ~ X', data=reg_df)
                model = model.fit()
                
                # append annualized growth trend to list
                trend_growth.append(np.exp(model.params[1]*4)-1)

                # find old and new observations for actual growth calculation
                old = np.log(growth_df.iloc[df_end - 4])
                new = np.log(growth_df.iloc[df_end])
                
                # append actual growth to list
                actual_growth.append(new - old)
                
        # assign meeting-wise observations to dictionaries
        trend_dict[meet] = trend_growth[-1]*100
        actual_dict[meet] = actual_growth[-1]*100
        spread_dict[meet] = (actual_growth[-1] - trend_growth[-1])*100

        # combine results into a single dataframe
        results = pd.DataFrame({column_A_name:pd.Series(trend_dict),column_B_name:pd.Series(actual_dict),column_C_name:pd.Series(spread_dict)})

    return results
    
def find_cpi_growth(cpi_frame, FOMC_date_list, column_A_name='cpi'):
    '''returns a data frame of vintage average CPI growth for the previous quarter at each FOMC meeting date'''
            
    # create a dictionary to store the 
    cpi_dict = {}
    
    # create a dataframe to store and return the results
    results = pd.DataFrame(index=FOMC_date_list)
    
    # remove benchmark revisions where last observation is left uncalculated/ unreported
    # for example, see GDPC1 from FRED, 20031210 vintage, last obs ~07/01/2003 
    for col in cpi_frame:
        # get location of current column
        i = cpi_frame.columns.get_loc(col)
        # if it isn't the first column
        if i > 0:
            # find the index of the current column's last observation
            col_last_index = cpi_frame.iloc[:, i].last_valid_index()
            # find the index of the previous column's last observation
            prev_col_last_index = cpi_frame.iloc[:, i - 1].last_valid_index()
            # if the current column is shorter than the previous column
            if col_last_index < prev_col_last_index:
                # drop the current column
                cpi_frame.drop(columns=col, inplace = True)
    
    # create a list to store associated column dates 
    temp_cpi_column_dates_list = []

    # capture the FRED column prefix including '_'
    cpi_FRED_prefix = cpi_frame.columns[-1][:len(cpi_frame.columns[-1])-len(cpi_frame.columns[-1][-8:])]
    
    # for each FOMC meeting
    for meet in FOMC_date_list:

        # clear list after previous iteration
        temp_cpi_column_dates_list.clear()

        # find the gdp vintages before the current meeting
        for col in cpi_frame.columns:

            # capture the date of the column being referenced as a datetime
            col_date = dt.datetime.strptime(col[-8:], '%Y%m%d')

            # if the current column's date is before the meeting's date
            if col_date < meet:

                # add the column date to a temporary list of column dates
                temp_cpi_column_dates_list.append(col_date)

        # find the largest date in the temporary list. this should be the date of the vintage that immediately preceeds the meeting being referenced
        cpi_vintage = max(temp_cpi_column_dates_list)

        # construct the name of the appropriate FRED data column
        cpi_col_ref = cpi_FRED_prefix + dt.datetime.strftime(cpi_vintage, '%Y%m%d')
        cpi_col_ref_int = cpi_frame.columns.get_loc(cpi_col_ref)
        
        # find the needed range of data
        last_valid_cpi_index = cpi_frame[cpi_col_ref].last_valid_index()
        last_valid_cpi_index_int = cpi_frame.index.get_loc(last_valid_cpi_index) + 1
        first_valid_cpi_index_int = last_valid_cpi_index_int - 3
        
        # calculate the last available 3 months worth of data
        cpi_growth = np.mean(cpi_frame[cpi_col_ref].iloc[first_valid_cpi_index_int:last_valid_cpi_index_int])
                            
        # assign meeting-wise observations to dictionary
        cpi_dict[meet] = cpi_growth

        # combine results into a single dataframe
        results = pd.DataFrame({column_A_name:pd.Series(cpi_dict)})
        
    return results
    
def daily_to_quarterly_avg_percent_chg(dframe, FOMC_date_list, column_A_name = 'col', target_col = 'target'):
    '''returns a dataframe which contains, for each Fed meeting, the quarterly average of the yoy percent change in a variable preceeding the meeting'''

    # create a date list containing all possible dates between the start and end of the passed dframe
    full_dates = pd.date_range(dframe.first_valid_index(), dframe.last_valid_index())

    # rebuild dframe index to contain all possible dates
    dframe = dframe.reindex(full_dates)
    
    # fill forward the previous observations
    dframe = dframe.fillna(method = 'ffill')

    # calculat the yoy percent change
    dframe[column_A_name] = dframe[target_col].pct_change(365)

    # take the rolling quarterly average of the yoy percent change
    results = dframe.rolling(window=91)[column_A_name].mean()
    
    return results