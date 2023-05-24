""" Greedy constructive TrainLineExtension generator """

from __future__ import annotations

import random
from typing import Generator

from src.classes.lines import Network
from src.classes.moves import ExtensionMove
from src.classes.rails import Rails, Station


def gen_extensions(net: Network, max_lines: int = 7,
                   optimal: bool = False) -> Generator[ExtensionMove]:
    """
    Constructively generate extensions to a network
    :param net: The network to generate for
    :param max_lines: The maximum amount of lines permitted
    :param optimal: Whether overlapping lines should be denied
    :return: Yields ExtensionMoves
    """
    infra = net.rails
    net.add_line(select_root(infra, net))

    def _sort_key(extension: ExtensionMove):
        """
        Assign a value to a TrainLineExtension, where
        new extensions are more valuable than old ones then
        short extensions are more valuable than long ones
        """
        return extension.new * infra.longest - extension.duration

    while True:
        try:
            choice = max(net.extensions(), key=_sort_key)
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
        free_links = sum(not count for count in net.link_count[station].values())
        if free_links:
            root = station

            if free_links % 1:
                break

    return root


def run(infra: Rails | tuple[str, str],
        max_line_duration: int, **kwargs) -> Network:
    """ Run the algorithm a single time """
    if not isinstance(infra, Rails):
        loc, conn = infra
        infra = Rails()
        infra.load(loc, conn)

    net = Network(infra, max_line_duration)
    gen = gen_extensions(net, **kwargs)

    while not net.fully_covered() and (choice := next(gen, None)):
        choice.commit()

    return net
