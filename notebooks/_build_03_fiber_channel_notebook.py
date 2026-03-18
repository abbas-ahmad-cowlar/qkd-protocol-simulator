"""
Builder for notebooks/03_fiber_channel.ipynb (Notebook 03: Fiber Channel Model).

Run with:
    python notebooks/_build_03_fiber_channel_notebook.py

Then execute via notebooks/_execute_notebook.py 03_fiber_channel.ipynb
to populate outputs and save the four PNG figures.
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "03_fiber_channel.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# Fiber Channel Model for BB84\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 03 extends the ideal BB84 simulator to a direct-fiber "
        "channel model. We add a "
        "single new module &mdash; `src/channel.py` &mdash; that turns "
        "fiber attenuation, detector efficiency, dark counts and "
        "misalignment into a per-pulse secure-key rate, and we generate "
        "the headline figure of the project: BB84 key rate vs. fiber "
        "distance.\n"
        "\n"
        "Three effects limit performance:\n"
        "\n"
        "1. **Fiber attenuation** &mdash; $\\eta(L) = 10^{-\\alpha L / 10}$ "
        "with $\\alpha = 0.2$ dB/km at the 1550 nm telecom-C minimum.\n"
        "2. **Detector efficiency** &mdash; $\\eta_{det} \\approx 0.2$ for "
        "InGaAs APDs, up to $\\sim 0.9$ for SNSPDs.\n"
        "3. **Dark counts** &mdash; $p_{dark} \\sim 10^{-6}$ per detector "
        "per gate, summing to $2 p_{dark}$ across BB84's two detectors.\n"
        "\n"
        "**Key constraint:** unlike classical telecom, QKD cannot use EDFA "
        "amplifiers to overcome fiber loss &mdash; the no-cloning theorem "
        "(Notebook 02) forbids it. Attenuation is the fundamental distance-"
        "limit driver for direct-fiber QKD, and that is exactly why the "
        "headline figure below has a hard cutoff.\n"
        "\n"
        "**Security caveat.** The non-decoy BB84 curve below "
        "is the *idealised single-photon source model*. We also implement "
        "the simplified asymptotic decoy-state estimate (Lo, Ma & Chen, "
        "2005) so the realistic weak-coherent-pulse case can be compared "
        "directly."
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
        "from src.channel import (\n"
        "    fiber_transmittance, bb84_signal_prob, total_detection_prob,\n"
        "    qber_channel, bb84_key_rate, decoy_bb84_key_rate,\n"
        ")\n"
        "from src.info_theory import binary_entropy\n"
        "from src.plotting import semilogy_positive\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
        "\n"
        "L_dense = np.linspace(0, 300, 1001)\n"
    ))

    cells.append(md(
        "## 2. Fiber transmittance &mdash; the dB convention\n"
        "\n"
        "$\\eta(L) = 10^{-\\alpha L / 10}$. The base is **10**, not "
        "$e$. At $\\alpha = 0.2$ dB/km, every 50 km adds 10 dB of loss "
        "&mdash; a factor of 10 drop in transmittance."
    ))

    cells.append(code(
        "fig, ax = plt.subplots(figsize=(8, 5))\n"
        "eta = fiber_transmittance(L_dense)\n"
        "ax.semilogy(L_dense, eta, '-', color='#4C72B0', linewidth=2)\n"
        "for Lm, label in [(50, '10 dB'), (100, '20 dB'), (150, '30 dB')]:\n"
        "    eta_m = fiber_transmittance(Lm)\n"
        "    ax.plot(Lm, eta_m, 'o', color='#DD8452', markersize=8, zorder=5)\n"
        "    ax.annotate(\n"
        "        f'{Lm} km: $\\\\eta = {eta_m:.4f}$\\n({label} loss)',\n"
        "        xy=(Lm, eta_m), xytext=(Lm + 15, eta_m * 3),\n"
        "        fontsize=9, arrowprops=dict(arrowstyle='->', color='gray'),\n"
        "    )\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "ax.set_ylabel(r'Transmittance $\\eta(L)$', fontsize=13)\n"
        "ax.set_title(r'Fiber Transmittance at 1550 nm '\n"
        "             r'($\\alpha = 0.2$ dB/km)', fontsize=14)\n"
        "ax.set_xlim(0, 300)\n"
        "ax.set_ylim(1e-7, 2)\n"
        "plt.tight_layout()\n"
