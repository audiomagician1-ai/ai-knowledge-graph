---
id: "se-gitlab-ci"
concept: "GitLab CI"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 2
is_milestone: false
tags: ["平台"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# GitLab CI

## 概述

GitLab CI 是 GitLab 平台内置的持续集成系统，通过在代码仓库根目录放置 `.gitlab-ci.yml` 配置文件来定义自动化流水线。与 Jenkins 等独立工具不同，GitLab CI 与代码托管、合并请求（Merge Request）、容器注册表（Container Registry）深度集成，无需额外安装独立 CI 服务器即可触发构建、测试和部署任务。

GitLab CI 首次发布于 2012 年，最初作为独立项目 GitLab CI 存在，2015 年 GitLab 8.0 版本将其完全合并进主产品，成为 GitLab 平台不可分割的一部分。此后引入了 GitLab Runner（负责实际执行任务的代理程序）与 GitLab 服务器分离部署的架构，使执行环境高度灵活。

GitLab CI 的核心价值在于"配置即代码"——`.gitlab-ci.yml` 文件随代码一同提交、版本化、审查，流水线行为完全透明可追溯。对于已将代码托管在 GitLab 的团队，无需额外集成外部 CI 工具，即可实现从代码推送到生产部署的全链路自动化。

## 核心原理

### `.gitlab-ci.yml` 文件结构

`.gitlab-ci.yml` 使用 YAML 语法编写，最顶层的关键字包括 `stages`、`variables`、`default` 和各个 `job` 定义。一个最小可运行的示例如下：

```yaml
stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  script:
    - echo "Compiling..."
    - make build

unit-test:
  stage: test
  script:
    - pytest tests/
  only:
    - merge_requests
    - main
```

`stages` 字段定义阶段执行顺序，同一 `stage` 内的多个 job 并行执行，不同 `stage` 之间严格串行。每个 job 必须指定所属 `stage`，以及至少包含 `script` 字段（一个 Shell 命令列表）。

### GitLab Runner 与执行器

GitLab Runner 是独立的 Go 语言程序，负责从 GitLab 服务器拉取 job 并在本地执行。Runner 注册时需要选择**执行器（Executor）**类型，常见类型有：

- **Shell**：直接在 Runner 所在机器的 Shell 中执行，适合简单场景，但环境污染风险高
- **Docker**：每个 job 启动一个独立容器执行，通过 `image` 字段指定镜像（如 `image: python:3.11`），环境隔离彻底
- **Kubernetes**：在 K8s 集群中为每个 job 动态创建 Pod，适合大规模并发场景

注册 Runner 使用命令 `gitlab-runner register`，需要提供 GitLab 服务器 URL 和注册令牌（Registration Token）。Runner 有三种作用域：**Shared Runner**（所有项目共用）、**Group Runner**（组内项目共享）和**Specific Runner**（仅绑定指定项目）。

### 流水线触发规则与 `rules` 关键字

GitLab CI 通过 `rules`、`only`/`except` 关键字控制 job 的触发条件。推荐使用较新的 `rules` 语法（GitLab 12.3 引入），支持更复杂的条件逻辑：

```yaml
deploy-prod:
  stage: deploy
  script:
    - ./deploy.sh production
  rules:
    - if: '$CI_COMMIT_BRANCH == "main" && $CI_PIPELINE_SOURCE == "push"'
      when: manual
    - when: never
```

上述配置表示：仅当推送到 `main` 分支时该 job 出现，且需要手动触发（`when: manual`）。GitLab 提供超过 50 个预定义 CI/CD 变量（如 `$CI_COMMIT_SHA`、`$CI_MERGE_REQUEST_ID`），可在条件判断和脚本中直接使用。

### Artifacts 与缓存机制

`artifacts` 关键字将 job 产出的文件传递给后续 stage 的 job，默认保留 30 天：

```yaml
build-job:
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

`cache` 关键字用于跨 pipeline 复用文件（如 `node_modules`），通过 `key` 字段区分不同缓存桶。`artifacts` 和 `cache` 的本质区别：前者在同一 pipeline 的 stage 之间传递数据，后者在不同 pipeline 执行之间节省下载时间。

## 实际应用

**前端项目完整流水线**：一个典型的 Vue.js 项目 `.gitlab-ci.yml` 会包含 `install`（`npm ci`）、`lint`（`eslint`）、`test`（`jest --coverage`）、`build`（`npm run build`）、`docker-build`（推送镜像到 GitLab Container Registry）和 `deploy`（触发 K8s 滚动更新）六个 stage，合并请求触发前五个 stage，仅 `main` 分支的推送触发 `deploy`。

**多环境部署**：利用 GitLab CI 的环境（`environment`）功能，可以定义 `staging` 和 `production` 两套部署 job，在 GitLab UI 的 Deployments 页面追踪每个环境当前部署的版本，并支持一键回滚。

**矩阵测试**：使用 `parallel: matrix` 关键字（GitLab 13.3 引入）可在单个 job 定义中并行运行多个参数组合，例如同时测试 Python 3.9、3.10、3.11 三个版本，无需手动复制三份 job 配置。

## 常见误区

**误区一：将 `cache` 当 `artifacts` 使用**。cache 不保证可靠传递——Runner 可能在不同机器上执行导致缓存未命中，也可能因存储满而被清除。若 build 阶段产出的二进制文件需要在 deploy 阶段使用，必须用 `artifacts`，而不能依赖 `cache`。

**误区二：忽视 Runner 标签（Tags）导致 job 永远处于 Pending 状态**。每个 Runner 注册时可添加标签（如 `docker`、`linux`），job 中通过 `tags` 字段指定需要的 Runner。若 job 的 `tags` 要求无法被任何在线 Runner 满足，该 job 会无限期等待，而不会报错提示。排查时应检查 GitLab 项目设置中的 CI/CD Runner 列表，确认有绑定且在线的 Runner 具备匹配标签。

**误区三：在 `.gitlab-ci.yml` 中硬编码敏感信息**。API 密钥、数据库密码等不应明文写入配置文件。正确做法是在 GitLab 项目或组的 **Settings > CI/CD > Variables** 中添加 Masked 变量（变量值在 job 日志中自动屏蔽），在脚本中以 `$DEPLOY_KEY` 形式引用。

## 知识关联

学习 GitLab CI 之前需要掌握**流水线设计**的基本思想——理解 stage 串行与 job 并行的区别，以及构建、测试、部署分层的必要性，这样才能合理规划 `.gitlab-ci.yml` 的 `stages` 结构，避免将所有任务塞进单个 job。

在 GitLab CI 的具体技术上，还可以进一步研究**父子流水线**（Parent-Child Pipelines，通过 `trigger` 关键字拆分大型仓库的配置）和**多项目流水线**（跨仓库触发，适合微服务联动部署场景）。掌握 GitLab CI 后，理解 GitHub Actions 或 Azure Pipelines 等其他 CI/CD 工具的配置语法也会更加容易，因为"触发规则 + 执行环境 + 步骤脚本"的三段式结构是各平台的共同范式。