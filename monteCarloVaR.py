# Last Updated: 22/07. This module contains functions whjch calculate the Monte Carlo VaR for both single assets
# and for multi asset portfolios.

import numpy as np
import scipy.linalg   # SciPy Linear Algebra Library

# Calculates the lower triangular Cholesky matrix (L) of the variance-covariance matrix (E) such that LL^T = E
# NOTE: Currently not required for multivariate normal distributions as numpy calculates this automatically in
# numpy.random.multivariate_normal
def choleskyMatrix(covarmatrix):
    matrix = scipy.linalg.cholesky(covarmatrix,lower=True)
    return matrix

# Python's built in random number generator which builds normally distributed random sequences using the Mersenne
# Twister algorithm. Returns a numpy array of (n x repetitions), where n is the number of assets
def pythonNormRand(muvector, cov, repetitions):
    randarray = np.random.multivariate_normal(muvector, cov, repetitions)
    return randarray


