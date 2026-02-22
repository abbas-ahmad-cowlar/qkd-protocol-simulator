"""
Fiber Channel Module
=====================

Realistic fiber channel model: attenuation, dark counts, detector
efficiency, BB84 per-pulse key rate as a function of distance, and a
simplified asymptotic decoy-state extension (Lo, Ma & Chen, 2005).

Conventions
-----------
* Fiber attenuation in dB/km. ``alpha_dB = 0.2`` corresponds to the
  1550 nm telecom-C minimum (e.g. SMF-28).
* Transmittance is ``eta(L) = 10**(-alpha_dB * L / 10)`` -- BASE 10, not e.
* Two-detector model: the per-pulse gain uses
  ``2 * p_dark`` (both detectors fire dark counts), but the QBER
  numerator uses only ``p_dark`` because only one of the two detectors
  fires erroneously per dark event.
* ``bb84_signal_prob`` is the single source of truth for the signal
  probability. ``total_detection_prob`` and
  ``qber_channel`` consume it directly so the formulas cannot drift.
* All functions are vectorized -- they accept a NumPy array of
  distances such as ``np.linspace(0, 300, 301)``.
"""

import numpy as np

from src.info_theory import binary_entropy


def _maybe_scalar(x, original):
    """Return a Python float when the original input was scalar."""
    return float(x) if np.ndim(original) == 0 else x


def fiber_transmittance(L, alpha_dB=0.2):
    """Fiber transmittance as a function of distance.

    Physics: ``eta(L) = 10**(-alpha_dB * L / 10)``. At 1550 nm the
    telecom C-band minimum sits at ``alpha_dB ~ 0.2``.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km. Must be non-negative.
    alpha_dB : float, optional
        Attenuation coefficient in dB/km (>= 0). Default 0.2.

    Returns
    -------
    float or numpy.ndarray
        Transmittance in (0, 1].
    """
    L_arr = np.asarray(L, dtype=float)
    if np.any(L_arr < 0.0):
        raise ValueError("Fiber length L must be nonnegative")
    if alpha_dB < 0.0:
        raise ValueError("alpha_dB must be nonnegative")
    eta = 10.0 ** (-alpha_dB * L_arr / 10.0)
    return _maybe_scalar(eta, L)


