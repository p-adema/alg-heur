""" Run the default runner and show results """
# pylint: skip-file
from __future__ import annotations

import time

from src.defaults import default_runner, custom_runner
from src.graphs.map import draw_network

if __name__ == '__main__':
    solution = default_runner.best()
    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
    draw_network(solution)
    # start = time.time()
    # print(default_runner.percentile(90, 10_000))
    # print(time.time() - start)
    # start = time.time()
    # print(custom_runner.name, custom_runner.percentile(90, 10_000), time.time() - start)
