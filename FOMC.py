{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [],
   "source": [
    "%config Completer.use_jedi = False #for intellisense compatibility w/ Jupyter Notebook\n",
    "\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import datetime as dt\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "from alfredhelperfile import find_growth_gap, find_price_growth, find_vintage_percent_chg"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in FOMC Meeting Dates"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [],
   "source": [
    "# read in FOMC meeting dates from author's file\n",
    "df = pd.read_csv('Input_Data/fomc_dates.csv', index_col='fomc_date', parse_dates=True)\n",
    "\n",
    "# set the name of the index for future merge\n",
    "df.index.name = 'observation_date'\n",
    "\n",
    "# name df for future reference\n",
    "FOMC_df = df"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in Philly Fed Forecast Dates"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\micha\\miniconda3\\envs\\FOMC\\lib\\site-packages\\openpyxl\\worksheet\\header_footer.py:48: UserWarning: Cannot parse header or footer so it will be ignored\n",
      "  warn(\"\"\"Cannot parse header or footer so it will be ignored\"\"\")\n"
     ]
    }
   ],
   "source": [
    "# URL: https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/spf-release-dates.txt?la=en&hash=B0031909EE9FFE77B26E57AC5FB39899\n",
    "# Note: Download used for this file was 9/10/2021\n",
    "\n",
    "# read in Philly Fed Real GDP in levels\n",
    "df = pd.read_excel(io='Input_Data/Median_RGDP_Level.xlsx', sheet_name='Median_Level') #read in data\n",
    "\n",
    "# read in Philly Fed release dates\n",
    "philly_dates_df = pd.read_csv('Input_Data/spf-release-dates.txt', engine='python', skiprows=3, skipfooter=7, skip_blank_lines=True, sep=\"[ \\t]{2,}\")\n",
    "\n",
    "# remove leading chars in column names\n",
    "philly_dates_df.rename(columns=lambda x: x.strip(), inplace=True)\n",
    "\n",
    "# retain only the News Release Date column and remove asterisk from data\n",
    "philly_dates = philly_dates_df['News Release Date'].replace({'\\*':''}, regex=True).to_frame()\n",
    "\n",
    "# isolate period of interest\n",
    "philly_dates = philly_dates[38:123]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Vintage Real GDP Data from ALFRED File"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [],
   "source": [
    "# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPC1\n",
    "# Note: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021\n",
    "\n",
    "# read in ALFRED data\n",
    "df = pd.read_csv('Input_Data/GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\\t', na_values='.')\n",
    "\n",
    "# set index to observation date\n",
    "df.set_index('observation_date', inplace=True)\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df = df.dropna(how='all', axis=1)\n",
    "\n",
    "# calculate vintage percent changes with helper function\n",
    "FOMC_gdp_hist = find_vintage_percent_chg(df, FOMC_dates, column_A_name='lg', column_B_name='g')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Median Real GDP Forecast Data from FRB Philadelphia"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\micha\\miniconda3\\envs\\FOMC\\lib\\site-packages\\openpyxl\\worksheet\\header_footer.py:48: UserWarning: Cannot parse header or footer so it will be ignored\n",
      "  warn(\"\"\"Cannot parse header or footer so it will be ignored\"\"\")\n"
     ]
    }
   ],
   "source": [
    "# URL: https://www.philadelphiafed.org/surveys-and-data/rgdp\n",
    "# Note: 'Median Responses' as of 1/10/2021\n",
    "\n",
    "# read in Philly Fed Real GDP in levels\n",
    "df = pd.read_excel(io='Input_Data/Median_RGDP_Level.xlsx', sheet_name='Median_Level') #read in data\n",
    "\n",
    "# drop last col which shows up as NaT in index (not sure why this shows up...)\n",
    "df = df[df['YEAR'].notna()]\n",
    "\n",
    "# drop date before the 4th quarter of 1999\n",
    "df = df[124:]\n",
    "\n",
    "# set index to index of Philly data df. this is manually alligned by the authors\n",
    "# the alignment is done to push a quarterly 'release date' to the corresponding \n",
    "# observation quarter\n",
    "philly_dates = philly_dates.set_index(df.index)\n",
    "\n",
    "# set df index to philly fed period\n",
    "df = df.set_index(philly_dates['News Release Date'])\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# calculate the one period ahead pct change from 1evels \n",
    "df['g1'] = df[['RGDP1', 'RGDP2']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100*4, axis=1)\n",
    "\n",
    "# calculate the two period ahead pct change from 1evels \n",
    "df['g2'] = df[['RGDP2', 'RGDP3']].apply(lambda row: (row.iloc[1]-row.iloc[0])/row.iloc[0]*100*4, axis=1)\n",
    "\n",
    "# identify columns to retain\n",
    "median_GDP_forecasts = ['g1', 'g2']\n",
    "\n",
    "# filter for wanted columns\n",
    "median_GDP_forecasts = df.filter(median_GDP_forecasts, axis=1)\n",
    "\n",
    "# set index to observation date\n",
    "median_GDP_forecasts.index.name = 'observation_date'\n",
    "\n",
    "# merge dataframes to retain observations on FOMC meeting dates\n",
    "FOMC_gdp_forecast_median = pd.merge_asof(FOMC_df, median_GDP_forecasts, left_index = True, right_index = True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Vintage GDP Chain-Type Price Index Data from ALFRED File (Percent Change from a Year Ago)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "# URL: https://alfred.stlouisfed.org/series/downloaddata?seid=GDPCTPI\n",
    "# NOTE: Must select 'All' in the Vintage Dates section. Data as of 1/28/2021\n",
    "\n",
    "# read in ALFRED data\n",
    "df = pd.read_csv('Input_Data/GDPCTPI_2_Vintages_Starting_1996_01_19.txt', sep='\\t', na_values='.')\n",
    "\n",
    "# set index to observation date\n",
    "df.set_index('observation_date', inplace=True)\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df = df.dropna(how='all', axis=1)\n",
    "\n",
    "# calculate vintage percent change with helper function\n",
    "FOMC_price_hist = find_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format GDP Price Percent Change (Growth) Forecast from Philly Fed"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\micha\\miniconda3\\envs\\FOMC\\lib\\site-packages\\openpyxl\\worksheet\\header_footer.py:48: UserWarning: Cannot parse header or footer so it will be ignored\n",
      "  warn(\"\"\"Cannot parse header or footer so it will be ignored\"\"\")\n"
     ]
    }
   ],
   "source": [
    "# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp\n",
    "# Note: 'Median Responses' as of 1/12/2021\n",
    "\n",
    "#read in data\n",
    "df = pd.read_excel(io='Input_Data/Median_PGDP_Growth.xlsx', sheet_name='Median_Growth') #read in data\n",
    "\n",
    "# drop last col which shows up as NaT in index (not sure why this shows up...)\n",
    "df = df[df['YEAR'].notna()]\n",
    "\n",
    "# set length to correct Philly Fed release date length\n",
    "df = df[124:]\n",
    "\n",
    "# set index to index of Philly data df. this is manually alligned by the authors\n",
    "# the alignment is done to push a quarterly 'release date' to the corresponding \n",
    "# observation quarter\n",
    "philly_dates = philly_dates.set_index(df.index)\n",
    "\n",
    "# set df index to philly fed period\n",
    "df = df.set_index(philly_dates['News Release Date'])\n",
    "\n",
    "# # set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# remove blank rows\n",
    "df = df[df['DPGDP2'].notna()]\n",
    "\n",
    "# rename columns\n",
    "df['p1'] = df['DPGDP2']\n",
    "df['p2'] = df['DPGDP3']\n",
    "\n",
    "# identify columns to retain\n",
    "median_price_forecasts = ['p1', 'p2']\n",
    "\n",
    "# filter for wanted columns\n",
    "median_price_forecasts = df.filter(median_price_forecasts, axis=1)\n",
    "\n",
    "# set index to observation date\n",
    "median_price_forecasts.index.name = 'observation_date'\n",
    "\n",
    "# merge dataframes to retain observations on FOMC meeting dates\n",
    "FOMC_price_forecast_median = pd.merge_asof(FOMC_df, median_price_forecasts, left_index = True, right_index = True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Vintage PCE Chain-Type Price Index Data from ALFRED File"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "# URL: https://alfred.stlouisfed.org/\n",
    "# Note: Must select 'All' in the Vintage Dates section. \n",
    "# Data as of 2/8/2021\n",
    "\n",
    "# read in ALFRED data\n",
    "df = pd.read_csv('Input_Data/JCXFE_2_Vintages_Starting_1999_07_29.txt', sep='\\t', na_values='.')\n",
    "\n",
    "# set index to observation date\n",
    "df.set_index('observation_date', inplace=True)\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df = df.dropna(how='all', axis=1)\n",
    "\n",
    "# calculate vintage percent change with helper function\n",
    "FOMC_pce_hist = find_vintage_percent_chg(df, FOMC_dates, column_A_name='lp', column_B_name='p')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Core PCE Median Forecast Data from Philly Fed"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\micha\\miniconda3\\envs\\FOMC\\lib\\site-packages\\openpyxl\\worksheet\\header_footer.py:48: UserWarning: Cannot parse header or footer so it will be ignored\n",
      "  warn(\"\"\"Cannot parse header or footer so it will be ignored\"\"\")\n"
     ]
    }
   ],
   "source": [
    "# URL: https://www.philadelphiafed.org/surveys-and-data/pgdp\n",
    "# Note: 'Median Responses' as of 1/12/2021\n",
    "\n",
    "# read in data from file\n",
    "df = pd.read_excel(io='Input_Data/Median_COREPCE_Level.xlsx', sheet_name='Median_Level') #read in data\n",
    "\n",
    "# drop last col which shows up as NaT in index (not sure why this shows up...)\n",
    "df = df[df['YEAR'].notna()]\n",
    "\n",
    "# set length to correct Philly Fed release date length\n",
    "df = df[124:]\n",
    "\n",
    "# set index to index of Philly data df. this is manually alligned by the authors\n",
    "# the alignment is done to push a quarterly 'release date' to the corresponding \n",
    "# observation quarter\n",
    "philly_dates = philly_dates.set_index(df.index)\n",
    "\n",
    "# set df index to philly fed period\n",
    "df = df.set_index(philly_dates['News Release Date'])\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# remove blank rows\n",
    "df = df[df['COREPCE1'].notna()]\n",
    "\n",
    "# rename columns\n",
    "df['p1'] = df['COREPCE2']\n",
    "df['p2'] = df['COREPCE3']\n",
    "\n",
    "# identify columns to retain\n",
    "median_pce_forecasts = ['p1', 'p2']\n",
    "\n",
    "# filter for wanted columns\n",
    "median_pce_forecasts = df.filter(median_pce_forecasts, axis=1)\n",
    "\n",
    "# set index to observation date\n",
    "median_pce_forecasts.index.name = 'observation_date'\n",
    "\n",
    "# merge dataframes to retain observations on FOMC meeting dates\n",
    "FOMC_pce_forecast_median = pd.merge_asof(FOMC_df, median_pce_forecasts, left_index = True, right_index = True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Join GDP Price Data with Core PCE Data When Available"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\micha\\miniconda3\\envs\\FOMC\\lib\\site-packages\\pandas\\core\\frame.py:4438: SettingWithCopyWarning: \n",
      "A value is trying to be set on a copy of a slice from a DataFrame\n",
      "\n",
      "See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy\n",
      "  return super().rename(\n"
     ]
    }
   ],
   "source": [
    "# join historic and forecast gdp price data\n",
    "price_df = FOMC_price_hist.join(FOMC_price_forecast_median)\n",
    "\n",
    "# join historic and forecast pce data\n",
    "pce_df = FOMC_pce_hist.join(FOMC_pce_forecast_median)\n",
    "\n",
    "# slice gdp price data for pre 2007\n",
    "part1 = price_df[:'2007-01-31']\n",
    "\n",
    "# slice pce data for post 2007\n",
    "part2 = pce_df['2007-03-21':]\n",
    "\n",
    "# rename columns to conform to macro_df variables\n",
    "part1.rename(columns={\"pricel1\": \"lp\", \"price\": \"p\", \"pricef1med\": \"p1\", \"pricef2med\": \"p2\"},inplace = True)\n",
    "part2.rename(columns={\"pcel1\": \"lp\", \"pce\": \"p\", \"pcef1med\": \"p1\", \"pcef2med\": \"p2\"},inplace = True)\n",
    "\n",
    "# concat parts to single df\n",
    "FOMC_prices = pd.concat([part1, part2], axis=0)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format Vintage Core PCE Inflation Data -- for Taylor Regression"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "metadata": {},
   "outputs": [],
   "source": [
    "# read in ALFRED data\n",
    "# https://alfred.stlouisfed.org/\n",
    "# data as of 3/5/2021\n",
    "\n",
    "# read in core cpi data from file\n",
    "df = pd.read_csv('Input_Data/PCEPILFE_2_Vintages_Starting_2000_08_01.txt', sep='\\t', na_values='.')\n",
    "\n",
    "# set index to observation date\n",
    "df.set_index('observation_date', inplace=True)\n",
    "\n",
    "# set df index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df = df.dropna(how='all', axis=1)\n",
    "\n",
    "# calculate vintage percent changes with helper function\n",
    "FOMC_corepce_growth = find_price_growth(df, FOMC_dates[4:], column_A_name='corepce')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Calculate Output Gap from Real GDP and Trend Growth -- for Taylor Regression"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "metadata": {},
   "outputs": [],
   "source": [
    "# read in ALFRED data\n",
    "# https://alfred.stlouisfed.org/\n",
    "# data as of 2/10/2021\n",
    "\n",
    "# read in real gdp data from file\n",
    "df1 = pd.read_csv('Input_Data/GDPC1_2_Vintages_Starting_1991_12_04.txt', sep='\\t', na_values='.')\n",
    "\n",
    "# set index to observation date\n",
    "df1.set_index('observation_date', inplace=True)\n",
    "\n",
    "# trim dataframe\n",
    "df1 = df1['1959-07-01':]\n",
    "# df1 = df1['1980-01-01':]\n",
    "\n",
    "# remove bad benchmark year\n",
    "# should build this into the find growt f(n). do this if publishing. \n",
    "# Check if I wrote this into the gap function...\n",
    "df1 = df1.drop('GDPC1_19991028', axis = 1)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df1 = df1.dropna(how='all', axis=1)\n",
    "\n",
    "# calculate vintage growth gap with helper function\n",
    "FOMC_gdp_gap = find_growth_gap(df1, FOMC_dates, column_C_name = 'gdpgap')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Read in and Format FOMC Target Data from Author's Calculations Based on ALFRED Data"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {},
   "outputs": [],
   "source": [
    "# to save time, this work was imported from a previous calculation. we should rebuild here if published\n",
    "df = pd.read_csv('Input_Data/fomc_rates.csv', index_col=0)\n",
    "\n",
    "# name index for future merge\n",
    "df.index.name = 'observation_date'\n",
    "\n",
    "# set the index to datetime\n",
    "df.index = pd.to_datetime(df.index)\n",
    "\n",
    "# drop any remaining columns with no observations\n",
    "df = df.dropna(how='all', axis=0)\n",
    "\n",
    "# name dataframe for join\n",
    "FOMC_target_hist = df"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Combine Macro Data from ALFRED, FRED, & Philly Fed"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "metadata": {},
   "outputs": [],
   "source": [
    "macro_df = FOMC_gdp_hist.join([FOMC_gdp_forecast_median, FOMC_prices, FOMC_corepce_growth, FOMC_gdp_gap, FOMC_target_hist])\n",
    "macro_df.index.names = ['date']\n",
    "macro_df.to_csv('Output_Data/macro_df.csv')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
