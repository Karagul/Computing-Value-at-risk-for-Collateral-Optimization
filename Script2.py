# SCRIPT 2
# This script calculates the historical, parametric, and Monte Carlo VaR of a single asset portfolio
# with an inital lookback period of 5000 days, a confidence of 90% for a single day into the future. For the Monte Carlo
# method, 2500 simulations were chosen. This script compares the three values and profiles the code.

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

# Read and clean the single asset data with a lookback of 5000 business days.
dirtydata = readData.readQuandl(["CHRIS/ICE_CC4.1"], 5000, True)
cleandata = readData.cleanData(dirtydata)

t2 = time.clock()

# Perform a single asset parametric VaR calculation

paraVaR = parametricVaR.singleParametricVaR(cleandata, 90, 1)

t3 = time.clock()

# Perform a single asset historical VaR calculation

histVaR = historicalVaR.historicalSingleVaR(cleandata, 90)

t4 = time.clock()

# Perform a single asset Monte Carlo VaR calculation, with 250 simulations.

monteReturns = monteCarloVaR.singleMonteCarlo(cleandata, [0,1], 2500)
monteVaR = historicalVaR.historicalSingleVaR(monteReturns, 90)

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


