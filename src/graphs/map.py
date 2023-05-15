from __future__ import annotations
import matplotlib.pyplot as plt
import itertools

from src.algorithms import random_greedy
from src.classes import rails, lines
from src import main


def draw_infra(ax: plt.Axes, infra: rails.Rails):
    for station in infra.stations:
        ax.scatter(station.E, station.N, color='black', marker='+')
        ax.annotate(station.name, (station.E, station.N), fontsize=7)

    for s_a, link_dict in infra.connections.items():
        for s_b in link_dict:
            ax.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='black', linewidth=3)


LINE_COLOURS = ['blue', 'orange', 'green', 'purple', 'brown', 'pink', 'olive', 'cyan', 'gray']


def draw_network(ax: plt.Axes, net: lines.Network):
    for line, colour in zip(net.lines, itertools.cycle(LINE_COLOURS)):
        for s_a, s_b in itertools.pairwise(line.stations):
            ax.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color=colour)
    ax.set_title(f'Score: {net.quality():.0f}    Coverage: {net.coverage():.0%}    Overtime: {net.overtime}')
    for s_a, s_b in net.unlinked:
        ax.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='red', linestyle='dotted', linewidth=5)


if __name__ == '__main__':
    infrastructure = rails.Rails()
    infrastructure.load('data/positions_small.csv', 'data/connections_small.csv')
    network = main.run_till_optimal(infrastructure, max_lines=5)
    axes = plt.subplot()
    draw_infra(axes, infrastructure)
    draw_network(axes, network)
    plt.show()
