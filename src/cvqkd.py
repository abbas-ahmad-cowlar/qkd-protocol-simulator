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

