""" Heuristic functions of state and move for generic algorithms """

import random

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
            return 100 * (1 + ExtensionMove.new) - ExtensionMove.duration
        if isinstance(mov, AdditionMove):
            return len(net.lines) < line_cap
        return 0

    return _greedy


def lookahead(line_cap: int = 20, depth: int = 2) -> Heuristic:
    """ 'Depth'-optimal heuristic, looks ahead at possible moves """
    def _lookahead(net: Network, __: Move, _depth: int = depth) -> float:
        if not _depth:
            return net.quality()

        return max(net.quality(), max(
            (_lookahead(state_neighbour, __, _depth - 1)
             for state_neighbour in
             net.state_neighbours(line_cap, stationary=True))
        ))

    return _lookahead
