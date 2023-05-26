""" Hill climbing iterative Network generator """
from __future__ import annotations

from src.classes.lines import Network
from random import sample, random, choice
from math import exp

SCHEDULE = 10


def next_network(base: Network, max_lines: int = 7, max_iter: int = 500) -> Network | None:
    quality = base.quality()
    iteration = getattr(base, 'sa_iter', 0)
    if iteration >= max_iter:
        return None
    temp = temperature(iteration, max_iter)
    neighbours = list(base.state_neighbours(max_lines))
    for state_neighbour in sample(neighbours, len(neighbours)):
        prob = probability(quality, state_neighbour, temp)

        if random() < prob:
            state_neighbour.sa_iter = iteration + 1
            return state_neighbour
    state_neighbour = choice(neighbours)
    state_neighbour.sa_iter = iteration + 1
    return state_neighbour


def probability(quality, state_neighbour, temp):
    return exp(min(state_neighbour.quality() - quality, 0) / temp)


def temperature(iteration: int, maximum: int) -> float:
    return SCHEDULE * (1 - iteration / maximum)
