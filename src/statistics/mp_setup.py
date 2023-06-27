""" Utility functions to facilitate statistics gathering and multithreading """

from __future__ import annotations

import multiprocessing as mp
import platform
import random
import time
from os.path import isfile
from subprocess import Popen
from typing import Iterable, Callable

THREADS = 8


def safety_check(path: str) -> bool:
    """ Run a check for if the data already has been generated """
    if isfile(path):
        print(f'Datafile already present at {path}')
        if input("     Overwrite data? (y/N)  ").lower() != 'y':
            print('     Aborted.')
            return False
    return True


def chunk(iterable: Iterable, count: int) -> list[list]:
    """ Split 'iterable' as evenly as possible into 'count' lists """
    full = list(iterable)

    # If some parts of iterable are 'harder' than others,
    # we hope this reduces the clustering somewhat
    random.shuffle(full)

    chunked = []
    size, rem = divmod(len(full), count)

    # Not very pythonic, but AFAIK no python method to do this properly
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

    # If we don't wait, Python (sometimes) gets process number wrong
    time.sleep(0.2)
    number = int(mp.current_process().name.split('-')[-1])

    for step, args in enumerate(arglist):
        print(f'{step/len(arglist):.0%}'.rjust(number * 5))
        res[args] = task(*args)

    if arglist:
        print('done!'.rjust(number * 5))
    else:
        print('empty'.rjust(number * 5))

    return res


class NoSleep:
    """ Context manager for macOS anti-sleep """
    def __init__(self):
        self.proc = None

    def __enter__(self):
        print('Preventing sleep...')
        if platform.platform().split('-')[0] == 'macOS':
            self.proc = Popen('caffeinate')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proc is not None:
            self.proc.terminate()
