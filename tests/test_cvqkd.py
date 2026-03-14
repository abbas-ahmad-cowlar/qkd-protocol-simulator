"""
tests/test_cvqkd.py -- Phase 5 CV-QKD unit + integration tests.

Run with:
    python -m pytest tests/test_cvqkd.py -v
or:
    python tests/test_cvqkd.py
"""

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cvqkd import (
    _cvqkd_symplectic_eigenvalues_homodyne,
    cvqkd_holevo_bound_homodyne,
    cvqkd_key_rate,
    cvqkd_mutual_info_heterodyne,
    cvqkd_mutual_info_homodyne,
)


# ---------------------------------------------------------------------------
# Mutual information
# ---------------------------------------------------------------------------

def test_mutual_info_homodyne_noiseless():
    I = cvqkd_mutual_info_homodyne(20, 1.0, 0)
    assert np.isclose(I, 0.5 * np.log2(21), rtol=1e-9)


def test_mutual_info_homodyne_loss_reduces():
    I_full = cvqkd_mutual_info_homodyne(20, 1.0, 0)
    I_half = cvqkd_mutual_info_homodyne(20, 0.5, 0)
    assert I_half < I_full


