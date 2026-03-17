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


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# Fiber Channel Model for BB84\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "Notebook 03 extends the ideal BB84 simulator to a direct-fiber "
        "channel model. We add a "
        "single new module &mdash; `src/channel.py` &mdash; that turns "
        "fiber attenuation, detector efficiency, dark counts and "
        "misalignment into a per-pulse secure-key rate, and we generate "
        "the headline figure of the project: BB84 key rate vs. fiber "
        "distance.\n"
        "\n"
        "Three effects limit performance:\n"
        "\n"
        "1. **Fiber attenuation** &mdash; $\\eta(L) = 10^{-\\alpha L / 10}$ "
        "with $\\alpha = 0.2$ dB/km at the 1550 nm telecom-C minimum.\n"
        "2. **Detector efficiency** &mdash; $\\eta_{det} \\approx 0.2$ for "
        "InGaAs APDs, up to $\\sim 0.9$ for SNSPDs.\n"
        "3. **Dark counts** &mdash; $p_{dark} \\sim 10^{-6}$ per detector "
        "per gate, summing to $2 p_{dark}$ across BB84's two detectors.\n"
        "\n"
        "**Key constraint:** unlike classical telecom, QKD cannot use EDFA "
        "amplifiers to overcome fiber loss &mdash; the no-cloning theorem "
        "(Notebook 02) forbids it. Attenuation is the fundamental distance-"
        "limit driver for direct-fiber QKD, and that is exactly why the "
        "headline figure below has a hard cutoff.\n"
        "\n"
        "**Security caveat.** The non-decoy BB84 curve below "
        "is the *idealised single-photon source model*. We also implement "
        "the simplified asymptotic decoy-state estimate (Lo, Ma & Chen, "
        "2005) so the realistic weak-coherent-pulse case can be compared "
        "directly."
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
