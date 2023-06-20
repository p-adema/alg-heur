""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import standard, generic, heuristics, adjusters
from src.classes import rails, runner

INFRA_FILES = [('data/positions_small.csv', 'data/connections_small.csv'),
               ('data/positions.csv', 'data/connections.csv')]
INFRA_LARGE = False

default_infra = rails.Rails()
default_infra.load(*INFRA_FILES[INFRA_LARGE])

if INFRA_LARGE:
    LINE_CAP = 12
    DIST_CAP = 180
    DROPPED_STATION = 'Utrecht Centraal'
else:
    LINE_CAP = 4
    DIST_CAP = 120
    DROPPED_STATION = 'Amsterdam Centraal'

dropped_infra = default_infra.copy()
dropped_infra.drop_stations(names=[DROPPED_STATION])

rr = partial(runner.Runner, infra=default_infra,
             dist_cap=DIST_CAP, line_cap=LINE_CAP)

std_rd = rr(standard.Random)
std_gr = rr(standard.Greedy, track_best=True)
std_pr = rr(standard.Perfectionist)
std_hc = rr(standard.HillClimb, start='greedy')
std_la = rr(standard.LookAhead, stop_backtracking=True, track_best=True, start='clean', depth=3)
std_sa = rr(standard.SimulatedAnnealing, start='greedy', iter_cap=500, tag=500)

cst_gr = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.greedy(LINE_CAP),
    adj=adjusters.soft_3,
    tag='gr-s3'
)

# Warning: absurdly slow! Like, 3 mins per result on NH
cst_la = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.full_lookahead(LINE_CAP, 3),
    adj=adjusters.argmax,
    tag='la-max'
)

cst_bb = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.branch_bound(LINE_CAP, 3),
    adj=adjusters.soft_3,
    start='stations degree',
    tag='bb-s3'
)

cst_nf = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.next_free(LINE_CAP),
    adj=adjusters.soft_3,
    tag='nf-s3'
)

custom_runner: runner.Runner = rr(
    generic.Constructive,
    stop_backtracking=True,
    start='clean',
    track_best=True,
    heur=heuristics.next_free(LINE_CAP),
    adj=adjusters.soft_3,
    tag='nf-s3'
)


default_runner: runner.Runner = cst_bb
