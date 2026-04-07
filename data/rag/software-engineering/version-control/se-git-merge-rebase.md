# Merge与Rebase

## 概述

Merge（合并）与Rebase（变基）是Git版本控制系统中将两条独立分支历史整合为一的两种根本不同的策略。二者解决同一个技术问题——多开发者并行工作后的代码汇聚——却产生截然不同的提交图（commit graph）拓扑结构。Merge通过创建一个拥有**两个父提交（parent commits）**的合并提交节点将两条历史线索连接，完整保留所有分支点信息；Rebase则将一条分支上的每个提交逐一以patch形式"重放"到另一条分支顶端，消灭分叉、生成全新的SHA-1哈希值，最终呈现一条线性历史。

Git由Linus Torvalds于2005年4月创建，最初仅用了10天完成第一版实现（Torvalds, 2005年LKML邮件列表）。`git merge`自第一版便存在，而`git rebase`及其交互模式`-i`标志在Git 1.6系列（约2008年）之后才趋于成熟稳定（Chacon & Straub, *Pro Git* 2nd ed., 2014）。理解两者的底层机制差异，直接决定了团队能否在`git log --graph`可读性、`git bisect`二分查找效率以及Pull Request代码审查体验之间做出正确权衡。

---

## 核心原理

### Merge的三方合并（3-way Merge）机制

当执行`git merge feature`时，Git首先通过**最近公共祖先算法**（Lowest Common Ancestor，LCA）定位`main`分支、`feature`分支以及二者的共同祖先提交（merge base）这三个快照节点。三方合并的逻辑如下：

- 若某文件仅在`feature`中被修改而祖先中未改动，取`feature`版本；
- 若某文件仅在`main`中被修改，取`main`版本；
- 若二者**均修改了同一文件的同一区域**，Git无法自动决策，标记为冲突（conflict）。

冲突标记格式如下：

```
<<<<<<< HEAD
main分支中的内容
=======
feature分支中的内容
>>>>>>> feature
```

整个Merge过程只产生**一次冲突解决窗口**：所有文件冲突集中在同一合并提交中处理，开发者`git add`标记已解决后执行`git commit`即告完成，且原有所有提交的SHA-1哈希值**保持不变**。

当`feature`分支是`main`的直接后代（即`main`分支顶端提交是`feature`分支的祖先）时，Git默认执行**快进合并（Fast-Forward Merge）**：直接移动`main`的HEAD指针，不创建额外合并提交。使用`git merge --no-ff`可强制创建合并提交，以在历史中保留分支存在的痕迹。

### Rebase的提交重放（Patch Replay）机制

执行`git rebase main`时，Git的内部步骤如下：

1. 找到当前分支（`feature`）与目标分支（`main`）的共同祖先提交 $C_0$；
2. 将`feature`上 $C_0$ 之后的每一个提交 $C_1, C_2, \ldots, C_n$ 提取为patch（`git format-patch`等效操作）；
3. 将HEAD临时指向`main`的最新提交 $M$；
4. 依次将 $C_1' , C_2', \ldots, C_n'$ 应用到 $M$ 之后，每个新提交都生成全新的SHA-1哈希。

用符号表达，若原始提交链为：

$$M_0 \leftarrow M_1 \leftarrow M_2 \quad (\text{main}) \quad \text{和} \quad M_0 \leftarrow C_1 \leftarrow C_2 \quad (\text{feature})$$

Rebase后变为：

$$M_0 \leftarrow M_1 \leftarrow M_2 \leftarrow C_1' \leftarrow C_2' \quad (\text{feature，线性历史})$$

其中 $C_1'$ 与 $C_1$ 内容相同但哈希值不同。这是**Rebase黄金法则**的技术根源：一旦 $C_1$ 已被推送到公共远程仓库并被他人基于其工作，将其替换为 $C_1'$ 会导致其他协作者的本地历史出现"孤儿提交"，强制要求所有人执行`git pull --rebase`或重置本地分支。

### 交互式Rebase（Interactive Rebase）

`git rebase -i HEAD~N`打开一个可编辑列表，列出最近N个提交，每行以操作指令开头：

| 指令 | 含义 |
|------|------|
| `pick` | 保留该提交不变 |
| `reword` | 保留提交内容，修改提交消息 |
| `squash` | 将该提交合并入上一个提交，合并消息 |
| `fixup` | 同`squash`但丢弃本提交消息 |
| `drop` | 完全删除该提交 |
| `edit` | 暂停以允许修改该提交内容（可用于拆分提交） |

例如，一个Feature分支开发过程中产生了"WIP: 调试日志"、"typo fix"等临时提交，上线前用`git rebase -i`将其`fixup`进相关功能提交，可使PR历史仅包含有意义的逻辑节点。

### 冲突解决频次差异

这是Rebase最常被忽视的成本：若`feature`分支有5个提交，而`main`上的修改与其中3个分别产生冲突，则需要**解决3次冲突**（每次重放一个提交时各解决一次）；相同情形下Merge仅需**解决1次冲突**（所有差异汇聚在三方合并节点）。冲突越多、提交粒度越细，Rebase的解决成本越高。这正是长期存活的Feature分支（超过2周未同步主干）通常更适合用Merge的原因。

---

## 关键命令与工作流公式

### 常用命令对照

