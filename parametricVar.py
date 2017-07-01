import statistics as st
from scipy.stats import norm
import numpy as np

# Calculates the most recent VaR value of a single asset.
def dailySingleParametricVar(retdata, confidence, windowsize):
    window = retdata['Returns'][-windowsize:]
    mean = st.mean(window)
    sd = st.pstdev(window)
    singleVaR = -norm.ppf(1-confidence/100, mean, sd) # Inv norm distribution of specified percentile, multiplied by -1
    return singleVaR

# Calculates multiple VaR values (ie for different dates) of a single asset.
def nondailySingleParametricVar(retdata, confidence, windowsize):
    VaRlist = []
    for index in range(windowsize-1, len(retdata)-1):
        window = retdata['Returns'][index:index+windowsize-1]
        mean = st.mean(window)
        sd = st.pstdev(window)
        singleVaR = -norm.ppf(1 - confidence / 100, mean, sd)
        VaRlist.append(singleVaR)

    retdata.drop(retdata.index[:windowsize], inplace=True)  # Drops the first row
    retdata['VaR'] = VaRlist
    return(retdata)

# Calculates the most recent VaR values of a multi asset.
def dailyMultiParametricVar(retdata, confidence, windowsize):
    VarList = []
    for asset in retdata:
        window = retdata[asset][-windowsize:]
        mean = st.mean(window)
        sd = st.pstdev(window)
        singleVaR = -norm.ppf(1-confidence/100, mean, sd) # Inv norm distribution of specified percentile, multiplied by -1
        VarList.append(singleVaR)
    return VarList

# Calculates and returns the variance-covariance matrix of a cleaned dataset of returns
def varCovarMatrix(cleandata):
    matrix = np.cov(cleandata, rowvar=False)
    return  matrix

# Calculates and returns the correlation matrix of a cleaned dataset of returns.
def correlationMatrix(cleandata):
    cov = varCovarMatrix(cleandata)
    # Iterate over the data and multiply all of the standard deviations (totalstd)
    totalstd = 1
    for asset in cleandata:
        assetstd = st.pstdev(cleandata[asset])
        totalstd = totalstd * assetstd
    correlation = cov/totalstd
    return correlation












