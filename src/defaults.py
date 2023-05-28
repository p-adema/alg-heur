""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import greedy, look_ahead, hill_climb, sim_annealing
from src.classes import rails, runner

DIST_CAP = 180
LINE_CAP = 11

infrastructure = rails.Rails()
infrastructure.load('data/positions.csv', 'data/connections.csv')
rr = partial(runner.Runner, infra=infrastructure,
             dist_cap=DIST_CAP, line_cap=LINE_CAP)

std_gr = rr(greedy.Greedy, backtracking=True, clean=True, optimal=False)
std_hc = rr(hill_climb.HillClimb, backtracking=True, clean=False)
std_la = rr(look_ahead.LookAhead, backtracking=False, clean=False, depth=1)
std_sa = rr(sim_annealing.SimulatedAnnealing, backtracking=True, clean=False, iter_cap=500)

default_runner = std_gr
