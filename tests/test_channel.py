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


