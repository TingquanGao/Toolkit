import json


def get_image_file2id(base_label):
    image_file2id_dict = {}
    for img in base_label['images']:
        file_name = img['file_name']
        image_id = img['id']
        image_file2id_dict[file_name] = image_id
    return image_file2id_dict


def get_pseudo_label(image_file2id):
    with open(pseudo_label_file_path) as f:
        pseudo_label_list = json.load(f)

    bbox_id = 909000554146   # max anno_id in coco (909000554145) + 1
    coco_format_label_list = []
    for label in pseudo_label_list:
        im_file = label['im_file'][0]
        file_name = im_file.split("/")[-1]

        image_id = image_file2id[file_name]
        bbox = label['bbox']
        area = bbox[2] * bbox[3]
        category_id = label['category_id']

        coco_format_label_list.append(
            {'area': area,
            'category_id': category_id,
            'image_id': image_id,
            'bbox': bbox,
            'iscrowd': 0,
            'id': bbox_id
            }
        )
        bbox_id += 1
    return coco_format_label_list


def merge_save(pseudo_label_list, true_label, base_label):
    true_label['images'] = base_label['images']

    for anno in true_label['annotations']:
        anno.pop('segmentation')
        anno_id = anno['id']

    true_label['annotations'].extend(pseudo_label_list)
    with open(save_label_file_path, 'w') as f:
        json.dump(true_label, f)


def main():
    with open(base_label_file_path) as f:
        base_label = json.load(f)

    with open(true_label_file_path) as f:
        true_label = json.load(f)

    image_file2id = get_image_file2id(base_label)
    pseudo_label_list = get_pseudo_label(image_file2id)
    merge_save(pseudo_label_list, true_label, base_label)


if __name__ == "__main__":
    base_label_file_path = "./annotations/instances_train2017.json"
    true_label_file_path = './ssod/instances_train2017.1@10.json'
    pseudo_label_file_path = "./pseudo/detr_hgnetv2_l_ssld_thresh0.5_bbox.json"
    save_label_file_path = "./merged/merged.json"
    main()
