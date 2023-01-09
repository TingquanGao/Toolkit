# Copyright (c) 2022 Tingquan Gao.
# All Rights Reserved.

import copy
import argparse
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm


def get_args():
    def str2bool(v):
        return v.lower() in ["1", "true", "t", True]

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, required=True, help="The path of csv file.")
    parser.add_argument("--graphs", type=str, required=True, nargs="+", help="The data to visualed. Format: Title:x,y")
    parser.add_argument("--specified", type=str, default=[], nargs="+", help="Specify style of import data. Format: DataName:ColorName,MarkerName")
    return parser.parse_args()


def parse_graph_dict(graph_arg_list):
    graph_dict = {}
    for graph_arg in graph_arg_list:
        graph_arg = graph_arg.strip()
        assert ":" in graph_arg, "[WARNINGS][Illegal args]"
        graph_title, x_y_args = graph_arg.split(":")

        x_y_args = x_y_args.strip()
        assert "," in x_y_args, "[WARNINGS][Illegal args]"
        x_arg, y_arg = x_y_args.split(",")
        graph_dict[graph_title] = (int(x_arg.strip()), int(y_arg.strip()))
    return graph_dict


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
    def __init__(self, labels, specifieds=[]) -> None:
        super().__init__()
        self.style_map = self.gen_style_map(labels, specifieds)

    def __getitem__(self, label):
        return self.style_map[label]

    def gen_style_map(self, labels, specifieds):
        labels = copy.deepcopy(labels)
        """
        tab:blue : #1f77b4
        tab:orange : #ff7f0e
        tab:green : #2ca02c
        tab:red : #d62728
        tab:purple : #9467bd
        tab:brown : #8c564b
        tab:pink : #e377c2
        tab:gray : #7f7f7f
        tab:olive : #bcbd22
        tab:cyan : #17becf
        """
        colors_name_list = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
        colors_rgba = list(cm.get_cmap("tab10").colors)
        color_dict = dict(zip(colors_name_list, colors_rgba))
        marker_dict = {
            'o':('o', 3),
            'v':('v', 4),
            '^':('^', 4),
            '<':('<', 4),
            '>':('>', 4),
            '1':('1', 6),
            '2':('2', 6),
            '3':('3', 6),
            '4':('4', 6),
            '8':('8', 4),
            's':('s', 4),
            'p':('p', 4),
            'P':('P', 4),
            '*':('*', 6),
            'h':('h', 4),
            'H':('H', 4),
            '+':('+', 4),
            'x':('x', 4),
            'X':('X', 4),
            'D':('D', 4),
            'd':('d', 4),
            '|':('|', 4),
            '_':('_', 4)
            }

        style_map = {}
        rm_colors = []
        rm_markers = []
        for specified in specifieds:
            specified_label, specified_style = specified.split(":")
            specified_color, specified_marker = specified_style.split(",")
            specified_color = specified_color.lower()
            assert specified_label in labels
            assert specified_color in colors_name_list
            assert specified_marker in marker_dict

            style_map[specified_label] = (color_dict[specified_color], marker_dict[specified_marker])

            labels.remove(specified_label)
            rm_colors.append(specified_color)
            rm_markers.append(specified_marker)

        for rm_marker in rm_markers:
            if specified_marker in marker_dict:
                marker_dict.pop(specified_marker)
        for rm_color in rm_colors:
            if rm_color in color_dict:
                color_dict.pop(rm_color)

        colors = list(color_dict.values())
        markers = list(marker_dict.values())
        colors_length = len(colors)
        marker_length = len(marker_dict)
        for idx, label in enumerate(labels):
            style_map[label] = (colors[idx % colors_length], markers[idx % marker_length])
        return style_map


class Visualizer(object):
    def __init__(self, df, graphs_dict, specified=[], group_key="series", save_dir="./") -> None:
        super().__init__()
        self.df = df
        self.graphs_dict = graphs_dict
        self.group_key = group_key
        self.save_dir = save_dir
        self.labels = self.re_label()
        self.style_mapper = StyleMap(self.labels, specified)

    def re_label(self):
        labels = self.df[self.group_key].tolist()
        self.df.index = labels
        return list(set(labels))

    def draw(self):
        for graph_title in self.graphs_dict:
            xlabel_idx, ylabel_idx = self.graphs_dict[graph_title]
            xlabel, ylabel = self.df.columns[xlabel_idx], self.df.columns[ylabel_idx]

            graph_data = []
            for label in self.labels:
                sub_data = self.df[self.df[self.group_key] == label]
                x_data = sub_data[xlabel].to_numpy()
                y_data = sub_data[ylabel].to_numpy()
                x_data, y_data = sort(x_data, y_data)

                graph_data.append((label, x_data, y_data))

            self.darw_plot(graph_title, xlabel, ylabel, graph_data)

    def darw_plot(self, graph_title, xlabel, ylabel, graph_data):
        plt.figure(dpi=500)
        all_x_data = []
        all_y_data = []
        for label, x_data, y_data in graph_data:
            color, marker = self.style_mapper[label]
            marker_tag, marker_size = marker
            plt.plot(x_data, y_data, label=label, color=color, marker=marker_tag, markersize=marker_size)
            all_x_data = [*all_x_data, *x_data]
            all_y_data = [*all_y_data, *y_data]
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(graph_title)

        x_ticks = get_ticks(all_x_data)
        plt.xticks(x_ticks)

        plt.grid(True, linestyle='-', alpha=0.3)

        handles, labels = plt.gca().get_legend_handles_labels()
        # sort both labels and handles by labels
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        plt.legend(handles, labels, loc="best", prop={'size': 6})

        file_name = ''.join(filter(str.isalnum, graph_title))
        plt.savefig(f"./{file_name}.png")


def main(args):
    df = pd.read_csv(args.csv)
    visualizer = Visualizer(df, parse_graph_dict(args.graphs), args.specified)
    visualizer.draw()


if __name__ == "__main__":
    args = get_args()
    main(args)
