""" Run the default runner and show results """

from __future__ import annotations

from src.defaults import default_runner, custom_runner
from src.graphs.map import draw_network

if __name__ == '__main__':
    solution = default_runner.best(100_000)

    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
    draw_network(solution)
