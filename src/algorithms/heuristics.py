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
            return 100 * (1 + mov.new) - mov.duration
        if isinstance(mov, AdditionMove):
            return len(net.lines) < line_cap
        return 0

    return _greedy


def full_lookahead(line_cap: int = 20, depth: int = 2,
                   constructive: bool = True) -> Heuristic:
    """ 'Depth'-optimal heuristic, looks ahead at possible moves """

    def _full_lookahead(net: Network, _depth: int) -> float:
        """ Performs lookahead to 'depth' """
        if _depth < 1:
            return net.quality()

        return max(net.quality(), max(
            (_full_lookahead(state_neighbour, _depth - 1)
             for state_neighbour in
             net.state_neighbours(line_cap, stationary=False, constructive=constructive)),
            default=0
        ))

    def _entry(origin: Network, mov: Move) -> float:
        """ Entrypoint for the heuristic, initialises values """
        net = origin.copy()
        mov.rebind(net).commit()
        highest = 0
        for state_neighbor in net.state_neighbours(line_cap, constructive=constructive, stationary=False):
            highest = max(_full_lookahead(state_neighbor, depth - 1), highest)

        return highest

    return _entry


def branch_bound(line_cap: int = 20, depth: int = 2,
                 constructive: bool = True) -> Heuristic:
    """ Pruning heuristic, discards branches seen as suboptimal.
        Probably 'depth'-optimal                                 """

    free_util = 0

    def _bound(net: Network, steps: int) -> float:
        """ Put an upper bound on how much the current net can be improved,
            given 'steps' remaining moves to analyse                        """
        return min(net.rails.links - net.total_links, steps) * free_util

    def _branch(net: Network, _depth: int, highest: float) -> float:
        """ Analyse all state neighbours of net, checking if they improve highest """
        if _depth > 0:
            for state_neighbor in net.state_neighbours(line_cap, constructive=constructive, stationary=False):
                score = state_neighbor.quality()
                if score + _bound(state_neighbor, _depth - 1) <= highest:
                    # Cut the branch
                    continue
                highest = max(_branch(state_neighbor, _depth - 1, score), highest)

        return highest

    def _entry(origin: Network, mov: Move) -> float:
        """ Entrypoint for the heuristic, initialises values """
        net = origin.copy()
        mov.rebind(net).commit()
        nonlocal free_util
        free_util = 10_000 / net.rails.links - net.rails.min_max[0]
        highest = net.quality()
        for state_neighbor in net.state_neighbours(line_cap, constructive=constructive):
            highest = _branch(state_neighbor, depth - 1, highest)

        return highest

    return _entry


def next_free(line_cap: int = 20) -> Heuristic:
    """ Similar priority scheme to Greedy, but looks at possible further
        extensions to rails that would overlap, prioritising moves that
        lead to free rails.                                              """

    def _free(mov: ExtensionMove) -> int:
        if mov.new:
            return 3
        if mov.line.network.free_degree[mov.destination]:
            return 2
        return 1

    def _next_free(net: Network, mov: Move) -> float:
        if isinstance(mov, ExtensionMove):
            return 100 * _free(mov) - mov.duration
        if isinstance(mov, AdditionMove):
            return len(net.lines) < line_cap
        return 0

    return _next_free


def perfectionist(line_cap: int = 20) -> Heuristic:
    """ Greedy algorithm, without overlapping lines """

    def _perfectionist(net: Network, mov: Move) -> float:
        if isinstance(mov, ExtensionMove) and mov.new:
            return 100 - mov.duration
        if isinstance(mov, AdditionMove):
            return len(net.lines) < line_cap
        return 0

    return _perfectionist
