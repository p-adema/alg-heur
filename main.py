""" Run the default runner and show results """
from src.defaults import default_runner
from src.graphs.map import draw_network

if __name__ == '__main__':
    print(f'Running default runner ({default_runner.name}) 1000 times...')

    solution = default_runner.best(1_000)

    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
    draw_network(solution)
