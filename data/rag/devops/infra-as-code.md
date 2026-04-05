---
id: "infra-as-code"
concept: "基础设施即代码"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 6
is_milestone: false
tags: ["自动化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 基础设施即代码

## 概述

基础设施即代码（Infrastructure as Code，简称 IaC）是一种通过机器可读的配置文件来定义、部署和管理计算基础设施的方法，而非依赖手动操作或交互式配置工具。其核心思想是将服务器、网络、数据库、存储等基础设施资源的配置完全用代码描述，从而使基础设施的创建和修改像软件开发一样可追踪、可复现、可审查。

IaC 的概念随着云计算和 DevOps 运动兴起而普及，HashiCorp 在 2014 年发布的 Terraform 是目前最广泛使用的 IaC 工具之一，而 AWS CloudFormation 则于 2011 年成为云厂商提供 IaC 能力的早期代表。在 AI 工程领域，模型训练集群、GPU 节点池、特征存储和推理服务的基础设施往往需要频繁扩缩，手动配置极易引发环境不一致和"配置漂移"（Configuration Drift）问题，IaC 正是解决这些问题的核心手段。

与 Docker 容器化解决应用运行环境一致性不同，IaC 解决的是**底层资源本身**的一致性——即在哪台机器上运行、网络如何打通、存储如何挂载、安全组如何设置。这两个层次共同构成了 AI 系统端到端的可重复部署能力。

---

## 核心原理

### 声明式 vs 命令式两种范式

IaC 工具分为两种主要范式。**声明式（Declarative）**要求用户只描述"期望的最终状态"，工具自动计算达到该状态所需的操作；Terraform 和 Kubernetes 的 YAML 均属此类。**命令式（Imperative）**要求用户逐步描述"如何操作"，Ansible 的 Playbook 在某种程度上混合了两者，但 Shell 脚本是最典型的命令式做法。

声明式方法具有幂等性（Idempotency）优势：无论执行多少次，结果都与预期状态一致。例如，一段 Terraform 代码声明"创建 3 个 GPU 节点的 Kubernetes 节点池"，即使执行 100 次，系统也只保持 3 个节点，而不会累加为 300 个。

### 状态管理与漂移检测

Terraform 通过维护一个 **state 文件**（`terraform.tfstate`）来记录当前实际资源与代码描述之间的映射关系。每次执行 `terraform plan` 时，工具会对比 state 文件、实际云端资源和代码三者的差异，生成变更计划（Execution Plan），明确列出哪些资源将被创建（`+`）、修改（`~`）或销毁（`-`）。

配置漂移是指基础设施的实际状态偏离了代码定义的状态（通常由人工控制台操作引起）。IaC 的 `terraform refresh` 或 `pulumi up --refresh` 命令可主动检测并修正漂移，这在 AI 平台运维中至关重要——例如，某工程师手动为训练节点扩充了内存，此漂移会在下次 IaC 部署时被发现并可按需处理。

### 模块化与 DRY 原则

IaC 支持将重复使用的资源组合抽象为**模块（Module）**。在 Terraform 中，一个模块可以封装"创建一个 AI 训练集群"所需的 VPC、子网、安全组、GPU 节点池等完整资源组合，其他团队只需传入参数（如 `gpu_count = 8`, `instance_type = "A100"`）即可复用。这遵循了软件工程的 DRY（Don't Repeat Yourself）原则，避免多个业务线各自维护相似但略有差异的基础设施配置代码。

Terraform 模块调用语法示例：
```hcl
module "ai_training_cluster" {
  source        = "./modules/gpu-cluster"
  gpu_count     = 8
  instance_type = "nvidia-a100"
  region        = "us-east-1"
}
```

---

## 实际应用

**AI 模型训练环境快速复现**：某团队使用 Terraform + Ansible 组合，将一套包含 16 块 A100 GPU、100Gbps 网络互联、共享 NFS 存储的分布式训练集群完整编码。新实验开始时，执行 `terraform apply` 约 8 分钟即可完整创建集群；实验结束后执行 `terraform destroy` 释放资源，避免闲置计费。整个流程无需人工登录控制台点击。

**多环境一致性管理**：AI 工程中常见 dev / staging / production 三套环境。使用 IaC 时，只需通过不同的变量文件（`dev.tfvars`, `prod.tfvars`）控制规格差异（如 dev 用 4 块 GPU，prod 用 64 块），而网络拓扑、安全策略、监控配置等保持完全一致，从而消除"在开发环境能跑但在生产挂掉"的环境差异问题。

**推理服务弹性扩缩**：结合 Kubernetes 的 HPA（Horizontal Pod Autoscaler）与 Terraform 管理的节点自动伸缩组，AI 推理服务可在请求量激增时自动扩展 GPU 节点，并在低峰时自动回收，全程由代码定义触发条件和边界（如最小 2 节点，最大 20 节点，CPU 利用率超过 70% 时触发）。

---

## 常见误区

**误区一：IaC 只是把 Shell 脚本换了个格式**。Shell 脚本是命令式的，不具有幂等性，重复执行会产生副作用（例如重复创建同名资源会报错）。IaC 工具的状态管理和 diff 计算机制从根本上不同于脚本执行，它理解资源之间的依赖图（Dependency Graph），能自动决定创建顺序，而 Shell 脚本需要手动维护这一逻辑。

**误区二：state 文件可以直接手动编辑或提交到公共仓库**。`terraform.tfstate` 文件包含敏感信息（如数据库密码、访问密钥），且手动修改极易破坏资源与状态的映射关系，导致后续操作意外删除生产资源。正确做法是将 state 存储在加密的远程后端（如 AWS S3 + DynamoDB 锁、Terraform Cloud），并通过 `.gitignore` 排除本地 state 文件。

**误区三：使用 IaC 后就不需要了解底层云服务**。IaC 工具只是操作云 API 的抽象层，若不理解 VPC、子网、IAM 角色等概念的语义，编写出的代码可能在语法上正确但在安全或网络配置上存在严重缺陷。例如，错误地将 AI 训练数据存储的 S3 桶设置为 `acl = "public-read"` 会直接导致数据泄露。

---

## 知识关联

**与 Docker 基础的关系**：Docker 解决容器镜像和运行时环境的一致性，IaC 解决承载这些容器的基础设施资源的一致性。在实践中，Terraform 负责创建 EKS 或 GKE 集群，Docker 镜像在其上运行，两者分工明确，共同保障 AI 工作负载的全链路可重复性。掌握 Docker 之后学习 IaC，可以将"环境一致性"的思维从容器层延伸到资源层。

**通往 GitOps 的关键一步**：GitOps 是将 IaC 与 Git 工作流深度结合的运维范式，要求基础设施的任何变更都必须通过 Git Pull Request 审核后才能应用，工具（如 Flux 或 ArgoCD）监听 Git 仓库变化并自动同步集群状态。没有 IaC 将基础设施代码化，GitOps 就无从实现——Git 无法追踪在控制台手动点击的操作。因此，IaC 是实践 GitOps 的前提条件，学习 IaC 的模块化和状态管理后，GitOps 的分支策略和 CD 流水线设计将水到渠成。