""" Generate data on the effects of rail / station dropout
    Effects are measured by comparing the average quality
    of high percentile (e.g. 90th) solutions before and after """

from __future__ import annotations

from functools import partial
from heapq import nlargest
from itertools import combinations, chain
from os.path import isfile
import multiprocessing as mp
from typing import Generator, Iterable, Callable

from src.defaults import default_runner as runner, default_infra

PERCENTILE = 90
PRECISION = 500
THREADS = 10

STATION_HEADER = "name,quality\n"
RAIL_HEADER = "name_a,name_b,quality\n"


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
    measurement = dropped if dropped is not None else 'base'
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


def chunk(it: Iterable, count: int) -> list[list]:
    """ Split 'it' as evenly as possible into 'count' lists """
    li = list(it)
    chunked = []
    size, rem = divmod(len(li), count)
    for num, idx in enumerate(range(0, len(li) // count * count, size)):
        offset = min(num, rem) + idx
        add = (1 if num < rem else 0) + size
        chunked.append(li[offset: offset + add])
    return chunked


def _worker(boilerplate: tuple[Callable, list]) -> dict:
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

    args = [(drop_station, ch) for ch in
            (chunk(((name,) for name in default_infra.names.keys()), THREADS))]

    print('Testing all station drops')
    with mp.Pool(10) as pool:
        pool: mp.Pool
        ret = pool.map(_worker, args)
    res = {}
    for d in ret:
        res.update(d)

    with open(path, 'w', encoding='utf-8') as file:
        file.write(STATION_HEADER)
        # file.write(f',{drop_station()}\n')
        for name in default_infra.names.keys():
            file.write(f'{name},{res[(name,)]}\n')


def drop_or_swap_rail(action: str, name_a: str, name_b: str):
    measurement = f'{name_a:20} <-> {name_b:20}' if action != 'control' else 'base'
    print('Measuring', measurement)
    if action == 'control':
        infra = default_infra
        runner.infra = infra
        return runner.percentile(PERCENTILE, PRECISION * 3)
    elif action == 'drop':
        infra = default_infra.copy()
        infra.drop_rails(pairs=[(name_a, name_b)])
        runner.infra = infra
        return runner.percentile(PERCENTILE, PRECISION)
    elif action != 'swap':
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
    with open(path, 'w', encoding='utf-8') as file:
        file.write(RAIL_HEADER)
        file.write(f",,{drop_or_swap_rail('control', '', '')}\n")
        for name_a, name_b in rail_names():
            file.write(f"{name_a},{name_b},"
                       f"{drop_or_swap_rail(action, name_a, name_b)}\n")


drop_all_rails = partial(_drop_or_swap_all_rails, 'drop')
swap_all_rails = partial(_drop_or_swap_all_rails, 'swap')

if __name__ == '__main__':
    drop_all_stations()
