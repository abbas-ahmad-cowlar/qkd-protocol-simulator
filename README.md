# QKD Protocol Simulator

> Comparing Discrete-Variable (BB84) and Continuous-Variable (GG02)
> Quantum Key Distribution under stated fiber-channel assumptions.

![BB84 vs CV-QKD Protocol Comparison](figures/protocol_comparison.png)

## Overview

This repository implements and compares two fundamental Quantum Key
Distribution (QKD) protocols: **BB84** (discrete-variable) and **GG02**
(continuous-variable). The code computes asymptotic secure key-rate bounds
under explicit, reproducible parameter sets.

The simulator shows how fiber attenuation, detector dark counts, excess
noise, and reconciliation efficiency constrain the maximum secure distance
for each protocol. All numbers in plots and tables are computed from the
code; no headline values are hardcoded.

The project is organized as a standalone scientific Python repository:
small numerical modules, executable notebooks, saved 300 dpi figures, and
regression tests that keep the stated assumptions visible.

## Headline Result

Under the default parameter sets used by the comparison notebook and
headline figure:

| Protocol | Source / detector | Trust model | Cutoff | K @ 50 km |
|---|---|---|---|---|
| BB84 | idealised single-photon source | -- (single-photon) | **169.4 km** | 9.876 x 10^-4 bits / pulse |
| CV-QKD GG02 | Gaussian-modulated coherent states, balanced homodyne | untrusted detector | **74.2 km** | 9.237 x 10^-3 bits / symbol |

> **Important caveat.** The two columns use different normalisations
> (per emitted pulse vs per coherent-state symbol) and different security
> models (asymptotic simplified BB84 vs asymptotic collective Gaussian
> attack). The cutoff column is not a universal performance ranking;
> changing detector efficiency, excess noise, dark counts, or reconciliation
> efficiency changes the relative ordering. See the parameter box on the
> figure for the exact assumptions.

## Key Figures

### BB84 key rate vs distance

![BB84 key rate vs distance](figures/bb84_key_rate_distance.png)

The BB84 per-pulse key rate is computed as a function of fiber length under
the standard direct-link parameter set. The cutoff lies in the documented
150-200 km window for the idealised single-photon source model. Practical
weak-coherent-pulse security requires decoy-state analysis.

### CV-QKD key rate vs distance

![CV-QKD key rate vs distance](figures/cvqkd_key_rate_distance.png)

The CV-QKD per-symbol key rate is computed from the Holevo bound using
symplectic eigenvalues of the joint Alice-Bob covariance matrix. The default
cutoff is 74.2 km, with excess noise as the dominant long-distance limiter.

### QBER under eavesdropping

![QBER vs interception probability](figures/qber_vs_interception.png)

The intercept-resend simulation verifies the canonical BB84 result: full
interception produces QBER = 25% from the Born rule applied twice
(1/2 x 1/2). Partial interception scales linearly: QBER = 0.25 x p.

A complete release inventory for the generated figures is in
[`figures/FIGURE_INVENTORY.md`](figures/FIGURE_INVENTORY.md).

## Technical Motivation

BB84 and GG02/CV-QKD are useful side-by-side because they expose different
physical and modelling tradeoffs. BB84 makes basis sifting, QBER, dark
counts, and decoy-state motivation transparent. GG02 brings in coherent
states, homodyne detection, covariance matrices, symplectic eigenvalues,
and the Holevo bound.

The repository keeps those concepts in a compact numerical form: vectorised
NumPy implementations, six notebooks that regenerate the figures, and tests
that lock the main physics checks and headline values.

## Notebooks

