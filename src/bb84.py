"""
BB84 Protocol Module
=====================

Functions for the BB84 QKD protocol: preparation, measurement, sifting,
QBER estimation, error correction, and privacy amplification.

All stochastic functions accept rng=None (random), int (seed), or
np.random.Generator for reproducible results.

Convention
----------
* basis 0 -> Z (rectilinear): bit 0 -> |0>, bit 1 -> |1>
* basis 1 -> X (diagonal):    bit 0 -> |+>, bit 1 -> |->

The simulation tracks classical (bit, basis) variables only -- the
underlying quantum state is implicit in the encoding table. The Born rule
gives exactly P = 1/2 for mismatched-basis measurement, so the classical
"copy on match, random on mismatch" rule IS the physics, not an
approximation.

"""

import numpy as np

from src.info_theory import binary_entropy


def _get_rng(rng=None):
    """Normalize a seed or Generator into a NumPy Generator.

    Parameters
    ----------
    rng : None, int, or numpy.random.Generator
        - None     : create a new random Generator (non-reproducible)
        - int      : create default_rng(seed) (reproducible)
        - Generator: use as-is

    Returns
    -------
    numpy.random.Generator
    """
    return np.random.default_rng(rng)


def alice_prepare(n_bits, rng=None):
    """Alice prepares n_bits random bits in random bases.

    Physics: Alice randomly chooses a bit (0 or 1) and a basis (0=Z, 1=X)
    for each round. The corresponding state from the BB84 encoding table
    is sent to Bob; we track only (bit, basis) here.

    Parameters
    ----------
    n_bits : int
        Number of bits / qubits to prepare.
    rng : None, int, or numpy.random.Generator
        Random number generator or seed.

    Returns
    -------
    bits : numpy.ndarray of int, shape (n_bits,)
        Alice's random bit values (0 or 1).
    bases : numpy.ndarray of int, shape (n_bits,)
        Alice's random basis choices (0 = Z, 1 = X).
    """
    rng = _get_rng(rng)
    bits = rng.integers(0, 2, n_bits)
    bases = rng.integers(0, 2, n_bits)
    return bits, bases


def bob_measure(alice_bits, alice_bases, bob_bases, rng=None):
    """Bob measures the incoming qubits in his chosen bases.

    Physics: when Bob's basis matches Alice's, projective measurement is
    deterministic (Bob reads Alice's bit). When bases mismatch, the Born
    rule gives a uniform 50/50 outcome (e.g. |<+|0>|^2 = 1/2). This is
    the exact physics, not a simulation approximation.

    Parameters
    ----------
    alice_bits : numpy.ndarray of int
        Alice's prepared bit values.
    alice_bases : numpy.ndarray of int
        Alice's basis choices (0 = Z, 1 = X).
    bob_bases : numpy.ndarray of int
        Bob's randomly chosen measurement bases.
    rng : None, int, or numpy.random.Generator
        Random number generator or seed.

    Returns
    -------
    results : numpy.ndarray of int
        Bob's measurement outcomes (one per round).
    """
    rng = _get_rng(rng)
    results = np.copy(alice_bits)
    mismatch = alice_bases != bob_bases
    results[mismatch] = rng.integers(0, 2, mismatch.sum())
    return results


def sift(alice_bits, bob_bits, alice_bases, bob_bases):
    """Sifting: keep only rounds where Alice and Bob used the same basis.

    Physics: Alice and Bob publicly announce their basis choices (NEVER
    the bit values). They keep only rounds where bases matched -- on those
    rounds Bob's measurement was deterministic. Mismatched rounds carry
    no correlated information and are discarded.

    Parameters
    ----------
    alice_bits, bob_bits : numpy.ndarray of int
        Alice's prepared bits and Bob's measured bits.
    alice_bases, bob_bases : numpy.ndarray of int
        Alice's and Bob's basis choices.

    Returns
    -------
    alice_sifted, bob_sifted : numpy.ndarray of int
        Bits where bases matched. Length is approximately N/2.
    """
    match = alice_bases == bob_bases
    return alice_bits[match], bob_bits[match]


def estimate_qber(alice_sifted, bob_sifted, sample_fraction=0.1, rng=None):
    """Estimate QBER from a randomly chosen sample of sifted bits.

    Physics: Alice and Bob disclose a random subset of their sifted key
    over the public channel and compare the BIT VALUES to estimate the
    error rate. The disclosed bits are PUBLIC and must be REMOVED from
    the remaining key -- they cannot contribute to the final secret key.

    Parameters
    ----------
    alice_sifted, bob_sifted : numpy.ndarray of int
        Sifted bits from Alice and Bob.
    sample_fraction : float, optional
        Fraction of sifted bits to disclose (default 0.1 = 10%). Must
        be in (0, 1].
    rng : None, int, or numpy.random.Generator
        Random number generator or seed.

    Returns
    -------
    qber : float
        Fraction of disagreements in the disclosed sample.
    alice_remaining, bob_remaining : numpy.ndarray of int
        Sifted bits AFTER removing the disclosed sample.
    sample_indices : numpy.ndarray of int
        Indices (into the sifted arrays) of the disclosed bits.

    Raises
    ------
    ValueError
        If the sifted key is empty, or sample_fraction is outside (0, 1].
    """
    rng = _get_rng(rng)
    n = len(alice_sifted)
    if n == 0:
        raise ValueError("cannot estimate QBER from an empty sifted key")
    if not 0 < sample_fraction <= 1:
        raise ValueError(
            f"sample_fraction must be in (0, 1], got {sample_fraction}"
        )

    sample_size = max(1, int(n * sample_fraction))
    sample_size = min(sample_size, n)
    sample_indices = rng.choice(n, sample_size, replace=False)
    sample_mask = np.zeros(n, dtype=bool)
    sample_mask[sample_indices] = True

    qber = float(np.mean(alice_sifted[sample_mask] != bob_sifted[sample_mask]))

    return (
        qber,
        alice_sifted[~sample_mask],
        bob_sifted[~sample_mask],
        sample_indices,
    )


