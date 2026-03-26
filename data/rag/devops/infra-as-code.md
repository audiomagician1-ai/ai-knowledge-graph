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
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
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

基础设施即代码（Infrastructure as Code，简称 IaC）是一种通过机器可读的配置文件来管理和配置计算机基础设施的方法，而非依赖交互式工具或手动操作。其核心思想是：服务器、网络、存储、数据库等基础设施资源的创建、修改和销毁，全部由声明式或命令式的代码文件描述，并可纳入版本控制系统统一管理。

IaC 的概念在 2000 年代中期随云计算的兴起而成熟。2006 年 AWS 推出 EC2 和 S3 服务后，手动点击控制台创建资源的方式很快暴露出不可复现、配置漂移（Configuration Drift）等问题。2011 年 HashiCorp 创始人 Mitchell Hashimoto 开始开发 Vagrant，2014 年发布的 Terraform 成为 IaC 领域最具代表性的工具，将"声明目标状态"的理念推向主流。

在 AI 工程领域，IaC 的重要性尤为突出。训练一个大型模型可能需要临时拉起数百台 GPU 实例，实验完成后立即销毁；推理服务则需要根据请求量自动弹性扩缩容。如果这些操作依靠人工执行，不仅效率低下，还会因环境不一致导致"在我机器上能跑"的经典难题。IaC 让整个 GPU 集群的拓扑结构像 Python 代码一样可以被 `git diff` 追踪和审查。

---

## 核心原理

### 声明式与命令式的本质区别

IaC 有两种编写风格，理解其差异是使用任何工具的前提。

**声明式（Declarative）**：描述期望的最终状态，由工具决定如何达到该状态。Terraform 的 HCL 语言和 Kubernetes 的 YAML 清单均属此类。例如声明"需要 3 个 GPU 节点的 Kubernetes 集群"，Terraform 会自动计算当前状态与目标状态的差异（`terraform plan` 输出的 diff），仅执行必要的变更操作。

**命令式（Imperative）**：按顺序描述每一步操作。Ansible 的 Playbook 和 AWS CDK（使用 Python/TypeScript 编写）偏向此风格。命令式的优点是逻辑更直观，但重复执行时需要手动处理幂等性问题。

Terraform 的状态管理文件 `terraform.tfstate` 是声明式 IaC 的核心机制：它记录了当前真实基础设施的快照，每次执行 `terraform apply` 都会将 `.tfstate` 与配置文件对比，生成变更计划。

### 幂等性（Idempotency）

IaC 的关键性质是幂等性：对同一段配置代码执行一次和执行 N 次，最终系统状态相同。这与普通脚本（如 Shell）本质不同——执行 `mkdir /data` 两次会报错，而 Terraform 的 `resource "aws_s3_bucket" "model_artifacts"` 声明无论运行多少次，始终只存在一个该名称的 S3 桶。

Ansible 通过模块内置幂等性保障，例如 `file` 模块的 `state: directory` 参数会检查目录是否存在再决定是否创建；`apt` 模块的 `state: present` 不会重复安装已有软件包。

### 配置漂移与状态一致性

"配置漂移"指基础设施的实际状态与代码描述的期望状态之间产生偏差，通常由临时的手动操作引起（俗称"雪花服务器"问题）。IaC 通过持续的状态检测来消除漂移：Terraform 的 `terraform refresh` 命令可以重新拉取云端真实状态，`terraform plan` 会检测并报告所有不一致之处。

在 AI 工程中，一个典型漂移场景是：工程师为了调试直接 SSH 进入训练节点修改了 CUDA 驱动版本，而这一修改未记录在任何 IaC 文件中，导致下次用同一套代码拉起新节点时，两批节点的驱动版本不一致，引发分布式训练中的隐性 Bug。

### 模块化与可复用性

Terraform 支持将重复使用的资源组合封装为**模块（Module）**。一个典型的 AI 训练基础设施模块可能包含：VPC 网络配置、GPU 实例组（Auto Scaling Group）、共享文件系统（如 AWS FSx for Lustre）、IAM 角色权限。团队只需传入参数（如 `instance_type = "p4d.24xlarge"`、`node_count = 8`）即可复用该模块，无需重写底层资源定义。

