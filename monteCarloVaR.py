# Last Updated: 22/07. This module contains functions whjch calculate the Monte Carlo VaR for both single assets
# and for multi asset portfolios.

import numpy as np
import scipy.linalg   # SciPy Linear Algebra Library
import parametricVaR
import matplotlib.pyplot as plt
import time
from numpy import genfromtxt
import readData

# Calculates the lower triangular Cholesky matrix (L) of the variance-covariance matrix (E) such that LL^T = E
def choleskyMatrix(covarmatrix):
    matrix = scipy.linalg.cholesky(covarmatrix,lower=True)
    return matrix

# Python's built in random number generator which builds normally distributed random sequences using the Mersenne
# Twister algorithm. Inputs are a vector of mean values for each risk factor, their covariance matrix, and a specified
# number of repetitions. Returns a numpy array of (n x repetitions), where n is the number of risk factors
def multiNormRand(muvector, cov, repetitions):
    randarray = np.random.multivariate_normal(muvector, cov, repetitions)
    return randarray

# Python's built in random number generator for calculations involving single asset portfolios.
def singleNormRand(mu, var, repetitions):
   # randarray = np.random.normal(mu, np.sqrt(var),repetitions)
    randarray = np.random.normal(0, 1, repetitions)
    return randarray

# This function is the Geometric Brownian Motion Calculator for a single risk factor at time (t(i+1)).
# initialvalue is the value of the risk factor at the current timestep t(i). timestep = t(i+1) - t(i)
def gbm(mu, random, var, timestep):
    nu = mu - var/2
    #newvalue = previousvalue*np.exp(nu*timestep + np.sqrt(var*timestep)*random)
    newvalue = mu * timestep +  np.sqrt(var*timestep) * random
    return newvalue

# This function performs a portfolio Monte Carlo simulation based on Geometric Brownian Motion. It differes from the
# "portfolioMonteCarlo" function in that it accepts a timesteplist and plots it as well.
# Timesteplist consists of a list starting with 0 of desired time intervals (in days) for which the MC simulation is
# performed. This function allows the plotting of the time series data to illustrate the Monte Carlo simulation process.
def portfolioMonteCarlo2(cleandata, timesteplist, weights, repetitions):

    muvector = np.mean(cleandata)
    cov = parametricVaR.varCovarMatrix(cleandata)
    cor = parametricVaR.correlationMatrix(cleandata)
    chol = choleskyMatrix(cor)
    replist = []

    # Random number generationL: Generates a triple nested list. Innermost lists are st
    # standard normally distributed random data of size replist. These are arranged in chunks of size asset length,
    # before being contained in chunks, one for each timestep.
    randomList = []
    for timeindex in range(len(timesteplist) - 1):
        assetChunks = []
        for index in range(len(muvector)):
            normalValues = singleNormRand(0,1,repetitions)
            assetChunks.append(normalValues)
        assetChunksTransposed = list(np.transpose(np.asarray(assetChunks)))
        randomList.append(list(assetChunksTransposed))

    for rep in range(1, repetitions+1):
        portfoliolist = [0]
        historicassetlist = []

        for timeindex in range(1, len(timesteplist)):
            timestep = timesteplist[timeindex] - timesteplist[timeindex - 1]
            assetlist = []

            randomChunk = randomList[timeindex-1]

            independentRandomVector = randomChunk.pop()
            randomCorrelatedVector = np.dot(chol, independentRandomVector)

            for asset in range(len(muvector)):
                # Obtain inputs for the gbm function
                mu = muvector[asset]
                random = randomCorrelatedVector[asset]
                var = cov[asset][asset]
                newassetvalue = gbm(mu, random, var, timestep)
                assetlist.append(newassetvalue) # assetlist for a specific time index

            # valuate the portfolio at timeindex
            portfoliovalue = np.dot(weights, assetlist)
            portfoliolist.append(portfoliovalue)
            historicassetlist.append(list(assetlist))

        replist.append(portfoliolist[-1])
        # Plot generated time series
        plt.plot(portfoliolist)

    plt.show()

    return replist

