---
title: jsonschema接口契约验证
date: 2026-09-10
updated: 2026-09-10
tags: [python, jsonschema, api-testing, contract-testing]
status: active
level: beginner
---

# jsonschema接口契约验证

## 1. 作用

jsonschema 验证 JSON 是否满足字段、类型、必填项、枚举、长度和嵌套结构要求。它验证结构，不负责判断业务状态是否成功。

## 2. 安装

```powershell
python -m pip install jsonschema
```

## 3. 最小示例

```python
from jsonschema import validate

schema = {
    "type": "object",
    "required": ["code", "message", "data"],
    "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"},
        "data": {"type": "array"},
    },
    "additionalProperties": False,
}

validate({"code": 0, "message": "success", "data": []}, schema)
```

## 4. 嵌套结构

```python
schema = {
    "type": "object",
    "required": ["id", "status"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "status": {"enum": ["NEW", "DONE", "FAILED"]},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "amount"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "amount": {"type": "number", "minimum": 0},
                },
            },
        },
    },
}
```

## 5. 收集全部错误

```python
from jsonschema import Draft202012Validator

validator = Draft202012Validator(schema)
errors = sorted(validator.iter_errors(response.json()), key=lambda e: list(e.path))

assert not errors, "\n".join(
    f"path={list(error.path)} message={error.message}"
    for error in errors
)
```

## 6. pytest 中使用

```python
def test_user_contract(api_session):
    response = api_session.get(url, timeout=10)
    assert response.status_code == 200
    body = response.json()
    validate(instance=body, schema=schema)
    assert body["code"] == 0
```

## 7. 常见坑

- `format: email` 默认不一定执行格式检查；
- `additionalProperties: False` 过严时会阻止后端兼容性新增字段；
- 可空字段需要声明 `{"type": ["string", "null"]}`；
- Schema 版本应固定；
- Schema 和接口实现同时修改时要防止“共同犯错”。

官方资料：[jsonschema Documentation](https://python-jsonschema.readthedocs.io/en/stable/)
