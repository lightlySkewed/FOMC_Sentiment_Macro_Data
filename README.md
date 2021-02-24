# FOMC-Shock-Macro-Variables

This repository contains all data files and associated code needed to generate the shocked version of our sentiment data and run the subsequent Taylor and ordinal (predictive) regressions.

Specifically, this code does several things:
	
1) It generates multi-horizon views of Real GDP Growth, real GDP price level Growth, and core PCE price level growth for each meeting of the FOMC from 2/2/2000 until 9/16/2020. These are horizons are then used to 'shock' our raw sentiment signal, in order to remove potential endogeneity issues from the subsequent Taylor and predictive models.
	
2) It ingests and formats Fed Funds rate, corecpi, and Real GDP data for the subsequent Taylor and predictive models.
	
3) It combines and aligns all of the data before outputting the data into a dataframe 'macro_df.csv'

Our aim was to make this research as easily replicable as possible. Therefore, variable selection hinged on the ease of aquizition and use. This project pulls heavily from Federal Reserve Bank of St. Louis's ALFRED database, and forecast data from the Federal Reserve Bank of Philadelphia's Survey of Professional Forecaster (SPF) database. Links to the data can be found in the code.

This constraint meant that we had to make several adaptations in the work. First, it meant that we had to use the GDP price level (rather than core PCE, which we believe the Fed watches slightly more closely) prior to 2007, as this is when the SPF first began tracking forecasts on core PCE. In our experiments, we blend GDP price and core PCE, with core PCE starting at 2007. Second, monthly core PCE vintages are housed at ALFRED starting in 2013. We therefore use core CPI as an analogous measure, as ALFRED houses real-time data for this series beginning before 2000. The reason for being picky about the data vintage availability is that (per Orphanides 1997) we aim to recreate the world as it existed just prior to each Federal Reserve meeting that we study. This means only looking at the data that were available at any on point in time. Examples of this can be found in the paper.

A keen reader will also note that we use one measure of price for our shock variables, and another for our Taylor and predictive models. This, too, is based largely on what was available to us, but we show that alternative specifications, while somewhat ex-post due to the vintages which were available cause our estimate to suffer little effect.

Finally, it is important to note that the 'release dates' that we use for the release of the SPF are purely fiction generated by these authors. While there is no known historica release calendar of the SPF data, The Federal Reserve Bank of Philadelphia does provide a rough outline on approximating these dates here:

https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/spf-documentation.pdf?la=en&hash=F2D73A2CE0C3EA90E71A363719588D25

These dates were approximated using rules in Excel, and can be found in the Input Data folder of this repository.

Developed using: 
Python 3.8.5
Jupyter Notebook

Dependencies include:
Pandas
datetime
statsmodels.formula.api
iGetByWithALittle.py


NOTES:

RGDP or GDP: This is U.S. Real (inflation-adjusted) Gross Domestic Product (RGDP), a measure of growth for the United States economy. It can be thought of as the sum of all goods sold at a certain price over a period. In this dataset it is expressed in percent change for stationarity purposes.

Core CPI: Measures inflation from the aspect of the consumer. Absent more volitile food and energy prices. Produced by the BEA.

Core PCE: Measures inflation from the aspect of the consumer. Absent more volitile food and energy prices. Differs from CPI primarily in construction method (Fisher-Ideal instead of Laspeyres), and component weights. Produced by the BLS.

GDP Price Index: Measures inflation from the perspective of consumers, producers (businesses), and the Government. While it captures price inflation in a manner similar to PCE (above), it differs in two primary ways for the purpose of this research. 1) This index includes not only food and energy prices, but all prices which contribute to U.S. GDP -- making it more volatile. 2) It is included as a variable in the SPF survey from the beginning, and therefor offers us a much deeper history. This contrasts with core PCE and core CPI, which are available only from 2007 on. Produced by the BEA.
