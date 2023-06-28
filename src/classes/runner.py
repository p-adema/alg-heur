""" Class to unify interface for running algorithms

Optional parameter list:
    start: What the algorithm should be given to start with
         = 'clean' -> An empty state
         = 'random' -> A run of the standard.Random algorithm
         = 'greedy' -> A run of the standard.Greedy algorithm
         = 'stations random' -> line_cap lines distributed randomly
         = 'stations degree' -> line_cap lines distributed on odd degree stations

    trim: Whether to trim useless overtime rails at the end (default True)
    tag: A string to add to the end of the algorithm name, to distinguish it

    Loop options, all default disabled:
    (note that enabling any results in a performance penalty)
        stop_backtracking: Whether backtracking should be prevented
        track_best: Whether the best intermediate state should be tracked
        state_hook: A callable to log the current state
"""

from __future__ import annotations

from heapq import nlargest
from random import sample
from typing import Type, Generator

from src.algorithms import standard
from src.classes.abstract import Algorithm
from src.classes.lines import Network, NetworkState
from src.classes.rails import Rails


class Runner:
    """ Class representing a run configuration for an algorithm """

    def __init__(self, alg: Type[Algorithm],
                 infra: Rails | tuple[str, str], start: str = 'clean', **opt):
        """
        Create a new run configuration
        :param alg: The Algorithm Type to construct from
        :param infra: The infrastructure or relevant files
        :param start: Whether a base solution should be generated to iterate on
        :param opt: Further options, see docstring at top of file
        """
        self.alg = alg
        if not isinstance(infra, Rails):
            loc, conn = infra
            self.infra = Rails()
            self.infra.load(loc, conn)
        else:
            self.infra = infra
        self.start = start
        self.state_hook = opt.get('state_hook', None)
        self.dist_cap = opt.get('dist_cap', 180)
        self.line_cap = opt.get('line_cap', 20)
        self.options = opt

    def run(self) -> Network:
        """ Run the algorithm once, returning the final network """
        if self.start == 'clean' or self.start.startswith('stations '):
            base = Network(self.infra, self.dist_cap)
            self._alloc_stations(base)
        elif self.start in ['greedy', 'random']:
            alg = standard.Greedy if self.start == 'greedy' else standard.Random
            base = Runner(alg, self.infra,
                          dist_cap=self.dist_cap, line_cap=self.line_cap).run()
        else:
            raise ValueError('Runner -> start invalid. See documentation at top of file')
        alg_inst = self.alg(base, **self.options)

        net = self._run_loop(alg_inst)
        if self.options.get('trim', True):
            net.trim()
        return net

    def _alloc_stations(self, net: Network) -> None:
        if self.start == 'clean':
            return
        if self.start == 'stations random':
            try:
                for root in sample(net.rails.stations, self.line_cap):
                    net.add_line(root)
                return
            except ValueError as exc:
                raise ValueError("Runner -> line_cap is "
                                 "larger than station count") from exc

        if self.start != 'stations degree':
            raise ValueError("Station allocation method must be one"
                             " of 'stations none', 'stations random'"
                             " or 'stations degree'")
        odd, even = [], []
        for station, links in net.link_count.items():
            if len(links) % 2:
                odd.append(station)
            else:
                even.append(station)
        for root in sample(odd, min(self.line_cap, len(odd))):
            net.add_line(root)
        if self.line_cap <= len(odd):
            return
        for root in sample(even, self.line_cap - len(odd)):
            net.add_line(root)

    def _run_loop(self, alg_inst: Algorithm) -> Network:
        """ Run the given instance with the runner options """
        intermediate = alg_inst.active

        visited = None
        if self.options.get('stop_backtracking', False):
            visited = set(NetworkState.from_network(alg_inst.active))
        best = None
        if self.options.get('track_best', False):
            best = NetworkState.from_network(intermediate)
        hook = None
        if self.state_hook is not None:
            hook = self.state_hook

        action = visited or best or hook

        for intermediate in alg_inst:
            if action:
                state = NetworkState.from_network(intermediate)

                if visited:
                    if state in visited:
                        break
                    visited.add(state)
                if best:
                    best = max(best, state, key=lambda s: s.score)
                if hook:
                    hook(state)

        if best:
            return Network.from_state(best)
        return intermediate

    def runs(self, bound: int | None = None) -> Generator[Network]:
        """ Yield networks, up to a limit if specified """
        if bound is None:
            while True:
                yield self.run()

        for _ in range(bound):
            yield self.run()

    def run_till_cover(self) -> Network:
        """ Repeatedly run until the solution has 100% coverage """
        for sol in self.runs():
            if sol.fully_covered():
                return sol
        raise ValueError  # Typechecker

    def run_till_optimal(self) -> Network:
        """ Repeatedly run until a fully-covering, non-overlapping solution is found """
        for sol in self.runs():
            if sol.is_optimal():
                return sol
        raise ValueError  # Typechecker

    def best(self, bound: int = 1_000) -> Network:
        """ Repeatedly run until optimal or bound and return the highest scoring network """
        return max(self.runs(bound))

    def average(self, count: int = 1_000) -> float:
        """ Repeatedly run and return the average quality solution generated """
        return sum(sol.quality() for sol in self.runs(count)) / count

    def percentile(self, nth: int = 90, bound: int = 1_000) -> float:
        """ Repeatedly run and return the average quality above the nth percentile """
        count = round(bound * (1 - nth / 100))
        top = nlargest(count, (sol.quality() for sol in self.runs(bound)))
        return sum(top) / count

    @property
    def name(self):
        """ Get the name of the assigned algorithm """
        if 'tag' in self.options:
            tag = f'-{self.options["tag"]}'
        else:
            tag = ''
        return self.alg.name + tag
