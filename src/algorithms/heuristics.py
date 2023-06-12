""" Heuristic functions of state and move for generic algorithms """

import random
import math

from src.classes.abstract import Move, Heuristic
from src.classes.lines import Network
from src.classes.moves import ExtensionMove, AdditionMove


def rand(line_cap: int = 20) -> Heuristic:
    """ Random heuristic """

    def _rand(net: Network, mov: Move) -> float:
        if isinstance(mov, AdditionMove) and len(net.lines) >= line_cap:
            return 0
        return random.random() + 1

    return _rand


def greedy(line_cap: int = 20) -> Heuristic:
    """ Locally (1 move) optimal heuristic """

    def _greedy(net: Network, mov: Move) -> float:
        if isinstance(mov, ExtensionMove):
            return 100 * (1 + mov.new) - mov.duration
        if isinstance(mov, AdditionMove):
            return len(net.lines) < line_cap
        return 0

    return _greedy


def full_lookahead(line_cap: int = 20, depth: int = 2,
                   constructive: bool = True) -> Heuristic:
    """ 'Depth'-optimal heuristic, looks ahead at possible moves """

    def _full_lookahead(net: Network, __: Move, _depth: int = depth) -> float:
        if not _depth:
            return net.quality()

        return max(net.quality(), max(
            (_full_lookahead(state_neighbour, __, _depth - 1)
             for state_neighbour in
             net.state_neighbours(line_cap, stationary=True, constructive=constructive))
        ))

    return _full_lookahead


def branch_bound(line_cap: int = 20, depth: int = 2) -> Heuristic:
    """ 'Depth'-optimal heuristic, prunes proven suboptimal branches """

    def _bound(net: Network, steps: int) -> float:
        max_plus = min(net.rails.links - net.total_links,
                       steps) / net.rails.links * 10_000
        min_minus = net.rails.min_max[0] * steps
        return max_plus - min_minus

    def _branch_bound(net: Network, __: Move, _depth: int = depth) -> float:
        if not _depth:
            return net.quality()

        highest = (-math.inf, None)
        for state_neighbor in net.state_neighbours(line_cap):
            ...

    return _branch_bound
