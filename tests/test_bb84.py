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


def test_estimate_qber_full_sample():
    a = np.array([0, 1, 0, 1])
    b = np.array([0, 0, 0, 1])
    qber, a_rem, b_rem, idx = estimate_qber(a, b, sample_fraction=1.0, rng=2026)
    assert qber == 0.25
    assert len(a_rem) == 0 and len(b_rem) == 0
    assert len(idx) == 4


# ---------------------------------------------------------------------------
# 5. error_correction
# ---------------------------------------------------------------------------

def test_error_correction_zero_qber_zero_leak():
    key = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    corrected, leaked = error_correction(key, key, qber=0.0)
    assert np.array_equal(corrected, key)
    assert leaked == 0.0


def test_error_correction_leakage_formula():
    n = 1000
    fake = np.zeros(n, dtype=int)
    _, leaked = error_correction(fake, fake, qber=0.11, f_ec=1.16)
    expected = 1.16 * n * binary_entropy(0.11)
    assert np.isclose(leaked, expected)


def test_error_correction_f_ec_monotonic():
    n = 1000
    fake = np.zeros(n, dtype=int)
    _, leak_ideal = error_correction(fake, fake, qber=0.05, f_ec=1.0)
    _, leak_real = error_correction(fake, fake, qber=0.05, f_ec=1.16)
    assert leak_ideal < leak_real


def test_error_correction_length_mismatch_raises():
    with pytest.raises(ValueError):
        error_correction(np.array([0, 1]), np.array([0, 1, 0]), qber=0.0)


# ---------------------------------------------------------------------------
# 6. final_key_length
# ---------------------------------------------------------------------------

def _bb84_threshold(f_ec):
    return brentq(
        lambda e: 1.0 - binary_entropy(e) - f_ec * binary_entropy(e),
        1e-12,
        0.5 - 1e-12,
    )


def test_final_key_length_qber_zero_returns_full():
    assert final_key_length(1000, qber=0.0, f_ec=1.16) == 1000


def test_final_key_length_threshold_f_ec_1():
    threshold = _bb84_threshold(1.0)
    assert np.isclose(threshold, 0.1100278644, atol=1e-6)
    assert final_key_length(100000, qber=threshold + 1e-4, f_ec=1.0) == 0
    assert final_key_length(100000, qber=threshold - 1e-4, f_ec=1.0) > 0


def test_final_key_length_threshold_f_ec_116():
    assert final_key_length(100000, qber=0.10, f_ec=1.16) == 0
    assert final_key_length(100000, qber=0.09, f_ec=1.16) > 0


def test_final_key_length_explicit_value():
    n = 1000
    qber = 0.05
    f_ec = 1.16
    h = binary_entropy(qber)
    expected = int(n * (1.0 - h - f_ec * h))
    assert final_key_length(n, qber=qber, f_ec=f_ec) == expected


def test_final_key_length_above_threshold_zero():
    assert final_key_length(1000, qber=0.5, f_ec=1.16) == 0


# ---------------------------------------------------------------------------
# 7. End-to-end pipeline (Step 2.6 integration test)
# ---------------------------------------------------------------------------

def test_full_pipeline_ideal_channel():
    rng = np.random.default_rng(2026)
    N = 100_000

    a_bits, a_bases = alice_prepare(N, rng=rng)
    b_bases = rng.integers(0, 2, N)
    b_bits = bob_measure(a_bits, a_bases, b_bases, rng=rng)
    a_s, b_s = sift(a_bits, b_bits, a_bases, b_bases)
    qber, a_rem, b_rem, _ = estimate_qber(a_s, b_s, sample_fraction=0.1, rng=rng)
    corrected, leaked = error_correction(a_rem, b_rem, qber)
    L = final_key_length(len(a_rem), qber)

    sift_rate = len(a_s) / N
    final_fraction = L / N

    assert abs(sift_rate - 0.5) < 0.01
    assert qber == 0.0
    assert leaked == 0.0
    assert L == len(a_rem)
    assert np.array_equal(corrected, b_rem)
    assert 0.35 < final_fraction < 0.55


# ---------------------------------------------------------------------------
# 8. eve_intercept_resend (Phase 3)
# ---------------------------------------------------------------------------

def _run_with_eve(N, interception_rate, seed):
    """Run the BB84 pipeline against Eve's intercept-resend; return QBER and the
    `intercepted` mask."""
    rng = np.random.default_rng(seed)
    a_bits, a_bases = alice_prepare(N, rng=rng)
    eve_bits, fwd_bits, fwd_bases, intercepted = eve_intercept_resend(
        a_bits, a_bases, interception_rate=interception_rate, rng=rng
    )
    b_bases = rng.integers(0, 2, N)
    b_bits = bob_measure(fwd_bits, fwd_bases, b_bases, rng=rng)
    a_sifted, b_sifted = sift(a_bits, b_bits, a_bases, b_bases)
    qber = float(np.mean(a_sifted != b_sifted)) if len(a_sifted) > 0 else 0.0
    return qber, intercepted, (a_bits, a_bases, eve_bits, fwd_bits, fwd_bases, b_bases, b_bits)


def test_eve_full_interception_qber_is_25pct():
    qber, intc, _ = _run_with_eve(100_000, 1.0, seed=2026)
    assert abs(qber - 0.25) < 0.01
    assert intc.all()


def test_eve_no_interception_qber_zero():
    qber, intc, _ = _run_with_eve(100_000, 0.0, seed=2026)
    assert qber == 0.0
    assert intc.sum() == 0


def test_eve_partial_10pct_qber_linear():
    qber, _, _ = _run_with_eve(100_000, 0.1, seed=2026)
    assert abs(qber - 0.025) < 0.01


