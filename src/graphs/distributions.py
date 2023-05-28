""" Cumulative graph of score distributions """

import matplotlib.pyplot as plt
import numpy as np

from src.main import default_runner as runner

SAMPLE_SIZE = 1_000
ax = plt.subplot()
sampler = np.vectorize(lambda _: runner().quality())

for max_lines in [4, 5, 6, 7]:
    print('Calculating', max_lines, 'rails')
    runner.m_lines = max_lines

    data = sampler(np.empty(SAMPLE_SIZE))
    data.sort()
    ax.plot(data, SAMPLE_SIZE - np.arange(SAMPLE_SIZE), label=f'{max_lines} rails')

ax.legend()
plt.show()
