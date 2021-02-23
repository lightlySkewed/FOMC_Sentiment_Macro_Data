#!/usr/bin/env python
# coding: utf-8

get_ipython().run_line_magic('config', 'Completer.use_jedi = False #for intellisense compatibility w/ Jupyter Notebook')

import pandas as pd
import numpy as np
import datetime as dt

from alfredhelperfile import find_new_vintage_percent_chg, find_growth_gap, find_cpi_growth


# Read in FOMC Meeting Dates

# read in FOMC meeting dates from author's file
df = pd.read_csv('Input_Data/fomc_dates.csv')

# create list of FOMC meetings
FOMC_meets = df['fomc_date'].tolist()

# cast list items to datetime objects for functions (probably could have just passed df to f(n)s)
FOMC_dates = [dt.datetime.strptime(meet,'%m/%d/%Y') for meet in FOMC_meets]

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# cast the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for future merge
FOMC_df.index.name = 'observation_date'


# Read in and Format Vintage Real GDP Data from ALFRED File

# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPC1
# Note: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021

# read in ALFRED data
df = pd.read_csv('Input_Data/GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent changes with helper function
FOMC_gdp_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lg', column_B_name='g')


# Read in and Format Median Real GDP Forecast Data from FRB Philadelphia

# URL: https://www.philadelphiafed.org/surveys-and-data/rgdp
# Note: 'Median Responses' as of 1/10/2021

df = pd.read_excel(io='Input_Data/Median_RGDP_Level.xlsx', sheet_name='Median_Level') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('Input_Data/philly_release_dates.csv')

# drop last col which shows up as NaT in index (not sure why this shows up...)
df = df[df['YEAR'].notna()]

# drop date before the 4th quarter of 1999
df = df[124:]

# set index to index of Philly data df. this is manually alligned by the authors
# the alignment is done to push a quarterly 'release date' to the corresponding 
# observation quarter
philly_dates = philly_dates.set_index(df.index)

# set df index to philly fed period
df = df.set_index(philly_dates['Period'])

# set df index to datetime
df.index = pd.to_datetime(df.index)

# calculate the one period ahead pct change from 1evels 
df['g1'] = df[['RGDP1', 'RGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# calculate the two period ahead pct change from 1evels 
df['g2'] = df[['RGDP2', 'RGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# identify columns to retain
median_GDP_forecasts = ['g1', 'g2']

# filter for wanted columns
median_GDP_forecasts = df.filter(median_GDP_forecasts, axis=1)

# set index to observation date
median_GDP_forecasts.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_gdp_forecast_median = pd.merge_asof(FOMC_df, median_GDP_forecasts, left_index = True, right_index = True)


# Read in and Format Vintage GDP Chain-Type Price Index Data from ALFRED File

# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPCTPI
# NOTE: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021

# read in ALFRED data
df = pd.read_csv('Input_Data/GDPCTPI_2_Vintages_Starting_1996_01_19.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent change with helper function
FOMC_price_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p', annualize_pct_chg=1)


# Read in and Format GDP Price Percent Change (Growth) Forecast from Philly Fed

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Median Responses' as of 1/12/2021

#read in data
df = pd.read_excel(io='Input_Data/Median_PGDP_Growth.xlsx', sheet_name='Median_Growth') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('Input_Data/philly_release_dates.csv')

# drop last col which shows up as NaT in index (not sure why this shows up...)
df = df[df['YEAR'].notna()]

# set length to correct Philly Fed release date length
df = df[124:]

# set index to index of Philly data df. this is manually alligned by the authors
# the alignment is done to push a quarterly 'release date' to the corresponding 
# observation quarter
philly_dates = philly_dates.set_index(df.index)

# set df index to philly fed period
df = df.set_index(philly_dates['Period'])

# # set df index to datetime
df.index = pd.to_datetime(df.index)

# remove blank rows
df = df[df['DPGDP2'].notna()]

# rename columns
df['p1'] = df['DPGDP2']
df['p2'] = df['DPGDP3']

# identify columns to retain
median_price_forecasts = ['p1', 'p2']

# filter for wanted columns
median_price_forecasts = df.filter(median_price_forecasts, axis=1)

# set index to observation date
median_price_forecasts.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_price_forecast_median = pd.merge_asof(FOMC_df, median_price_forecasts, left_index = True, right_index = True)


# Read in and Format Vintage PCE Chain-Type Price Index Data from ALFRED File

# URL: https://alfred.stlouisfed.org/
# Note: Must select 'All' in the Vintage Dates section. 
# Data as of 2/8/2021

# read in ALFRED data
df = pd.read_csv('Input_Data/JCXFE_2_Vintages_Starting_1999_07_29.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent change with helper function
FOMC_pce_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p', annualize_pct_chg=1)


# Read in and Format Core PCE Median Forecast Data from Philly Fed

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Median Responses' as of 1/12/2021

# read in data from file
df = pd.read_excel(io='Input_Data/Median_COREPCE_Level.xlsx', sheet_name='Median_Level') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('Input_Data/philly_release_dates.csv')

# drop last col which shows up as NaT in index (not sure why this shows up...)
df = df[df['YEAR'].notna()]

# set length to correct Philly Fed release date length
df = df[124:]

# set index to index of Philly data df. this is manually alligned by the authors
# the alignment is done to push a quarterly 'release date' to the corresponding 
# observation quarter
philly_dates = philly_dates.set_index(df.index)

# set df index to philly fed period
df = df.set_index(philly_dates['Period'])

# # set df index to datetime
df.index = pd.to_datetime(df.index)

# remove blank rows
df = df[df['COREPCE1'].notna()]

# rename columns
df['p1'] = df['COREPCE2']
df['p2'] = df['COREPCE3']

# identify columns to retain
median_pce_forecasts = ['p1', 'p2']

# filter for wanted columns
median_pce_forecasts = df.filter(median_pce_forecasts, axis=1)

# set index to observation date
median_pce_forecasts.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_pce_forecast_median = pd.merge_asof(FOMC_df, median_pce_forecasts, left_index = True, right_index = True)


# Join GDP Price Data with Core PCE Data When Available

# join historic and forecast gdp price data
price_df = FOMC_price_hist.join(FOMC_price_forecast_median)

# join historic and forecast pce data
pce_df = FOMC_pce_hist.join(FOMC_pce_forecast_median)

# slice gdp price data for pre 2007
part1 = price_df[:'2007-01-31']

# slice pce data for post 2007
part2 = pce_df['2007-03-21':]

# rename columns to conform to macro_df variables
part1.rename(columns={"pricel1": "lp", "price": "p", "pricef1med": "p1", "pricef2med": "p2"},inplace = True)
part2.rename(columns={"pcel1": "lp", "pce": "p", "pcef1med": "p1", "pcef2med": "p2"},inplace = True)

# concat parts to single df
FOMC_prices = pd.concat([part1, part2], axis=0)


# Read in and Format Vintage Core Inflation Data -- for Taylor Regression

# read in ALFRED data
# https://alfred.stlouisfed.org/
# data as of 2/23/2021
# must select percent change from a year ago as units 
# note: CPI was chosen as ALFRED didn't start recording vintage PCE data until ~2013

# read in core cpi data from file
df = pd.read_csv('Input_Data/CPILFESL_2_Vintages_Starting_1996_12_12.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent changes with helper function
FOMC_corecpi_growth = find_cpi_growth(df, FOMC_dates, column_A_name='corecpi')


# Calculate Output Gap from Real GDP and Trend Growth -- for Taylor Regression

# read in ALFRED data
# https://alfred.stlouisfed.org/
# data as of 2/10/2021

# read in real gdp data from file
df1 = pd.read_csv('Input_Data/GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\t', na_values='.')

# set index to observation date
df1.set_index('observation_date', inplace=True)

# trim dataframe
df1 = df1['1959-07-01':]

# remove bad benchmark year
# should build this into the find growt f(n). do this if publishing.
df1 = df1.drop('GDPC1_19991028', axis = 1)

# drop any remaining columns with no observations
df1 = df1.dropna(how='all', axis=1)

# calculate vintage growth gap with helper function
FOMC_gdp_gap = find_growth_gap(df1, FOMC_dates, column_C_name = 'gdpgap')


# Read in and Format FOMC Target Data from Author's Calculations Based on ALFRED Data

# to save time, this work was imported from a previous calculation. we should rebuild here if published
df = pd.read_csv('Input_Data/fomc_rates.csv', index_col=0)

# name index for future merge
df.index.name = 'observation_date'

# set the index to datetime
df.index = pd.to_datetime(df.index)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=0)

# name dataframe for join
FOMC_target_hist = df


# Combine Macro Data from ALFRED, FRED, & Philly Fed

macro_df = FOMC_gdp_hist.join([FOMC_gdp_forecast_median, FOMC_prices, FOMC_corecpi_growth, FOMC_gdp_gap, FOMC_target_hist])
macro_df.index.names = ['date']
macro_df.to_csv('Output_Data/macro_df.csv')

