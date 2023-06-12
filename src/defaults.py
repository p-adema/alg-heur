""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import standard, generic, heuristics, adjusters
from src.classes import rails, runner

DIST_CAP = 180
LINE_CAP = 20

INFRA_FILES = [('data/positions_small.csv', 'data/connections_small.csv'),
               ('data/positions.csv', 'data/connections.csv')]
INFRA_LARGE = False

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

std_rd = rr(standard.Random)
std_gr = rr(standard.Greedy, optimal=False, track_best=True)
std_hc = rr(standard.HillClimb, clean=False)
std_la = rr(standard.LookAhead, stop_backtracking=True, track_best=True, clean=False, stations='degree', depth=2)
std_sa = rr(standard.SimulatedAnnealing, clean=False, iter_cap=500)

custom_runner: runner.Runner = rr(
    generic.Constructive,
    stop_backtracking=False,
    clean=True,
    track_best=True,
    stations='none',
    heur=heuristics.greedy(LINE_CAP),
    adj=adjusters.argmax
)

default_runner: runner.Runner = custom_runner
