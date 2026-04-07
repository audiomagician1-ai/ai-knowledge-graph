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


# 基础设施即代码（Infrastructure as Code）

## 概述

基础设施即代码（Infrastructure as Code，简称 IaC）是指用声明式或命令式的代码文件来定义、配置和管理计算基础设施（服务器、网络、数据库、负载均衡器等），而非通过手动点击云控制台或执行一次性命令来完成。这些代码文件与应用程序源代码一样，存储在版本控制系统中，可以被审查、回滚和复用。

IaC 的概念在 2000 年代随着虚拟化技术普及而萌芽，2011 年前后以 Chef、Puppet 为代表的配置管理工具推动了它的第一波发展。真正的里程碑是 2014 年 HashiCorp 发布 Terraform 0.1，它引入了"声明式描述目标状态"的思路，用 HCL（HashiCorp Configuration Language）描述期望的云资源形态，工具自动计算出当前状态与目标状态的差异并执行变更。此后 AWS 推出 CloudFormation、Google 推出 Deployment Manager，各大云厂商也相继跟进。

IaC 的核心价值在于消除"配置漂移"（Configuration Drift）：在传统手动运维中，生产环境和测试环境常因不同操作员的细微差异逐渐偏离，导致"在我机器上能跑"的经典问题。IaC 将基础设施的预期状态编码化，每次部署都从同一份代码出发，环境一致性得到保证。

## 核心原理

### 声明式 vs. 命令式

IaC 工具分为两大范式。**声明式**工具（如 Terraform、CloudFormation）要求开发者描述"最终应该是什么"，工具自行规划执行步骤。例如在 Terraform 中：

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
}
```

这段代码告诉 Terraform：存在一个 EC2 实例，使用指定 AMI 和机型——无论当前没有这个实例还是已有旧实例，Terraform 都会计算出 `plan`，再执行 `apply` 到达目标状态。**命令式**工具（如 Pulumi 使用 Python/TypeScript、AWS CDK）则让开发者用通用编程语言编写逻辑，可以使用循环、条件和抽象类，灵活性更高，但理解执行顺序的心智负担也更重。

### 状态文件（State File）机制

Terraform 使用 `terraform.tfstate` 文件记录上一次已知的真实基础设施状态，以 JSON 格式存储每个受管资源的属性和 ID。每次执行 `terraform plan` 时，Terraform 将本地代码的期望状态、远端云 API 的实际状态与 `tfstate` 三者对比，生成差异计划（Diff Plan）。如果多人同时修改代码而状态文件未加锁，会引发竞态条件，因此生产环境必须将状态文件存储在支持锁定的后端（如 S3 + DynamoDB 或 Terraform Cloud），以防止并发写入造成状态损坏。

### 模块化与复用

Terraform 通过 **Module** 机制封装可复用的基础设施模式。一个 VPC 模块可以接收 `cidr_block`、`availability_zones` 等输入变量，输出子网 ID 供其他模块引用。Terraform Registry 上有超过 15,000 个公开模块（截至 2024 年），覆盖 AWS EKS、GCP GKE 等常见场景，避免重复编写样板代码。Pulumi 的复用机制则直接借助 npm 或 PyPI 包管理，可以像引用普通库一样引用基础设施组件。

### 幂等性保证

IaC 工具的核心承诺是**幂等性**：无论执行多少次相同的代码，结果都与执行一次相同。这依赖于工具在执行前先查询实际状态，仅对有差异的资源发出 API 调用。CloudFormation 通过 Stack 的变更集（Change Set）机制实现幂等——每次更新模板时先创建 Change Set 预览，确认后才执行，防止意外删除或替换资源。

## 实际应用

**多环境一致性管理**：电商公司通常需要开发、测试、预发布、生产四套环境。使用 Terraform Workspace 或 Terragrunt 的目录结构，可以用同一套模块代码配合不同的变量文件（`dev.tfvars`、`prod.tfvars`）分别部署，生产环境的实例规格用 `m5.2xlarge`，开发环境用 `t3.medium`，其余网络拓扑逻辑完全相同，大幅减少配置差异引入的 bug。

**灾难恢复演练**：某金融机构将整个东南亚区域的 AWS 架构（包含 47 个 VPC、230+ 安全组规则）全部以 Terraform 代码管理。每季度灾备演练时，只需在新区域执行 `terraform apply`，约 25 分钟内即可重建等效环境，而此前手动重建需要两个工程师工作三天。

**CI/CD 流水线集成**：在 GitHub Actions 或 GitLab CI 中，典型的 IaC 流水线包含以下阶段：`terraform init`（下载 Provider 插件）→ `terraform validate`（语法校验）→ `terraform plan`（输出变更预览作为 Pull Request 评论）→ 人工审批 → `terraform apply`（仅在合并主干后执行）。这将基础设施变更纳入与应用代码相同的 Code Review 流程。

## 常见误区

**误区一：IaC 只是自动化脚本的升级版**。许多初学者将 IaC 与 Bash 脚本或 Ansible Playbook 混为一谈。关键区别在于：Bash 脚本是命令序列，对当前状态无感知，多次执行同一脚本可能创建重复资源或报错；而 Terraform 的 `plan`-`apply` 循环始终基于状态差异操作，具有真正的幂等性。Ansible 虽支持幂等模块，但其设计重心是配置管理（操作系统层面），而非云资源生命周期管理。

**误区二：声明式代码天然不需要关心执行顺序**。初学者常以为 Terraform 会自动处理所有依赖关系，无需思考顺序。实际上，当资源间存在隐式依赖（如 Lambda 函数需要先创建 IAM Role）而未通过 `depends_on` 或引用关系显式声明时，Terraform 可能并发创建资源，导致权限未就绪的错误。显式依赖声明是写好 Terraform 代码的必要技能。

**误区三：将 tfstate 文件提交到 Git 仓库**。`terraform.tfstate` 文件包含资源 ID、IP 地址、甚至明文密码等敏感信息，绝不能提交到版本控制。正确做法是将其存储在加密的远端后端，并在 `.gitignore` 中排除所有 `*.tfstate` 和 `*.tfstate.backup` 文件。

## 知识关联

学习 IaC 不需要特定前置知识，但熟悉至少一个云平台（AWS/GCP/Azure）的基本概念（VPC、子网、安全组、计算实例）会大幅降低上手难度，因为 IaC 工具本质上是这些 API 的代码化封装。

掌握 IaC 之后，自然延伸至 **GitOps** 范式——GitOps 将 IaC 进一步规范化：以 Git 仓库作为基础设施状态的唯一可信来源（Single Source of Truth），通过 Pull Request 触发所有变更，由 Argo CD 或 Flux 等工具持续对比 Git 中的期望状态与集群实际状态，自动拉平差异。IaC 解决了"如何用代码描述基础设施"，而 GitOps 解决了"如何用 Git 工作流治理这些代码的变更流程"，两者共同构成现代云原生运维的基础。