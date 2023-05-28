""" Greedy constructive TrainLineExtension generator """

from __future__ import annotations

import random
from typing import Generator, Final

from src.classes.lines import Network
from src.classes.moves import ExtensionMove
from src.classes.rails import Rails, Station
from src.classes.algorithm import Algorithm


class Greedy(Algorithm):
    def __init__(self, base: Network, max_lines: int = 7,
                 optimal: bool = False):
        self.active = base
        self.infra = base.rails
        self.max_lines = max_lines
        self.optimal = optimal
        self.longest_rail = self.infra.longest

    def _sort_key(self, extension: ExtensionMove):
        """
        Assign a value to a TrainLineExtension, where
        new extensions are more valuable than old ones then
        short extensions are more valuable than long ones
        """
        return extension.new * self.longest_rail - extension.duration

    def next_move(self) -> ExtensionMove | None:
        """
        Constructively generate extensions to a network
        :return: ExtensionMoves, or None if there are none remaining
        """
        while True:
            try:
                choice = max(self.active.extensions(), key=self._sort_key)
            except ValueError:
                if len(self.active.lines) == self.max_lines:
                    return None
                self.active.add_line(self.select_root())
                continue

            if choice.new:
                return choice
            elif len(self.active.lines) < self.max_lines:
                self.active.add_line(self.select_root())

            elif not self.optimal:
                return choice
            else:
                return None

    def select_root(self) -> Station:
        """ Selects a root to start a new line from, preferring roots
            with an odd amount of links not yet in the network """
        root = None
        stations = random.sample(self.infra.stations, len(self.infra.stations))
        for station in stations:
            free_links = sum(not connected for connected in
                             self.active.link_count[station].values())
            if free_links:
                root = station

                if free_links % 1:
                    break

        return root

    def __next__(self) -> Network:
        if self.active.fully_covered():
            raise StopIteration
        ext = self.next_move()
        if ext is None:
            raise StopIteration
        ext.commit()
        return self.active


