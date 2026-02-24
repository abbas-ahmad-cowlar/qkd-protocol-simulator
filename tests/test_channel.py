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


