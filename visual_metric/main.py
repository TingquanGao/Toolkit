# Copyright (c) 2022 Tingquan Gao.
# All Rights Reserved.

import argparse
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.ticker import MultipleLocator

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


class StyleMap(object):
    def __init__(self, labels) -> None:
        super().__init__()
        self.labels = labels
        self.style_map = self.gen_style_map()
    
    def __getitem__(self, label):
        return self.style_map[label]

    def gen_style_map(self):
        colors = cm.get_cmap("Set1", len(self.labels)).colors
        markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D',
'd', '|', '_']

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
                chart_data.append((label, x_data, y_data))

            self.darw_plot(chart_title, xlabel, ylabel, chart_data)

    def darw_plot(self, chart_title, xlabel, ylabel, chart_data):
        plt.figure(dpi=300)
        ax = plt.subplot(111)
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

        xmajor_locator = MultipleLocator(1)
        ymajor_locator = MultipleLocator(0.05)
        ax.xaxis.set_major_locator(xmajor_locator)
        ax.yaxis.set_major_locator(ymajor_locator)
        # xminor_locator = MultipleLocator(0.5)
        # yminor_locator = MultipleLocator(0.01)
        # ax.xaxis.set_minor_locator(xminor_locator)
        # ax.yaxis.set_minor_locator(yminor_locator)

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