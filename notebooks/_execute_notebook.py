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


def execute(nb_name: str) -> None:
    nb_path = Path(__file__).resolve().parent / nb_name
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(nb_path.parent)}},
    )
    client.execute()
    nbformat.write(nb, nb_path)
    print(f"Executed and saved {nb_path}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else FALLBACK_NOTEBOOK
    execute(name)
