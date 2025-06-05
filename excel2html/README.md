# 将剪贴板中的 Excel 数据转为 HTML

## 1. 使用

1. 在 Excel 中选中待转换的表格区域，并复制；
2. 运行`python main.py`。

参数说明：
1. `--keep_align`：是否保留表格标签的对齐属性，包括`align`，`valign`和`text-align`，默认不保留。
2. `--keep_width_height`：是否保留表格标签的宽高属性，包括`width`和`height`，默认不保留。
3. `--print`：是否将 html 结果打印出来，默认不打印。
4. `--pretty`：是否对 html 进行格式化，默认不进行格式，以一行字符串输出。
5. `--save_path`：html 结果存储路径，默认为`result.html`。
