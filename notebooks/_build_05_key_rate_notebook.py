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

    cells.append(md(
        "## 4. Reconciliation-efficiency sensitivity\n"
        "\n"
        "$\\beta$ multiplies $I(A:B)$ but **not** the Holevo bound. "
        "Lowering $\\beta$ therefore shifts the cutoff inwards: the "
        "rate becomes negative sooner."
    ))

    cells.append(code(
        "beta_values = [0.80, 0.90, 0.95, 1.00]\n"
        "beta_styles = [('-', '#4C72B0'), ('--', '#55A868'),\n"
        "               ('-.', '#DD8452'), (':', '#C44E52')]\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(9, 6))\n"
        "summary = []\n"
        "for beta_val, (ls, color) in zip(beta_values, beta_styles):\n"
        "    r = cvqkd_key_rate(L, beta=beta_val)\n"
        "    semilogy_positive(ax, L, r, ls, color=color, linewidth=2,\n"
        "                      label=fr'$\\beta = {beta_val}$')\n"
        "    if (r > 0).any():\n"
        "        L_max = float(L[r > 0].max())\n"
        "    else:\n"
        "        L_max = 0.0\n"
        "    summary.append((beta_val, L_max))\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "ax.set_ylabel('Key rate per symbol', fontsize=13)\n"
        "ax.set_title('Reconciliation-efficiency sensitivity', fontsize=14)\n"
        "ax.legend(fontsize=10)\n"
        "ax.set_xlim(0, 300)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_reconciliation_efficiency.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "print('beta    max distance (km)')\n"
        "for beta_val, L_max in summary:\n"
        "    print(f'{beta_val:>5.2f}   {L_max:>14.1f}')\n"
    ))

    cells.append(md(
        "## 5. Pure-loss intuition: $I(A:B)$ vs $\\chi(B:E)$\n"
        "\n"
        "For $\\xi = 0$ (pure-loss channel), the standard physical "
        "picture is a beam splitter that diverts the lost fraction "
        "$1 - \\eta$ to Eve. Plotting both terms vs transmittance "
        "$\\eta$ exposes the secure region: $\\beta\\,I(A:B) > "
        "\\chi(B:E)$.\n"
        "\n"
        "**Beam-splitting vs entangling cloner.** "
        "Pure-loss collective attacks are intuitively a beam splitter; "
        "with $\\xi > 0$ the standard collective Gaussian attack is "
        "modelled as an *entangling cloner* &mdash; a beam splitter "
        "with an entangled ancilla that reproduces the observed "
        "$(\\eta, \\xi)$ statistics. The Holevo bound from the "
        "covariance matrix bounds Eve's information in **both** cases, "
        "so a single computation works for the pure-loss and "
        "excess-noise regimes."
    ))

    cells.append(code(
        "etas = np.linspace(0.01, 1.0, 200)\n"
        "I_AB = cvqkd_mutual_info_homodyne(20, etas, 0.0)\n"
        "chi_BE = cvqkd_holevo_bound_homodyne(20, etas, 0.0)\n"
        "beta_demo = 0.95\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(8, 5))\n"
        "ax.plot(etas, I_AB, '-', linewidth=2, color='#4C72B0',\n"
        "        label=r'$I(A:B)$')\n"
        "ax.plot(etas, beta_demo * I_AB, ':', linewidth=2, color='#4C72B0',\n"
        "        alpha=0.7, label=fr'$\\beta\\, I(A:B)$, $\\beta={beta_demo}$')\n"
        "ax.plot(etas, chi_BE, '--', linewidth=2, color='#C44E52',\n"
        "        label=r'$\\chi(B:E)$')\n"
        "secure = beta_demo * I_AB > chi_BE\n"
        "ax.fill_between(etas, chi_BE, beta_demo * I_AB,\n"
        "                where=secure, alpha=0.2, color='green',\n"
        "                label='Secure region (positive rate)')\n"
        "ax.set_xlabel(r'Channel transmittance $\\eta$', fontsize=13)\n"
        "ax.set_ylabel('Information (bits / symbol)', fontsize=13)\n"
        "ax.set_title(r'Pure-loss CV-QKD ($V_A = 20$, $\\xi = 0$):'\n"
        "             r' $I(A:B)$ vs $\\chi(B:E)$', fontsize=14)\n"
        "ax.legend(fontsize=10, loc='upper left')\n"
        "ax.set_xlim(0, 1)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_pure_loss_information.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "if secure.any():\n"
        "    eta_thresh = float(etas[secure][0])\n"
        "    print(f'Pure-loss secure-region threshold (beta={beta_demo}): '\n"
        "          f'eta >= {eta_thresh:.3f}')\n"
        "else:\n"
        "    print('No secure region under these parameters.')\n"
    ))

    cells.append(md(
        "## 6. BB84 vs CV-QKD &mdash; same axes, **different units**\n"
        "\n"
        "We overlay the Notebook 03 BB84 per-pulse curve and the Notebook 04/05 "
        "CV-QKD per-symbol curve on the same semilogy axis. The "
        "y-axis units are **different** (bits / pulse vs bits / "
        "symbol), so the visual ordering is *not* a direct security "
        "ranking; this overlay is meant to surface the cutoff "
        "behaviour of each protocol under the stated parameter sets, "
        "under the stated parameter set."
    ))

    cells.append(code(
        "rates_bb = bb84_key_rate(L)\n"
        "rates_cv = cvqkd_key_rate(L)\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(9, 6))\n"
        "semilogy_positive(\n"
        "    ax, L, rates_bb, '-', color='#4C72B0', linewidth=2,\n"
        "    label='BB84 per-pulse (Notebook 03 default)',\n"
        ")\n"
        "semilogy_positive(\n"
        "    ax, L, rates_cv, '--', color='#C44E52', linewidth=2,\n"
        "    label='CV-QKD per-symbol (GG02 default)',\n"
        ")\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "ax.set_ylabel('Key rate (bits / pulse or bits / symbol)', fontsize=13)\n"
        "ax.set_title(\n"
        "    'BB84 vs CV-QKD key rate vs distance\\n'\n"
        "    '(different units: per pulse vs per symbol; not a direct security ranking)',\n"
        "    fontsize=13,\n"
        ")\n"
        "ax.legend(fontsize=11, loc='upper right')\n"
        "ax.set_xlim(0, 300)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'bb84_vs_cvqkd_key_rate.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "L_max_bb = float(L[rates_bb > 0].max()) if (rates_bb > 0).any() else 0.0\n"
        "L_max_cv2 = float(L[rates_cv > 0].max()) if (rates_cv > 0).any() else 0.0\n"
        "print(f'BB84   max distance (per pulse, defaults):  {L_max_bb:.1f} km')\n"
        "print(f'CV-QKD max distance (per symbol, defaults): {L_max_cv2:.1f} km')\n"
    ))

    cells.append(md(
        "## 7. Forward vs reverse reconciliation\n"
        "\n"
        "| Feature | Forward | Reverse |\n"
        "|---|---|---|\n"
        "| Key source | Alice | Bob |\n"
        "| Key rate | $I(A:B) - \\chi(A:E)$ | $\\beta\\,I(A:B) - \\chi(B:E)$ |\n"
        "| Works at $\\eta < 0.5$? | **No** (the 3 dB loss limit) | **Yes** |\n"
        "| Practical range | $\\sim 15$ km | $\\sim 50$&ndash;$100^+$ km |\n"
        "| Used in GG02? | No | **Yes** |\n"
        "\n"
        "Reverse reconciliation works below 3 dB because Bob's "
        "measurement noise (shot noise) is *independent* of Eve. With "
        "forward reconciliation, Alice's uncertainty about Bob is "
        "augmented by Eve's information; with reverse, Bob's "
        "uncertainty about Alice is **not**, so $\\chi(B:E) < "
        "\\chi(A:E)$ at low $\\eta$. The implementation in "
        "`src.cvqkd.cvqkd_key_rate` uses reverse reconciliation."
    ))

    cells.append(md(
        "## 8. What this notebook demonstrates\n"
        "\n"
        "1. **CV-QKD has a finite distance limit** &mdash; the cutoff "
        "value depends on $V_A$, $\\xi$, $\\eta_\\mathrm{det}$, "
        "$\\beta$, and $\\alpha$.\n"
        "2. **Excess noise dominates the long-distance behaviour.** "
        "The cutoff falls dramatically as $\\xi$ rises through "
        "$0.001 \\to 0.10$.\n"
        "3. **Reconciliation efficiency multiplies $I(A:B)$ only.** "
        "Lower $\\beta$ shrinks the secure region but does not "
        "reduce $\\chi(B:E)$.\n"
        "4. **Pure-loss intuition.** Crossing $\\beta\\,I(A:B) = "
        "\\chi(B:E)$ on the $\\eta$-axis identifies the secure region "
        "without simulating the protocol.\n"
        "5. **Holevo from covariance matrix is universal.** The same "
        "$\\chi$ formula works for pure-loss beam-splitting and "
        "excess-noise entangling-cloner attacks.\n"
        "6. **No range pre-claims.** The maximum distances in this "
        "notebook are computed from the stated parameter sets; they "
        "are not universal CV-vs-DV statements.\n"
        "\n"
        "Notebook 06 will sit on top of this and produce the headline "
        "comparison figure."
    ))

    nb.cells = cells
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    return nb


def main():
    nb = build_notebook()
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with NB_PATH.open("w", encoding="utf-8") as fh:
        nbf.write(nb, fh)
    print(f"Wrote {NB_PATH}")


if __name__ == "__main__":
    main()
