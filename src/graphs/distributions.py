import numpy as np
from functools import partial
import matplotlib.pyplot as plt

from src.algorithms import random_greedy
from src.classes import rails, lines

sample_size = 5_000
ax = plt.subplot()
bins = None
infra = rails.Rails()
infra.load('data/positions_small.csv', 'data/connections_small.csv')
for max_rails in [4, 5, 6, 7]:
    print('Calculating', max_rails, 'rails')
    rg = partial(random_greedy.rg_full_cover, infra, max_rails)
    sampler = np.vectorize(lambda _: rg().quality())

    data = sampler(np.empty(sample_size))
    data.sort()
    ax.plot(data, sample_size - np.arange(sample_size), label=f'{max_rails} rails')

ax.legend()
plt.show()
