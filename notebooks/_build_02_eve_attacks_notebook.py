"""
Builder script for notebooks/02_eve_attacks.ipynb.

Run once with:
    python notebooks/_build_02_eve_attacks_notebook.py

Then execute via notebooks/_execute_notebook02.py to populate outputs and
save figures.
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "02_eve_attacks.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# Eavesdropper Attacks on BB84\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 02 introduces Eve. We add a single function to `src/bb84.py` "
        "&mdash; `eve_intercept_resend` &mdash; and use it to verify two of "
        "the most quoted BB84 results:\n"
        "\n"
        "1. **Full intercept-resend produces $\\mathrm{QBER} = 25\\%$** "
        "(not 50%, despite Eve guessing the wrong basis half the time).\n"
        "2. **QBER is linear in Eve's interception probability:** "
        "$\\mathrm{QBER}(p) = 0.25\\,p$.\n"
        "\n"
        "We then push to the security threshold and chart the key rate "
        "vs. interception probability for two error-correction efficiencies. "
        "All values are simulated end-to-end &mdash; nothing is hardcoded.\n"
        "\n"
        "**Caveat:** every key-rate plot in this notebook "
        "uses the *idealized single-photon source model*. Real weak "
        "coherent sources are vulnerable to PNS attacks; that is "
        "discussed conceptually in Step 3.4 and addressed by decoy states."
    ))

    cells.append(md("## 1. Bootstrap and imports"))

    cells.append(code(
        "from pathlib import Path\n"
        "import sys\n"
        "\n"
        "\n"
        "def find_project_root(start=None):\n"
        "    start = Path.cwd().resolve() if start is None else Path(start).resolve()\n"
        "    for candidate in [start, *start.parents]:\n"
        "        if (candidate / 'src').is_dir() and (candidate / 'notebooks').is_dir():\n"
        "            return candidate\n"
        "    raise RuntimeError('Could not find project root')\n"
        "\n"
        "\n"
        "PROJECT_ROOT = find_project_root()\n"
        "FIG_DIR = PROJECT_ROOT / 'figures'\n"
        "FIG_DIR.mkdir(parents=True, exist_ok=True)\n"
        "\n"
        "if str(PROJECT_ROOT) not in sys.path:\n"
        "    sys.path.insert(0, str(PROJECT_ROOT))\n"
        "\n"
        "print(f'Project root: {PROJECT_ROOT}')\n"
    ))

    cells.append(code(
        "import numpy as np\n"
        "%matplotlib inline\n"
        "import matplotlib.pyplot as plt\n"
        "from scipy.optimize import brentq\n"
        "\n"
        "from src.bb84 import (\n"
        "    alice_prepare, bob_measure, sift, estimate_qber,\n"
        "    error_correction, final_key_length, eve_intercept_resend,\n"
        ")\n"
        "from src.info_theory import binary_entropy\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
        "\n"
        "rng_master = np.random.default_rng(2026)\n"
        "N = 100_000\n"
    ))

    cells.append(md(
        "## 2. The intercept-resend attack &mdash; QBER = 25%\n"
        "\n"
        "Eve intercepts every qubit, picks $Z$ or $X$ at random, measures, "
        "re-prepares a fresh photon in *her* basis, and forwards it to "
        "Bob. The Born rule applies twice:\n"
        "\n"
        "* Eve's wrong-basis measurement (probability 1/2) gives a uniform "
        "  random result.\n"
        "* Bob's correct-basis measurement of Eve's wrong-basis state has "
        "  50% overlap with each eigenstate, so Bob errs with probability "
        "  1/2 on those rounds.\n"
        "\n"
        "$\\mathrm{QBER} = P(\\text{Eve wrong}) \\times P(\\text{Bob err} "
        "\\mid \\text{Eve wrong}) = 1/2 \\times 1/2 = 1/4$."
    ))

    cells.append(code(
        "rng = np.random.default_rng(2026)\n"
        "\n"
        "alice_bits, alice_bases = alice_prepare(N, rng=rng)\n"
        "eve_bits, fwd_bits, fwd_bases, intercepted = eve_intercept_resend(\n"
        "    alice_bits, alice_bases, interception_rate=1.0, rng=rng,\n"
        ")\n"
        "bob_bases = rng.integers(0, 2, N)\n"
        "bob_bits = bob_measure(fwd_bits, fwd_bases, bob_bases, rng=rng)\n"
        "\n"
        "alice_sifted, bob_sifted = sift(alice_bits, bob_bits, alice_bases, bob_bases)\n"
        "qber_full_eve = float(np.mean(alice_sifted != bob_sifted))\n"
        "\n"
        "print(f'BB84 with full intercept-resend (N = {N:,}, seed = 2026):')\n"
        "print(f'  Sifted key length : {len(alice_sifted):,}')\n"
        "print(f'  QBER              : {qber_full_eve:.4f}  (theory 0.2500)')\n"
        "print(f'  Eve detected ?    : {\"YES\" if qber_full_eve > 0.05 else \"NO\"}')\n"
    ))

    cells.append(md(
        "### 2.1 Comparison: with vs. without Eve\n"
