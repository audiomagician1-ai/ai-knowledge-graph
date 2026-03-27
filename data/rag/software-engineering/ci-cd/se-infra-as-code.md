---
id: "se-infra-as-code"
concept: "基础设施即代码"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 3
is_milestone: false
tags: ["IaC"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.552
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 基础设施即代码

## 概述

基础设施即代码（Infrastructure as Code，简称 IaC）是指通过声明式或命令式的代码文件来定义、配置和管理计算基础设施（服务器、网络、数据库、存储等）的工程实践，而非通过手动点击云控制台或执行脚本命令来完成这些操作。使用 IaC，一个 VPC 网络的创建过程被写成文本文件，可以被版本控制、代码审查和自动化部署，就像管理应用程序源代码一样。

IaC 的概念随着云计算的普及在 2010 年代逐渐成熟。2014 年 HashiCorp 发布 Terraform，将声明式 IaC 推向主流；更早的 2011 年，AWS 已推出 CloudFormation，允许用户用 JSON/YAML 模板描述 AWS 资源。2019 年 Pulumi 出现，进一步允许开发者用 TypeScript、Python、Go 等通用编程语言编写基础设施定义，降低了专用 DSL 的学习门槛。这三款工具至今仍是 IaC 领域的代表性产品。

IaC 的核心价值在于**消灭"雪花服务器"问题**——手动配置的服务器在时间推移后变得独一无二、难以复现，而 IaC 通过代码强制基础设施的一致性与可重复性，使得在五分钟内创建与生产环境完全相同的测试环境成为可能。

## 核心原理

### 声明式 vs 命令式模型

IaC 主要分两种编写风格。**声明式**要求用户描述"期望状态"，工具负责计算差异并执行变更，Terraform 和 CloudFormation 均采用此模型。例如，在 Terraform 的 HCL（HashiCorp Configuration Language）中写：

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}
```

Terraform 会自动检测当前云端状态与代码描述之间的差异，仅执行必要操作，不需要用户明确写出"先查询是否存在，再决定创建或更新"的逻辑。**命令式**风格则需要用户编写具体操作步骤，Pulumi 虽然使用通用语言，但其执行引擎底层仍是声明式状态管理，并非纯命令式。

### 状态管理机制

Terraform 使用一个名为 `terraform.tfstate` 的 JSON 文件记录当前已部署的真实资源状态。每次执行 `terraform plan` 时，工具会对比三方数据：代码中的期望状态、状态文件中的上次已知状态、以及从云 API 查询到的当前实际状态。若团队协作，该状态文件必须存储在 S3 Bucket 或 Terraform Cloud 等远程后端，并配合 DynamoDB 实现分布式锁，防止多人同时运行 `terraform apply` 导致状态冲突。CloudFormation 将状态托管在 AWS 服务端，无需用户自行维护状态文件，这是其对新手更友好的原因之一。

### 模块化与可复用性

Terraform 通过**模块（Module）**实现代码复用，一个模块是一组 `.tf` 文件的集合，接受输入变量（`variable`）并输出值（`output`）。Terraform Registry（registry.terraform.io）上托管了超过 15,000 个社区模块，例如 `terraform-aws-modules/vpc/aws` 模块封装了创建完整 AWS VPC（含子网、路由表、NAT 网关）所需的数百行配置，调用者只需传入 CIDR 块和可用区列表即可。Pulumi 的复用单元是普通函数和类，可直接利用 npm、PyPI 等生态的包管理能力。

### 不可变基础设施原则

IaC 通常与**不可变基础设施**理念配合：服务器一旦部署就不再在运行时修改，需要变更时销毁旧实例、以新配置重建。Terraform 的 `lifecycle { create_before_destroy = true }` 配置块正是用于实现这种"先建后删"的滚动替换策略，避免单实例更新期间出现服务中断。

## 实际应用

**多环境管理**：一家公司通常需要 dev、staging、production 三套相同拓扑的环境。使用 Terraform Workspace 或在目录结构上按环境隔离，通过不同的 `terraform.tfvars` 传入差异化参数（如实例规格 `t3.micro` 用于 dev，`m5.large` 用于 prod），同一套模块代码即可驱动三套环境，确保环境间差异完全可见且受版本控制。

**灾难恢复演练**：某电商平台将全部基础设施描述在 Terraform 代码中，当主区域 us-east-1 模拟故障时，运维工程师只需修改一个变量 `region = "us-west-2"` 并执行 `terraform apply`，即可在备用区域快速重建等价架构，将 RTO（恢复时间目标）从数小时缩短至约 30 分钟。

**合规审计**：Terraform 代码提交到 Git 仓库后，每一次基础设施变更都有对应的 commit 记录，包含变更时间、操作人、变更内容。配合 Checkov 或 tfsec 等静态分析工具扫描 Terraform 代码，可在 PR 阶段自动检测安全组是否开放了 `0.0.0.0/0` 的 22 端口等违规配置。

## 常见误区

**误区一：IaC 只适合大型团队**。许多开发者认为 Terraform 配置复杂，仅对百人团队才值得投入。实际上即使是个人项目，IaC 也能解决"半年后忘记自己创建了哪些 AWS 资源"和"账单意外暴增找不到原因"的痛点。Pulumi 允许用已熟悉的 Python 编写配置，单人项目的上手成本不超过半天。

**误区二：执行 IaC 代码后云资源立即与代码完全一致**。实际上云 API 存在最终一致性，某些资源（如 AWS IAM 策略传播）在 `terraform apply` 完成后可能仍需数秒至数分钟才能在所有区域生效。此外，若有人手动在控制台修改了资源，下次 `terraform plan` 才会检测到"配置漂移（drift）"，IaC 本身不是实时监控工具。

**误区三：Terraform 和 Ansible 是竞争产品**。Terraform 专注于资源的**供给（provisioning）**——创建和销毁云资源；Ansible 专注于**配置管理（configuration management）**——在已有服务器上安装软件、修改配置文件。两者在工程实践中经常组合使用，Terraform 建好虚拟机，Ansible 负责在其上部署 Nginx 和应用程序。

## 知识关联

IaC 是实现 **GitOps** 的前提条件：只有当基础设施已经被代码化并托管到 Git 仓库，才能进一步实现"以 Git 为唯一可信数据源，通过 Pull Request 驱动基础设施变更"的 GitOps 工作流。工具如 Atlantis 可监听 GitHub PR 事件，自动对 Terraform 代码执行 `plan` 并将结果评论到 PR 中，人工审批后触发 `apply`，这是 IaC 向 GitOps 演进的典型路径。

在 CI/CD 流水线中，IaC 通常作为独立的"基础设施流水线"与应用代码流水线并行存在。应用流水线负责构建 Docker 镜像并推送到 ECR；基础设施流水线负责确保 ECS Cluster 和 Task Definition 的配置符合代码描述，两条流水线通过镜像标签变量耦合，共同构成完整的持续交付体系。