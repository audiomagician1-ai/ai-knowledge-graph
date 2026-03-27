---
id: "se-github-actions"
concept: "GitHub Actions"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 2
is_milestone: true
tags: ["平台"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# GitHub Actions

## 概述

GitHub Actions 是 GitHub 于 2018 年推出、2019 年 11 月正式 GA（General Availability）的内置 CI/CD 自动化平台。它将工作流配置文件直接存储在代码仓库的 `.github/workflows/` 目录下，以 YAML 格式编写，使流水线定义与源代码版本同步管理。相比 Jenkins 等独立 CI 服务器，GitHub Actions 无需维护独立基础设施即可完成构建、测试和部署。

GitHub Actions 的计费模型对公开仓库完全免费，私有仓库每月提供 2000 分钟的免费额度（免费账户），超出后按 Ubuntu Runner 每分钟 $0.008 计费，macOS Runner 费率是其 10 倍（每分钟 $0.08）。这一定价结构直接影响了工作流的设计决策，例如是否使用 `continue-on-error`、是否并行化 job。

理解 GitHub Actions 的关键在于掌握其四层抽象结构：**Event → Workflow → Job → Step**。每一层都有独立的配置键和执行上下文，混淆这四层是初学者最常见的错误。

---

## 核心原理

### 触发事件（Event）

工作流由 `on:` 键定义触发条件。GitHub Actions 支持超过 35 种事件类型，最常用的包括：

- `push`：代码推送到指定分支时触发
- `pull_request`：PR 创建或更新时触发
- `schedule`：使用 POSIX cron 语法定时触发，例如 `'0 9 * * 1'` 表示每周一 UTC 9:00
- `workflow_dispatch`：手动触发，支持通过 `inputs:` 定义用户输入参数

触发条件可以精细控制范围。例如 `push` 事件可用 `branches`、`paths` 过滤器限定仅在 `main` 分支且 `src/**` 目录有变更时才运行，避免文档修改触发完整构建流水线。

### Job 与 Runner 配置

Job 是并行执行的基本单位，通过 `runs-on:` 指定运行环境。GitHub 提供的托管 Runner 包括：

- `ubuntu-latest`（当前映射至 Ubuntu 22.04）
- `windows-latest`（Windows Server 2022）
- `macos-latest`（macOS 13 Ventura）

Job 间默认并行执行。若需串行，必须显式使用 `needs:` 声明依赖关系：

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
  test:
    needs: build
    runs-on: ubuntu-latest
```

`needs:` 还可以引用依赖 job 的输出值，通过 `needs.<job_id>.outputs.<output_name>` 语法跨 job 传递数据，例如将构建产生的镜像 tag 传递给部署 job。

### Step、Action 与环境变量

每个 Job 内部由顺序执行的 Step 组成。Step 有两种形式：

1. **`uses:`**：调用一个 Action（可重用单元），例如 `actions/checkout@v4` 检出代码，`actions/setup-node@v4` 配置 Node.js 环境
2. **`run:`**：直接执行 shell 命令，默认在 bash 中运行（Windows 下为 PowerShell）

环境变量通过三种方式注入：`env:` 键（在 workflow/job/step 级别均可设置）、GitHub 内置的 `$GITHUB_SHA`、`$GITHUB_REF` 等上下文变量，以及通过 Repository Settings 配置的 **Secrets**（加密存储，使用 `${{ secrets.MY_SECRET }}` 语法引用）。

矩阵策略（Matrix Strategy）是 GitHub Actions 的高效并行测试机制：

```yaml
strategy:
  matrix:
    node-version: [18, 20, 22]
    os: [ubuntu-latest, windows-latest]
```

上述配置会自动生成 6 个并行 Job，覆盖 3 个 Node.js 版本 × 2 个操作系统的组合，无需手动复制 Job 配置。

---

## 实际应用

**Node.js 项目的标准 CI 工作流**通常包含以下结构：在 `push` 和 `pull_request` 事件触发后，使用 `actions/checkout@v4` 检出代码，`actions/setup-node@v4` 配置指定版本的 Node.js 环境，`actions/cache@v4` 缓存 `~/.npm` 目录以加速依赖安装（缓存命中时 `npm ci` 速度可提升 60% 以上），最后依次执行 `npm ci`、`npm run lint`、`npm test`。

**自动发布 npm 包**的场景中，可在 `release` 事件的 `published` 类型触发时，使用 `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}` 注入认证信息，执行 `npm publish`，实现从 GitHub Release 到 npm 包发布的全自动流程。

**Composite Action** 允许将重复的 Step 序列封装为可重用模块，存放在仓库的 `.github/actions/my-action/action.yml` 中，通过 `using: composite` 声明，在其他工作流中以 `uses: ./.github/actions/my-action` 调用，避免跨工作流的代码重复。

---

## 常见误区

**误区一：将 Secret 直接打印到日志**
GitHub Actions 会自动遮蔽已注册 Secret 的值（显示为 `***`），但通过 `echo ${{ secrets.TOKEN }}` 显式打印时，某些 base64 变体或字符串分割仍可能绕过遮蔽机制。正确做法是永远不在 `run:` 中直接输出 Secret 内容，而是将其作为环境变量传递给需要的命令。

**误区二：误解 `runs-on: ubuntu-latest` 的稳定性**
`ubuntu-latest` 并非固定版本，GitHub 会周期性地将其从 Ubuntu 20.04 更新到 22.04 再到更新版本。如果工作流依赖特定系统库版本，应固定写 `ubuntu-22.04` 而非使用 `latest` 标签，否则 GitHub 升级映射时可能导致构建静默失败。

**误区三：混淆 `pull_request` 与 `pull_request_target` 的安全边界**
`pull_request` 事件在 fork PR 中无法访问目标仓库的 Secrets（出于安全隔离设计），而 `pull_request_target` 在仓库上下文中执行，可以访问 Secrets 但会执行 fork 提交的代码，存在安全风险。在公开仓库中不加防护地使用 `pull_request_target` 是导致 CI 密钥泄露的已知攻击向量。

---

## 知识关联

学习 GitHub Actions 需要以**流水线设计**为前置知识，具体体现在：流水线中的阶段划分（构建→测试→部署）直接对应 GitHub Actions 中多个 Job 通过 `needs:` 连接的有向无环图结构；流水线的并行化策略与 GitHub Actions 的 Matrix Strategy 和并发 Job 机制一一对应。

掌握 GitHub Actions 后，自然延伸到**Docker 在 CI 中的应用**：`docker/build-push-action@v5` 是 GitHub Marketplace 中使用最广泛的 Action 之一，它利用 Docker BuildKit 的缓存机制（通过 `cache-from: type=gha` 将 Docker 层缓存存入 GitHub Actions Cache）大幅缩短镜像构建时间。理解 GitHub Actions 的 Runner 环境和权限模型，是正确配置 Docker 登录、推送镜像到 GHCR（GitHub Container Registry）的基础。

进一步学习**游戏 CI/CD** 时，GitHub Actions 的 Self-hosted Runner 功能尤为关键——游戏项目通常需要 GPU 资源或特定的 Unity/Unreal 许可证服务器，托管 Runner 无法满足，需要在本地机器注册 Self-hosted Runner，通过 `runs-on: self-hosted` 调度到指定硬件上执行构建任务。