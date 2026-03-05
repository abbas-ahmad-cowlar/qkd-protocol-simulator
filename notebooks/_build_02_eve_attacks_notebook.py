"""
Builder script for notebooks/02_eve_attacks.ipynb.

Run once with:
    python notebooks/_build_02_eve_attacks_notebook.py

Then execute via notebooks/_execute_notebook02.py to populate outputs and
save figures.
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "02_eve_attacks.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# Eavesdropper Attacks on BB84\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 02 introduces Eve. We add a single function to `src/bb84.py` "
        "&mdash; `eve_intercept_resend` &mdash; and use it to verify two of "
        "the most quoted BB84 results:\n"
        "\n"
        "1. **Full intercept-resend produces $\\mathrm{QBER} = 25\\%$** "
        "(not 50%, despite Eve guessing the wrong basis half the time).\n"
        "2. **QBER is linear in Eve's interception probability:** "
        "$\\mathrm{QBER}(p) = 0.25\\,p$.\n"
        "\n"
        "We then push to the security threshold and chart the key rate "
        "vs. interception probability for two error-correction efficiencies. "
        "All values are simulated end-to-end &mdash; nothing is hardcoded.\n"
        "\n"
        "**Caveat:** every key-rate plot in this notebook "
        "uses the *idealized single-photon source model*. Real weak "
        "coherent sources are vulnerable to PNS attacks; that is "
        "discussed conceptually in Step 3.4 and addressed by decoy states."
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
