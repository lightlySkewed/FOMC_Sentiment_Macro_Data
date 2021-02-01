#!/usr/bin/env python
# coding: utf-8

# ToDo:
# 
# Plot important dates against our output: https://www.policyuncertainty.com/media/US_Annotated_Series.pdf
# 
# 1) Bush Election
# 2) 9/11
# 3) Gulf War II
# 4) Stimulus Debate ~2007/ 2008
# 5) Lehman/ TARP ~2008/ 2009
# 6) Eurozone Crisis/ US Midterm Elections ~Nov 2010
# 7) Debt Ceiling Debate ~2011/2012
# 8) Fiscal Cliff ~2013
# 9) Govt. Shutdown ~2013/ 2014
# 10) Brexit ~2016
# 11) Trump Election ~Nov 2016
# 12) US out of TPP ~2016/ 2017
# 13) Tarrifs 2018
# 
# Market Dates: https://www.timetoast.com/timelines/important-dates-in-the-history-of-the-u-s-stock-markets
# 
# 1) Dot Com Bubble = Mar 10, 2000
# 2) NASDAQ Drop 356 Points = Apr 14, 2000
# 3) Hurricane Katrina = Aug 25, 2005
# 4) 2008 Market Selloff = 09/29/2008, 10/08/2008, 10/15/2008, 10/22/2008, 12/01/2008, 12/10/2008
# 5) 2011 Market Selloff = 08/04/2011, 08/08/2011, 09/17/2011, 12/31/2011
# 6) Derive other dates from SPX data
# 
# https://fraser.stlouisfed.org/timeline/covid-19-pandemic
# 
# https://fraser.stlouisfed.org/timeline/financial-crisis

get_ipython().run_line_magic('config', 'Completer.use_jedi = False #for intellisense compatibility w/ Jupyter Notebook')

from sklearn.preprocessing import StandardScaler
import pandas as pd
import datetime as dt
from iGetByWithALittle import find_target_columns, find_new_obs_percent_chg, find_new_vintage_percent_chg, find_index_in_Excel_File_dict


# Read in FOMC Meeting Dates

# read in FOMC meeting dates
df = pd.read_csv('fomc_dates.csv')

# create list of FOMC meetings
FOMC_meets = df['fomc_date'].tolist()

# create datetime objects out of list items
FOMC_dates = [dt.datetime.strptime(meet,'%m/%d/%Y') for meet in FOMC_meets]


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
FOMC_gdp_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='gdp-1', column_B_name='gdp+0')


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
FOMC_price_hist = find_new_vintage_percent_chg(df, FOMC_dates, column_A_name='price-1', column_B_name='price+0')


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
df['EPU Std 30 Day MA'] = StandardScaler().fit_transform(df[['EPU 30 Day MA']])

# retain only the centered and scaled data
epu_df = df[['EPU Std 30 Day MA']]

# build FOMC dates dataframe for observations of EPU data on meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# set index to datetime for merge
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set index name to match epu_df for merge
FOMC_df.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_epu_hist = pd.merge_asof(FOMC_df, epu_df, left_index = True, right_index = True)


# Read in and Format S&P 500 Data from Yahoo

# URL: https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC

# read in data from Yahoo finance
df = pd.read_csv('^GSPC.csv')

# set the date as the index
df.set_index('Date', inplace=True)

# set the indec to datetime
df.index = pd.to_datetime(df.index)

# take a 30 day moving average of the data
df['SPX 30 Day MA'] = df.rolling(window=30)['Close'].mean()

# center and scale the data
df['SPX Std 30 Day MA'] = StandardScaler().fit_transform(df[['SPX 30 Day MA']])

# rename the index for the merge
df.index.name = 'observation_date'

# Retain only the centered and scaled data
spx_df = df[['SPX Std 30 Day MA']]

# merge dataframes to retain observations on FOMC meeting dates
FOMC_spx_hist = pd.merge_asof(FOMC_df, spx_df, left_index = True, right_index = True)


# Read in and Format Mean GDP Forecast Data from FRB Philadelphia

