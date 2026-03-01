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
