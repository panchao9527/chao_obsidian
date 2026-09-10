---
title: Python操作基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - beginner
  - automation
aliases:
  - Python小白入门
status: active
level: beginner
---

# Python操作基础

上一步：[[01-技术基础/Python/测试自动化基础/00-从零开始学习路线与环境搭建|00-环境搭建]]

下一步：[[01-技术基础/Python/测试自动化基础/02-pytest测试框架基础|02-pytest测试框架基础]]

## 1. 运行 Python 的三种方式

交互式运行：

```powershell
python
```

输入：

```python
print("Hello Python")
```

输入 `exit()` 退出。

运行脚本：

```powershell
python hello.py
```

运行模块：

```powershell
python -m pytest
```

`-m` 表示按照 Python 模块运行，能减少“命令装到了另一个 Python”这类环境问题。

## 2. 变量和常见类型

```python
name = "Alice"          # str 字符串
age = 20                # int 整数
price = 19.99           # float 小数
enabled = True          # bool 布尔值
result = None           # 暂无值
```

查看类型：

```python
print(type(name))
print(type(age))
```

类型转换：

```python
age_text = "20"
age = int(age_text)
price_text = str(19.99)
```

> [!warning] 用户输入永远是字符串
> `input()` 得到的是 `str`。做数学计算前要转换成 `int` 或 `float`。

## 3. 字符串

```python
username = "tester"
message = f"当前用户：{username}"

print(username.upper())
print(username.startswith("test"))
print("test" in username)
print(message)
```

常用清理：

```python
raw = "  success\n"
clean = raw.strip()
assert clean == "success"
```

## 4. List、Tuple、Dict、Set

列表：有顺序、可修改。

```python
users = ["alice", "bob"]
users.append("carol")
print(users[0])
print(len(users))
```

元组：有顺序、通常不修改。

```python
point = (10, 20)
x, y = point
```

字典：键值对，是接口测试中最常用的结构。

```python
user = {
    "id": 1001,
    "name": "alice",
    "active": True,
}

print(user["name"])
print(user.get("email"))          # 不存在时返回 None
print(user.get("email", "N/A")) # 提供默认值
```

集合：无重复元素。

```python
actual_roles = {"user", "admin", "user"}
assert actual_roles == {"user", "admin"}
```

## 5. 判断

```python
status_code = 200

if status_code == 200:
    print("请求成功")
elif status_code == 404:
    print("资源不存在")
else:
    print(f"其他状态：{status_code}")
```

常见比较：

```python
assert 200 <= status_code < 300
assert username != ""
assert "data" in {"code": 0, "data": []}
```

## 6. 循环

```python
users = ["alice", "bob", "carol"]

for user in users:
    print(user)
```

同时得到序号：

```python
for index, user in enumerate(users, start=1):
    print(index, user)
```

遍历字典：

```python
response = {"code": 0, "message": "success"}

for key, value in response.items():
    print(key, value)
```

`while` 适合次数不确定的循环，但必须保证能退出：

```python
attempt = 0

while attempt < 3:
    attempt += 1
    print(f"第 {attempt} 次")
```

## 7. 函数

```python
def build_user_payload(name: str, age: int = 18) -> dict:
    return {
        "name": name,
        "age": age,
    }


payload = build_user_payload("alice", age=20)
print(payload)
```

函数的作用：

- 避免重复代码；
- 给一段操作命名；
- 方便测试；
- 隔离变化。

测试代码中，不要写一个几百行的大函数，应拆成“准备数据、调用接口、验证结果、清理数据”。

## 8. 异常处理

```python
try:
    value = int("abc")
except ValueError as error:
    print(f"转换失败：{error}")
```

网络代码常见结构：

```python
import requests

try:
    response = requests.get("https://httpbin.org/get", timeout=10)
    response.raise_for_status()
except requests.Timeout:
    print("请求超时")
except requests.RequestException as error:
    print(f"请求失败：{error}")
```

不要这样写：

```python
try:
    do_something()
except Exception:
    pass
```

它会吞掉真实错误，使测试看起来像成功。

## 9. 文件和路径

推荐使用 `pathlib`：

```python
from pathlib import Path

project_root = Path(__file__).resolve().parent
data_file = project_root / "data" / "users.json"

print(data_file)
print(data_file.exists())
```

写入文本：

```python
from pathlib import Path

Path("result.txt").write_text("测试通过", encoding="utf-8")
```

读取文本：

```python
content = Path("result.txt").read_text(encoding="utf-8")
print(content)
```

## 10. JSON

```python
import json

payload = {"name": "alice", "active": True}
text = json.dumps(payload, ensure_ascii=False, indent=2)
print(text)

restored = json.loads(text)
assert restored["name"] == "alice"
```

文件读写：

```python
from pathlib import Path
import json

path = Path("user.json")
path.write_text(
    json.dumps({"id": 1, "name": "测试用户"}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

user = json.loads(path.read_text(encoding="utf-8"))
```

## 11. 模块和导入

`utils/data_factory.py`：

```python
from uuid import uuid4


def unique_name(prefix: str = "auto") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"
```

其他文件使用：

```python
from utils.data_factory import unique_name

print(unique_name("user"))
```

如果出现 `ModuleNotFoundError`：

1. 确认虚拟环境已经激活；
2. 确认从项目根目录执行；
3. 确认包已安装到当前环境；
4. 用 `python -m pytest` 代替裸 `pytest`；
5. 不要随意修改 `sys.path` 掩盖目录设计问题。

## 12. 类的最小理解

```python
class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"


client = ApiClient("https://example.com/")
assert client.build_url("/users") == "https://example.com/users"
```

- `class` 定义一种对象；
- `__init__` 创建对象时执行；
- `self` 表示当前对象；
- 方法是对象拥有的函数。

## 13. 日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.info("开始执行测试")
```

日志不要输出密码、Token、Cookie 和完整个人信息。

## 14. 环境变量

PowerShell 当前会话设置：

```powershell
$env:TEST_BASE_URL = 'https://httpbin.org'
```

Python 读取：

```python
import os

base_url = os.getenv("TEST_BASE_URL", "https://httpbin.org")
```

清理：

```powershell
Remove-Item Env:TEST_BASE_URL
```

## 15. 调试方法

最简单的断点：

```python
breakpoint()
```

运行到断点后常用命令：

```text
p variable_name  查看变量
n                执行下一行
c                继续运行
q                退出调试
```

## 16. 练习

- [ ] 写一个函数生成唯一用户名
- [ ] 创建包含 3 个用户的列表并遍历
- [ ] 将用户数据写入 JSON 后再读取
- [ ] 从环境变量读取测试地址
- [ ] 故意触发 `ValueError` 并正确捕获

## 17. 官方资料

- [Python 官方教程](https://docs.python.org/3/tutorial/)
- [Python 标准库](https://docs.python.org/3/library/)
