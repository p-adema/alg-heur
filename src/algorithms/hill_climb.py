""" Hill climbing iterative Network generator """
from __future__ import annotations
from src.classes.lines import Network
from src.classes.algorithm import Algorithm


class HillClimb(Algorithm):
    def __next__(self) -> Network:
        quality = self.active.quality()
        for state_neighbour in self.active.state_neighbours(self.options['max_lines']):
            if state_neighbour.quality() > quality:
                self.active = state_neighbour
                return state_neighbour
        raise StopIteration
