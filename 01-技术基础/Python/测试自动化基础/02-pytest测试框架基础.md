---
title: pytest测试框架基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - pytest
  - testing
  - beginner
aliases:
  - pytest小白教程
status: active
level: beginner
---

# pytest测试框架基础

上一步：[[01-技术基础/Python/测试自动化基础/01-Python操作基础|01-Python操作基础]]

下一步：[[01-技术基础/Python/测试自动化基础/03-requests接口测试基础|03-requests接口测试基础]]

## 1. pytest 是什么

pytest 是 Python 测试框架，负责发现用例、执行测试、展示失败原因、管理前置与清理动作。测试函数使用普通 `assert`，失败时 pytest 会展示参与比较的实际值。

安装：

```powershell
python -m pip install -U pytest
python -m pytest --version
```

## 2. 第一个测试

创建 `tests/test_calculator.py`：

```python
def add(left: int, right: int) -> int:
    return left + right


def test_add_two_numbers():
    actual = add(1, 2)
    assert actual == 3
```

运行：

```powershell
python -m pytest
```

常见结果：

```text
.  通过
F  失败
E  准备或清理阶段出错
s  跳过
x  预期失败
```

## 3. 用例发现规则

pytest 默认寻找：

- `test_*.py` 或 `*_test.py` 文件；
- `test_` 开头的函数；
- `Test` 开头、没有自定义 `__init__` 的类；
- 类中 `test_` 开头的方法。

```python
class TestCalculator:
    def test_add(self):
        assert 1 + 1 == 2

    def test_subtract(self):
        assert 3 - 1 == 2
```

`helper_check()` 不会自动被当成测试执行。

## 4. 常用运行命令

```powershell
# 全部测试
python -m pytest

# 简洁输出
python -m pytest -q

# 详细输出
python -m pytest -v

# 运行一个文件
python -m pytest tests\test_calculator.py

# 运行一个函数
python -m pytest tests\test_calculator.py::test_add_two_numbers

# 名称包含 login 的用例
python -m pytest -k login

# 第一次失败后停止
python -m pytest -x

# 最多失败 3 条后停止
python -m pytest --maxfail=3

# 显示 print 输出
python -m pytest -s

# 只收集，不执行
python -m pytest --collect-only
```

## 5. 断言

```python
def test_common_assertions():
    status_code = 200
    body = {"code": 0, "message": "success", "data": [1, 2]}

    assert status_code == 200
    assert body["code"] == 0
    assert body["message"] == "success"
    assert len(body["data"]) == 2
    assert 1 in body["data"]
    assert body["data"]
```

添加失败说明：

```python
assert body["code"] == 0, f"业务失败，响应为：{body}"
```

浮点数：

```python
import pytest


def test_price():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

异常断言：

```python
import pytest


def divide(left, right):
    return left / right


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

## 6. fixture：准备和清理测试资源

```python
import pytest


@pytest.fixture
def user():
    return {"id": 1, "name": "alice"}


def test_user_name(user):
    assert user["name"] == "alice"
```

fixture 名字写在测试函数参数中，pytest 会自动调用。

带清理动作：

```python
import pytest


@pytest.fixture
def temporary_user():
    user = {"id": 1001, "name": "auto-user"}
    print("创建用户")
    yield user
    print("删除用户")


def test_temporary_user(temporary_user):
    assert temporary_user["id"] == 1001
```

`yield` 前是准备，`yield` 后是清理。即使测试失败，pytest 通常仍会执行清理阶段。

## 7. fixture scope

```python
@pytest.fixture(scope="function")  # 每个测试一次，默认
@pytest.fixture(scope="class")     # 每个测试类一次
@pytest.fixture(scope="module")    # 每个文件一次
@pytest.fixture(scope="session")   # 整次运行一次
```

选择原则：

- 数据会被测试修改：使用 `function`；
- 创建代价高且可安全共享：考虑 `session`；
- 浏览器页面一般不要跨用例共享脏状态；
- 数据库事务和临时目录优先每条测试隔离。

## 8. conftest.py

多个测试共享 fixture 时，将其放到 `conftest.py`：

```python
import pytest
import requests


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "python-test-lab"})
    yield session
    session.close()
```

测试文件无需导入 `conftest.py`：

```python
def test_httpbin(api_session):
    response = api_session.get("https://httpbin.org/get", timeout=10)
    assert response.status_code == 200
```

## 9. 参数化

```python
import pytest


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
    ],
)
def test_add(left, right, expected):
    assert left + right == expected
```

给参数起名字：

```python
@pytest.mark.parametrize(
    ("username", "valid"),
    [
        pytest.param("alice", True, id="normal-user"),
        pytest.param("", False, id="empty-user"),
    ],
)
def test_username(username, valid):
    assert bool(username) is valid
```

参数化适合相同逻辑、不同输入，不适合把完全不同业务强塞进一条测试。

## 10. mark：测试分类

`pytest.ini`：

```ini
[pytest]
testpaths = tests
addopts = -ra
markers =
    smoke: 核心冒烟测试
    regression: 回归测试
    api: 接口测试
    web: 网页测试
```

用例：

```python
import pytest


@pytest.mark.smoke
@pytest.mark.api
def test_health():
    assert True
```

执行：

```powershell
python -m pytest -m smoke
python -m pytest -m "api and not regression"
```

## 11. skip 和 xfail

```python
import sys
import pytest


@pytest.mark.skip(reason="功能尚未开放")
def test_future_feature():
    pass


@pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 执行")
def test_windows_only():
    assert True


@pytest.mark.xfail(reason="已知缺陷 BUG-123")
def test_known_bug():
    assert 1 == 2
```

不要用 `xfail` 长期掩盖失败，必须写明缺陷编号和清理条件。

## 12. 临时目录和日志

```python
def test_write_file(tmp_path):
    result_file = tmp_path / "result.txt"
    result_file.write_text("success", encoding="utf-8")
    assert result_file.read_text(encoding="utf-8") == "success"
```

```python
import logging


def test_logging(caplog):
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.INFO):
        logger.info("operation completed")
    assert "operation completed" in caplog.text
```

## 13. 常见错误

`collected 0 items`：检查文件名和函数名是否以 `test_` 开头。

`fixture 'xxx' not found`：检查 fixture 名、`conftest.py` 位置和运行目录。

`PytestUnknownMarkWarning`：在 `pytest.ini` 注册 mark。

导入失败：从项目根目录运行 `python -m pytest`，不要在 `tests` 子目录里随意运行。

用例相互影响：检查全局变量、共享账号、缓存、浏览器状态和未清理数据。

## 14. 好用例的结构

```python
def test_create_user(api_client, unique_user_payload):
    # Arrange：准备
    payload = unique_user_payload

    # Act：执行
    response = api_client.create_user(payload)

    # Assert：验证
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["id"]
```

一条测试最好只有一个清晰目标。失败时应能立刻知道哪个业务行为出错。

## 15. 练习

- [ ] 编写 3 条加减法测试
- [ ] 用参数化覆盖正数、零和负数
- [ ] 编写 fixture 准备用户数据
- [ ] 使用 `tmp_path` 测试文件写入
- [ ] 注册并执行 `smoke` 标记
- [ ] 故意写错断言并阅读失败输出

## 16. 官方资料

- [pytest 入门](https://docs.pytest.org/en/stable/getting-started.html)
- [pytest 完整文档](https://docs.pytest.org/en/stable/contents.html)
