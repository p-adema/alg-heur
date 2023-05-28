from functools import partial
from typing import Callable, Type

from src.algorithms import greedy
from src.classes.lines import Network, NetworkState
from src.classes.rails import Rails
from src.classes.algorithm import Algorithm


class Runner:
    def __init__(self, alg: Type[Algorithm], infra: Rails | tuple[str, str], max_line_duration: int, backtracking: bool,
                 max_lines=20, clean: bool = True, **options):
        self.alg = alg
        self.permit_backtracking = backtracking
        self.base: Network | None = None
        if not isinstance(infra, Rails):
            loc, conn = infra
            self.infra = Rails()
            self.infra.load(loc, conn)
        else:
            self.infra = infra
        self.clean = clean
        self.m_line_dur = max_line_duration
        self.m_lines = max_lines
        self.options = options

    def run(self) -> Network:
        if self.clean:
            self.base = Network(self.infra, self.m_line_dur)
        else:
            self.base = Runner(greedy.Greedy, self.infra, self.m_line_dur,
                               True, max_lines=self.m_lines).run()
        alg_inst = self.alg(self.base, max_lines=self.m_lines, **self.options)
        if self.permit_backtracking:
            return self._run_full(alg_inst)
        return self._run_no_backtrack(alg_inst)

    def _run_full(self, alg_inst: Algorithm) -> Network:
        intermediate = self.base
        for intermediate in alg_inst:
            pass
        return intermediate

    def _run_no_backtrack(self, alg_inst: Algorithm) -> Network:
        visited = set(NetworkState.from_network(alg_inst.active))
        intermediate = self.base
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
