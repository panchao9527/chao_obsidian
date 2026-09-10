---
title: SQLAlchemy数据库测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, sqlalchemy, database-testing]
status: active
level: intermediate
---

# SQLAlchemy数据库测试

## 1. 作用

SQLAlchemy 提供数据库连接、SQL 表达式和 ORM。测试中适合准备前置数据、验证接口后的状态、管理事务和支持多种数据库驱动。

## 2. 安装

```powershell
python -m pip install sqlalchemy
```

不同数据库还需要驱动，例如 PostgreSQL 可使用 `psycopg`，MySQL 可使用 `pymysql`。

## 3. Engine 和查询

```python
from sqlalchemy import create_engine, text

engine = create_engine(database_url, pool_pre_ping=True)

with engine.connect() as connection:
    row = connection.execute(
        text("SELECT status FROM task WHERE id = :task_id"),
        {"task_id": 1001},
    ).one()

assert row.status == "COMPLETED"
```

必须使用参数绑定，不要拼接用户输入：

```python
# 错误
text(f"SELECT * FROM task WHERE id = {task_id}")

# 正确
text("SELECT * FROM task WHERE id = :task_id")
```

## 4. 事务隔离 fixture

```python
import pytest


@pytest.fixture
def db_connection(engine):
    connection = engine.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()
```

事务回滚并非适合所有场景：如果被测服务使用另一个数据库连接，它可能看不到未提交数据，也不会被当前测试事务自动回滚。

## 5. 验证接口后的数据库状态

```python
def test_create_task(api_client, db_connection):
    response = api_client.post("/tasks", json={"name": "auto-task"})
    assert response.status_code == 201

    task_id = response.json()["id"]
    row = db_connection.execute(
        text("SELECT name, status FROM task WHERE id=:id"),
        {"id": task_id},
    ).one()

    assert row.name == "auto-task"
    assert row.status == "NEW"
```

## 6. 安全边界

- 生产连接默认只读；
- 凭据来自环境变量或 Secret Manager；
- 不记录连接串密码；
- 测试数据带唯一前缀并可清理；
- 不使用无 WHERE 的 UPDATE/DELETE；
- 跨系统一致性要考虑异步延迟和最终一致性。

官方资料：[SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
