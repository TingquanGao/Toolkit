import re
from bs4 import BeautifulSoup, Comment, ProcessingInstruction
import argparse

# 导入 PyObjC 库中的必要模块
from AppKit import NSPasteboard, NSHTMLPboardType

def get_clipboard_html():
    pb = NSPasteboard.generalPasteboard()
    types = pb.types()
    if NSHTMLPboardType in types:
        data = pb.stringForType_(NSHTMLPboardType)
        # 确保返回的数据是字符串类型
        if isinstance(data, str):
            return data
        else:
            return data.decode('utf-8')
    else:
        return None

def process_html(html_data, keep_align=True, keep_width_height=True):
    soup = BeautifulSoup(html_data, 'html.parser')
    # 删除不必要的标签
    delete_tags = ['style', 'link', 'meta']
    
    # 定义允许的标签和属性
    allowed_tags = ['table', 'thead', 'tbody', 'tr', 'td', 'th']
    always_allowed_attrs = ['colspan', 'rowspan']
    if keep_align:
        always_allowed_attrs.extend(['align', 'valign', 'text-align'])
    if keep_width_height:
        always_allowed_attrs.extend(['width', 'height'])

    # 移除不在允许列表中的标签，但保留其内容
    for tag in soup.find_all():
        if tag.name in delete_tags:
            tag.extract()
            continue
        if tag.name not in allowed_tags:
            tag.unwrap()

    # 移除不必要的属性
    for tag in soup.find_all():
        attrs = dict(tag.attrs)
        for attr in attrs:
            if attr not in always_allowed_attrs:
                del tag.attrs[attr]

    # NOTE: 如果不这样做，会因为处理后的soup中存在空行及格式化问题造成无法去除所有的注释和 processing instructions
    soup = BeautifulSoup(str(soup), 'html.parser')
    # 查找所有的注释和 processing instructions
    for tag in soup.find_all(string=lambda text: isinstance(text, (Comment, ProcessingInstruction))):
        tag.extract()

    # 移除空标签
    for tag in soup.find_all(['td', 'th', 'tr', 'table', 'thead', 'tbody']):
        if not tag.get_text(strip=True):
            tag.unwrap()

    # 为每个<table>标签添加border属性
    for table in soup.find_all('table'):
        table['border'] = '1'

    return soup.prettify()


def main():
    parser = argparse.ArgumentParser(description='将 Excel 剪贴板表格转换为 HTML')
    parser.add_argument('--keep_align', action='store_true', default=True, help='保留对齐属性（align）')
    parser.add_argument('--keep_width_height', action='store_true', default=False, help='保留宽高属性（width 和 height）')
    parser.add_argument('--save_path', type=str, default="result.html", help='存储路径')
    args = parser.parse_args()

    html_data = get_clipboard_html()
    if html_data:
        output_html = process_html(
            html_data,
            keep_align=args.keep_align,
            keep_width_height=args.keep_width_height
        )
        with open(args.save_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        print(f"HTML 数据已保存到 {args.save_path}")
    else:
        print("剪贴板中没有 HTML 数据.")

if __name__ == '__main__':
    main()
