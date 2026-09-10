---
title: Locust性能测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, locust, performance-testing, load-testing]
status: active
level: intermediate
---

# Locust性能测试

## 1. 作用

Locust 使用 Python 描述并发用户行为，可通过 Web UI 或无头模式运行，观察吞吐量、响应时间和错误。适合 HTTP API 容量、稳定性和负载测试。

> [!danger] 压测必须授权
> 不要对生产、共享 SIT、第三方服务或未知容量环境直接发起负载。必须确认目标、时间窗口、并发上限、监控、停止条件和负责人。

## 2. 安装

```powershell
# 安装 Locust 并确认命令可用
python -m pip install locust
locust --version
```

## 3. 第一个 locustfile.py

```python
# HttpUser 表示使用 HTTP 客户端的虚拟用户
# task 标记用户会重复执行的业务动作
from locust import HttpUser, between, task


class ApiUser(HttpUser):
    # 每个任务之间随机等待 1 到 3 秒，模拟用户思考时间
    wait_time = between(1, 3)

    # 权重 3：相对于权重 1 的任务，执行频率约为 3 倍
    @task(3)
    def query_users(self):
        self.client.get("/api/users", name="GET /api/users")

    @task(1)
    def query_health(self):
        self.client.get("/health", name="GET /health")
```

启动：

```powershell
# 启动 Locust Web UI，并把相对请求路径拼到 host 后
locust -f locustfile.py --host https://example.test
```

浏览器打开 `http://localhost:8089`，输入用户数和启动速率。

## 4. 无头运行

```powershell
# 无头模式适合 CI：20 个用户，每秒启动 2 个，持续 2 分钟
locust -f locustfile.py `
  --host https://example.test `
  --headless `
  --users 20 `
  --spawn-rate 2 `
  --run-time 2m `
  --csv artifacts\locust
```

## 5. 业务失败判断

HTTP 200 也可能业务失败：

```python
@task
def query_tasks(self):
    # catch_response=True 允许根据业务正文手动判定成功或失败
    with self.client.get("/api/tasks", catch_response=True) as response:
        # 先检查 HTTP 状态
        if response.status_code != 200:
            response.failure(f"HTTP {response.status_code}")
            return

        # 再解析 JSON 并检查业务 code
        body = response.json()
        if body.get("code") != 0:
            response.failure(f"business code={body.get('code')}")
```

## 6. 登录和测试数据

```python
import os


class ApiUser(HttpUser):
    def on_start(self):
        # on_start 在每个虚拟用户开始运行时执行一次
        response = self.client.post(
            "/api/login",
            json={
                "username": os.environ["PERF_USER"],
                "password": os.environ["PERF_PASSWORD"],
            },
        )
        # 取出 Token 后写入当前虚拟用户的公共请求头
        token = response.json()["token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})
```

使用专用压测账号，日志不得输出 Token。写操作需要可控数据池和清理方案。

## 7. 关键指标

- RPS：每秒请求数；
- 并发用户：同时运行的虚拟用户；
- P50/P90/P95/P99：延迟分位数；
- Failure Rate：失败比例；
- 吞吐量：单位时间完成的业务量；
- 资源指标：CPU、内存、GC、线程池、连接池、数据库。

只有客户端响应时间，没有服务端监控，无法完整定位瓶颈。

## 8. 停止条件示例

```text
错误率 > 1%
P95 > 2 秒持续 5 分钟
数据库连接池耗尽
CPU > 90% 持续 5 分钟
出现数据污染或不可恢复写入
```

## 9. 常见误区

- 用用户数代替实际 RPS；
- 没有预热就记录结果；
- 在笔记本网络上推导服务容量；
- 测试脚本自身成为瓶颈；
- 数据全部命中缓存；
- 只看平均值，不看 P95/P99；
- 没有版本、环境和数据快照。

官方资料：[Locust Documentation](https://docs.locust.io/en/stable/)
