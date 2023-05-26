""" Functions to draw maps of infrastructure and networks """

from __future__ import annotations

import itertools

import matplotlib.pyplot as plt

from src.main import default_runner as runner
from src.classes import rails, lines


def draw_infra(axes: plt.Axes, infra: rails.Rails):
    """ Draw the rail infrastructure on the given axes """
    for station in infra.stations:
        axes.scatter(station.E, station.N, color='black', marker='+')
        axes.annotate(station.name, (station.E, station.N), fontsize=7)

    for s_a, link_dict in infra.connections.items():
        for s_b in link_dict:
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='black', linewidth=3)


LINE_COLOURS = ['blue', 'orange', 'green', 'purple', 'brown', 'pink', 'olive', 'cyan', 'gray']


def draw_network(axes: plt.Axes, net: lines.Network):
    """ Draw a network on the given axes """
    for line, colour in zip(net.lines, itertools.cycle(LINE_COLOURS)):
        for s_a, s_b in itertools.pairwise(line.stations):
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color=colour)
    axes.set_title(f'Score: {net.quality():.0f}    '
                   f'Coverage: {net.coverage():.0%}'
                   f'    Over-time: {net.overtime}')
    for s_a, unlinked in net.link_count.items():
        for s_b in (station for station, links in unlinked.items() if not links):
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='red', linestyle='dotted', linewidth=5)


if __name__ == '__main__':
    plt.rcParams['figure.dpi'] = 300
    network = runner.run()
    ax = plt.subplot()
    draw_infra(ax, runner.infra)
    draw_network(ax, network)
    plt.show()
    print(network.to_output())
