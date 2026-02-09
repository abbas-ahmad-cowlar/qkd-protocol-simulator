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


def binary_entropy(p):
    """Compute the binary entropy h(p) = -p log2(p) - (1-p) log2(1-p).

    Physics: h(p) is the Shannon entropy of a Bernoulli variable. It is the
    workhorse function for DV-QKD security:
        - BB84 key rate (ideal, f_ec = 1):  R = 1 - 2 h(QBER)
        - Ideal security threshold:         h(QBER) = 0.5  ->  QBER ~= 0.110027

    Parameters
    ----------
    p : float or numpy.ndarray
        Error probability or array of probabilities. Must lie in [0, 1].

    Returns
    -------
    float or numpy.ndarray
        Binary entropy in bits. Returns 0.0 at p = 0 and p = 1.

    Raises
    ------
    ValueError
        If any value of p lies outside [0, 1].
    """
    p_arr = np.asarray(p, dtype=float)
    if np.any(p_arr < 0) or np.any(p_arr > 1):
        raise ValueError(
            f"p must be in [0, 1], got min={p_arr.min()}, max={p_arr.max()}"
        )

    out = np.zeros_like(p_arr)
    mask = (p_arr > 0) & (p_arr < 1)
    pm = p_arr[mask]
    out[mask] = -pm * np.log2(pm) - (1 - pm) * np.log2(1 - pm)

    return _return_scalar_if_scalar(p, out)


