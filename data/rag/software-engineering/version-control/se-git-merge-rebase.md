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
quality_tier: "B"
quality_score: 47.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
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

Merge（合并）和Rebase（变基）是Git中将一个分支的变更整合到另一个分支的两种核心操作，两者产生的历史记录结构截然不同。`git merge` 会创建一个新的"合并提交"（merge commit），保留两个分支并行开发的完整历史轨迹；而 `git rebase` 则将当前分支的提交"重放"到目标分支的顶端，从而产生一条线性的提交历史，但每个被重放的提交会获得全新的SHA-1哈希值。

Rebase命令由Linus Torvalds在Git早期版本中引入，其设计动机之一是Linux内核的补丁管理需求——维护者需要将贡献者的补丁整洁地应用到主线代码上。`git merge` 的 `--no-ff` 选项（禁用快进合并）则是后来为了强制保留分支拓扑结构而添加的标志，在团队规范中被广泛推荐。

两种操作的选择直接影响项目历史的可读性与协作安全性。Merge适合保留完整的协作记录，适用于公共分支；Rebase适合整理本地提交历史，但不应在已推送的共享分支上执行，否则会造成其他协作者的历史分叉。

## 核心原理

### Merge的三方合并机制

执行 `git merge feature` 时，Git会寻找当前分支（如`main`）、目标分支（`feature`）以及它们的**公共祖先提交**（merge base），以这三个快照执行三方合并（3-way merge）。合并成功后生成一个具有**两个父提交**的合并提交，可通过 `git log --graph` 看到分叉后汇聚的菱形结构。快进合并（fast-forward）是Merge的特殊情况：若当前分支是目标分支的直接祖先，Git默认只移动分支指针而不创建新提交，使用 `--no-ff` 可强制生成合并提交。

### Rebase的提交重放过程

`git rebase main` 的执行步骤如下：
1. Git找到当前分支与`main`的公共祖先；
2. 将当前分支自公共祖先以来的所有提交保存为临时补丁；
3. 将当前分支指针重置到`main`的最新提交；
4. 依次将保存的补丁逐一应用（即"重放"），每次应用后生成一个哈希值不同的新提交。

这意味着即使提交内容与原来完全相同，SHA-1也会改变。`git rebase -i`（交互式Rebase）允许在重放前对提交进行`squash`（合并）、`reword`（改写信息）、`drop`（删除）等操作，是整理功能分支提交记录的重要工具。

### 冲突解决的差异

Merge冲突在合并时**一次性全部呈现**，解决完毕后执行 `git merge --continue` 即可。Rebase冲突则在**每个提交重放时逐一出现**，每解决一次冲突后需执行 `git rebase --continue`，若某个提交的变更在目标分支已被包含，可用 `git rebase --skip` 跳过。冲突标记格式相同，均使用`<<<<<<<`、`=======`、`>>>>>>>`分隔两侧内容，但Rebase场景中`<<<<<<< HEAD`代表目标分支的内容，而非当前分支，这是初学者常见的误判点。

## 实际应用

**功能分支开发完毕后合并**：在GitHub Flow中，功能分支完成后通常通过Pull Request触发 `git merge --no-ff`，强制生成合并提交，使得 `git log --merges` 可以清晰过滤出每次功能合并的记录。

**保持功能分支与主干同步**：当`main`分支有新提交时，在本地功能分支执行 `git rebase main`，可使功能分支始终基于最新代码，避免后续合并时出现大量冲突，且不产生"同步合并"提交污染历史。

**交互式整理提交**：在提交Pull Request前，使用 `git rebase -i HEAD~5` 将最近5个提交进行squash，将"修复typo"、"调试日志"等中间提交合并为一个语义完整的提交，使代码审查更加清晰。

**处理Rebase冲突的实用命令**：
- `git rebase --abort`：放弃本次Rebase，恢复到执行前的状态；
- `git rerere`（Reuse Recorded Resolution）：开启后Git会记录冲突解决方案，在相同冲突再次出现时自动应用。

## 常见误区

**误区一：对已推送的共享分支执行Rebase**  
这是最危险的操作。若在`feature`分支已被同事拉取后执行 `git rebase main`，SHA-1变化会导致同事的本地分支与远程产生分叉，对方执行 `git pull` 后会出现重复提交，历史记录变得混乱。Git黄金法则（The Golden Rule of Rebasing）明确规定：**永远不要对公共历史执行Rebase**。

**误区二：认为Merge会"弄乱"历史，Rebase绝对更优**  
Rebase产生的线性历史看似整洁，但它**抹去了分支并行开发的真实过程**。当某个Rebase后的提交引入了Bug时，无法通过历史判断该提交当时的完整上下文，而Merge的完整历史保留了"这些变更是在某个时间点从某分支合入的"这一关键信息。两种策略各有适用场景，不存在绝对优劣。

**误区三：Rebase后的提交与原提交内容不同**  
Rebase不会修改提交中的文件变更内容（diff），只会改变提交的父节点，从而产生新的SHA-1。`squash` 是在交互式Rebase中主动合并多个提交的操作，不是Rebase的默认行为。普通Rebase完成后，每个提交的代码变更与原来完全一致，仅哈希值和时间戳有所变化。

## 知识关联

**前置知识**：理解Merge与Rebase需要掌握Git分支策略的基础，包括分支指针（branch pointer）本质上是指向某个提交的可移动引用，以及HEAD指针的含义。Git的提交对象通过SHA-1哈希链接父提交的数据结构，是理解Rebase"重写历史"机制的基础。

**与工作流的关联**：GitHub Flow倾向于使用Merge保留PR记录，Gitflow在`develop`合并`feature`时使用 `--no-ff`，而Google等公司的Trunk-based Development工作流则大量使用Rebase保持线性历史。理解这两个操作的区别，能帮助开发者在团队中参与和制定分支管理规范，评估"squash and merge"、"rebase and merge"、"create a merge commit"三种GitHub PR合并策略的取舍。