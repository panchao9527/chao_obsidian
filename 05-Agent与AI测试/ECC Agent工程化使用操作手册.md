---
title: ECC Agent工程化使用操作手册
date: 2026-09-10
updated: 2026-09-10
tags:
  - agent-testing
  - ai-engineering
  - codex
  - claude-code
  - ecc
  - security
aliases:
  - Everything Claude Code 使用指南
  - ECC 使用手册
status: active
level: intermediate
---

# ECC Agent工程化使用操作手册

> [!abstract] 文档定位
> ECC（Everything Claude Code）是一个面向 AI 编程助手的工程化配置与工作流集合。它将 Skills、专用 Agent、Rules、Hooks、记忆、验证循环和安全扫描组合起来，帮助 Agent 按“规划—测试—实现—审查—验证—沉淀”的方式完成任务。

> [!warning] 使用边界
> 本文以公开仓库当前文档为依据，重点覆盖 Codex 和 Claude Code 的本地开发、测试与知识沉淀场景。ECC 不是模型，也不会自动保证代码正确；生产环境、企业仓库和含敏感数据的项目必须经过人工审查、最小权限配置和独立验证。

## 1. 官方入口与版本信息

- GitHub：[affaan-m/ECC](https://github.com/affaan-m/ECC)
- 中文说明：[README.zh-CN.md](https://github.com/affaan-m/ECC/blob/main/README.zh-CN.md)
- 安全指南：[the-security-guide.md](https://github.com/affaan-m/ECC/blob/main/the-security-guide.md)
- 安全报告入口：[SECURITY.md](https://github.com/affaan-m/ECC/blob/main/SECURITY.md)
- 官方网站：[ecc.tools](https://ecc.tools/)

官方仓库目前将 ECC 描述为 Agent harness 的性能优化系统，包含专用 Agent、Skills、Commands、Hooks、Rules、Memory 和 AgentShield 等组件，并面向 Claude Code、Codex、Cursor、OpenCode、Gemini 等工具提供不同程度的适配。

> [!danger] 只使用官方来源
> 不要从不明镜像、复制粘贴站点或陌生压缩包安装 ECC。仓库 README 明确提醒，第三方重打包可能包含恶意代码。下载、安装和升级前，优先使用上面的 GitHub 仓库或官方 npm 包。

## 2. ECC 解决什么问题

普通的 Agent 使用方式通常是：

```text
描述需求 → Agent 修改代码 → 人工查看结果
```

ECC 希望把它变成可重复的工程流程：

```text
理解需求
  → 搜索现有代码与文档
  → 制定计划
  → 先写或确认测试
  → 实现最小改动
  → 运行验证
  → 重新审查 diff
  → 保存有价值的经验
```

项目 README 给出的核心循环是：

```text
plan → test → implement → review → verify → remember → improve
```

这套思路适合以下问题：

- Agent 经常跳过需求分析直接改代码；
- 同类任务每次都要重新解释检查清单；
- 测试、构建和安全审查容易被遗漏；
- 多次会话之间缺少项目上下文；
- Skills、Hooks、MCP 配置逐渐失控；
- Agent 给出“已完成”，但没有实际验证证据。

ECC 不能解决的问题包括：

- 不能替代真实业务验收；
- 不能把静态分析结果变成运行时证据；
- 不能保证第三方 Skill 或 MCP Server 安全；
- 不能替代代码审查、权限审批和生产变更流程；
- 不能自动判断测试数据是否适合企业环境。

## 3. 组件总览

| 组件 | 主要作用 | 适合什么时候使用 |
|---|---|---|
| `agents/` | 面向规划、审查、测试、构建、安全等职责的专用 Agent | 任务复杂、需要角色分工时 |
| `skills/` | 某类任务的可复用知识和操作流程 | 需要稳定复用工作方法时 |
| `rules/` | 长期生效的语言、项目和安全规范 | 每次任务都必须遵守的规则 |
| `commands/` | 便捷入口，兼容旧的命令式用法 | 快速触发计划、审查、修复等流程 |
| `hooks/` | 在命令、编辑、会话等生命周期节点自动触发动作 | 希望自动提醒或自动校验时 |
| `mcp-configs/` | MCP Server 配置示例 | 需要连接外部工具时 |
| `memory/` 或记忆运行时 | 保存跨会话的项目经验 | 有经过审查、值得复用的知识时 |
| AgentShield | 扫描 Prompt、Hooks、MCP、权限、Secrets 等风险 | 安装第三方 Agent 组件前 |

### 3.1 Agents 与 Skills 的区别

可以这样理解：

```text
Agent  = 谁来做
Skill  = 按什么方法做
Rule   = 必须遵守什么约束
Hook   = 什么时候自动检查
Command= 怎样快速启动
```

例如，处理一个 Spring Boot 接口变更时：

```text
planner             负责拆解需求
springboot-patterns 负责参考实现模式
springboot-tdd       负责测试驱动流程
java-reviewer        负责代码审查
security-review      负责安全检查
verification-loop    负责收集验证证据
```

## 4. 安装前准备

### 4.1 基础环境

官方当前说明中，通用安装流程需要 Node.js 18 或更高版本；具体 Harness 还需要满足自身版本要求。

Windows PowerShell 检查：

```powershell
node --version
npm --version
git --version
codex --version
```

如果使用 Claude Code：

```powershell
claude --version
```

### 4.2 先确定安装范围

安装前先回答三个问题：

1. 只想学习 Skills，还是要启用运行时 Hooks？
2. 只给某个项目使用，还是修改全局 Agent 配置？
3. 是否需要 MCP、记忆库或外部网络访问？

建议采用以下顺序：

```text
阅读仓库
  → 复制少量规则到实验项目
  → 在隔离配置中验证
  → 选择性启用插件
  → 最后才考虑全局 Hooks 和 Memory
```

### 4.3 建议建立回滚点

在安装前保存当前配置：

```powershell
$backup = Join-Path $env:TEMP ('ecc-config-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $backup | Out-Null

if (Test-Path "$HOME\.codex") {
    Copy-Item -Recurse -Force "$HOME\.codex" (Join-Path $backup 'codex')
}

if (Test-Path "$HOME\.claude") {
    Copy-Item -Recurse -Force "$HOME\.claude" (Join-Path $backup 'claude')
}

Write-Output "Backup: $backup"
```

> [!warning] 不要覆盖用户现有配置
> 不要在没有备份的情况下直接运行全量安装器，也不要同时运行插件安装、完整手动安装和旧版同步脚本。重复安装可能造成 Skills、Commands、Hooks 和配置重复加载。

## 5. Codex 推荐安装方式

ECC 当前为 Codex 提供原生插件市场安装路径。建议优先使用该方式，不要先执行旧的 `sync-ecc-to-codex.sh`。

### 5.1 添加 ECC 插件市场

```powershell
codex plugin marketplace add affaan-m/ECC
```

### 5.2 安装插件

```powershell
codex plugin add ecc@ecc
```

### 5.3 查看安装状态

```powershell
codex plugin list --json
```

### 5.4 验证插件缓存

如果已经在 ECC 仓库目录中：

```powershell
node scripts/codex/check-plugin-cache.js
```

如果插件没有出现，先执行：

```powershell
codex plugin marketplace upgrade ecc
codex plugin add ecc@ecc
```

### 5.5 在 Codex 中配置

安装完成后，使用 ECC 提供的配置入口：

```text
$configure-ecc
```

配置时只选择需要的功能。对于你的场景，建议优先选择：

- 代码搜索与规划；
- Python/Java 测试；
- API 与 E2E 测试；
- 安全审查；
- 验证循环；
- 文档和知识沉淀。

暂时不要启用：

- 自动修改生产配置；
- 自动执行未知脚本；
- 自动访问生产数据库；
- 未审查的远程 MCP；
- 会自动上传代码或日志的外部服务。

## 6. Claude Code 安装方式

如果使用 Claude Code，可以选择官方插件方式：

```text
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

或者使用通用 npm 安装器：

```powershell
npx ecc-universal setup
```

官方说明中，两种方式安装的是同一个 `ecc@ecc` 插件。选择一种即可，不要叠加完整手动安装。

如果只需要规则，可以手动复制：

```powershell
git clone https://github.com/affaan-m/ECC.git
Set-Location .\ECC

New-Item -ItemType Directory -Force -Path "$HOME\.claude\rules\ecc" | Out-Null
Copy-Item -Recurse rules\common "$HOME\.claude\rules\ecc\"
Copy-Item -Recurse rules\typescript "$HOME\.claude\rules\ecc\"
```

将 `typescript` 替换为实际技术栈目录。插件安装后，不要再运行完整的 `install.ps1 --profile full`。

## 7. 不推荐的新手安装方式

仓库仍保留旧的 Codex 同步脚本：

```powershell
git clone https://github.com/affaan-m/ECC.git
Set-Location .\ECC
npm install
bash scripts/sync-ecc-to-codex.sh
```

这条路径会复制并合并配置到 Codex 用户目录，适合明确知道自己为什么要使用兼容层的用户。

如果已经使用过旧同步方式，可先做预览：

```powershell
node scripts/ecc.js uninstall --legacy-codex-sync --dry-run
```

确认影响范围后再决定是否清理：

```powershell
node scripts/ecc.js uninstall --legacy-codex-sync
```

不要把原生插件安装和旧版同步叠加在同一个 Codex 配置中。

## 8. 第一次使用：从小任务开始

不要第一次就让 ECC 修改大型生产项目。建议新建一个临时项目：

```powershell
New-Item -ItemType Directory -Force -Path 'D:\ecc-lab' | Out-Null
Set-Location 'D:\ecc-lab'
git init -b main
```

准备一个简单任务，例如：

```text
请先不要修改代码。
阅读当前项目，给出：
1. 目录结构
2. 入口和调用链
3. 现有测试
4. 可能的风险
5. 最小实施计划
输出计划后等待确认。
```

确认计划后，再执行：

```text
根据刚才的计划实施，但遵守以下要求：
- 先补充最小测试
- 不修改无关文件
- 不使用真实密钥和生产数据
- 完成后运行目标测试
- 输出修改文件、测试命令和实际结果
```

### 8.1 常用工作入口

不同 Harness 的命令名称可能略有差异。Claude Code 插件路径通常使用命名空间：

```text
/ecc:plan "添加用户认证"
```

旧命令或手动安装路径可能使用：

```text
/plan "添加用户认证"
```

在 Codex 中优先使用 Skill、项目规则和自然语言任务描述，不要假设 Claude Code 的 slash command 在 Codex 中完全同名。

## 9. 面向测试自动化的推荐工作流

下面这套流程适合 Java 服务、Python API 自动化、Playwright 和 Agent 测试。

### 第一步：检索优先

```text
先搜索仓库中的：
- 测试入口
- 环境配置
- 数据准备函数
- API Client
- 断言工具
- 日志和报告目录
- CI 配置

不要先写代码。先列出已有能力和缺口。
```

对应思路是 ECC 的 `search-first`。

### 第二步：建立测试计划

要求 Agent 输出：

- 目标业务分支；
- 输入条件；
- 前置数据；
- 预期响应；
- 数据库或状态验证；
- 异常和边界场景；
- 可执行测试命令；
- 可能的环境依赖；
- 不在本次范围内的内容。

### 第三步：动态准备数据

对于接口自动化，明确要求：

```text
测试数据必须通过 debugtalk.py 或同等动态方式准备。
禁止依赖固定 UAT ID、固定员工、固定门店、固定任务和共享快照。
优先使用唯一前缀、可清理数据和稳定的空数据场景。
```

### 第四步：实现和验证

要求 Agent 同时给出：

- 修改文件列表；
- 关键分支覆盖点；
- 测试命令；
- 实际执行输出；
- 失败分类；
- 是否需要环境或 UAT 数据配合。

### 第五步：独立审查

让 Agent 在新的上下文中审查：

```text
请只审查当前 diff，不要修改文件。
重点检查：
1. 是否改变了无关行为
2. 是否有固定测试数据
3. 是否存在生产写入风险
4. 是否遗漏异常分支
5. 是否有只验证 HTTP 200、没有验证业务结果的问题
6. 测试失败时是否能区分代码、用例、数据和环境原因
```

### 第六步：收集证据

一份合格的测试结果至少应包括：

| 证据 | 内容 |
|---|---|
| 版本 | 分支、提交、依赖版本 |
| 输入 | 请求参数、前置条件、数据来源 |
| 执行 | 实际命令、时间、环境 |
| 结果 | 响应、业务断言、状态变化 |
| 失败 | 原始错误、定位层级、排除项 |
| 回归 | 目标测试和相关回归测试结果 |

## 10. 面向 Obsidian 和知识库的使用方式

ECC 的经验沉淀思想可以直接应用到 Obsidian，但不要把所有聊天记录原样保存。

建议每次任务只沉淀以下内容：

- 已验证的命令；
- 已确认的项目约束；
- 可复用的排错步骤；
- 稳定的测试数据策略；
- 失败原因和反例；
- 需要人工确认的风险；
- 对应源码、日志或执行证据。

推荐笔记结构：

```text
问题背景
前置条件
最小复现
定位路径
根因或当前结论
反证与排除项
修复或测试方案
执行证据
可复用经验
```

不要把以下内容写入公开仓库：

- 真实 API Key；
- Cookie、Token、密码；
- 生产域名和内部网络细节；
- 未脱敏日志；
- 客户、员工、发票和财务数据；
- 含页面内容、网络请求和源码的 Trace ZIP；
- 个人家目录下的完整 Agent 配置快照。

## 11. Hooks 的启用策略

Hooks 很有价值，但建议逐级启用：

### Level 1：人工触发

只使用 Skills 和 Rules，所有命令由用户确认执行。

适合刚开始学习、处理敏感项目时。

### Level 2：提醒型 Hooks

只做提醒和检查，例如：

- 提醒先运行测试；
- 提醒检查 diff；
- 提醒不要把密钥写入文件；
- 提醒使用隔离分支。

### Level 3：验证型 Hooks

自动运行：

- 格式化检查；
- 类型检查；
- 单元测试；
- Secret 扫描；
- Markdown 检查。

### Level 4：修改型 Hooks

让 Hook 自动修改代码、文件或配置前，必须确认：

- 作用目录；
- 备份方式；
- 是否可回滚；
- 是否可能触发生产操作；
- 是否会覆盖用户现有文件。

不建议在生产仓库直接启用 Level 4。

## 12. MCP 和外部工具安全

ECC 支持 MCP 配置，但 MCP 会扩大 Agent 的权限边界。

接入任何 MCP 前检查：

1. Server 来源是否可信；
2. 启动命令是否会下载或执行未知代码；
3. 是否需要读写本地文件；
4. 是否能访问浏览器 Cookie；
5. 是否会访问外部网络；
6. 是否把页面、日志或源码发送给第三方；
7. 是否有只读模式；
8. 是否可以限制到临时目录；
9. 是否需要单独的测试账号；
10. 是否有停用和卸载方法。

建议先使用：

```text
只读
低权限
测试数据
独立账号
隔离目录
可审计日志
```

不要因为某个 MCP 能“自动完成任务”，就直接授予它生产数据库、生产浏览器会话或企业凭据。

## 13. 安全扫描与人工审查

安装或升级 ECC 后，至少做以下检查：

```powershell
git status --short
git diff --check
git diff --stat
```

对仓库内容搜索常见敏感标记：

```powershell
git grep -n -I -E '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----|ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|password\s*[:=]|api[_-]?key\s*[:=]|access[_-]?token\s*[:=])'
```

再人工检查：

- `install.ps1`、`install.sh`；
- `hooks/`；
- `scripts/`；
- `.mcp.json`；
- `.claude-plugin/`；
- `.codex/`；
- `agents/` 中包含命令执行的文件；
- 任何会读取环境变量、浏览器数据或凭据的代码。

安全扫描的结果只能作为辅助证据。扫描通过不等于可以无审查地运行。

## 14. 更新、诊断和卸载

### 14.1 更新插件

Codex 原生插件可以按官方说明更新市场内容后重新添加：

```powershell
codex plugin marketplace upgrade ecc
codex plugin add ecc@ecc
codex plugin list --json
```

### 14.2 诊断

如果已经克隆 ECC 仓库，可尝试：

```powershell
node scripts/ecc.js list-installed
node scripts/ecc.js doctor
```

不要看到诊断命令成功就认为业务流程正确。仍然需要在目标项目运行实际的测试和验证命令。

### 14.3 卸载前预览

```powershell
node scripts/ecc.js uninstall --legacy-codex-sync --dry-run
```

任何卸载或修复动作都应先查看 dry-run 结果，避免误删自己维护的配置。

## 15. 常见问题

### Q1：是不是安装后所有 Agent 都会自动变强？

不是。ECC 提供了流程、规则和工具箱，但最终效果取决于模型、项目上下文、任务描述、权限边界和实际验证。它不能替代清晰需求和工程判断。

### Q2：为什么同一个 Skill 在不同工具里表现不同？

因为 Claude Code、Codex、Cursor、OpenCode 等 Harness 的插件、Hook、命令和上下文加载机制不同。ECC 提供的是适配层，不代表所有功能完全等价。使用前要查看仓库的 Platform Support 说明。

### Q3：能不能把全部 Skills 都装上？

技术上可能可以，但不建议。Skills 太多会增加上下文噪音，也可能让 Agent 在不相关任务中调用错误流程。应该按技术栈和工作类型选择最小集合。

### Q4：能不能把 Memory 当知识库？

不能完全等同。Memory 适合保存经过审查的短期或跨会话上下文；长期、正式、需要团队维护的知识，应进入项目文档、测试文档或 Obsidian 知识库。

### Q5：ECC 能不能自动做生产修数？

不建议。任何生产修数、任务重放、批处理和状态修改都必须有明确授权、只读分析、审批、回滚方案和执行证据。ECC 的自动化能力不能扩大业务操作权限。

## 16. 针对当前工作场景的落地方案

建议按以下顺序在你的工作流中吸收 ECC：

### 第一阶段：只借鉴方法

- 使用 `search-first` 的先检索后修改思想；
- 使用 `verification-loop` 的验证闭环；
- 使用 `security-review` 的安全检查清单；
- 使用 `tdd-workflow` 重新组织测试任务。

### 第二阶段：整理成自己的项目规则

将以下约束写入项目级 `AGENTS.md` 或测试文档：

```text
- 先定位代码和现有测试，再提出修改方案
- 测试数据动态准备，不依赖固定 UAT 数据
- 生产默认只读
- 不把 HTTP 200 当成业务成功
- 不把静态覆盖率缺口当成业务验收证据
- 失败必须区分代码、用例、数据和环境
- 只修改请求范围内的文件
- 提交前执行 diff、敏感信息和回滚检查
```

### 第三阶段：选择性安装

只引入与你当前工作最相关的组件：

- Java/Spring Boot 规则；
- Python 测试规则；
- E2E 测试 Skill；
- 安全审查 Skill；
- 验证循环 Skill；
- 文档和知识沉淀 Skill。

### 第四阶段：用真实但低风险的任务验证

建议先做：

1. 一个本地 Python API 测试用例；
2. 一个隔离的 Playwright 流程；
3. 一个 Java 服务的静态审查任务；
4. 一个测试文档整理任务。

暂时不要用 ECC 首次验证：

- 生产数据库；
- 生产浏览器登录态；
- 真实客户数据；
- 直接推送正式分支；
- 自动修改全局 Codex 配置。

## 17. 最小检查清单

安装前：

- [ ] 已确认官方仓库和版本
- [ ] 已备份当前 Codex/Claude 配置
- [ ] 已选择一个 Harness 的一种安装方式
- [ ] 已确认是否需要 Hooks、MCP、Memory
- [ ] 已准备隔离测试项目

安装后：

- [ ] 能查看插件安装状态
- [ ] 能执行一个只读规划任务
- [ ] 能使用一个测试相关 Skill
- [ ] 能查看实际执行结果
- [ ] 能检查 Hooks 和 MCP 配置
- [ ] 未出现重复命令或重复 Skill

交付前：

- [ ] 已检查 `git diff --check`
- [ ] 已检查敏感信息
- [ ] 已运行目标测试
- [ ] 已区分静态证据与运行证据
- [ ] 已确认修改文件范围
- [ ] 已保留可回滚提交

## 18. 参考资料

- [ECC GitHub 仓库](https://github.com/affaan-m/ECC)
- [ECC 中文 README](https://github.com/affaan-m/ECC/blob/main/README.zh-CN.md)
- [ECC 安全指南](https://github.com/affaan-m/ECC/blob/main/the-security-guide.md)
- [ECC 安全策略](https://github.com/affaan-m/ECC/blob/main/SECURITY.md)
- [Codex 插件安装说明](https://github.com/affaan-m/ECC#codex-app-and-cli)
- [Codex ECC 导航说明](https://github.com/affaan-m/ECC/blob/main/.codex/README.md)

> [!tip] 下一步
> 先在隔离项目中验证一个“先规划—再测试—再实现—最后验证”的小任务，再决定是否启用全局插件、Hooks 或 Memory。对于企业测试和生产相关仓库，建议优先吸收方法和规则，不要直接复制全部运行时配置。
