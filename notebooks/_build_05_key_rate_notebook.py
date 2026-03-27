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


