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


def test_return_scalar_if_scalar_array_input():
    out = _return_scalar_if_scalar(np.array([0.5]), np.array([1.0]))
    assert isinstance(out, np.ndarray)


# ---------------------------------------------------------------------------
# 1. binary_entropy
# ---------------------------------------------------------------------------

def test_binary_entropy_known_values():
    assert np.isclose(binary_entropy(0.0), 0.0)
    assert np.isclose(binary_entropy(1.0), 0.0)
    assert np.isclose(binary_entropy(0.5), 1.0)


def test_binary_entropy_symmetry():
    for p in [0.1, 0.2, 0.3, 0.4]:
        assert np.isclose(binary_entropy(p), binary_entropy(1 - p))


def test_binary_entropy_bb84_threshold():
    h_11 = binary_entropy(0.110027)
    assert abs(h_11 - 0.5) < 1e-4


def test_binary_entropy_vectorized():
    p = np.linspace(0, 1, 101)
    h = binary_entropy(p)
    assert h.shape == (101,)
    assert np.isclose(h[0], 0.0)
    assert np.isclose(h[50], 1.0)
    assert np.isclose(h[-1], 0.0)
    assert np.all(h >= -1e-15)


def test_binary_entropy_scalar_returns_float():
    assert isinstance(binary_entropy(0.5), float)
    assert isinstance(binary_entropy(np.array([0.5])), np.ndarray)


def test_binary_entropy_invalid_input():
    with pytest.raises(ValueError):
        binary_entropy(-0.1)
    with pytest.raises(ValueError):
        binary_entropy(1.1)
    with pytest.raises(ValueError):
        binary_entropy(np.array([0.1, 1.5]))


# ---------------------------------------------------------------------------
# 2. shannon_entropy
# ---------------------------------------------------------------------------

def test_shannon_entropy_deterministic():
    assert np.isclose(shannon_entropy([1, 0, 0, 0]), 0.0)
    assert np.isclose(shannon_entropy([0, 0, 1, 0]), 0.0)


def test_shannon_entropy_uniform():
    for n in [2, 4, 6, 8, 16]:
        probs = np.ones(n) / n
        assert np.isclose(shannon_entropy(probs), np.log2(n), atol=1e-10)


