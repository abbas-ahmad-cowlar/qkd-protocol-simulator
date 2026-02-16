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


