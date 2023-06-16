""" Cumulative graph of score distributions """

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

SMOOTH_LEVEL = 0
LARGE = True

targets = {
    # 'gr': 'Greedy',
    'rd': 'Random',
    # 'pr': 'Perfectionist',
    # 'hc': 'Hill Climb',
    'cn-gr-s3': 'Soft greedy',
    'cn-nf-s3': 'Soft next-free',
    # 'sa-100': 'Sim. Anneal. 100 iter.',
    # 'sa-500': 'Sim. Anneal. 500 iter.',
}

ax = plt.subplot()
print('ALGORITHMS'.rjust(20), '| AVERAGES')
for alg, name in targets.items():
    file = f'results/statistics/dist/{"nl" if LARGE else "nh"}_{alg}.npy'
    arr = np.lib.stride_tricks.sliding_window_view(
        np.load(file), 1 + 2 * SMOOTH_LEVEL).mean(axis=1)
    bins = np.arange(0 + 10 * SMOOTH_LEVEL, 10_000 - 10 * SMOOTH_LEVEL, 10)

    ax.plot(bins, arr / sum(arr), label=name)
    print(f'{name:>20} | {round((arr / sum(arr) * bins).mean() * 10_000) :,}')

ax.legend()
if LARGE:
    plt.xlim((3_500, 7_500))
else:
    plt.xlim((7_000, 9_500))
plt.show()
