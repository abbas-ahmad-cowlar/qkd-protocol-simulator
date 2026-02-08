"""
Information Theory Utility Module
==================================

Entropy and mutual-information primitives for QKD analysis, including
Gaussian entropy used later in Holevo-bound calculations.
All functions operate on NumPy arrays for vectorized distance sweeps.

Functions:
    1. _return_scalar_if_scalar(x, out)  -- Scalar/array ergonomics
    2. binary_entropy(p)                 -- h(p) = -p log2(p) - (1-p) log2(1-p)
    3. shannon_entropy(probs)            -- H(X) = -sum p(x) log2(p(x))
    4. mutual_information(p_xy)          -- I(X;Y) from joint distribution
    5. gaussian_entropy(nu, tol)         -- von Neumann entropy from symplectic eigenvalue

Conventions:
    * All entropies are in bits (log base 2).
    * 0 * log2(0) := 0 (handled via boolean masking, not scalar ifs, so the
      functions remain vectorized over NumPy arrays).
    * Gaussian convention: vacuum variance = 1, so symplectic eigenvalues
      satisfy nu >= 1; nu = 2*nbar + 1 in this convention.

"""

import numpy as np


def _return_scalar_if_scalar(x, out):
    """Return a Python float when x was a scalar; otherwise return the array.

    Keeps notebook printing and downstream plotting clean: scalar inputs
    produce plain floats, while array inputs preserve the array type.

    Parameters
    ----------
    x : scalar or array-like
        The original input before np.asarray conversion.
    out : numpy.ndarray
        The computed result array.

    Returns
    -------
    float or numpy.ndarray
    """
    if np.ndim(x) == 0:
        return float(out)
    return out


