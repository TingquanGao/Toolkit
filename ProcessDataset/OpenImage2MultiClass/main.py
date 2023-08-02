import os

import numpy as np


def LabelName2IdDict():
    if label_file_path == "annos/validation-annotations-bbox.csv":
        label_name_idx = 0
    elif label_file_path == "annos/oidv6-train-annotations-bbox.csv-tmp.csv":
        label_name_idx = 1
    else:
        raise Exception()

    with open(label_description_file_path) as f:
        lines = f.readlines()
    label_name2id = {}
    for idx, line in enumerate(lines):
        label_name = line.strip().split(',')[label_name_idx]
        label_name2id[label_name.lower()] = idx
    return label_name2id


def TrainImageName2PathDict():
    with open(image_path_file_path) as f:
        lines = f.readlines()
    image_name2path = {}
    for l in lines:
        path = l.strip().split(' ')[0]
        name = path.split('/')[-1]
        image_name2path[name] = path
    return image_name2path


def format_label_list(image_class_dict, class_num):
    label_list = []
    for img_path in image_class_dict:
        label = image_class_dict[img_path]
        onehot = np.zeros(class_num, dtype=int)
        onehot[label] = 1
        onehot_str = ",".join(str(v) for v in list(onehot))
        label_list.append(f"{img_path}\t{onehot_str}")
    return label_list


class LabelLinePaser:
    def __init__(self, label_name2id_dict):
        if label_file_path == "annos/oidv6-train-annotations-bbox.csv":
            self._func = self._train
        elif label_file_path == "annos/oidv6-train-annotations-bbox.csv-tmp.csv":
            self._func = self._train_tmp
            self.image_name2path_dict = TrainImageName2PathDict()
            self.label_name2id_dict = label_name2id_dict
        elif label_file_path == "annos/validation-annotations-bbox.csv":
            self._func = self._val
            self.label_name2id_dict = label_name2id_dict
        else:
            raise Exception()
        
    def __call__(self, line):
        return self._func(line)
    
    def _train(self, line):
        # line[0]: ImageID,Source,LabelName,Confidence,XMin,XMax,YMin,YMax,IsOccluded,IsTruncated,IsGroupOf,IsDepiction,IsInside,XClick1X,XClick2X,XClick3X,XClick4X,XClick1Y,XClick2Y,XClick3Y,XClick4Y
        # line[1]: 000002b66c9c498e,xclick,/m/01g317,1,0.025000,0.276563,0.714063,0.948438,0,1,0,0,0,0.025000,0.248438,0.276563,0.214062,0.914062,0.714063,0.782813,0.948438
        # num: 14610230
        pass

    def _train_tmp(self, line):
        # line[0]: ,ImagePath,LabelName,XMin,YMin,XMax,YMax,IsOccluded,IsTruncated
        id_, image_path, label_name, x_min, y_min, x_max, y_max, is_occluded, is_truncated = line.strip().split(',')
        image_name = image_path.split('/')[-1]
        image_path = self.image_name2path_dict[image_name]
        label_id = self.label_name2id_dict[label_name.lower()]
        return image_path, label_id
    
    def _val(self, line):
        # line[0]: ImageID,Source,LabelName,Confidence,XMin,XMax,YMin,YMax,IsOccluded,IsTruncated,IsGroupOf,IsDepiction,IsInside
        # line[1]: 0001eeaf4aed83f9,xclick,/m/0cmf2,1,0.022673031,0.9642005,0.07103825,0.80054647,0,0,0,0,0
        image_id, source, label_name, confidence, x_min, x_max, y_min, y_max, is_occluded, is_truncated, is_group_of, is_depiction, is_inside = line.strip().split(',')
        image_path = os.path.join("validation", f"{image_id}.jpg")
        label_id = self.label_name2id_dict[label_name.lower()]
        return image_path, label_id


def main():
    label_name2id_dict = LabelName2IdDict()
    parse_label_line = LabelLinePaser(label_name2id_dict)

    with open(label_file_path) as f:
        det_label_list = f.readlines()

    image_class_dict = {}
    for det_label in det_label_list[1:]:
        image_path, label_id = parse_label_line(det_label)
        if image_path not in image_class_dict:
            image_class_dict[image_path] = []
        if label_id not in image_class_dict[image_path]:
            image_class_dict[image_path].append(label_id)

    label_list = format_label_list(image_class_dict, len(label_name2id_dict))
    with open(save_file_path, "w") as f:
        f.write("\n".join(label_list))


if __name__ == '__main__':
    label_description_file_path = "annos/class-descriptions-boxable.csv"
    image_path_file_path = "annos/train_list.txt"
    # label_file_path = "annos/oidv6-train-annotations-bbox.csv"
    # label_file_path = "annos/oidv6-train-annotations-bbox.csv-tmp.csv"
    # save_file_path = "./multilabel_train_list.txt"

    label_file_path = "annos/validation-annotations-bbox.csv"
    save_file_path = "./multilabel_val_list.txt"

    main()
