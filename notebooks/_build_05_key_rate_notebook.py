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
