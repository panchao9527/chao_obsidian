---
title: DuckDB本地数据验证
date: 2026-09-10
updated: 2026-09-10
tags: [python, duckdb, sql, data-testing]
status: active
level: beginner
---

# DuckDB本地数据验证

## 1. 为什么测试人员值得学

DuckDB 是嵌入式分析数据库，不需要单独部署服务，可以用 SQL 直接查询 CSV、JSON、Parquet、pandas 和 Polars 数据。适合大文件核对、ETL 结果检查和报表分析。

## 2. 安装

```powershell
# DuckDB 提供本地 SQL，pandas/pyarrow 用于 DataFrame 和 Parquet 互操作
python -m pip install duckdb pandas pyarrow
```

## 3. 查询 CSV 和 Parquet

```python
import duckdb

# DuckDB 可以把 CSV 路径直接当作 SQL 表查询
summary = duckdb.sql("""
    SELECT status, COUNT(*) AS total, SUM(amount) AS amount
    FROM 'orders.csv'
    GROUP BY status
    ORDER BY status
""").df()  # 将查询结果转换成 pandas DataFrame

print(summary)
```

```python
# 直接扫描 Parquet，并筛选主键为空或金额为负的问题行
invalid = duckdb.sql("""
    SELECT *
    FROM 'orders.parquet'
    WHERE id IS NULL OR amount < 0
""").df()

# 没有问题行时 DataFrame 才为空
assert invalid.empty
```

## 4. 查询 pandas

```python
import duckdb
import pandas as pd

# 创建待校验的 pandas DataFrame
actual_df = pd.DataFrame({"id": [1, 2], "amount": [10, 20]})
# SQL 中可以直接引用当前作用域内的 actual_df 变量名
result = duckdb.sql("SELECT SUM(amount) AS total FROM actual_df").fetchone()
# fetchone 返回一行元组，第一个元素是 SUM 结果
assert result[0] == 30
```

## 5. 使用独立连接

```python
import duckdb

# :memory: 表示数据库只存在于内存，关闭后不保留
with duckdb.connect(":memory:") as connection:
    # 创建测试表并插入一行预期数据
    connection.execute("CREATE TABLE expected (id INTEGER, amount DECIMAL(10,2))")
    connection.execute("INSERT INTO expected VALUES (1, 10.00)")
    rows = connection.execute("SELECT * FROM expected").fetchall()
```

并行程序不要共享默认全局连接，每个线程使用自己的 connection。

## 6. 对比两个结果集

```sql
-- 找出预期存在但实际不存在的记录
SELECT * FROM expected
EXCEPT
SELECT * FROM actual
UNION ALL
-- 再找出实际多出来的记录
SELECT * FROM actual
EXCEPT
SELECT * FROM expected;
```

实际使用时要明确列顺序、数据类型、重复记录和 NULL 语义。

## 7. DuckDB 和 Spark

本地单机文件、百万级记录和临时分析优先 DuckDB；已有 Spark 平台、超大规模分布式数据或流处理再使用 PySpark。

官方资料：[DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview)
