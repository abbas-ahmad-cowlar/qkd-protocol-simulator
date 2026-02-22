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


