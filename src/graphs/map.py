""" Functions to draw maps of infrastructure and networks """

from __future__ import annotations

import itertools

import matplotlib.pyplot as plt

from src.classes import rails, lines
from src.defaults import default_runner as runner, INFRA_LARGE

ANNOTATE_STATIONS = False
PRESENTATION = True
plt.rcParams['figure.dpi'] = 200


def ax_draw_infra(axes: plt.Axes, infra: rails.Rails, color='black'):
    """ Draw the rail infrastructure on the given axes """
    for station in infra.stations:
        axes.scatter(station.E, station.N, color=color, marker='o', s=10, zorder=1)
        if ANNOTATE_STATIONS:
            axes.annotate(station.name, (station.E, station.N), fontsize=7)

    for s_a, link_dict in infra.connections.items():
        for s_b in link_dict:
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color=color, linewidth=1, zorder=-2)


LINE_COLOURS = ['blue', 'orange', 'green', 'purple', 'brown', 'pink', 'olive', 'cyan', 'gray']


def ax_draw_network(axes: plt.Axes, net: lines.Network):
    """ Draw a network on the given axes """
    for line, colour, num in zip(net.lines, itertools.cycle(LINE_COLOURS), range(len(net.lines))):
        for s_a, s_b in itertools.pairwise(line.stations):
            if net.link_count[s_a][s_b] == 1:
                axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color=colour, zorder=-1)
            else:
                offset = (len(net.lines) // 2 - num) * 0.1
                axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color=colour, zorder=-1, linestyle=(offset, (3, 2, 1, 2)))

    axes.set_title(f'Score: {net.quality():.0f}    '
                   f'Coverage: {net.coverage():.0%}'
                   f'    Over-time: {net.overtime}',
                   color=('white' if PRESENTATION else 'black'))
    for s_a, unlinked in net.link_count.items():
        for s_b in (station for station, links in unlinked.items() if not links):
            if PRESENTATION:
                axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='#222222', linewidth=1, zorder=0)
                axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='#bf8888', linestyle='dotted', linewidth=1, zorder=0)
            else:
                axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='red',
                          linestyle='dotted', linewidth=5, zorder=0)


def draw_network(net: lines.Network):
    """ Plot a network and its infrastructure """
    fig, axes = plt.subplots()
    if PRESENTATION:
        ax_draw_infra(axes, runner.infra, color='#b9b8bf')
        fig.set_facecolor('#222222')
        plt.axis('off')
    else:
        ax_draw_infra(axes, runner.infra)
    ax_draw_network(axes, net)
    plt.show()


def show_best():
    print('Showing stored best solutions')
    size = 'nl' if INFRA_LARGE else 'nh'
    with open(f'results/solutions/{size}.csv', 'r') as file:
        sol = file.read()
    network = lines.Network.from_output(sol, runner.infra)
    draw_network(network)


def show_default():
    print('Drawing a map for', runner.name, '...')
    network = runner.run()
    draw_network(network)
    print('Result:\n')
    print(network.to_output())


def show_infra():
    print('Drawing the infrastructure')
    fig, axes = plt.subplots()
    if PRESENTATION:
        ax_draw_infra(axes, runner.infra, color='#b9b8bf')
        fig.set_facecolor('#222222')
        plt.axis('off')
    else:
        ax_draw_infra(axes, runner.infra)
    plt.show()


if __name__ == '__main__':
    show_best()
    # show_default()
    # show_infra()
