""" Cumulative graph of score distributions """

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

SMOOTH_LEVEL = 0
LARGE = False
FRAMED = True
PRESENTATION = True

# noinspection SpellCheckingInspection
TARGETS = {
    # 'gr': ('Greedy', '#f96a29'),
    # 'rd': ('Random', '#aa1629'),
    # 'pr': ('Perfectionist', '#ff5791'),
    # 'hc': ('Hill Climb', 'white'),
    # 'cn-gr-s3': ('Soft greedy', 'white'),
    # 'cn-nf-s3': ('Soft next-free', 'yellow'),
    # 'cn-bb-s3': ('Branch-bound', '#8abe5e'),
    # 'sa-100': ('Sim. Anneal. 100 iter.', 'cyan'),
    # 'sa-500': 'Sim. Anneal. 500 iter.',

    # 'cn-nf-s1': ('S1', '#40ff7e'),
    # 'cn-nf-s2': ('S2', '#47cf98'),
    'cn-nf-s3': ('S3', '#4f90ba'),
    # 'cn-nf-s4': ('S4', '#584ddf'),
    # 'cn-nf-s5': ('S5', '#824ec6'),
    # 'cn-nf-s6': ('S6', '#ac4fad'),
    'cn-nf-s7': ('S7', '#d65095'),
    'cn-nf-s8': ('S8', '#ff517c'),
}

fig, ax = plt.subplots()
print('ALGORITHMS'.rjust(20), '| AVERAGES')
for alg, desc in TARGETS.items():
    name, col = desc
    file = f'results/statistics/dist/{"nl" if LARGE else "nh"}_{alg}.npy'
    arr = np.lib.stride_tricks.sliding_window_view(
        np.load(file), 1 + 2 * SMOOTH_LEVEL).mean(axis=1)
    bins = np.arange(0 + 10 * SMOOTH_LEVEL, 10_000 - 10 * SMOOTH_LEVEL, 10)

    ax.plot(bins, arr / sum(arr), label=name, color=col)
    print(f'{name:>20} | {round((arr / sum(arr) * bins).mean() * 1_000) :,}')

ax.legend(facecolor='#222222', labelcolor='white', edgecolor='#222222')
ax.set_ylim(bottom=0)

TITLE = 'Distributions' if len(TARGETS) > 1 else 'Distribution'
TEXT_COLOR = 'white' if PRESENTATION else 'black'

if LARGE:
    if FRAMED:
        plt.xlim((4_797, 7_550))
        plt.axvline(7_549, color='green', linewidth=7)
        plt.axvline(4_780, color='red', linewidth=11)
    else:
        plt.xlim((2_500, 7_500))
    plt.title(f'{TITLE} for NL problem', color=TEXT_COLOR)
else:
    if FRAMED:
        plt.xlim((6_664, 9_220))
        plt.axvline(9_219, color='green', linewidth=7)
        plt.axvline(6_666, color='red', linewidth=7)
    else:
        plt.xlim((4_500, 9_500))
    plt.title(f'{TITLE} for NH problem', color=TEXT_COLOR)

if PRESENTATION:
    ax.get_yaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    fig.set_facecolor('#222222')
    ax.set_facecolor('#222222')

plt.show()
