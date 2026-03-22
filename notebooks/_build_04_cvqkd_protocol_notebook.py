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
