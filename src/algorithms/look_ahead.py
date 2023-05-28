""" Best-first iterative algorithm, can look ahead in state space """
from __future__ import annotations

from src.classes.algorithm import Algorithm
from src.classes.lines import Network


class LookAhead(Algorithm):
    """ Best first iterative algorithm, ranks moves based on
        highest score achievable with 'depth' further moves  """

    def __next__(self) -> Network:
        line_cap = self.options.get('line_cap', 7)
        net = max(
            (state_neighbour for state_neighbour in
             self.active.state_neighbours(line_cap, stationary=True)),
            key=self.look_ahead, default=self.active)
        return net

    def look_ahead(self, base: Network, depth: int | None = None) -> float:
        """ Look 'depth' moves ahead (default is the given depth cap),
            and return the highest score achievable                    """
        if depth is None:
            depth = self.options.get('depth', 1)
        if not depth:
            return base.quality()

        line_cap = self.options.get('line_cap', 7)
        return max(base.quality(), max(
            (self.look_ahead(state_neighbour, depth - 1)
             for state_neighbour in
             base.state_neighbours(line_cap, stationary=True))
        ))
