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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

Git本质上是一个**内容寻址文件系统**（content-addressable filesystem），其核心设计思想是：所有数据都以对象形式存储，每个对象用其内容的SHA-1哈希值（40位十六进制字符串）作为唯一标识。这与传统版本控制系统（如SVN）按文件路径和版本号管理数据的方式截本不同。当你执行 `git init` 时，Git在当前目录创建 `.git` 文件夹，其中的 `objects/` 子目录就是这个对象数据库的物理存储位置。

Git的对象模型由Linus Torvalds于2005年4月设计，最初的Git代码仅有约1000行C代码，却已包含了blob、tree、commit三种核心对象类型。这种设计使得Git天然具备数据完整性验证能力——任何对象内容的修改都会产生不同的哈希值，从而被系统感知。

理解Git内部原理的实际价值在于：能够解释为何Git的分支切换（`checkout`）几乎是瞬时完成的，能够理解为何删除分支不会丢失提交对象，以及能够手动从损坏的仓库中恢复数据。

---

## 核心原理

### 四种对象类型

**Blob对象**存储文件的原始内容，不包含文件名。两个内容完全相同的文件（无论路径如何）在Git中只对应一个blob对象，这是Git节省存储空间的重要机制。blob对象的数据格式为：`"blob <content_length>\0<content>"`，对这段字节序列计算SHA-1得到其哈希。

**Tree对象**对应文件系统中的目录，记录该目录下各条目的模式（文件权限，如 `100644` 表示普通文件，`040000` 表示子目录）、对象类型、SHA-1哈希和文件名。一个tree对象的内容示例：
```
100644 blob a8f3e1... README.md
100644 blob 9c2d7f... main.py
040000 tree b7a5c2... src/
```

**Commit对象**是快照的元数据封装，包含五个固定字段：指向项目根tree对象的SHA-1、零个或多个parent commit的SHA-1（合并提交有两个parent）、author信息（姓名+邮箱+Unix时间戳+时区）、committer信息，以及提交消息。正是parent指针将所有commit串联成有向无环图（DAG）。

**Tag对象**（附注标签）存储标签名、创建者、时间戳、GPG签名及指向的对象SHA-1。轻量标签（lightweight tag）不创建tag对象，仅是一个指向commit的引用文件。

### 对象存储机制

Git将对象存储在 `.git/objects/` 目录下，以哈希值前2位作为子目录名，后38位作为文件名。例如哈希 `a8f3e1c9...` 对应路径 `.git/objects/a8/f3e1c9...`。对象内容用zlib压缩后写入。

可用底层命令直接操作对象数据库：
- `git hash-object -w <file>`：将文件写入对象库，输出其SHA-1
- `git cat-file -t <sha1>`：查看对象类型
- `git cat-file -p <sha1>`：打印对象内容

当对象数量增多时，Git会将松散对象（loose objects）打包为packfile（`.git/objects/pack/` 目录），同时生成 `.idx` 索引文件加速查找，这个过程通过 `git gc` 或 `git pack-objects` 触发。

### 引用（References）

引用是指向SHA-1的别名，存储在 `.git/refs/` 目录下。主要有三类：

- **分支引用**：位于 `.git/refs/heads/`，如 `main` 分支对应文件内容就是一个40字符的commit哈希
- **远程跟踪引用**：位于 `.git/refs/remotes/`，记录最后一次与远程同步时的commit位置
- **标签引用**：位于 `.git/refs/tags/`

**HEAD**是一个特殊文件（`.git/HEAD`），通常不直接存储SHA-1，而是存储一个符号引用（symbolic ref），如：`ref: refs/heads/main`。这意味着HEAD指向当前分支，当前分支又指向最新commit。当处于"游离HEAD"（detached HEAD）状态时，`.git/HEAD` 直接存储一个commit的SHA-1。

---

## 实际应用

**场景一：理解为何分支切换极快**
切换分支时（`git checkout feature`），Git仅需将 `.git/HEAD` 的内容改写为 `ref: refs/heads/feature`，然后根据新HEAD指向的commit的tree对象，更新工作目录文件。整个过程不需要生成diff或传输数据，因此切换即使在有数万个提交的仓库中也在毫秒级完成。

**场景二：手动恢复悬空对象**
执行 `git branch -d` 删除分支后，对应的commit对象并未立即删除，只是失去了引用（成为"悬空对象"）。通过 `git fsck --lost-found` 可以找到所有无引用对象，再用 `git cat-file -p <sha1>` 确认内容，最后执行 `git branch recovery-branch <sha1>` 重建引用，即可恢复"丢失"的提交。

**场景三：理解合并提交**
当执行 `git merge` 产生合并提交时，该commit对象包含两个parent字段，分别指向被合并的两个分支的最新commit。这就是为什么 `git log --graph` 能够可视化分叉与合并——它直接读取commit对象中的parent链。

---

## 常见误区

**误区一：认为分支是提交的"副本"**
很多初学者认为创建分支会复制代码。实际上，分支仅是 `.git/refs/heads/` 下一个40字节的文件，存储一个commit的SHA-1。创建100个分支的存储成本仅仅是100个小文件，它们都指向同一套对象，没有任何数据被复制。

**误区二：认为commit存储的是文件差异（diff）**
SVN等系统存储增量差异，但Git的commit存储的是完整快照——每次提交都保存当时所有文件的tree结构。Git的存储效率依靠blob对象的内容去重（相同内容只存一份）和packfile的delta压缩来实现，而非在commit层面存储diff。

**误区三：混淆轻量标签与附注标签的内部结构**
`git tag v1.0`（轻量标签）只在 `.git/refs/tags/v1.0` 写入一个commit的SHA-1；而 `git tag -a v1.0 -m "release"` 创建的附注标签，在该文件中存储的是一个**tag对象**的SHA-1，tag对象再指向commit对象。因此只有附注标签能被 `git cat-file -t` 识别为 `tag` 类型。

---

## 知识关联

**前置依赖**：掌握 `git add`、`git commit`、`git branch` 等基础操作是理解本文的前提。`git add` 的本质是将文件写入对象库并更新索引（`.git/index`），`git commit` 的本质是创建tree和commit对象并移动HEAD。

**横向关联**：本文的对象模型直接解释了 `git rebase` 的工作方式——rebase是基于原commit内容创建一系列新的commit对象（新SHA-1），而非移动原对象；也解释了 `git stash` 实际上创建了一个特殊的commit对象存储在 `refs/stash` 引用中。理解对象的不可变性（immutable）和引用的可变性，是理解所有Git高级操作的统一框架。