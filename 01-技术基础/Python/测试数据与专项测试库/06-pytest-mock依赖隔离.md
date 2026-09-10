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
# 安装后 pytest 会自动提供 mocker fixture
python -m pip install pytest-mock
```

## 3. 替换函数

假设 `service.py`：

```python
# service.py 导入真实支付网关模块
import payment_gateway


def pay(order_id: int):
    # 将订单号传给第三方支付网关
    return payment_gateway.charge(order_id)
```

测试：

```python
def test_pay(mocker):
    # 替换 service 模块当前使用的 charge，并指定模拟返回值
    charge = mocker.patch("service.payment_gateway.charge", return_value={"status": "SUCCESS"})

    # 调用被测函数；此时不会访问真实支付网关
    result = pay(1001)

    # 验证返回结果和第三方调用参数
    assert result["status"] == "SUCCESS"
    charge.assert_called_once_with(1001)
```

关键原则：patch 被测模块“使用该对象的位置”，不是对象最初定义的位置。

## 4. 模拟异常

```python
def test_payment_timeout(mocker):
    # side_effect 表示调用 Mock 时抛出指定异常
    mocker.patch(
        "service.payment_gateway.charge",
        side_effect=TimeoutError("gateway timeout"),
    )

    # 验证被测函数确实向上抛出了超时
    with pytest.raises(TimeoutError):
        pay(1001)
```

## 5. Spy

```python
# spy 保留真实调用，同时记录调用次数和参数
spy = mocker.spy(service, "calculate_total")
result = service.create_order(items)
# 验证 calculate_total 只被调用一次，参数就是 items
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
