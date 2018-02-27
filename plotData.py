# Last Updated: 05/07. This module contains functions whjch plot time series and VaR data.

import matplotlib.pyplot as plt

def plotSeries(mydata):
    """Plot all of the columns of the time series """
    plt.plot(mydata)
    plt.show()

def plotOpen(mydata):
    """Plot the Open price of the time series """
    plt.plot(mydata['Open'])
    plt.show()

