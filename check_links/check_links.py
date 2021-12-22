# Copyright (c) 2021 Tingquan Gao.
# All Rights Reserved.

import os
import argparse
import re
import time
import csv
from urllib import request


def get_args():
    def str2bool(v):
        return v.lower() in ("true", "t", "1", True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", type=str, default="./docs", help="The root directory of file(s) to be checked.")
    parser.add_argument("--save_path", type=str, default="check_result.csv", help="The path of result to be saved.")
    parser.add_argument("--suffix", nargs='+', type=str, default=".md", help="The suffix of file(s) to be checked.")
    parser.add_argument("--j_anchor", type=str2bool, default=True, help="Check link that jump to doc's anchor.")
    parser.add_argument("--j_file", type=str2bool, default=True, help="Check link that jump to other file.")
    parser.add_argument("--j_http", type=str2bool, default=True, help="Check http link.")

    return parser.parse_args()


class FileChecker(object):
    def __init__(self, file_path, re_exp_dict):
        self.re_exp_dict = re_exp_dict
        self.file_path = file_path
        self.line_list = self.load_file()

        # internal anchor regular expression
        self.re_exp = r"<a name=(\"|\')(.+?)(\"|\')>.*</a>"
        self.anchor_list = self.load_anchor()

    # Find internal jump anchor
    def load_anchor(self):
        anchor_list = []
        for line in self.line_list:
            targets = re.findall(self.re_exp, line)
            if len(targets) > 0:
                if targets[0][0] == targets[0][2]:
                    anchor_list.append(targets[0][1])
        return anchor_list

    def load_file(self):
        line_list = []
        try:
            with open(self.file_path) as f:
                line_list = f.readlines()
        # except Exception.FileNotFoundError
        except Exception as e:
            print(f"Process {self.file_path}: {e}.")
        return line_list

    def check_line(self, line_str):
        invalid_link_list = []
        for re_exp, test_func in re_exp_dict.items():
            re_results = re.findall(re_exp, line_str)
            for result in re_results:
                if getattr(self, test_func)(result):
                    invalid_link_list.append(result)
        return invalid_link_list

    def __call__(self):
        invalid_link_list = []
        for num, line in enumerate(self.line_list):
            links = self.check_line(line)
            for link in links:
                invalid_link_list.append([self.file_path, num+1, link])
                print(f"{self.file_path}\t{num+1}\t{link}")

        return invalid_link_list

    def check_http(self, http_str):
        try:
            with request.urlopen(http_str) as f:
                if f.status == 200:
                    return False
        except Exception as e:
            pass
        return True

    def check_inter_link(self, tag_str):
        # target_str = f"<a name=\"{tag_str}\"></a>"
        return not tag_str in self.anchor_list

    def check_exter_link(self, path_str):
        path_str = path_str.split("#")[0]
        target_path = os.path.join(os.path.dirname(self.file_path), path_str)
        if os.path.exists(target_path):
            return False
        return True


def recursive_walk(root_dir, suffix_list):
    file_list = []
    for root, dirs, files in os.walk(root_dir, followlinks=False):
        for name in files:
            for suffix in suffix_list:
                if name.endswith(suffix):
                    file_path = os.path.join(root, name)
                    file_list.append(file_path)
    return file_list


def main():
    file_list = recursive_walk(root_dir, suffix_list)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(f"{len(file_list)} file(s) has beed found.")

    total_invalid_link_list = []
    for file_path in file_list:
        file_checker = FileChecker(file_path, re_exp_dict)
        invalid_link_list = file_checker()
        total_invalid_link_list += invalid_link_list

    with open(save_path, "w+", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["FilePath", "LineNum", "Link"])
        writer.writerows(total_invalid_link_list)
    print("Done!")

if __name__ == "__main__":
    args = get_args()

    root_dir = args.root_dir
    suffix_list = args.suffix
    save_path = args.save_path

    re_exp_dict = {}

    # 文档内跳转
    if args.j_anchor:
        anchor_re_exp = {r"^(?!<!--).*\[.+\]\(#(.*?)\)": "check_inter_link"}
        re_exp_dict = {**re_exp_dict, **anchor_re_exp}

    # 文档间跳转
    if args.j_file:
        file_re_exp = {r"^(?!<!--).*\[.+\]\((?!#)(?!http)(.*?)\)": "check_exter_link"}
        re_exp_dict = {**re_exp_dict, **file_re_exp}

    # http link
    if args.j_http:
        http_re_exp = {r"^(?!<!--).*\[.+\]\((http.+?)\)": "check_http", r"^(?!<!--).*\"(http.+?)\"": "check_http"}
        re_exp_dict = {**re_exp_dict, **http_re_exp}

    main()
