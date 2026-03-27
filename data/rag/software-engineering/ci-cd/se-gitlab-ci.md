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

GitLab CI 是 GitLab 内置的持续集成与持续交付系统，通过在代码仓库根目录放置 `.gitlab-ci.yml` 文件来定义自动化流水线。与 Jenkins 等需要独立部署的 CI 工具不同，GitLab CI 与代码仓库深度集成，每次 `git push` 或合并请求（Merge Request）都可自动触发流水线执行，无需额外的 Webhook 配置。

GitLab CI 最早在 2012 年随 GitLab 4.0 版本引入，最初功能较为简单。2015 年 GitLab 8.0 版本对其进行了大规模重构，引入了 GitLab Runner 作为独立的执行代理，从此形成了"GitLab 服务器 + Runner"的两层架构，这一架构延续至今。Runner 可以部署在任意机器上，通过轮询或 WebSocket 长连接与 GitLab 服务器通信，领取并执行 Job 任务。

GitLab CI 对团队的意义在于：它将 CI/CD 配置作为代码（Configuration as Code）存储在版本库中，任何对 `.gitlab-ci.yml` 的修改都有完整的 Git 历史追踪，这比在 Jenkins Web 界面手动配置 Job 更具可审计性和可重现性。

---

## 核心原理

### `.gitlab-ci.yml` 文件结构

`.gitlab-ci.yml` 使用 YAML 格式，最核心的概念是 **Stage（阶段）** 和 **Job（作业）**。Stage 定义执行顺序，同一 Stage 内的 Job 并行运行，前一 Stage 全部成功后才会进入下一 Stage。

```yaml
stages:
  - build
  - test
  - deploy

build-job:
  stage: build
  script:
    - docker build -t myapp:$CI_COMMIT_SHORT_SHA .

unit-test:
  stage: test
  script:
    - pytest tests/unit

deploy-prod:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

每个 Job 至少需要 `stage` 和 `script` 两个字段。`script` 是一个 Shell 命令列表，Runner 会按顺序逐行执行这些命令，任意一行返回非零退出码即视为 Job 失败。

### GitLab Runner 的类型与注册

Runner 是实际执行 Job 的代理进程，通过 `gitlab-runner register` 命令向 GitLab 服务器注册，注册时需要填写服务器 URL 和 Registration Token（在 GitLab 项目的 Settings > CI/CD > Runners 页面获取）。Runner 分为三种作用域：

- **Shared Runner**：由 GitLab 管理员配置，所有项目共享使用，GitLab.com 提供的免费 Shared Runner 每月有 400 分钟的配额限制。
- **Group Runner**：归属于某个 Group，该 Group 下所有项目可用。
- **Specific Runner**：仅绑定到单个项目，适合需要特殊硬件（如 GPU）或特定网络环境的任务。

Runner 的执行器（Executor）决定了 Job 在什么环境中运行，常用的有 `docker`（每次 Job 启动干净容器）、`shell`（直接在 Runner 所在机器执行）和 `kubernetes`（在 K8s 集群中动态创建 Pod）。

### 关键配置指令

**`only` / `except` 与 `rules`**：控制 Job 的触发条件。`only: [main]` 表示仅在 `main` 分支触发，而较新的 `rules` 语法更灵活，支持基于文件变更路径、变量值等复杂条件判断：

```yaml
rules:
  - if: '$CI_COMMIT_BRANCH == "main" && $CI_PIPELINE_SOURCE == "push"'
    when: always
  - when: never
```

**`artifacts`**：用于在 Job 之间传递文件。声明了 `artifacts` 的 Job 会将指定路径的文件上传到 GitLab 服务器，后续 Stage 的 Job 会自动下载这些文件：

```yaml
build-job:
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
```

**`cache`**：与 `artifacts` 不同，`cache` 用于缓存依赖包（如 `node_modules`、`.pip` 目录）以加速构建，基于 `key` 字段决定缓存是否复用。

**`variables`**：GitLab CI 内置了大量预定义变量，如 `$CI_COMMIT_SHA`（完整提交哈希）、`$CI_PROJECT_NAME`（项目名）、`$CI_REGISTRY`（容器镜像仓库地址），可直接在 `script` 中使用。

---

## 实际应用

**Node.js 项目的典型流水线**：在 `build` 阶段运行 `npm ci` 安装依赖并编译，在 `test` 阶段并行运行单元测试和 ESLint 代码检查，在 `deploy` 阶段使用 `only: [main]` 限制仅主分支自动部署到生产环境。整个过程利用 `cache` 缓存 `node_modules` 目录，可将后续流水线的依赖安装时间从 2 分钟降至 15 秒以内。

**合并请求流水线（Merge Request Pipeline）**：在 Job 中设置 `only: [merge_requests]` 或使用 `rules` 配置 `$CI_PIPELINE_SOURCE == "merge_request_event"`，可使流水线仅在 MR 创建或更新时触发，从而在代码合并前就完成测试验证，并将测试报告直接展示在 MR 页面的评论区。

**动态环境（Review Apps）**：GitLab CI 支持为每个 MR 自动部署一个临时预览环境，在 Job 中配置 `environment: name: review/$CI_COMMIT_REF_NAME`，GitLab 会在 Environments 页面展示每个预览环境的访问链接，MR 合并后可配置 `on_stop` 自动销毁该环境。

---

## 常见误区

**误区一：混淆 `cache` 与 `artifacts` 的用途**。很多初学者将两者互换使用。`artifacts` 是流水线内跨 Job 传递构建产物（如编译后的二进制文件）的机制，具有严格的生命周期；而 `cache` 是跨流水线复用的加速机制（如缓存 Maven 本地仓库），不保证一定命中。将大型构建产物放入 `cache` 会导致每次流水线都上传/下载不必要的大文件，严重拖慢速度。

**误区二：认为 `only: [main]` 与 `rules` 等效且可以混用**。实际上，在同一个 Job 中不能同时使用 `only/except` 和 `rules`，GitLab 会报配置错误。此外，`only` 语法在功能上存在局限，GitLab 官方文档已明确建议迁移至 `rules` 语法以获得更精细的控制能力。

**误区三：Shared Runner 与 Specific Runner 安全等价**。Shared Runner 在多个项目间共享执行环境，若使用 `shell` 执行器，不同项目的 Job 实际上运行在同一操作系统用户下，存在环境污染和敏感信息泄露风险。对于包含生产环境密钥的 Job，应使用专属的 Specific Runner 并配置 `docker` 执行器以隔离执行环境。

---

## 知识关联

学习 GitLab CI 需要具备**流水线设计**的基础认知，理解 Stage 串行、Job 并行的执行模型正是流水线设计中阶段划分原则的直接落地实现。`.gitlab-ci.yml` 中 `stages` 数组的顺序对应流水线设计中对构建、测试、部署三层结构的划分逻辑。

GitLab CI 与 GitLab 的**Protected Branches**（受保护分支）和**Environments**功能深度联动——受保护分支上的 Job 只能由标记了 `Protected` 的 Runner 执行，这提供了一层额外的安全隔离，是将代码评审流程与部署权限控制结合的关键机制。掌握 `.gitlab-ci.yml` 的完整语法后，可进一步探索 GitLab 的**父子流水线（Parent-Child Pipelines）**和**多项目流水线（Multi-project Pipelines）**，用于管理大型 Monorepo 或跨服务的协作部署场景。