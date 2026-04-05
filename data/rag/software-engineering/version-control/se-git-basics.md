---
id: "se-git-basics"
concept: "Git基础"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 1
is_milestone: false
tags: ["Git"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Git基础

## 概述

Git 是由 Linus Torvalds 于 2005 年 4 月为管理 Linux 内核源代码而开发的分布式版本控制系统。最初版本仅用 10 天完成原型，第一个正式版本 Git 0.99 于同年 7 月发布。与 CVS、SVN 等集中式系统不同，Git 的每个本地仓库都包含完整的历史记录和版本信息，无需持续连接中央服务器即可提交、查看历史或创建分支。

Git 的核心数据模型不是基于文件差异（delta）存储，而是基于**快照**（snapshot）存储。每次提交时，Git 会对当时所有被跟踪文件拍摄一张完整快照，并保存指向该快照的引用。若某文件未发生变化，Git 不会重复存储其内容，而是保存一个指向上一个相同文件的链接。这种设计使得 Git 的分支操作极为廉价，切换分支只需移动一个 40 字节的 SHA-1 指针。

理解 Git 的工作流对于软件团队协作至关重要。一个错误的 `git push --force` 可以覆盖团队成员的工作，而正确掌握暂存区机制则允许开发者将一个文件的部分修改拆分成多个语义清晰的提交，大幅提升代码审查效率。

---

## 核心原理

### 仓库初始化与 .git 目录结构

执行 `git init` 后，Git 在当前目录创建 `.git` 隐藏目录，这是整个仓库的数据库。`.git` 目录包含以下关键子目录和文件：

- **objects/**：对象存储区，存放所有 blob（文件内容）、tree（目录结构）、commit（提交）和 tag 对象，以 SHA-1 哈希的前 2 位作为子目录名，后 38 位作为文件名。
- **refs/heads/**：存放各本地分支指针，每个文件内容是一个 40 字符的 SHA-1 哈希值。
- **HEAD**：一个文本文件，通常内容为 `ref: refs/heads/main`，指向当前所在分支。
- **config**：仓库级别的配置文件，优先级高于全局配置 `~/.gitconfig`。
- **index**：暂存区的二进制索引文件，记录下次提交将包含的文件快照。

对于已有项目，`git clone <url>` 不仅下载所有对象，还会自动设置名为 `origin` 的远程仓库引用，并将默认分支检出到工作区。

### 三个工作区域与文件状态转换

Git 管理文件时涉及三个截然不同的区域：

1. **工作区**（Working Directory）：磁盘上实际可编辑的文件。
2. **暂存区**（Staging Area / Index）：下次提交的准备区域，存储在 `.git/index` 文件中。
3. **本地仓库**（Local Repository）：已提交的永久历史，存储在 `.git/objects/` 中。

文件状态转换遵循固定路径：`Untracked → Staged → Committed → Modified → Staged`。执行 `git add <file>` 将工作区的修改写入暂存区（即更新 `.git/index` 并在 `objects/` 中创建对应的 blob 对象）。执行 `git commit` 则基于暂存区当前内容创建一个新的 commit 对象，包含作者信息、时间戳、父提交的 SHA-1 引用以及根 tree 对象的引用。

`git status` 输出分为两栏：`Changes to be committed`（暂存区与上次提交的差异）和 `Changes not staged for commit`（工作区与暂存区的差异）。两栏同时出现意味着同一文件被修改后部分暂存、又继续修改。

### 提交对象与 SHA-1 哈希

每个 Git 提交对象包含固定格式的元数据，其 SHA-1 由以下内容共同决定：

```
commit <size>\0
tree <tree-sha1>
parent <parent-sha1>
author <name> <email> <timestamp> <timezone>
committer <name> <email> <timestamp> <timezone>

<commit message>
```

由于 SHA-1 的输入包含父提交哈希，修改历史中任何一个提交（例如通过 `git commit --amend`）都会导致该提交及其所有后代提交的哈希值全部改变。这是 Git 历史不可篡改性的数学基础，也是为何 `--amend` 已推送的提交会给协作者带来麻烦的根本原因。

`git log --oneline` 显示每个提交的缩短 SHA-1（默认 7 位）。当仓库规模增大时，Git 会自动使用更多位数以避免碰撞。Linux 内核仓库约有 100 万个提交，通常需要 12 位前缀才能唯一标识一个提交。

---

## 实际应用

**场景一：将一次大改动拆分为多个语义提交**

假设你同时修改了 `user.py` 中的登录逻辑和错误提示文案。使用 `git add -p user.py`（交互式暂存），Git 会将文件按 hunk（差异块）逐一呈现，你可以用 `y`（暂存）、`n`（跳过）、`s`（拆分更小块）来选择性暂存，从而将一个文件的修改拆分成两次独立的提交，分别对应功能修复和文案调整。

**场景二：撤销操作的正确选择**

- `git restore <file>`：丢弃工作区修改，恢复到暂存区版本（Git 2.23+ 推荐命令，替代旧版 `git checkout -- <file>`）。
- `git restore --staged <file>`：将文件从暂存区移出，退回工作区，但保留磁盘上的修改内容。
- `git commit --amend --no-edit`：将暂存区的新修改追加到上一次提交，且不修改提交信息，适合修正刚提交时遗漏的文件。

**场景三：初始化新项目的标准流程**

```bash
git init my-project
cd my-project
echo "# My Project" > README.md
git add README.md
git commit -m "init: add README"
git remote add origin https://github.com/user/my-project.git
git push -u origin main
```

`-u` 参数设置上游追踪关系，此后可直接使用 `git push` 和 `git pull` 而无需指定远程和分支名。

---

## 常见误区

**误区一：`git add .` 与 `git add -A` 完全相同**

在 Git 2.x 中，`git add .` 暂存当前目录及其子目录的所有变更（含新文件、修改、删除），行为已与 `git add -A` 一致。但在 Git 1.x 中，`git add .` 不会暂存当前目录以外的删除操作，而 `git add -A` 会处理整个工作区。若仓库中存在使用旧版 Git 的团队成员，这一差异可能导致提交内容不一致。

**误区二：`git commit -m` 之后文件就"备份到服务器"了**

`git commit` 只在本地仓库（`.git/objects/`）创建提交对象，不涉及任何网络操作。代码必须通过 `git push` 才会上传到远程仓库。新手常见的错误是连续提交数天后才首次推送，导致远程仓库无法及时反映进度，也无法触发 CI/CD 流水线。

**误区三：删除工作区文件等于告知 Git 删除了该文件**

直接在文件系统删除文件（如 `rm file.txt`）后，`git status` 会显示该文件为 `deleted`（未暂存状态），但该删除**不会**出现在下次提交中，除非执行 `git rm file.txt`（同时删除工作区并暂存删除操作）或 `git add file.txt`（将已删除状态暂存）。

---

## 知识关联

**与前置概念的衔接**：版本控制概述介绍了"为什么需要追踪文件历史"的动机，而 Git 基础将这一抽象需求具体化为 `git init`、`git add`、`git commit` 三个命令和三个工作区域的物理实现。SHA-1 快照模型是理解后续所有高级操作的基础。

**通向后续概念**：掌握 commit 对象的不可变性和 HEAD 指针的移动逻辑，是理解**Git 分支策略**（branch 不过是指向 commit 的可移动指针）的直接前提。`.git/info/exclude` 和 `.gitignore` 文件的优先级规则属于**忽略规则**的专项内容。`git commit --amend` 修改提交哈希的原理，则直接延伸至 **Cherry-pick 与补丁**（`git format-patch` 基于提交元数据生成 .patch 文件）以及 **Git 内部原理**（pack 文件、引用日志 reflog 的存储机制）等进阶主题。