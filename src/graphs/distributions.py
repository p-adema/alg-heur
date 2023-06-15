""" Cumulative graph of score distributions """

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

SMOOTH = 0
LARGE = False

targets = {
    'gr': 'Greedy',
    'rd': 'Random',
    # 'pr': 'Perfectionist',
    'hc': 'Hill Climb',
    # 'sa-100': 'Sim. Anneal. 100 iter.',
    # 'sa-500': 'Sim. Anneal. 500 iter.',
}

ax = plt.subplot()
for alg, name in targets.items():
    file = f'results/statistics/dist/{"nl" if LARGE else "nh"}_{alg}.npy'
    arr = np.lib.stride_tricks.sliding_window_view(np.load(file), 1 + 2 * SMOOTH).mean(axis=1)

    ax.plot(np.arange(0 + 10 * SMOOTH, 10_000 - 10 * SMOOTH, 10), arr / sum(arr), label=name)

ax.legend()
if LARGE:
    plt.xlim((1_000, 7_500))
else:
    plt.xlim((7_000, 9_500))
plt.show()
