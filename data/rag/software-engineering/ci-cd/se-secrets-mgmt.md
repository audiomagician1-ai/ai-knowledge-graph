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
quality_tier: "A"
quality_score: 79.6
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


# 密钥管理

## 概述

密钥管理（Secret Management）是指在CI/CD流水线中安全存储、分发、轮换和撤销敏感凭证的一整套机制。这些敏感凭证包括数据库密码、API Token、TLS证书、SSH私钥、云服务访问密钥（如AWS Access Key ID + Secret Access Key）等。一旦这类信息泄露到代码仓库或日志中，攻击者即可立即利用其获取生产环境权限，因此密钥管理是CI/CD安全的第一道防线。

密钥管理的现代实践起源于2013年前后"不要将密钥提交到Git"的行业共识。HashiCorp于2015年发布Vault 0.1版本，将密钥管理从"手工约定"升级为可审计、可编程的基础设施服务。2019年GitHub推出Secret Scanning功能，能够自动检测代码仓库中意外提交的AWS密钥、Google服务账号等超过200种凭证格式，标志着密钥防泄漏进入自动化阶段。

在CI/CD语境下，密钥管理的核心挑战是：流水线需要访问外部资源（如部署到Kubernetes、推送镜像到Registry），但同时必须避免长期静态凭证在多个Agent、容器、日志系统中扩散。现代方案通过短期令牌（TTL通常为15分钟至1小时）和最小权限原则来解决这一矛盾。

## 核心原理

### 环境变量注入

最基础的密钥传递方式是通过环境变量将密钥注入到CI运行时。GitHub Actions、GitLab CI、Jenkins均支持在平台侧加密存储密钥，在Job执行时以环境变量形式注入。以GitHub Actions为例，在仓库Settings > Secrets中存储的密钥，在YAML中通过`${{ secrets.DB_PASSWORD }}`引用，平台会自动在日志中将其替换为`***`以防止明文输出。

环境变量方案的致命缺陷在于**静态性**：一个密钥一旦创建，通常长期有效，且无法追踪"哪次构建使用了哪个密钥的哪个版本"。若某个密钥需要紧急吊销，必须逐个检查所有依赖该密钥的流水线并手动更新。

### Vault动态密钥

HashiCorp Vault通过**动态密钥（Dynamic Secrets）**解决了静态密钥的轮换问题。其工作流程为：

1. CI Runner以自身身份（AppRole或Kubernetes ServiceAccount）向Vault认证，获得短期Vault Token（TTL=15min）
2. 用该Token请求Vault的数据库Secret Engine：`GET /v1/database/creds/my-role`
3. Vault实时在数据库中创建一个临时账号（如`v-ci-abc123`），返回用户名+密码，TTL=1h
4. 流水线用该临时账号完成数据库操作
5. TTL到期后Vault自动吊销该账号

这一机制保证了每次CI运行获得唯一凭证，即使凭证泄露，其有效窗口极短。Vault还提供完整的审计日志，记录每次密钥请求的主体、时间、IP，满足SOC 2等合规要求。

### OIDC无密钥认证

OpenID Connect（OIDC）是2021年后GitHub Actions、GitLab CI等平台推广的**零静态密钥**方案。其核心思路是：CI平台本身作为身份提供方（IdP），为每次Job签发一个短期JWT（通常有效期10分钟），云服务商（AWS、GCP、Azure）预先配置信任该IdP，Job凭JWT直接换取云平台的临时凭证。

以GitHub Actions对接AWS为例：
- AWS侧配置IAM OIDC Provider，受众（Audience）为`sts.amazonaws.com`
- IAM Role信任策略限制`token.actions.githubusercontent.com`签发的、`sub`字段为`repo:org/repo:ref:refs/heads/main`的Token才可Assume
- Workflow中通过`aws-actions/configure-aws-credentials`动作自动完成JWT交换，获得有效期1小时的STS临时凭证

OIDC方案完全消除了在CI平台侧存储AWS Access Key的需要，AWS控制台中不存在任何长期密钥，攻击面大幅缩小。

### 密钥扫描与防泄漏

密钥管理不只是"存哪里"的问题，还包括防止密钥进入代码库。`git-secrets`（AWS开源，2016年）和`truffleHog`（支持正则+高熵值检测）可在`pre-commit`阶段拦截包含高熵字符串（Shannon熵 > 4.5 bits/char通常被标记为可疑）的提交，阻止密钥污染Git历史。

## 实际应用

**场景一：GitLab CI部署到Kubernetes**
在`.gitlab-ci.yml`中使用`KUBECONFIG`环境变量存储集群凭证是常见反模式——该文件包含集群CA证书和用户私钥。推荐方案是为CI Runner配置Kubernetes ServiceAccount，使用Vault的Kubernetes Auth Method认证，动态获取仅有`kubectl apply`权限的短期Token。

**场景二：Docker镜像推送到Harbor**
将Harbor机器人账号的用户名密码存入GitHub Actions Secrets（`HARBOR_USERNAME`、`HARBOR_PASSWORD`），在workflow中：
```yaml
- uses: docker/login-action@v3
  with:
    registry: harbor.example.com
    username: ${{ secrets.HARBOR_USERNAME }}
    password: ${{ secrets.HARBOR_PASSWORD }}
```
此方案适合中小团队，但密钥为静态长期有效，建议结合Harbor的机器人账号过期时间（建议设90天）和定期自动轮换脚本使用。

**场景三：多环境密钥隔离**
生产和测试环境应使用完全独立的密钥集合。Vault通过命名空间（Namespace）或不同的Secret Path（`secret/prod/db`与`secret/staging/db`）实现隔离，配合不同的Vault Policy确保staging的CI Runner无法读取prod路径下的密钥。

## 常见误区

**误区一：将密钥Base64编码后存入代码库等于加密**
Base64是编码而非加密，解码无需任何密钥，`echo "c2VjcmV0" | base64 -d`即可还原原文。GitHub Secret Scanning会主动检测Base64编码的常见凭证格式。正确做法是使用平台提供的加密密钥存储，或使用`git-crypt`对特定文件进行AES-256加密（但这引入了额外的密钥管理问题）。

**误区二：OIDC配置的IAM Role不限制sub字段**
部分教程示例中IAM信任策略仅验证Issuer为`token.actions.githubusercontent.com`，而不限制`sub`（代表具体repo和分支）。这意味着GitHub上任何仓库的任何Workflow都能Assume该Role，形成严重的横向越权风险。正确配置必须将`Condition`中的`StringEquals`限定到具体的`repo:org/repo:ref:refs/heads/main`。

**误区三：Vault Token直接硬编码为环境变量**
有些团队虽然引入了Vault，却将一个长期有效的Vault Root Token或高权限Token直接存入CI的环境变量，等于把"保险箱钥匙"放在了保险箱外面。正确做法是使用AppRole（RoleID公开存储，SecretID短期动态获取）或Kubernetes Auth等无需长期Token的认证方式。

## 知识关联

密钥管理与**流水线权限模型**直接相关：理解最小权限原则（Principle of Least Privilege）有助于设计Vault Policy和IAM Role的权限边界。在持续部署场景中，密钥管理与**部署策略**（蓝绿部署、金丝雀发布）结合时需要考虑新旧版本同时运行期间的密钥兼容性问题——若在灰度期间轮换数据库密码，必须确保新旧两个版本的应用都支持新密码。对于使用Kubernetes的团队，**External Secrets Operator**（ESO）将Vault/AWS Secrets Manager中的密钥自动同步为Kubernetes Secret对象，是连接密钥管理系统与容器编排层的常用工具。