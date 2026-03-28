"""
Builder for notebooks/05_key_rate_analysis.ipynb (Notebook 04/05: CV-QKD key rate).

Run:
    python notebooks/_build_05_key_rate_notebook.py

Then execute:
    python notebooks/_execute_notebook.py 05_key_rate_analysis.ipynb
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "05_key_rate_analysis.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# CV-QKD Key-Rate Analysis\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 04 visualised the GG02 protocol in phase space and "
        "ran the Alice-Bob mutual information. This notebook closes the "
        "loop: the Holevo bound is computed from the symplectic "
        "eigenvalues of the joint covariance matrix, and the per-symbol "
        "secure-key rate is\n"
        "\n"
        "$$K = \\max\\bigl(0,\\ \\beta\\,I(A:B) - \\chi(B:E)\\bigr)$$\n"
        "\n"
        "with $\\beta$ the reverse-reconciliation efficiency and $\\chi$ "
        "the asymptotic collective-attack Holevo bound from "
        "Laudenbach et al. (2018), Sections 6&ndash;7.\n"
        "\n"
        "**Convention contract.** Vacuum variance = 1, $\\hbar = 2$, "
        "$\\nu \\ge 1$ for physical states.\n"
        "\n"
        "**Untrusted-detector model.** Total $\\eta = "
        "\\eta_\\mathrm{ch} \\times \\eta_\\mathrm{det}$ is attributed to "
        "the channel available to Eve.\n"
        "\n"
        "**Range pre-claim caveat .** The maximum secure "
        "distance reported below is computed under the *stated* "
        "parameter set; it is not a universal CV-QKD-vs-BB84 ranking."
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
        "import numpy as np\n"
        "%matplotlib inline\n"
        "import matplotlib.pyplot as plt\n"
        "from scipy.optimize import brentq\n"
        "\n"
        "from src.cvqkd import (\n"
        "    cvqkd_holevo_bound_homodyne,\n"
        "    cvqkd_key_rate,\n"
        "    cvqkd_mutual_info_homodyne,\n"
        ")\n"
        "from src.channel import bb84_key_rate, fiber_transmittance\n"
        "from src.plotting import semilogy_positive\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
        "L = np.linspace(0.0, 300.0, 1001)\n"
    ))

    cells.append(md(
        "## 2. CV-QKD key rate vs distance\n"
        "\n"
        "Default parameters: $V_A = 20$ shot-noise units, $\\xi = 0.01$, "
        "$\\eta_{det} = 0.6$, $\\beta = 0.95$, $\\alpha = 0.2$ dB/km.\n"
        "\n"
        "We plot only positive rates on the semilogy axis and draw the "
        "cutoff distance as a vertical dashed line."
    ))

    cells.append(code(
        "rates_cv = cvqkd_key_rate(L)\n"
        "positive = rates_cv > 0\n"
        "if positive.all():\n"
        "    L_max_cv = float(L[-1])\n"
        "else:\n"
        "    cutoff_idx = int(np.where(~positive)[0][0])\n"
        "    L_max_cv = float(L[cutoff_idx - 1])\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(9, 6))\n"
        "semilogy_positive(\n"
        "    ax, L, rates_cv, '-', color='#C44E52', linewidth=2.5,\n"
        "    label='CV-QKD (GG02, homodyne, reverse rec.)',\n"
        ")\n"
        "ax.axvline(L_max_cv, color='red', linestyle='--', alpha=0.7,\n"
        "           label=fr'Max distance: ${L_max_cv:.0f}$ km')\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=14)\n"
        "ax.set_ylabel('Key rate per symbol (bits / symbol)', fontsize=14)\n"
        "ax.set_title('CV-QKD key rate vs fiber distance\\n'\n"
        "             '(GG02, homodyne, reverse reconciliation)', fontsize=15)\n"
        "ax.legend(fontsize=11, loc='upper right')\n"
        "param_text = (\n"
        "    r'$V_A = 20$, $\\xi = 0.01$' + '\\n'\n"
        "    r'$\\eta_{det} = 0.6$, $\\beta = 0.95$' + '\\n'\n"
        "    r'$\\alpha = 0.2$ dB/km'\n"
        ")\n"
        "ax.text(0.02, 0.04, param_text, transform=ax.transAxes, fontsize=10,\n"
        "        verticalalignment='bottom',\n"
        "        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))\n"
        "ax.set_xlim(0, 300)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_key_rate_distance.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "print(f'CV-QKD max secure distance (default params): {L_max_cv:.1f} km')\n"
    ))

    cells.append(md(
        "## 3. Excess noise sensitivity\n"
        "\n"
        "$\\xi$ is the input-referred excess noise. Even small values "
        "shave off significant range &mdash; CV-QKD is much more "
        "noise-sensitive than BB84 is to dark counts. The figure below "
        "compares four settings at fixed $\\beta = 0.95$, $V_A = 20$."
    ))

    cells.append(code(
        "xi_values = [0.001, 0.01, 0.05, 0.10]\n"
        "xi_styles = [('-', '#4C72B0'), ('--', '#55A868'),\n"
        "             ('-.', '#DD8452'), (':', '#C44E52')]\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(9, 6))\n"
        "summary = []\n"
        "for xi_val, (ls, color) in zip(xi_values, xi_styles):\n"
        "    r = cvqkd_key_rate(L, xi=xi_val)\n"
        "    semilogy_positive(ax, L, r, ls, color=color, linewidth=2,\n"
        "                      label=fr'$\\xi = {xi_val}$')\n"
        "    if (r > 0).any():\n"
        "        L_max = float(L[r > 0].max())\n"
        "    else:\n"
        "        L_max = 0.0\n"
        "    summary.append((xi_val, L_max))\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "ax.set_ylabel('Key rate per symbol', fontsize=13)\n"
        "ax.set_title('Excess-noise sensitivity of the CV-QKD key rate',\n"
        "             fontsize=14)\n"
        "ax.legend(fontsize=10)\n"
        "ax.set_xlim(0, 300)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'excess_noise_effect.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "print('xi      max distance (km)')\n"
        "for xi_val, L_max in summary:\n"
        "    print(f'{xi_val:>7.3f} {L_max:>16.1f}')\n"
    ))

