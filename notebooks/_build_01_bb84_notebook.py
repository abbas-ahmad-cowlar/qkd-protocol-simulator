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


