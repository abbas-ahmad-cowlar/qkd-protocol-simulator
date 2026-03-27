"""
Builder for notebooks/04_cvqkd_protocol.ipynb (Notebook 04/05: GG02 protocol).

Run:
    python notebooks/_build_04_cvqkd_protocol_notebook.py

Then execute:
    python notebooks/_execute_notebook.py 04_cvqkd_protocol.ipynb
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "04_cvqkd_protocol.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# CV-QKD: The GG02 Protocol\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 04/05 leaves discrete variables behind. Instead of bits and "
        "bases (BB84), GG02 (Grosshans & Grangier, 2002) modulates the "
        "two quadratures of a coherent state and reads them out with "
        "balanced homodyne detection &mdash; the same component family used "
        "in coherent optical telecom systems.\n"
        "\n"
        "**Convention contract.** Throughout this project we use the "
        "shot-noise-units / $\\hbar = 2$ convention:\n"
        "* vacuum / coherent state covariance $\\gamma = I$,\n"
        "* symplectic eigenvalue of vacuum $\\nu = 1$,\n"
        "* physical states satisfy $\\nu \\ge 1$.\n"
        "\n"
        "This notebook visualises Alice's modulation, the channel's "
        "action, and the Alice-Bob mutual information. The companion "
        "notebook `05_key_rate_analysis.ipynb` runs the Holevo bound and "
        "the secure-key rate."
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
        "\n"
        "from src.cvqkd import (\n"
        "    cvqkd_mutual_info_homodyne,\n"
        "    cvqkd_mutual_info_heterodyne,\n"
        ")\n"
        "from src.channel import fiber_transmittance\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
        "rng = np.random.default_rng(42)\n"
        "\n"
        "V_A = 20.0      # Modulation variance in shot-noise units\n"
        "ETA_DET = 0.6   # Homodyne detector efficiency\n"
        "XI = 0.01       # Excess noise (input-referred)\n"
        "N = 10_000      # Phase-space samples\n"
    ))

    cells.append(md(
        "## 2. Alice's two-quadrature Gaussian modulation\n"
        "\n"
        "Alice draws $x_A$ and $p_A$ independently from $\\mathcal{N}(0, "
        "V_A)$ and prepares a coherent state with displacement "
        "$\\propto x_A + i\\,p_A$. The cloud of $(x_A, p_A)$ samples is "
        "isotropic with radius $\\sqrt{V_A}$ &mdash; that is the "
        "modulation, not the quantum noise. The shot-noise of each "
        "individual coherent state is the unit-variance vacuum spread "
        "added to every point."
    ))

    cells.append(code(
        "x_A = rng.normal(0.0, np.sqrt(V_A), N)\n"
        "p_A = rng.normal(0.0, np.sqrt(V_A), N)\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(7, 7))\n"
        "ax.scatter(x_A, p_A, s=2, alpha=0.3, color='#4C72B0')\n"
        "circle = plt.Circle((0.0, 0.0), np.sqrt(V_A), fill=False,\n"
        "                    color='red', linestyle='--', linewidth=2,\n"
        "                    label=fr'$\\sqrt{{V_A}} = {np.sqrt(V_A):.2f}$')\n"
        "ax.add_patch(circle)\n"
        "ax.set_xlabel(r'$x_A$ (shot-noise units)', fontsize=13)\n"
        "ax.set_ylabel(r'$p_A$ (shot-noise units)', fontsize=13)\n"
        "ax.set_title(fr'Alice modulation ($V_A = {V_A:.0f}$, $N = {N:,}$)',\n"
        "             fontsize=14)\n"
        "ax.set_aspect('equal')\n"
        "ax.legend(fontsize=11)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_gaussian_modulation.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
    ))

    cells.append(md(
        "## 3. Channel action: attenuation and excess noise\n"
        "\n"
        "Each quadrature is attenuated by $\\sqrt{\\eta}$ and the "
        "channel adds Gaussian noise with variance $1 + \\eta\\xi$ "
        "(unit shot-noise plus excess noise referred to the input). "
        "Bob's cloud is therefore *smaller* (rescaled by $\\sqrt{\\eta}$) "
        "and *noisier* (additional Gaussian blur). At $\\eta = 0.5$ "
        "(roughly 15 km of standard fiber) and $\\xi = 0.01$, both "
        "effects are visible side-by-side."
    ))

    cells.append(code(
        "L_demo = 15.0  # km\n"
        "eta_demo = float(fiber_transmittance(L_demo) * ETA_DET)\n"
        "noise_var = 1.0 + eta_demo * XI\n"
        "\n"
        "x_B = np.sqrt(eta_demo) * x_A + rng.normal(0.0, np.sqrt(noise_var), N)\n"
        "p_B = np.sqrt(eta_demo) * p_A + rng.normal(0.0, np.sqrt(noise_var), N)\n"
        "\n"
        "fig, axes = plt.subplots(1, 2, figsize=(14, 6))\n"
        "axes[0].scatter(x_A, p_A, s=2, alpha=0.3, color='#4C72B0')\n"
        "axes[0].set_title(\"Alice's phase space\", fontsize=13)\n"
        "axes[1].scatter(x_B, p_B, s=2, alpha=0.3, color='#DD8452')\n"
        "axes[1].set_title(\n"
        "    fr\"Bob's phase space ($L = {L_demo:.0f}$ km, \"\n"
        "    fr\"$\\eta = {eta_demo:.2f}$, $\\xi = {XI}$)\",\n"
        "    fontsize=13,\n"
        ")\n"
        "for ax in axes:\n"
        "    ax.set_xlabel('quadrature $x$ (SNU)', fontsize=12)\n"
        "    ax.set_ylabel('quadrature $p$ (SNU)', fontsize=12)\n"
        "    ax.set_aspect('equal')\n"
        "lim = float(np.max([\n"
        "    np.max(np.abs(x_A)), np.max(np.abs(p_A)),\n"
        "    np.max(np.abs(x_B)), np.max(np.abs(p_B)),\n"
        "])) * 1.05\n"
        "for ax in axes:\n"
        "    ax.set_xlim(-lim, lim)\n"
        "    ax.set_ylim(-lim, lim)\n"
        "plt.suptitle('GG02 phase space through the fiber channel', fontsize=15)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_phase_space_channel.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "print(f'Demo: L = {L_demo} km  ->  eta = {eta_demo:.4f}, '\n"
        "      f'noise variance = {noise_var:.4f}')\n"
    ))

    cells.append(md(
        "## 4. SNR and homodyne mutual information vs distance\n"
        "\n"
        "$\\mathrm{SNR} = \\eta V_A / (1 + \\eta\\xi)$ on a single "
        "homodyne quadrature. The mutual information is "
        "$I(A:B) = \\tfrac{1}{2} \\log_2(1 + \\mathrm{SNR})$. Both "
        "decay exponentially with distance because $\\eta(L)$ does."
    ))

    cells.append(code(
        "L_grid = np.linspace(0.0, 200.0, 1001)\n"
        "eta_grid = fiber_transmittance(L_grid) * ETA_DET\n"
        "snr_grid = eta_grid * V_A / (1.0 + eta_grid * XI)\n"
        "I_hom_grid = cvqkd_mutual_info_homodyne(V_A, eta_grid, XI)\n"
        "\n"
        "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n"
        "axes[0].semilogy(L_grid, snr_grid, '-', color='#4C72B0', linewidth=2)\n"
        "axes[0].set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "axes[0].set_ylabel('SNR (shot-noise units)', fontsize=13)\n"
        "axes[0].set_title(\n"
        "    fr'CV-QKD SNR ($V_A = {V_A:.0f}$, '\n"
        "    fr'$\\eta_{{det}} = {ETA_DET}$, $\\xi = {XI}$)',\n"
        "    fontsize=14,\n"
        ")\n"
        "axes[0].set_xlim(0, 200)\n"
        "\n"
        "mask = I_hom_grid > 0\n"
        "axes[1].plot(L_grid[mask], I_hom_grid[mask], '-', color='#4C72B0',\n"
        "             linewidth=2)\n"
        "axes[1].set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "axes[1].set_ylabel(r'$I(A:B)$ (bits / symbol)', fontsize=13)\n"
        "axes[1].set_title('Homodyne mutual information', fontsize=14)\n"
        "axes[1].set_xlim(0, 200)\n"
        "\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'cvqkd_snr_and_mutual_info.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "for L in [0, 25, 50, 75, 100, 150, 200]:\n"
        "    e = float(fiber_transmittance(L) * ETA_DET)\n"
        "    I = float(cvqkd_mutual_info_homodyne(V_A, e, XI))\n"
        "    print(f'  L = {L:>3} km  ->  eta = {e:.4e}  I(A:B) = {I:.4f} bits/symbol')\n"
    ))

    cells.append(md(
        "## 5. Homodyne vs heterodyne &mdash; mutual information only\n"
        "\n"
        "**Modeling caveat.** This panel compares the *raw* mutual "
        "information of the two detection schemes; it is **not** a "
        "secure-key comparison because we have not implemented the "
        "heterodyne Holevo bound. With one quadrature measured per "
        "channel use, homodyne carries the leading $1/2$. Heterodyne "
        "measures both quadratures but pays one extra unit of vacuum "
        "noise per arm.\n"
        "\n"
        "$$ I_\\mathrm{hom} = \\tfrac{1}{2}\\log_2\\!\\bigl(1 + \\tfrac{\\eta V_A}{1 + \\eta\\xi}\\bigr), \\quad I_\\mathrm{het} = \\log_2\\!\\bigl(1 + \\tfrac{\\eta V_A}{2 + \\eta\\xi}\\bigr). $$"
    ))

    cells.append(code(
        "I_het_grid = cvqkd_mutual_info_heterodyne(V_A, eta_grid, XI)\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(8, 5))\n"
        "ax.plot(L_grid, I_hom_grid, '-', linewidth=2, color='#4C72B0',\n"
        "        label='Homodyne')\n"
        "ax.plot(L_grid, I_het_grid, '--', linewidth=2, color='#DD8452',\n"
        "        label='Heterodyne')\n"
        "ax.set_xlabel('Fiber distance (km)', fontsize=13)\n"
        "ax.set_ylabel(r'$I(A:B)$ (bits / symbol)', fontsize=13)\n"
        "ax.set_title('Homodyne vs heterodyne mutual information\\n'\n"
        "             '(NOT a secure-key comparison)', fontsize=14)\n"
        "ax.legend(fontsize=11)\n"
        "ax.set_xlim(0, 200)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'homodyne_vs_heterodyne.png', dpi=300,\n"
        "            bbox_inches='tight')\n"
        "plt.show()\n"
        "\n"
        "print('At eta=1, xi=0:')\n"
        "print(f'  homodyne  I = {float(cvqkd_mutual_info_homodyne(V_A, 1.0, 0.0)):.4f}')\n"
        "print(f'  hetero    I = {float(cvqkd_mutual_info_heterodyne(V_A, 1.0, 0.0)):.4f}')\n"
    ))

    cells.append(md(
        "## 6. In the lab\n"
        "\n"
        "A practical CV-QKD receiver uses balanced homodyne detection: "
        "the signal mode is mixed with a strong local oscillator on a "
        "50:50 beam splitter, and the difference of the two photodiode "
        "currents is proportional to the chosen quadrature. The same "
        "component families &mdash; coherent 1550 nm lasers, balanced "
        "detectors, ADCs, and DSP chains &mdash; are common in classical "
        "coherent telecom, which is why CV-QKD can integrate naturally "
        "with deployed fiber infrastructure."
    ))

    cells.append(md(
        "## 7. What this notebook demonstrates\n"
        "\n"
        "1. **Two-quadrature Gaussian modulation.** Alice's $(x_A, p_A)$ "
        "samples form an isotropic Gaussian with variance $V_A$.\n"
        "2. **Channel action.** Bob's cloud is shrunk by $\\sqrt{\\eta}$ "
        "and broadened by additional Gaussian noise of variance "
        "$1 + \\eta\\xi$.\n"
        "3. **SNR collapses exponentially with distance.** Same fiber "
        "transmittance as Notebook 03 BB84.\n"
        "4. **Homodyne vs heterodyne.** Different prefactor ($1/2$ vs "
        "$1$) and different noise floor (1 vs 2). Comparison is for "
        "raw mutual information only, not a secure-key claim.\n"
        "\n"
        "Notebook 05 takes these foundations and runs the Holevo bound + "
        "asymptotic key-rate calculation."
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
