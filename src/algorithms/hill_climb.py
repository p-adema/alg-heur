""" Hill climbing iterative Network generator """
from __future__ import annotations

import random
from typing import Generator
from functools import partial

from src.classes.lines import Network, NetworkState
from src.classes.moves import ExtensionMove
from src.classes.rails import Rails, Station
from src.algorithms import greedy


def next_network(base: Network, lookahead: int = 1, max_lines: int = 7) -> Network:
    score = partial(best_score_possible, remaining_depth=lookahead - 1, max_lines=max_lines)
    net = max(
        (state_neighbour for state_neighbour in base.state_neighbours(max_lines)),
        key=score, default=base)
    return net


def best_score_possible(base: Network, remaining_depth: int, max_lines: int = 7) \
        -> float:
    if not remaining_depth:
        return base.quality()

    return max(base.quality(), max(
        (best_score_possible(state_neighbour, remaining_depth - 1)
         for state_neighbour in base.state_neighbours(max_lines))
    ))


def run(infra: Rails | tuple[str, str], max_line_duration: int,
        clean: bool = False, **kwargs) -> Network:
    visited = set()
    if clean:
        if not isinstance(infra, Rails):
            loc, conn = infra
            infra = Rails()
            infra.load(loc, conn)

        base = Network(infra, max_line_duration)
    else:
        base = greedy.run(infra, max_line_duration, max_lines=kwargs['max_lines'])
    print(base.quality())
    while True:
        base = next_network(base, **kwargs)
        state = NetworkState.from_network(base)
        if state in visited:
            break
        visited.add(state)
    print(base.quality())

    return base
