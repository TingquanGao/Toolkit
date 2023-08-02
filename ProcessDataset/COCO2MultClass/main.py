import json

import numpy as np


def format_label_list(image_class_dict, class_num):
    label_list = []
    for img_path in image_class_dict:
        label = image_class_dict[img_path]
        onehot = np.zeros(class_num, dtype=int)
        onehot[label] = 1
        onehot_str = ",".join(str(v) for v in list(onehot))
        label_list.append(f"{img_path}\t{onehot_str}")
    return label_list



def main():
    with open(coco_label_path) as f:
        label_data = json.load(f)
    
    image_id2path = {}
    for img_info in label_data['images']:
        image_path, image_id = img_info['file_name'], img_info['id']
        image_id2path[image_id] = image_path
    
    label_id_rerank = {}
    for idx, categ_info in enumerate(label_data['categories']):
        label_id_rerank[categ_info['id']] = idx

    image_class_dict = {}
    for anno in label_data['annotations']:
        image_id, label_id = anno['image_id'], anno['category_id']
        image_path = image_id2path[image_id]
        label_id = label_id_rerank[label_id]
        if image_path not in image_class_dict:
            image_class_dict[image_path] = []
        if label_id not in image_class_dict[image_path]:
            image_class_dict[image_path].append(label_id)

    label_list = format_label_list(image_class_dict, len(label_data['categories']))
    with open(save_file_path, "w") as f:
        f.write("\n".join(label_list))


if __name__ == '__main__':
    coco_label_path = "./instances_train2017.json"
    save_file_path = "./multilabel_train_list.txt"
    main()
