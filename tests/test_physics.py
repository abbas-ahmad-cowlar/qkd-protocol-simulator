"""
tests/test_physics.py -- Phase 6 cross-module physics regression tests.

These tests do NOT exercise individual modules in isolation. They lock
in the *numerical* output of the full QKD pipeline at specific
distances under the project's default parameter sets. Any failure here
means a formula or convention has drifted, even if the per-module
tests still pass.

Locked headline values (notebook 06 / seed 2026 where stochastic):

* BB84 default-parameter cutoff       : 169.38 km
* CV-QKD default-parameter cutoff     :  74.19 km
* BB84 K(50 km, defaults)             : 9.875977e-04 bits / pulse
* CV-QKD K(50 km, defaults)           : 9.236829e-03 bits / symbol
* Full intercept-resend QBER (N=1e5)  : ~ 0.25 (within 0.01)

Run:
    python -m pytest tests/test_physics.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bb84 import (
    alice_prepare,
    bob_measure,
    eve_intercept_resend,
    sift,
)
from src.channel import (
    bb84_key_rate,
    fiber_transmittance,
    qber_channel,
)
from src.cvqkd import (
    _cvqkd_symplectic_eigenvalues_homodyne,
    cvqkd_holevo_bound_homodyne,
    cvqkd_key_rate,
    cvqkd_mutual_info_homodyne,
)
from src.info_theory import binary_entropy, gaussian_entropy


# ===========================================================================
# Information theory primitives
# ===========================================================================

def test_binary_entropy_endpoints():
    assert binary_entropy(0.0) == 0.0
    assert binary_entropy(1.0) == 0.0
    assert np.isclose(binary_entropy(0.5), 1.0)


def test_binary_entropy_symmetry():
    for p in [0.05, 0.10, 0.20, 0.30, 0.40]:
        assert np.isclose(binary_entropy(p), binary_entropy(1.0 - p))


def test_gaussian_entropy_vacuum_zero():
    assert np.isclose(gaussian_entropy(1.0), 0.0, atol=1e-12)


def test_gaussian_entropy_monotone_above_vacuum():
    nus = np.array([1.01, 2.0, 5.0, 10.0, 50.0])
    g = gaussian_entropy(nus)
    assert np.all(np.diff(g) > 0)


# ===========================================================================
# Fiber channel and BB84 per-pulse rate
# ===========================================================================

def test_fiber_transmittance_canonical_values():
    assert np.isclose(fiber_transmittance(0.0, 0.2), 1.0)
    assert np.isclose(fiber_transmittance(50.0, 0.2), 0.1)
    assert np.isclose(fiber_transmittance(100.0, 0.2), 1e-2)


def test_qber_long_distance_random_limit():
    assert qber_channel(300.0) > 0.45


def test_qber_short_distance_negligible():
    assert qber_channel(0.0, e_det=0.0) < 1e-3


def test_bb84_key_rate_short_positive():
    assert bb84_key_rate(0.0) > 0.0


def test_bb84_key_rate_sweep_finite_nonneg():
    L = np.linspace(0.0, 300.0, 301)
    r = bb84_key_rate(L)
    assert np.all(np.isfinite(r))
    assert np.all(r >= 0.0)


def test_bb84_key_rate_decreasing_with_distance():
    rates = [float(bb84_key_rate(d)) for d in [0.0, 50.0, 100.0]]
    assert rates[0] >= rates[1] >= rates[2]


# ----- Locked-in numeric regression (Phase 6 headline) ----------------------

@pytest.mark.parametrize("distance, expected", [
    (0.0, 9.984011e-03),
    (50.0, 9.875977e-04),
    (100.0, 9.117488e-05),
    (150.0, 4.661664e-06),
])
