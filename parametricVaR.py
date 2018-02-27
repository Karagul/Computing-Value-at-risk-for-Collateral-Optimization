# Last Updated: 05/07. This module contains functions whjch calculate the Parametric VaR for both single assets
# and for multi asset portfolios.

import statistics as st
from scipy.stats import norm
import numpy as np

def singleParametricVaR(retdata, confidence, T):
    """Calculates the most recent VaR value of a single asset, for T days into the future. """
    npdata = np.asarray(retdata)
    mean = np.mean(npdata)
    z = norm.ppf(1 - confidence / 100)        # Inv standard normal distribution of specified percentile
    sd = np.sqrt(np.var(npdata))
    singleVaR = abs(mean*T - z*sd*np.sqrt(T)) # Inv norm distribution of specified percentile, multiplied by -1
    return singleVaR

def singleParametricCVaR(retdata, confidence, T):
    """Calculates the most recent CVaR value of a single asset, for T days into the future. """
    npdata = np.asarray(retdata)
    mean = np.mean(npdata)
    z = norm.ppf(1 - confidence / 100)        # Inv standard normal distribution of specified percentile
    sd = np.sqrt(np.var(npdata))
    signedVaR = mean*T - z*sd*np.sqrt(T)
    if signedVaR > 0:
        CVaR = abs(mean*T - (sd*np.sqrt(T)*norm.pdf(norm.ppf(1-confidence/100)))/(1-confidence/100))
    else: CVaR = 0
    return CVaR

def oldSingleParametricVaR(retdata, confidence, windowsize, T):
    """Calculates multiple VaR values (ie for different dates) of a single asset. """
    VaRlist = []
    for index in range(windowsize-1, len(retdata)-1):
        window = retdata['Returns'][index:index+windowsize-1]
        mean = st.mean(window)
        sd = st.pstdev(window)
        z = norm.ppf(1 - confidence / 100)
        singleVaR = abs(mean*T - z*sd*np.sqrt(T))  # Inv norm distribution of specified percentile, multiplied by -1
        VaRlist.append(singleVaR)

    retdata.drop(retdata.index[:windowsize], inplace=True)  # Drops the first row
    retdata['VaR'] = VaRlist
    return retdata

def dailyMultiParametricVaR(retdata, confidence, windowsize, T):
    """Calculates a list of VaR values for each asset. Note that this is not for a portfolio. """
    VarList = []
    for asset in retdata:
        window = retdata[asset][-windowsize:]
        mean = st.mean(window)
        sd = st.pstdev(window)
        z = norm.ppf(1 - confidence / 100)
        singleVaR = abs(mean*T - z*sd*np.sqrt(T))  # Inv norm distribution of specified percentile, multiplied by -1
        VarList.append(singleVaR)
    return VarList

def varCovarMatrix(cleandata):
    """Calculates and returns the variance-covariance matrix of a cleaned dataset of returns. """
    matrix = np.cov(cleandata, rowvar=False)
    return matrix

def correlationMatrix(cleandata):
    """Calculates and returns the correlation matrix of a cleaned dataset of returns. """
    matrix = np.corrcoef(cleandata, rowvar=False)
    return matrix

def portfolioVariance(cleandata, weights):
    """Calculates the variance of a multi asset portfolio. """
    covMatrix = varCovarMatrix(cleandata)
    weights = np.mat(weights)
    variance = weights*covMatrix*weights.transpose()
    variance2 = float(variance[0][0])                    # Flatten out the list into a scalar
    return variance2

def portfolioMean(cleandata, weights):
    """Calculates the mean return of a portfolio given a set of asset returns data and the portfolio weights """
    assetsMean = np.mean(cleandata)
    portfolioMean = np.dot(np.array(weights),assetsMean)
    return portfolioMean


def paraPortfolioVaR(cleandata, weights, confidence, T):
    """Calculates the value-at-risk for a portfolio given a set of clean asset data, confidence level, portfolio
    weights, and a period of validity for the VaR figure T (days) """
    mean = portfolioMean(cleandata, weights)
    variance = portfolioVariance(cleandata, weights)
    z = norm.ppf(1-confidence/100)                          # Inv standard normal distribution of specified percentile
    signedVaR = mean*T - z*np.sqrt(variance)*np.sqrt(T)
    if signedVaR > 0:
        VaR = abs(signedVaR)                                # Want the absolute value not a negative one
    else: VaR = 0
    return VaR


def paraPortfolioCVaR(cleandata, weights, confidence, T):
    """Calculates the conditional value-at-risk (CVaR) for a portfolio given a set of clean asset data, confidence
    level, portfolio weights, and a period of validity for the VaR figure T (days) """
    mean = portfolioMean(cleandata, weights)
    variance = portfolioVariance(cleandata, weights)
    z = norm.ppf(1-confidence/100)                      # Inv standard normal distribution of specified percentile
    signedVaR = mean*T - z*np.sqrt(variance)*np.sqrt(T)
    if signedVaR > 0:
        CVaR = abs(mean*T - (np.sqrt(variance)*np.sqrt(T)*norm.pdf(norm.ppf(1-confidence/100)))/(1-confidence/100))
    else: CVaR = 0
    return CVaR






