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
