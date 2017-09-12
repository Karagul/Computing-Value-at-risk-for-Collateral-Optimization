# SCRIPT 5
# This script profiles Monte Carlo simulations with a portfolio consisting of 5 assets, a confidence of 99\% and a
# lookback period of 2000 business days. A number of values are used for the simulations:
# 16,160,1600,16000, 160000, 1600000

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

# Read and clean the single multi data with a lookback of 2000 business days.
dirtydata = readData.readQuandl(["CHRIS/ICE_CC4.1", "CHRIS/ASX_UB6.1", "CHRIS/ASX_WM1.1", "CHRIS/ASX_VW1.1", "CHRIS/ASX_WM2.1"], 2000, True)
cleandata = readData.cleanData(dirtydata)

# Perform a multi asset Monte Carlo VaR calculation, with 250 simulations.

rangeOfSimulations = [16,160,1600,16000, 160000, 1600000]
results = []
for simulations in rangeOfSimulations:
    t4 = time.clock()

    monteReturns = monteCarloVaR.portfolioMonteCarlo(cleandata, [0.1, 0.2, 0.3, 0.25, 0.15], simulations)

    t5 = time.clock()
    monteVaR = historicalVaR.historicalSingleVaR(monteReturns, 99)

    t6 = time.clock()
    results.append(t6-t4)

    print("VaR time was: " + str(t6- t5))
    print(str(t5-t4))

plt.plot(rangeOfSimulations, results)
plt.xscale('log')
plt.grid('on')
plt.show()
