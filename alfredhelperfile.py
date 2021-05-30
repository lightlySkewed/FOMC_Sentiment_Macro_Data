import pandas as pd
import numpy as np
import datetime as dt
import statsmodels.formula.api as smf

def find_vintage_percent_chg(dframe1, FOMC_date_list, column_A_name='lag', column_B_name='coincident'):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    # create a dictionary to store the conincident vintages' percent changes
    coincident_results = {}
    
    # create a dictionary to store the previous vintages' percent changes
    previous_results = {}
    
    # export dframe1 to csv
    #dframe1.to_csv('dframe1.csv')
    
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
        # print("Meeting:", meet)
        # print("Lagged Value:", lag_coincident_value)
        # print("Prev Value:", prev_coincident_value)
        
        # append meeting and coincident percent change to coincident_results dict
        coincident_results[meet] = coincident_percent_change
        
        # append meeting and lagged percent change to previous_results dict
        previous_results[meet] = lag_coincident_percent_change
        

    # combine results into a single dataframe
    results = pd.DataFrame({column_A_name:pd.Series(previous_results),column_B_name:pd.Series(coincident_results)})
    
    # return dataframe
    return results

def find_growth_gap(gdp_frame, FOMC_date_list, column_A_name='trend', column_B_name='actual', column_C_name='spread'):
    '''returns a data frame of vintage lagged and coincident percent change values from vintage levels'''
    '''this code takes forever to run. it needs to be refactored.'''
    
    # create a dictionary to store the trend
    trend_dict = {}
    
    # create a dictionary to store the actual
    actual_dict = {}
    
    # create a dictionary to store the spread between the trend and actual
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
        growth_df = gdp_frame.loc[:last_valid_gdp_index , gdp_col_ref].to_frame()
        growth_df = growth_df.assign(t=pd.Series(range(0,len(growth_df))).values)
        growth_df['ln.gdp'] = np.log(growth_df[gdp_col_ref])
        
        # setup regression variables
        X = growth_df['t']
        y = growth_df['ln.gdp']
        
        # Initialise and fit linear regression model using `statsmodels`
        model = smf.ols('y ~ X', data=growth_df)
        model = model.fit()
        
        # create empty lists for trend and actual growth
        trend_growth = []
        actual_growth = []

        # append annualized growth trend to list
        trend_growth.append(np.exp(model.params[1]*4)-1)

        # find old and new observations for actual growth calculation
        previous = growth_df['ln.gdp'].iloc[-5]
        last = growth_df['ln.gdp'].iloc[-1]

        # append actual growth to list
        actual_growth.append(last - previous)

        # assign meeting-wise observations to dictionaries
        trend_dict[meet] = trend_growth[-1]*100
        actual_dict[meet] = actual_growth[-1]*100
        spread_dict[meet] = (actual_growth[-1] - trend_growth[-1])*100

        # combine results into a single dataframe
        results = pd.DataFrame({column_A_name:pd.Series(trend_dict),column_B_name:pd.Series(actual_dict),column_C_name:pd.Series(spread_dict)})

    return results
    
def find_price_growth(price_frame, FOMC_date_list, column_A_name='cpi'):
    '''returns a data frame of vintage average CPI growth for the previous quarter at each FOMC meeting date'''
            
    # create a dictionary to store the 
    cpi_dict = {}
    
    # create a dataframe to store and return the results
    results = pd.DataFrame(index=FOMC_date_list)
    
    # remove benchmark revisions where last observation is left uncalculated/ unreported
    # for example, see GDPC1 from FRED, 20031210 vintage, last obs ~07/01/2003 
    for col in price_frame:
        # get location of current column
        i = price_frame.columns.get_loc(col)
        # if it isn't the first column
        if i > 0:
            # find the index of the current column's last observation
            col_last_index = price_frame.iloc[:, i].last_valid_index()
            # find the index of the previous column's last observation
            prev_col_last_index = price_frame.iloc[:, i - 1].last_valid_index()
            # if the current column is shorter than the previous column
            if col_last_index < prev_col_last_index:
                # drop the current column
                price_frame.drop(columns=col, inplace = True)
    
    # create a list to store associated column dates 
    temp_cpi_column_dates_list = []

    # capture the FRED column prefix including '_'
    cpi_FRED_prefix = price_frame.columns[-1][:len(price_frame.columns[-1])-len(price_frame.columns[-1][-8:])]
    
    # for each FOMC meeting
    for meet in FOMC_date_list:

        # clear list after previous iteration
        temp_cpi_column_dates_list.clear()

        # find the gdp vintages before the current meeting
        for col in price_frame.columns:

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
        cpi_col_ref_int = price_frame.columns.get_loc(cpi_col_ref)
        
        # find the needed range of data
        last_valid_cpi_index = price_frame[cpi_col_ref].last_valid_index()
        last_valid_cpi_index_int = price_frame.index.get_loc(last_valid_cpi_index) + 1
        first_valid_cpi_index_int = last_valid_cpi_index_int - 12
        # first_valid_cpi_index_int = last_valid_cpi_index_int - 3        
        
        # calculate the last available 12 months worth of data
        cpi_growth = np.mean(price_frame[cpi_col_ref].iloc[first_valid_cpi_index_int:last_valid_cpi_index_int])
                            
        # assign meeting-wise observations to dictionary
        cpi_dict[meet] = cpi_growth

        # combine results into a single dataframe
        results = pd.DataFrame({column_A_name:pd.Series(cpi_dict)})
        
    return results