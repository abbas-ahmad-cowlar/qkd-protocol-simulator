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


def cvqkd_mutual_info_heterodyne(V_A, eta, xi):
    """Alice-Bob mutual information for heterodyne detection.

    Heterodyne measures both quadratures in one shot but pays one extra
    unit of vacuum noise per quadrature (the beam-splitter penalty), so

        I_het(A:B) = log2(1 + eta * V_A / (2 + eta * xi))

    Modeling caveat: this function is provided for the homodyne-vs-
    heterodyne mutual-information comparison only. The matching
    heterodyne Holevo bound is NOT implemented in this project, so do
    not use this function inside a secure-key-rate calculation.

    Parameters
    ----------
    V_A : float
        Alice's modulation variance in shot-noise units.
    eta : float or numpy.ndarray
        Total transmittance in [0, 1].
    xi : float
        Input-referred excess noise.

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
    snr = eta_arr * V_A / (2.0 + eta_arr * xi)
    return np.log2(1.0 + snr)


# ---------------------------------------------------------------------------
# Symplectic eigenvalues + Holevo bound
# ---------------------------------------------------------------------------

def _cvqkd_symplectic_eigenvalues_homodyne(V_A, eta, xi, eps=1e-12):
    """Return ``(nu1, nu2, nu3, a, b, c)`` for GG02 homodyne.

    Builds the joint Alice-Bob covariance matrix in normal form

        gamma_AB = [[a I, c Z], [c Z, b I]]

    with ``V = V_A + 1``, ``chi_line = 1/T - 1 + xi``, ``T = eta``,
    ``a = V``, ``b = T (V + chi_line)``, ``c = sqrt(T (V**2 - 1))``,
    then computes the two unconditional symplectic eigenvalues
    ``nu1, nu2`` and the conditional eigenvalue ``nu3`` after Bob's
    homodyne measurement of one quadrature. All three are clamped to
    ``>= 1`` to absorb floating-point noise (physical eigenvalues
    cannot drop below 1 under our convention).
    """
    eta_arr = np.asarray(eta, dtype=float)
    if np.any((eta_arr <= 0.0) | (eta_arr > 1.0)):
        raise ValueError("eta must be in (0, 1] for Holevo calculation")
    if V_A < 0 or xi < 0:
        raise ValueError("V_A and xi must be nonnegative")

    T = np.clip(eta_arr, eps, 1.0)
    V = V_A + 1.0
    chi_line = 1.0 / T - 1.0 + xi

    a = V * np.ones_like(T)
    b = T * (V + chi_line)
    c = np.sqrt(np.maximum(T * (V**2 - 1.0), 0.0))

    Delta = a**2 + b**2 - 2.0 * c**2
    det_gamma = (a * b - c**2) ** 2
    rad = np.maximum(Delta**2 - 4.0 * det_gamma, 0.0)

    nu1 = np.sqrt(np.maximum((Delta + np.sqrt(rad)) / 2.0, 1.0))
    nu2 = np.sqrt(np.maximum((Delta - np.sqrt(rad)) / 2.0, 1.0))
    nu3 = np.sqrt(np.maximum(a * (a - c**2 / b), 1.0))

    return nu1, nu2, nu3, a, b, c


def cvqkd_holevo_bound_homodyne(V_A, eta, xi, eps=1e-12):
    """Holevo bound chi(B:E) for reverse-reconciliation, homodyne GG02.

    Physics: the asymptotic collective-attack Gaussian Holevo bound
    against an entangling-cloner adversary is

        chi(B:E) = g(nu1) + g(nu2) - g(nu3)

    where ``g(nu)`` is the von Neumann entropy of a thermal mode with
    symplectic eigenvalue ``nu``, computed via
    ``info_theory.gaussian_entropy``. ``nu1, nu2`` come from the joint
    Alice-Bob covariance matrix; ``nu3`` is the conditional eigenvalue
    after Bob's homodyne measurement of one quadrature.

    Untrusted-detector model: the supplied ``eta`` should
    already include the detector efficiency, with all loss attributed to
    the channel available to Eve. The pure-state limit ``eta = 1,
    xi = 0`` yields ``nu1 = nu2 = nu3 = 1`` and ``chi = 0``.

    Parameters
    ----------
    V_A : float
        Alice's modulation variance in shot-noise units.
    eta : float or numpy.ndarray
        Total transmittance in (0, 1]. ``eta = 0`` is rejected because
        the line-noise term ``1/eta`` is singular there.
    xi : float
        Input-referred excess noise.
    eps : float, optional
        Floor used in ``np.clip(eta, eps, 1.0)`` to keep the formulas
        finite at extremely small ``eta``. Default 1e-12.

    Returns
    -------
    float or numpy.ndarray
        ``chi(B:E)`` in bits / symbol, non-negative.
    """
    nu1, nu2, nu3, _, _, _ = _cvqkd_symplectic_eigenvalues_homodyne(
        V_A, eta, xi, eps=eps,
    )

    chi_BE = (
        gaussian_entropy(nu1)
        + gaussian_entropy(nu2)
        - gaussian_entropy(nu3)
    )
    if np.any(np.asarray(chi_BE) < -1e-9):
        raise ValueError(
            "Holevo bound became materially negative -- check covariance formulas"
        )
    return np.maximum(0.0, chi_BE)


# ---------------------------------------------------------------------------
# Per-symbol secure-key rate
# ---------------------------------------------------------------------------

