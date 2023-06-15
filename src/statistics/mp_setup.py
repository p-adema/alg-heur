""" Utility functions to facilitate statistics gathering and multithreading """

from __future__ import annotations

from os.path import isfile
from typing import Iterable, Callable

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


def worker(boilerplate: tuple[Callable, list]) -> dict:
    """ Execute a task for all arguments in the list, then
        return a mapping from arguments to return values   """
    task, arglist = boilerplate
    res = {}
    for args in arglist:
        res[args] = task(*args)
    return res
