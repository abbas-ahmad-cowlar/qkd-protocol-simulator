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