# Monte Carlo simulations for a single asset
def singleMonteCarlo(cleandata, timesteplist, repetitions):
    mu = np.mean(cleandata)
    var = np.var(cleandata)
    # There is a new random vector for each timestep and for each each repetition
    randomarray = singleNormRand(mu, var, repetitions * (len(timesteplist) - 1))
    replist = []

    for rep in range(1, repetitions + 1):
        timelist = []

        for timeindex in range(1, len(timesteplist)):
            timestep = timesteplist[timeindex] - timesteplist[timeindex - 1]

            random = randomarray[(rep - 1) * (len(timesteplist) - 1) + (timeindex - 1)]
            newassetvalue = gbm(mu, random, var, timestep)
            timelist.append(newassetvalue)  # asset values for different times

        replist.append(timelist[len(timelist) - 1])

    return replist


# This function performs a portfolio Monte Carlo simulation based on Geometric Brownian Motion.
# This function does NOT allow the plotting of  the time series, and is only calculates VaR for the next day.
def portfolioMonteCarlo(cleandata, weights, repetitions):

    muvector = np.mean(cleandata)
    covar = parametricVaR.varCovarMatrix(cleandata)
    cor = parametricVaR.correlationMatrix(cleandata)
    chol = choleskyMatrix(cor)
    replist = []

    # Random number generation: Generates a triple nested list. Innermost lists are st
    # standard normally distributed random data of size replist. These are arranged in chunks of size asset length,
    # before being contained in chunks, one for each timestep.
    ranstart = time.clock()
    randomChunk = []
    for index in range(len(muvector)):
        normalValues = singleNormRand(0,1,repetitions)
        randomChunk.append(normalValues)

    randomChunkTransposed = list(np.transpose(np.asarray(randomChunk)))
    ranend = time.clock()
    print("Random time is: " + str(ranend-ranstart))

    montestart = time.clock()
    for rep in range(1, repetitions+1):
        assetlist = []

        independentRandomVector = randomChunkTransposed.pop()
        randomCorrelatedVector = np.dot(chol, independentRandomVector)

        for asset in range(len(muvector)):
            # Obtain inputs for the gbm function
            mu = muvector[asset]
            random = randomCorrelatedVector[asset]
            var = covar[asset][asset]

            newassetvalue = gbm(mu, random, var, 1)
            assetlist.append(newassetvalue) # assetlist for a specific time index

        # valuate the portfolio at timeindex
        portfoliovalue = np.dot(weights, assetlist)
        replist.append(portfoliovalue)
    monteend = time.clock()
    print("Monte time was: " + str(monteend - montestart))

    return replist


# This function generates and saves correlated random numbers. The input is a given CSV of financial data. The output is
# a CSV file containing random numbers for each CSV. This is only for a single timestep.
def randomCSV(inputFile, csvfilename, repetitions):

    # Read the inputFile, each list is a row of prices for different assets
    my_data = genfromtxt(inputFile, delimiter=',')
    # Calculate the Cholesky matrix
    data = np.asarray(np.transpose(my_data))
    cor = parametricVaR.correlationMatrix(data)
    chol = choleskyMatrix(cor)

    # Generation of random numbers
    # Random number generation: Generates a double nested list.
    randomList = []
    for index in range(len(my_data)):
        normalValues = singleNormRand(0,1,repetitions)
        randomList.append(normalValues)

    randomListT = list(np.transpose(randomList))

    # Apply Cholesky to each array of randomListT
    finalList = []
    for assetValues in randomListT:
        correlatedValues = np.dot(chol,assetValues)
        finalList.append(correlatedValues)

    # Save the random numbers in a CSV
    np.savetxt(csvfilename, finalList, delimiter=",")