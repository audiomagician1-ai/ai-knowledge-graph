---
id: "se-cherry-pick"
concept: "Cherry-pick与补丁"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["Git"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Cherry-pick与补丁

## 概述

`git cherry-pick` 是Git中一条专门用于将**特定提交**从一个分支"摘取"并重新应用到另一个分支的命令，其名称来源于"精挑细选"的含义——只取你想要的那颗"樱桃"，而不是合并整棵树。它与 `git merge` 的本质区别在于：merge会将两个分支的全部历史合并，而cherry-pick只复制单条或少数几条提交的变更内容。

该命令最早随Git 1.5版本（2007年前后）进入主线，最初主要用于Linux内核开发社区中的补丁管理流程。在Linux内核开发中，维护者需要将稳定分支上已审核通过的修复精确移植到多个活跃发布分支，cherry-pick成为完成这一工作的标准工具。

在生产环境中，当主干（main/master）已经积累了大量新功能提交，但某个旧版本分支出现了紧急安全漏洞时，开发者不能直接合并主干，只能使用cherry-pick将那一次修复提交单独"回港"到旧版本分支，这就是所谓的**热修复回港（hotfix backport）**策略。

---

## 核心原理

### cherry-pick的工作机制

执行 `git cherry-pick <commit-hash>` 时，Git实际上做的是：

1. 提取目标提交相对于其父提交的**diff差异**（即该次提交引入的变更集）；
2. 将这份diff作为补丁，应用到当前所在分支的HEAD；
3. 生成一个**全新的提交对象**，其内容与原提交相同，但commit hash不同，时间戳和父提交均为新分支上的当前状态。

这意味着cherry-pick之后，原分支和目标分支上会各有一个"内容相同但身份不同"的提交，它们在Git历史图中是独立节点。

### 常用命令变体与参数

| 用法 | 说明 |
|------|------|
| `git cherry-pick A..B` | 摘取从A（不含）到B（含）之间的连续提交区间 |
| `git cherry-pick -n <hash>` | 应用变更但不自动创建提交，允许你先修改再提交 |
| `git cherry-pick -x <hash>` | 在新提交的message中自动附加 `(cherry picked from commit xxxx)` 注释 |
| `git cherry-pick --abort` | 遇到冲突时放弃整个操作，回到执行前状态 |

推荐在团队协作中始终使用 `-x` 参数，这样可以在提交历史中保留溯源信息，方便日后审计。

### 补丁文件与cherry-pick的关系

与cherry-pick相关的另一条工作流是"补丁文件"方式：使用 `git format-patch <commit-hash>` 将提交导出为 `.patch` 文件，再通过 `git am <file.patch>` 在另一仓库中应用。这种方式适用于无法直接访问源仓库的场景（例如给开源项目贡献代码时通过邮件列表提交补丁）。Linux内核至今仍部分使用这一基于邮件补丁的工作流，`git am` 中的"am"即"apply mailbox"的缩写。

两种方式的核心差异：cherry-pick要求两个分支在同一Git仓库或可互相fetch的仓库中；补丁文件方式则可以完全离线，跨越仓库边界传递变更。

---

## 实际应用

### 场景一：热修复回港

假设你的产品同时维护 `release/2.0` 和 `release/3.0` 两条发布线，主干上的开发者在 `main` 分支修复了一个SQL注入漏洞，提交哈希为 `a3f9c12`。你需要将这个修复同时应用到两条旧版本分支：

```bash
git checkout release/2.0
git cherry-pick -x a3f9c12

git checkout release/3.0
git cherry-pick -x a3f9c12
```

执行后，两个发布分支各自新增一个内容相同的修复提交，且commit message中保留了对原始提交 `a3f9c12` 的引用，审计时可清楚追溯修复来源。

### 场景二：从功能分支单独摘取工具函数

当一个长期功能分支（feature branch）开发周期较长，但其中某个工具函数已经稳定且其他分支急需使用时，可以只cherry-pick那一个函数的提交，而不必等待整个feature分支合并，从而避免引入未完成功能的代码。

### 场景三：撤销错误合并后的精细恢复

若某次误操作将包含10个提交的分支合并到主干，使用 `git revert` 回滚整个merge后，可以通过cherry-pick逐一将其中9个已确认无问题的提交重新应用，从而实现"只排除1个有问题提交"的精细化恢复。

---

## 常见误区

### 误区一：cherry-pick会"移动"提交

许多初学者认为cherry-pick会把提交从原分支"剪切"过来，原分支上的提交因此消失。实际上cherry-pick是**复制**操作，原分支的提交完全不受影响，两个分支上会同时存在内容等价但哈希不同的两个提交。如果日后这两个分支再次合并，Git会将它们识别为两次独立的变更，可能引发重复应用的冲突，这是cherry-pick使用过频时需要警惕的副作用。

### 误区二：cherry-pick只能用于单个提交

实际上 `git cherry-pick A..B` 支持提交范围，可以一次性摘取连续的多个提交。但注意该语法中A是**不包含**的起点（即实际从A的下一个提交开始），若要包含A本身，需要写成 `git cherry-pick A^..B`，漏掉 `^` 是新手高频犯错点。

### 误区三：cherry-pick可以替代merge/rebase

cherry-pick适用于精确摘取少量提交的场景，如果需要将一个分支上的大量提交整体同步到另一个分支，应使用 `git rebase` 或 `git merge`。滥用cherry-pick会导致大量重复内容的提交散落在不同分支，使项目历史图变得混乱，且增大后续合并时产生冲突的概率。

---

## 知识关联

**前置知识**：使用cherry-pick需要理解Git的提交模型——每个提交记录的是一份完整的文件快照加上父节点引用，而非增量存储；cherry-pick之所以能独立迁移提交，正是因为Git内部将每次提交对父节点的diff计算为可独立应用的补丁。此外，需要熟悉基本的冲突解决流程，因为当目标分支上下文与原始提交的上下文不一致时，cherry-pick会产生和merge相同性质的冲突，需要手动 `git add` 后再 `git cherry-pick --continue` 完成。

**延伸实践**：掌握cherry-pick后，可以进一步研究 `git format-patch` + `git am` 组成的补丁邮件工作流，这是参与Linux内核及众多基础软件开源社区的必备技能；也可以结合 `git log --oneline --graph` 命令，在执行cherry-pick前可视化分支历史，准确定位目标提交哈希，减少操作失误。
