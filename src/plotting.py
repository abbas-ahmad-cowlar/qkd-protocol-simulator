"""
Plotting Utility Module
========================

Shared plotting style, figure saving, cutoff annotations,
and log-scale handling for QKD key-rate distance sweeps.

"""

import numpy as np


def semilogy_positive(ax, x, y, *args, **kwargs):
    """Plot only positive y values on a semilogy axis.

    Log-scale key-rate figures must not include K=0 points. This helper
    centralizes the positive-rate mask used in Phases 4-6.
    """
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)
    mask = y_arr > 0.0
    return ax.semilogy(x_arr[mask], y_arr[mask], *args, **kwargs)
