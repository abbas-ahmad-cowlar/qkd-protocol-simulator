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


def test_mutual_info_homodyne_excess_noise_reduces():
    I_clean = cvqkd_mutual_info_homodyne(20, 0.5, 0)
    I_noisy = cvqkd_mutual_info_homodyne(20, 0.5, 0.1)
    assert I_noisy < I_clean


def test_mutual_info_homodyne_zero_eta():
    assert cvqkd_mutual_info_homodyne(20, 0.0, 0) == 0.0


def test_mutual_info_homodyne_vectorized():
    eta = np.linspace(0.0, 1.0, 11)
    I = cvqkd_mutual_info_homodyne(20, eta, 0.01)
    assert I.shape == eta.shape
    assert np.all(np.isfinite(I))
    assert I[0] == 0.0
    assert np.all(np.diff(I) >= -1e-12)  # monotonic in eta


def test_mutual_info_homodyne_invalid_inputs():
    with pytest.raises(ValueError):
        cvqkd_mutual_info_homodyne(-1.0, 0.5, 0)
    with pytest.raises(ValueError):
        cvqkd_mutual_info_homodyne(20, 1.5, 0)
    with pytest.raises(ValueError):
        cvqkd_mutual_info_homodyne(20, 0.5, -0.1)


def test_mutual_info_heterodyne_noiseless():
    I = cvqkd_mutual_info_heterodyne(20, 1.0, 0)
    assert np.isclose(I, np.log2(11), rtol=1e-9)


# ---------------------------------------------------------------------------
# Symplectic eigenvalues
# ---------------------------------------------------------------------------

def test_eigenvalues_pure_state_two_mode():
    """Pure-state check: eta = 1, xi = 0 -> nu1 = nu2 = nu3 = 1."""
    V_A = 20.0
    V = V_A + 1.0
    nu1, nu2, nu3, a, b, c = _cvqkd_symplectic_eigenvalues_homodyne(V_A, 1.0, 0.0)
    assert np.isclose(nu1, 1.0, atol=1e-9)
    assert np.isclose(nu2, 1.0, atol=1e-9)
    assert np.isclose(nu3, 1.0, atol=1e-9)
    assert np.isclose(a, V, atol=1e-12)
    assert np.isclose(b, V, atol=1e-12)
    assert np.isclose(c, np.sqrt(V**2 - 1.0), atol=1e-12)


def test_eigenvalues_physicality_lossy_noisy():
    nu1, nu2, nu3, *_ = _cvqkd_symplectic_eigenvalues_homodyne(20.0, 0.5, 0.01)
    assert nu1 >= 1.0 - 1e-12
    assert nu2 >= 1.0 - 1e-12
    assert nu3 >= 1.0 - 1e-12
    assert nu1 * nu2 >= 1.0 - 1e-12  # uncertainty principle


def test_eigenvalues_rejects_zero_eta():
    with pytest.raises(ValueError):
        _cvqkd_symplectic_eigenvalues_homodyne(20.0, 0.0, 0.0)


def test_eigenvalues_vectorized():
    eta = np.linspace(0.05, 1.0, 20)
    nu1, nu2, nu3, *_ = _cvqkd_symplectic_eigenvalues_homodyne(20.0, eta, 0.01)
    assert nu1.shape == eta.shape
    assert np.all(nu1 >= 1.0 - 1e-12)
    assert np.all(nu2 >= 1.0 - 1e-12)
    assert np.all(nu3 >= 1.0 - 1e-12)


# ---------------------------------------------------------------------------
# Holevo bound
# ---------------------------------------------------------------------------

def test_holevo_pure_state_zero():
    chi = cvqkd_holevo_bound_homodyne(20.0, 1.0, 0.0)
    assert np.isclose(chi, 0.0, atol=1e-9)


def test_holevo_loss_positive_finite():
    chi = cvqkd_holevo_bound_homodyne(20.0, 0.5, 0.0)
    assert chi > 0.0
    assert np.isfinite(chi)


def test_holevo_excess_noise_increases():
    chi_clean = cvqkd_holevo_bound_homodyne(20.0, 0.5, 0.0)
    chi_noisy = cvqkd_holevo_bound_homodyne(20.0, 0.5, 0.01)
    assert chi_noisy > chi_clean


def test_holevo_rejects_zero_eta():
    with pytest.raises(ValueError):
        cvqkd_holevo_bound_homodyne(20.0, 0.0, 0.0)


def test_holevo_vectorized():
    eta = np.linspace(0.05, 1.0, 25)
    chi = cvqkd_holevo_bound_homodyne(20.0, eta, 0.01)
    assert chi.shape == eta.shape
    assert np.all(np.isfinite(chi))
    assert np.all(chi >= 0.0)


# ---------------------------------------------------------------------------
# Key rate
# ---------------------------------------------------------------------------

def test_key_rate_short_positive():
    assert cvqkd_key_rate(0) > 0.0


