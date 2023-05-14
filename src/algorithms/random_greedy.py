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

        choice = ext[-1]
        if choice.new or random.random() < line_count / max_lines:
            yield choice
        else:
            net.add_line(random.choice(infra.stations))
            line_count += 1


def random_greedy(file_pos: str, file_conn: str,
                  max_lines=7) -> lines.Network:
    infra = rails.Rails()
    infra.load(file_pos, file_conn)
    net = lines.Network(infra)
    ext = extensions(infra, net, max_lines)

    while not net.fully_covered() and (choice := next(ext, None)):
        choice.commit()

    return net


def rg_quality(file_pos: str, file_conn: str, max_lines: int,
               require_connected: bool = True) -> tuple[float, lines.Network]:
    sol = random_greedy(file_pos, file_conn, max_lines)
    while require_connected and not sol.fully_covered():
        sol = random_greedy(file_pos, file_conn, max_lines)

    return sol.quality(), sol


def best(fun: Callable, *args, iterations: int = 1000) -> float:
    return max((fun(*args) for _ in range(iterations)), key=lambda t: t[0])


if __name__ == '__main__':
    from functools import partial

    q = partial(rg_quality, 'data/positions_small.csv', 'data/connections_small.csv')
