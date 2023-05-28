""" Hill climbing iterative Network generator """
from math import exp
from random import sample, random, choice

from src.classes.algorithm import Algorithm
from src.classes.lines import Network


class SimulatedAnnealing(Algorithm):
    schedule = 10

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.iter = 0

    @staticmethod
    def probability(quality, state_neighbour, temp):
        return exp(min(state_neighbour.quality() - quality, 0) / temp)

    def temperature(self, iteration: int, maximum: int) -> float:
        return self.schedule * (1 - iteration / maximum)

    def __next__(self) -> Network:
        quality = self.active.quality()
        max_iter = self.options['max_iter']
        if self.iter >= max_iter:
            raise StopIteration
        temp = self.temperature(self.iter, max_iter)
        self.iter += 1
        neighbours = list(self.active.state_neighbours(self.options['max_lines']))
        for state_neighbour in sample(neighbours, len(neighbours)):
            prob = self.probability(quality, state_neighbour, temp)

            if random() < prob:
                return state_neighbour
        state_neighbour = choice(neighbours)
        return state_neighbour
