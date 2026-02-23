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


def bb84_signal_prob(L, mu=0.1, eta_det=0.2, alpha_dB=0.2):
    """Signal detection probability: photon arrives AND is detected.

    Physics: ``signal = eta_ch(L) * eta_det * mu``. This is the SINGLE
    SOURCE OF TRUTH for the signal probability used downstream.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km.
    mu : float, optional
        Mean photon number per pulse. Default 0.1.
    eta_det : float, optional
        Detector quantum efficiency. Default 0.2.
    alpha_dB : float, optional
        Fiber attenuation in dB/km. Default 0.2.

    Returns
    -------
    float or numpy.ndarray
        Signal detection probability (dimensionless).
    """
    eta_ch = fiber_transmittance(L, alpha_dB)
    return eta_ch * eta_det * mu


def total_detection_prob(L, mu=0.1, eta_det=0.2, p_dark=1e-6, alpha_dB=0.2):
    """Per-pulse gain: probability Bob registers any click at all.

    Physics: ``Q = signal + 2 * p_dark``. Two detectors each fire dark
    counts with probability ``p_dark``.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km.
    mu, eta_det, p_dark, alpha_dB : floats
        Channel and source parameters.

    Returns
    -------
    float or numpy.ndarray
        Detection gain Q.
    """
    signal = bb84_signal_prob(L, mu, eta_det, alpha_dB)
    return signal + 2.0 * p_dark


def qber_channel(L, mu=0.1, eta_det=0.2, p_dark=1e-6, alpha_dB=0.2, e_det=0.0):
    """Channel QBER from dark counts and optical misalignment.

    Physics: ``QBER = (e_det * signal + p_dark) / gain``. The QBER
    numerator uses ``p_dark`` (not ``2 * p_dark``) because only one of
    the two detectors fires per dark event and it is random which.

    The ``e_det * signal`` term captures intrinsic optical and detector
    misalignment errors -- nonzero for real systems, default 0 here so
    the unattacked channel produces the textbook ``QBER -> 0`` at short
    distance and ``QBER -> 0.5`` at long distance.

    The ``where=`` clause guards the ``mu = eta_det = p_dark = 0`` edge
    case: when the gain is exactly zero, no bits are detected at all
    and we return the random-error limit 0.5 so downstream key-rate
    formulas clamp to zero.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km.
    mu, eta_det, p_dark, alpha_dB : floats
        Channel and source parameters.
    e_det : float, optional
        Intrinsic optical / detector misalignment error rate. Default 0.0.

    Returns
    -------
    float or numpy.ndarray
        QBER in [0, 0.5].
    """
    signal = bb84_signal_prob(L, mu, eta_det, alpha_dB)
    gain = signal + 2.0 * p_dark
    numerator = e_det * signal + p_dark

    gain_arr = np.asarray(gain, dtype=float)
    num_arr = np.asarray(numerator, dtype=float) * np.ones_like(gain_arr)
    qber = np.divide(
        num_arr,
        gain_arr,
        out=np.full_like(gain_arr, 0.5, dtype=float),
        where=gain_arr > 0.0,
    )
    return _maybe_scalar(qber, L)


def bb84_key_rate(L, mu=0.1, eta_det=0.2, p_dark=1e-6, f_ec=1.16,
                  alpha_dB=0.2, e_det=0.0):
    """Per-pulse secure-key rate for BB84 with the realistic channel.

    Physics: ``K = q * Q * max(0, 1 - h(QBER) - f_ec * h(QBER))`` with
    sifting factor ``q = 1/2``. Use ``np.maximum`` so the
    clamp survives vectorised distance sweeps.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km.
    mu, eta_det, p_dark, alpha_dB, e_det : floats
        Channel and source parameters.
    f_ec : float, optional
        Error-correction inefficiency factor (>= 1). Default 1.16.

    Returns
    -------
    float or numpy.ndarray
        Per-pulse key rate (bits / pulse). Always non-negative.
    """
    gain = total_detection_prob(L, mu, eta_det, p_dark, alpha_dB)
    qber = qber_channel(L, mu, eta_det, p_dark, alpha_dB, e_det)
    bracket = 1.0 - binary_entropy(qber) - f_ec * binary_entropy(qber)
    return np.maximum(0.0, 0.5 * gain * bracket)


def decoy_bb84_key_rate(L, mu=0.5, eta_det=0.2, p_dark=1e-6,
                        e_det=0.015, f_ec=1.16, alpha_dB=0.2):
    """Simplified asymptotic decoy-state BB84 per-pulse key rate.

    Physics: weak-coherent sources are vulnerable to PNS attacks
    because multi-photon pulses leak information silently. Decoy
    states (Lo, Ma & Chen, 2005) detect PNS by varying the pulse
    intensity; in the asymptotic limit the recoverable secret-key rate
    is

        K = q * max(0, Q1 * (1 - h(e1)) - Q_mu * f_ec * h(E_mu))

    where ``Q1, e1`` are the single-photon gain and error rate
    estimated from the decoy statistics, and ``Q_mu, E_mu`` are the
    overall gain and QBER at the signal intensity.

    The yields used here:

        Y0 = 2 * p_dark                      (vacuum, two detectors)
        Y1 = 1 - (1 - Y0) * (1 - eta_total)  (single-photon yield)
        Q1 = mu * exp(-mu) * Y1              (Poisson n=1 weight)
        e1 = (e_det * eta_total + 0.5 * Y0) / Y1
        Q_mu = 1 - exp(-eta_total * mu) + Y0
        E_mu = (e_det * (1 - exp(-eta_total * mu)) + 0.5 * Y0) / Q_mu

    Modeling caveat: this is a simplified asymptotic estimate. It assumes
    infinite decoy statistics and asymptotic key length; finite-key
    corrections are out of scope.

    Parameters
    ----------
    L : float or numpy.ndarray
        Fiber length in km.
    mu : float, optional
        Signal-pulse mean photon number. Default 0.5.
    eta_det : float, optional
        Detector quantum efficiency. Default 0.2.
    p_dark : float, optional
        Per-detector dark-count probability. Default 1e-6.
    e_det : float, optional
        Intrinsic optical / detector misalignment error rate. Default 0.015.
    f_ec : float, optional
        Error-correction inefficiency factor. Default 1.16.
    alpha_dB : float, optional
        Fiber attenuation in dB/km. Default 0.2.

    Returns
    -------
    float or numpy.ndarray
        Per-pulse decoy-state key rate (bits / pulse). Always >= 0.
    """
    eta_total = fiber_transmittance(L, alpha_dB) * eta_det

    Y0 = 2.0 * p_dark
    Y1 = 1.0 - (1.0 - Y0) * (1.0 - eta_total)
