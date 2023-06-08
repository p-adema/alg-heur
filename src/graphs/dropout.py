""" Visualise the effects of rail / station dropout """

from __future__ import annotations

import colorsys

import matplotlib.pyplot as plt
from matplotlib import colors as mc
from matplotlib.patches import Rectangle

from src.defaults import default_infra

DPI = 200


def _show_scale():
    """ Display the hue scale for debugging purposes """
    # Adapted from documentation:
    #   https://matplotlib.org/stable/gallery/color/named_colors.html
    colors = list(hue(x / 10) for x in range(-1, 11))
    count = len(colors)
    width = 10 * 4 + 2 * 2
    bottom = 22 * count + 2 * 2
    fig, axes = plt.subplots(figsize=(width / DPI, bottom / DPI), dpi=DPI)
    fig.subplots_adjust(2 / width, 2 / bottom,
                        (width - 2) / width, (bottom - 2) / bottom)
    axes.set_xlim(0, 10 * 4)
    axes.set_ylim(22 * (count - 0.5), -22 / 2.)
    axes.yaxis.set_visible(False)
    axes.xaxis.set_visible(False)
    axes.set_axis_off()
    for i, name in enumerate(colors):
        row = i % count
        col = i // count
        bottom = row * 22
        left = 10 * col
        axes.add_patch(
            Rectangle(xy=(left, bottom - 9), width=48,
                      height=18, facecolor=name, edgecolor='0.7'))
    plt.show()


def hue(percentage: float) -> str:
    """ Turn a score into a hex colour """
    scaled = max(min(percentage - 0.3, 1), 0) * 0.5
    return mc.to_hex(colorsys.hsv_to_rgb(scaled, 1, 0.8))


def station_map(alg: str):
    """ Create a visualisation of the effects of station dropout """
    fig, axes = plt.subplots(dpi=DPI)
    for s_a, link_dict in default_infra.connections.items():
        for s_b in link_dict:
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='black',
                      linewidth=0.5, linestyle='dotted')

    with open(f'results/statistics/{alg}_drop_stations.csv',
              'r', encoding='utf-8') as file:
        file.readline()
        base = float(file.readline().split(',')[1])
        rows = (row.split(',') for row in file)
        data = ((default_infra.names[nm], float(sc)) for nm, sc in rows)
        for station, score in data:
            result = (score / base - 1) * 5 + 1 + (0.2 if score > base else -0.4)
            marker = '+' if score > base else '_'
            axes.scatter(station.E, station.N, color=hue(result), marker=marker, s=100, zorder=2)
    plt.suptitle('Effects of dropping stations')
    plt.title('+ means score improved, - means score decreased', fontsize='small')
    plt.show()


def rail_map(alg: str, action: str):
    """ Create a visualisation of the effects of rail dropout """
    _, axes = plt.subplots(dpi=DPI)
    for station in default_infra.stations:
        axes.scatter(station.E, station.N, color='black', marker='o', s=10)

    with open(f'results/statistics/{alg}_{action}_rails.csv',
              'r', encoding='utf-8') as file:
        file.readline()
        base = float(file.readline().split(',')[2])
        rows = (row.split(',') for row in file)
        data = ((default_infra.names[nm_a], default_infra.names[nm_b],
                 float(sc)) for nm_a, nm_b, sc in rows)
        for s_a, s_b, score in data:
            result = (score / base - 1) * 5 + 1 + (0.2 if score > base else -0.4)
            style = 'dashed' if score > base else 'dotted'
            axes.plot((s_a.E, s_b.E), (s_a.N, s_b.N),
                      color=hue(result), linewidth=2, linestyle=style, zorder=-1)

    plt.suptitle(f'Effects of {action}ping rails')
    plt.title('dashed means score improved, dotted means score decreased', fontsize='small')

    plt.show()


if __name__ == '__main__':
    alg = 'gr'
    station_map(alg)
    rail_map(alg, 'drop')
    rail_map(alg, 'swap')
