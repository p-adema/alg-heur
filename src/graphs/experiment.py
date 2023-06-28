""" Create visualisations for experiment results """

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Graphs to draw:
DRAW = [
    'raw heatmap',
    'adjusted heatmap',
    'peaked heatmap',
    'line graphs',
]

TEXT_WHITE = {'color': 'white'}
plt.rcParams['figure.dpi'] = 200


def clean_dataframe(dataframe: pd.DataFrame):
    """ Clean df in-place, while also returning it """
    dataframe.columns -= 40
    dataframe.index += 1
    return dataframe


def adjust_dataframe(dataframe: pd.DataFrame):
    """ Adjust df in-place, while also returning it """
    clean_dataframe(dataframe)
    for col in dataframe:
        dataframe[col] /= dataframe[col].max() / 100
    return dataframe


def simple_heatmap(dataframe: np.ndarray):
    """ Draw a simple heatmap for one of the dataframes """
    fig, axes = plt.subplots()
    axes.tick_params(colors='white')
    fig.set_facecolor('#222222')
    axes.set_facecolor('#222222')
    sns.heatmap(clean_dataframe(pd.DataFrame(dataframe)), ax=axes)
    plt.title('Raw data for 50th percentile', fontdict=TEXT_WHITE)
    plt.xlabel('Links added or removed', fontdict=TEXT_WHITE)
    plt.ylabel('Top N moves for softmax', fontdict=TEXT_WHITE)
    fig.axes[1].tick_params(colors='white')
    plt.show()


def draw_heatmap(dfs: list[pd.DataFrame], peaked: bool = True):
    """ Draw a heatmap for the adjusted dataframe """
    fig, axs = plt.subplots(2, 1, height_ratios=[3, 4])
    fig.set_size_inches(7, 8)
    fig.set_facecolor('#222222')
    plt.suptitle('Percentage relative to highest score', fontdict=TEXT_WHITE)
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
        axes.tick_params(colors='white')
    axs[0].set_title("50th percentile", fontdict=TEXT_WHITE)
    axs[1].set_title("90th percentile", fontdict=TEXT_WHITE)
    cbar = fig.axes[2]
    cbar.tick_params(colors='white')
    if peaked:
        cbar.set_xticks([90, 95, 100, 102])
        cbar.set_xticklabels(['90%', '95%', '100%', 'Best score'])
    else:
        cbar.set_xticks([90, 95, 100])
        cbar.set_xticklabels(['90%', '95%', '100%'])
    plt.show()


def draw_lines(dataframe: pd.DataFrame, name: str):
    """ Draw four lines from the dataframe, with the given title """
    fig, axes = plt.subplots()
    axes.spines['top'].set_visible(False)
    axes.spines['right'].set_visible(False)
    axes.spines['left'].set_color('white')
    axes.spines['bottom'].set_color('white')
    axes.set_ylim(90, 100.5)
    axes.tick_params(colors='white')
    fig.set_facecolor('#222222')
    axes.set_facecolor('#222222')
    for conn, colour in zip(range(-30, 31, 20),
                            ['#b58b4c', '#e3df2e', '#50e360', '#37fffc']):
        data = dataframe[conn]
        sns.lineplot(data, color=colour, label=conn, zorder=-1)
        best_idx = data.where(data == data.max()).idxmin()
        axes.scatter(best_idx, data.loc[best_idx] + conn / 150, c=colour)
    plt.setp(
        axes.legend(labelcolor='white', facecolor='#222222',
                    loc='lower right', title='Rails added').get_title(), color='white')
    axes.set_xlabel('Top N choices included in softmax', fontdict=TEXT_WHITE)
    axes.set_ylabel('Score, relative to highest point', fontdict=TEXT_WHITE)
    axes.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=100, decimals=0))
    plt.title(name, fontdict=TEXT_WHITE, pad=20)
    plt.show()


def visualise(draw: list[str]):
    """ Draw all visualisations listed in 'draw' """
    try:
        arr_50 = np.load('results/statistics/exp/perc_50.npy')
        arr_90 = np.load('results/statistics/exp/perc_90.npy')
    except FileNotFoundError:
        print('Warning: Experiment data not found')
        return

    if 'raw heatmap' in draw:
        simple_heatmap(arr_50)

    if 'adjusted heatmap' in draw or \
            'peaked heatmap' in draw or \
            'line graphs' in draw:

        p50 = adjust_dataframe(pd.DataFrame(arr_50))
        p90 = adjust_dataframe(pd.DataFrame(arr_90))
        if 'adjusted heatmap' in draw:
            draw_heatmap([p50, p90], False)
        if 'peaked heatmap' in draw:
            draw_heatmap([p50, p90], True)
        if 'line graphs' in draw:
            draw_lines(p50, '50th percentile performance')
            draw_lines(p90, '90th percentile performance')


if __name__ == '__main__':
    visualise(DRAW)
