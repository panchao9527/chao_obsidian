---
title: Faker动态测试数据
date: 2026-09-10
updated: 2026-09-10
tags: [python, faker, test-data, beginner]
status: active
level: beginner
---

# Faker动态测试数据

## 1. 用途

Faker 可以生成姓名、地址、邮箱、日期等近似真实数据，适合减少对固定 UAT 数据的依赖。它生成的是格式数据，不保证满足具体业务校验。

## 2. 安装

```powershell
python -m pip install Faker
```

## 3. 基础使用

```python
from faker import Faker

fake = Faker("zh_CN")

print(fake.name())
print(fake.address())
print(fake.email())
print(fake.date_of_birth(minimum_age=18, maximum_age=60))
```

## 4. 唯一业务数据

```python
from uuid import uuid4
from faker import Faker

fake = Faker("zh_CN")


def build_user() -> dict:
    suffix = uuid4().hex[:10]
    return {
        "username": f"auto-{suffix}",
        "name": fake.name(),
        "email": f"auto-{suffix}@example.test",
    }
```

业务唯一键优先用 UUID、时间戳或数据库返回 ID，不能只依赖 Faker 的随机性。

## 5. 可复现数据

```python
from faker import Faker

Faker.seed(20260910)
fake = Faker("zh_CN")
print(fake.name())
```

固定 seed 适合复现缺陷；并行测试中要避免共享全局随机状态。

## 6. pytest fixture

```python
import pytest
from faker import Faker


@pytest.fixture
def fake():
    return Faker("zh_CN")


def test_user_name(fake):
    name = fake.name()
    assert name.strip()
```

## 7. 自定义 Provider

```python
from faker import Faker
from faker.providers import BaseProvider


class BusinessProvider(BaseProvider):
    def task_type(self):
        return self.random_element(["PAYMENT", "INVOICE", "AUDIT"])


fake = Faker()
fake.add_provider(BusinessProvider)
print(fake.task_type())
```

## 8. 风险

- 假手机号、邮箱仍可能误触真实系统；
- 随机数据可能偶发不满足业务规则；
- 生成数据必须带自动化前缀并可清理；
- 不用 Faker 伪造必须来自权威系统的员工、门店、发票数据；
- 失败时记录 seed 或最终输入。

官方资料：[Faker Documentation](https://faker.readthedocs.io/)
