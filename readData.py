import quandl
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day

# Allows more than 50 data requests per day from Quandl
quandl.ApiConfig.api_key = ""

# Reads time series and obtains returns for specified derivatives on Quandl
def readQuandl(derivativelist, lookback):
    today = pd.datetime.today()
    start = today - BDay(lookback)
    mydata = quandl.get(derivativelist, start_date = start, end_date = today, transformation = 'rdiff', rows = lookback)
    return mydata

# Zero's are assumed to be missing values, and are replaced with NaN.
# Missing data is filled in using linear interpolation for all columns.
# NaN at the start and end of a column are replaced with ~ 0 (FUTURE: CHANGE LINEAR INTERPOLATION?)
def cleanData(mydata):
    mydata2 = mydata.replace(0, np.NaN)
    if mydata2.isnull().values.any():
        print("Dataset Contains NA or 0 values")
        mydata3 = mydata2.interpolate()
        mydata3 = mydata3.fillna(0.000000001)
        return mydata3
    else:
        return mydata2

# Missing data is filled in using linear interpolation 'Open' only.
def cleanOpen(mydata):
    if mydata['Open'].isnull().values.any():
        print("Open Contains NA values")
        mydata['Open'] = mydata['Open'].interpolate()
    return mydata

# Converts series of prices to one of returns. CURRENTLY NOT REQUIRED AS get.quandl DOES THIS FOR US
def tick2ret(series):
    retdata = pd.DataFrame(series['Open'])
    prices = series['Open']
    retlist = []

    index = 1
    while index < len(prices):
        ret = (prices[index]-prices[index-1])/prices[index-1]
        retlist.append(ret)
        index += 1

    retdata.drop(retdata.index[:1], inplace=True) # Drops the first row
    retdata['Returns'] = retlist
    return retdata


