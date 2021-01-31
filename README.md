# FOMC-Shock-Macro-Variables
Contains code and files to generate multi-horizon views of RGDP and PCE

This project was developed to format and combine; historical vintage data from the Federal Reserve Bank of St. Louis's ALFRED database, and forecast data from the Federal Reserve Bank of Philadelphia's Survey of Professional Forecaster (SPF) database.

Specifically, the script (and helper functions) ingests ALFRED xls files and SPF xlsx files, calculates appropriate percent changes (where necessary) and combines the data into a single dataframe or optional csv file.

Developed using: 
Python 3.8.5
Jupyter Notebook

Dependencies:
Pandas
ipdb
iGetByWithALittle

NOTES:

RGDP or GDP: This is U.S. Real (inflation-adjusted) Gross Domestic Product (RGDP), a measure of growth for the United States economy. It can be thought of as the sum of all goods sold at a certain price over a period. In this dataset it is expressed in percent change for stationarity purposes.

PCE: This is the U.S. Core Personal Consumption Expenditure Price Index. It is a measure of inflation sans food and energy prices, which are removed to reduce unnecessary variance from the time series. This data only has forecasts starting in 2007. As such, it is not included in the final output, but may be in the future.

PGDP/ GDP Price Index: This is the GDP price index. While it captures price inflation in a manner similar to PCE (above), it differs in two primary ways for the purpose of this research. 1) This index includes not only food and energy prices, but all prices which contribute to U.S. GDP -- making it potentially more volatile. 2) It is included as a variable in the SPF survey from the beginning, and therefor offers us a much deeper history.

Miles: See the last frame of the notebook. I built a single df (named 'macro_data') that contains only the growth (gdp) and inflation (price index) data that we want to use for the initial regressions. Hope it helps.
