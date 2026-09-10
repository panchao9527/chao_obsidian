---
title: requests接口测试基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - requests
  - api-testing
  - beginner
aliases:
  - requests小白教程
status: active
level: beginner
---

# requests接口测试基础

上一步：[[01-技术基础/Python/测试自动化基础/02-pytest测试框架基础|02-pytest测试框架基础]]

下一步：[[01-技术基础/Python/测试自动化基础/04-Selenium网页自动化基础|04-Selenium网页自动化基础]]

## 1. 先理解 HTTP

一次 HTTP 请求通常包含：

- URL：访问地址；
- Method：GET、POST、PUT、PATCH、DELETE；
- Headers：请求头，例如认证和内容类型；
- Query：URL 查询参数；
- Body：请求体；
- Cookie：会话信息。

响应通常包含：

- Status Code：HTTP 状态码；
- Headers：响应头；
- Body：响应正文；
- Elapsed：耗时；
- Cookies：服务端设置的 Cookie。

> [!warning] HTTP 200 不等于业务成功
> 接口可能返回 HTTP 200，但正文是 `{"code": 500, "message": "failed"}`。测试必须同时检查 HTTP 状态和业务字段。

## 2. 安装和第一个请求

```powershell
python -m pip install -U requests
```

```python
import requests

response = requests.get("https://httpbin.org/get", timeout=10)

print(response.status_code)
print(response.headers)
print(response.text)
print(response.json())
```

## 3. Response 常用属性

```python
response.status_code       # 状态码
response.text              # 解码后的文本
response.content           # 原始 bytes
response.json()            # JSON 转 Python 对象
response.headers           # 响应头
response.cookies           # Cookie
response.url               # 最终 URL
response.history           # 重定向历史
response.elapsed           # 请求耗时
response.encoding          # 文本编码
```

`response.json()` 能成功只说明正文是合法 JSON，不代表请求成功。

## 4. GET 查询参数

```python
import requests

params = {
    "keyword": "python",
    "page": 1,
    "size": 20,
}

response = requests.get(
    "https://httpbin.org/get",
    params=params,
    timeout=10,
)

assert response.status_code == 200
body = response.json()
assert body["args"]["keyword"] == "python"
```

不要手工拼接复杂查询字符串，使用 `params` 可自动编码。

## 5. POST JSON

```python
import requests

payload = {
    "name": "alice",
    "age": 20,
}

response = requests.post(
    "https://httpbin.org/post",
    json=payload,
    timeout=10,
)

assert response.status_code == 200
body = response.json()
assert body["json"] == payload
```

`json=payload` 会序列化 JSON 并设置适当的 Content-Type。

表单请求使用 `data=`：

```python
response = requests.post(
    "https://httpbin.org/post",
    data={"username": "alice"},
    timeout=10,
)
```

## 6. Headers 和鉴权

```python
import os
import requests

token = os.environ["TEST_API_TOKEN"]
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

response = requests.get(
    "https://example.test/api/users",
    headers=headers,
    timeout=10,
)
```

PowerShell 当前会话设置测试 Token：

```powershell
$env:TEST_API_TOKEN = 'replace-with-test-token'
```

> [!danger] 不要打印完整 Token
> 日志中最多保留前后少数字符，公开仓库中只能出现占位符。不要提交 `.env`。

Basic Auth：

```python
from requests.auth import HTTPBasicAuth
import requests

response = requests.get(
    "https://httpbin.org/basic-auth/user/passwd",
    auth=HTTPBasicAuth("user", "passwd"),
    timeout=10,
)
```

## 7. Session

Session 可以复用 Headers、Cookie 和底层连接：

```python
import requests

with requests.Session() as session:
    session.headers.update({"User-Agent": "python-test-lab"})
    first = session.get("https://httpbin.org/cookies/set/demo/yes", timeout=10)
    second = session.get("https://httpbin.org/cookies", timeout=10)
    assert second.json()["cookies"]["demo"] == "yes"
```

与 pytest 组合：

```python
import pytest
import requests


@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()
```

## 8. 超时

生产级请求几乎都应该指定 `timeout`：

```python
requests.get(url, timeout=10)
```

分别设置连接和读取超时：

```python
requests.get(url, timeout=(3.05, 10))
```

这不是整个下载过程的绝对总时长，而是连接和等待数据的超时控制。未设置时，Requests 默认可能一直等待。

