---
title: Testcontainers集成测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, testcontainers, docker, integration-testing]
status: active
level: intermediate
---

# Testcontainers集成测试

## 1. 作用

Testcontainers 在测试期间启动临时 Docker 容器，例如 PostgreSQL、MySQL、Redis、Kafka；测试结束后销毁，用真实依赖替代共享环境或纯 Mock。

## 2. 前置条件

- Docker Desktop 正常运行；
- 当前账号可执行 Docker；
- CI Runner 支持容器；
- 镜像源、代理和磁盘空间可用。

```powershell
docker version
python -m pip install testcontainers
```

## 3. PostgreSQL 示例

```python
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text


def test_database_round_trip():
    with PostgresContainer("postgres:17") as postgres:
        engine = create_engine(postgres.get_connection_url())
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE users (id INT, name TEXT)"))
            connection.execute(
                text("INSERT INTO users VALUES (:id, :name)"),
                {"id": 1, "name": "alice"},
            )
            actual = connection.execute(text("SELECT name FROM users WHERE id=1")).scalar_one()
        assert actual == "alice"
```

## 4. pytest fixture

```python
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:17") as container:
        yield container.get_connection_url()
```

Session 级容器启动更快，但每条测试仍应通过事务或清表隔离数据。

## 5. 最佳实践

- 固定镜像大版本，避免 `latest` 漂移；
- 等待容器健康，而不是固定 sleep；
- 初始化 Schema 与生产迁移脚本保持一致；
- 为每条测试准备独立数据；
- CI 中缓存镜像但不要缓存脏数据卷；
- 测试结束确认容器已清理。

## 6. 常见问题

启动慢通常是首次拉镜像；连接失败可能是容器尚未就绪；Windows 路径挂载要注意权限。Testcontainers 适合集成测试，不必用于每条纯函数单元测试。

官方资料：[Testcontainers for Python](https://testcontainers-python.readthedocs.io/)