---

## 实际应用

### AI 训练集群的按需拉起与销毁

使用 Terraform + AWS，可以用约 50 行 HCL 代码定义一个由 8 台 `p3.16xlarge`（每台 8 块 V100 GPU）组成的训练集群，配置置放群组（Placement Group）保障节点间低延迟网络互通，挂载 FSx for Lustre 文件系统共享训练数据集。训练任务提交后执行 `terraform destroy`，整个集群在 10 分钟内完全销毁，避免产生闲置费用。与手动操作相比，这一流程从原来需要 2 小时的人工操作缩短至 `terraform apply` 的约 8 分钟自动化执行。

### MLflow 追踪服务器的版本化部署

将 MLflow 追踪服务器的部署配置（包括 RDS PostgreSQL 数据库、ECS Fargate 任务定义、ALB 负载均衡器、S3 Artifact Store 桶）全部用 Terraform 代码描述，提交至 Git 仓库。每次更新 MLflow 版本时，只需修改 `container_image = "mlflow:2.11.0"` 中的版本号并提交 Pull Request，经过 Code Review 后合并即可自动触发部署，全程留有完整的变更审计日志。

### Kubernetes 集群的多环境管理

使用 Terraform 的 Workspace 功能，同一套代码配合不同变量文件（`dev.tfvars`、`staging.tfvars`、`prod.tfvars`）可以管理开发、预发布、生产三套独立的 EKS 集群，确保环境间配置一致性的同时允许合理的差异化配置（如生产环境使用 3 可用区高可用布局，而开发环境仅使用单可用区降低成本）。

---

## 常见误区

**误区一：IaC 只是"自动化脚本的升级版"**
IaC 与 Shell 脚本的根本区别不在于"更长"或"更复杂"，而在于**状态管理**和**幂等性**。Shell 脚本描述"做什么操作"，IaC 描述"目标是什么状态"。一个创建 EC2 实例的 Shell 脚本每次运行都会创建新实例；而 Terraform 的同一段代码无论运行多少次，都只维护一个该名称的实例。混淆这两者会导致使用 Terraform 时仍用命令式思维编写 `null_resource` 配合 `local-exec`，完全丧失声明式的优势。

**误区二：`terraform.tfstate` 文件可以直接提交到 Git**
`.tfstate` 文件中包含敏感信息（数据库密码、API 密钥等明文），并且在团队协作时多人同时操作会产生状态文件冲突。正确做法是使用**远程后端（Remote Backend）**，如 Terraform Cloud、AWS S3 + DynamoDB（利用 DynamoDB 实现状态锁，防止并发写入）。将 `.tfstate` 提交 Git 是一个严重的安全漏洞，GitHub 上因此泄露云账号凭证的事故屡见不鲜。

**误区三：IaC 仅适用于云资源**
IaC 工具的应用范围远超公有云 VM。Terraform 通过 Provider 生态（截至 2024 年已超过 3000 个 Provider）可以管理 GitHub 仓库权限配置、Datadog 监控告警规则、Cloudflare DNS 记录、Kubernetes 命名空间和 RBAC 策略，甚至 Snowflake 数据仓库的表结构。在 AI 工程中，将 Weights & Biases 的项目配置、Grafana 的模型监控看板定义纳入 IaC 管理，与基础设施代码统一版本化，是更完整的 IaC 实践。

---

## 知识关联

**与 Docker 基础的关联**：Docker 容器本身定义了应用运行环境的"不可变性"，而 IaC 将这一不可变性原则延伸至整个基础设施层。Dockerfile 描述镜像构建过程，Terraform/Ansible 描述运行这些容器所需的网络、存储、计算资源，两者共同构成从代码到生产环境的完整"基础设施即代码"链条。Kubernetes 的 `Deployment` YAML 清单本身也是 IaC 的具体体现，是学习过 Docker 后自然延伸的声明式配置实践。

**通向 GitOps 的路径**：IaC 解决了"如何用代码描述基础设施"的问题，而 GitOps 在此基础上进一步规定了**变更的工作流程**：所有基础设施变更必须以 Git Pull Request 的形式提交，由 CI/CD 流水线（如 ArgoCD、Flux）自动将 Git 仓库中的代码状态