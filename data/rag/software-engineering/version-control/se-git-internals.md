---
id: "se-git-internals"
concept: "Git内部原理"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 3
is_milestone: false
tags: ["原理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Git内部原理：对象模型与引用

## 概述

Git本质上是一个**内容寻址文件系统**（content-addressable filesystem），其所有数据都存储在项目根目录下的 `.git/` 文件夹中。与传统版本控制系统（如SVN）追踪文件差异不同，Git保存的是每次提交时整个项目的**完整快照**（snapshot）。理解这个根本差异，才能真正明白为何Git的分支切换和合并操作如此高效。

Git的对象模型由Linus Torvalds于2005年4月设计，最初仅用2周时间完成原型。整个对象数据库的寻址机制基于SHA-1哈希算法（2005年后的新版本已逐步迁移到SHA-256），每个对象通过其内容的40位十六进制哈希值唯一标识。这意味着内容相同的文件在整个仓库历史中只会存储一次，天然实现去重。

理解Git内部原理能解释很多实际操作背后的逻辑：为什么两个内容相同的文件共享同一个blob对象、为什么`git reset --hard`可以精确回滚到任意历史状态、为什么分支只是一个41字节的文本文件。这些不是魔法，而是对象模型的直接结果。

---

## 核心原理

### 四种对象类型

Git对象数据库（`.git/objects/`）中只有四种对象类型，它们共同构成整个版本历史。

**blob对象**：存储文件内容，不包含文件名或权限信息。一个blob的哈希值完全由文件内容决定，与路径无关。若两个文件内容相同，它们对应同一个blob，节省存储空间。可用 `git cat-file -p <hash>` 查看其内容。

**tree对象**：类似文件系统的目录，记录一组blob和子tree的引用，同时保存文件名和权限（如 `100644` 普通文件、`100755` 可执行文件、`040000` 子目录）。一个tree的格式如下：

```
100644 blob a8c3... README.md
100755 blob f4e1... run.sh
040000 tree 9b2d... src/
```

**commit对象**：指向一个根tree对象，同时包含：父提交哈希（首次提交无父提交）、作者（author）、提交者（committer）、时间戳、提交消息。正是commit的链式引用构成了项目的完整历史有向无环图（DAG）。

**tag对象**：附注标签（annotated tag）会创建一个独立的tag对象，指向某个commit并包含标签者信息和消息。轻量标签（lightweight tag）则不创建对象，仅是一个引用文件，直接指向commit哈希。

### 对象的存储格式与SHA-1计算

每个Git对象在写入磁盘前，都会加上一个**头部（header）**，格式为：`"<type> <size>\0<content>"`。以一个内容为 `hello\n` 的blob为例，完整数据为 `"blob 6\0hello\n"`，对这段字节序列计算SHA-1，得到 `ce013625030ba8dba906f756967f9e9ca394464a`，随后用zlib压缩后存入 `.git/objects/ce/013625030ba8dba906f756967f9e9ca394464a`（前两位为目录名，后38位为文件名）。

### 引用（References）

引用（refs）是指向对象哈希的别名，存储在 `.git/refs/` 目录下。主要分三类：

- **分支引用**：`.git/refs/heads/main` 文件内容仅为一行40字符的commit哈希。创建新分支的代价极低，仅需新建一个41字节的文件。
- **远程引用**：`.git/refs/remotes/origin/main`，记录上次与远程同步时的状态。
- **标签引用**：`.git/refs/tags/v1.0`。

**HEAD**是一个特殊引用，存储在 `.git/HEAD`，通常内容为 `ref: refs/heads/main`（符号引用），指向当前所在分支。当处于"detached HEAD"状态时，HEAD直接存储一个commit哈希，而非指向分支引用。

**packed-refs**：当引用数量较多时，Git会将它们压缩进 `.git/packed-refs` 单个文件，以提升查找性能。

---

## 实际应用

**追踪`git commit`的底层操作**：执行 `git commit` 时，Git依次执行以下步骤：①为暂存区（index）中所有修改的文件创建blob对象；②构建对应目录结构的tree对象（递归地从叶节点向上构建）；③创建commit对象，指向根tree，并将父commit设为当前HEAD所指commit；④将当前分支引用文件更新为新commit的哈希。

**`git log` 的遍历原理**：`git log` 从HEAD所指commit出发，沿 `parent` 指针链不断回溯，按拓扑顺序输出。`git log --graph` 能展示分叉与合并，正是因为merge commit拥有两个或多个父引用。

**`git gc` 与packfile**：`.git/objects/` 中大量松散对象（loose objects）会影响性能。`git gc` 会将它们打包进 `.git/objects/pack/` 目录下的 `.pack` 文件（二进制格式，包含delta压缩），同时生成 `.idx` 索引文件用于快速定位。一个典型的大型项目在 `git gc` 后可将对象目录体积压缩60%以上。

---

## 常见误区

**误区一：分支是文件的副本**。许多初学者认为创建分支会复制整个项目文件。实际上，Git分支只是一个指向某个commit对象的41字节文件。切换分支时，Git根据目标commit的tree对象重建工作区文件，本质是对象引用的改变，而非文件的物理复制。这也是为什么Git的分支操作比SVN快几个数量级。

**误区二：commit保存的是差异（diff）**。SVN等系统存储的是文件变更差异，而Git每次commit存储的是**完整快照**——所有文件当前状态对应的tree和blob对象树。`git diff` 显示的差异是Git在展示时**实时计算**两个commit之间tree的差异，并非从存储中读取预先保存的diff。

**误区三：相同内容的文件会重复存储**。由于blob哈希由内容决定，若在不同目录下放置两个内容完全相同的文件，或者某个文件在修改后又改回原内容，Git只存储一个blob对象。这种内容寻址机制使得Git在存储空间上比看起来更高效。

---

## 知识关联

**与Git基础的衔接**：学习 `git add` 时知道它将文件放入暂存区（index），现在可以进一步理解：`git add` 实际上是在 `.git/objects/` 中创建blob对象，并更新 `.git/index` 二进制文件（记录blob哈希与文件路径的映射）。`git status` 通过比较index与HEAD commit的tree、以及index与工作区文件的状态来判断"已暂存"和"未暂存"的变更。

**分支与合并的底层支撑**：理解commit的DAG结构后，`git merge` 的三路合并（three-way merge）逻辑变得清晰：Git寻找两个分支的最近公共祖先commit（LCA），分别对比两个分支head与祖先的diff，再合并这两组变更。`git rebase` 则是将一系列commit对象重新创建（哈希改变），接在目标分支顶端。

**与远程操作的关系**：`git fetch` 本质上是下载远程仓库中本地缺少的对象（blob/tree/commit），并更新 `.git/refs/remotes/` 下的引用。网络传输使用packfile格式，仅传输本地不存在的增量对象，这也是Git分布式协作高效的根本原因。