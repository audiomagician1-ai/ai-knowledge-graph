---
id: "helm-charts"
concept: "Helm Charts"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["helm", "kubernetes", "package-management"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# Helm Charts

## 概述

Helm Charts 是 Kubernetes 应用的打包格式，它将一组相关的 Kubernetes 资源定义文件（YAML 清单）捆绑为一个可版本化、可复用的部署单元。一个 Chart 本质上是一个目录树，包含描述 Kubernetes 应用的模板文件、默认配置值以及元数据。Helm 本身被称为"Kubernetes 的包管理器"，其角色类似于 Linux 系统中的 apt 或 yum。

Helm 项目由 Deis 公司于 2015 年发起，并于 2016 年并入 Cloud Native Computing Foundation（CNCF）。Helm v3 于 2019 年 11 月正式发布，相比 v2 最重要的变化是移除了服务端组件 Tiller，所有权限控制直接通过 Kubernetes RBAC 实现，显著降低了安全风险。目前主流版本均基于 Helm v3，理解这一版本差异对于阅读历史文档至关重要。

在 AI 工程的 MLOps 场景中，一套机器学习系统通常包含模型服务、特征存储、调度器、监控等十几个微服务，手动管理这些组件的 Kubernetes YAML 文件既容易出错又难以版本追踪。Helm Charts 通过模板化和版本控制机制，使整套系统可以用一条 `helm install` 命令完成部署，并支持回滚到历史任意版本。

---

## 核心原理

### Chart 目录结构

一个标准的 Helm Chart 目录具有固定的文件布局：

```
my-ml-service/
├── Chart.yaml          # Chart元数据（名称、版本、apiVersion）
├── values.yaml         # 默认配置值
├── templates/          # Kubernetes清单模板目录
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl    # 命名模板辅助文件
└── charts/             # 依赖子Chart目录
```

`Chart.yaml` 中必须包含 `apiVersion`（v2 对应 Helm 3）、`name` 和 `version` 三个字段，其中 `version` 遵循语义化版本规范（SemVer 2.0），例如 `1.4.2`。`appVersion` 字段则记录实际应用程序的版本号，与 Chart 版本相互独立。

### Go 模板引擎与 values 注入

Helm 使用 Go 语言内置的 `text/template` 包解析 `templates/` 目录下的所有文件。模板中通过双花括号语法引用变量，例如：

```yaml
# templates/deployment.yaml
spec:
  replicas: {{ .Values.replicaCount }}
  containers:
    - image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

渲染时，Helm 将 `values.yaml` 中的默认值与用户通过 `--set` 或 `-f custom.yaml` 传入的覆盖值合并，再填入模板。值的优先级从低到高依次为：`values.yaml` 默认值 < 父 Chart 的 `values.yaml` < `-f` 指定文件 < `--set` 命令行参数。这种分层覆盖机制使得同一套 Chart 可以无修改地部署到开发、测试、生产三套环境，只需提供不同的 `values` 文件。

### Release 与版本管理

每次执行 `helm install` 会创建一个 **Release**，即 Chart 在特定命名空间内的一次具名安装实例。Helm v3 将 Release 的状态（包括历史版本的 manifest 快照）以 Secret 形式存储在对应的 Kubernetes 命名空间中，而非独立数据库。执行 `helm upgrade` 时，Helm 会生成新的 manifest 与当前运行状态做三路合并（three-way merge），智能计算需要新增、更新或删除的资源。`helm rollback my-release 2` 可将指定 Release 回退到历史第 2 个版本，Helm 最多默认保留 10 个历史版本（通过 `--history-max` 可调整）。

### Chart 依赖管理

`Chart.yaml` 中的 `dependencies` 字段声明子 Chart 依赖，例如一个 AI 推理服务 Chart 可以声明依赖 `redis` 和 `postgresql`：

```yaml
dependencies:
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
```

执行 `helm dependency update` 后，子 Chart 的 `.tgz` 压缩包会被下载至 `charts/` 目录，并生成 `Chart.lock` 文件锁定精确版本，确保团队协作和 CI/CD 流水线的可复现性。

---

## 实际应用

**部署 Kubeflow Pipelines**：Kubeflow 官方提供的 Helm Chart 一次性安装涵盖 API Server、Persistence Agent、Scheduler 等 8 个组件。运维团队只需在 `values.yaml` 中配置 `objectStore.host` 指向内部 MinIO 地址，执行 `helm install kubeflow kubeflow/kubeflow-pipelines -f prod-values.yaml -n kubeflow` 即可完成生产级部署。

**多环境模型服务管理**：以 Triton Inference Server 为例，开发环境使用 1 个副本、CPU 推理，生产环境使用 4 个副本、GPU 节点亲和性调度。通过维护 `values-dev.yaml` 和 `values-prod.yaml` 两个文件，同一个 Chart 无需修改模板即可支持两套环境，用 `helm diff upgrade`（需安装 helm-diff 插件）可以在执行前预览生产环境变更差异。

**Helm Repository 私有化**：企业内部可使用 Harbor 或 Chartmuseum 搭建私有 Chart 仓库。通过 `helm push my-service-1.2.0.tgz oci://registry.company.com/charts`，借助 OCI 镜像仓库协议存储 Chart，使 Chart 版本管理与容器镜像版本管理统一在同一套基础设施中。

---

## 常见误区

**误区一：混淆 `version` 与 `appVersion` 的用途**
许多初学者将 `Chart.yaml` 中的 `version`（Chart 本身的版本）与 `appVersion`（应用程序版本）随意同步修改。正确做法是：只有 Chart 模板或打包逻辑发生变化时才升级 `version`；仅应用镜像版本变动时只更新 `appVersion`，两者独立演进。将两者强绑定会导致 Chart 的语义化版本失去意义，破坏依赖管理。

**误区二：在模板中硬编码敏感配置**
将数据库密码、API Key 等直接写入 `values.yaml` 并提交至 Git 仓库是严重的安全隐患。正确做法是在模板中引用 Kubernetes Secret，结合 `helm-secrets` 插件（基于 SOPS 加密）或外部 Secret 管理系统（如 HashiCorp Vault）注入敏感值，`values.yaml` 中仅保留 Secret 的名称引用而非明文内容。

**误区三：忽略 `helm template` 的调试价值**
部分工程师在 Chart 报错时直接反复执行 `helm install` 观察集群状态。实际上 `helm template my-release ./my-chart -f values.yaml` 命令可在本地将模板渲染为完整的 Kubernetes YAML 并输出到标准输出，无需访问集群即可检查变量替换、缩进错误等模板问题，配合 `kubectl apply --dry-run=client -f -` 管道使用可进一步验证资源合法性。

---

## 知识关联

**依赖 Kubernetes 基础知识**：理解 Helm Charts 需要熟悉 Deployment、Service、ConfigMap、Secret、Namespace 等 Kubernetes 原生资源类型，因为 Chart 模板本质上是这些资源 YAML 的参数化包装。不了解 `Pod` 的 `resource.limits` 字段含义，就无法正确设置 Chart 的 GPU 资源请求参数。

**依赖 Docker 镜像管理**：Chart 中的 `image.repository` 和 `image.tag` 直接引用 Docker 镜像地址，掌握镜像命名规范和私有仓库认证（`imagePullSecrets`）是配置 Chart 的必要前提。AI 场景下模型镜像通常数 GB，合理设置 `imagePullPolicy: IfNotPresent` 可避免每次部署都重新拉取镜像。

**延伸至 GitOps 实践**：Helm Charts 是 ArgoCD 和 Flux 等 GitOps 工具的主要部署单元。将 Chart 的 `values.yaml` 存储在 Git 仓库中，由 GitOps 控制器监听变更并自动同步到集群，是构建 AI 平台持续部署流水线的标准模式。掌握 Helm 是进入 GitOps 工作流的必要技术准备。