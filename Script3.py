# SCRIPT 3
# This script calculates the historical, parametric, and Monte Carlo VaR of a multi asset portfolio of 5 assets,
# with an inital lookback period of 2500 days, a confidence of 99% for a single day into the future. For the Monte Carlo
# method, 20000 simulations were chosen. This script compares the three values and profiles the code.

import readData
import parametricVaR
import historicalVaR
import monteCarloVaR
import optimization
import numpy as np
from numpy import genfromtxt
import pandas as pd
import plotData
import matplotlib.pyplot as plt
import time

t1 = time.clock()

# Read and clean the multi asset data with a lookback of 5000 business days.
dirtydata = readData.readQuandl(["CHRIS/ICE_CC4.1", "CHRIS/ASX_UB6.1", "CHRIS/ASX_WM1.1", "CHRIS/ASX_VW1.1", "CHRIS/ASX_WM2.1"], 2500, True)
cleandata = readData.cleanData(dirtydata)

t2 = time.clock()

# Perform a multi asset parametric VaR calculation

paraVaR = parametricVaR.paraPortfolioVaR(cleandata, [0.1, 0.2, 0.3, 0.25, 0.15], 99, 1)

t3 = time.clock()

# Perform a multi asset historical VaR calculation

histVaR = historicalVaR.historicalPortfolioVaR(cleandata, 99, [0.1, 0.2, 0.3, 0.25, 0.15] )

t4 = time.clock()

# Perform a multi asset Monte Carlo VaR calculation, with 250 simulations.

monteReturns = monteCarloVaR.portfolioMonteCarlo(cleandata, [0.1, 0.2, 0.3, 0.25, 0.15], 20000)
monteVaR = historicalVaR.historicalSingleVaR(monteReturns, 99)

t5 = time.clock()

print("Parametric Results are: " )
print(paraVaR)
print("Historic Results are: " )
print(histVaR)
print("Monte Carlo Results are: " )
print(monteVaR)
print("Read time is: ")
print(str(t2-t1))
print("Parametric time is: ")
print(str(t3-t2))
print("Historical time is: ")
print(str(t4-t3))
print("Monte Carlo time is: ")
print(str(t5-t4))


