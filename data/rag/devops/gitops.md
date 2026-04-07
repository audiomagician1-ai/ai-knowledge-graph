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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# GitOps

## 概述

GitOps是由Weaveworks公司于2017年提出的一种运维方法论，其核心思想是将Git仓库作为系统基础设施和应用配置的**唯一事实来源（Single Source of Truth）**。与传统CI/CD流程不同，GitOps要求所有生产环境的变更必须通过Git提交（commit）触发，禁止直接登录服务器或手动执行`kubectl apply`等命令。

在AI工程场景下，GitOps尤为重要，因为机器学习系统涉及模型版本、特征工程管道、推理服务配置等大量需要严格追踪的组件。一次未经Git记录的手动配置变更，可能导致模型A/B测试结果无法复现。GitOps通过让Git历史成为完整的审计日志，解决了AI系统"代码可复现但环境不可复现"的典型痛点。

GitOps区别于普通CI/CD流程的关键在于**操作方向（Pull vs Push）**。传统CI/CD是由流水线主动将制品推送（push）到目标环境；而GitOps使用运行在集群内部的Operator（如Argo CD、Flux CD）持续轮询Git仓库，检测到差异后主动拉取（pull）并应用变更，这种架构避免了CI系统需要持有生产环境凭证的安全风险。

## 核心原理

### 四大原则（Four Principles）

GitOps遵循由OpenGitOps工作组在2021年正式定义的四项原则：

1. **声明式（Declarative）**：系统期望状态用声明式配置描述，例如Kubernetes YAML中`replicas: 3`表示期望3个副本，而非命令式地"增加2个副本"。
2. **版本化且不可变（Versioned and Immutable）**：所有配置存储在Git中，每次变更产生不可篡改的commit SHA，作为回滚和审计的锚点。
3. **自动拉取（Pulled Automatically）**：认可的变更由软件Agent自动应用，不依赖人工干预。
4. **持续协调（Continuously Reconciled）**：系统实际状态与Git中定义的期望状态之间存在偏差时，Agent自动修正，这一特性被称为**漂移检测（Drift Detection）**。

### 协调循环（Reconciliation Loop）

GitOps Operator的工作机制是一个不断运行的控制循环，其逻辑可以表达为：

```
while true:
    desired_state = git.fetch(repo, branch)
    actual_state  = cluster.observe()
    diff = compare(desired_state, actual_state)
    if diff != ∅:
        cluster.apply(diff)
    sleep(interval)  # Argo CD默认间隔3分钟
```

当AI推理服务的GPU资源配额（`nvidia.com/gpu: "2"`）在Git中被修改后，Argo CD会在下一个协调周期内将集群中实际运行的Pod规格同步到最新声明，无需人工介入。

### 仓库结构策略：App of Apps vs Monorepo

实践中GitOps仓库的组织方式直接影响多团队协作效率。常见方案有两种：

- **单仓库（Monorepo）**：将所有服务的Kubernetes manifests集中在一个仓库，路径按环境划分如`/prod/model-serving/`和`/staging/model-serving/`，适合小型团队。
- **App of Apps模式**（Argo CD特有）：根仓库仅包含指向其他子仓库的`Application` CR（Custom Resource），每个AI服务团队维护独立仓库，根仓库变更触发级联同步，适合大规模多团队场景。

Flux CD采用类似方案称为**Kustomization层叠**，通过`base/`和`overlay/`目录复用公共配置，减少AI模型部署配置的重复定义。

## 实际应用

**场景一：模型金丝雀发布**

在AI推理服务升级中，通过修改Git仓库中的Argo Rollouts配置，将新模型`bert-v2.1`的流量权重从0%逐步提升到10%、30%，再到100%。整个过程仅通过`git commit`触发，Rollouts Controller负责执行流量切分，一旦指标（如P99延迟超过200ms）达到回滚阈值，可执行`git revert`一键还原，比手动操作的平均恢复时间（MTTR）快60%以上。

**场景二：多环境特征工程管道配置**

某AI平台维护dev/staging/prod三套特征处理管道，使用Kustomize的overlay机制，`base/`目录定义通用Spark配置，`overlays/prod/`仅覆盖生产环境的executor数量（`spark.executor.instances: 20`）。每次特征工程代码合并到`main`分支后，Flux CD自动将prod环境同步到最新配置，同时保留完整的变更历史供数据科学团队审计。

**场景三：合规审计**

金融领域部署的AI风控模型受监管机构要求，需要提供"谁在什么时间以什么理由修改了模型推理阈值"的完整记录。GitOps天然满足此需求：`git log --follow configs/risk-model/threshold.yaml`命令即可输出完整变更链，每条commit包含作者、时间戳、PR审批记录和关联的Jira工单号。

## 常见误区

**误区一：GitOps等同于"把kubectl命令放到Git里"**

部分初学者将Shell脚本（如`kubectl apply -f deploy.yaml`）版本化到Git中，误认为这就是GitOps。这种方式仍是命令式操作，缺少持续协调能力——脚本只在CI触发时执行一次，无法检测和修复之后发生的配置漂移。真正的GitOps必须有运行在集群内部的Operator持续监听。

**误区二：GitOps只适用于Kubernetes**

GitOps的原则与Kubernetes无关，Terraform配合Atlantis可以对云基础设施实现GitOps；AWS CloudFormation配合StackSets同样符合GitOps原则。在AI工程中，MLflow Model Registry的模型晋级流程也可以用GitOps模式管理——通过修改Git中的模型版本配置文件触发Registry API，而非直接调用API。

**误区三：Git仓库存储所有内容包括密钥**

GitOps要求所有配置存储在Git中，但这不包括密钥（Secrets）。将`DATABASE_PASSWORD`明文写入Git是严重安全漏洞。正确做法是在Git中存储加密后的密文（使用Sealed Secrets或SOPS工具），或在Git中存储对外部密钥管理系统（如HashiCorp Vault、AWS Secrets Manager）的引用，由Operator在运行时动态注入明文。

## 知识关联

**与Git工作流（GitFlow）的关系**：GitOps高度依赖分支保护策略。`main`分支通常对应生产环境，任何合并到`main`的PR必须经过至少一名SRE审批，这要求团队对GitFlow的`feature branch → PR → merge`流程有扎实的工程实践。GitFlow定义了代码如何流转，GitOps定义了代码合并后如何自动反映到实际系统。

**与CI/CD的关系**：传统CI/CD负责将源代码构建为镜像并推送到镜像仓库（Push阶段），GitOps从这一步之后接管——CI流水线完成后自动更新Git配置仓库中的镜像Tag（如将`image: model-server:sha-abc123`更新为`image: model-server:sha-def456`），触发GitOps的Pull阶段。两者分工明确，CI不再直接接触生产集群。

**与基础设施即代码（IaC）的关系**：IaC（如Terraform的`.tf`文件）提供了将基础设施意图写成代码的能力，但本身不规定这些代码如何被执行和管理。GitOps为IaC提供了执行框架——规定IaC文件必须存储在Git中，变更必须通过PR流程审批，并由自动化Agent负责应用，将IaC从"人工执行的脚本"升级为"持续自协调的系统"。