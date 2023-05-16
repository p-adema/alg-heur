""" Functions to run a given algorithm and generate solutions """

from __future__ import annotations

from src.algorithms import best_first
from src.classes import rails, lines

ALG = best_first.gen_extensions


def run_alg(infra: rails.Rails | tuple[str, str],
            max_line_duration: int, **kwargs) -> lines.Network:
    """ Run the algorithm defined as ALG a single time """
    if not isinstance(infra, rails.Rails):
        loc, conn = infra
        infra = rails.Rails()
        infra.load(loc, conn)

    net = lines.Network(infra, max_line_duration)
    gen = ALG(infra, net, **kwargs)

    while not net.fully_covered() and (choice := next(gen, None)):
        choice.commit()

    return net


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
    while sol.overtime or not sol.fully_covered():
        sol = run_alg(infra, **kwargs)

    return sol


def best(infra: rails.Rails | tuple[str, str], bound: int = 1_000, **kwargs) -> lines.Network:
    """ Repeatedly run ALG and return the highest scoring network """
    sol = run_alg(infra, **kwargs)
    iterations = 1
    while (sol.overtime or not sol.fully_covered()) and iterations < bound:
        sol = max(sol, run_alg(infra, **kwargs))
        iterations += 1

    return sol


if __name__ == '__main__':
    infrastructure = rails.Rails()
    infrastructure.load('data/positions.csv', 'data/connections.csv')
    solution = lines.Network(infrastructure)

    solution = max(solution, best(infrastructure, max_lines=19,
                                  max_line_duration=180, bound=1_000, temperature=0))
    print(f'Best score found: (overlap {solution.overtime}, {len(solution.lines)} lines)\n')
    print(solution.to_output())
