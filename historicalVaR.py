import statistics as st
from scipy.stats import norm
import numpy as np

# Given a distribution of returns and a validity period T, this function calculates the historical VaR for a single
# asset.
def historicalSingleVaR(cleanasset, confidence):
    negVaR = np.percentile(cleanasset, 1-confidence)  # returns the 1-confidence percentile
    VaR = abs(negVaR)
    return VaR

# Calculates historical VaR for a given portfolio
def historicalPortfolioVaR(cleanasset, confidence):
    negVaR = np.percentile(cleanasset, 1-confidence)  # returns the 1-confidence percentile
    VaR = abs(negVaR)
    return VaR




