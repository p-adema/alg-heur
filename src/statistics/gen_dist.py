""" Functions to generate distribution data for run configurations """

from __future__ import annotations

import os.path
import time
from multiprocessing import Pool

import numpy as np

import src.statistics.mp_setup as setup
from src.classes.lines import Network
from src.defaults import default_runner as runner, INFRA_LARGE, default_infra

SIZE = 1_000_000


def _dist(size: int):
    """ Worker thread function """
    arr = np.zeros(1_000, dtype='uint32')
    best = 0, None
    for net in runner.runs(size):
        score = net.quality()
        if score > best[0]:
            best = score, net
        arr[int(score // 10)] += 1
    return arr, best


def dist():
    """ Gather distribution data for the default runner """
    print(f'Recording {SIZE} runs on {setup.PROCESSES} threads for {runner.name}...')
    start = time.time()
    w_size = (int(SIZE // setup.PROCESSES),)
    args = [(_dist, (w_size,)) for _ in range(setup.PROCESSES)]
    with Pool(setup.PROCESSES) as pool:
        ret = pool.map(setup.worker, args)

    print('Took', round(time.time() - start), 'seconds')
    res: np.ndarray = sum(d[w_size][0] for d in ret)
    best: tuple[float, Network] = max((d[w_size][1] for d in ret), key=lambda t: t[0])

    dist_file = f'results/statistics/dist/{"nl" if INFRA_LARGE else "nh"}_{runner.name}.npy'
    if not os.path.isfile(dist_file):
        os.makedirs(os.path.dirname(dist_file), exist_ok=True)
        np.save(dist_file, res)
    else:
        last = np.load(dist_file)
        np.save(dist_file, res + last)

    record_file = f'results/solutions/{"nl" if INFRA_LARGE else "nh"}.csv'
    if not os.path.isfile(record_file):
        os.makedirs(os.path.dirname(record_file), exist_ok=True)
        with open(record_file, 'w', encoding='utf-8') as file:
            file.write(best[1].to_output())
    else:
        with open(record_file, 'r', encoding='utf-8') as file:
            last = Network.from_output(file.read(), default_infra)
        if best[0] > last.quality():
            print('Best solution improved to', best[0])
            with open(record_file, 'w', encoding='utf-8') as file:
                file.write(best[1].to_output())
        else:
            print(f'Best solution ({best[0]}) under record ({last.quality()})')
    print('Saved to', dist_file)


if __name__ == '__main__':
    dist()
