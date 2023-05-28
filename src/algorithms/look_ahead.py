""" Hill climbing iterative Network generator """
from __future__ import annotations

from functools import partial

from src.classes.lines import Network
from src.classes.algorithm import Algorithm


class LookAhead(Algorithm):
    def __next__(self) -> Network:
        max_lines = self.options['max_lines']
        net = max(
            (state_neighbour for state_neighbour in
             self.active.state_neighbours(max_lines, permit_stationary=True)),
            key=self.look_ahead, default=self.active)
        return net

    def look_ahead(self, base: Network, depth: int | None = None) -> float:
        if depth is None:
            depth = self.options['depth']
        if not depth:
            return base.quality()

        max_lines = self.options['max_lines']
        return max(base.quality(), max(
            (self.look_ahead(state_neighbour, depth - 1)
             for state_neighbour in
             base.state_neighbours(max_lines, permit_stationary=True))
        ))
