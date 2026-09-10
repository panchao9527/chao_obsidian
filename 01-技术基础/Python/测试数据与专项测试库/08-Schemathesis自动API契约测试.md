---
title: Schemathesis自动API契约测试
date: 2026-09-10
updated: 2026-09-10
tags: [python, schemathesis, api-testing, openapi]
status: active
level: intermediate
---

# Schemathesis自动API契约测试

## 1. 作用

Schemathesis 根据 OpenAPI/GraphQL Schema 自动生成请求，探索边界输入，检查服务是否出现异常状态、响应是否符合契约。

## 2. 安装

```powershell
# 安装命令行和 Python 运行时
python -m pip install schemathesis
# 查看当前版本支持的完整参数
schemathesis --help
```

## 3. 命令行运行

```powershell
# 根据远程 OpenAPI 文档自动生成并运行测试请求
schemathesis run https://example.test/openapi.json
```

需要测试 Token 时使用环境变量和工具支持的 Header 参数，禁止把真实 Token 写进仓库或 shell 历史。

## 4. 它能发现什么

- 必填字段缺失时返回 500；
- 数值边界处理错误；
- 响应结构不符合 OpenAPI；
- 未声明状态码；
- 错误输入导致未处理异常；
- Content-Type 不符合契约。

## 5. 使用前准备

确认测试环境允许自动生成请求，特别是 POST、PUT、PATCH、DELETE。对发邮件、支付、删数据等端点必须过滤、只读或使用隔离账号。

## 6. 结果判断

Schemathesis 失败是“发现契约或健壮性疑点”，仍要结合请求、响应、服务日志和业务规则判断。OpenAPI 本身错误时，自动测试也会沿着错误契约执行。

## 7. 推荐流程

```text
校验 OpenAPI
→ 先跑只读接口
→ 限制端点和样例数量
→ 检查失败反例
→ 与手工业务用例互补
→ 再纳入 CI
```

官方资料：[Schemathesis Documentation](https://schemathesis.readthedocs.io/)
