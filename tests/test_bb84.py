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


def test_get_rng_int_seed_reproducible():
    a = _get_rng(42).integers(0, 100, 10)
    b = _get_rng(42).integers(0, 100, 10)
    assert np.array_equal(a, b)


def test_get_rng_generator_passthrough():
    gen = np.random.default_rng(99)
    out = _get_rng(gen)
    a = gen.integers(0, 100, 5)
    b = out.integers(0, 100, 5)
    # When passing a Generator, default_rng returns it unchanged, so the
    # two reads should advance the same internal state.
    assert isinstance(out, np.random.Generator)


# ---------------------------------------------------------------------------
# 1. alice_prepare
# ---------------------------------------------------------------------------

def test_alice_prepare_shapes():
    bits, bases = alice_prepare(10000, rng=42)
    assert bits.shape == (10000,)
    assert bases.shape == (10000,)


def test_alice_prepare_binary():
    bits, bases = alice_prepare(10000, rng=42)
    assert set(np.unique(bits)).issubset({0, 1})
    assert set(np.unique(bases)).issubset({0, 1})


def test_alice_prepare_uniform():
    bits, bases = alice_prepare(100000, rng=42)
    assert abs(np.mean(bits) - 0.5) < 0.01
    assert abs(np.mean(bases) - 0.5) < 0.01


def test_alice_prepare_reproducible():
    b1, ba1 = alice_prepare(100, rng=42)
    b2, ba2 = alice_prepare(100, rng=42)
    assert np.array_equal(b1, b2)
    assert np.array_equal(ba1, ba2)


# ---------------------------------------------------------------------------
# 2. bob_measure
# ---------------------------------------------------------------------------

def test_bob_measure_match_is_deterministic():
    alice_bits = np.array([0, 1, 0, 1, 0])
    alice_bases = np.array([0, 0, 1, 1, 0])
    bob_bases = alice_bases.copy()
    bob_bits = bob_measure(alice_bits, alice_bases, bob_bases, rng=2026)
    assert np.array_equal(bob_bits, alice_bits)


def test_bob_measure_mismatch_is_uniform():
    n = 100000
    alice_bits = np.zeros(n, dtype=int)
    alice_bases = np.ones(n, dtype=int)   # Alice always X
    bob_bases = np.zeros(n, dtype=int)    # Bob always Z -> 100% mismatch
    bob_bits = bob_measure(alice_bits, alice_bases, bob_bases, rng=99)
    assert abs(np.mean(bob_bits) - 0.5) < 0.01


def test_bob_measure_does_not_mutate_inputs():
    alice_bits = np.array([0, 0, 0, 0, 0])
    snapshot = alice_bits.copy()
    bob_measure(
        alice_bits,
        np.zeros(5, dtype=int),
        np.ones(5, dtype=int),
        rng=42,
    )
    assert np.array_equal(alice_bits, snapshot)


# ---------------------------------------------------------------------------
# 3. sift
# ---------------------------------------------------------------------------

def test_sift_known_indices():
    a_bits = np.array([0, 1, 0, 1, 0, 1])
    b_bits = np.array([0, 1, 1, 0, 0, 1])
    a_bases = np.array([0, 0, 1, 1, 0, 1])
    b_bases = np.array([0, 1, 1, 0, 0, 1])
    # Matching positions: 0, 2, 4, 5
    a_s, b_s = sift(a_bits, b_bits, a_bases, b_bases)
    assert len(a_s) == 4
    assert np.array_equal(a_s, np.array([0, 0, 0, 1]))
    assert np.array_equal(b_s, np.array([0, 1, 0, 1]))


def test_sift_rate_is_about_half():
    rng = np.random.default_rng(42)
    n = 100000
    a_bits, a_bases = alice_prepare(n, rng=rng)
    b_bases = rng.integers(0, 2, n)
    b_bits = bob_measure(a_bits, a_bases, b_bases, rng=rng)
    a_s, _ = sift(a_bits, b_bits, a_bases, b_bases)
    assert abs(len(a_s) / n - 0.5) < 0.01


def test_sift_ideal_channel_is_lossless():
    rng = np.random.default_rng(2026)
    n = 50000
    a_bits, a_bases = alice_prepare(n, rng=rng)
    b_bases = rng.integers(0, 2, n)
    b_bits = bob_measure(a_bits, a_bases, b_bases, rng=rng)
    a_s, b_s = sift(a_bits, b_bits, a_bases, b_bases)
    assert np.array_equal(a_s, b_s)


# ---------------------------------------------------------------------------
# 4. estimate_qber
# ---------------------------------------------------------------------------

def test_estimate_qber_zero_on_ideal_channel():
    rng = np.random.default_rng(2026)
    n = 10000
    a_bits, a_bases = alice_prepare(n, rng=rng)
    b_bases = rng.integers(0, 2, n)
    b_bits = bob_measure(a_bits, a_bases, b_bases, rng=rng)
    a_s, b_s = sift(a_bits, b_bits, a_bases, b_bases)
    qber, *_ = estimate_qber(a_s, b_s, rng=rng)
    assert qber == 0.0


def test_estimate_qber_removes_sample():
    rng = np.random.default_rng(7)
    n = 10000
    a_bits, a_bases = alice_prepare(n, rng=rng)
    b_bases = rng.integers(0, 2, n)
    b_bits = bob_measure(a_bits, a_bases, b_bases, rng=rng)
    a_s, b_s = sift(a_bits, b_bits, a_bases, b_bases)
    _, a_rem, b_rem, idx = estimate_qber(a_s, b_s, sample_fraction=0.1, rng=rng)
    assert len(a_rem) + len(idx) == len(a_s)
    assert len(b_rem) == len(a_rem)
    assert len(a_rem) < len(a_s)


def test_estimate_qber_empty_key_raises():
    with pytest.raises(ValueError):
        estimate_qber(np.array([], dtype=int), np.array([], dtype=int))


def test_estimate_qber_invalid_fraction_raises():
    with pytest.raises(ValueError):
        estimate_qber(np.array([0, 1]), np.array([0, 1]), sample_fraction=0.0)
    with pytest.raises(ValueError):
        estimate_qber(np.array([0, 1]), np.array([0, 1]), sample_fraction=1.5)


