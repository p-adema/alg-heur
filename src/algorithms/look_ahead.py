""" Hill climbing iterative Network generator """
from __future__ import annotations

import random
from typing import Generator
from functools import partial

from src.classes.lines import Network, NetworkState
from src.classes.moves import ExtensionMove
from src.classes.rails import Rails, Station
from src.algorithms import greedy


def next_network(base: Network, depth: int = 1, max_lines: int = 7) -> Network:
    score = partial(look_ahead, depth=depth - 1, max_lines=max_lines)
    net = max(
        (state_neighbour for state_neighbour in base.state_neighbours(max_lines)),
        key=score, default=base)
    return net


def look_ahead(base: Network, depth: int, max_lines: int = 7) -> float:
    if not depth:
        return base.quality()

    return max(base.quality(), max(
        (look_ahead(state_neighbour, depth - 1)
         for state_neighbour in base.state_neighbours(max_lines))
    ))
