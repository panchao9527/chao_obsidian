---
title: test-mcp 断言、Trace 与异常场景
date: 2026-09-02
updated: 2026-09-02
tags:
  - testing
  - agent-testing
  - mcp
  - trace
  - assertions
aliases:
  - test-mcp 调试与断言
status: active
level: intermediate
---

# 断言、Trace 与异常场景

上一步：[[03-Agent与AI测试/工具实战/test-mcp/02-test-mcp 安装与第一个测试|02-test-mcp 安装与第一个测试]]  
下一步：[[03-Agent与AI测试/工具实战/test-mcp/04-安全测试与 CI 回归|04-安全测试与 CI 回归]]

## 1. 从“能调用”升级到“调用正确”

一个业务场景不要只写：

```yaml
- assert: "The task succeeded"
```

这太模糊。更好的断言应包含关键事实：

```yaml
- assert: >-
    The create_order tool was called before cancel_order,
    cancel_order used the order ID returned by create_order,
    and the final reported status was cancelled.
```

断言要覆盖：

- 工具名；
- 调用顺序；
- 关键参数来源；
- 工具返回结果；
- 最终业务状态；
- 失败时不得宣称成功。

## 2. 多轮场景模板

```yaml
description: "Create and cancel an order"

steps:
  - prompt: >-
      Create one test order for product DEMO-001 with quantity 1.
      Do not create any other order.
  - prompt: >-
      Cancel the order you just created. Use the ID returned by the tool,
      not an ID guessed from the conversation.
  - assert: >-
      Exactly one order was created, the same order was cancelled,
      and the final status reported by the tools is cancelled.
```

> [!warning] 这是通用设计示例
> 只有你的 MCP Server 真正提供对应工具时才能运行。测试前先在交互模式确认工具名称、输入 schema 和返回结构。

## 3. 使用 Trace

```powershell
test-mcp `
  --config test-mcp.config.json `
  --tests-dir .\tests `
  --trace
```

分析 Trace 时按顺序回答：

1. 配置加载了哪些 MCP Servers？
2. Agent 看到哪些工具及 schema？
3. 每轮 Prompt 后模型选择了什么工具？
4. 实际参数是什么？
5. 工具返回成功、业务失败，还是 Transport 失败？
6. Agent 是否忠实使用工具结果？
7. 断言依据了什么上下文？

`--trace` 会在 `traces/` 下写入 `mcp-trace-<timestamp>.jsonl`。记录可能包含 LLM 元数据、MCP 工具信息、错误和完整 Tool Call 参数。

> [!danger] Trace 默认不会替你脱敏
> 当前源码没有通用的 Trace 参数脱敏层。账号、个人数据、Token 或业务敏感字段一旦进入工具参数，就可能写进 JSONL。Trace 目录应加入 `.gitignore`，并只用合成测试数据。

## 4. 四类假阳性

| 假阳性 | 表现 | 防范 |
|---|---|---|
| 文本假阳性 | Agent 说成功，工具没调用 | Trace 检查 Tool Call |
| 工具假阳性 | 工具返回 OK，业务未落地 | 查询最终业务状态 |
| 上下文假阳性 | 取消了错误对象 | 断言 ID 传递链 |
| 评估假阳性 | LLM 误判自然语言断言 | 加确定性断言/人工抽检 |

## 5. 必测异常场景

### 工具不存在

Prompt 要求一个未提供的能力，期望 Agent 明确说明无法完成，不得伪造结果。

### 参数非法

传入缺失必填字段、错误类型、越界值或非法枚举，期望工具拒绝且 Agent 解释真实错误。

### Transport 失败

临时指向不可用的本地/测试 Server，期望显示连接错误或超时，不得返回业务成功。

### 多个相似工具

同时提供只读查询与写入工具，验证 Agent 是否选择最小权限工具。

### 工具部分成功

第一步成功、第二步失败，期望 Agent 报告部分完成并给出可恢复信息，不重复制造副作用。

## 6. 稳定性策略

Agent 测试天生包含模型波动。建议：

- Prompt 指明目标、约束和完成条件；
- 测试数据使用唯一前缀，避免并发冲突；
- 固定模型配置并记录模型版本/名称；
- 核心场景连续运行多次观察波动；
- 只对 Transport 短暂失败做有限重试；
- 不用重试掩盖稳定复现的工具/业务错误；
- 用 API 或只读数据源补最终状态断言。

## 7. 当前测试发现边界

官方当前只执行 `tests/` 目录下以 `.test.yaml` 结尾的文件；递归发现和完整 Glob 仍在计划中。因此先保持平铺：

```text
tests/
├─ smoke-dice.test.yaml
├─ order-create.test.yaml
├─ order-cancel.test.yaml
└─ security-no-permission.test.yaml
```

## 本章验收

- [ ] 能把模糊断言改成包含工具、顺序、参数和状态的断言
- [ ] 能用 `--trace` 找到工具调用链
- [ ] 能识别四类假阳性
- [ ] 至少跑过工具不存在、参数非法、Transport 失败三类异常
- [ ] 对关键业务增加了确定性最终状态校验

官方依据：[test-mcp README - CLI flags and test discovery](https://github.com/loadmill/test-mcp#-cli-flags)
