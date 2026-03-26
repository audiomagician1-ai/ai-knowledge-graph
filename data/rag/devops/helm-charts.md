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

Helm Charts 是 Kubernetes 应用程序的打包格式，允许将一组相关的 Kubernetes 资源（Deployment、Service、ConfigMap、Ingress 等）打包成一个可版本化、可分发的单元。与手动管理数十个 YAML 文件相比，Helm Charts 将整个应用程序的基础设施定义封装在一个标准化目录结构中，并通过 Go 模板引擎（`text/template`）实现参数化配置。

Helm 于 2015 年由 Deis 公司的工程师创建，最初在 KubeCon 2015 上发布。2016 年项目捐献给 CNCF（Cloud Native Computing Foundation），Helm 3 于 2019 年 11 月发布，移除了备受批评的服务端组件 Tiller，改为纯客户端架构，直接使用 kubeconfig 凭证与 Kubernetes API Server 通信，从根本上解决了 Tiller 带来的 RBAC 权限过度集中问题。

对于 AI 工程的 MLOps/DevOps 场景，Helm Charts 的价值在于：一个 ML 推理服务可能同时需要 Deployment（运行模型服务器）、HorizontalPodAutoscaler（按请求量扩缩）、PersistentVolumeClaim（挂载模型权重文件）和 Service（对外暴露端口），若没有 Helm，这些资源需逐一手动部署且难以复用于开发、测试、生产三套环境。

---

## 核心原理

### Chart 目录结构

一个标准 Helm Chart 的目录布局固定如下：

```
mychart/
├── Chart.yaml          # Chart 元数据（名称、版本、appVersion）
├── values.yaml         # 默认参数值
├── templates/          # Go 模板文件（*.yaml, helpers.tpl）
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl    # 可复用的命名模板片段
└── charts/             # 子 Chart 依赖目录
```

`Chart.yaml` 中必须包含 `apiVersion`（Helm 3 使用 `v2`）、`name` 和 `version` 字段，其中 `version` 遵循语义化版本规范（SemVer 2.0），如 `1.4.2`，而 `appVersion` 则记录被打包应用本身的版本号（例如模型服务框架 Triton Inference Server 的版本 `22.12`），两者相互独立。

### Go 模板引擎与 values 注入

Helm 的核心机制是将 `values.yaml` 中的参数注入到 `templates/` 目录下的 Kubernetes 资源模板中。模板语法使用 `{{ .Values.key }}` 引用参数，使用 `{{ if }}...{{ end }}` 实现条件渲染，使用 `{{ range }}` 遍历列表。例如：

```yaml
# templates/deployment.yaml
spec:
  replicas: {{ .Values.replicaCount }}
  containers:
    - name: model-server
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
      resources:
        limits:
          nvidia.com/gpu: {{ .Values.gpu.limit }}
```

部署时通过 `--set` 或 `-f custom-values.yaml` 覆盖默认值，实现同一 Chart 跨环境复用：`helm install prod-inference ./mychart -f production-values.yaml`。

### Release 生命周期管理

Helm 将每次部署称为一个 **Release**，并在 Kubernetes 的 Secret 资源中以 `helm.sh/release.v1` 类型存储 Release 的完整状态（包括渲染后的 manifest 和 values）。这使得以下操作成为可能：

- **`helm upgrade`**：对比新旧 manifest，仅更新有变化的资源，并将 Release revision 号递增（如从 revision 3 升至 4）
- **`helm rollback <release> <revision>`**：回滚至指定历史版本，例如 `helm rollback my-model-service 2` 将配置恢复到 revision 2 的状态
- **`helm history`**：查看某 Release 的所有历史修订记录

默认情况下 Helm 保留最近 10 个 Release 历史记录（可通过 `--history-max` 调整），每条记录存储于集群内，无需外部数据库。

### Chart 依赖管理