```bash
# Merge：保留历史，创建合并提交
git checkout main
git merge feature                # 标准合并
git merge --no-ff feature        # 强制保留合并提交（禁用Fast-Forward）
git merge --squash feature       # 压缩为单提交（不自动commit）

# Rebase：线性化历史
git checkout feature
git rebase main                  # 将feature变基到main顶端
git rebase -i HEAD~4             # 交互式整理最近4个提交
git rebase --onto main oldbase feature  # 高级变基：仅移植oldbase之后的提交

# 冲突发生时
git rebase --continue            # 解决冲突后继续
git rebase --abort               # 放弃本次Rebase，恢复原状
git merge --abort                # 放弃本次Merge，恢复原状
```

### 分支同步的数学直觉

设主干分支在时间 $t$ 上的提交序列为 $M = \{m_1, m_2, \ldots, m_k\}$，Feature分支从 $m_j$ 分叉产生 $F = \{f_1, f_2, \ldots, f_n\}$。

- **Merge后的DAG节点数**：$k + n + 1$（增加一个合并节点）
- **Rebase后的线性节点数**：$k + n$（无额外节点，但 $f_i$ 均被替换为 $f_i'$）

在`git log --oneline`输出中，Merge产生有向无环图（DAG），Rebase产生链表。`git bisect`在链表结构上的二分查找路径长度为 $O(\log n)$，在复杂DAG中由于需要跳过合并节点，实际定位效率可能退化。

---

## 实际应用

### 工作流一：GitHub Flow（推荐Merge）

GitHub官方推荐的工作流中，Feature分支通过Pull Request合并时使用`--no-ff`产生合并提交。这样在`git log --graph`中每个Feature的完整开发历史清晰可见，回滚整个Feature只需`git revert -m 1 <merge-commit-hash>`一条命令（`-m 1`指定保留主干父提交方向）。

### 工作流二：线性历史强制Rebase（Shopify等采用）

部分公司的CI/CD流水线要求所有PR在Squash+Rebase后才能合并，主干历史形如一条直线。这使得`git log`不借助`--graph`也完全可读，生产事故排查时通过`git log --oneline`快速定位问题提交的速度显著提升。GitHub、GitLab的"Squash and merge"按钮即服务于此场景。

### 案例：Linux内核的Merge策略

Linux内核项目是全球最大的Git仓库之一（截至2024年约120万个提交）。Linus Torvalds明确要求子系统维护者的集成分支使用Merge而非Rebase，原因是：Merge保留了"谁在何时将哪批提交集成"的完整元信息，这对于内核的法律审计（提交者身份与Signed-off-by链）和历史溯源至关重要（Torvalds, LKML, 2012年邮件）。

### `git rerere`：自动复用冲突解决

对于长期分支频繁Rebase的场景，`git rerere`（Reuse Recorded Resolution，重用已记录的解决方案）是关键工具。开启`git config rerere.enabled true`后，Git会记录每次冲突的解决方式。当相同的冲突再次出现（例如每次同步主干都遇到同一处冲突），Git自动应用上次的解决方案，将重复劳动降至最低。

---

## 常见误区

### 误区一："Rebase比Merge更高级"

这是认知偏差。两者各有适用场景，无高下之分。Rebase适合**个人Feature分支在合并前的整理**；Merge适合**团队集成分支的历史记录**。在共享分支（如`develop`、`release`）上执行Rebase并强推（`git push --force`）会覆盖他人工作，是导致生产事故的高危操作。

### 误区二："Squash Merge等同于Rebase"

`git merge --squash`将Feature分支所有提交压缩为**一个新提交**添加到目标分支，但它**不移动Feature分支的HEAD**，也不创建合并提交，相当于手工将diff应用为单一提交。而`git rebase`逐个重放提交，粒度更细，可保留中间提交节点。在`git log`中，Squash Merge后的Feature分支与主干仍然"分离"，后续若再次Merge会产生重复提交问题，因此Squash后通常应删除Feature分支。

### 误区三："`git pull`默认行为是安全的"

`git pull`默认等同于`git fetch` + `git merge`，会在本地产生合并提交，使本地主干历史出现不必要的分叉。Git 2.27版本（2020年）引入警告提示，建议用户明确设置`pull.rebase`配置项：

```bash
git config --global pull.rebase true    # 等同于 git pull --rebase
git config --global pull.rebase false   # 明确保留Merge行为（默认）
git config --global pull.ff only        # 仅允许Fast-Forward，否则报错
```

### 误区四："Rebase后的提交时间戳会改变"

Git提交元数据包含两个时间字段：`author date`（原始编写时间）和`committer date`（提交写入仓库的时间）。`git rebase`在重放提交时，**保留原始`author date`**，但会将`committer date`更新为当前时间。因此`git log --format="%ai %ci %s"`可以看到同一提交的两个时间不一致，这在法律审计或时间序列分析中需特别注意。

---

## 知识关联

### 与Cherry-pick的关系

`git cherry-pick <commit-hash>`可视为"单次提交的Rebase"：将指定提交的diff以patch形式应用到当前分支，生成新哈希。其底层机制与`git rebase`相同，差异在于cherry-pick可跨越任意距离选取单个或多个不连续的提交，而rebase处理的是连续的提交序列。

### 与Git Bisect的协同

`git bisect`通过二分法在提交历史中定位引入Bug的提交，其效率直接依赖于历史的线性程度。在一个包含大量合并提交的DAG中，`git bisect`默认跳过合并提交本身（因为合并提交本身不引入代码变更），但复杂的交叉合并结构会使二分路径不确定。保持线性历史的Rebase策略在此场景下将`git bisect`的查找次数严格控制在 $\lceil \log_2 n \rceil$ 以内。

### 与CI/CD流水线的整合

现代CI系统（如GitHub Actions、