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
# 安装 PySpark 和测试运行器；本机还必须有兼容 JDK
python -m pip install pyspark pytest
# 检查 Java 是否能被当前终端找到
java -version
```

## 3. 创建 SparkSession

```python
# SparkSession 是 DataFrame 和 SQL 功能的入口
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    # local[2] 表示本机模式，最多使用两个工作线程
    .master("local[2]")
    .appName("data-test")
    .getOrCreate()
)

# 减少控制台中不影响学习的 INFO 日志
spark.sparkContext.setLogLevel("WARN")
```

## 4. DataFrame 和 Schema

```python
# 显式定义字段类型和是否允许 NULL
from pyspark.sql.types import DecimalType, IntegerType, StringType, StructField, StructType

schema = StructType([
    # 第三个参数 False 表示该字段不允许 NULL
    StructField("id", IntegerType(), False),
    StructField("status", StringType(), False),
    StructField("amount", DecimalType(10, 2), True),
])

# 使用数据和显式 Schema 创建 DataFrame
df = spark.createDataFrame(
    [(1, "SUCCESS", None), (2, "FAILED", None)],
    schema=schema,
)

df.printSchema()  # 打印字段结构
df.show()         # 触发执行并展示少量数据
```

数据测试应显式检查 Schema、nullable、Decimal 精度和时间类型，不要完全依赖推断。

## 5. Transformation 与 Action

```python
from pyspark.sql.functions import col

# filter 只记录转换计划，此时通常还没有真正计算
valid = df.filter(col("id").isNotNull())  # Transformation，惰性
# count 是 Action，会触发 Spark 执行前面的转换
count = valid.count()                       # Action，触发计算
```

常见 Action：`count`、`collect`、`show`、`write`。不要对超大数据随意 `collect()` 到本机内存。

## 6. pytest fixture

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    # 整次 pytest 运行共享一个本地 SparkSession，减少启动耗时
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest-pyspark")
        .getOrCreate()
    )
    # 将 Session 提供给所有测试
    yield session
    # 全部测试结束后释放 Spark 资源
    session.stop()
```

## 7. 测试转换函数

```python
from pyspark.sql.functions import col
from pyspark.testing.utils import assertDataFrameEqual


def keep_positive_amount(df):
    # 被测转换：只保留金额大于 0 的行
    return df.filter(col("amount") > 0)


def test_keep_positive_amount(spark):
    # Arrange：准备输入和预期 DataFrame
    source = spark.createDataFrame([(1, 10), (2, -1)], ["id", "amount"])
    expected = spark.createDataFrame([(1, 10)], ["id", "amount"])

    # Act：调用被测转换函数
    actual = keep_positive_amount(source)
    # Assert：使用 Spark 官方辅助函数比较内容和结构
    assertDataFrameEqual(actual, expected)
```

## 8. Schema 对比

```python
from pyspark.testing.utils import assertSchemaEqual

# 只比较字段名、类型和 nullable 等 Schema 信息
assertSchemaEqual(actual.schema, expected.schema)
```

## 9. 数据质量检查

```python
from pyspark.sql.functions import col, count, when

# 必须没有空主键
assert df.filter(col("id").isNull()).count() == 0
# 按 id 分组，找到 count > 1 的重复键；预期重复组数量为 0
assert df.groupBy("id").count().filter(col("count") > 1).count() == 0
# 金额不能为负
assert df.filter(col("amount") < 0).count() == 0

# 对每一列分别统计 NULL 数量，形成一行汇总结果
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
