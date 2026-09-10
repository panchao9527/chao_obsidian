---
title: responses模拟HTTP接口
date: 2026-09-10
updated: 2026-09-10
tags: [python, requests, responses, mock]
status: active
level: intermediate
---

# responses模拟HTTP接口

## 1. 作用

responses 专门拦截 Python `requests` 发出的 HTTP 请求，适合单元测试超时、错误码和第三方服务，不发送真实网络请求。

## 2. 安装

```powershell
python -m pip install responses
```

## 3. 模拟 GET

```python
import requests
import responses


@responses.activate
def test_query_user():
    responses.get(
        "https://example.test/users/1",
        json={"id": 1, "name": "alice"},
        status=200,
    )

    response = requests.get("https://example.test/users/1", timeout=10)
    assert response.json()["name"] == "alice"
```

## 4. 模拟 POST 并验证请求

```python
@responses.activate
def test_create_user():
    responses.post("https://example.test/users", json={"id": 10}, status=201)

    response = requests.post(
        "https://example.test/users",
        json={"name": "alice"},
        timeout=10,
    )

    assert response.status_code == 201
    assert len(responses.calls) == 1
    assert b'"name": "alice"' in responses.calls[0].request.body
```

## 5. 模拟异常

```python
@responses.activate
def test_timeout():
    responses.get(
        "https://example.test/slow",
        body=requests.Timeout("timeout"),
    )

    with pytest.raises(requests.Timeout):
        requests.get("https://example.test/slow", timeout=1)
```

## 6. 使用边界

responses 适合验证客户端逻辑，不验证 DNS、TLS、网关、真实鉴权和服务端行为。至少保留少量真实 SIT/UAT 集成测试。

如果项目使用 `httpx`，考虑使用 [RESPX](https://lundberg.github.io/respx/)；不要混用不匹配的 Mock 库。

官方资料：[responses Documentation](https://github.com/getsentry/responses)
