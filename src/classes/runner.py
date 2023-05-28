""" Class to unify interface for running algorithms """

from __future__ import annotations

from typing import Type

from src.algorithms import greedy
from src.classes.algorithm import Algorithm
from src.classes.lines import Network, NetworkState
from src.classes.rails import Rails


class Runner:
    """ Class representing a run configuration for an algorithm """

    def __init__(self, alg: Type[Algorithm], infra: Rails | tuple[str, str],
                 backtracking: bool, clean: bool = True, **options):
        """
        Create a new run configuration
        :param alg: The Algorithm Type to construct from
        :param infra: The infrastructure or relevant files
        :param backtracking: Whether algorithms should be allowed to backtrack
        :param clean: Whether a random solution should not be generated as base
        :param options: Further options, passed to the algorithm
        """
        self.alg = alg
        self.backtracking = backtracking
        if not isinstance(infra, Rails):
            loc, conn = infra
            self.infra = Rails()
            self.infra.load(loc, conn)
        else:
            self.infra = infra
        self.clean = clean
        self.dist_cap = options.get('dist_cap', 180)
        self.line_cap = options.get('line_cap', 20)
        self.options = options

    def run(self) -> Network:
        """ Run the algorithm once, returning the final network """
        if self.clean:
            base = Network(self.infra, self.dist_cap)
        else:
            base = Runner(greedy.Greedy, self.infra, True,
                          dist_cap=self.dist_cap, line_cap=self.line_cap).run()
        alg_inst = self.alg(base, **self.options)
        if self.backtracking:
            return self._run_full(alg_inst)
        return self._run_no_backtrack(alg_inst)

    @staticmethod
    def _run_full(alg_inst: Algorithm) -> Network:
        """ Run the given instance without watching for backtracking """
        intermediate = alg_inst.active
        for intermediate in alg_inst:
            pass
        return intermediate

    @staticmethod
    def _run_no_backtrack(alg_inst: Algorithm) -> Network:
        """ Run the given instance, returning if it backtracks """
        visited = set(NetworkState.from_network(alg_inst.active))
        intermediate = alg_inst.active
        for intermediate in alg_inst:
            state = NetworkState.from_network(intermediate)
            if state in visited:
                break
            visited.add(state)
        return intermediate

    def run_till_cover(self) -> Network:
        """ Repeatedly run until the solution has 100% coverage """
        sol = self.run()
        while not sol.fully_covered():
            sol = self.run()

        return sol

    def run_till_optimal(self) -> Network:
        """ Repeatedly run until a fully-covering, non-overlapping solution is found """
        sol = self.run()
        while not sol.is_optimal():
            sol = self.run()

        return sol

    def best(self, bound: int = 1_000) -> Network:
        """ Repeatedly run until optimal or bound and return the highest scoring network """
        sol = self.run()
        iterations = 0
        while not sol.is_optimal() and iterations < bound:
            sol = max(sol, self.run())
            iterations += 1

        return sol

    def average(self, bound: int = 1_000) -> float:
        """ Repeatedly run and return the average quality solution generated """
        return sum(self.run().quality() for _ in range(bound)) / bound
