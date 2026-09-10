---
title: Git 与 Jenkins 工作流速查
type: 工具实战
status: 已整理
updated: 2026-09-09
tags: [Git, Jenkins, CI, 版本控制]
---

# Git 与 Jenkins 工作流速查

返回：[[07-工具与工作流/00-工具与工作流导航|工具与工作流导航]] · [[08-学习与成长/测试工程知识体系/00-测试总结知识地图|测试总结知识地图]]

## Git 日常检查

```bash
git status --short
git diff
git diff --staged
git log --oneline --decorate -10
git branch --show-current
git remote -v
```

提交前明确当前分支、变更范围和远端。按文件精确暂存，避免在脏工作区使用 `git add .` 把无关内容一起提交。

```bash
git switch -c codex/example-change
git add -- path/to/file
git diff --cached --check
git commit -m "docs: describe the change"
git push -u origin codex/example-change
```

## 撤销与恢复

- 未提交修改先看 `git diff`，确认后再按明确文件恢复。
- 已暂存内容可从暂存区移除而不丢工作区修改。
- 已共享提交优先用 `git revert <commit>` 生成反向提交。
- `reset --hard`、清理未跟踪文件和强推可能造成难以恢复的数据丢失，不作为常规手段。

合并冲突时逐文件理解两边意图，完成后运行相关测试。解决了文本冲突不代表行为正确。

## Jenkins Pipeline 思路

流水线通常包含：检出 → 安装依赖 → 静态检查 → 测试 → 报告 → 制品保存 → 部署/通知。凭据使用 Jenkins Credentials，不写入 Jenkinsfile 或日志。

```groovy
pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh 'python -m pytest -q --junitxml=output/junit.xml'
      }
      post {
        always { junit 'output/junit.xml' }
      }
    }
  }
}
```

Windows Agent 使用适合宿主的步骤和路径。Pipeline 示例必须根据实际仓库、环境和依赖调整。

## CI 证据与安全

- 记录提交 SHA、依赖版本、执行命令、用例数和失败详情。
- 测试报告和产物设置合理保留期；Trace、截图和响应可能含敏感数据。
- 部署只接受经过验证且可追溯的制品，不能在部署阶段重新构建另一份代码。
- CI 通过只代表配置的检查通过；未执行、跳过或条件过滤的测试要单独报告。
- 回滚优先回到已验证制品，并保留回滚原因与复测证据。
