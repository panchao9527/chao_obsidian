---
title: PySpark大数据测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, pyspark, spark, big-data-testing]
status: active
level: intermediate
---

# PySpark大数据测试

## 1. 什么时候学习

PySpark 是 Apache Spark 的 Python API，适合分布式 ETL、数据湖、Hive/Spark SQL、批处理和流处理。普通 CSV、Excel 和接口结果优先 pandas 或 DuckDB；项目本身使用 Spark、数据规模超过单机能力时再重点学习。

## 2. 前置条件

- Python；
- Java/JDK；
- 基础 SQL；
- DataFrame 概念；
- 本地或集群 Spark 环境。

```powershell
python -m pip install pyspark pytest
java -version
```

## 3. 创建 SparkSession

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("data-test")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")
```

## 4. DataFrame 和 Schema

```python
from pyspark.sql.types import DecimalType, IntegerType, StringType, StructField, StructType

schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("status", StringType(), False),
    StructField("amount", DecimalType(10, 2), True),
])

df = spark.createDataFrame(
    [(1, "SUCCESS", None), (2, "FAILED", None)],
    schema=schema,
)

df.printSchema()
df.show()
```

数据测试应显式检查 Schema、nullable、Decimal 精度和时间类型，不要完全依赖推断。

## 5. Transformation 与 Action

```python
from pyspark.sql.functions import col

valid = df.filter(col("id").isNotNull())  # Transformation，惰性
count = valid.count()                       # Action，触发计算
```

常见 Action：`count`、`collect`、`show`、`write`。不要对超大数据随意 `collect()` 到本机内存。

## 6. pytest fixture

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest-pyspark")
        .getOrCreate()
    )
    yield session
    session.stop()
```

## 7. 测试转换函数

```python
from pyspark.sql.functions import col
from pyspark.testing.utils import assertDataFrameEqual


def keep_positive_amount(df):
    return df.filter(col("amount") > 0)


def test_keep_positive_amount(spark):
    source = spark.createDataFrame([(1, 10), (2, -1)], ["id", "amount"])
    expected = spark.createDataFrame([(1, 10)], ["id", "amount"])

    actual = keep_positive_amount(source)
    assertDataFrameEqual(actual, expected)
```

## 8. Schema 对比

```python
from pyspark.testing.utils import assertSchemaEqual

assertSchemaEqual(actual.schema, expected.schema)
```

## 9. 数据质量检查

```python
from pyspark.sql.functions import col, count, when

assert df.filter(col("id").isNull()).count() == 0
assert df.groupBy("id").count().filter(col("count") > 1).count() == 0
assert df.filter(col("amount") < 0).count() == 0

null_summary = df.select([
    count(when(col(name).isNull(), name)).alias(name)
    for name in df.columns
])
```

## 10. 大数据测试维度

- Schema 和字段类型；
- 行数和唯一键；
- NULL、重复、越界值；
- 分区数量和分区字段；
- Join 前后数据量；
- 聚合和金额守恒；
- 增量和幂等；
- 时区与迟到数据；
- 数据倾斜和 Shuffle；
- 重跑、失败恢复和检查点；
- 输入、输出和血缘一致性。

## 11. 常见坑

- DataFrame 默认不保证行顺序，对比前排序；
- `collect()` 可能导致 Driver 内存溢出；
- 浮点金额有误差，使用 Decimal；
- 本地 `local[2]` 通过不能证明集群配置正确；
- 小样本无法暴露数据倾斜；
- UDF 逻辑应尽量拆成可单测纯函数；
- 测试结果要记录 Spark 配置、输入分区和代码版本。

## 12. pandas、DuckDB、PySpark 选择

```text
小中型表格和快速分析 → pandas
本地 SQL 查询 CSV/Parquet → DuckDB
高性能单机 DataFrame → Polars
分布式 ETL 和湖仓 → PySpark
```

官方资料：

- [PySpark DataFrame Quickstart](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html)
- [Testing PySpark](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html)
