from __future__ import annotations

from typing import Callable

from src.algorithms import random_greedy
from src.classes import rails, lines

alg = random_greedy.gen_extensions


def run_alg(infra: rails.Rails | tuple[str, str], **kwargs) -> lines.Network:
    if not isinstance(infra, rails.Rails):
        loc, conn = infra
        infra = rails.Rails()
        infra.load(loc, conn)

    net = lines.Network(infra)
    ext = alg(infra, net, **kwargs)

    while not net.fully_covered() and (choice := next(ext, None)):
        choice.commit()

    return net


def run_till_cover(infra: rails.Rails | tuple[str, str], max_lines: int = 7) -> lines.Network:
    sol = run_alg(infra, max_lines=max_lines)
    while not sol.fully_covered():
        sol = run_alg(infra, max_lines=max_lines)

    return sol


def run_till_optimal(infra: rails.Rails | tuple[str, str], max_lines: int = 7) -> lines.Network:
    sol = run_alg(infra, max_lines=max_lines, optimal=True)
    while sol.overtime or not sol.fully_covered():
        sol = run_alg(infra, max_lines=max_lines, optimal=True)

    return sol


def best(infra: rails.Rails | tuple[str, str], max_lines: int = 7,
         bound: int = 1000) -> lines.Network:
    sol = run_alg(infra, max_lines=max_lines)
    iterations = 1
    while (sol.overtime or not sol.fully_covered()) and iterations < bound:
        sol = max(sol, run_alg(infra, max_lines=max_lines))
        iterations += 1

    return sol


if __name__ == '__main__':
    infrastructure = rails.Rails()
    infrastructure.load('data/positions_small.csv', 'data/connections_small.csv')
    solution = best(infrastructure, 4, bound=50_000)
    print(f'Best score found: (overlap {solution.overtime})\n')
    print(solution.output())
