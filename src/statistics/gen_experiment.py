""" Functions to generate distribution data for softmax variations on modified infra """

from __future__ import annotations

import time
from collections import ChainMap
from multiprocessing import Pool

import numpy as np

import src.statistics.mp_setup as setup
from src.algorithms import generic, heuristics, adjusters
from src.classes.runner import Runner
from src.defaults import rr, INFRA_LARGE, default_infra

SAMPLE_SIZE = 10_000
MAX_N = 10
MOD_WIDTH = 40
BIN_SIZE = 1


def _get_runner(soft_level: int) -> Runner:
    if soft_level == 1:
        runner = rr(
            generic.Constructive,
            track_best=False,
            heur=heuristics.next_free(20),
            adj=adjusters.argmax,
            tag='nf-s1'
        )
    else:
        runner = rr(
            generic.Constructive,
            track_best=False,
            heur=heuristics.next_free(20),
            adj=adjusters.soft_n(soft_level),
            tag=f'nf-s{soft_level}'
        )
    runner.line_cap = 20
    return runner


def _get_infra(infra_mod: int):
    infra = default_infra.copy()
    if infra_mod > 0:
        infra.add_rails(count=infra_mod)
    elif infra_mod < 0:
        infra.drop_rails(count=abs(infra_mod))
    return infra


def _task(soft_level: int, infra_mod: int):
    """ Worker thread function """
    arr = np.zeros(10_000 // BIN_SIZE, dtype='uint32')
    runner = _get_runner(soft_level)
    for _ in range(SAMPLE_SIZE // 10):
        runner.infra = _get_infra(infra_mod)
        for net in runner.runs(10):
            score = net.quality()
            arr[int(score) // BIN_SIZE] += 1
    return arr


def experiment():
    """ Gather distribution data for softmax variations on modified infrastructure """
    if not INFRA_LARGE:
        print('Experiment must be run with NL case')
        print('     (change src.defaults.INFRA_LARGE to True)')
        return

    path50 = 'results/statistics/exp/perc_50.npy'
    path90 = 'results/statistics/exp/perc_90.npy'
    if not setup.safety_check(path50) or not setup.safety_check(path90):
        return

    estimate = 0.0003125 * SAMPLE_SIZE * MAX_N * MOD_WIDTH * setup.THREADS
    print(
        f"Running experiment, estimated completion "
        f"{time.strftime('%H:%M', time.gmtime(time.time() + 60 * 60 * 2 + estimate))}")
    start = time.time()

    with setup.NoSleep():
        ret = _run_experiment()

        print('Results gathered, analysing data...')

        perc_50, perc_90 = _analyse_results(ret)

        np.save(path50, perc_50)
        np.save(path90, perc_90)

        print('Done. Experiment took', round(time.time() - start), 'seconds')


def _analyse_results(ret):
    perc_50 = np.zeros((MAX_N, 2 * MOD_WIDTH + 1))
    perc_90 = np.zeros((MAX_N, 2 * MOD_WIDTH + 1))
    with np.nditer([perc_50, perc_90], flags=['multi_index'], op_flags=['writeonly']) as ndit:
        for p5_loc, p9_loc in ndit:
            dist: np.ndarray = ret[(ndit.multi_index[0] + 1, ndit.multi_index[1] - MOD_WIDTH)]
            tot = dist.sum()
            p5_val, p9_val = None, None
            for score, count in zip(range(0, 10_000, BIN_SIZE), dist.cumsum()):
                if p5_val is None and count >= tot * 0.5:
                    p5_val = score
                if count >= tot * 0.9:
                    p9_val = score
                    break
            p5_loc[...] = p5_val
            p9_loc[...] = p9_val
    return perc_50, perc_90


def _run_experiment():
    targets = [(soft_level, infra_mod)
               for soft_level in range(1, MAX_N + 1)
               for infra_mod in range(-MOD_WIDTH, MOD_WIDTH + 1)]
    args = [(_task, ch) for ch in
            (setup.chunk(targets, setup.THREADS))]
    with Pool(setup.THREADS) as pool:
        ret = ChainMap(*pool.map(setup.worker, args))
    return ret


if __name__ == '__main__':
    experiment()
