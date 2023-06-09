""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import standard
from src.classes import rails, runner

DIST_CAP = 180
LINE_CAP = 13

INFRA_FILES = [('data/positions_small.csv', 'data/connections_small.csv'),
               ('data/positions.csv', 'data/connections.csv')]
INFRA_LARGE = True

default_infra = rails.Rails()
default_infra.load(*INFRA_FILES[INFRA_LARGE])

if INFRA_LARGE:
    DROPPED_STATION = 'Utrecht Centraal'
else:
    DROPPED_STATION = 'Amsterdam Centraal'

dropped_infra = default_infra.copy()
dropped_infra.drop_stations(names=[DROPPED_STATION])

rr = partial(runner.Runner, infra=default_infra,
             dist_cap=DIST_CAP, line_cap=LINE_CAP)

std_rd = rr(standard.Random, backtracking=True, clean=True)
std_gr = rr(standard.Greedy, backtracking=True, clean=True, optimal=False)
std_hc = rr(standard.HillClimb, backtracking=True, clean=False)
std_la = rr(standard.LookAhead, backtracking=False, clean=False, depth=1)
std_sa = rr(standard.SimulatedAnnealing, backtracking=True, clean=False, iter_cap=500)

default_runner: runner.Runner = std_gr
