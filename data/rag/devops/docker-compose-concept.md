---
id: "docker-compose-concept"
concept: "Docker Compose"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 5
is_milestone: false
tags: ["容器"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.484
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Docker Compose

## 概述

Docker Compose 是 Docker 官方提供的多容器编排工具，通过单一 YAML 配置文件（默认命名为 `docker-compose.yml`）定义和运行多个相互协作的容器服务。它于 2014 年作为 Fig 项目被 Docker 公司收购后重新发布，最初版本使用 Python 编写，Docker Compose V2 版本（2021年发布）改用 Go 语言重写，并以 `docker compose`（无连字符）子命令的形式集成进 Docker CLI。

在 AI 工程场景中，一个典型的机器学习服务往往需要同时运行模型推理服务器、Redis 缓存、PostgreSQL 数据库和 Nginx 反向代理四个组件。如果用纯 Docker 命令逐一启动，不仅命令冗长，还需手动管理网络连接和依赖顺序。Docker Compose 将这些服务的镜像、端口、挂载卷、环境变量和启动依赖关系全部声明在一个文件里，用 `docker compose up -d` 一条命令即可完整拉起整个栈。

## 核心原理

### YAML 服务定义结构

`docker-compose.yml` 的顶层结构分为四个关键字段：`services`、`networks`、`volumes` 和 `configs`。其中 `services` 是必填项，每个 service 对应一个容器定义。以下是一个 AI 推理服务的典型配置片段：

```yaml
version: "3.9"
services:
  inference:
    image: pytorch/torchserve:0.9.0-cpu
    ports:
      - "8080:8080"
    volumes:
      - model_store:/home/model-server/model-store
    environment:
      - TS_NUMBER_OF_NETTY_THREADS=4
    depends_on:
      redis:
        condition: service_healthy
  redis:
    image: redis:7.2-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 3
volumes:
  model_store:
```

`version: "3.9"` 指定 Compose 文件格式版本，不同版本支持的字段集合不同，3.x 系列对应 Docker Engine 19.03 及以上。

### depends_on 与健康检查的协作机制

`depends_on` 字段控制容器启动顺序，但仅凭 `depends_on` 只能保证容器**启动**顺序，无法保证依赖服务**就绪**。要实现真正的就绪等待，必须在被依赖服务上配置 `healthcheck`，并在依赖方使用 `condition: service_healthy`。上例中 Redis 容器每 5 秒执行一次 `redis-cli ping`，连续 3 次失败才判定为不健康，inference 容器只有在 Redis 健康检查通过后才会启动。

### 网络隔离与服务发现

Docker Compose 默认为每个项目创建一个独立的桥接网络，网络名称格式为 `{项目名}_default`。同一 Compose 文件中的服务可以直接用服务名作为主机名互相访问，例如 inference 容器可以通过 `redis:6379` 直接连接 Redis，无需知道容器 IP。这一机制基于 Docker 内置的 DNS 解析，DNS 服务运行在 `127.0.0.11`。多个 Compose 项目之间默认网络隔离，若需跨项目通信，需要在 `networks` 字段中声明 `external: true` 引用已存在的外部网络。

### 环境变量与 .env 文件

Compose 自动读取与 `docker-compose.yml` 同目录下的 `.env` 文件，文件中的变量可在 YAML 内用 `${VAR_NAME}` 语法引用。例如将模型路径、GPU 数量等配置提取到 `.env` 文件，可实现开发环境与生产环境的配置切换，而无需修改主配置文件。运行时也可通过 `docker compose --env-file ./prod.env up` 显式指定不同的环境文件。

## 实际应用

**AI 模型开发环境一键搭建**：在本地开发 NLP 服务时，通常需要 JupyterLab、FastAPI 推理服务、MinIO 对象存储（用于存放模型文件）和 MLflow 实验跟踪四个组件。用一份 `docker-compose.yml` 定义这四个 service，挂载本地代码目录到容器，开发者执行 `docker compose up` 后立即获得完整开发环境，团队成员共享同一配置文件确保环境一致性。

**GPU 资源分配**：在需要 GPU 的 AI 训练场景中，Compose 文件可以通过 `deploy.resources.reservations.devices` 字段为特定服务分配 GPU：

```yaml
services:
  trainer:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 2
              capabilities: [gpu]
```

这要求宿主机安装 NVIDIA Container Toolkit，并使用 Docker Engine 19.03 以上版本。

**滚动配置更新**：修改 `docker-compose.yml` 后执行 `docker compose up -d --no-recreate` 可以只重建配置发生变化的容器，保持其余容器继续运行，适合在不中断 Redis 缓存的前提下更新推理服务镜像。

## 常见误区

**误区一：认为 Compose 的 `scale` 等同于生产级负载均衡**。`docker compose up --scale inference=3` 确实能启动 3 个 inference 容器实例，但 Compose 默认的 DNS 轮询并不具备健康感知能力——某个实例崩溃后，DNS 仍可能将请求路由到该实例，导致请求失败。Compose 的扩缩容适合开发测试验证并发行为，生产环境需要 Kubernetes 或 Docker Swarm 的服务编排。

**误区二：将 `version` 字段视为当前安装的 Compose 版本**。`docker-compose.yml` 中的 `version` 字段声明的是 **Compose 文件格式规范版本**，而非工具本身的版本。Docker Compose V2 已将该字段标记为过时（deprecated），新版本中即使省略 `version` 字段也能正常解析，混淆两者会导致无谓的版本排查。

**误区三：误以为 `docker compose down` 会删除挂载卷**。`docker compose down` 默认只删除容器和网络，具名卷（named volumes）会被保留，数据不会丢失。只有执行 `docker compose down -v` 才会同时删除具名卷。在 AI 项目中误用 `-v` 参数可能导致训练好的模型文件或数据库数据永久丢失。

## 知识关联

**前置知识衔接**：Docker Compose 建立在 Docker 单容器操作的基础之上。理解 `docker run` 的 `-p`、`-v`、`-e`、`--network` 等参数，有助于直接对应 `docker-compose.yml` 中的 `ports`、`volumes`、`environment`、`networks` 字段——Compose 本质上是将这些命令行参数结构化为声明式配置。Dockerfile 的编写能力同样不可或缺，因为 Compose 的 `build` 字段直接引用 Dockerfile 来构建自定义镜像。

**通往 Kubernetes 的过渡**：Compose 的服务定义概念与 Kubernetes 的 Pod、Service、Deployment 存在明确的对应关系。`kompose convert` 工具可以将 `docker-compose.yml` 自动转换为 Kubernetes YAML 清单文件，虽然转换结果通常需要手动调整，但这一映射关系有助于理解 K8s 的资源模型。Kubernetes 在多节点调度、自动扩缩容（HPA）、滚动更新策略等方面提供了 Compose 所不具备的生产级能力，是 AI 服务从单机部署迈向集群部署的下一个核心工具。