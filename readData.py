# Last Updated: 05/07. This module contains functions whjch allow the use to enter a portfolio and to preprocess
# time series data.

import quandl
import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay # BDay is business day

# Allows more than 50 data requests per day from Quandl
quandl.ApiConfig.api_key = ""

# Reads time series and obtains daily returns if desired for specified derivatives on Quandl
def readQuandl(derivativelist, lookback, returns):
    today = pd.datetime.today()
    start = today - BDay(lookback)
    if returns == True:
        mydata = quandl.get(derivativelist, start_date = start, end_date = today,
                            transformation = 'rdiff', rows = lookback)
    else: mydata = quandl.get(derivativelist, start_date = start, end_date = today, rows = lookback)
    return mydata

# Zero's are assumed to be missing values, and are replaced with NaN.
# Missing data is filled in using linear interpolation for all columns.
# NaN at the start and end of a column are replaced with ~ 0 TODO: Change to random interpolation with same variance?
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

# Obtains portfolio weights as an input from the user. TODO: Add in exceptions for incorrect entries
def portfolioWeights():
    weights = [float(x) for x in input("Enter a list of weights which sum to 1, separated by spaces: ").split()]
    return weights

# Obtains returns for specified T day intervals (not T=1), since Quandl only calculates
# returns for T=1. Useful for historical simulations. TODO: Add in raw returns capability for all read data
def alternativeHistReturns(derivativelist, lookback, T):
    rawdata = readQuandl(derivativelist, lookback+T, False)
    cleanrawdata = cleanData(rawdata)
    for derivative in cleanrawdata:
        index = len(cleanrawdata)-1
        while index >= T and index > 0:
            indexedreturn = cleanrawdata[derivative][index]/cleanrawdata[derivative][index-T] - 1
            cleanrawdata[derivative][index] = indexedreturn
            index = index - 1
    cleanrawdata.drop(cleanrawdata.index[:T], inplace=True)  # Drops the first T rows
    return cleanrawdata

