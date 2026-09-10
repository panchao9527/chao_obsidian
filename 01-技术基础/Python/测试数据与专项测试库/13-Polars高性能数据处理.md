---
title: Polars高性能数据处理
date: 2026-09-10
updated: 2026-09-10
tags: [python, polars, data-testing, performance]
status: active
level: intermediate
---

# Polars高性能数据处理

## 1. 什么时候使用

Polars 是高性能 DataFrame 库。当 pandas 读取、过滤、分组大型 CSV/Parquet 明显变慢，或需要 Lazy 执行和流式处理时，可以考虑 Polars。初学者仍建议先掌握 pandas。

## 2. 安装

```powershell
# 安装 Polars Python 包
python -m pip install polars
```

## 3. 创建和读取

```python
# Polars 的社区惯用简称是 pl
import polars as pl

# 创建内存 DataFrame
df = pl.DataFrame({
    "id": [1, 2, 3],
    "amount": [10.0, 20.0, -1.0],
    "status": ["SUCCESS", "SUCCESS", "FAILED"],
})

# 根据文件格式读取数据
csv_df = pl.read_csv("orders.csv")
parquet_df = pl.read_parquet("orders.parquet")
```

## 4. 表达式

```python
# pl.col 表示引用某一列；| 表示“或者”
invalid = df.filter(
    pl.col("id").is_null()
    | (pl.col("amount") < 0)
)

# height 是 DataFrame 行数，本例预期只有一条负金额
assert invalid.height == 1
```

新增列：

```python
# with_columns 新增或替换列；表达式不会逐行进入 Python 循环
result = df.with_columns(
    # 金额乘 100、四舍五入、转整数，并命名为 amount_cent
    (pl.col("amount") * 100).round(0).cast(pl.Int64).alias("amount_cent")
)
```

## 5. 分组统计

```python
# 先按 status 分组
summary = (
    df.group_by("status")
    .agg(
        # pl.len 统计每组行数；sum 对每组金额求和
        pl.len().alias("total"),
        pl.col("amount").sum().alias("amount_sum"),
    )
    .sort("status")
)
```

## 6. Lazy API

```python
# scan_parquet 返回 LazyFrame，暂时不读取全部数据
result = (
    pl.scan_parquet("orders/*.parquet")
    .filter(pl.col("amount") >= 0)
    .group_by("status")
    .agg(pl.col("amount").sum())
    .collect()  # collect 才真正执行完整查询计划
)
```

LazyFrame 在 `collect()` 时执行，能优化查询并减少不必要的数据读取。

## 7. 测试对比

```python
# 使用 Polars 官方测试辅助函数比较 DataFrame
from polars.testing import assert_frame_equal

expected = pl.DataFrame({"status": ["SUCCESS"], "total": [2]})
actual = (
    df.filter(pl.col("status") == "SUCCESS")
    .group_by("status")
    .agg(pl.len().alias("total"))
)

# 对比前排序，避免行顺序差异造成误报
assert_frame_equal(actual.sort("status"), expected.sort("status"))
```

## 8. 常见坑

- pandas 与 Polars API 不是完全一致；
- 避免逐行 Python 循环；
- 对比前明确排序，因为分布或并行操作不总保证顺序；
- Lazy 错误可能到 `collect()` 才出现；
- 日期、Decimal、NULL 类型必须显式检查。

官方资料：[Polars Getting Started](https://docs.pola.rs/user-guide/getting-started/)
