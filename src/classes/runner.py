from functools import partial
from typing import Callable

from src.algorithms import greedy
from src.classes.lines import Network, NetworkState
from src.classes.rails import Rails


class Runner:
    def __init__(self, next_net: Callable, infra: Rails | tuple[str, str],
                 max_line_duration: int, backtracking: bool, clean: bool = True, **kwargs):
        self.next: Callable[[Network], Network | None] = partial(next_net, **kwargs)
        self.permit_backtracking = backtracking
        self.base: Network
        if not isinstance(infra, Rails):
            loc, conn = infra
            self.infra = Rails()
            self.infra.load(loc, conn)
        else:
            self.infra = infra
        self.clean = clean
        self.max_line_duration = max_line_duration
        self.max_lines = kwargs['max_lines']

    def run(self) -> Network:
        if self.clean:
            base = Network(self.infra, self.max_line_duration)
        else:
            base = Runner(greedy.next_network, self.infra,
                          self.max_line_duration, True, max_lines=self.max_lines).run()
        if self.permit_backtracking:
            return self._run_full(base)
        return self._run_no_backtrack(base)

    def _run_full(self, base: Network) -> Network:
        next = self.next(base)
        while next is not None:
            base, next = next, self.next(next)
        return base

    def _run_no_backtrack(self, base: Network) -> Network:
        visited = set(NetworkState.from_network(base))
        next = self.next(base)
        while next is not None:
            base, next = next, self.next(next)
            state = NetworkState.from_network(base)
            if state in visited:
                break
            visited.add(state)
        return base

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

    def average(self) -> float:
        """ Repeatedly run ALG and return the average quality solution generated """
        return sum(self.run().quality() for _ in range(bound)) / bound
