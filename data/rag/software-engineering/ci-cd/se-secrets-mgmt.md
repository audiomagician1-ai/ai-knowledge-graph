---
id: "se-secrets-mgmt"
concept: "密钥管理"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 2
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 密钥管理

## 概述

密钥管理（Secret Management）是指在软件交付流水线中安全存储、分发和轮换密码、API密钥、数据库连接字符串、TLS证书等敏感凭证的系统性实践。在CI/CD环境中，自动化构建和部署脚本必须访问生产数据库、云平台API等资源，若凭证以明文形式硬编码在代码仓库中，攻击者一旦获取仓库权限即可横向渗透整个基础设施，因此密钥管理是自动化流水线安全的核心问题。

2021年Codecov供应链攻击事件是密钥管理失败的典型案例：攻击者篡改了Codecov的Bash Uploader脚本，导致数千家企业的CI环境变量（包含AWS密钥、GitHub Token等）被窃取，受害者涵盖Twilio、Hashicorp等知名公司。这一事件说明即便是"环境变量"这一常见做法，若缺乏额外保护层，同样面临严重风险。

密钥管理的核心目标是遵循**最小权限原则**：每个CI/CD任务只能获得完成其特定任务所需的最小凭证集合，凭证具有有限生命周期，使用后应自动过期。这与传统的静态长期凭证管理方式有本质区别。

---

## 核心原理

### 环境变量注入

最基础的CI/CD密钥管理方式是通过平台提供的加密变量存储注入环境变量。GitHub Actions、GitLab CI、Jenkins等平台均提供加密的Secret存储区：用户在平台UI中设置 `DB_PASSWORD=xxx`，流水线运行时该值被注入为环境变量，在日志中自动屏蔽（masked）。这种方式实现简单，但存在明显局限：密钥以静态方式长期存在，无自动轮换机制，且当多个项目共享密钥时管理成本极高。

### HashiCorp Vault动态密钥

HashiCorp Vault是企业级密钥管理的事实标准，其核心能力是**动态密钥（Dynamic Secrets）**。以数据库场景为例，Vault不存储一个静态数据库密码，而是在CI任务请求时实时调用数据库API创建一个临时账户，该账户附带TTL（Time-To-Live），例如设置 `ttl=1h`，流水线任务完成或TTL过期后账户自动撤销。Vault的访问控制基于策略（Policy），以HCL语言描述，例如：

```
path "secret/data/myapp/prod" {
  capabilities = ["read"]
}
```

CI Agent通过AppRole认证（包含RoleID + SecretID两因素）获取临时Token，再凭Token读取对应路径的密钥，整个过程实现了密钥的零静态暴露。

### OIDC无密钥认证

OpenID Connect（OIDC）是当前最先进的CI/CD凭证方案，其核心思想是**完全消除长期静态密钥**。以GitHub Actions与AWS的集成为例：GitHub OIDC Provider向每个工作流颁发一个短期JWT Token，该Token包含仓库名称、分支、工作流触发者等声明（Claims）；AWS IAM配置信任该GitHub OIDC Provider，当CI任务调用 `aws sts assume-role-with-web-identity` 时，AWS验证JWT并返回有效期默认为3600秒的临时STS凭证。整个流程中CI平台无需存储任何AWS密钥，消除了密钥泄露面。

OIDC信任配置的关键是条件限制，例如仅允许特定仓库和主分支触发角色扮演：

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
  }
}
```

### 密钥轮换与审计

成熟的密钥管理实践要求每个密钥具有明确的轮换周期。Vault的`lease`机制自动追踪每个颁发密钥的生命周期；AWS Secrets Manager提供托管轮换功能，可配置每30天自动轮换RDS密码并通知依赖方。Vault还内置审计日志（Audit Log），以JSON格式记录每次密钥访问的操作者、时间戳、请求路径，满足SOC 2、PCI-DSS等合规审计要求。

---

## 实际应用

**Kubernetes + Vault集成场景**：在Kubernetes集群中，Vault Agent以Sidecar形式注入到业务Pod中，通过Kubernetes Service Account Token进行认证，自动将密钥以文件形式挂载到 `/vault/secrets/` 目录，业务容器无需任何代码改动即可读取凭证，且凭证随Vault Lease自动刷新。

**GitHub Actions + AWS OIDC标准配置**：在 `.github/workflows/deploy.yml` 中设置 `permissions: id-token: write`，然后使用 `aws-actions/configure-aws-credentials` Action，指定 `role-to-assume` 和 `aws-region`，即可在无任何硬编码密钥的情况下完成AWS资源部署。这已成为2023年后GitHub Actions对接AWS的推荐标准做法。

**Doppler/1Password Secrets Automation**：中小团队常采用Doppler或1Password CLI作为轻量级Vault替代方案，通过Service Token在CI中执行 `doppler run -- your-deploy-script.sh`，Doppler自动将项目密钥注入子进程环境，同时提供版本历史和访问日志。

---

## 常见误区

**误区一：`.env`文件加入`.gitignore`就足够安全**。`.gitignore`只防止文件被意外提交，无法防止开发者本地机器被入侵后`.env`文件的泄露，也无法解决多人团队如何同步密钥、如何在CI服务器上分发密钥的问题。正确做法是`.env`文件仅用于本地开发，CI和生产环境必须使用专用密钥管理系统。

**误区二：环境变量永远安全，因为不在代码里**。许多CI系统的调试日志功能（如 `set -x` 的Shell脚本、某些框架的详细错误页）会将进程的完整环境变量打印出来。2021年Codecov事件正是通过读取CI环境变量实现密钥窃取。此外，子进程默认继承父进程的全部环境变量，导致非预期的密钥泄露范围扩大。

**误区三：OIDC配置信任整个GitHub组织就足够**。若AWS IAM的信任条件仅检查 `token.actions.githubusercontent.com:aud` 而不限制具体仓库和分支，则组织内任意仓库的任意工作流均可扮演该IAM角色。正确配置必须在 `sub` 字段明确限定仓库路径和分支，防止组织内的横向越权。

---

## 知识关联

密钥管理是CI/CD流水线安全的入口实践，掌握它之后可以进一步学习**供应链安全（Supply Chain Security）**，了解SLSA框架如何对构建产物的完整性做端到端保证；以及**基础设施即代码（IaC）安全**，即如何在Terraform/Pulumi代码中安全引用Vault或AWS Secrets Manager而非硬编码敏感值。密钥管理的OIDC原理与**服务网格的mTLS**共享零信任安全的设计思想，两者都致力于以短期可验证身份替代长期静态凭证。