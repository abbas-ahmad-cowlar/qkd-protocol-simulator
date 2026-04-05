"""
tests/test_physics.py -- Phase 6 cross-module physics regression tests.

These tests do NOT exercise individual modules in isolation. They lock
in the *numerical* output of the full QKD pipeline at specific
distances under the project's default parameter sets. Any failure here
means a formula or convention has drifted, even if the per-module
tests still pass.

Locked headline values (notebook 06 / seed 2026 where stochastic):

* BB84 default-parameter cutoff       : 169.38 km
* CV-QKD default-parameter cutoff     :  74.19 km
* BB84 K(50 km, defaults)             : 9.875977e-04 bits / pulse
* CV-QKD K(50 km, defaults)           : 9.236829e-03 bits / symbol
* Full intercept-resend QBER (N=1e5)  : ~ 0.25 (within 0.01)

Run:
    python -m pytest tests/test_physics.py -v
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
    alice_prepare,
    bob_measure,
    eve_intercept_resend,
    sift,
)
from src.channel import (
    bb84_key_rate,
    fiber_transmittance,
    qber_channel,
)
from src.cvqkd import (
    _cvqkd_symplectic_eigenvalues_homodyne,
    cvqkd_holevo_bound_homodyne,
    cvqkd_key_rate,
    cvqkd_mutual_info_homodyne,
)
from src.info_theory import binary_entropy, gaussian_entropy


# ===========================================================================
# Information theory primitives
# ===========================================================================
