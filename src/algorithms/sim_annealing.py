""" Iterative algorithm implementing simulated annealing,
    transitions from semi-random to hill-climbing         """

from __future__ import annotations

from math import exp
from random import sample, random, choice

from src.classes.abstract import Algorithm
from src.classes.lines import Network


class SimulatedAnnealing(Algorithm):
    """ Iterative algorithm type implementing simulated annealing,
        transitions from semi-random to hill-climbing              """
    name = 'sa'

    # Scalar constant influencing how random the algorithm should start off
    schedule = 10

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.iter = 0
        self.iter_cap = self.options.get('iter_cap', 500)
        self.line_cap = self.options.get('line_cap', 7)

    @staticmethod
    def probability(quality, state_neighbour, temp):
        """ The probability of a state neighbour being selected,
            given the current quality and temperature            """
        return exp(min(state_neighbour.quality() - quality, 0) / temp)

    def temperature(self) -> float:
        """ The current 'temperature' of the algorithm """
        return self.schedule * (1 - self.iter / self.iter_cap)

    def __next__(self) -> Network:
        quality = self.active.quality()
        if self.iter >= self.iter_cap:
            raise StopIteration
        temp = self.temperature()
        self.iter += 1
        neighbours = list(self.active.state_neighbours(self.line_cap))
        for state_neighbour in sample(neighbours, len(neighbours)):
            prob = self.probability(quality, state_neighbour, temp)

            if random() < prob:
                return state_neighbour
        state_neighbour = choice(neighbours)
        return state_neighbour
