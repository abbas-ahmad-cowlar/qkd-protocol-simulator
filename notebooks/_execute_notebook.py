"""Execute a notebook in place using nbclient.

Usage:
    python notebooks/_execute_notebook.py [notebook_filename]

Falls back to ``01_bb84_protocol.ipynb`` when no argument is given.
"""

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

FALLBACK_NOTEBOOK = "01_bb84_protocol.ipynb"


