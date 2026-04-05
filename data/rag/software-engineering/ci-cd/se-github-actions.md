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
quality_tier: "S"
quality_score: 81.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.952
last_scored: "2026-04-06"
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

GitHub Actions 是 GitHub 于 2019 年 11 月正式发布的原生 CI/CD 自动化平台，直接集成在 GitHub 代码仓库中，无需安装任何额外服务即可使用。它基于事件驱动模型，当仓库发生特定事件（如 `push`、`pull_request`、`release`）时，自动触发预定义的工作流程（Workflow）。与 Jenkins、Travis CI 等外部工具不同，GitHub Actions 将流水线配置文件以 YAML 格式存放在仓库的 `.github/workflows/` 目录下，配置即代码，版本可追踪。

GitHub Actions 的计费模式对公开仓库完全免费，私有仓库每月提供 2000 分钟的免费使用额度（GitHub Free 方案）。GitHub 托管的 Runner 机器规格为 2 核 CPU、7 GB RAM、14 GB SSD，可运行 Ubuntu、Windows 和 macOS 环境。这种零基础设施维护成本的特性，使它成为中小型项目 CI/CD 的首选方案。

## 核心原理

### Workflow 文件结构

一个完整的 Workflow 文件由三个必要字段构成：`name`（工作流名称）、`on`（触发条件）和 `jobs`（任务列表）。每个 Job 包含 `runs-on`（指定 Runner 环境）和 `steps`（执行步骤列表）。Steps 可以是运行 Shell 命令的 `run` 字段，也可以是调用预封装逻辑的 `uses` 字段。

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - run: npm install && npm test
```

`on` 字段支持多种触发器，包括 `workflow_dispatch`（手动触发）、`schedule`（基于 cron 表达式的定时触发，如 `'0 8 * * 1'` 表示每周一上午 8 点）以及 `workflow_call`（被其他 Workflow 调用，实现复用）。

### Action 的本质与复用

Action 是 GitHub Actions 中可复用的最小工作单元，分为三种类型：Docker 容器型 Action、JavaScript 型 Action 和复合型 Action（Composite Action）。官方维护的 `actions/checkout@v4` 负责将仓库代码检出到 Runner 工作目录，`actions/setup-node@v4` 负责配置指定版本的 Node.js 运行环境。这些 Action 本身也是公开的 GitHub 仓库，可在 GitHub Marketplace 中搜索超过 20000 个社区 Action。

引用 Action 时，版本固定写法推荐使用完整的 commit SHA（如 `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`）而非标签，以防止供应链攻击导致的恶意代码注入。

### Runner 与执行环境

Runner 是执行 Workflow Job 的宿主机器，分为 **GitHub 托管 Runner** 和**自托管 Runner（Self-hosted Runner）**两类。GitHub 托管 Runner 每个 Job 都在全新的虚拟机中运行，Job 结束后环境销毁，保证隔离性。自托管 Runner 需要在目标机器上安装 `actions/runner` 软件并注册到仓库，适合需要访问内网资源或使用特殊硬件（如 GPU）的场景。

多个 Job 默认并行执行，若需串行则使用 `needs` 字段声明依赖：`needs: build` 表示当前 Job 必须等待 `build` Job 成功后才能启动。Job 间数据传递通过 `actions/upload-artifact` 和 `actions/download-artifact` 实现，将构建产物（如编译后的二进制文件）以 ZIP 包形式暂存，默认保留 90 天。

### 秘密变量与上下文

GitHub Actions 提供 Secrets 和 Variables 两种仓库级配置存储。Secrets 中的值（如 API 密钥、部署令牌）在日志中自动被 `***` 遮蔽，通过 `${{ secrets.MY_SECRET }}` 语法引用。环境变量通过 `${{ env.VAR_NAME }}` 或直接写入 `GITHUB_ENV` 文件来传递。`github` 上下文对象提供运行时元数据，例如 `${{ github.sha }}` 获取触发当前运行的 commit 哈希值，`${{ github.actor }}` 获取触发者用户名。

## 实际应用

**Node.js 项目的完整 CI 流程**：在 `push` 和 `pull_request` 事件触发时，先用 `actions/setup-node@v4` 配置 Node 18 环境，再通过矩阵策略（`matrix`）同时在 `ubuntu-latest`、`windows-latest`、`macos-latest` 三个平台运行测试，确保跨平台兼容性。矩阵配置示例：

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20]
```

这会生成 2×2=4 个并行 Job，大幅缩短整体 CI 时间。

**自动发布到 npm**：在 `release` 事件触发时，用 `NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}` 完成身份验证，执行 `npm publish` 将包发布到 npm 注册表，实现代码合并即发布的完整 CD 流程。

## 常见误区

**误区一：认为 Job 之间可以直接共享文件系统。** 每个 Job 运行在独立的 Runner 虚拟机上，文件系统完全隔离。同一 Job 内不同 Step 共享工作目录，但跨 Job 传递文件必须通过 Artifact 机制，而非直接读取路径。忽略这一点会导致 "文件不存在" 的报错，即便 `needs` 依赖已正确配置。

**误区二：混淆 `on: push` 与 `on: pull_request` 的代码来源。** `push` 触发时，`actions/checkout` 检出的是目标分支的最新 commit；而 `pull_request` 触发时，检出的是 GitHub 自动生成的合并提交（merge commit），即将 PR 源分支与目标分支合并后的结果，而非 PR 分支本身的 HEAD。这一差异在调试 CI 失败原因时容易被忽视。

**误区三：将 Self-hosted Runner 注册到公开仓库而不加限制。** 公开仓库的 Pull Request 可由任何人提交，若 Self-hosted Runner 未设置适当的权限隔离，恶意 PR 中的 Workflow 代码可能在内部服务器上执行危险命令。GitHub 官方建议对公开仓库的 Self-hosted Runner 始终在隔离的容器或虚拟机中运行。

## 知识关联

学习 GitHub Actions 之前需要掌握**流水线设计**的基本思想，理解 CI/CD 流程中构建、测试、部署阶段的职责划分——这直接对应 GitHub Actions 中 Job 的拆分逻辑和 `needs` 依赖链的设计方式。

掌握 GitHub Actions 后，自然进入 **Docker 在 CI 中的应用**这一话题：GitHub Actions 支持在 Job 中直接使用 `container` 字段指定 Docker 镜像作为运行环境，也支持通过 `services` 字段启动 MySQL、Redis 等辅助容器，构建更复杂的集成测试场景。此外，**游戏 CI/CD** 场景中对 Unity 构建、资源压缩等耗时任务的处理，需要在 GitHub Actions 的矩阵策略、缓存机制（`actions/cache`）和 Self-hosted Runner GPU 支持上进一步深化。