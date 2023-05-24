""" Functions to run a given algorithm and generate solutions """

from __future__ import annotations

from src.algorithms import greedy, hill_climb
from src.classes import rails, lines

run_alg = hill_climb.run


def run_till_cover(infra: rails.Rails | tuple[str, str], **kwargs) -> lines.Network:
    """ Repeatedly run ALG until the network has 100% coverage """
    sol = run_alg(infra, **kwargs)
    while not sol.fully_covered():
        sol = run_alg(infra, **kwargs)

    return sol


def run_till_optimal(infra: rails.Rails | tuple[str, str],
                     **kwargs) -> lines.Network:
    """ Repeatedly run ALG until a fully-covering, non-overlapping solution is found """
    sol = run_alg(infra, **kwargs)
    while not sol.is_optimal():
        sol = run_alg(infra, **kwargs)

    return sol


def best(infra: rails.Rails | tuple[str, str], bound: int = 1_000, **kwargs) -> lines.Network:
    """ Repeatedly run ALG until optimal or bound and return the highest scoring network """
    sol = run_alg(infra, **kwargs)
    iterations = 0
    while not sol.is_optimal() and iterations < bound:
        sol = max(sol, run_alg(infra, **kwargs))
        iterations += 1

    return sol


def average(infra: rails.Rails | tuple[str, str], bound: int = 1_000, **kwargs) -> float:
    """ Repeatedly run ALG and return the average quality solution generated """
    return sum(run_alg(infra, **kwargs).quality() for _ in range(bound)) / bound


if __name__ == '__main__':
    infrastructure = rails.Rails()
    infrastructure.load('data/positions.csv', 'data/connections.csv')

    # print(average(infrastructure, max_lines=20, max_line_duration=180, bound=5_000))
    solution = lines.Network(infrastructure)

    solution = max(solution, best(infrastructure, max_lines=17,
                                  max_line_duration=180, bound=1_000))
    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
