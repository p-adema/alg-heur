""" Generate data on the effects of rail / station dropout
    Effects are measured by comparing the average quality
    of high percentile (e.g. 90th) solutions before and after """

from __future__ import annotations

import multiprocessing as mp
from functools import partial
from heapq import nlargest
from itertools import combinations, chain
from os.path import isfile
from typing import Generator, Iterable, Callable

from src.defaults import default_runner as runner, default_infra

PERCENTILE = 90
PRECISION = 1_000
THREADS = 8


def safety_check(path: str) -> bool:
    """ Run a check for if the data already has been generated """
    if isfile(path):
        print(f'Datafile already present at {path}')
        if input("     Overwrite data? (y/N)  ").lower() != 'y':
            print('     Aborted.')
            return False
        print('     Deleted...\n')
    return True


def drop_station(dropped: str | None = None) -> float:
    """ Measure the effect of dropping a station """
    measurement = dropped if dropped is not None else 'baseline'
    print('Measuring', measurement)
    count = PRECISION
    if dropped is not None:
        infra = default_infra.copy()
        infra.drop_stations(names=[dropped])
    else:
        infra = default_infra
        count *= 3
    runner.infra = infra
    return runner.percentile(PERCENTILE, count)


def chunk(iterable: Iterable, count: int) -> list[list]:
    """ Split 'it' as evenly as possible into 'count' lists """
    full = list(iterable)
    chunked = []
    size, rem = divmod(len(full), count)
    for num, idx in enumerate(range(0, len(full) // count * count, size)):
        offset = min(num, rem) + idx
        add = (1 if num < rem else 0) + size
        chunked.append(full[offset: offset + add])
    return chunked


def _worker(boilerplate: tuple[Callable, list]) -> dict:
    """ Execute a task for all arguments in the list, then
        return a mapping from arguments to return values   """
    task, arglist = boilerplate
    res = {}
    for args in arglist:
        res[args] = task(*args)
    return res


def drop_all_stations() -> None:
    """ Measure the effects of dropping stations,
        one by one for all stations                """
    path = f'results/statistics/{runner.name}_drop_stations.csv'
    if not safety_check(path):
        return

    targets = list(chain(((None,),),
                         ((name,) for name in default_infra.names.keys())))

    args = [(drop_station, ch) for ch in
            (chunk(targets, THREADS))]

    print('Testing all station drops')
    with mp.Pool(THREADS) as pool:
        ret = pool.map(_worker, args)
    res = {}
    for part in ret:
        res.update(part)

    with open(path, 'w', encoding='utf-8') as file:
        file.write("name,quality\n")
        for name in targets:
            file.write(f'{name[0]},{res[name]}\n')


def drop_or_swap_rail(action: str, name_a: str, name_b: str):
    """ Measure the effect of dropping or swapping a rail, where
        'action' is whether to drop or swap, and the rail is between
        the two stations given by name                               """
    measurement = f'{name_a:20} <-> {name_b:20}' if action != 'control' else 'base'
    print('Measuring', measurement)
    if action == 'control':
        infra = default_infra
        runner.infra = infra
        return runner.percentile(PERCENTILE, PRECISION * 3)
    if action == 'drop':
        infra = default_infra.copy()
        infra.drop_rails(pairs=[(name_a, name_b)])
        runner.infra = infra
        return runner.percentile(PERCENTILE, PRECISION)
    if action != 'swap':
        raise ValueError("Action should be 'control', 'drop' or 'swap'")

    # The code for swap is a little odd, because if we ran it the same as the
    # drop variants, the results would be heavily dependent on where the swap
    # went to. As such, we change the swap every 10 runs, which makes it...
    #       less bad.

    swap_qualities = chain.from_iterable(
        (sol.quality() for sol in runner.runs(10))
        for _ in range(PRECISION // 10)
    )

    count = round(PRECISION * (1 - PERCENTILE / 100))
    top = nlargest(count, swap_qualities)
    return sum(top) / count


def rail_names() -> Generator[tuple[str, str]]:
    """ Generate all valid rails in the form of station name pairs """
    for stn_a, stn_b in combinations(default_infra.stations, 2):
        if stn_b in default_infra.connections[stn_a]:
            yield stn_a.name, stn_b.name


def _drop_or_swap_all_rails(action: str) -> None:
    """ Measure the effects of dropping rails,
        one by one for all rails                """
    if action not in ['drop', 'swap']:
        raise ValueError("Action must be either 'drop' or 'swap'")
    path = f'results/statistics/{runner.name}_{action}_rails.csv'
    if not safety_check(path):
        return

    print(f'Testing all rail {action}s')

    targets = list(chain((('control', '', ''),),
                         ((action, n_a, n_b) for n_a, n_b
                          in rail_names())))

    args = [(drop_or_swap_rail, ch) for ch in
            (chunk(targets, THREADS))]

    with mp.Pool(THREADS) as pool:
        ret = pool.map(_worker, args)
    res = {}
    for part in ret:
        res.update(part)

    with open(path, 'w', encoding='utf-8') as file:
        file.write("name_a,name_b,quality\n")
        for target in targets:
            _, name_a, name_b = target
            file.write(f"{name_a},{name_b},{res[target]}\n")


drop_all_rails = partial(_drop_or_swap_all_rails, 'drop')
swap_all_rails = partial(_drop_or_swap_all_rails, 'swap')

if __name__ == '__main__':
    drop_all_stations()
