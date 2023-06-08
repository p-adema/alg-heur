""" Class to unify interface for running algorithms

Optional parameter list:
    clean: Whether a random solution should not be generated as base
    backtracking: Whether backtracking should be permitted, default True
    state_hook: A callable to log the current state, default disabled
    state_hook_out: A TextIO handle for a file for the hook to output to
"""

from __future__ import annotations

from heapq import nlargest
from typing import Type, Callable, Generator

from src.algorithms import greedy
from src.classes.algorithm import Algorithm
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
        else:
            base = Runner(greedy.Greedy, self.infra,
                          dist_cap=self.dist_cap, line_cap=self.line_cap).run()
        alg_inst = self.alg(base, **self.options)
        if self.options.get('backtracking', True):
            return self._run_full(alg_inst)
        return self._run_no_backtrack(alg_inst)

    def _run_full(self, alg_inst: Algorithm) -> Network:
        """ Run the given instance without watching for backtracking """
        intermediate = alg_inst.active
        sh_buffer = None
        if self.state_hook is not None and 'state_hook_out' in self.options:
            sh_buffer = self.options['state_hook_out']
        for intermediate in alg_inst:
            if sh_buffer is not None:
                self.state_hook(intermediate, sh_buffer)
        return intermediate

    def _run_no_backtrack(self, alg_inst: Algorithm) -> Network:
        """ Run the given instance, returning if it backtracks """
        visited = set(NetworkState.from_network(alg_inst.active))
        intermediate = alg_inst.active
        sh_buffer = None
        if self.state_hook is not None and 'state_hook_out' in self.options:
            sh_buffer = self.options['state_hook_out']
        for intermediate in alg_inst:
            if sh_buffer is not None:
                self.state_hook(intermediate, sh_buffer)
            state = NetworkState.from_network(intermediate)
            if state in visited:
                break
            visited.add(state)
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
        return self.alg.name
