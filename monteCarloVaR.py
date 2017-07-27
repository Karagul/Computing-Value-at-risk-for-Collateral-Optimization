# Last Updated: 22/07. This module contains functions whjch calculate the Monte Carlo VaR for both single assets
# and for multi asset portfolios.

import numpy as np
import scipy.linalg   # SciPy Linear Algebra Library

# Calculates the lower triangular Cholesky matrix (L) of the variance-covariance matrix (E) such that LL^T = E
def choleskyMatrix(covarmatrix):
    matrix = scipy.linalg.cholesky(covarmatrix,lower=True)
    return matrix


