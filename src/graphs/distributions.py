""" Cumulative graph of score distributions """

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from src.defaults import default_runner as runner

SAMPLE_SIZE = 1_000
ax = plt.subplot()
sampler = np.vectorize(lambda _: runner.run().quality())

for line_cap in [4, 5, 6, 7]:
    print('Calculating', line_cap, 'rails')
    runner.line_cap = line_cap

    data = sampler(np.empty(SAMPLE_SIZE))
    data.sort()
    ax.plot(data, SAMPLE_SIZE - np.arange(SAMPLE_SIZE), label=f'{line_cap} rails')

ax.legend()
plt.show()