| # | File | Purpose |
|---|---|---|
| 01 | [`01_bb84_protocol.ipynb`](notebooks/01_bb84_protocol.ipynb) | BB84 protocol on the ideal channel: basis agreement, sifting, end-to-end pipeline at N = 100,000 |
| 02 | [`02_eve_attacks.ipynb`](notebooks/02_eve_attacks.ipynb) | Intercept-resend attack: QBER = 25% derivation, security threshold, security summary table |
| 03 | [`03_fiber_channel.ipynb`](notebooks/03_fiber_channel.ipynb) | Fiber channel model: transmittance, dark-count QBER, BB84 distance limit, parameter sweeps, decoy comparison |
| 04 | [`04_cvqkd_protocol.ipynb`](notebooks/04_cvqkd_protocol.ipynb) | GG02 protocol: phase-space scatter plots, channel transformation, mutual information vs distance |
| 05 | [`05_key_rate_analysis.ipynb`](notebooks/05_key_rate_analysis.ipynb) | CV-QKD key rate vs distance, excess-noise and reconciliation-efficiency sensitivity, beam-splitting intuition |
| 06 | [`06_protocol_comparison.ipynb`](notebooks/06_protocol_comparison.ipynb) | Headline comparison: BB84 and CV-QKD on the same axes with computed cutoffs and explicit caveats |

Every notebook can be rebuilt from its corresponding
`notebooks/_build_*_notebook.py` source. The `tests/test_physics.py`
regression suite locks the headline numbers.

## Installation

```powershell
# Clone the repository
git clone https://github.com/<your-handle>/qkd-protocol-simulator.git
cd qkd-protocol-simulator

# Optional: virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate    # macOS / Linux

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run all tests
python -m pytest tests/ -v

# Rebuild notebooks from source
python notebooks/_build_01_bb84_notebook.py
python notebooks/_build_02_eve_attacks_notebook.py
python notebooks/_build_03_fiber_channel_notebook.py
python notebooks/_build_04_cvqkd_protocol_notebook.py
python notebooks/_build_05_key_rate_notebook.py
python notebooks/_build_06_protocol_comparison_notebook.py

# Execute notebooks end-to-end when fresh outputs are needed
python notebooks/_execute_notebook.py 01_bb84_protocol.ipynb
python notebooks/_execute_notebook.py 02_eve_attacks.ipynb
python notebooks/_execute_notebook.py 03_fiber_channel.ipynb
python notebooks/_execute_notebook.py 04_cvqkd_protocol.ipynb
python notebooks/_execute_notebook.py 05_key_rate_analysis.ipynb
python notebooks/_execute_notebook.py 06_protocol_comparison.ipynb
```

The project runs on Python 3.10+ with NumPy, SciPy, Matplotlib, nbformat,
nbclient, and pytest.

## Project Structure

```text
qkd-protocol-simulator/
|-- src/
|   |-- __init__.py
|   |-- info_theory.py          # Entropy primitives + Gaussian entropy
|   |-- bb84.py                 # BB84 protocol + intercept-resend model
|   |-- channel.py              # Fiber channel + BB84 per-pulse key rate
|   |-- cvqkd.py                # GG02 + Holevo bound + per-symbol key rate
|   `-- plotting.py             # Shared semilogy helper for masked log-scale plots
|-- tests/
|   |-- smoke_test.py
|   |-- test_info_theory.py     # 30 tests
|   |-- test_bb84.py            # 37 tests
|   |-- test_channel.py         # 26 tests
|   |-- test_cvqkd.py           # 25 tests
|   `-- test_physics.py         # 32 cross-module regression tests
|-- notebooks/
|   |-- 01_bb84_protocol.ipynb
|   |-- 02_eve_attacks.ipynb
|   |-- 03_fiber_channel.ipynb
|   |-- 04_cvqkd_protocol.ipynb
|   |-- 05_key_rate_analysis.ipynb
|   |-- 06_protocol_comparison.ipynb
|   `-- _build_*_notebook.py    # Reproducible notebook builders
|-- figures/                    # 21 PNGs at 300 dpi + FIGURE_INVENTORY.md
|-- requirements.txt
|-- pyproject.toml
|-- LICENSE
`-- README.md
```

