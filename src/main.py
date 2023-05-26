""" Default Runners and infrastructure, to reduce repetition """
from functools import partial
from src.algorithms import greedy, look_ahead, hill_climb, sim_annealing
from src.classes import rails, lines, runner

infrastructure = rails.Rails()
infrastructure.load('data/positions.csv', 'data/connections.csv')
MAX_LINES = 18
rr = partial(runner.Runner, infra=infrastructure,
             max_line_duration=180, max_lines=MAX_LINES)

std_gr = rr(greedy.next_network, backtracking=True, clean=True)
std_hc = rr(hill_climb.next_network, backtracking=False, clean=False)
std_la = rr(look_ahead.next_network, backtracking=False, clean=False, depth=2)
std_sa = rr(sim_annealing.next_network, backtracking=True, clean=False, max_iter=500)

default_runner = std_sa

if __name__ == '__main__':
    solution = default_runner.run()
    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
