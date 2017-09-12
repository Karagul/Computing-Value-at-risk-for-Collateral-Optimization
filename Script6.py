# SCRIPT 6: This script demonstrates the alternative asset optimization algorithm using a small portfolio of assets and
# the Monte Carlo method of VaR calculation.

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

p = readData.readQuandl(["CHRIS/ICE_M1.1", "CHRIS/CME_W1.1"], 200, True )
q = readData.cleanData(p)

x = time.clock()

optimization.optimizeSimilarAssets(q, ["CHRIS/ICE_M1.1","CHRIS/CME_W1.1"], [0.1, 0.9],
                              "CHRIS/ICE_M1.1", ["CHRIS/SHFE_CC4.1"], "Monte Carlo", 1, 200, 99)

y = time.clock()

print("Optimization time is " + str(y-x))
