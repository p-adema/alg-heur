from functools import partial
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np

from src.classes import rails, lines
from src.main import run_alg

SAMPLE_SIZE = 1_000
ax = plt.subplot()
infra = rails.Rails()
infra.load('data/positions_small.csv', 'data/connections_small.csv')
rg: Callable[[], lines.Network]
sampler = np.vectorize(lambda _: rg().quality())

for max_lines in [4, 5, 6, 7]:
    print('Calculating', max_lines, 'rails')
    rg = partial(run_alg, infra, max_lines=max_lines)

    data = sampler(np.empty(SAMPLE_SIZE))
    data.sort()
    ax.plot(data, SAMPLE_SIZE - np.arange(SAMPLE_SIZE), label=f'{max_lines} rails')

ax.legend()
plt.show()
