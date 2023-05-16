""" Best-first constructive TrainLineExtension generator """

from __future__ import annotations

import random
from typing import Generator

from src.classes.lines import Network, TrainLineExtension
from src.classes.rails import Rails, Station


def gen_extensions(infra: Rails, net: Network, max_lines: int = 7,
                   optimal: bool = False) -> Generator[TrainLineExtension]:
    """
    Constructively generate extensions to a network
    :param infra: The rails the network runs on
    :param net: The network to generate for
    :param max_lines: The maximum amount of lines permitted
    :param optimal: Whether overlapping lines should be denied
    :return: Yields TrainLineExtensions
    """
    net.add_line(select_root(infra, net))
    while True:
        try:
            choice = max(net.extensions())
        except ValueError:
            if len(net.lines) == max_lines:
                return
            net.add_line(select_root(infra, net))
            continue

        if choice.new:
            yield choice
        elif len(net.lines) < max_lines:
            net.add_line(select_root(infra, net))

        elif not optimal:
            yield choice
        else:
            return


def select_root(infra: Rails, net: Network) -> Station:
    """ Selects a root to start a new line from, preferring roots
        with an odd amount of links not yet in the network """
    root = None
    for station in random.sample(infra.stations, len(infra.stations)):
        free_links = len(net.unlinked[station])
        if free_links:
            root = station

            if free_links % 1:  # or random.random() < 0.1:
                break

    return root
