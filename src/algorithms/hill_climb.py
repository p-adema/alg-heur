""" Iterative greedy algorithm, takes the first score-increasing move it sees """

from __future__ import annotations

from typing import Generator

from src.classes.algorithm import Algorithm
from src.classes.lines import Network


class HillClimb(Algorithm):
    """ Hill climbing algorithm type, tries the first
        score-increasing move it finds (randomly ordered) """

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.line_cap = options.get('line_cap', 7)

    def better_neighbours(self) -> Generator[Network]:
        """ Yields neighbours that are of higher quality """
        current = self.active.quality()
        return (state for state in self.active.state_neighbours(self.line_cap)
                if state.quality() > current)

    def __next__(self) -> Network:
        for state_neighbour in self.better_neighbours():
            self.active = state_neighbour
            return state_neighbour
        raise StopIteration
