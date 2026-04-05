---
id: "se-git-hooks"
concept: "Git Hooks"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["自动化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 83.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# Git Hooks

## 概述

Git Hooks 是 Git 在特定操作发生时自动执行的脚本程序，存储在每个 Git 仓库的 `.git/hooks/` 目录下。当开发者执行 `git commit`、`git push`、`git merge` 等操作时，Git 会在操作的特定阶段（前置或后置）触发对应的钩子脚本，从而实现自动化检查、通知或其他任务。

Git Hooks 的概念自 Git 诞生之初（2005年）便已存在，与 Unix 的"脚本钩子"传统一脉相承。默认情况下，`.git/hooks/` 目录包含多个以 `.sample` 为后缀的示例文件，例如 `pre-commit.sample`，将 `.sample` 后缀移除并赋予可执行权限（`chmod +x`）即可激活对应钩子。

Git Hooks 的核心价值在于将质量保障嵌入开发工作流本身，而非依赖开发者的主动记忆。例如，通过 `pre-commit` 钩子在代码提交前自动运行 ESLint，可在第一时间拦截不合规代码，避免其进入代码历史记录。

---

## 核心原理

### 客户端钩子

客户端钩子运行在开发者本地机器上，由开发者的本地 Git 操作触发。最常用的客户端钩子包括：

- **`pre-commit`**：在 `git commit` 生成提交对象之前执行。若脚本返回非零退出码（`exit 1`），提交会被中止。常用于运行代码格式检查（如 `prettier --check`）或单元测试。
- **`commit-msg`**：在开发者完成提交信息编辑后、提交正式创建前执行，接收一个参数——提交信息文件的路径（通常为 `.git/COMMIT_EDITMSG`）。常用于校验提交信息是否符合 Conventional Commits 规范，例如检查是否以 `feat:`、`fix:` 等前缀开头。
- **`pre-push`**：在 `git push` 将本地引用发送至远程之前执行，可用于阻止直接推送到 `main` 分支。
- **`post-commit`**：在提交完成后执行，退出码不影响提交结果，常用于发送通知。

### 服务端钩子

服务端钩子运行在托管 Git 仓库的远程服务器上，是集中式强制执行规范的关键机制：

- **`pre-receive`**：当服务端接收到 `git push` 推送的数据包时，在更新任何引用之前执行一次。通过标准输入接收 `旧SHA 新SHA 引用名` 格式的数据流。若返回非零码，整次推送被拒绝。
- **`update`**：与 `pre-receive` 类似，但对每个被推送的分支各触发一次，接收三个参数：引用名、旧对象名、新对象名。适合对不同分支执行不同策略。
- **`post-receive`**：在所有引用更新完成后执行，常用于触发 CI/CD 流水线或向 Slack 发送部署通知。

### 钩子的执行机制与限制

Git Hooks 脚本可以是任意可执行文件，包括 Bash、Python、Node.js 脚本，只需首行 shebang 正确（如 `#!/bin/bash`）。重要限制是：**客户端钩子不随仓库克隆而传播**——`.git/` 目录不被 Git 追踪，因此新克隆的仓库不会自动获得团队的钩子脚本。解决方案是使用 `Husky`（Node.js 生态）或 `pre-commit`（Python 生态）等工具，将钩子配置文件纳入版本控制，并通过 `npm install` 或 `pip install` 时的安装钩子自动部署。Husky 从版本 8 起通过在 `.husky/` 目录存放钩子文件并配置 Git 的 `core.hooksPath` 实现共享。

---

## 实际应用

**场景一：提交前代码质量检查**

在前端项目中，通常将 `pre-commit` 钩子与 `lint-staged` 结合使用。`lint-staged` 只对本次暂存的文件运行检查，避免对整个项目的全量扫描带来的性能损耗。`package.json` 配置示例：

```json
{
  "lint-staged": {
    "*.ts": ["eslint --fix", "prettier --write"]
  }
}
```

Husky 的 `pre-commit` 钩子内容仅需一行 `npx lint-staged`，即可实现"只检查本次改动文件"的精准拦截。

**场景二：服务端保护主分支**

在自建 GitLab/Gitea 服务器上，通过 `update` 钩子检查推送目标分支：若 `$1`（引用名）等于 `refs/heads/main` 且推送者不在白名单中，则输出错误信息并 `exit 1`，拒绝直接推送，强制所有变更必须通过 Merge Request 合入。

**场景三：`commit-msg` 验证规范**

通过正则表达式验证提交信息：
```bash
#!/bin/bash
MSG=$(cat "$1")
PATTERN="^(feat|fix|docs|chore|refactor|test|style)(\(.+\))?: .{1,72}"
if ! echo "$MSG" | grep -qP "$PATTERN"; then
  echo "错误：提交信息不符合 Conventional Commits 规范"
  exit 1
fi
```

---

## 常见误区

**误区一：认为客户端钩子能保证团队规范强制执行**

客户端钩子完全可被开发者绕过：`git commit --no-verify` 参数会跳过 `pre-commit` 和 `commit-msg` 两个钩子。因此，客户端钩子只是便捷的本地辅助，真正无法绕过的规范必须通过服务端钩子（`pre-receive`、`update`）或代码托管平台（GitHub 的 Branch Protection Rules、GitLab 的 Push Rules）来强制执行。

**误区二：混淆 `pre-receive` 与 `update` 的触发时机**

`pre-receive` 在一次推送中只执行一次，处理的是整批引用更新；而 `update` 对每一个被更新的引用分别触发一次。如果一次 `git push` 同时推送了 3 个分支，`pre-receive` 执行 1 次，`update` 执行 3 次。当需要对每个分支独立做权限判断时，必须使用 `update` 而非 `pre-receive`。

**误区三：`post-commit` 中的错误会导致提交失败**

`post-commit` 在提交已经完成后运行，其退出码被 Git 完全忽略，无法撤销提交。若在 `post-commit` 中写了"提交失败时回滚"的逻辑，该逻辑永远不会被正确触发。需要在提交前进行校验，必须使用 `pre-commit` 钩子。

---

## 知识关联

学习 Git Hooks 需要掌握 **Git 基础**中的暂存区（staging area）概念、`git commit` 的执行流程，以及基本的 Shell 脚本语法（理解 `exit 0` 与 `exit 1` 的意义）。

Git Hooks 是实现**自动化代码审查**的基础机制：`pre-commit` 钩子与静态分析工具（SonarLint、ESLint）结合，构成本地代码审查的第一道防线；服务端 `pre-receive` 钩子则可集成 SonarQube 扫描，在代码进入主干前完成集中式质量门禁（Quality Gate）检查。此外，`post-receive` 钩子是传统 CI/CD 中触发构建流水线的经典方式，理解它有助于深入学习 Jenkins 或 Gitea Actions 等 CI 系统的触发机制。