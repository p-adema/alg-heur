""" Constructive algorithm that takes random actions """

from __future__ import annotations

from random import sample

from src.classes.algorithm import Algorithm
from src.classes.lines import Network


class Random(Algorithm):
    """ Constructive algorithm that repeatedly takes a random action.
        First starts all lines, then expands them                     """
    name = 'ra'

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.line_cap = options.get('line_cap', 7)
        self.add_lines()

    def add_lines(self):
        """ Add 'line_cap' lines to the active network """
        self.active: Network
        for addition in sample(list(self.active.additions()), self.line_cap):
            addition.commit()

    def __next__(self) -> Network:
        try:
            for ext in sample(list(self.active.extensions()), 1):
                ext.commit()
                return self.active
        except ValueError as exc:
            raise StopIteration from exc
