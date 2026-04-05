---
id: "git-basics"
concept: "Git基础"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 2
is_milestone: false
tags: ["版本控制"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# Git基础

## 概述

Git是由Linus Torvalds于2005年4月创建的分布式版本控制系统，最初是为了管理Linux内核的源代码开发而设计的。与CVS、SVN等集中式版本控制工具不同，Git的每个本地仓库都包含完整的项目历史记录，这意味着即使在没有网络连接的情况下也可以完整地提交、查看历史和创建分支。

Git使用SHA-1哈希算法（产生40位十六进制字符串）来唯一标识每一个提交对象、树对象和文件对象，这保证了数据的完整性——任何一个字节的变化都会导致哈希值完全不同。在AI工程开发运维场景中，Git不仅用于管理Python训练脚本和模型配置文件，还与MLflow、DVC等工具配合追踪实验版本，是可复现机器学习实验的基础设施之一。

## 核心原理

### 三棵树模型

Git在本地维护三个"区域"：工作目录（Working Directory）、暂存区（Staging Area / Index）和本地仓库（Repository）。工作目录是实际修改文件的地方；`git add`命令将修改写入暂存区，形成一个快照；`git commit`命令将暂存区的快照永久写入仓库历史。这个三阶段流程与SVN的"直接提交"模式完全不同，允许开发者精确控制哪些改动进入同一个提交。

### 对象存储结构

Git的底层存储由四种对象类型构成：**blob**（存储文件内容）、**tree**（存储目录结构）、**commit**（存储提交元数据和指向tree的指针）、**tag**（存储标签信息）。所有对象均以压缩格式存放在`.git/objects/`目录中，按哈希值的前2位作为子目录名。例如哈希值`a1b2c3d4...`会存储在`.git/objects/a1/b2c3d4...`路径下。这种内容寻址机制使得相同内容的文件在仓库中只存储一次，节省磁盘空间。

### 基础命令与工作流

以下是AI工程开发中最常用的Git操作链：

```
git init / git clone <url>        # 初始化或克隆仓库
git status                        # 查看三棵树的当前状态
git add <file> / git add .        # 将变更加入暂存区
git commit -m "feat: add ResNet config"   # 创建提交
git log --oneline --graph         # 可视化提交历史
git diff HEAD~1 HEAD              # 对比最近两次提交的差异
git remote add origin <url>       # 关联远程仓库
git push origin main              # 推送到远程分支
```

`git log`命令中，`HEAD`是一个特殊指针，始终指向当前所在分支的最新提交。`HEAD~1`表示当前提交的父提交，`HEAD~2`表示祖父提交，以此类推。

### .gitignore的重要性

在AI项目中，必须正确配置`.gitignore`文件，避免将以下内容提交到仓库：模型权重文件（`.pt`、`.h5`、`.pkl`）、数据集目录（通常几十GB以上）、Python虚拟环境目录（`venv/`、`.env/`）以及含有API密钥的`.env`配置文件。一旦敏感信息被提交，即使后续删除，在Git历史中仍然可以通过`git log`找回，需要使用`git filter-branch`或`BFG Repo-Cleaner`才能彻底清除。

## 实际应用

**场景一：追踪模型训练超参数变更**
在调整神经网络学习率时，将每次参数变更和对应实验结果写入提交信息，例如`git commit -m "exp: lr=0.001, batch=32, val_acc=0.923"`。配合`git log --oneline`可以快速对比多组实验的超参数历史，无需依赖额外的实验管理工具。

**场景二：使用git stash临时保存现场**
当训练脚本修改到一半，线上模型服务出现紧急bug需要立即修复时，可以执行`git stash`将未完成的修改临时存入堆栈，切换到生产分支修复后，再用`git stash pop`恢复现场，避免用临时文件备份代码的混乱做法。

**场景三：回滚错误的数据预处理代码**
若发现三个提交前引入了一个错误的数据归一化公式，可以使用`git revert <commit-hash>`创建一个新提交来撤销指定提交的改动，而不会破坏已有的提交历史——这在多人协作的AI项目中比`git reset --hard`更安全。

## 常见误区

**误区一：混淆`git reset`的三种模式**
`git reset`有三个关键参数，行为截然不同：`--soft`只移动HEAD指针，暂存区和工作目录保持不变；`--mixed`（默认）移动HEAD并重置暂存区，但保留工作目录修改；`--hard`移动HEAD、重置暂存区并丢弃工作目录的修改，数据无法通过常规手段恢复。AI工程师在回滚实验代码时误用`--hard`导致丢失未提交的模型改进是非常常见的事故。

**误区二：认为`git add .`等同于"保存全部文件"**
`git add .`确实会将当前目录所有变更加入暂存区，但它遵循`.gitignore`规则并且不会追踪空目录。更重要的是，如果`.gitignore`配置不当，执行`git add .`可能意外将数百MB的训练数据或敏感凭证加入暂存区。正确做法是先运行`git status`确认暂存内容，或使用`git add -p`进行交互式逐块确认。

**误区三：频繁使用`git push --force`覆盖远程历史**
当本地执行了`git commit --amend`或`git rebase`修改历史后，直接推送会失败，部分工程师会习惯性地加上`--force`强制覆盖。这在共享分支上会破坏其他团队成员的本地历史，导致他们的后续推送产生大量冲突。应使用更安全的`git push --force-with-lease`，该选项在检测到远程有其他人提交时会自动拒绝强制推送。

## 知识关联

学习Git基础需要具备**命令行基础**知识，因为Git的绝大多数操作通过终端命令完成，理解路径、文件权限和管道符是正确使用`git diff`、`git log --grep`等命令的前提。熟悉`cd`、`ls`、`cat`等命令也能帮助理解`.git/`目录的内部结构。

掌握Git基础后，下一步是学习**Git分支策略**。单人开发只需了解`git commit`和`git push`，但AI团队协作开发时需要设计合理的分支模型：例如为每个实验创建独立特性分支、使用`main`/`develop`双主干结构隔离生产代码，或者采用GitHub Flow中的Pull Request审查机制。Git分支策略是在当前所学提交、暂存、回滚操作基础上，应用于多人协作场景的完整工作流设计。