#!/usr/bin/env python
# coding: utf-8

get_ipython().run_line_magic('config', 'Completer.use_jedi = False #for intellisense compatibility w/ Jupyter Notebook')

from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std

from alfredhelperfile import find_new_vintage_percent_chg, find_log_pct_chg_gdps


# Read in FOMC Meeting Dates

# read in FOMC meeting dates from author's file
df = pd.read_csv('fomc_dates.csv')

# create list of FOMC meetings
FOMC_meets = df['fomc_date'].tolist()

# cast list items to datetime objects for functions (probably could have just passed df to f(n)s)
FOMC_dates = [dt.datetime.strptime(meet,'%m/%d/%Y') for meet in FOMC_meets]

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# cast the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for merge
FOMC_df.index.name = 'observation_date'


# Read in and Format Vintage Potential Real GDP & Real GDP Data from ALFRED File

# read in ALFRED data
# https://alfred.stlouisfed.org/
# data as of 2/10/2021

# read in real gdp data from file
df1 = pd.read_csv('GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\t', na_values='.')

# set index to observation date
df1.set_index('observation_date', inplace=True)

# discard data prior to 1997 as our FOMC data begin in 2000
df1 = df1.loc['1997-01-01':]

# drop any remaining columns with no observations
df1 = df1.dropna(how='all', axis=1)

# read in real potential gdp data from file
df2 = pd.read_csv('GDPPOT_2_Vintages_Starting_1991_01_30.txt', sep='\t', na_values='.')

# set index to observation date
df2.set_index('observation_date', inplace=True)

# discard data prior to 1997 as our FOMC data begin in 2000
df2 = df2.loc['1997-01-01':]

# drop any remaining columns with no observations
df2 = df2.dropna(how='all', axis=1)

# calculate vintage percent changes with helper function
FOMC_log_gdp_hist = find_log_pct_chg_gdps(df1, df2, FOMC_dates, column_A_name='logg', column_B_name='logpg')

# create our spread variable for the taylor regression
FOMC_log_gdp_hist['loggs'] = FOMC_log_gdp_hist['logg'] - FOMC_log_gdp_hist['logpg']


# Read in and Format CPI % Change from Year Ago from ALFRED File

# URL: https://alfred.stlouisfed.org/
# Note: Must select 'All' in the Vintage Dates section. 
# Data as of 2/9/2021

# read in ALFRED data
df = pd.read_csv('CPILFESL_2_Vintages_Starting_1996_12_12.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# discard data prior to 1999 as our FOMC data begin in 2000
df = df.loc['1997-01-01':]

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent changes with helper function
CPI_change_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='cpil', column_B_name='cpi', annualize_pct_chg=0, pct_chg_year_ago=1)

# create data frame for merge and drop lagged calulations
CPI_change_hist = CPI_change_hist.drop(columns = ['cpil'])


# Read in and Format Core PCE % Change from Year Ago from ALFRED File

# URL: https://alfred.stlouisfed.org/
# Note: Must select 'All' in the Vintage Dates section. 
# Data as of 2/9/2021