## 9. 错误处理

```python
import requests

try:
    response = requests.get("https://httpbin.org/status/500", timeout=10)
    response.raise_for_status()
except requests.Timeout:
    print("请求超时")
except requests.ConnectionError:
    print("无法连接服务器")
except requests.HTTPError as error:
    print(f"HTTP 错误：{error.response.status_code}")
except requests.RequestException as error:
    print(f"其他请求错误：{error}")
```

测试负向场景时，不一定调用 `raise_for_status()`，可以直接断言预期错误码。

## 10. 文件上传和下载

上传：

```python
from pathlib import Path
import requests

file_path = Path("sample.txt")

with file_path.open("rb") as file_obj:
    response = requests.post(
        "https://httpbin.org/post",
        files={"file": (file_path.name, file_obj, "text/plain")},
        timeout=30,
    )

assert response.status_code == 200
```

流式下载：

```python
from pathlib import Path
import requests

target = Path("download.bin")

with requests.get("https://httpbin.org/bytes/1024", stream=True, timeout=30) as response:
    response.raise_for_status()
    with target.open("wb") as file_obj:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file_obj.write(chunk)
```

## 11. 重定向、代理和证书

查看重定向：

```python
response = requests.get(url, allow_redirects=True, timeout=10)
print(response.history)
```

代理示例：

```python
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}
response = requests.get(url, proxies=proxies, timeout=10)
```

不要通过 `verify=False` 长期绕过 HTTPS 证书错误。优先配置正确 CA：

```python
response = requests.get(url, verify="path/to/company-ca.pem", timeout=10)
```

## 12. 封装 ApiClient

```python
from typing import Any
import requests


class ApiClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", 10)
        return self.session.request(
            method,
            f"{self.base_url}/{path.lstrip('/')}",
            **kwargs,
        )

    def close(self) -> None:
        self.session.close()
```

不要在通用 Client 中偷偷断言所有接口必须返回 200；创建接口可能返回 201，删除可能返回 204，负向用例可能预期 400。

## 13. pytest 接口用例

```python
import pytest
import requests


@pytest.mark.api
def test_query_parameters():
    response = requests.get(
        "https://httpbin.org/get",
        params={"name": "alice"},
        timeout=10,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["args"]["name"] == "alice"
```

更完整的断言：

```python
assert response.status_code == 200
assert response.headers["Content-Type"].startswith("application/json")
body = response.json()
assert isinstance(body, dict)
assert body.get("code") == 0
assert body.get("message") == "success"
assert "data" in body
```

## 14. 动态测试数据

```python
from uuid import uuid4


def build_unique_user() -> dict:
    suffix = uuid4().hex[:8]
    return {
        "username": f"auto-{suffix}",
        "email": f"auto-{suffix}@example.test",
    }
```

动态数据可以减少固定数据被修改、被占用、被删除导致的偶发失败。创建的数据应有明确清理方式。

## 15. 日志脱敏

```python
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}


def sanitize_headers(headers: dict) -> dict:
    return {
        key: "***" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }
```

响应正文也可能包含手机号、邮箱、身份证、账号或财务信息，不要默认完整写入 Allure。

## 16. 常见错误

- `JSONDecodeError`：响应不是 JSON，先看状态码、Content-Type 和 `response.text`；
- `Timeout`：服务慢、网络不通或超时太小；
- `ConnectionError`：DNS、代理、VPN、证书或服务未启动；
- `401`：缺少认证、Token 过期或认证格式错误；
- `403`：身份有效但没有权限；
- `404`：路径、环境地址或资源 ID 错误；
- `415`：Content-Type 与请求体格式不匹配；
- 本地通过、CI 失败：检查代理、证书、环境变量、网络白名单和时区。

## 17. 练习

- [ ] GET 请求带两个查询参数
- [ ] POST JSON 并断言返回值
- [ ] 为所有请求设置超时
- [ ] 使用 Session 保存 Cookie
- [ ] 参数化测试 200、404、500
- [ ] 生成唯一测试用户名
- [ ] 对请求头进行脱敏后输出

## 18. 官方资料

- [Requests 安装](https://requests.readthedocs.io/en/latest/user/install/)
- [Requests Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [Requests 高级用法](https://requests.readthedocs.io/en/latest/user/advanced/)