`Chart.yaml` 中的 `dependencies` 字段允许声明子 Chart 依赖，类似于 `package.json`。例如一个 AI 平台 Chart 可以依赖官方 `postgresql` Chart（来自 `https://charts.bitnami.com/bitnami`，版本 `~12.0.0`）作为元数据存储。运行 `helm dependency update` 后，子 Chart 会被下载到 `charts/` 目录并锁定版本至 `Chart.lock` 文件，防止依赖漂移。

---

## 实际应用

**部署 Triton Inference Server**：在 Kubernetes 上为 LLM 推理服务创建 Helm Chart 时，`values.yaml` 中通常包含 `modelRepository`（对象存储路径，如 `s3://my-bucket/models`）、`gpuCount`（申请的 GPU 数量）和 `maxBatchSize` 等 AI 特有参数。通过 `-f production.yaml` 传入生产环境配置，可在不修改 Chart 源码的情况下将同一 Chart 复用于不同规模的推理集群。

**多环境配置分离**：团队通常维护 `values-dev.yaml`、`values-staging.yaml`、`values-prod.yaml` 三套文件，其中 dev 环境将 `replicaCount` 设为 1、不启用 HPA，而 prod 环境将 `replicaCount` 设为 3 并启用 `autoscaling.enabled: true`。这种模式避免了环境间配置混乱，且所有差异均通过 Git 版本控制追踪。

**使用 Artifact Hub 分发**：Chart 打包后（`helm package ./mychart` 生成 `.tgz` 文件）可推送至 OCI 兼容仓库（Helm 3.8.0 起正式支持 OCI Registry），例如 `helm push mychart-1.4.2.tgz oci://registry.example.com/charts`，团队成员随后通过 `helm install` 直接拉取，无需共享原始源代码。

---

## 常见误区

**误区一：混淆 `version` 与 `appVersion`**
许多初学者将 Chart 版本（`version: 1.2.0`）与应用版本（`appVersion: "2.28.0"`）视为同一字段，导致升级混乱。`version` 跟踪的是 Chart 模板和配置结构本身的变化，而 `appVersion` 仅作为描述性标签，Helm 不会基于 `appVersion` 做任何部署决策——实际镜像版本由 `values.yaml` 中的 `image.tag` 控制。

**误区二：在 `templates/` 中硬编码敏感信息**
将数据库密码或 API 密钥直接写入 Chart 的 `values.yaml` 并提交 Git 是严重的安全风险。正确做法是在模板中引用已预先存在的 Kubernetes Secret（`valueFrom.secretKeyRef`），或集成 External Secrets Operator，使 Chart 本身不包含任何明文凭证。

**误区三：认为 `helm upgrade` 等价于全量重建**
`helm upgrade` 并非删除所有资源后重新创建，而是通过三方合并（three-way merge）对比原始 Chart、当前集群状态和新 Chart 的差异，仅对发生变更的资源执行 patch 操作。这意味着如果某个 Deployment 被手动修改（kubectl edit），upgrade 时 Helm 会将其强制恢复为 Chart 定义的状态，导致"漂移"被覆盖——应始终通过 `helm upgrade` 而非 `kubectl edit` 来变更由 Helm 管理的资源。

---

## 知识关联

**前置知识衔接**：Helm Charts 的每个模板文件最终都会渲染成标准 Kubernetes YAML，因此需要掌握 Kubernetes 中 Deployment、Service、ConfigMap 等核心资源的结构——`templates/deployment.yaml` 中的字段（如 `spec.selector.matchLabels`）与直接编写 Kubernetes manifest 时完全相同，Helm 只是在外层包裹了参数化逻辑。Docker 基础同样必要，因为 Chart 中的容器镜像来源、`imagePullPolicy` 和镜像仓库认证（`imagePullSecrets`）均涉及 Docker 镜像管理知识。

**横向关联**：在 MLOps 流水线中，Helm Charts 通常与 ArgoCD 或 Flux 结合实现 GitOps——将 Chart 和 values 文件存储于 Git 仓库，CD 工具自动检测变更并触发 `helm upgrade`，形成完整的模型服务持续交付链路。Helm 的 `helm test` 子命令支持在 Release 部署后运行测试 Pod，可用于验证模型推理端点的健康状态。