# read in ALFRED data
df = pd.read_csv('PCEPILFE_2_Vintages_Starting_2000_08_01.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# discard data prior to 1997 as our FOMC data begin in 2000
df = df.loc['1997-01-01':]

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent changes for later meetings with helper function
PCE_change_hist = find_new_vintage_percent_chg(df, FOMC_dates[4:], column_A_name='pcel', column_B_name='pce', annualize_pct_chg=0, pct_chg_year_ago=1)

# create data frame for merge and drop lagged calulations
PCE_change_hist = PCE_change_hist.drop(columns = ['pcel'])


# Blend CPI & PCE % Chg from a Year Ago Data at 8-2000 Meeting

# create the cpi data frame
part1 = CPI_change_hist[:'2000-06-28']

# create the pce data frame
part2 = PCE_change_hist['2000-06-28':]

# rename cpi df for concat
part1.rename(columns={"cpi": "pby"},inplace = True)

# rename pce df for concat
part2.rename(columns={"pce": "pby"},inplace = True)

# concatenate dfs
FOMC_blend_change_prices = pd.concat([part1, part2], axis=0)

# create inflation target column for taylor regression
FOMC_blend_change_prices['pt'] = 2

# create our spread variable for the taylor regression
FOMC_blend_change_prices['pts'] = FOMC_blend_change_prices['pby'] - FOMC_blend_change_prices['pt']


# Read in and Format Vintage GDP Data from ALFRED File

# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPC1
# Note: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021

# read in ALFRED data
df = pd.read_csv('GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# discard data prior to 1999 as our FOMC data begin in 2000
df = df.loc['1999-01-01':]

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent changes with helper function
FOMC_gdp_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lg', column_B_name='g')


# Read in and Format Vintage GDP Chain-Type Price Index Data from ALFRED File

# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPCTPI
# NOTE: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021

# read in ALFRED data
df = pd.read_csv('GDPCTPI_2_Vintages_Starting_1996_01_19.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# discard data prior to 1999 as our FOMC data begins in 2000
df = df.loc['1999-01-01':]

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent change with helper function
FOMC_price_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p', annualize_pct_chg=1)


# Read in and Format Vintage PCE Chain-Type Price Index Data from ALFRED File

# URL: https://alfred.stlouisfed.org/
# Note: Must select 'All' in the Vintage Dates section. 
# Data as of 2/8/2021

# read in ALFRED data
df = pd.read_csv('JCXFE_2_Vintages_Starting_1999_07_29.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# discard data prior to 1999 as our FOMC data begins in 2000
df = df.loc['1999-01-01':]

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=1)

# calculate vintage percent change with helper function
FOMC_pce_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p', annualize_pct_chg=1)


# Read in and Format US Economic Policy Uncertainty Index Data from ALFRED

# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=USEPUINDXD
# Note: Cannot select all here as too many vintages exists. Data as of 1/28/2021.
# These data don't strongly revise so we calculate on the latest vintage

# read in ALFRED data
df = pd.read_csv('USEPUINDXD_2_Vintages_Starting_2018_06_29.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# set index to datetime
df.index = pd.to_datetime(df.index)

# grab last column
df = df.iloc[:, -1:]

# take a 30 day moving average of the data
df['EPU 30 Day MA'] = df.rolling(window=30)['USEPUINDXD_20210128'].mean()

# center and scale the data
df['epu'] = StandardScaler().fit_transform(df[['EPU 30 Day MA']])

# retain only the centered and scaled data
epu_df = df[['epu']]

# merge dataframes to retain observations on FOMC meeting dates
FOMC_epu_hist = pd.merge_asof(FOMC_df, epu_df, left_index = True, right_index = True)


# Read in and Format 10 Year, 2 Year Treasury Constant Maturity Index Data from ALFRED

# URL: https://alfred.stlouisfed.org/
# Note: Must select 'All' in the Vintage Dates section. 
# Data as of 2/10/2021
# These data don't strongly revise so we calculate on the latest vintage

# read in ALFRED data
df = pd.read_csv('T10Y2YM_2_Vintages_Starting_2021_02_01.txt', sep='\t', na_values='.')

# set index to observation date
df.set_index('observation_date', inplace=True)

# set index to datetime
df.index = pd.to_datetime(df.index)

# center and scale the data
df['ts'] = StandardScaler().fit_transform(df[['T10Y2YM_20210201']])

# retain only the centered and scaled data
term_df = df[['ts']]

# merge dataframes to retain observations on FOMC meeting dates
FOMC_term_hist = pd.merge_asof(FOMC_df, term_df, left_index = True, right_index = True)


# Read in and Format S&P 500 Data from Yahoo

# URL: https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC

# read in data from Yahoo finance
df = pd.read_csv('^GSPC.csv')

# set the date as the index
df.set_index('Date', inplace=True)

# set the indec to datetime
df.index = pd.to_datetime(df.index)

# rename the index for the merge
df.index.name = 'observation_date'

# take a 21 day moving average of the data
df['SPX 21 Day MA'] = df.rolling(window=21)['Close'].mean()

# center and scale the data
df['spx'] = StandardScaler().fit_transform(df[['SPX 21 Day MA']])

# Retain only the centered and scaled data
spx_df = df[['spx']]

# merge dataframes to retain observations on FOMC meeting dates
FOMC_spx_hist = pd.merge_asof(FOMC_df, spx_df, left_index = True, right_index = True)


# Read in and Format Median GDP Forecast Data from FRB Philadelphia

# URL: https://www.philadelphiafed.org/surveys-and-data/rgdp
# Note: 'Median Responses' as of 1/10/2021

df = pd.read_excel(io='Median_RGDP_Level.xlsx', sheet_name='Median_Level') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('philly_release_dates.csv')

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


# Read in and Format GDP Price Percent Change (Growth) Forecast from Philly Fed

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Median Responses' as of 1/12/2021

#read in data
df = pd.read_excel(io='Median_PGDP_Growth.xlsx', sheet_name='Median_Growth') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('philly_release_dates.csv')

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

# FOMC_price_forecast_median.tail(15)


# Read in and Format Core PCE Median Forecast Data from Philly Fed

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Median Responses' as of 1/12/2021

# read in data from file
df = pd.read_excel(io='Median_COREPCE_Level.xlsx', sheet_name='Median_Level') #read in data

# read in approximate Philly Fed release dates
philly_dates = pd.read_csv('philly_release_dates.csv')

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


# Read in and Format FOMC Target Data from Author's Calculations Based on ALFRED Data

# to save time, this work was imported from a previous calculation. we should rebuild here if published
df = pd.read_csv('fomc_rates.csv', index_col=0)

df.index.name = 'observation_date'

# set the index to datetime
df.index = pd.to_datetime(df.index)

# drop any remaining columns with no observations
df = df.dropna(how='all', axis=0)

# name dataframe for join
FOMC_target_hist = df


# Combine Macro Data from ALFRED, FRED, & Philly Fed

macro_df = FOMC_gdp_hist.join([FOMC_gdp_forecast_median, FOMC_prices, FOMC_epu_hist, FOMC_spx_hist, FOMC_term_hist, FOMC_log_gdp_hist, FOMC_blend_change_prices, FOMC_target_hist])
macro_df.index.names = ['date']
macro_df.to_csv('macro_df.csv')

