""" Run the default runner and show results """
# pylint: skip-file
from __future__ import annotations

import time

from src.defaults import default_runner, custom_runner, mod_inf
from src.graphs.map import draw_network

if __name__ == '__main__':
    default_runner.infra = mod_inf
    solution = default_runner.best(50)
    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
    draw_network(solution)
    # for net in default_runner.runs(10_000):
    #     if net.quality() > 7200:
    #         draw_network(net)
