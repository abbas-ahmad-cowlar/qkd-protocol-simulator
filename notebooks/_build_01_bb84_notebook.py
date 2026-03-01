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


def build_notebook() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    cells.append(md(
        "# BB84 Quantum Key Distribution Protocol\n"
        "\n"
        "Generated from the public notebook builder for reproducible analysis.\n"
        "\n"
        "The BB84 protocol (Bennett & Brassard, 1984) lets two parties — "
        "Alice and Bob — establish a shared secret key over an insecure "
        "quantum channel. This notebook runs an **ideal-channel** simulation "
        "(no eavesdropper, no fiber loss) using the seven `src/bb84.py` "
        "functions built in Notebook 01.\n"
        "\n"
        "## Protocol pipeline\n"
        "\n"
        "1. **Preparation** &mdash; Alice randomly chooses a bit and a basis, "
        "encoding it into one of $\\{|0\\rangle, |1\\rangle, |+\\rangle, "
        "|-\\rangle\\}$.\n"
        "2. **Transmission** &mdash; Single photons travel to Bob.\n"
        "3. **Measurement** &mdash; Bob picks a random basis. Same basis as "
        "Alice $\\Rightarrow$ deterministic; mismatched basis $\\Rightarrow$ "
        "uniform 50/50 (Born rule).\n"
        "4. **Sifting** &mdash; Alice and Bob publicly compare *bases* (not "
        "bit values). Mismatched rounds are dropped.\n"
        "5. **QBER estimation** &mdash; A random subset of sifted bits is "
        "disclosed to estimate the error rate. The disclosed sample is "
        "permanently removed.\n"
        "6. **Error correction** &mdash; A perfect-reconciliation stub leaks "
        "$f_{ec} \\, n \\, h(\\mathrm{QBER})$ bits to Eve.\n"
        "7. **Privacy amplification** &mdash; Universal$_2$ hashing yields a "
        "final key of length $L = N_{\\text{remaining}} \\, "
        "\\max(0, 1 - h(\\mathrm{QBER}) - f_{ec} \\, h(\\mathrm{QBER}))$.\n"
    ))

    cells.append(md(
        "## 1. Bootstrap and imports\n"
        "\n"
        "The bootstrap cell finds the project root from the notebook's CWD, "
        "appends it to `sys.path`, and creates the `figures/` directory."
    ))

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
        "print(f'Figure dir : {FIG_DIR}')\n"
    ))

    cells.append(code(
        "import numpy as np\n"
        "%matplotlib inline\n"
        "import matplotlib.pyplot as plt\n"
        "\n"
        "from src.bb84 import (\n"
        "    alice_prepare, bob_measure, sift, estimate_qber,\n"
        "    error_correction, final_key_length,\n"
        ")\n"
        "from src.info_theory import binary_entropy\n"
        "\n"
        "plt.style.use('seaborn-v0_8-whitegrid')\n"
        "plt.rcParams.update({'font.size': 12, 'figure.dpi': 150})\n"
    ))

    cells.append(md(
        "## 2. Protocol-flow diagram\n"
        "\n"
        "Pure-matplotlib block diagram of the seven BB84 steps. Saved at "
        "300 dpi to `figures/bb84_protocol_flow.png` so the figure travels "
        "with the GitHub repo even when the notebook is not rendered."
    ))

    cells.append(code(
        "fig, ax = plt.subplots(figsize=(11, 5.5))\n"
        "ax.set_xlim(0, 11)\n"
        "ax.set_ylim(0, 5)\n"
        "ax.axis('off')\n"
        "\n"
        "stages = [\n"
        "    (1, 'Alice prepares\\n(bit, basis)', '#4C72B0'),\n"
        "    (2, 'Quantum\\nchannel', '#8FB1D8'),\n"
        "    (3, 'Bob measures\\n(random basis)', '#4C72B0'),\n"
        "    (4, 'Sifting\\n(compare BASES)', '#55A868'),\n"
        "    (5, 'QBER estimation\\n(sacrifice 10%)', '#55A868'),\n"
        "    (6, 'Error correction\\n(leak f·n·h(QBER))', '#C44E52'),\n"
        "    (7, 'Privacy amplification\\nL = N_rem · max(0, K)', '#C44E52'),\n"
        "]\n"
        "\n"
        "box_w, box_h = 1.35, 1.0\n"
        "\n"
        "for i, (num, label, color) in enumerate(stages):\n"
        "    x = 0.4 + i * 1.5\n"
        "    y = 3.6 if i % 2 == 0 else 2.0\n"
        "    rect = plt.Rectangle(\n"
        "        (x, y), box_w, box_h,\n"
        "        facecolor=color, edgecolor='black', linewidth=1.2, alpha=0.85,\n"
        "    )\n"
        "    ax.add_patch(rect)\n"
        "    ax.text(\n"
        "        x + box_w / 2, y + box_h / 2,\n"
        "        f'{num}.\\n{label}',\n"
        "        ha='center', va='center', fontsize=8.5, color='white',\n"
        "        fontweight='bold',\n"
        "    )\n"
        "    if i < len(stages) - 1:\n"
        "        nx_x = 0.4 + (i + 1) * 1.5\n"
        "        ny = 3.6 if (i + 1) % 2 == 0 else 2.0\n"
        "        ax.annotate(\n"
        "            '',\n"
        "            xy=(nx_x, ny + box_h / 2),\n"
        "            xytext=(x + box_w, y + box_h / 2),\n"
        "            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),\n"
        "        )\n"
        "\n"
        "ax.text(0.4, 4.85, 'QUANTUM', fontsize=11, fontweight='bold', color='#4C72B0')\n"
        "ax.text(5.4, 4.85, 'CLASSICAL POST-PROCESSING', fontsize=11, fontweight='bold',\n"
        "        color='#55A868')\n"
        "\n"
        "ax.set_title('BB84 Protocol Flow (Notebook 01 -- ideal channel)', fontsize=14)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'bb84_protocol_flow.png', dpi=300, bbox_inches='tight')\n"
        "plt.show()\n"
    ))

    cells.append(md(
        "## 3. Run the BB84 simulation\n"
        "\n"
        "We use a fixed seed (`2026`) so the entire pipeline &mdash; from "
        "Alice's bit string through the disclosed QBER sample &mdash; is "
        "reproducible. The notebook runs the full $N = 100\\,000$ pipeline for "
        "consistency with the Notebook 01 success criterion and the "
        "integration test in `tests/test_bb84.py`."
    ))

    cells.append(code(
        "rng = np.random.default_rng(2026)\n"
        "N_TOTAL = 100_000\n"
        "F_EC = 1.16\n"
        "\n"
        "alice_bits, alice_bases = alice_prepare(N_TOTAL, rng=rng)\n"
        "bob_bases = rng.integers(0, 2, N_TOTAL)\n"
        "bob_bits = bob_measure(alice_bits, alice_bases, bob_bases, rng=rng)\n"
        "\n"
        "alice_sifted, bob_sifted = sift(alice_bits, bob_bits, alice_bases, bob_bases)\n"
        "qber, alice_key, bob_key, sample_idx = estimate_qber(\n"
        "    alice_sifted, bob_sifted, sample_fraction=0.1, rng=rng\n"
        ")\n"
        "\n"
        "corrected_key, leaked_bits = error_correction(alice_key, bob_key, qber, f_ec=F_EC)\n"
        "L_final = final_key_length(len(alice_key), qber, f_ec=F_EC)\n"
        "\n"
        "print('=' * 56)\n"
        "print('BB84 simulation (ideal channel, no Eve)')\n"
        "print('=' * 56)\n"
        "print(f'Total bits sent              : {N_TOTAL:>10,}')\n"
        "print(f'Sifted key length            : {len(alice_sifted):>10,} '\n"
        "      f'({len(alice_sifted) / N_TOTAL:.1%})')\n"
        "print(f'QBER sample size (10%)       : {len(sample_idx):>10,}')\n"
        "print(f'Estimated QBER               : {qber:>10.6f}')\n"
        "print(f'Remaining key (post-sample)  : {len(alice_key):>10,}')\n"
        "print(f'EC leakage (f_ec={F_EC})       : {leaked_bits:>10.4f} bits')\n"
        "print(f'Final secure key length      : {L_final:>10,}')\n"
        "print(f'Final key fraction / pulse   : {L_final / N_TOTAL:>10.4f}')\n"
        "print(f'Alice == Bob (post-correction): {bool(np.array_equal(corrected_key, bob_key))}')\n"
        "print('=' * 56)\n"
    ))

    cells.append(md(
        "### Sanity checks\n"
        "\n"
        "On an ideal channel the simulation must satisfy: sift rate "
        "$\\approx 50\\%$, $\\mathrm{QBER}=0$, EC leakage $=0$, and "
        "$L_{\\text{final}}=N_{\\text{remaining}}$."
    ))

    cells.append(code(
        "assert abs(len(alice_sifted) / N_TOTAL - 0.5) < 0.05\n"
        "assert qber == 0.0\n"
        "assert leaked_bits == 0.0\n"
        "assert L_final == len(alice_key)\n"
        "assert np.array_equal(corrected_key, bob_key)\n"
        "print('All sanity checks passed.')\n"
    ))

    cells.append(md(
        "## 4. Figure 1 &mdash; basis-agreement matrix\n"
        "\n"
        "The four cells of the (Alice basis, Bob basis) contingency table "
        "should be roughly equal at $N/4$. Diagonal cells are kept; "
        "off-diagonal cells are discarded during sifting."
    ))

    cells.append(code(
        "matrix = np.zeros((2, 2), dtype=int)\n"
        "for i in range(2):\n"
        "    for j in range(2):\n"
        "        matrix[i, j] = int(np.sum((alice_bases == i) & (bob_bases == j)))\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(6, 5))\n"
        "im = ax.imshow(matrix, cmap='Blues')\n"
        "for i in range(2):\n"
        "    for j in range(2):\n"
        "        label = 'Keep' if i == j else 'Discard'\n"
        "        color = 'white' if matrix[i, j] > matrix.max() * 0.5 else 'black'\n"
        "        ax.text(\n"
        "            j, i, f'{matrix[i, j]:,}\\n({label})',\n"
        "            ha='center', va='center', fontsize=12, color=color,\n"
        "            fontweight='bold',\n"
        "        )\n"
        "ax.set_xticks([0, 1])\n"
        "ax.set_xticklabels(['Bob $Z$', 'Bob $X$'])\n"
        "ax.set_yticks([0, 1])\n"
        "ax.set_yticklabels(['Alice $Z$', 'Alice $X$'])\n"
        "ax.set_title(rf'Basis-Agreement Matrix ($N = {N_TOTAL:,}$)', fontsize=14)\n"
        "fig.colorbar(im, ax=ax, label='Count')\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'bb84_basis_matrix.png', dpi=300, bbox_inches='tight')\n"
        "plt.show()\n"
    ))

    cells.append(md(
        "## 5. Figure 2 &mdash; sifted-key bit distribution\n"
        "\n"
        "Alice's sifted bits should remain uniform: roughly half zeros and "
        "half ones. Any deviation from $\\sim 50/50$ would indicate a bug in "
        "preparation or measurement."
    ))

    cells.append(code(
        "counts = [int(np.sum(alice_key == 0)), int(np.sum(alice_key == 1))]\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(6, 4))\n"
        "bars = ax.bar(\n"
        "    ['Bit 0', 'Bit 1'], counts,\n"
        "    color=['#4C72B0', '#DD8452'], edgecolor='white', linewidth=1.5,\n"
        ")\n"
        "for bar, count in zip(bars, counts):\n"
        "    ax.text(\n"
        "        bar.get_x() + bar.get_width() / 2,\n"
        "        bar.get_height() + max(counts) * 0.02,\n"
        "        f'{count:,}',\n"
        "        ha='center', va='bottom', fontsize=12,\n"
        "    )\n"
        "ax.set_ylabel('Count')\n"
        "ax.set_title('Sifted-Key Bit Distribution (Ideal Channel)', fontsize=14)\n"
        "ax.set_ylim(0, max(counts) * 1.18)\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'bb84_sifted_key_dist.png', dpi=300, bbox_inches='tight')\n"
        "plt.show()\n"
    ))

    cells.append(md(
        "## 6. Key-rate vs QBER (with $f_{ec}$ sweep)\n"
        "\n"
        "Although Notebook 01 only simulates QBER $=0$, the key-rate curve "
        "$K = 1 - h(E) - f_{ec} \\, h(E)$ is what determines the security "
        "threshold. Plotting it here makes the famous \"$\\sim 11\\%$\" vs "
        "\"$\\sim 9.8\\%$\" distinction explicit."
    ))

    cells.append(code(
        "qber_grid = np.linspace(0, 0.25, 401)\n"
        "h_grid = binary_entropy(qber_grid)\n"
        "\n"
        "fig, ax = plt.subplots(figsize=(7, 4.5))\n"
        "for f_ec, color, label in [\n"
        "    (1.00, '#4C72B0', r'$f_{ec} = 1.00$ (Shannon limit)'),\n"
        "    (1.16, '#C44E52', r'$f_{ec} = 1.16$ (realistic)'),\n"
        "    (1.50, '#888888', r'$f_{ec} = 1.50$ (poor)'),\n"
        "]:\n"
        "    rate = 1.0 - h_grid - f_ec * h_grid\n"
        "    rate_clipped = np.maximum(rate, 0.0)\n"
        "    ax.plot(qber_grid, rate_clipped, color=color, lw=2, label=label)\n"
        "    threshold_idx = np.argmax(rate < 0)\n"
        "    if threshold_idx > 0:\n"
        "        ax.axvline(qber_grid[threshold_idx], color=color, ls=':', lw=1, alpha=0.6)\n"
        "\n"
        "ax.set_xlabel('QBER')\n"
        "ax.set_ylabel(r'Key rate $K$ (bits / sifted bit)')\n"
        "ax.set_title(r'BB84 key rate $K = 1 - h(E) - f_{ec}\\, h(E)$', fontsize=14)\n"
        "ax.set_xlim(0, 0.25)\n"
        "ax.set_ylim(-0.05, 1.05)\n"
        "ax.legend(loc='upper right')\n"
        "plt.tight_layout()\n"
        "plt.savefig(FIG_DIR / 'bb84_key_rate_curve.png', dpi=300, bbox_inches='tight')\n"
        "plt.show()\n"
    ))

    cells.append(md(
        "## 7. In the lab\n"
        "\n"
        "A real BB84 implementation replaces the abstractions above with:\n"
        "\n"
        "* **Single-photon source** &mdash; attenuated laser ($\\mu \\sim 0.1$) "
        "or quantum dots; perfect single-photon sources do not yet exist.\n"
        "* **Quantum channel** &mdash; optical fiber at the 1550 nm telecom "
        "window ($\\alpha \\approx 0.2$ dB/km).\n"
        "* **Detectors** &mdash; single-photon avalanche diodes (SPADs) with "
        "10–20 % efficiency and dark-count rates around $10^{-6}$/gate.\n"
        "* **Timing** &mdash; nanosecond-level synchronization between "
        "Alice's pulse slots and Bob's detection windows.\n"
        "* **Classical channel** &mdash; *authenticated* (not secret) TCP/IP "
        "for sifting, error correction and privacy amplification.\n"
        "\n"
        "Notebook 03 will replace the ideal channel with a realistic fiber model; "
        "Notebook 02 introduces Eve."
    ))

    cells.append(md(
        "## 8. What this notebook demonstrates\n"
        "\n"
        "1. **BB84 works.** With matching bases the keys are bit-for-bit "
