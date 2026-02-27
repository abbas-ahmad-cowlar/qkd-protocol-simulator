"""
tests/test_channel.py -- Phase 4 fiber-channel unit + integration tests.

Run with:
    python -m pytest tests/test_channel.py -v
or:
    python tests/test_channel.py
"""

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.channel import (
    fiber_transmittance,
    bb84_signal_prob,
    total_detection_prob,
    qber_channel,
    bb84_key_rate,
    decoy_bb84_key_rate,
)


# ---------------------------------------------------------------------------
# fiber_transmittance
# ---------------------------------------------------------------------------

def test_transmittance_zero():
    assert fiber_transmittance(0) == 1.0


def test_transmittance_50km():
    assert np.isclose(fiber_transmittance(50), 0.1, rtol=1e-9)


def test_transmittance_100km():
    assert np.isclose(fiber_transmittance(100), 0.01, rtol=1e-9)


def test_transmittance_rejects_negative_distance():
    with pytest.raises(ValueError):
        fiber_transmittance(-1)


def test_transmittance_rejects_negative_alpha():
    with pytest.raises(ValueError):
        fiber_transmittance(10, alpha_dB=-0.2)


def test_transmittance_vectorized():
    L = np.array([0, 50, 100, 150])
    eta = fiber_transmittance(L)
    np.testing.assert_allclose(eta, [1.0, 0.1, 0.01, 1e-3], rtol=1e-9)


def test_transmittance_scalar_returns_float():
    assert isinstance(fiber_transmittance(50.0), float)


# ---------------------------------------------------------------------------
# bb84_signal_prob
# ---------------------------------------------------------------------------

def test_signal_prob_zero():
    assert np.isclose(bb84_signal_prob(0), 0.02)


def test_signal_prob_50km():
    assert np.isclose(bb84_signal_prob(50), 0.002, rtol=1e-9)


def test_signal_prob_vectorized():
    L = np.linspace(0, 100, 11)
    s = bb84_signal_prob(L)
    assert s.shape == L.shape
    assert np.all(np.isfinite(s))
    assert s[0] > s[-1]


# ---------------------------------------------------------------------------
# total_detection_prob
# ---------------------------------------------------------------------------

def test_total_detection_short():
    gain = total_detection_prob(0)
    assert np.isclose(gain, 0.020002, rtol=1e-4)


def test_total_detection_long():
    gain = total_detection_prob(300)
    assert np.isclose(gain, 2e-6, rtol=0.01)


# ---------------------------------------------------------------------------
# qber_channel
# ---------------------------------------------------------------------------

def test_qber_short_negligible():
    q = qber_channel(0)
    assert q < 1e-3


def test_qber_long_approaches_half():
    q = qber_channel(300)
    assert abs(q - 0.5) < 0.01


def test_qber_zero_gain_returns_half():
    q = qber_channel(0, mu=0.0, eta_det=0.0, p_dark=0.0)
    assert q == 0.5


def test_qber_misalignment_dominates_at_short_L():
    q = qber_channel(0, e_det=0.01)
    assert abs(q - 0.01) < 1e-3


def test_qber_vectorized_no_nan():
    L = np.linspace(0, 300, 301)
    q = qber_channel(L)
    assert q.shape == L.shape
    assert np.all(np.isfinite(q))
    assert np.all((q >= 0.0) & (q <= 0.5 + 1e-12))


# ---------------------------------------------------------------------------
# bb84_key_rate
# ---------------------------------------------------------------------------

def test_key_rate_short_positive():
    assert bb84_key_rate(0) > 0.0


def test_key_rate_long_zero():
    assert bb84_key_rate(300) == 0.0


def test_key_rate_zero_gain_zero():
    assert bb84_key_rate(0, mu=0.0, eta_det=0.0, p_dark=0.0) == 0.0


