"""
Builder for notebooks/03_fiber_channel.ipynb (Notebook 03: Fiber Channel Model).

Run with:
    python notebooks/_build_03_fiber_channel_notebook.py

Then execute via notebooks/_execute_notebook.py 03_fiber_channel.ipynb
to populate outputs and save the four PNG figures.
"""

from pathlib import Path

import nbformat as nbf

NB_PATH = Path(__file__).resolve().parent / "03_fiber_channel.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text)


def code(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(text)