def error_correction(alice_key, bob_key, qber, f_ec=1.16):
    """Perfect-reconciliation stub returning the leaked information cost.

    Physics: real protocols (Cascade, LDPC) exchange parity information
    over the public channel to fix bit errors between Alice and Bob.
    The minimum (Shannon-limit) leakage is n * h(QBER); practical
    protocols leak f_ec * n * h(QBER) with f_ec >= 1. We do NOT implement
    Cascade/LDPC -- we assume reconciliation succeeds and return the
    leakage budget needed by privacy amplification.

    Parameters
    ----------
    alice_key, bob_key : numpy.ndarray of int
        Remaining keys after QBER sample removal. Must have equal length.
    qber : float
        Estimated QBER.
    f_ec : float, optional
        Error-correction inefficiency factor (>= 1). Default 1.16 -- a
        realistic value for modern Cascade / LDPC implementations.

    Returns
    -------
    corrected_key : numpy.ndarray of int
        Alice's key, taken as the reconciled reference.
    leaked_bits : float
        Information revealed during correction, in bits.

    Raises
    ------
    ValueError
        If alice_key and bob_key have different lengths.
    """
    if len(alice_key) != len(bob_key):
        raise ValueError("alice_key and bob_key must have the same length")
    corrected_key = np.copy(alice_key)
    leaked_bits = f_ec * len(alice_key) * binary_entropy(qber)
    return corrected_key, leaked_bits


def eve_intercept_resend(alice_bits, alice_bases, interception_rate=1.0, rng=None):
    """Eve performs an intercept-resend attack.

    Physics: Eve intercepts a fraction `interception_rate` of the qubits,
    measures each in a randomly chosen basis (Z or X), and re-prepares a
    fresh qubit in her measurement outcome. The Born rule then operates
    twice -- Eve's wrong-basis measurements give random results, and
    those random states have only 50% overlap with Bob's correct-basis
    eigenstates. The two factors of 1/2 yield QBER = 0.25 *
    interception_rate on sifted bits.

    Parameters
    ----------
    alice_bits : numpy.ndarray of int
        Alice's prepared bit values.
    alice_bases : numpy.ndarray of int
        Alice's basis choices (0 = Z, 1 = X).
    interception_rate : float, optional
        Fraction of qubits Eve intercepts; must lie in [0, 1]. Default 1.0.
    rng : None, int, or numpy.random.Generator
        Random number generator or seed.

    Returns
    -------
    eve_bits : numpy.ndarray of int
        Eve's measurement outcome for every round. Only meaningful where
        `intercepted` is True; on non-intercepted rounds Eve never measured.
    forwarded_bits : numpy.ndarray of int
        Bits Eve sends on to Bob (Eve's outcome on intercepted rounds,
        Alice's bit otherwise).
    forwarded_bases : numpy.ndarray of int
        Bases used to re-prepare each forwarded qubit (Eve's basis on
        intercepted rounds, Alice's basis otherwise). This is the
        critical handoff -- if this stayed Alice's basis, no QBER
        would appear.
    intercepted : numpy.ndarray of bool
        True where Eve actually intercepted.

    Raises
    ------
    ValueError
        If `interception_rate` is not in [0, 1].
    """
    rng = _get_rng(rng)
    n = len(alice_bits)

    if not 0.0 <= interception_rate <= 1.0:
        raise ValueError(
            f"interception_rate must be in [0, 1], got {interception_rate}"
        )

    intercepted = rng.random(n) < interception_rate
    eve_bases = rng.integers(0, 2, n)

    eve_bits = np.copy(alice_bits)
    eve_wrong_basis = intercepted & (eve_bases != alice_bases)
    eve_bits[eve_wrong_basis] = rng.integers(0, 2, eve_wrong_basis.sum())

    forwarded_bits = np.copy(alice_bits)
    forwarded_bases = np.copy(alice_bases)
    forwarded_bits[intercepted] = eve_bits[intercepted]
    forwarded_bases[intercepted] = eve_bases[intercepted]

    return eve_bits, forwarded_bits, forwarded_bases, intercepted


def final_key_length(n_remaining, qber, f_ec=1.16):
    """Final secure key length after privacy amplification.

    Physics: the per-sifted-bit secret-key rate is

        K = 1 - h(QBER) - f_ec * h(QBER)

    where the first h(QBER) bounds Eve's Holevo information for the
    depolarizing channel, and f_ec * h(QBER) is the error-correction
    leakage. Final length L = N_remaining * max(0, K).

    The threshold (K = 0) sits at h(E*) = 1 / (1 + f_ec), giving
    E* ~ 11.0% for f_ec = 1 and E* ~ 9.8% for f_ec = 1.16.

    Parameters
    ----------
    n_remaining : int
        Sifted bits AFTER QBER sample removal (NOT the full sifted key).
    qber : float
        Estimated QBER.
    f_ec : float, optional
        Error-correction inefficiency factor. Default 1.16.

    Returns
    -------
    int
        Final secure key length in bits. Zero when QBER is above threshold.
    """
    h_q = binary_entropy(qber)
    key_rate = 1.0 - h_q - f_ec * h_q
    return max(0, int(n_remaining * key_rate))
