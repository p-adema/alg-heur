import numpy as np
from functools import partial
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

from src.algorithms import random_greedy

sample_size = 5_000
ax = plt.subplot()
bins = None
for max_rails in [4, 5, 6, 7]:
    print('Calculating', max_rails, 'rails')
    func = partial(random_greedy.rg_quality, 'data/positions_small.csv',
                   'data/connections_small.csv', max_rails, False)
    sampler = np.vectorize(
        lambda _: func()[0])

    data = sampler(np.empty(sample_size))
    data.sort()
    ax.plot(data, sample_size - np.arange(sample_size), label=f'{max_rails} rails')

ax.legend()
plt.show()
