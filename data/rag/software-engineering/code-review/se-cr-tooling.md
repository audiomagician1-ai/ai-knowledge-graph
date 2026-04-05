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
quality_tier: "A"
quality_score: 73.0
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


# 审查工具

## 概述

代码审查工具是专门用于辅助开发团队进行代码审阅、批注和合并决策的软件平台。与简单地用邮件互传diff文件相比，现代审查工具提供了内联评论（inline comment）、自动化检查触发、审批状态跟踪等功能，使得审查过程可追溯、可量化。当前主流的三类工具分别是：集成在Git托管平台上的**GitHub Pull Request Review**、谷歌开源的**Gerrit**，以及Atlassian旗下已停止更新的**Crucible**。

这三种工具的诞生背景各不相同。GitHub PR Review随GitHub平台于2008年上线，以社交化协作为设计理念；Gerrit由谷歌内部工具Mondrian演化而来，2008年由Shawn Pearce开源，专为Android项目大规模协作设计；Crucible则是Atlassian在2007年推出的商业产品，与Jira和Confluence深度整合，但自2020年起Atlassian已宣布该产品进入维护模式，不再新增功能。选择不同工具直接影响团队的审查流程设计、与CI/CD系统的集成方式和权限管控粒度。

## 核心原理

### GitHub Pull Request Review 的工作机制

GitHub PR Review 基于**分支合并请求**模型。开发者从主干创建特性分支，完成开发后发起 Pull Request，整个diff在浏览器中可视化呈现。审查者可在具体代码行添加 `line comment`，也可发起 `review` 并选择三种状态之一：`Comment`（仅评论）、`Approve`（批准）或 `Request changes`（要求修改）。只有收到足够数量的 `Approve` 且通过所有必需的 Status Check 后，PR才可合并。

GitHub提供的 **Branch Protection Rules** 可配置"至少需要N名审查者批准"（N可设为1至6），以及"代码所有者（CODEOWNERS文件中指定的人员）必须审查"等策略。整个审查历史以 conversation thread 形式保留在PR页面，每个thread可被单独标记为 `Resolved`，方便追踪修改落实情况。

### Gerrit 的变更集审查模型

Gerrit 采用完全不同的**变更集（Change）**模型，而非分支模型。开发者通过特殊的 `git push refs/for/<branch>` 命令将提交推送到 Gerrit 服务器，每个提交形成一个独立的 Change，拥有唯一的 Change-Id（写入commit message的形如 `I3b3a5e...` 的哈希串）。

Gerrit 的评分系统是其最显著特征：每个 Change 需要在两个维度上同时满足条件才能合并。`Code-Review` 维度评分范围为 **-2 到 +2**，`Verified` 维度评分范围为 **-1 到 +1**。任何 -2 评分均构成一票否决，即使其他所有人打了+2也无法合并。这种设计来源于谷歌的工程文化，强调单个资深工程师有权独立阻止不符合标准的代码合入主干。Gerrit 还原生支持**主题（Topic）**功能，允许将跨仓库的多个相关 Change 分组，这对于需要同时修改多个微服务仓库的场景非常实用。

### Crucible 的审查会话模型

Crucible 将代码审查组织为**审查会话（Review Session）**，支持对 SVN、Git、Mercurial 等多种版本控制系统的diff进行审查，也支持对任意文件集合发起临时性（pre-commit）审查——这在Git工作流尚未普及的2007年至2015年期间是重要优势。Crucible 与 Fisheye（代码搜索工具）配套使用，通过 Fisheye 的提交索引来触发自动审查工作流。每个审查有明确的 `Moderator`（主持人）、`Author`（作者）和 `Reviewer` 三种角色，主持人负责关闭审查会话并记录最终结论（`Summarize`）。

## 实际应用

**开源项目首选 GitHub PR Review**：Linux内核子系统之外的绝大多数开源项目（如React、Vue、Kubernetes）均使用GitHub PR Review，原因是其零摩擦的 fork-and-PR 工作流降低了外部贡献者的参与门槛，且 GitHub Actions 可直接在PR上运行lint、测试。

**Android和大型企业单体仓库首选 Gerrit**：Android Open Source Project（AOSP）至今使用 Gerrit 管理所有代码合入，其变更集模型特别适合需要强制每次提交都经过独立审查的场景，以及基于 Repo 工具管理多仓库的 monorepo 架构。谷歌内部使用的 Piper 系统也采用类似的评分机制。

**Jira重度用户团队的历史选择**：2010至2018年间，使用 Atlassian 技术栈（Jira+Confluence+Bamboo）的企业团队普遍选用 Crucible，因为它能将 Jira Issue 与具体审查会话双向关联，在 Jira 的看板上直接显示代码审查状态，无需切换工具。

## 常见误区

**误区一：认为 Gerrit 的 +2 等同于 GitHub 的 Approve**。实际上两者语义不同。GitHub 的 Approve 表示"我认可这段代码可以合并"，是一种相对主观的判断；而 Gerrit 的 `Code-Review +2` 在大多数团队的配置中意味着"这段代码符合项目的编码规范和架构要求，具有合并资格"，且通常只有 Maintainer 级别的成员才有权打出 +2。混淆两者会导致团队在迁移工具时错误地将所有开发者都赋予 +2 权限，削弱门控效果。

**误区二：认为 Crucible 已完全不可用**。Atlassian 虽已停止新功能开发，但 Crucible 仍在安全修复支持范围内（截至官方公告，支持期至2024年）。部分仍在使用 SVN 或混合版本控制系统的老旧企业项目，短期内迁移成本极高，Crucible 依然是其可用选项。但对于新建项目，不应再选择 Crucible 作为主要审查工具。

**误区三：认为 GitHub PR Review 不适合大规模团队**。GitHub 的 `CODEOWNERS` 文件配合 Branch Protection Rules 可以实现细粒度的权限控制，如指定 `/src/auth/` 目录的改动必须由 `@security-team` 审查。Meta、Microsoft等公司均在 GitHub 上管理数百人协作的大型项目，通过自动化机器人（如 Meta 的 ReviewBot）补充 Gerrit 式的强制审查能力。

## 知识关联

学习审查工具需要以**代码审查概述**中的概念为前提，包括审查目的（质量门控、知识共享）、审查粒度（提交级 vs 功能级）以及同步审查与异步审查的区别——理解这些概念后才能判断 Gerrit 的 Change 模型和 GitHub 的 PR 模型各自适用于何种团队纪律。

在横向关联上，审查工具的选型与**持续集成（CI）系统**紧密耦合：GitHub PR Review 原生对接 GitHub Actions，Gerrit 通过 `Verified` 标签与 Jenkins 或 Zuul CI 集成，而 Crucible 依赖 Bamboo 的 post-build 步骤触发审查通知。此外，**分支管理策略**（如 Trunk-Based Development 或 GitFlow）也直接影响工具选择：Trunk-Based Development 的极短特性分支与 GitHub PR Review 配合自然，而 Gerrit 强制的逐提交审查则天然契合直接推送主干的开发模式。