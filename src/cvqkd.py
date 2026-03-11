"""
CV-QKD Protocol Module
=======================

Continuous-variable QKD: GG02 protocol (Grosshans & Grangier, 2002) with
two-quadrature Gaussian modulation and homodyne detection. The Holevo
bound is computed from the symplectic eigenvalues of the joint Alice-Bob
covariance matrix in normal form.

Convention contract (CRITICAL)
------------------------------
Vacuum variance = 1, shot-noise units, hbar = 2. Under this convention:

* coherent / vacuum state covariance: ``gamma = I``
* thermal state with mean photon number nbar: ``gamma = (2*nbar + 1) * I``
* symplectic eigenvalue of vacuum: ``nu = 1``
* physical states: ``nu >= 1`` (uncertainty principle)

``gaussian_entropy(nu)`` from ``src.info_theory`` expects a symplectic
eigenvalue, NOT a variance.

Reference
---------
Laudenbach, Pacher, Pacher, Lechner, Schrenk, Hentschel, Walenta,
Hubel, Poppe (2018), "Continuous-Variable Quantum Key Distribution with
Gaussian Modulation -- The Theory of Practical Implementations",
Adv. Quantum Technol. 1800011, arXiv:1703.09278, Sections 6-7.
"""

import numpy as np

from src.channel import fiber_transmittance
from src.info_theory import gaussian_entropy


# ---------------------------------------------------------------------------
# Mutual information
# ---------------------------------------------------------------------------

def cvqkd_mutual_info_homodyne(V_A, eta, xi):
    """Alice-Bob mutual information for homodyne GG02.

    Physics: Bob measures one quadrature with shot-noise variance 1 plus
    excess noise ``eta * xi``. With Alice's modulation variance ``V_A``
    and total transmittance ``eta``, the per-symbol mutual information is

        I(A:B) = (1/2) * log2(1 + eta * V_A / (1 + eta * xi))

    The leading 1/2 is because homodyne measures only one quadrature per
    pulse.

    Parameters
    ----------
    V_A : float
        Alice's modulation variance in shot-noise units. ``V_A >= 0``.
    eta : float or numpy.ndarray
        Total transmittance (channel * detector) in [0, 1].
    xi : float
        Input-referred excess noise in shot-noise units. ``xi >= 0``.

    Returns
    -------
    float or numpy.ndarray
        Mutual information in bits / symbol.
    """
    eta_arr = np.asarray(eta, dtype=float)
    if np.any((eta_arr < 0.0) | (eta_arr > 1.0)):
        raise ValueError("eta must be in [0, 1]")
    if V_A < 0 or xi < 0:
        raise ValueError("V_A and xi must be nonnegative")
    snr = eta_arr * V_A / (1.0 + eta_arr * xi)
    return 0.5 * np.log2(1.0 + snr)


