---
title: 测试工程师Python库学习路线
date: 2026-09-10
updated: 2026-09-10
tags: [python, testing, data-testing, beginner]
aliases: [测试工程师Python工具箱]
status: active
level: beginner
---

# 测试工程师Python库学习路线

> [!abstract] 学习目标
> 在 pytest、requests、Selenium、Playwright 和 Allure 基础上，继续补齐测试数据、契约、Mock、数据库、性能和大数据验证能力。

## 推荐顺序

| 阶段 | 库 | 解决的问题 |
|---|---|---|
| 立即学习 | pandas、Faker、jsonschema、Pydantic | 表格处理、动态造数、接口契约 |
| 质量提升 | Hypothesis、pytest-mock、responses、Schemathesis | 边界值、依赖隔离、自动 API 探索 |
| 集成测试 | SQLAlchemy、Testcontainers | 数据库验证、真实依赖隔离 |
| 数据效率 | DuckDB、openpyxl、Polars | SQL 分析、Excel、较大数据集 |
| 专项能力 | Locust、PySpark | 性能测试、分布式数据测试 |

## 文件导航

- [[01-技术基础/Python/测试数据与专项测试库/01-pandas测试数据处理|01-pandas测试数据处理]]
- [[01-技术基础/Python/测试数据与专项测试库/02-Faker动态测试数据|02-Faker动态测试数据]]
- [[01-技术基础/Python/测试数据与专项测试库/03-jsonschema接口契约验证|03-jsonschema接口契约验证]]
- [[01-技术基础/Python/测试数据与专项测试库/04-Pydantic数据模型验证|04-Pydantic数据模型验证]]
- [[01-技术基础/Python/测试数据与专项测试库/05-Hypothesis属性测试|05-Hypothesis属性测试]]
- [[01-技术基础/Python/测试数据与专项测试库/06-pytest-mock依赖隔离|06-pytest-mock依赖隔离]]
- [[01-技术基础/Python/测试数据与专项测试库/07-responses模拟HTTP接口|07-responses模拟HTTP接口]]
- [[01-技术基础/Python/测试数据与专项测试库/08-Schemathesis自动API契约测试|08-Schemathesis自动API契约测试]]
- [[01-技术基础/Python/测试数据与专项测试库/09-Testcontainers集成测试|09-Testcontainers集成测试]]
- [[01-技术基础/Python/测试数据与专项测试库/10-SQLAlchemy数据库测试|10-SQLAlchemy数据库测试]]
- [[01-技术基础/Python/测试数据与专项测试库/11-DuckDB本地数据验证|11-DuckDB本地数据验证]]
- [[01-技术基础/Python/测试数据与专项测试库/12-openpyxl-Excel测试|12-openpyxl Excel测试]]
- [[01-技术基础/Python/测试数据与专项测试库/13-Polars高性能数据处理|13-Polars高性能数据处理]]
- [[01-技术基础/Python/测试数据与专项测试库/14-Locust性能测试|14-Locust性能测试]]
- [[01-技术基础/Python/测试数据与专项测试库/15-PySpark大数据测试|15-PySpark大数据测试]]

## 选择原则

```text
Excel/CSV/接口结果对比 → pandas
动态姓名和地址 → Faker
JSON Schema 契约 → jsonschema
Python 类型模型 → Pydantic
自动探索边界值 → Hypothesis
替换函数和对象 → pytest-mock
模拟 requests HTTP → responses
从 OpenAPI 自动造请求 → Schemathesis
临时启动数据库/中间件 → Testcontainers
查询业务数据库 → SQLAlchemy
本地 SQL 分析大文件 → DuckDB
检查 Excel 样式和公式 → openpyxl
pandas 性能不足 → Polars
并发与容量测试 → Locust
Spark/湖仓/ETL → PySpark
```

> [!warning] 结论边界
> Mock 通过不是集成通过；Schema 通过不是业务成功；本地数据核对不是生产验收；性能脚本能运行也不代表具备压测授权。
