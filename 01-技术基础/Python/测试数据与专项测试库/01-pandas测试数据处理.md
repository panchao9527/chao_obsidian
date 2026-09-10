---
title: pandas测试数据处理
date: 2026-09-10
updated: 2026-09-10
tags: [python, pandas, data-testing, beginner]
status: active
level: beginner
---

# pandas测试数据处理

## 1. 适用场景

pandas 用 `DataFrame` 表示二维表格，适合读取 CSV、Excel、JSON、SQL，进行筛选、去重、关联、分组、统计和结果对比。测试中常用于报表核对、批量造数、接口结果与数据库结果比较。

## 2. 安装

```powershell
python -m pip install pandas openpyxl pyarrow
```

`openpyxl` 用于 xlsx，`pyarrow` 常用于 Parquet。

## 3. 创建和查看数据

```python
import pandas as pd

df = pd.DataFrame([
    {"id": 1, "amount": 20.5, "status": "SUCCESS"},
    {"id": 2, "amount": 30.0, "status": "FAILED"},
])

print(df.head())
print(df.shape)
print(df.columns.tolist())
print(df.dtypes)
```

## 4. 读取和写出

```python
csv_df = pd.read_csv("orders.csv", encoding="utf-8")
excel_df = pd.read_excel("orders.xlsx", sheet_name="Orders")
json_df = pd.read_json("orders.json")

csv_df.to_csv("clean.csv", index=False, encoding="utf-8-sig")
excel_df.to_excel("clean.xlsx", index=False)
```

## 5. 常用测试检查

```python
assert not df.empty
assert df["id"].is_unique
assert df["id"].notna().all()
assert (df["amount"] >= 0).all()
assert set(df["status"]) <= {"SUCCESS", "FAILED"}
assert len(df) == 2
```

定位问题行：

```python
invalid = df[df["amount"].isna() | (df["amount"] < 0)]
assert invalid.empty, f"发现非法金额：\n{invalid}"
```

## 6. 筛选、排序、分组

```python
success = df[df["status"] == "SUCCESS"]
sorted_df = df.sort_values(["status", "id"])
summary = df.groupby("status", as_index=False)["amount"].sum()
```

## 7. 表关联

```python
orders = pd.DataFrame([{"user_id": 1, "amount": 20}])
users = pd.DataFrame([{"user_id": 1, "name": "alice"}])

merged = orders.merge(users, on="user_id", how="left", validate="many_to_one")
assert merged["name"].notna().all()
```

`validate` 能发现错误的一对多或多对多关系。

## 8. 精确对比

```python
expected = pd.read_excel("expected.xlsx")
actual = pd.read_excel("actual.xlsx")

sort_keys = ["id"]
expected = expected.sort_values(sort_keys).reset_index(drop=True)
actual = actual.sort_values(sort_keys).reset_index(drop=True)

pd.testing.assert_frame_equal(actual, expected, check_dtype=False)
```

金额建议先转换为 `Decimal` 或按业务精度统一 round，不要盲目忽略差异。

## 9. 常见坑

- Excel 数字可能被读成浮点数；
- 空值有 `None`、`NaN`、空字符串多种形式；
- 日期、时区和字符串格式可能不同；
- 对比前必须确定排序键；
- 大表逐行 `iterrows()` 很慢，优先列运算；
- 输出数据前先脱敏。

## 10. 练习

- [ ] 读取一个 Excel 并检查必填列
- [ ] 找出重复 ID 和负金额
- [ ] 按状态统计数量和金额
- [ ] 比较 expected 与 actual 两张表

官方资料：[pandas Getting Started](https://pandas.pydata.org/docs/getting_started/)
