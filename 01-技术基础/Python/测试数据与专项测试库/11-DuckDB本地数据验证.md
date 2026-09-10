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
python -m pip install duckdb pandas pyarrow
```

## 3. 查询 CSV 和 Parquet

```python
import duckdb

summary = duckdb.sql("""
    SELECT status, COUNT(*) AS total, SUM(amount) AS amount
    FROM 'orders.csv'
    GROUP BY status
    ORDER BY status
""").df()

print(summary)
```

```python
invalid = duckdb.sql("""
    SELECT *
    FROM 'orders.parquet'
    WHERE id IS NULL OR amount < 0
""").df()

assert invalid.empty
```

## 4. 查询 pandas

```python
import duckdb
import pandas as pd

actual_df = pd.DataFrame({"id": [1, 2], "amount": [10, 20]})
result = duckdb.sql("SELECT SUM(amount) AS total FROM actual_df").fetchone()
assert result[0] == 30
```

## 5. 使用独立连接

```python
import duckdb

with duckdb.connect(":memory:") as connection:
    connection.execute("CREATE TABLE expected (id INTEGER, amount DECIMAL(10,2))")
    connection.execute("INSERT INTO expected VALUES (1, 10.00)")
    rows = connection.execute("SELECT * FROM expected").fetchall()
```

并行程序不要共享默认全局连接，每个线程使用自己的 connection。

## 6. 对比两个结果集

```sql
SELECT * FROM expected
EXCEPT
SELECT * FROM actual
UNION ALL
SELECT * FROM actual
EXCEPT
SELECT * FROM expected;
```

实际使用时要明确列顺序、数据类型、重复记录和 NULL 语义。

## 7. DuckDB 和 Spark

本地单机文件、百万级记录和临时分析优先 DuckDB；已有 Spark 平台、超大规模分布式数据或流处理再使用 PySpark。

官方资料：[DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview)
