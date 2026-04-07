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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

Docker Compose 是 Docker 官方提供的多容器编排工具，通过一个名为 `docker-compose.yml` 的 YAML 配置文件定义和运行由多个容器组成的应用程序。它解决了单独使用 `docker run` 命令管理多容器应用时参数繁琐、容器间依赖关系难以维护的问题。一条 `docker-compose up` 命令即可启动整个应用栈，包括网络、卷挂载、环境变量和服务依赖。

Docker Compose 最初由 Orchard Labs 开发，产品名为 Fig，2014 年 Docker 公司收购后将其重命名为 Docker Compose 并集成进 Docker 生态系统。2020 年发布的 Compose Specification（组合规范）将配置格式标准化，使其不再局限于 Docker 引擎，Compose V2 于 2022 年正式取代 V1，以 Go 语言重写并作为 Docker CLI 插件发布，命令从 `docker-compose` 变更为 `docker compose`（无连字符）。

在 AI 工程场景中，Docker Compose 常用于本地搭建包含模型服务、向量数据库、API 网关和监控服务的完整推理环境。例如，一个典型的 RAG 系统本地环境可能同时运行 Ollama（模型推理）、Qdrant（向量数据库）、FastAPI（应用后端）和 Prometheus（指标采集）四个容器，Compose 使这四个服务能以声明式方式一键启动并自动组网。

## 核心原理

### YAML 配置文件结构

`docker-compose.yml` 的顶层键包含四个主要部分：`version`（V2 中已废弃）、`services`、`networks` 和 `volumes`。其中 `services` 是必填项，每个服务对应一个容器定义。以下是一个 AI 推理服务的典型配置示例：

```yaml
services:
  inference:
    image: ollama/ollama:0.1.32
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  vector_db:
    image: qdrant/qdrant:v1.7.4
    depends_on:
      - inference
    ports:
      - "6333:6333"

volumes:
  ollama_data:
```

`ports` 字段格式为 `"宿主机端口:容器端口"`，`depends_on` 控制启动顺序但不等待服务就绪（需配合 `healthcheck` 实现真正的健康等待）。

### 服务网络与服务发现

Compose 默认为每个项目创建一个名为 `{项目名}_default` 的桥接网络，所有服务自动加入该网络。服务之间通过**服务名**作为主机名直接通信，无需知道 IP 地址。例如，应用服务访问 PostgreSQL 时连接字符串写作 `postgresql://postgres:5432/mydb`，其中 `postgres` 就是服务名，Docker 内置 DNS 负责解析。若需隔离不同服务组，可自定义多个 `networks` 并为每个服务指定所属网络，实现前端服务与数据库层的网络隔离。

### 环境变量与 .env 文件

Compose 原生支持从项目根目录下的 `.env` 文件读取变量，语法为 `${VARIABLE_NAME}` 或 `${VARIABLE_NAME:-default_value}`。敏感信息（如 API Key、数据库密码）应存放于 `.env` 文件并加入 `.gitignore`，配置文件中只保留变量引用。`env_file` 字段可为特定服务指定额外的环境变量文件：

```yaml
services:
  app:
    env_file:
      - .env
      - .env.production
```

后加载的文件中的同名变量会覆盖先加载的值，优先级从低到高为：`.env` 文件 → `environment` 字段 → Shell 环境变量。

### 健康检查与启动顺序控制

`depends_on` 的基础形式仅保证容器启动顺序，不保证服务可用。通过为服务配置 `healthcheck` 并将 `depends_on` 改写为条件形式，可实现真正的服务就绪等待：

```yaml
depends_on:
  vector_db:
    condition: service_healthy
```

`healthcheck` 支持 `test`（检查命令）、`interval`（间隔，默认 30s）、`timeout`（超时，默认 30s）、`retries`（重试次数，默认 3）和 `start_period`（初始化宽限期）五个参数。

## 实际应用

**本地 AI 开发环境搭建**：AI 工程师使用 Compose 在本地同时运行 Jupyter Lab、MLflow Tracking Server 和 MinIO（S3 兼容存储）。MLflow 通过服务名 `minio:9000` 访问对象存储，无需手动配置 IP，整个环境用 `docker compose up -d` 一键后台启动，`docker compose logs -f mlflow` 实时跟踪 MLflow 日志。

**多阶段服务依赖**：生产级 AI API 服务通常由模型预热服务、主推理服务和负载均衡器三层构成。Compose 可通过 `healthcheck` + `depends_on: condition: service_healthy` 确保模型加载完毕后再启动接受请求的推理服务，避免冷启动期间返回 503 错误。

**Override 文件实现多环境配置**：使用 `docker-compose.yml`（基础配置）+ `docker-compose.override.yml`（本地开发覆盖，自动合并）+ `docker-compose.prod.yml`（生产配置，需显式指定）的三文件模式，本地开发时挂载代码目录实现热重载，生产环境中移除调试端口和卷挂载，执行 `docker compose -f docker-compose.yml -f docker-compose.prod.yml up` 应用生产配置。

## 常见误区

**误区一：`depends_on` 等同于服务就绪**。许多开发者认为配置 `depends_on: - postgres` 后应用容器启动时数据库已经可以接受连接。实际上 Compose 仅等待 postgres 容器的进程启动，PostgreSQL 初始化数据目录可能需要额外 3-10 秒。未配置 `healthcheck` + `condition: service_healthy` 时，应用容器会因数据库尚未就绪而连接失败并崩溃。

**误区二：Compose 适合生产环境大规模部署**。Docker Compose 设计定位是单机多容器编排，不具备跨节点调度、自动故障转移和水平扩展能力。虽然 `docker compose up --scale inference=3` 可在单机启动 3 个推理副本，但没有负载均衡和节点感知，不适合承载高可用生产负载，该场景应迁移至 Kubernetes。

**误区三：修改 `.env` 文件后容器自动更新**。Compose 仅在容器创建时注入环境变量，修改 `.env` 后必须执行 `docker compose up -d` 重建受影响的容器（Compose 会检测配置变更并仅重建需要更新的服务），而非 `docker compose restart`（`restart` 只重启进程，不重建容器，不会读取新的环境变量）。

## 知识关联

**前置知识衔接**：Docker 基础中学习的镜像构建（`Dockerfile`）、容器生命周期和卷挂载概念是理解 Compose 配置的直接基础。Compose 的 `build` 字段可直接引用 `Dockerfile` 路径并传入 `args`，将单容器构建与多服务编排合并在同一工作流中。网络模式（bridge/host/none）在 Compose 的 `networks` 配置中直接沿用，理解 Docker 桥接网络原理有助于排查服务间通信问题。

**通向 Kubernetes**：Kubernetes 的核心概念 Pod、Service、Deployment 与 Compose 的 service、networks、`deploy.replicas` 存在概念映射关系。Compose Specification 提供了 `kompose convert` 工具，可将 `docker-compose.yml` 自动转换为 Kubernetes YAML 清单，迁移时需重点补充 Liveness/Readiness Probe（对应 Compose 的 `healthcheck`）和 ConfigMap/Secret（对应 Compose 的 `env_file` 和 `.env`）。掌握 Compose 的声明式配置思维，是理解 Kubernetes "期望状态" 控制循环模型的重要认知铺垫。