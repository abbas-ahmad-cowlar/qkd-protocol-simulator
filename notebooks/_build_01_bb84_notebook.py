"""
Builder script: writes notebooks/01_bb84_protocol.ipynb using nbformat.

Run once with:
    python notebooks/_build_01_bb84_notebook.py

After the notebook is written, execute it (nbclient) to populate output
cells and save the figures into figures/.
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "01_bb84_protocol.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# BB84 Quantum Key Distribution Protocol\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "The BB84 protocol (Bennett & Brassard, 1984) lets two parties — "
        "Alice and Bob — establish a shared secret key over an insecure "
        "quantum channel. This notebook runs an **ideal-channel** simulation "
        "(no eavesdropper, no fiber loss) using the seven `src/bb84.py` "
        "functions built in Notebook 01.\n"
        "\n"
        "## Protocol pipeline\n"
        "\n"
        "1. **Preparation** &mdash; Alice randomly chooses a bit and a basis, "
        "encoding it into one of $\\{|0\\rangle, |1\\rangle, |+\\rangle, "
        "|-\\rangle\\}$.\n"
        "2. **Transmission** &mdash; Single photons travel to Bob.\n"
        "3. **Measurement** &mdash; Bob picks a random basis. Same basis as "
        "Alice $\\Rightarrow$ deterministic; mismatched basis $\\Rightarrow$ "
        "uniform 50/50 (Born rule).\n"
        "4. **Sifting** &mdash; Alice and Bob publicly compare *bases* (not "
        "bit values). Mismatched rounds are dropped.\n"
        "5. **QBER estimation** &mdash; A random subset of sifted bits is "
        "disclosed to estimate the error rate. The disclosed sample is "
        "permanently removed.\n"
        "6. **Error correction** &mdash; A perfect-reconciliation stub leaks "
        "$f_{ec} \\, n \\, h(\\mathrm{QBER})$ bits to Eve.\n"
        "7. **Privacy amplification** &mdash; Universal$_2$ hashing yields a "
        "final key of length $L = N_{\\text{remaining}} \\, "
        "\\max(0, 1 - h(\\mathrm{QBER}) - f_{ec} \\, h(\\mathrm{QBER}))$.\n"
    ))

    cells.append(md(
        "## 1. Bootstrap and imports\n"
        "\n"
        "The bootstrap cell finds the project root from the notebook's CWD, "
        "appends it to `sys.path`, and creates the `figures/` directory."
    ))

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
        "print(f'Figure dir : {FIG_DIR}')\n"
    ))

    cells.append(code(
        "import numpy as np\n"
        "%matplotlib inline\n"
        "import matplotlib.pyplot as plt\n"
        "\n"
        "from src.bb84 import (\n"
        "    alice_prepare, bob_measure, sift, estimate_qber,\n"
        "    error_correction, final_key_length,\n"
        ")\n"
        "from src.info_theory import binary_entropy\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
    ))

    cells.append(md(
        "## 2. Protocol-flow diagram\n"
        "\n"
        "Pure-matplotlib block diagram of the seven BB84 steps. Saved at "
        "300 dpi to `figures/bb84_protocol_flow.png` so the figure travels "
        "with the GitHub repo even when the notebook is not rendered."
    ))

    cells.append(code(
        "fig, ax = plt.subplots(figsize=(11, 5.5))\n"
        "ax.set_xlim(0, 11)\n"
        "ax.set_ylim(0, 5)\n"
        "ax.axis('off')\n"
        "\n"
        "stages = [\n"
        "    (1, 'Alice prepares\\n(bit, basis)', '#4C72B0'),\n"
        "    (2, 'Quantum\\nchannel', '#8FB1D8'),\n"
        "    (3, 'Bob measures\\n(random basis)', '#4C72B0'),\n"
        "    (4, 'Sifting\\n(compare BASES)', '#55A868'),\n"
        "    (5, 'QBER estimation\\n(sacrifice 10%)', '#55A868'),\n"
        "    (6, 'Error correction\\n(leak f·n·h(QBER))', '#C44E52'),\n"
        "    (7, 'Privacy amplification\\nL = N_rem · max(0, K)', '#C44E52'),\n"
        "]\n"
        "\n"
        "box_w, box_h = 1.35, 1.0\n"
        "\n"
        "for i, (num, label, color) in enumerate(stages):\n"
        "    x = 0.4 + i * 1.5\n"
