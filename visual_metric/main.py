# Copyright (c) 2022 Tingquan Gao.
# All Rights Reserved.

import argparse
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm


def get_args():
    def str2bool(v):
        return v.lower() in ["1", "true", "t", True]

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="The path of csv file.")
    parser.add_argument("--charts", type=str, required=True, nargs="+", help="The data to visualed. Format: Title:x,y")
    return parser.parse_args()


def parse_chart_dict(chart_arg_list):
    chart_dict = {}
    for chart_arg in chart_arg_list:
        chart_arg = chart_arg.strip()
        assert ":" in chart_arg, "[WARNINGS][Illegal args]"
        chart_title, x_y_args = chart_arg.split(":")

        x_y_args = x_y_args.strip()
        assert "," in x_y_args, "[WARNINGS][Illegal args]"
        x_arg, y_arg = x_y_args.split(",")
        chart_dict[chart_title] = (x_arg.strip(), y_arg.strip())
    return chart_dict


def sort(x, y):
    assert len(x) == len(y)
    if len(x) < 2:
        return x, y
    xy = zip(x, y)
    sorted_xy = sorted(xy, key=lambda v: v[1])
    x, y = list(zip(*sorted_xy))
    return x, y


def make_approximate(v, candidate=[1, 2, 5, 10]):
    diffs = list(map(lambda x: abs(x - v), candidate))
    idx = diffs.index(min(diffs))
    return candidate[idx]

def get_ticks(values):
    min_v = min(values)
    max_v = max(values)

    step = (max_v - min_v) / 10

    if step < 1:
        step = int(1 / step)
        magnitude = int(step / 10) + 1
        step = 1 / (make_approximate(int(step / magnitude)) * magnitude)
    else:
        magnitude = int(step / 10) + 1
        step = make_approximate(int(step / magnitude)) * magnitude

    min_v = (min_v // step) * step
    max_v = (max_v // step + 1) * step

    return np.arange(min_v, max_v, step)


class StyleMap(object):
    def __init__(self, labels) -> None:
        super().__init__()
        self.labels = labels
        self.style_map = self.gen_style_map()

    def __getitem__(self, label):
        return self.style_map[label]

    def gen_style_map(self):
        colors = cm.get_cmap("Set1", len(self.labels)).colors
        markers = ['o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D', 'd', '|', '_']

        style_map = {label: (colors[idx], markers[idx % len(markers)]) for idx, label in enumerate(self.labels)}
        return style_map


class Visualizer(object):
    def __init__(self, df, charts_dict, group_key="series", save_dir="./") -> None:
        super().__init__()
        self.df = df
        self.charts_dict = charts_dict
        self.group_key = group_key
        self.save_dir = save_dir
        self.labels = self.re_label()
        self.style_mapper = StyleMap(self.labels)

    def re_label(self):
        labels = self.df[self.group_key].tolist()
        self.df.index = labels
        return list(set(labels))

    def draw(self):
        for chart_title in self.charts_dict:
            xlabel, ylabel = self.charts_dict[chart_title]
            assert xlabel in self.df.columns, "Error"
            assert ylabel in self.df.columns, "Error"

            chart_data = []
            for label in self.labels:
                sub_data = self.df[self.df[self.group_key] == label]
                x_data = sub_data[xlabel].to_numpy()
                y_data = sub_data[ylabel].to_numpy()
                x_data, y_data = sort(x_data, y_data)

                chart_data.append((label, x_data, y_data))

            self.darw_plot(chart_title, xlabel, ylabel, chart_data)

    def darw_plot(self, chart_title, xlabel, ylabel, chart_data):
        plt.figure(dpi=300)
        all_x_data = []
        all_y_data = []
        for label, x_data, y_data in chart_data:
            color, marker = self.style_mapper[label]
            plt.plot(x_data, y_data, label=label, color=color, marker=marker)
            all_x_data = [*all_x_data, *x_data]
            all_y_data = [*all_y_data, *y_data]
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(chart_title)

        x_ticks = get_ticks(all_x_data)
        plt.xticks(x_ticks)

        plt.grid(True, linestyle = '--', alpha=0.3)
        plt.legend(loc="best")
        plt.savefig(f"./{chart_title}.png")


def main(args):
    df = pd.read_csv(args.csv)
    visualizer = Visualizer(df, parse_chart_dict(args.charts))
    visualizer.draw()


if __name__ == "__main__":
    args = get_args()
    main(args)
