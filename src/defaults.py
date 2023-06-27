""" Default Runners and infrastructure, to reduce repetition """

from __future__ import annotations

from functools import partial

from src.algorithms import standard, generic, heuristics, adjusters
from src.classes import rails, runner

INFRA_FILES = [('data/positions_small.csv', 'data/connections_small.csv'),
               ('data/positions.csv', 'data/connections.csv')]
INFRA_LARGE = True

default_infra = rails.Rails()
default_infra.load(*INFRA_FILES[INFRA_LARGE])

if INFRA_LARGE:
    # Lowering the line cap to around the best rail count
    # improves score for algorithms that blindly add rails, making
    # the comparisons more accurate
    LINE_CAP = 12
    DIST_CAP = 180
else:
    LINE_CAP = 4
    DIST_CAP = 120

rr = partial(runner.Runner, infra=default_infra,
             dist_cap=DIST_CAP, line_cap=LINE_CAP)

std_rd = rr(standard.Random)
std_gr = rr(standard.Greedy, track_best=True)
std_pr = rr(standard.Perfectionist)
std_hc = rr(standard.HillClimb, start='greedy')
std_la = rr(standard.LookAhead, stop_backtracking=True, track_best=True, start='clean', depth=3)
std_sa = rr(standard.SimulatedAnnealing, start='greedy', iter_cap=100, tag=100)

# Warning: absurdly slow! Like, 3 mins per result on NH
cst_la = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.full_lookahead(LINE_CAP, 3),
    adj=adjusters.argmax,
    tag='la-max'
)

# Still slow but less terrible...
cst_bb = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.branch_bound(LINE_CAP, 3),
    adj=adjusters.soft_n(3),
    start='stations degree',
    tag='bb-s3'
)

# Use this.
cst_nf = rr(
    generic.Constructive,
    track_best=True,
    heur=heuristics.next_free(LINE_CAP),
    adj=adjusters.soft_n(3),
    tag='nf-s3'
)

# If you want to experiment yourself:
custom_runner: runner.Runner = rr(
    generic.Constructive,
    stop_backtracking=False,
    start='clean',
    track_best=False,
    heur=heuristics.greedy(LINE_CAP),
    adj=adjusters.soft_n(4),
    tag='gr-s4'
)


default_runner: runner.Runner = cst_nf
