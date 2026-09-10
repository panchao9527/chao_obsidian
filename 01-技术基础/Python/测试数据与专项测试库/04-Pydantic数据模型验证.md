---
title: Pydantic数据模型验证
date: 2026-09-10
updated: 2026-09-10
tags: [python, pydantic, api-testing, data-validation]
status: active
level: beginner
---

# Pydantic数据模型验证

## 1. 作用

Pydantic 用 Python 类型注解定义数据模型，适合把接口 JSON 转为可复用、可自动校验的对象。

## 2. 安装

```powershell
# 安装当前 Pydantic 版本
python -m pip install pydantic
```

## 3. 基础模型

```python
# BaseModel 是所有 Pydantic 数据模型的基类
from pydantic import BaseModel


class User(BaseModel):
    # 类型注解同时描述字段类型和必填字段
    id: int
    name: str
    enabled: bool


# model_validate 将字典校验并转换成 User 对象
user = User.model_validate({"id": 1, "name": "alice", "enabled": True})
# 之后可以通过属性读取字段，而不是 user["id"]
assert user.id == 1
```

## 4. 嵌套响应

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    # gt=0 表示 id 必须大于 0
    id: int = Field(gt=0)
    # 字符串长度必须在 1 到 100 之间
    name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    code: int
    message: str
    data: list[User]


# 把接口响应 JSON 转成带类型的对象
result = UserResponse.model_validate(response.json())
assert result.code == 0
assert result.data[0].id > 0
```

## 5. 禁止额外字段

```python
from pydantic import BaseModel, ConfigDict


class StrictUser(BaseModel):
    # extra="forbid" 表示响应出现未定义字段时也报错
    model_config = ConfigDict(extra="forbid")
    id: int
    name: str
```

是否禁止新增字段取决于契约策略。开放接口新增兼容字段时，过严模型会造成无意义失败。

## 6. 自定义校验

```python
from pydantic import BaseModel, field_validator


class Payment(BaseModel):
    amount: float

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        # 自定义业务规则：金额必须大于 0
        if value <= 0:
            raise ValueError("amount must be positive")
        return value
```

金额场景更推荐 `Decimal`，避免浮点误差。

## 7. jsonschema 还是 Pydantic

```text
外部标准契约、跨语言共享 → jsonschema
Python 框架内部模型、类型提示 → Pydantic
严格核心接口 → 两者可组合，但避免重复维护失控
```

## 8. 常见坑

- 注意 Pydantic 大版本语法差异；
- 自动类型转换可能掩盖服务端类型错误，严格场景启用 strict；
- 不在错误日志中输出敏感原始响应；
- 模型通过后仍要断言业务语义。

官方资料：[Pydantic Documentation](https://docs.pydantic.dev/latest/)
