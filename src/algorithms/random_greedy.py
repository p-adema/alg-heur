from __future__ import annotations

import random
from typing import Generator, Callable

from src.classes import rails, lines


def extensions(infra: rails.Rails, net: lines.Network, max_lines: int = 7) \
        -> Generator[lines.TrainLineExtension, None, None]:
    net.add_line(random.choice(infra.stations))
    line_count = 1
    while True:
        ext = net.extensions()
        if not ext:
            if line_count == max_lines:
                return
            net.add_line(random.choice(infra.stations))
            line_count += 1
            continue

        choice = max(ext)
        if choice.new or random.random() < line_count / max_lines:
            yield choice
        else:
            net.add_line(random.choice(infra.stations))
            line_count += 1


def random_greedy(infra: rails.Rails | tuple[str, str],
                  max_lines=7) -> lines.Network:
    if not isinstance(infra, rails.Rails):
        loc, conn = infra
        infra = rails.Rails()
        infra.load(loc, conn)

    net = lines.Network(infra)
    ext = extensions(infra, net, max_lines)

    while not net.fully_covered() and (choice := next(ext, None)):
        choice.commit()

    return net


def rg_full_cover(infra: rails.Rails | tuple[str, str], max_lines: int) -> lines.Network:
    sol = random_greedy(infra, max_lines)
    while not sol.fully_covered():
        sol = random_greedy(infra, max_lines)

    return sol


def best(fun: Callable, *args, iterations: int = 1000) -> float:
    return max((fun(*args) for _ in range(iterations)))


if __name__ == '__main__':
    from functools import partial
    infrastructure = rails.Rails()
    infrastructure.load('data/positions_small.csv', 'data/connections_small.csv')
    q = partial(rg_full_cover, infrastructure)
    score, solution = best(q, 7, iterations=50)
