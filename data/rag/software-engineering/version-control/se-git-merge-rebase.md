---
id: "se-git-merge-rebase"
concept: "Merge与Rebase"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["Git"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# Merge与Rebase

## 概述

Merge（合并）和Rebase（变基）是Git中将两条分支历史整合为一的两种根本不同的方式。Merge通过创建一个新的"合并提交"（merge commit）将两个分支的末端连接起来，完整保留双方的提交历史；而Rebase则将一条分支上的所有提交逐一"重放"到另一条分支的顶端，从而生成全新的提交哈希值，最终呈现出一条线性历史。

Merge操作自Git诞生之初（2005年Linus Torvalds发布第一版）便存在，而Rebase被设计为一种"整理历史"的工具，其核心命令`git rebase`在Git 1.6版本后逐渐成熟。两者共同解决的问题是：多个开发者在不同分支上并行工作后，如何将各自的修改汇聚到同一个代码库中。

选择Merge还是Rebase直接影响项目的提交图（commit graph）形态，进而影响`git log`的可读性、`git bisect`的二分查找效率以及代码审查的便利性。在开源项目如Linux内核中，官方明确禁止对已推送的分支使用Rebase；而许多硅谷公司（如Shopify）则强制要求Feature分支在合并前必须先Rebase，以保持主干历史清洁。

---

## 核心原理

### Merge的三方合并机制

执行`git merge feature`时，Git会找到当前分支（如`main`）、目标分支（`feature`）以及它们的**共同祖先提交**（merge base）这三个提交点，对三者的文件快照进行对比，这一过程称为**三方合并（3-way merge）**。若两个分支修改了同一文件的不同区域，Git可以自动合并；若修改了同一行，则产生冲突，需要人工解决后手动执行`git add`标记冲突已解决，再`git commit`完成合并。

Merge默认会产生一个额外的合并提交，其提交消息通常为`Merge branch 'feature' into main`，并拥有**两个父提交（parent commits）**。可以使用`git merge --squash`将feature分支的所有提交压缩为单个提交，或使用`git merge --ff-only`强制仅在可以快进（fast-forward）时才允许合并——即feature分支是main分支的直接后代时，Git直接移动HEAD指针而不产生额外提交。

### Rebase的提交重放机制

执行`git rebase main`时，Git会从当前分支与main的共同祖先出发，将当前分支上的每一个提交依次取出，以patch的形式应用到main的最新提交之后。每个被重放的提交都会生成一个**全新的SHA-1哈希值**，即使内容完全相同，原有的提交哈希将不再有效。这也是为什么"黄金法则"规定：**永远不要对已经推送到公共仓库的分支执行Rebase**，否则会强制团队成员的本地历史与远程产生分叉。

`git rebase -i`（交互式Rebase）允许开发者在重放过程中对提交进行`pick`（保留）、`squash`（压缩到上一个提交）、`reword`（修改提交消息）、`drop`（删除提交）等操作，是整理"工作过程中产生的临时提交"的利器。

### 冲突解决的差异

Merge发生冲突时，整个过程只需解决**一次冲突**（所有变更汇聚到一个合并提交中）。而Rebase在重放多个提交时，每一个提交在应用时都可能单独产生冲突，开发者必须依次解决每一步的冲突并执行`git rebase --continue`，在最坏情况下需要解决N个提交各自的冲突（N为被重放的提交数量）。遇到复杂情况可随时执行`git rebase --abort`完整回滚到Rebase开始前的状态。

---

## 实际应用

**场景一：Feature分支合并到主干**
团队开发中，Feature分支完成后合并到`main`，通常有两种工作流：
- **GitHub Flow**：在GitHub上通过Pull Request发起`git merge --no-ff`（非快进合并），保留合并提交作为功能边界标记，方便日后用`git revert`一次性撤销整个功能。
- **GitLab推荐的Rebase工作流**：开发者在本地执行`git fetch origin && git rebase origin/main`，将feature分支更新到最新main之上，推送后在CI通过后由maintainer执行fast-forward merge，最终主干历史完全线性。

**场景二：同步上游更新**
当fork的仓库需要同步原始仓库（upstream）的更新时，`git rebase upstream/main`比`git merge upstream/main`更常用，因为后者会在你的fork历史中引入大量来自upstream的合并提交，污染你自己的贡献历史。

**场景三：清理本地实验性提交**
本地开发过程中产生了类似`fix typo`、`WIP: try another approach`这样的临时提交，在推送之前使用`git rebase -i HEAD~5`对最近5个提交进行整理，将相关提交squash为一个有意义的提交，是专业开发者的常规操作。

---

## 常见误区

**误区一：Rebase比Merge"更先进"，应当总是使用Rebase**
Rebase产生的线性历史看起来整洁，但它**篡改了历史真实性**。如果一个bug是在某次并行开发期间引入的，完整的Merge历史可以清晰还原时间线上的并发状态，而Rebase后的线性历史会掩盖这一信息。Linux内核项目明确规定集成分支（如`linux/master`）的历史只能通过Merge维护，正是出于审计可追溯性的考虑。

**误区二：Merge产生的合并提交越多越乱，应当用`--squash`替代**
`--squash`会丢失feature分支上每个独立提交的作者信息和提交消息，将所有变更压成一个匿名大包，实际上比保留合并提交**损失了更多历史信息**。`--squash`适合"临时分支、实验性代码"场景，而不适合团队协作中有明确功能边界的feature分支。

**误区三：Rebase冲突比Merge冲突更难解决**
Rebase的冲突总次数未必多于Merge，只是分散在多个步骤中逐一出现。实际上，每一步Rebase冲突的**范围更小、上下文更清晰**（只涉及单个提交的改动），相比Merge将所有冲突集中在一次解决，有时反而更容易逐步处理。

---

## 知识关联

本概念建立在**Git分支策略**的基础上——理解`git branch`的轻量指针本质、以及Feature分支、主干分支的职责划分，是正确选择Merge或Rebase的前提。知道一条分支上有多少个提交、这些提交是否已被他人基于此开展工作，直接决定了能否安全使用Rebase。

在工具层面，`git cherry-pick`可以视为"单次提交的Rebase"，它将指定的一个提交以patch形式应用到当前分支，理解了Rebase的重放机制便能自然理解cherry-pick的行为和限制。此外，`git reflog`是Rebase操作的安全网——即便Rebase后原提交哈希"消失"，reflog仍会在30天内保留操作前的状态，可通过`git reset --hard <old-hash>`进行恢复。掌握Merge与Rebase的选择逻辑，配合团队约定的分支命名规范与CI/CD流水线中的合并门控（merge gate），构成了完整的代码集成工作流。