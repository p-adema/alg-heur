""" Standard algorithms, implemented slightly better than with generics """

from __future__ import annotations

from math import exp
from random import sample, random, choice, shuffle
from typing import Generator

from src.classes.abstract import Algorithm
from src.classes.lines import Network
from src.classes.moves import ExtensionMove, AdditionMove


class Random(Algorithm):
    """ Constructive algorithm that repeatedly takes a random action.
        First starts all lines, then expands them                     """
    name = 'rd'

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.line_cap = options.get('line_cap', 7)
        self.add_lines()

    def add_lines(self):
        """ Add 'line_cap' lines to the active network """
        for addition in sample(list(self.active.additions()), self.line_cap):
            addition.commit()

    def __next__(self) -> Network:
        try:
            for ext in sample(list(self.active.extensions()), 1):
                ext.commit()
                return self.active
        except ValueError as exc:
            raise StopIteration from exc


class Greedy(Algorithm):
    """ Greedy constructive algorithm type, avoids overlap """
    name = 'gr'

    def __init__(self, base: Network, **options):
        super().__init__(base, **options)
        self.infra = base.rails
        self.line_cap = options.get('line_cap', 7)
        self.longest_rail = self.infra.min_max[1]

    def _sort_key(self, extension: ExtensionMove):
        """
        Assign a value to a TrainLineExtension, where
        new extensions are more valuable than old ones then
        short extensions are more valuable than long ones
        """
        return extension.new * self.longest_rail - extension.duration

    def next_move(self) -> ExtensionMove | None:
        """
        Constructively generate an extension to a network
        :return: ExtensionMove, or None if there are none remaining
        """
        while True:
            try:
                mov = max(self.active.extensions(), key=self._sort_key)
            except ValueError:
                if len(self.active.lines) == self.line_cap:
                    return None
                add = self.select_root()
                if add is None:
                    return None
                add.commit()
                continue

            return mov

    def select_root(self) -> AdditionMove | None:
        """ Selects a root to start a new line from, preferring roots
            with an odd amount of links not yet in the network """
        stations = list(self.active.additions())
        shuffle(stations)
        root = stations[0]
        for root in stations:
            if not root.degree() % 2:
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


class Perfectionist(Greedy):
    """ A variant of the greedy algorithm, that only
        looks for perfect (zero overlap) solutions   """
    name = 'pr'

    def next_move(self) -> ExtensionMove | None:
        """
        Constructively generate an extension to a network, refusing overlap
        :return: ExtensionMove, or None if there are none remaining
        """
        while True:
            mov = super().next_move()

            if mov is not None and mov.new:
                return mov
            if len(self.active.lines) < self.line_cap:
                add = self.select_root()
                if add is not None:
                    add.commit()
                    continue

            return None


class HillClimb(Algorithm):
    """ Hill climbing algorithm type, tries the first
        score-increasing move it finds (randomly ordered) """
    name = 'hc'

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


class LookAhead(Algorithm):
    """ Best first iterative algorithm, ranks moves based on
        highest score achievable with 'depth' further moves  """
    name = 'la'

    def __next__(self) -> Network:
        line_cap = self.options.get('line_cap', 7)
        self.active = max(
            (state_neighbour for state_neighbour in
             self.active.state_neighbours(line_cap, stationary=False)),
            key=self.look_ahead, default=self.active)

        return self.active

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
             base.state_neighbours(line_cap, stationary=False)),
            default=0))


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
