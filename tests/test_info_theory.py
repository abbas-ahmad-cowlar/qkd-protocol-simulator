"""
Unit + Integration Tests for src/info_theory.py
================================================

Covers all five functions plus the BSC/BB84 cross-check.
Run with:  python tests/test_info_theory.py
or:        pytest tests/test_info_theory.py
"""

import numpy as np
import pytest

from src.info_theory import (
    _return_scalar_if_scalar,
    binary_entropy,
    shannon_entropy,
    mutual_information,
    gaussian_entropy,
)


# ---------------------------------------------------------------------------
# 0. Helper
# ---------------------------------------------------------------------------

def test_return_scalar_if_scalar_scalar_input():
    assert isinstance(_return_scalar_if_scalar(0.5, np.array(1.0)), float)


