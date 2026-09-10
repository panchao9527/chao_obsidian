---
title: Agent Skill 从本地整理到 GitLab 发布完整流程
date: 2026-08-26
tags:
  - skill
  - gitlab
  - kiro
  - codex
  - fct
  - knowledge-management
aliases:
  - Skill 发布流程
  - FCT Skill GitLab 发布
status: completed
---

# Agent Skill 从本地整理到 GitLab 发布完整流程

本文记录如何将一个本地 Agent Skill 整理成可供团队复用的 GitLab 仓库，并说明同事如何在 Kiro、Codex 或其他兼容 Agent Skills 的客户端中安装和使用。

本文以 `fct-ops-troubleshoot` 为例，但发布流程可以复用于其他 Skill。

> [!info] 当前发布地址
> [fct-ops-troubleshoot GitLab 仓库](https://gitlab-ex.mcd.com.cn/cn-chaopanod/fct-ops-troubleshoot)
>
> 默认分支：`main`

## 一、完整链路概览

```mermaid
flowchart LR
    A[审查本地 Skill] --> B[整理通用目录结构]
    B --> C[补充使用与环境文档]
    C --> D[校验并扫描敏感信息]
    D --> E[创建空 GitLab 项目]
    E --> F[推送 main 分支]
    F --> G[同事安装 Skill]
    G --> H[按项目补充环境映射]
    H --> I[通过 MR 持续维护]
```

核心原则是：

- GitLab 仓库保存可共享、可审查的 Skill 本体。
- 项目差异放在各项目自己的配置中，不硬编码到共享 Skill。
- MCP 名称可以不同，重要的是提供等价能力。
- 默认执行只读排查；评论、修数、写库等操作必须单独授权。
- 仓库中不得出现账号、密码、Token、Cookie、生产数据或一次性修数参数。

## 二、发布前整理 Skill

### 2.1 推荐目录结构

```text
fct-ops-troubleshoot/
├─ SKILL.md
├─ README.md
├─ adapters/
│  └─ codex/
│     └─ openai.yaml
├─ docs/
│  ├─ CLIENTS.md
│  └─ ENVIRONMENT.md
├─ references/
├─ scripts/
│  └─ mapper_columns.py
├─ .gitignore
└─ .gitattributes
```

各目录职责：

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 所有客户端共用的 Skill 入口和核心规则 |
| `README.md` | 面向使用者的安装、使用和仓库说明 |
| `references/` | FCT 业务知识、排查手册和证据规则 |
| `scripts/` | 可复用的辅助脚本，不存放一次性修数脚本 |
| `docs/CLIENTS.md` | Kiro、Codex 和其他客户端的安装差异 |
| `docs/ENVIRONMENT.md` | 项目适配方式、环境能力及 MCP 映射 |
| `adapters/codex/openai.yaml` | 可选的 Codex 展示元数据，不是第二份 Skill |
| `.gitignore` | 排除本地配置、缓存、密钥和构建产物 |
| `.gitattributes` | 统一 Markdown、YAML、Python 等文本文件的换行符 |

> [!important] 单一入口
> 仓库根目录的 `SKILL.md` 是唯一的 Skill 入口。不要再复制一份内容不同的 Kiro 版或 Codex 版，否则后续很容易出现规则不一致。

### 2.2 Kiro 优先、同时保持通用

Kiro 可以直接发现符合 Agent Skills 结构的根目录 `SKILL.md`。其他客户端只要支持以下能力，也可以使用：

- 能读取根目录 `SKILL.md`；
- 能解析其 YAML frontmatter 中的 `name` 和 `description`；
- 能读取 `references/` 中的相对路径文件；
- 能按需运行 `scripts/` 中的 Python 脚本。

`adapters/codex/openai.yaml` 只用于 Codex 中更友好的名称、描述和默认提示展示。Kiro 和其他客户端可以忽略该目录。

### 2.3 通用知识与项目差异分离

共享 Skill 中可以保留：

- 排查流程和证据标准；
- FCT 领域知识；
- 只读权限边界；
- 输出格式与脱敏规则；
- 各类能力缺失时的降级方式。

以下信息应由各项目自己维护：

- 本地代码仓库路径；
- SIT、UAT 和生产部署分支或提交；
- 当前客户端的 MCP 服务名称；
- 数据库、ELK、业务 ES 的访问权限；
- 项目特有的表、索引、服务名和环境差异。

Kiro 项目可将这些信息写到 `.kiro/steering/fct-environment.md`。其他客户端使用自己的项目级配置即可。

示例：

```markdown
# FCT repository and capability mapping

- Jira 读取：公司 Jira MCP，只读
- Jira 评论：默认关闭，用户明确确认后才能调用
- SIT/UAT 数据库：项目对应只读 SQL MCP
- 生产数据库：只读查询，禁止写入
- ELK：提供索引查询和上下文日志检索
- FCT 业务 ES：仅在 SAP GL、台账等场景启用
- 代码仓库：列出本项目真实的本地路径
- 已部署版本：记录环境对应分支或 commit
```

> [!warning] 不适用于所有业务项目
> `fct-ops-troubleshoot` 包含 FCT 领域知识。非 FCT 项目不应原样套用，应复制通用发布结构并替换业务知识和排查规则。

### 2.4 文档去重

同一信息只维护一处：

- 客户端安装说明统一放在 `docs/CLIENTS.md`；
- MCP 和环境能力统一放在 `docs/ENVIRONMENT.md`；
- `README.md` 只提供摘要和链接；
- 不再单独维护内容重复的 `docs/MCP_REQUIREMENTS.md`。

这样可以避免改了一个文件、忘记同步另一个文件。

## 三、MCP 与运行能力要求

安装 Skill 本身不要求固定名称的 MCP。不同同事、不同客户端可以使用不同名称，只要提供等价能力。

### 3.1 常规 FCT 工单排查建议能力

| 能力 | 用途 | 是否必需 |
|---|---|---|
| Jira 读取 | 获取工单描述、附件和历史记录 | 工单排查需要 |
| Recon 数据库只读查询 | 对账、支付和追票问题 | 按场景需要 |
| Collaboration 数据库只读查询 | 协同任务、节点和状态问题 | 按场景需要 |
| Basicdata 数据库只读查询 | 主数据、供应商和基础配置问题 | 按场景需要 |
| 生产数据库只读查询 | 核实生产状态 | 仅授权人员按需使用 |
| ELK 搜索与上下文查询 | 定位异常日志和调用链 | 线上异常建议提供 |
| 本地代码读取与搜索 | 将报错对应到源码逻辑 | 建议提供 |
| FCT 业务 ES | SAP GL、台账等业务查询 | 特定场景需要 |
| 代码图谱 | 跨仓库调用链分析 | 可选增强 |
| Jira 评论写入 | 将结论回填工单 | 可选，默认关闭 |

GitLab MCP 不是 Skill 运行时的必要条件。发布和更新仓库可以直接使用 Git 命令完成。

> [!caution] 最小权限
> 不要为了“配齐能力”给所有同事开放全部生产权限。应按职责分配最小只读权限；写库、修数、工单评论等能力必须单独控制。

当某项能力不可用时，Skill 应明确标记“证据缺失”以及需要用户补充的材料，不能把“无法查询”写成“系统中没有数据”。

## 四、发布前检查

### 4.1 内容检查

确认仓库中不存在：

- 真实 Jira 工单号、任务号、发票号和业务流水号；
- 用户名、邮箱、Token、Cookie、密码、证书和数据库连接串；
- 维护者电脑上的绝对路径；
- 生产写 SQL、一次性修数参数或绕过审批的说明；
- 只适用于某个维护者个人环境的 MCP 名称，却没有通用解释。

### 4.2 自动校验

在 Skill 根目录执行：

```powershell
python -X utf8 <skill-creator目录>\scripts\quick_validate.py .
python -X utf8 .\scripts\mapper_columns.py --help
git diff --check
git fsck --full
```

还应搜索敏感关键词和个人路径，例如：

```powershell
rg -n -i "token|cookie|password|secret|authorization|C:\\Users\\" .
```

命中并不一定代表泄密，但每一处都要人工确认。

## 五、创建 GitLab 项目

在 GitLab 的 **New project → Blank project** 页面填写：

| 字段 | 建议值 |
|---|---|
| Project name | `fct-ops-troubleshoot` |
| Project slug | `fct-ops-troubleshoot` |
| Namespace | 优先选择团队 Group；没有时可先放个人空间 |
| Description | `FCT 运维工单与线上异常的只读证据化排查 Skill，适用于 Kiro 及兼容 Agent Skills 的客户端。` |
| Visibility | 团队内部复用选 `Internal`；需逐人授权选 `Private` |

> [!warning] 不要勾选 Initialize repository with a README
> 本地仓库已经有完整提交历史。如果 GitLab 先生成 README，会产生两套不相干的提交历史，首次推送时需要额外合并。

## 六、推送本地仓库

本例的本地发布目录：

```text
D:\fctproject\gitlab-release\fct-ops-troubleshoot
```

进入目录后执行：

```powershell
git remote add origin https://gitlab-ex.mcd.com.cn/cn-chaopanod/fct-ops-troubleshoot.git
git push -u origin main
```

使用 HTTPS 推送时不需要配置 SSH key。若公司 GitLab 要求凭据，按浏览器或凭据管理器提示登录即可。

推送后验证：

```powershell
git status --short --branch
git remote -v
git ls-remote --heads origin main
```

检查 GitLab 页面应能看到 `SKILL.md`、`README.md`、`references/`、`scripts/`、`docs/` 和可选适配器目录。

本次整理后的关键提交包括：

```text
9a3ce07 Initial release of FCT operations troubleshooting skill
224b7d6 Make skill portable with Kiro-first Agent Skills layout
04d9282 Document MCP requirements and project setup
f5e0f20 Consolidate MCP guidance into environment docs
```

其中最后一次提交删除了重复的 MCP 文档，将说明统一合并到 `docs/ENVIRONMENT.md`。

## 七、同事如何安装和使用

### 7.1 Kiro 项目级安装（推荐团队项目使用）

在目标项目根目录执行：

```powershell
git submodule add https://gitlab-ex.mcd.com.cn/cn-chaopanod/fct-ops-troubleshoot.git .kiro/skills/fct-ops-troubleshoot
git commit -m "Add FCT troubleshooting skill"
```

优点：

- 项目成员使用相同 Skill 版本；
- Skill 版本随项目提交记录固定；
- 更新可以通过 submodule 提交进行审查。

使用时在 Kiro 中输入：

```text
/fct-ops-troubleshoot
```

或直接描述 FCT 工单、任务卡住、线上报错、状态不同步、日志或数据库排查需求，由客户端根据 `description` 自动选择 Skill。

### 7.2 Kiro 用户级安装

适合个人在多个项目中复用：

```powershell
$kiroSkillRoot = Join-Path $env:USERPROFILE ".kiro\skills"
New-Item -ItemType Directory -Force -Path $kiroSkillRoot | Out-Null
git clone https://gitlab-ex.mcd.com.cn/cn-chaopanod/fct-ops-troubleshoot.git `
  (Join-Path $kiroSkillRoot "fct-ops-troubleshoot")
```

Kiro 默认 Agent 会自动发现 Skill。如果自定义 Agent 禁用了默认资源或没有发现 Skill，可在 Agent 配置中显式加入：

```json
{
  "name": "fct-ops-agent",
  "resources": [
    "skill://.kiro/skills/*/SKILL.md",
    "skill://~/.kiro/skills/*/SKILL.md"
  ]
}
```

使用 `/context show` 检查 Skill 是否被发现。Kiro Skills 文档见 [Kiro Agent Skills](https://kiro.dev/docs/skills/)。

### 7.3 Codex 安装

Codex 本地安装通常将仓库克隆到：

```text
%CODEX_HOME%\skills\fct-ops-troubleshoot
```

如果未单独设置 `CODEX_HOME`，通常可放到：

```text
%USERPROFILE%\.codex\skills\fct-ops-troubleshoot
```

不同 Codex 发行方式的目录约定可能变化，应以当前客户端实际的 `CODEX_HOME` 和 Skills 设置为准。

使用时输入：

```text
$fct-ops-troubleshoot
```

`adapters/codex/openai.yaml` 是可选展示元数据。如果当前 Codex 版本需要，可在安装副本中复制到 `agents/openai.yaml`；不要因此维护另一份 `SKILL.md`。

### 7.4 其他客户端

其他客户端需要支持 Agent Skills 或提供等价加载方式：

1. 将仓库克隆到客户端的 Skills 搜索目录；
2. 确认客户端能够读取根目录 `SKILL.md`；
3. 配置该项目实际可用的 Jira、数据库、ELK、业务 ES 和代码检索能力；
4. 在项目级配置中填写真实仓库路径与环境差异；
5. 先使用无敏感数据的测试工单验证只读排查流程。

## 八、不同项目如何适配

同事的项目通常与维护者项目不同，不能把本机配置一并复制过去。

每个接入项目至少确认：

1. 这个项目是否属于 FCT 业务范围；
2. 工单来源和 Jira 项目标识是什么；
3. 涉及哪些服务和代码仓库；
4. SIT、UAT、生产分别部署了哪个版本；
5. 可以使用哪些只读数据库；
6. ELK 索引、时间字段和 trace 字段是什么；
7. 是否需要 FCT 业务 ES；
8. 哪些能力不可用，以及如何由用户提供替代证据；
9. 谁可以批准 Jira 评论、修数或其他写操作。

项目配置只保存映射和说明，不保存凭据。Token、Cookie、数据库密码、证书等必须由公司批准的凭据系统或本机受控配置提供。

## 九、后续更新与团队协作

不要直接修改个人安装目录后就视为团队版本。共享仓库是唯一可信来源，建议使用分支和 Merge Request：

```powershell
git checkout -b docs/update-environment-guide
# 修改 SKILL.md、references、scripts 或 docs
python -X utf8 <skill-creator目录>\scripts\quick_validate.py .
git diff --check
git add SKILL.md README.md docs references scripts
git commit -m "Update environment guidance"
git push -u origin docs/update-environment-guide
```

然后在 GitLab 创建 Merge Request，重点审查：

- 是否改变了权限边界；
- 是否引入真实生产数据或凭据；
- 是否将项目特例误写成通用规则；
- 是否与已有文档重复；
- 是否说明能力缺失时的降级方式；
- 示例是否已脱敏；
- Python 脚本和 Markdown 校验是否通过。

项目级 submodule 用户更新版本时执行：

```powershell
git submodule update --remote .kiro/skills/fct-ops-troubleshoot
git add .kiro/skills/fct-ops-troubleshoot
git commit -m "Update FCT troubleshooting skill"
```

个人 clone 用户更新版本时执行：

```powershell
git -C "$env:USERPROFILE\.kiro\skills\fct-ops-troubleshoot" pull --ff-only
```

## 十、发布检查清单

### 仓库

- [ ] 根目录只有一份权威 `SKILL.md`
- [ ] README 说明用途、权限边界和安装入口
- [ ] 客户端差异与环境映射分开维护
- [ ] 无重复文档
- [ ] `.gitignore` 和 `.gitattributes` 已配置
- [ ] 仓库无真实工单数据、凭据和个人绝对路径
- [ ] 校验脚本、辅助脚本和 Git 检查通过

### GitLab

- [ ] Namespace 选择正确，优先团队 Group
- [ ] Visibility 符合公司数据范围
- [ ] 创建空仓库时未初始化 README
- [ ] `main` 推送成功并设置 upstream
- [ ] GitLab 页面目录和 README 显示正常
- [ ] 如需保护分支，已限制直接推送并要求 MR

### 使用者

- [ ] 已按客户端安装到正确目录
- [ ] 客户端能发现 `SKILL.md`
- [ ] 已配置项目自己的仓库与环境映射
- [ ] 只授予职责所需的最小只读 MCP 权限
- [ ] 能明确识别缺失能力和证据缺口
- [ ] 写操作仍需用户明确授权

## 十一、本次发布结果

- 本地发布目录：`D:\fctproject\gitlab-release\fct-ops-troubleshoot`
- GitLab 项目：`cn-chaopanod/fct-ops-troubleshoot`
- 默认分支：`main`
- 当前结构：Kiro 优先，同时兼容支持 Agent Skills 的其他客户端
- MCP 说明：统一维护在 `docs/ENVIRONMENT.md`
- Codex 适配：保留在 `adapters/codex/openai.yaml`，不影响其他客户端
- 安全边界：默认只读，评论、修数和知识更新需另行授权

后续如果团队建立了正式 GitLab Group，建议将项目从个人 Namespace 迁移到团队 Group，并更新安装地址；仓库内容和使用方式不需要因此改变。
