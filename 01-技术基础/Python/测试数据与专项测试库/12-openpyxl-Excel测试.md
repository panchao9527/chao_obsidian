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
python -m pip install openpyxl
```

## 3. 读取工作簿

```python
from openpyxl import load_workbook

workbook = load_workbook("report.xlsx", data_only=False)
assert "Summary" in workbook.sheetnames

sheet = workbook["Summary"]
assert sheet["A1"].value == "测试报告"
assert sheet.max_row >= 2
```

`data_only=False` 读取公式文本；`data_only=True` 读取 Excel 上次保存的公式缓存值。openpyxl 本身不会计算公式。

## 4. 遍历数据

```python
rows = list(sheet.iter_rows(min_row=2, values_only=True))
assert rows

for order_id, amount, status in rows:
    assert order_id is not None
    assert amount >= 0
    assert status in {"SUCCESS", "FAILED"}
```

## 5. 验证样式和合并

```python
assert sheet["A1"].font.bold is True
assert sheet["A1"].fill.fill_type is not None
assert "A1:C1" in {str(item) for item in sheet.merged_cells.ranges}
```

## 6. 创建测试结果文件

```python
from openpyxl import Workbook

workbook = Workbook()
sheet = workbook.active
sheet.title = "Results"
sheet.append(["case", "status"])
sheet.append(["test_login", "PASSED"])
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