# URL: https://www.philadelphiafed.org/surveys-and-data/rgdp
# Note: 'Mean Responses' as of 1/10/2021. Philly Fed Release dates are approximate and are created by the author. These dates have not been confirmed with the Philly Fed.

# read in Philly Fed data
df = pd.read_excel(io='Mean_RGDP_Level.xlsx', sheet_name='Mean_Level') #read in data

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
df['gdp+1_mean'] = df[['RGDP1', 'RGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# calculate the two period ahead pct change from 1evels 
df['gdp+2_mean'] = df[['RGDP2', 'RGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# identify columns to retain
mean_GDP_forecasts = ['gdp+1_mean', 'gdp+2_mean']

# filter for wanted columns
mean_GDP_forecasts = df.filter(mean_GDP_forecasts, axis=1)

# set index to observation date
mean_GDP_forecasts.index.name = 'observation_date'

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# set the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for merge
FOMC_df.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_gdp_forecast_mean = pd.merge_asof(FOMC_df, mean_GDP_forecasts, left_index = True, right_index = True)


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
df['gdp+1_median'] = df[['RGDP1', 'RGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# calculate the two period ahead pct change from 1evels 
df['gdp+2_median'] = df[['RGDP2', 'RGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# identify columns to retain
median_GDP_forecasts = ['gdp+1_median', 'gdp+2_median']

# filter for wanted columns
median_GDP_forecasts = df.filter(median_GDP_forecasts, axis=1)

# set index to observation date
median_GDP_forecasts.index.name = 'observation_date'

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# set the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for merge
FOMC_df.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_gdp_forecast_median = pd.merge_asof(FOMC_df, median_GDP_forecasts, left_index = True, right_index = True)


# Read in and Format Mean GDP Price Index Forecast Data from FRB Philadelphia

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Mean Responses' as of 1/12/2021
df = pd.read_excel(io='Mean_PGDP_Level.xlsx', sheet_name='Mean_Level') #read in data

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
df['price+1_mean'] = df[['PGDP1', 'PGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# calculate the two period ahead pct change from 1evels 
df['price+2_mean'] = df[['PGDP2', 'PGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# identify columns to retain
mean_price_forecasts = ['price+1_mean', 'price+2_mean']

# filter for wanted columns
mean_price_forecasts = df.filter(mean_price_forecasts, axis=1)

# set index to observation date
mean_price_forecasts.index.name = 'observation_date'

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# set the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for merge
FOMC_df.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_price_forecast_mean = pd.merge_asof(FOMC_df, mean_price_forecasts, left_index = True, right_index = True)

# FOMC_price_forecast_mean.tail(15)


# Read in and Format Median GDP Price Index Forecast Data from FRB Philadelphia

# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp
# Note: 'Median Responses' as of 1/12/2021
df = pd.read_excel(io='Median_PGDP_Level.xlsx', sheet_name='Median_Level') #read in data

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
df['price+1_median'] = df[['PGDP1', 'PGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# calculate the two period ahead pct change from 1evels 
df['price+2_median'] = df[['PGDP2', 'PGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100, axis=1)

# identify columns to retain
median_price_forecasts = ['price+1_median', 'price+2_median']

# filter for wanted columns
median_price_forecasts = df.filter(median_price_forecasts, axis=1)

# set index to observation date
median_price_forecasts.index.name = 'observation_date'

# create df of FOMC meeting dates
FOMC_df = pd.DataFrame(index=FOMC_meets)

# set the index to datetime
FOMC_df.index = pd.to_datetime(FOMC_df.index)

# set the name of the index for merge
FOMC_df.index.name = 'observation_date'

# merge dataframes to retain observations on FOMC meeting dates
FOMC_price_forecast_median = pd.merge_asof(FOMC_df, median_price_forecasts, left_index = True, right_index = True)

# FOMC_price_median.tail(15)


# Combine Macro Data from ALFRED, FRED, & Philly Fed

macro_df = FOMC_gdp_hist.join([FOMC_gdp_forecast_mean, FOMC_gdp_forecast_median, FOMC_price_hist, FOMC_price_forecast_mean, FOMC_price_forecast_median, FOMC_epu_hist, FOMC_spx_hist])
macro_df.to_csv('macro_df.csv')

