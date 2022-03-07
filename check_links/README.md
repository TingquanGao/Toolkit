# 检查文档中的跳转链接

## 1. 使用

```python
python path_to_repo/Toolkit/check_links/check_links.py --root_path ./docs --suffix .md .py --save_path ./check.csv --j_anchor True --j_file True --j_http True
```

## 2. 参数说明

* --root_dir: 待检查文档的路径，或是包含待检查文档的目录，默认为 `./docs`；
* --suffix: 待检查文档的后缀名，默认为 `.md`；
* --save_path: 检查结果的保存路径，默认为 `./check.csv`；
* --j_anchor: 是否检查文档内部跳转链接，如：`[1. 前言](#1)`；
* --j_file: 是否检查文件之间跳转链接，如 `[Paddle-Lite benchmark](../others/paddle_mobile_inference.md)。`；
* --j_http: 是否检查文档中的 `http` 跳转链接，如 `[PaddleClas](https://github.com/PaddlePaddle/PaddleClas)`。

## 3. 注意事项

* 当检查文档中的http链接时，因为需要request，因此会受网络环境影响。
* 对于 MarkDown 文档中的注释行（`<!--`）将忽略检查。
