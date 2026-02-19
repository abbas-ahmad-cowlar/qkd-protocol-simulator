"""
tests/test_bb84.py -- BB84 protocol unit + integration tests.

Run with:
    python -m pytest tests/test_bb84.py -v
or:
    python tests/test_bb84.py
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
    _get_rng,
    alice_prepare,
    bob_measure,
    sift,
    estimate_qber,
    error_correction,
    final_key_length,
    eve_intercept_resend,
)
from src.info_theory import binary_entropy


# ---------------------------------------------------------------------------
# 0. _get_rng
# ---------------------------------------------------------------------------

def test_get_rng_none_returns_generator():
    rng = _get_rng(None)
    assert isinstance(rng, np.random.Generator)


