import re
import json


def filter():
    md = []
    with open(md_path) as f:
        md = f.readlines()

    models_list = []
    for line in md:
        if "预训练模型下载地址" in line:
            heads = line.split("|")
            continue

        if "下载链接" in line:
            attrs = line.split("|")

            assert len(attrs) == len(heads)
            #attrs_dict = {k.strip(): attrs[i].strip() for i, k in enumerate(heads)}

            attrs_dict = {}
            for i, k in enumerate(heads):
                k = k.strip().replace("<br/>", "").replace("<br>", "")
                if not k == "":
                    v = attrs[i].strip().replace("<br/>", "").replace("<br>", "")
                    v = re.findall(r"]\((.*)\)", v)[0] if "下载地址" in k else v
                    attrs_dict[k] = v

            models_list.append(attrs_dict)
    return models_list


def unify(models_list):
    for model in models_list:
        model_name = model[""]
        pass


def main():
    models_list = filter()
    with open("metric.json", "w") as f:
        f.write(json.dumps(models_list, ensure_ascii=False, indent=4, separators=(',', ':')))


if __name__=="__main__":
    md_path = "./model_list.md"
    main()
