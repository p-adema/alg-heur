""" Generic constructive algorithm for customisation """

from __future__ import annotations

import random

from src.algorithms import adjusters
from src.classes.abstract import Algorithm, Heuristic, Adjuster, Move
from src.classes.lines import Network


class Constructive(Algorithm):
    """ Generic constructive algorithm, chooses using a
        heuristic and normalisation                     """
    name = 'cn'

    def __init__(self, base: Network, heur: Heuristic,
                 adj: Adjuster = adjusters.relu, **options):
        super().__init__(base, **options)
        self.infra = base.rails
        self.line_cap = options.get('line_cap', 7)
        self.heur = heur
        self.adj = adj

    def next_move(self) -> Move | None:
        """
        Constructively add to the network
        :return: Moves, or None if there are none remaining
        """
        can_add = len(self.active.lines) < self.line_cap
        moves = list(self.active.constructions(can_add))
        if not moves:
            return None
        weights = self.adj([self.heur(self.active, mv) for mv in moves])
        if not any(weights):
            return None
        return random.choices(moves, weights=weights, k=1)[0]

    def __next__(self) -> Network:
        """ Get the next intermediate state """
        if self.active.fully_covered():
            raise StopIteration
        mov = self.next_move()
        if mov is None:
            raise StopIteration
        mov.commit()
        return self.active
