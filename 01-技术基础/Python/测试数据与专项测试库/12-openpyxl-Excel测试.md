---
title: openpyxl Excel测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, openpyxl, excel, data-testing]
status: active
level: beginner
---

# openpyxl Excel测试

## 1. 作用

openpyxl 用于读取和写入 `.xlsx` 文件，适合验证工作表、单元格、公式、样式、合并区域和报表模板。pandas 更擅长数据分析，openpyxl 更擅长 Excel 结构。

## 2. 安装

```powershell
# 安装 xlsx 文件读写库
python -m pip install openpyxl
```

## 3. 读取工作簿

```python
# load_workbook 用于打开已有 xlsx 文件
from openpyxl import load_workbook

# data_only=False 表示读取公式本身，而不是公式缓存结果
workbook = load_workbook("report.xlsx", data_only=False)
# 先检查目标工作表是否存在
assert "Summary" in workbook.sheetnames

# 按工作表名称取出 Sheet 对象
sheet = workbook["Summary"]
assert sheet["A1"].value == "测试报告"
assert sheet.max_row >= 2
```

`data_only=False` 读取公式文本；`data_only=True` 读取 Excel 上次保存的公式缓存值。openpyxl 本身不会计算公式。

## 4. 遍历数据

```python
# values_only=True 只返回单元格值，不返回 Cell 对象
rows = list(sheet.iter_rows(min_row=2, values_only=True))
assert rows

# 按列顺序解包每一行
for order_id, amount, status in rows:
    assert order_id is not None
    assert amount >= 0
    assert status in {"SUCCESS", "FAILED"}
```

## 5. 验证样式和合并

```python
# 检查标题是否加粗
assert sheet["A1"].font.bold is True
# 检查单元格是否有填充样式
assert sheet["A1"].fill.fill_type is not None
# 将所有合并区域转成字符串后检查 A1:C1
assert "A1:C1" in {str(item) for item in sheet.merged_cells.ranges}
```

## 6. 创建测试结果文件

```python
from openpyxl import Workbook

# 创建新工作簿；默认自带一张工作表
workbook = Workbook()
sheet = workbook.active
# 修改工作表名称并逐行追加内容
sheet.title = "Results"
sheet.append(["case", "status"])
sheet.append(["test_login", "PASSED"])
# 保存到当前工作目录
workbook.save("results.xlsx")
```

## 7. 常见坑

- 不支持旧 `.xls`；
- 不能计算公式；
- 日期可能被解析为 datetime；
- 大文件使用只读模式 `read_only=True`；
- 带宏文件需要谨慎使用 `keep_vba=True`；
- 修改模板前先备份，避免覆盖原件。

官方资料：[openpyxl Documentation](https://openpyxl.readthedocs.io/)
