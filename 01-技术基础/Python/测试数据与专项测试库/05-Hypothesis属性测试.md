---
title: Hypothesis属性测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, hypothesis, property-based-testing]
status: active
level: intermediate
---

# Hypothesis属性测试

## 1. 什么是属性测试

传统测试手工给出几个输入；Hypothesis 根据“输入策略”生成大量样例，自动探索空值、边界、Unicode、极大值等情况，并将失败缩减为最小反例。

## 2. 安装

```powershell
# 安装属性测试库
python -m pip install hypothesis
```

## 3. 第一个测试

```python
# given 负责把生成的数据传给测试函数，strategies 定义数据范围
from hypothesis import given, strategies as st


@given(st.integers(), st.integers())
def test_addition_commutative(left, right):
    # 无论生成什么整数，交换加数顺序后结果都应相同
    assert left + right == right + left
```

## 4. 常用策略

```python
st.integers(min_value=0, max_value=100)              # 0 到 100 的整数
st.floats(allow_nan=False, allow_infinity=False)     # 排除 NaN 和无穷值的小数
st.text(min_size=1, max_size=50)                     # 1 到 50 字符的字符串
st.booleans()                                        # True 或 False
st.none()                                            # 只生成 None
st.lists(st.integers(), max_size=20)                 # 最多 20 个整数的列表
st.dictionaries(st.text(min_size=1), st.integers(), max_size=10)  # 字典
st.one_of(st.none(), st.text())                      # None 或字符串
```

## 5. 测试数据转换

```python
@given(st.text())
def test_normalize_never_has_outer_spaces(value):
    # 把自动生成的任意 Unicode 字符串交给被测函数
    result = normalize(value)
    # 归一化后的结果不允许保留首尾空格
    assert result == result.strip()
```

## 6. 组合业务对象

```python
@st.composite
def users(draw):
    # draw 从指定策略中取出一条本次测试数据
    return {
        "name": draw(st.text(min_size=1, max_size=30)),
        "age": draw(st.integers(min_value=18, max_value=65)),
    }


@given(users())
def test_user_payload(user):
    # Hypothesis 会尝试多组满足策略的用户对象
    assert 18 <= user["age"] <= 65
```

## 7. 适用和不适用

适合纯函数、解析器、金额规则、排序、校验器和序列化。对会写数据库、发短信或创建真实订单的接口，不能直接无限生成输入，应先隔离副作用。

## 8. 调试失败

Hypothesis 会保存失败示例并在后续重放。不要看到随机输入就认为不可复现；保留失败输出、代码版本和配置，不要随意删除 `.hypothesis` 来掩盖失败。

官方资料：[Hypothesis Documentation](https://hypothesis.readthedocs.io/en/latest/)
