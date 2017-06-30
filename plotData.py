import matplotlib.pyplot as plt

# Plot all of the columns of the time series
def plotSeries(mydata):
    plt.plot(mydata)
    plt.show()

# Plot the Open price of the time series
def plotOpen(mydata):
    plt.plot(mydata['Open'])
    plt.show()

