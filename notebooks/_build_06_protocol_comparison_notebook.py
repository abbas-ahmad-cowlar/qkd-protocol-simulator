"""
Builder for notebooks/06_protocol_comparison.ipynb (Notebook 06: headline comparison).

Run:
    python notebooks/_build_06_protocol_comparison_notebook.py

Then execute:
    python notebooks/_execute_notebook.py 06_protocol_comparison.ipynb
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "06_protocol_comparison.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# BB84 vs CV-QKD: Headline Protocol Comparison\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 06 closes the project. No new physics modules are added; we "
        "combine everything from the earlier notebooks into a single "
        "headline figure that compares the BB84 and CV-QKD secure-key "
        "rates on the same axes under explicit, reproducible parameter "
        "sets.\n"
        "\n"
        "## What this comparison can and cannot claim\n"
        "\n"
        "* Both curves are *asymptotic* secure-key rates under stated "
        "parameter assumptions. **Finite-key effects are not included.**\n"
        "* BB84 rates are reported **per emitted pulse**; CV-QKD rates "
        "are reported **per coherent-state symbol**. These are related "
        "channel-use normalisations &mdash; *not* a direct hardware "
        "throughput comparison.\n"
        "* Cutoff distances and any \"winner\" language depend on the "
        "specific parameter set. Changing detector efficiency, excess "
        "noise, dark counts, or reconciliation efficiency changes the "
        "relative ordering.\n"
        "* The defensible claim is that this repository implements and "
        "validates comparable DV/CV-QKD asymptotic models under stated "
        "assumptions; it does not claim that one protocol universally "
        "beats the other.\n"
        "\n"
        "## Stated parameters\n"
        "\n"
        "**BB84** (asymptotic simplified, idealised single-photon source):\n"
        "* $\\mu = 0.1$, $\\eta_\\mathrm{det} = 0.2$, $p_\\mathrm{dark} = 10^{-6}$, $e_\\mathrm{det} = 0$\n"
        "* $f_\\mathrm{ec} = 1.16$, $\\alpha = 0.2$ dB/km\n"
        "* rate normalisation: per emitted pulse\n"
        "\n"
        "**CV-QKD GG02** (asymptotic collective Gaussian attack, "
        "untrusted-detector model):\n"
        "* $V_A = 20$ shot-noise units, $\\xi = 0.01$\n"
        "* $\\eta_\\mathrm{det} = 0.6$, $\\beta = 0.95$, $\\alpha = 0.2$ dB/km\n"
        "* rate normalisation: per coherent-state symbol"
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
        "print(f'Project root: {PROJECT_ROOT}')\n"
    ))

    cells.append(code(
        "import os\n"
        "\n"
        "import numpy as np\n"
        "%matplotlib inline\n"
        "import matplotlib.pyplot as plt\n"
        "from scipy.optimize import brentq\n"
        "\n"
        "from src.channel import (\n"
        "    bb84_key_rate, fiber_transmittance, qber_channel,\n"
        ")\n"
        "from src.cvqkd import (\n"
        "    cvqkd_holevo_bound_homodyne,\n"
        "    cvqkd_key_rate,\n"
        "    cvqkd_mutual_info_homodyne,\n"
        ")\n"
        "from src.info_theory import binary_entropy\n"
        "from src.plotting import semilogy_positive\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
        "\n"
        "L = np.linspace(0.0, 300.0, 1001)\n"
    ))

    cells.append(md(
        "## 2. Compute both key-rate curves\n"
        "\n"
        "These call the existing Notebook 03 / Notebook 04/05 implementations "
        "verbatim &mdash; the headline figure is just a combined result."
    ))

    cells.append(code(
        "rate_bb84 = bb84_key_rate(L)\n"
        "rate_cvqkd = cvqkd_key_rate(L)\n"
        "\n"
        "print(f'BB84   K(0)   = {float(bb84_key_rate(0)):.6e} bits / pulse')\n"
        "print(f'CV-QKD K(0)   = {float(cvqkd_key_rate(0)):.6e} bits / symbol')\n"
        "print(f'BB84   K(50)  = {float(bb84_key_rate(50)):.6e} bits / pulse')\n"
        "print(f'CV-QKD K(50)  = {float(cvqkd_key_rate(50)):.6e} bits / symbol')\n"
