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
