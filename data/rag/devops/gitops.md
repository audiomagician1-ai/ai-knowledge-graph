---
id: "gitops"
concept: "GitOps"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["argocd", "flux", "declarative"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# GitOps

## 概述

GitOps 是由 Weaveworks 公司于 2017 年由 Alexis Richardson 首次提出的运维方法论，其核心思想是将 Git 仓库作为系统基础设施和应用配置的**唯一事实来源**（Single Source of Truth）。与传统的命令式运维不同，GitOps 要求所有对生产环境的变更必须先以声明式方式提交到 Git，再由自动化系统将集群实际状态与 Git 中定义的期望状态进行对比并同步，而不是由工程师直接通过 `kubectl apply` 或 SSH 登录服务器来修改环境。

GitOps 区别于普通 CI/CD 的关键在于方向性差异：传统 CI/CD 是"推送式"（Push-based），流水线触发后主动将制品推送到目标环境；而 GitOps 引入了"拉取式"（Pull-based）模式，部署在集群内部的 Operator（如 Flux 或 ArgoCD）持续监听 Git 仓库变化，主动将期望状态拉取并应用到集群。这一设计从根本上消除了流水线需要持有集群凭证的安全风险。

在 AI 工程的 MLOps 场景中，GitOps 尤为重要，因为模型部署配置（如 Kubernetes 的 Deployment YAML、推理服务的副本数、GPU 资源限制）需要经过可审计、可回滚的版本管理，避免"配置漂移"导致线上模型版本与预期不一致的问题。

## 核心原理

### 四大原则

GitOps 由 OpenGitOps 社区于 2021 年正式规范化，定义了四条核心原则：

1. **声明式（Declarative）**：系统的期望状态必须以声明式方式描述，例如 Kubernetes 的 YAML 文件描述"应运行 3 个副本的 resnet50-serving 容器"，而非"执行 `scale --replicas=3` 命令"。
2. **版本化且不可变（Versioned and Immutable）**：期望状态存储在 Git 中，每次变更产生一个不可篡改的提交记录（commit hash），提供完整的变更历史。
3. **自动拉取（Pulled Automatically）**：已获批准的期望状态由软件 Agent 自动应用，无需人工干预触发部署。
4. **持续核对（Continuously Reconciled）**：软件 Agent 持续比对实际状态与期望状态，发现偏差时立即触发自动修复，防止配置漂移。

### 协调循环（Reconciliation Loop）

GitOps 的运行核心是**协调循环**，其逻辑可以表示为：

```
DesiredState(Git) ≠ ActualState(Cluster)  →  Apply(Diff)
DesiredState(Git) = ActualState(Cluster)  →  No-Op
```

以 ArgoCD 为例，其默认协调间隔为 **3 分钟**，同时支持 Git 仓库 Webhook 触发即时协调。当工程师向 `main` 分支合并一个将 `model-server` 镜像从 `v1.2.0` 更新到 `v1.3.0` 的 PR 时，ArgoCD 检测到变更后会在数秒内计算差异并触发 Kubernetes 滚动更新，整个过程无需人工执行任何部署命令。

### 仓库结构策略：App-of-Apps 与多环境管理

在 AI 工程中，常见的 GitOps 仓库结构将"应用代码仓库"与"配置仓库"分离：

- **应用仓库**：存放模型训练代码、推理服务代码，CI 流水线在此构建并推送镜像到容器镜像仓库。
- **配置仓库（GitOps 仓库）**：存放各环境的 Kubernetes YAML 或 Helm values，如 `envs/staging/model-server/values.yaml` 和 `envs/production/model-server/values.yaml`。

分离的原因是：镜像构建成功后，CI 系统只需修改配置仓库中对应环境的镜像标签字段，由 GitOps Operator 完成实际部署，实现关注点分离，同时确保生产环境配置变更必须经过 PR Review 和审批，形成强制审计门控。

### 安全模型：消除外部凭证暴露

传统 Push-based CI/CD 需要将 `KUBECONFIG` 或云服务商密钥存储在 CI 平台的 Secret 中，一旦 CI 系统被攻破，攻击者可直接访问生产集群。GitOps 的 Pull-based 模型将 Operator 部署在集群内部，Operator 拥有集群内权限但不对外暴露，外部系统（包括 CI）对集群没有直接写权限，大幅缩小了攻击面。

## 实际应用

**AI 模型推理服务的渐进式发布**：在生产环境中部署新版本的 BERT 模型时，工程师向配置仓库提交一个将 Argo Rollouts 策略中金丝雀权重从 0% 调整为 10% 的 PR，通过 Review 后 ArgoCD 自动执行金丝雀发布，观察 P99 延迟和错误率指标，若指标正常再提交后续 PR 逐步将流量从 10% 增加到 100%，每一步均有 Git commit 记录可追溯。

**灾难恢复**：当集群因误操作导致 GPU 节点上的推理服务配置被错误修改时，工程师只需执行 `git revert` 回滚配置仓库的提交，ArgoCD 会在下一个协调周期内将集群状态恢复到回滚后的版本，整个恢复操作的唯一入口是 Git，无需记忆或重现原始部署命令。

**多集群联邦管理**：一个 AI 平台团队使用 Flux 的 `Kustomization` 资源，在同一个配置仓库中管理分布于三个地域的推理集群，通过 `clusters/us-west/` 、`clusters/eu-central/`、`clusters/ap-east/` 目录结构区分配置，实现跨集群的一致性部署和差异化配置管理。

## 常见误区

**误区一：GitOps 等同于"把 kubectl 命令放进 Git"**

GitOps 要求配置必须是**声明式**的，存放 `kubectl scale deployment model-server --replicas=3` 这类命令行脚本到 Git 并不是 GitOps。真正的 GitOps 配置应是描述期望状态的 YAML 资源定义，Operator 根据声明的状态自主决定如何达到目标，而非执行预设命令。

**误区二：GitOps 可以替代所有 CI 流程**

GitOps 专注于**CD（持续交付）** 部分，即从制品到部署环境的同步。模型训练代码的单元测试、镜像构建、集成测试等 CI 环节仍需要传统流水线工具（如 GitHub Actions、Jenkins）完成，GitOps Operator 的职责起点是"已有经过验证的制品可以部署"之后，两者协作而非替代关系。

**误区三：只要用了 ArgoCD/Flux 就是在做 GitOps**

如果团队安装了 ArgoCD 但仍然允许工程师通过 `kubectl exec` 或直接修改 Kubernetes 资源来绕过 Git，则集群实际状态随时可能偏离 Git 定义的期望状态，这只是"装了一个 GitOps 工具"而非真正实践 GitOps。真正的 GitOps 需要通过 RBAC 和审计策略强制所有变更路径都经过 Git。

## 知识关联

GitOps 直接建立在**基础设施即代码（IaC）** 的基础上：IaC 定义了如何用声明式文件描述基础设施，GitOps 进一步规定这些文件的存储、审核和应用方式必须以 Git 为中心。没有将基础设施配置声明化，GitOps 无从落地。

GitOps 同时依赖 **CI/CD 流水线**完成镜像构建和测试环节，ArgoCD 的 Image Updater 插件可以监听镜像仓库的新标签并自动向配置仓库提交镜像更新 commit，实现 CI 流水线与 GitOps 配置仓库的自动化衔接。

**GitFlow 工作流**与 GitOps 的配置仓库策略密切相关：多环境 GitOps 策略通常采用 `main` 分支对应生产环境、`staging` 分支对应预发布环境的分支策略，或采用基于目录的环境隔离配合单一 `main` 分支的扁平化策略，团队需根据发布频率和审批流程选择适合的分支模型。
