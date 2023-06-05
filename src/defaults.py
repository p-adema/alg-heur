""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import rand, greedy, look_ahead, hill_climb, sim_annealing
from src.classes import rails, runner

DIST_CAP = 180
LINE_CAP = 13

default_infra = rails.Rails()
default_infra.load('data/positions.csv', 'data/connections.csv')
dropped_infra = default_infra.copy()
dropped_infra.drop_stations(names=['Utrecht Centraal'])

rr = partial(runner.Runner, infra=dropped_infra,
             dist_cap=DIST_CAP, line_cap=LINE_CAP)

std_rd = rr(rand.Random, backtracking=True, clean=True)
std_gr = rr(greedy.Greedy, backtracking=True, clean=True, optimal=False)
std_hc = rr(hill_climb.HillClimb, backtracking=True, clean=False)
std_la = rr(look_ahead.LookAhead, backtracking=False, clean=False, depth=1)
std_sa = rr(sim_annealing.SimulatedAnnealing, backtracking=True, clean=False, iter_cap=500)

default_runner = std_gr
