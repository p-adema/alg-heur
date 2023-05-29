""" State hooks for generating data for the ML models """
from __future__ import annotations

from itertools import zip_longest, product
from random import shuffle
from typing import TextIO

from src.classes.lines import Network, NetworkState

CSV_HEADER = 'Score,' + ','.join(','.join(f'L{line}S{station}'
                                          for station in range(1, 21))
                                 for line in range(1, 14)) + '\n'


def csv_format(lines: list[tuple[int, ...]], score: float) -> str:
    out = [str(round(score))]
    for line, _ in zip_longest(lines, range(13), fillvalue=()):
        for s_id, valid in zip_longest(line, range(1, 21), fillvalue=0):
            if not valid:
                return ''
            out.append(str(s_id))
    return ','.join(out) + '\n'


def quality_hook(net: Network, file: TextIO):
    state = NetworkState.from_network(net)
    lines = [tuple(state.infra.ids[station] for station in line)
             for line in state.lines]

    file.write(csv_format(lines, state.score))
    shuffle(lines)
    file.write(csv_format(lines, state.score))


def gen_quality_data():
    from src.classes.runner import Runner
    from src.algorithms.rand import Random
    from src.algorithms.greedy import Greedy
    with open('results/training/quality.csv', 'w') as results:
        results.write(CSV_HEADER)
        rand = Runner(Random, backtracking=True,
                      infra=('data/positions.csv', 'data/connections.csv'),
                      dist_cap=180, line_cap=13, clean=True,
                      state_hook=quality_hook, state_hook_out=results)
        for line_cap, alg in product(range(9, 14), (Random, Greedy)):
            rand.line_cap = line_cap
            rand.alg = alg
            rand.best()


if __name__ == '__main__':
    gen_quality_data()
