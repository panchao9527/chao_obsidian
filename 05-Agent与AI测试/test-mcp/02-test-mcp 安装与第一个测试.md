---
title: test-mcp 安装与第一个测试
date: 2026-09-02
updated: 2026-09-02
tags:
  - testing
  - agent-testing
  - mcp
  - test-mcp
  - nodejs
aliases:
  - test-mcp Quick Start
status: active
level: beginner
---

# test-mcp 安装与第一个测试

上一步：[[03-Agent与AI测试/工具实战/test-mcp/01-Agent E2E 测试核心概念|01-Agent E2E 测试核心概念]]  
下一步：[[03-Agent与AI测试/工具实战/test-mcp/03-断言、Trace 与异常场景|03-断言、Trace 与异常场景]]

## 1. 环境要求

`test-mcp` 的 package engine 是 Node.js 18.17 或更高版本，但很多 MCP Server 要求 Node.js 20。官方建议使用 Node.js 20。

```powershell
node --version
npm --version
git --version
```

## 2. 两种安装方式

### 方式 A：全局安装

```powershell
npm install -g @loadmill/test-mcp
test-mcp --help
```

也可以使用：

```powershell
pnpm add -g @loadmill/test-mcp
```

适合在自己的独立测试目录中编写配置与用例。

### 方式 B：从源码运行官方 Demo

```powershell
Set-Location 'D:\test-lab'
git clone https://github.com/loadmill/test-mcp.git
Set-Location '.\test-mcp'
npm install
npm run build
```

源码方式便于查看官方 Dice Server、配置和混合 Transport 测试。

## 3. 设置模型密钥

OpenAI 示例：

```powershell
$env:OPENAI_API_KEY = 'replace-with-your-test-key'
```

Anthropic 示例：

```powershell
$env:ANTHROPIC_API_KEY = 'replace-with-your-test-key'
```

> [!danger] 不要把真实值写进教程或提交 Git
> 官方源码示例也支持 `.env`，但对初学实验更建议只在当前 PowerShell 会话设置环境变量。使用完关闭终端或执行 `Remove-Item Env:OPENAI_API_KEY`。

## 4. 配置 STDIO 与 HTTP MCP

仓库根目录官方配置 `test-mcp.config.json` 同时连接本地 Dice Server 和远程 HTTP Server：

```json
{
  "mcpClient": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key": "${env:OPENAI_API_KEY}"
  },
  "mcpServers": {
    "dice": {
      "type": "stdio",
      "command": "node",
      "args": ["examples/dice-mcp-server.js"]
    },
    "remoteMCP": {
      "type": "http",
      "url": "https://mcp.remote-mcp.com"
    }
  }
}
```

说明：

- STDIO Server 由 test-mcp 按 `command + args` 启动；
- HTTP Server 通过 URL 连接；
- `${env:OPENAI_API_KEY}` 从环境变量读取；占位符必须占据整个字符串，变量缺失或为空会直接报错；
- `gpt-4o-mini` 是仓库当前示例值，不代表你的账号一定可用；如 Provider 拒绝模型，应依据项目当前兼容性与账号权限调整。

Anthropic 示例把 Provider 改为 `anthropic`，密钥用 `${env:ANTHROPIC_API_KEY}`。官方示例文件：[`examples/test-mcp-anthropic.config.json`](https://github.com/loadmill/test-mcp/blob/master/examples/test-mcp-anthropic.config.json)。

## 5. 认识本地 Dice Server

官方 Demo 注册一个无参数工具：

```text
工具名：rollDice
输入：无
输出：1～6 的文本数字
Transport：STDIO
```

这很适合入门，因为没有数据库、账号和副作用。

## 6. 编写第一个测试

README/官网写默认读取 `mcp.config.json`，但当前 CLI 源码实际默认 `test-mcp.config.json`，仓库根目录也使用后者。为避免版本/文档差异，本教程始终显式传 `--config`。测试发现只扫描指定目录第一层中以 `.test.yaml` 结尾的文件。

创建 `tests/dice-only.test.yaml`：

```yaml
description: "Local dice MCP smoke test"

steps:
  - prompt: "Use the rollDice tool exactly once and tell me the result"
  - assert: "The rollDice tool was called and returned an integer from 1 through 6"
```

运行：

```powershell
test-mcp --config test-mcp.config.json --tests-dir .\tests
```

从源码运行：

```powershell
node build/index.js --config test-mcp.config.json --tests-dir .\tests
```

> [!note] 官方混合 Demo 会访问远程 MCP
> `test-mcp.config.json` 还配置了 `https://mcp.remote-mcp.com`。只想做本地实验时，可以复制一份配置并删除 `remoteMCP`，避免外部网络成为失败变量。

## 7. 交互模式

先用交互模式确认 Agent 能发现工具：

```powershell
test-mcp --config test-mcp.config.json --interactive
```

输入类似：

```text
List the MCP tools you can use, then roll the dice once.
```

交互模式适合探索；正式回归仍应写成 `.test.yaml`。

## 8. 常见错误

| 现象 | 先检查 |
|---|---|
| 401/模型调用失败 | 环境变量、Provider、模型权限 |
| 找不到配置 | 默认名是 `mcp.config.json`，或使用 `--config` |
| 没发现测试 | 文件是否直接位于 tests 目录并以 `.test.yaml` 结尾 |
| STDIO Server 启动失败 | `command`、相对路径、Node 版本、依赖安装 |
| HTTP MCP 连接失败 | URL、网络、认证、Server 是否可用 |

## 本章验收

- [ ] 能运行 `test-mcp --help`
- [ ] 能解释配置中 Provider、STDIO、HTTP 三部分
- [ ] 能运行本地 Dice MCP 测试
- [ ] 能使用交互模式发现工具
- [ ] 密钥没有写进配置文件和 Git

官方依据：[test-mcp README](https://github.com/loadmill/test-mcp)
