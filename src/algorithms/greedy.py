""" Greedy constructive TrainLineExtension generator """

from __future__ import annotations

import random
from typing import Generator, Final

from src.classes.lines import Network
from src.classes.moves import ExtensionMove
from src.classes.rails import Rails, Station

# A value equal to or above the duration of the longest rail connection
LONGEST_RAIL: Final = 70


def _sort_key(extension: ExtensionMove):
    """
    Assign a value to a TrainLineExtension, where
    new extensions are more valuable than old ones then
    short extensions are more valuable than long ones
    """
    return extension.new * LONGEST_RAIL - extension.duration


def next_extension(net: Network, max_lines: int = 7,
                   optimal: bool = False) -> ExtensionMove | None:
    """
    Constructively generate extensions to a network
    :param net: The network to generate for
    :param max_lines: The maximum amount of lines permitted
    :param optimal: Whether overlapping lines should be denied
    :return: Yields ExtensionMoves
    """
    infra = net.rails

    while True:
        try:
            choice = max(net.extensions(), key=_sort_key)
        except ValueError:
            if len(net.lines) == max_lines:
                return
            net.add_line(select_root(infra, net))
            continue

        if choice.new:
            return choice
        elif len(net.lines) < max_lines:
            net.add_line(select_root(infra, net))

        elif not optimal:
            return choice
        else:
            return


def select_root(infra: Rails, net: Network) -> Station:
    """ Selects a root to start a new line from, preferring roots
        with an odd amount of links not yet in the network """
    root = None
    for station in random.sample(infra.stations, len(infra.stations)):
        free_links = sum(not count for count in net.link_count[station].values())
        if free_links:
            root = station

            if free_links % 1:
                break

    return root


def next_network(net: Network, **kwargs) -> Network | None:
    if net.fully_covered():
        return None
    ext = next_extension(net, **kwargs)
    if ext is None:
        return None
    ext.commit()
    return net
