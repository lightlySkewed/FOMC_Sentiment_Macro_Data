# FOMC-Shock-Macro-Variables

This repository contains all data files and associated code needed to generate the shocked version of our sentiment data.

Specifically, the code generates multi-horizon views of Real GDP and the Real GDP price level for each meeting of the FOMC from 2/2/2000 until 9/16/2020.

This project pulls heavily from Federal Reserve Bank of St. Louis's ALFRED database, and forecast data from the Federal Reserve Bank of Philadelphia's Survey of Professional Forecaster (SPF) database. Links to the data can be found in the code.

Specifically, the script (and helper functions) ingests ALFRED txt files and SPF xlsx files, calculates appropriate percent changes (where necessary) and combines the data into a single dataframe or optional csv file.

Developed using: 
Python 3.8.5
Jupyter Notebook

Dependencies include:
sklearn
Pandas
datetime
iGetByWithALittle.py


NOTES:

RGDP or GDP: This is U.S. Real (inflation-adjusted) Gross Domestic Product (RGDP), a measure of growth for the United States economy. It can be thought of as the sum of all goods sold at a certain price over a period. In this dataset it is expressed in percent change for stationarity purposes.

PGDP/ GDP Price Index: This is the GDP price index. While it captures price inflation in a manner similar to PCE (above), it differs in two primary ways for the purpose of this research. 1) This index includes not only food and energy prices, but all prices which contribute to U.S. GDP -- making it potentially more volatile. 2) It is included as a variable in the SPF survey from the beginning, and therefor offers us a much deeper history.
