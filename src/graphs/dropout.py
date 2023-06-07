from __future__ import annotations

import colorsys

import matplotlib.pyplot as plt
from matplotlib import colors as mc
from matplotlib.patches import Rectangle

from src.defaults import default_infra

DPI = 200


def show_scale():
    # Adapted from documentation:
    #   https://matplotlib.org/stable/gallery/color/named_colors.html
    colors = list(hue(x / 10) for x in range(-1, 11))
    n = len(colors)
    width = 10 * 4 + 2 * 2
    height = 22 * n + 2 * 2
    fig, ax = plt.subplots(figsize=(width / DPI, height / DPI), dpi=DPI)
    fig.subplots_adjust(2 / width, 2 / height,
                        (width - 2) / width, (height - 2) / height)
    ax.set_xlim(0, 10 * 4)
    ax.set_ylim(22 * (n - 0.5), -22 / 2.)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_axis_off()
    for i, name in enumerate(colors):
        row = i % n
        col = i // n
        y = row * 22
        swatch_start_x = 10 * col
        ax.add_patch(
            Rectangle(xy=(swatch_start_x, y - 9), width=48,
                      height=18, facecolor=name, edgecolor='0.7'))
    plt.show()


def hue(percentage: float) -> str:
    scaled = max(min(percentage - 0.3, 1), 0) * 0.5
    return mc.to_hex(colorsys.hsv_to_rgb(scaled, 1, 0.8))


def station_graph(alg: str):
    fig, ax = plt.subplots(dpi=DPI)
    for s_a, link_dict in default_infra.connections.items():
        for s_b in link_dict:
            ax.plot((s_a.E, s_b.E), (s_a.N, s_b.N), color='black', linewidth=0.5, linestyle='dotted')

    with open(f'results/statistics/{alg}_drop_stations.csv', 'r') as file:
        file.readline()
        base = float(file.readline().split(',')[1])
        rows = (row.split(',') for row in file)
        data = ((default_infra.names[nm], float(sc)) for nm, sc in rows)
        for station, score in data:
            result = (score / base - 1) * 5 + 1 + (0.2 if score > base else -0.4)
            marker = '+' if score > base else '_'
            ax.scatter(station.E, station.N, color=hue(result), marker=marker, s=100, zorder=2)

    plt.show()


if __name__ == '__main__':
    station_graph('gr')
