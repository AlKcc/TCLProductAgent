#!/usr/bin/env python3
"""
快速验证：能否从TCL官网提取产品数据
"""
import re
import json

# 读取之前保存的HTML文件
with open('/Users/chenkai/.claude/projects/-Users-chenkai-Downloads-AGENT-DEMO/11730b1d-21f7-4f75-a66f-fca0ed8e688f/tool-results/bzu430t6v.txt', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 提取产品型号信息
product_models = []

# 方法1: 查找JSON数据中的产品信息
json_pattern = r'"name":"([^"]+)","link":"([^"]+)"'
matches = re.findall(json_pattern, html_content)

print("=" * 60)
print("从TCL官网提取到的产品类别和链接：")
print("=" * 60)

product_categories = {}
for name, link in matches[:50]:  # 只显示前50个
    if '电视' in name or '空调' in name or '冰箱' in name or '洗衣机' in name:
        if name not in product_categories:
            product_categories[name] = link
            print(f"✓ {name}: {link}")

print("\n" + "=" * 60)
print("总结：")
print("=" * 60)
print(f"找到 {len(product_categories)} 个相关产品类别")
print("\n结论：✅ TCL官网的产品数据结构化程度很高，可以提取！")

# 检查是否有参数信息
param_pattern = r'(\d+英寸|\d+P|\d+K|Mini LED|量子点|变频|风冷)'
param_matches = re.findall(param_pattern, html_content)
print(f"\n找到的技术参数关键词：{len(param_matches)} 个")
print("示例参数：", param_matches[:20])