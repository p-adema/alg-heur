""" Create visualisations for experiment results """

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Graphs to draw:
DRAW = [
    # 'raw heatmap',
    # 'adjusted heatmap',
    'peaked heatmap',
]


def clean_dataframe(dataframe: pd.DataFrame):
    """ Clean df in-place, also returning it """
    dataframe.columns -= 40
    dataframe.index += 1
    return dataframe


def adjust_dataframe(dataframe: pd.DataFrame):
    """ Adjust df in-place, also returning it """
    clean_dataframe(dataframe)
    for col in dataframe:
        dataframe[col] /= dataframe[col].max() / 100
    return dataframe


def draw_heatmap(dfs: list[pd.DataFrame], peaked: bool = True):
    """ Draw a heatmap for the adjusted dataframe """
    fig, axs = plt.subplots(2, 1, height_ratios=[3, 4])
    fig.set_size_inches(7, 8)
    plt.suptitle('Percentile scores relative to highest in column (link count)')
    for axes, dataframe, do_colour_bar in zip(axs, dfs, [False, True]):
        if peaked:
            sns.heatmap(dataframe, mask=dataframe < 100, cmap='viridis', ax=axes, vmin=90,
                        vmax=100, cbar=False, square=False,
                        xticklabels=False, yticklabels=False)
            sns.heatmap(dataframe, vmin=90, mask=dataframe >= 100, ax=axes, cmap='viridis',
                        vmax=102, square=False,
                        cbar_kws={"orientation": "horizontal"}, xticklabels=10,
                        yticklabels=2, cbar=do_colour_bar)
        else:
            sns.heatmap(dataframe, vmin=90, vmax=102, cmap='viridis', ax=axes,
                        cbar_kws={"orientation": "horizontal"},
                        xticklabels=10, yticklabels=2, cbar=do_colour_bar)
    axs[0].set_title("50th percentile")
    axs[1].set_title("90th percentile")
    if peaked:
        fig.axes[2].set_xticks([90, 95, 100, 102])
        fig.axes[2].set_xticklabels(['90%', '95%', '100%', 'Best score'])
    else:
        fig.axes[2].set_xticks([90, 95, 100])
        fig.axes[2].set_xticklabels(['90%', '95%', '100%'])
    plt.show()


def visualise(draw: list[str]):
    """ Draw all visualisations listed in 'draw' """
    arr_50 = np.load('results/statistics/exp/perc_50.npy')
    arr_90 = np.load('results/statistics/exp/perc_90.npy')

    if 'raw heatmap' in draw:
        sns.heatmap(clean_dataframe(pd.DataFrame(arr_50)))
        plt.title('Raw data for 50th percentile')
        plt.xlabel('Links added or removed')
        plt.ylabel('Top N moves for softmax')
        plt.show()

    if 'adjusted heatmap' in draw or 'peaked heatmap' in draw:
        p50 = adjust_dataframe(pd.DataFrame(arr_50))
        p90 = adjust_dataframe(pd.DataFrame(arr_90))
        if 'adjusted heatmap' in draw:
            draw_heatmap([p50, p90], False)
        if 'peaked heatmap' in draw:
            draw_heatmap([p50, p90], True)


if __name__ == '__main__':
    visualise(DRAW)
