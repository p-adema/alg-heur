from __future__ import annotations

from typing import Callable

from src.algorithms import random_greedy
from src.classes import rails, lines

alg = random_greedy.gen_extensions


def run_alg(infra: rails.Rails | tuple[str, str],
            max_lines: int = 7) -> lines.Network:
    if not isinstance(infra, rails.Rails):
        loc, conn = infra
        infra = rails.Rails()
        infra.load(loc, conn)

    net = lines.Network(infra)
    ext = alg(infra, net, max_lines)

    while not net.fully_covered() and (choice := next(ext, None)):
        choice.commit()

    return net


def run_till_cover(infra: rails.Rails | tuple[str, str], max_lines: int = 7) -> lines.Network:
    sol = run_alg(infra, max_lines)
    while not sol.fully_covered():
        sol = run_alg(infra, max_lines)

    return sol


def run_till_optimal(infra: rails.Rails | tuple[str, str], max_lines: int = 7) -> lines.Network:
    sol = run_till_cover(infra, max_lines)
    while sol.overtime:
        sol = run_till_cover(infra, max_lines)

    return sol


def best(fun: Callable, *args, iterations: int = 1000):
    return max((fun(*args) for _ in range(iterations)))


if __name__ == '__main__':
    from functools import partial

    infrastructure = rails.Rails()
    infrastructure.load('data/positions_small.csv', 'data/connections_small.csv')
    q = partial(run_till_cover, infrastructure)
    solution = best(q, 7, iterations=5000)
    print(f'Best score found: (overlap {solution.overtime})\n')
    print(solution.output())
