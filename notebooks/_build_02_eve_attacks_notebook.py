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


