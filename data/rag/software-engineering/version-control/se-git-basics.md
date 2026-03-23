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
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.375
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Git基础

## 概述

Git 是由 Linus Torvalds 于 2005 年 4 月为管理 Linux 内核代码而创建的分布式版本控制系统。与 CVS、Subversion 等集中式系统不同，Git 的每个本地仓库都包含完整的历史记录和版本管理能力，无需持续连接中央服务器即可完成大多数操作。Git 首次公开发布时，Torvalds 的设计目标是：速度、数据完整性保证以及对非线性开发（数千个并行分支）的支持。

Git 的工作模型建立在三个区域的概念之上：工作目录（Working Directory）、暂存区（Staging Area / Index）和本地仓库（Repository）。这三个区域的分离是 Git 有别于大多数版本控制系统的核心设计。理解这三个区域之间文件状态的流转，是掌握 Git 日常操作的基础。

对于软件工程团队而言，Git 的意义不仅在于备份代码，更在于它将每一次修改的"为什么"通过提交信息（commit message）永久记录下来，使得代码历史本身成为项目文档的一部分。一个规范的 Git 工作流能够让团队成员追溯任意时间点的代码状态，精确定位某个 Bug 是在哪次提交中引入的。

---

## 核心原理

### 仓库初始化：`git init` 做了什么

执行 `git init` 命令后，Git 会在当前目录下创建一个名为 `.git` 的隐藏目录。该目录包含以下关键子目录和文件：
- `objects/`：存储所有数据对象（blob、tree、commit、tag）
- `refs/`：存储分支和标签指针
- `HEAD`：一个文本文件，初始内容为 `ref: refs/heads/master`（或 `main`），指向当前所在分支
- `config`：仓库级别的配置文件，优先级高于全局配置 `~/.gitconfig`

删除 `.git` 目录将立即销毁整个仓库历史，工作目录中的文件不受影响但不再被 Git 追踪。`git clone` 的本质是复制远程仓库的完整 `.git` 目录内容到本地。

### 暂存区：Git 的"草稿台"

暂存区（Index）是 Git 独有的中间层，物理上对应 `.git/index` 这个二进制文件。它记录了"下一次提交将包含哪些内容"，允许开发者从一批修改中有选择地组织提交。

`git add <file>` 命令将文件的当前内容生成一个 blob 对象（以文件内容的 SHA-1 哈希值命名）存入 `objects/` 目录，并将该哈希值登记到 `index` 文件中。这意味着执行 `git add` 之后再修改文件，暂存区保存的仍是执行 `add` 时的版本，而非最新修改——这是初学者最常遭遇的困惑之一。

`git add -p`（交互式暂存）允许将同一文件中不同代码块（hunk）分批加入暂存区，实现"一次修改、多次提交"的精细控制。

### 提交工作流与对象模型

`git commit` 将暂存区的当前状态打包成一个 commit 对象。该对象包含四项内容：一个指向目录树快照（tree 对象）的指针、父 commit 的 SHA-1 哈希值、作者/提交者信息及提交时间戳，以及提交信息文本。

每个 commit 的 SHA-1 哈希值（40 位十六进制字符串，如 `a3f5c2d...`）由以上所有内容共同决定。修改提交信息或作者信息都会产生一个全新的哈希值，这也是为什么 `git commit --amend` 会改变 commit 历史、不能对已推送的提交随意使用的原因。

三个区域之间的状态转换命令如下：

```
工作目录  --git add-->   暂存区   --git commit-->  本地仓库
          <--git restore-- (丢弃工作目录修改)
                         <--git restore --staged-- (撤出暂存区)
          <-----------git checkout <commit>------  (切换到历史版本)
```

`git status` 同时展示工作目录与暂存区的差异，`git diff` 显示工作目录相对暂存区的差异，`git diff --staged` 显示暂存区相对上次提交的差异。

---

## 实际应用

**场景一：修复一个 Bug 同时调整了多处代码**

假设你在修复登录验证逻辑时，顺手改了一处 UI 样式。通过 `git add -p` 可以只将逻辑修复的代码块加入暂存区，先提交一个"fix: 修复登录 token 过期未跳转的问题"，再提交一个"style: 调整登录按钮边距"。这两个提交的职责清晰，日后查阅 `git log` 时便于理解。

**场景二：初始化一个新项目**

```bash
mkdir my-project && cd my-project
git init
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit: add README"
```

此时 `.git/refs/heads/master`（或 `main`）文件中存储了第一个 commit 的 SHA-1 值，项目历史正式建立。

**场景三：查看提交历史**

`git log --oneline --graph` 以简洁的单行格式附带 ASCII 分支图展示历史，常用于快速了解项目的提交脉络。`git show <commit-hash>` 可查看某次提交引入的具体变更内容。

---

## 常见误区

**误区一："暂存后再修改文件，下次提交会包含最新修改"**

执行 `git add` 时 Git 已将文件内容的快照写入 `objects/`，此后对该文件的修改不会自动更新暂存区。必须再次执行 `git add` 才能将新内容纳入下次提交。`git status` 此时会同时显示该文件出现在"Changes to be committed"和"Changes not staged for commit"两个区域，这一现象是最直接的提示。

**误区二："`git add .` 与 `git add -A` 效果相同"**

在 Git 2.x 版本中，`git add .` 从当前目录递归暂存所有新增和修改（包括子目录），也会暂存当前目录下的删除操作；`git add -A` 则无论当前所在目录，始终作用于整个仓库根目录，包含全部新增、修改和删除。在仓库子目录中运行时，两者行为存在差异。

**误区三："提交之后代码就安全了"**

`git commit` 仅将数据保存在本地 `.git` 目录中。只有执行 `git push` 将提交推送到远程仓库（如 GitHub、GitLab），数据才有了异地备份。本地磁盘损坏将导致未推送的所有提交永久丢失。

---

## 知识关联

**前置概念**：版本控制概述建立了"快照 vs. 差异"的基本认知框架。Git 采用快照模型——每次提交存储整个项目状态的快照（通过 SHA-1 去重避免冗余），而非记录文件变化的差异列表。这与 SVN 的 delta 存储策略截然不同，是理解 Git 高效分支切换的前提。

**后续方向**：掌握三区域工作流之后，**Git 分支策略**将在此基础上引入 `HEAD` 指针的移动机制——分支本质上只是指向某个 commit 的可移动指针，分支切换即是改变 `HEAD` 的指向。**忽略规则**（`.gitignore`）解决的是如何让特定文件永久不进入暂存区的问题，直接作用于 `git add` 的行为。**Git 内部原理**则会深入 `objects/` 目录，剖析 blob、tree、commit 四种对象类型的二进制存储结构——这些对象在本文中已多次提及，届时将得到完整的技术解释。
