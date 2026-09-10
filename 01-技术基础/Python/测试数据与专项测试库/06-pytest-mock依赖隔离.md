---
title: pytest-mock依赖隔离
date: 2026-09-10
updated: 2026-09-10
tags: [python, pytest, mock, unit-testing]
status: active
level: intermediate
---

# pytest-mock依赖隔离

## 1. 作用

pytest-mock 提供 `mocker` fixture，包装标准库 `unittest.mock`，用于替换外部依赖、固定时间、模拟异常并验证函数是否按预期调用。

## 2. 安装

```powershell
python -m pip install pytest-mock
```

## 3. 替换函数

假设 `service.py`：

```python
import payment_gateway


def pay(order_id: int):
    return payment_gateway.charge(order_id)
```

测试：

```python
def test_pay(mocker):
    charge = mocker.patch("service.payment_gateway.charge", return_value={"status": "SUCCESS"})

    result = pay(1001)

    assert result["status"] == "SUCCESS"
    charge.assert_called_once_with(1001)
```

关键原则：patch 被测模块“使用该对象的位置”，不是对象最初定义的位置。

## 4. 模拟异常

```python
def test_payment_timeout(mocker):
    mocker.patch(
        "service.payment_gateway.charge",
        side_effect=TimeoutError("gateway timeout"),
    )

    with pytest.raises(TimeoutError):
        pay(1001)
```

## 5. Spy

```python
spy = mocker.spy(service, "calculate_total")
result = service.create_order(items)
spy.assert_called_once_with(items)
```

Spy 调用真实实现并记录调用；Mock 通常替换真实实现。

## 6. 常见错误

- Patch 路径错误，实际依赖仍被调用；
- Mock 返回值与真实接口结构不一致；
- 过度 Mock 导致测试只验证自己的假设；
- Mock 通过不能代替集成测试；
- 不要 Mock 被测核心逻辑本身。

官方资料：[pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
