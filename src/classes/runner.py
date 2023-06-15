""" Class to unify interface for running algorithms

Optional parameter list:
    clean: Whether a random solution should not be generated as base
    stations: Whether, on a clean run, lines should be pre-selected
        'none' for no allocation
        'random' for random allocation
        'degree' for odd degree preference

    Loop options, all default disabled:
    (note that enabling any results in a performance penalty)
        stop_backtracking: Whether backtracking should be prevented
        track_best: Whether the best intermediate state should be tracked
        state_hook: A callable to log the current state
"""

from __future__ import annotations

from heapq import nlargest
from random import sample
from typing import Type, Callable, Generator

from src.algorithms import standard
from src.classes.abstract import Algorithm
from src.classes.lines import Network, NetworkState
from src.classes.rails import Rails


class Runner:
    """ Class representing a run configuration for an algorithm """

    def __init__(self, alg: Type[Algorithm],
                 infra: Rails | tuple[str, str], clean: bool = True,
                 state_hook: Callable | None = None, **opt):
        """
        Create a new run configuration
        :param alg: The Algorithm Type to construct from
        :param infra: The infrastructure or relevant files
        :param clean: Whether a random solution should not be generated as base
        :param opt: Further options, see docstring at top of file
        """
        self.alg = alg
        if not isinstance(infra, Rails):
            loc, conn = infra
            self.infra = Rails()
            self.infra.load(loc, conn)
        else:
            self.infra = infra
        self.clean = clean
        self.state_hook = state_hook
        self.dist_cap = opt.get('dist_cap', 180)
        self.line_cap = opt.get('line_cap', 20)
        self.options = opt

    def run(self) -> Network:
        """ Run the algorithm once, returning the final network """
        if self.clean:
            base = Network(self.infra, self.dist_cap)
            self._alloc_stations(base)
        else:
            base = Runner(standard.Greedy, self.infra,
                          dist_cap=self.dist_cap, line_cap=self.line_cap).run()
        alg_inst = self.alg(base, **self.options)
        return self._run_loop(alg_inst)

    def _alloc_stations(self, net: Network) -> None:
        mode = self.options.get('stations', 'none')
        if mode == 'none':
            return
        if mode == 'random':
            # Assumption: line_cap <= station count
            for root in sample(net.rails.stations, self.line_cap):
                net.add_line(root)
            return
        if mode != 'degree':
            raise ValueError("Station allocation method must be one"
                             " of 'none', 'random' or 'degree'")
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
        tag = f'-{self.options["tag"]}' if 'tag' in self.options else ''
        return self.alg.name + tag
