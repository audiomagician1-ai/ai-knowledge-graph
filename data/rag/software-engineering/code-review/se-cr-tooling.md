---
id: "se-cr-tooling"
concept: "审查工具"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 审查工具

## 概述

代码审查工具是软件工程团队用于组织、执行和追踪代码审查流程的专用平台，其核心功能包括：展示代码差异（diff）、允许行内评论、管理审查状态以及与版本控制系统集成。三款最具代表性的工具分别是 **GitHub Pull Request Review**、**Gerrit** 和 **Atlassian Crucible**，它们诞生于不同背景，各自针对不同团队规模和工作流程设计。

GitHub Pull Request 功能于 2008 年随 GitHub 平台推出，最初目的是为开源社区提供贡献代码的标准化渠道。Gerrit 由 Shawn Pearce 于 2008 年为 Android 开源项目（AOSP）开发，专为需要严格门控提交的大型项目设计。Crucible 则由 Atlassian 于 2007 年发布，与 Jira 和 Bitbucket 深度集成，面向企业级团队。了解这三款工具的差异，能帮助团队根据自身规模、审查严格度需求和现有技术栈做出正确选型决策。

## 核心原理

### GitHub Pull Request Review 的工作机制

GitHub PR 采用**基于分支的异步审查模型**。开发者从主分支创建特性分支，推送若干提交后，向目标分支发起 Pull Request。审查者可在具体代码行添加评论，评论会以线程形式组织，支持对话回复。当所有 Reviewer 点击"Approve"且通过必要的 CI 检查后，PR 可被合并。

GitHub 支持三种审查状态：**Comment（仅评论）**、**Approve（批准）**、**Request Changes（要求修改）**。仓库管理员可在分支保护规则中设置最少需要 N 名审查者批准才能合并，此数字通常设为 1 或 2。PR 的评论直接附加在 diff 视图中，支持建议性修改（Suggested Change），审查者可直接提议替换代码片段，作者一键即可接受。

### Gerrit 的提交门控模型

Gerrit 采用与 GitHub 截然不同的**单提交（patchset）门控模型**。每个提交在合并前必须独立通过审查，Gerrit 引入了两个独立的投票维度：**Code-Review（代码质量）** 和 **Verified（验证/CI通过）**，各自使用 -2 到 +2 的评分制度。只有当提交获得至少一个 Code-Review +2 并且 Verified +1 时，才允许提交到主线，即"Submit"操作。

Gerrit 强制执行"一个提交一次审查"原则，避免大批量代码同时进入主线。若开发者修改代码后重新上传，Gerrit 会将其识别为同一变更的新 **Patchset**（如 Patchset 2、Patchset 3），保留完整的修改历史。Gerrit 使用专有的 `git push refs/for/master` 语法将提交推送到审查队列，而非直接推送到目标分支，这是它与普通 Git 工作流最大的操作差异。

### Crucible 的特色能力

Crucible 支持**计划内审查（Pre-commit Review）和事后审查（Post-commit Review）**两种模式，这是 GitHub PR 和 Gerrit 均不原生支持的能力。团队可以对已经提交到代码库的历史代码发起审查，适合合规审计或遗留代码改进场景。

Crucible 与 Jira 的集成允许将代码审查缺陷直接转化为 Jira Issue，审查评论与任务追踪系统之间的关联是其企业场景的核心优势。Crucible 还提供审查统计报告，如每位审查者的平均响应时间、缺陷发现率等度量数据，支持管理层监控审查流程质量。然而，Atlassian 已于 **2020 年 4 月宣布 Crucible 进入维护模式**，不再开发新功能，因此新项目不建议选用。

### 三款工具关键参数对比

| 维度 | GitHub PR | Gerrit | Crucible |
|---|---|---|---|
| 合并粒度 | PR（含多个提交） | 单提交 | 灵活 |
| 评分机制 | Approve/Request Changes | -2 至 +2 分制 | 通过/拒绝 |
| 离线审查支持 | 不支持 | 不支持 | 支持 |
| 典型用户规模 | 中小型到大型开源 | 超大型（如 AOSP） | 中型企业 |

## 实际应用

**Android 开源项目（AOSP）** 是 Gerrit 最典型的真实案例。AOSP 代码库包含数百万行代码，每天有来自 Google 和全球设备厂商的大量提交，Gerrit 的 +2 门控机制确保只有经过双重独立审查的代码才能进入主线，单个提交的审查周期有时长达数周。

**Facebook（现 Meta）** 早年使用内部工具 Phabricator（其差异审查功能 Differential 与 Gerrit 类似），后逐步向 GitHub PR 迁移，这一案例说明随着团队开源协作比重增加，工具选型会相应调整。

初创公司和开源项目通常首选 **GitHub PR**，因为其学习成本低，开发者只需掌握标准 `git push` 和网页操作即可参与审查，而无需学习 Gerrit 的 `refs/for/` 推送协议。

## 常见误区

**误区一：Gerrit 的 +2 等同于"两个人各打 +1"**。事实上，Gerrit 的 +2 和 +1 不能相加，一个 +2 高于两个 +1 之和，+2 代表该提交获得项目核心维护者的完全认可，通常只有少数拥有该权限的人才能打出。普通贡献者的最高评分权限往往被限制在 +1，无法单独放行提交。

**误区二：GitHub PR Review 与 GitHub PR 是同一概念**。Pull Request 是代码合并请求的容器，而 PR Review 是对该容器内代码进行正式审查的动作，一个 PR 可以在没有任何正式 Review 的情况下被强制合并（前提是没有设置分支保护规则）。理解这一区别对配置正确的分支保护策略至关重要。

**误区三：选择更复杂的工具意味着更高审查质量**。Gerrit 的严格门控确实能拦截更多问题，但其陡峭的学习曲线（尤其是 `git push refs/for/master` 语法和 Change-Id hook 配置）会增加新人上手时间。团队规模在 10 人以下时，Gerrit 的配置和维护成本往往超过其带来的质量收益，此时 GitHub PR 配合两人审查规则是更实用的选择。

## 知识关联

学习审查工具需要预先理解**代码审查概述**中建立的基础概念，例如为何需要正式审查流程、审查的质量目标是什么，只有在此基础上才能理解三款工具各自的设计权衡——Gerrit 的复杂性服务于"零缺陷入库"目标，GitHub PR 的简洁性服务于"快速迭代协作"目标。

从工具层面向上延伸，审查工具的选型直接影响**持续集成（CI）流水线**的接入方式：GitHub PR 通过 GitHub Actions 或第三方 CI 以状态检查（Status Check）形式集成，而 Gerrit 通过其内置的 Verified 投票维度接受 CI 系统的自动评分，两者接入逻辑有本质差异。掌握审查工具的操作机制，也是理解 **GitFlow** 和 **Trunk-Based Development** 等分支策略在实际团队中如何落地的前提。