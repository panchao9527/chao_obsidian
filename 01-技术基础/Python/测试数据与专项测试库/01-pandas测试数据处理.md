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
# 安装 pandas；openpyxl 用于 xlsx，pyarrow 用于 Parquet
python -m pip install pandas openpyxl pyarrow
```

`openpyxl` 用于 xlsx，`pyarrow` 常用于 Parquet。

## 3. 创建和查看数据

```python
# 导入 pandas，并使用常见简称 pd
import pandas as pd

# DataFrame 可以理解为一张带行列的内存表格
df = pd.DataFrame([
    {"id": 1, "amount": 20.5, "status": "SUCCESS"},
    {"id": 2, "amount": 30.0, "status": "FAILED"},
])

print(df.head())           # 查看前 5 行
print(df.shape)            # 返回 (行数, 列数)
print(df.columns.tolist()) # 将列名转换成普通列表
print(df.dtypes)           # 查看每一列的数据类型
```

## 4. 读取和写出

```python
# 根据文件格式选择对应的读取函数
csv_df = pd.read_csv("orders.csv", encoding="utf-8")
excel_df = pd.read_excel("orders.xlsx", sheet_name="Orders")
json_df = pd.read_json("orders.json")

# index=False 表示不把 DataFrame 行号写入文件
csv_df.to_csv("clean.csv", index=False, encoding="utf-8-sig")
excel_df.to_excel("clean.xlsx", index=False)
```

## 5. 常用测试检查

```python
# 表不能是空的
assert not df.empty
# id 列不能有重复值
assert df["id"].is_unique
# id 列的每个值都不能是空值
assert df["id"].notna().all()
# 每一行金额都必须大于或等于 0
assert (df["amount"] >= 0).all()
# 实际状态集合必须是允许状态集合的子集
assert set(df["status"]) <= {"SUCCESS", "FAILED"}
# 本次示例预期正好有两行
assert len(df) == 2
```

定位问题行：

```python
# 使用布尔条件筛出金额为空或小于 0 的问题行
invalid = df[df["amount"].isna() | (df["amount"] < 0)]
# 如果 invalid 不是空表，就把问题数据打印到失败信息中
assert invalid.empty, f"发现非法金额：\n{invalid}"
```

## 6. 筛选、排序、分组

```python
# 只保留状态为 SUCCESS 的行
success = df[df["status"] == "SUCCESS"]
# 先按状态、再按 id 排序
sorted_df = df.sort_values(["status", "id"])
# 按状态分组，然后对金额求和
summary = df.groupby("status", as_index=False)["amount"].sum()
```

## 7. 表关联

```python
# 订单表通过 user_id 关联用户表
orders = pd.DataFrame([{"user_id": 1, "amount": 20}])
users = pd.DataFrame([{"user_id": 1, "name": "alice"}])

# how="left" 保留全部订单；validate 检查右表 user_id 是否唯一
merged = orders.merge(users, on="user_id", how="left", validate="many_to_one")
# 关联后的订单必须都能找到用户名
assert merged["name"].notna().all()
```

`validate` 能发现错误的一对多或多对多关系。

## 8. 精确对比

```python
# 分别读取预期结果和实际结果
expected = pd.read_excel("expected.xlsx")
actual = pd.read_excel("actual.xlsx")

# DataFrame 对比依赖行顺序，因此先按业务主键排序并重建行号
sort_keys = ["id"]
expected = expected.sort_values(sort_keys).reset_index(drop=True)
actual = actual.sort_values(sort_keys).reset_index(drop=True)

# 精确比较两张表；示例忽略 dtype 差异，但正式项目应按需决定
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
