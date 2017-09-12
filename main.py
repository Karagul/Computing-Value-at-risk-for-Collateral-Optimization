# SCRIPT 7: This script optimizes the overall CVaR of a portfolio across several exchanges. It requires the wikifutures.csv
# metadata.

import monteCarloVaR
import optimization
import numpy as np
from numpy import genfromtxt
import pandas as pd
import plotData
import matplotlib.pyplot as plt
import time
import readData

p = readData.readQuandl(["CHRIS/ICE_M1.1", "CHRIS/CME_W1.1"], 1000, True )
q = readData.cleanData(p)

x = time.clock()

optimization.exchangeOptimize(q, ["CHRIS/ICE_M1","CHRIS/CME_W1"], [0.1, 0.9],
                              "CHRIS/CME_W1", "Historical", 1, 1000)

y = time.clock()

print("Optimization time is " + str(y-x))

