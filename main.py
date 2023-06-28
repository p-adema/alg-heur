""" Run the default runner and show results """
import time

from src.defaults import default_runner
from src.graphs.map import draw_network

COUNT = 1

if __name__ == '__main__':
    print(f'Running default runner ({default_runner.name})'
          f' {COUNT} time{"s" if COUNT > 1 else ""}...')
    start = time.time()

    solution = default_runner.best(COUNT)

    print(f'Took {time.time() - start:.1f} seconds')
    print(f'Best score found: '
          f'(overlap {solution.overtime}, {len(solution.lines)} lines)\n')

    print(solution.to_output())
    draw_network(solution)
