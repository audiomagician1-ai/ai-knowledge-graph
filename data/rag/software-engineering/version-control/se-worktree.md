# Git Worktree

## 概述

Git Worktree 是 Git 2.5 版本（2015年7月20日正式发布）引入的核心功能，由 Nguyễn Thái Ngọc Duy 主导设计实现，允许同一个本地仓库在文件系统上**同时挂载多个独立工作目录**，每个工作目录可检出不同的分支或提交。与 `git clone` 创建完整副本不同，所有 Worktree 共享同一个 `.git` 对象数据库（objects store）——这意味着任意一个 Worktree 中产生的提交对象，其他所有 Worktree 无需 `fetch` 即可立即访问。

在 Git Worktree 出现之前，并行处理多分支任务的主流方案有两种缺陷：`git stash` 会强制打断当前未完成工作的上下文（IDE 的调试状态、构建缓存等会丢失）；而手动 `git clone` 则会在 `.git` 目录完整复制所有历史对象，对于 Linux 内核（`.git` 目录超过 3GB）或 Chromium 等大型项目，此方案在磁盘空间和 I/O 成本上均不可接受。Git Worktree 通过共享对象库机制彻底解决了上述矛盾：附加 Worktree 只需占用工作区文件和极少量元数据（通常不足 1KB），而与主仓库共享全部 Git 对象。

Git 官方手册（`git-worktree(1)`）将该功能描述为"Manage multiple working trees attached to the same repository"，强调其**附着（attached）**语义：每个 Worktree 都是同一仓库的有效组成部分，而非外部副本。

## 核心原理

### 目录结构与元数据布局

执行 `git worktree add ../hotfix main` 后，Git 在文件系统层面执行以下操作：

1. 在 `../hotfix` 创建工作区目录，并写入一个名为 `.git` 的**普通文件**（非目录），文件内容形如 `gitdir: /home/user/project/.git/worktrees/hotfix`
2. 在主仓库的 `.git/worktrees/hotfix/` 下生成三个关键元数据文件：
   - `gitdir`：指向附加工作区中 `.git` 文件的绝对路径（双向引用机制）
   - `HEAD`：独立存储该 Worktree 当前检出的引用（如 `ref: refs/heads/main`）
   - `commondir`：值为 `../..`，指向主仓库 `.git` 目录，使该 Worktree 得以访问共享对象库、引用数据库和配置

这一"`.git` 文件而非目录"的设计是刻意为之：Git 所有子命令在执行前都会调用 `setup_git_directory()` 函数，该函数会识别 `.git` 文件并将 GIT_DIR 环境变量解析到正确的元数据路径，从而确保在任意 Worktree 目录执行 `git log`、`git commit` 等命令时行为完全一致。

### 分支独占性约束

Git Worktree 强制施加**分支单一检出约束**：同一具名分支在同一时刻只能被一个 Worktree 检出。当两个 Worktree 同时持有同一分支时，若其中一个提交了新对象并移动了 `refs/heads/main`，另一个 Worktree 的 HEAD 将立即指向过期提交——这会造成数据完整性问题。Git 通过在 `.git/worktrees/<name>/HEAD` 中记录锁定状态来防止此场景，尝试在已被占用的分支上添加 Worktree 时，会报错：

```
fatal: 'main' is already checked out at '/home/user/project'
```

若确实需要在相同提交上开展只读审查，可使用 `--detach` 参数绕过此限制：

```bash
git worktree add --detach ../review abc1234f
```

分离 HEAD 状态的 Worktree 没有对应分支引用，因此不受独占性约束，适合代码审查、性能基准测试等只读场景。

### 对象共享的存储效益

设仓库历史对象总大小为 $S_{objects}$，工作区文件大小为 $S_{wt}$，则：

- 完整克隆的磁盘占用：$S_{clone} = S_{objects} + S_{wt}$
- 附加 Worktree 的磁盘占用：$S_{worktree} \approx S_{wt} + \epsilon$，其中 $\epsilon$ 为元数据文件大小（通常 $< 1\text{KB}$）

对于 Linux 内核仓库，$S_{objects} \approx 3.2\text{GB}$，$S_{wt} \approx 1.2\text{GB}$，使用 Worktree 而非克隆每个附加工作区可节约约 3.2GB 存储，并跳过对象传输阶段，创建速度从分钟级降为秒级。

## 关键命令与工作流

### 完整命令参考

| 命令 | 作用 | 关键参数 |
|------|------|----------|
| `git worktree add <路径> <分支>` | 创建新 Worktree 并检出指定分支 | `--detach` 分离HEAD；`-b <新分支>` 同时新建分支 |
| `git worktree list` | 列出所有 Worktree 的路径、HEAD 提交和分支 | `--porcelain` 输出机器可读格式 |
| `git worktree remove <路径>` | 删除指定 Worktree（工作区须干净） | `--force` 强制删除含未提交修改的 Worktree |
| `git worktree lock <路径>` | 锁定 Worktree 防止被 `prune` 清理 | `--reason <文字>` 记录锁定原因 |
| `git worktree unlock <路径>` | 解除锁定 | — |
| `git worktree prune` | 清理已失效（路径不存在）的 Worktree 元数据 | `--dry-run` 预览将被清理的条目 |
| `git worktree move <旧路径> <新路径>` | 移动 Worktree 目录并自动更新元数据（Git 2.17+） | — |

### 创建 Worktree 时同步新建分支

```bash
# 从 origin/main 创建新分支 hotfix-403 并挂载工作区
git worktree add -b hotfix-403 ../hotfix origin/main
```

执行后，`../hotfix` 目录完成 `origin/main` 最新提交的检出，同时在本地创建 `hotfix-403` 分支，整个过程无需切换当前工作目录。

## 实际应用场景

### 场景一：紧急热修复不中断功能开发

例如：开发者正在 `feature/payment-v2` 分支进行支付模块重构，已修改 23 个文件且尚未达到可提交状态。此时生产环境出现 P0 级 BUG，需要立即在 `main` 分支上修复并部署。

```bash
# 当前工作区保持不动，另开工作区处理热修复
git worktree add ../hotfix-prod main
cd ../hotfix-prod
# 执行修复、提交、推送
git commit -am "fix: 修复支付金额精度丢失问题 (#1203)"
git push origin main
# 回到功能开发，工作区原封未动
cd ../my-project
```

整个过程中，`feature/payment-v2` 分支的 23 个已修改文件、IDE 的调试断点、`node_modules` 缓存均未受到任何干扰。

### 场景二：并行运行多版本测试

在维护同时支持 v1 和 v2 API 的项目时，可以为每个维护分支创建独立 Worktree，并在各自目录中并发执行测试套件，无需反复切换分支重新编译：

```bash
git worktree add ../project-v1 release/v1
git worktree add ../project-v2 release/v2
# 终端1：cd ../project-v1 && npm test
# 终端2：cd ../project-v2 && npm test
```

### 场景三：CI/CD 构建隔离

部分 CI 系统（如 Jenkins Pipeline）利用 Git Worktree 在同一 Agent 上为不同构建任务分配独立工作目录，所有任务共享 Git 对象缓存，可将冷启动时的 `git clone` 替换为毫秒级的 `git worktree add`，显著缩短 CI 等待时间。

### 场景四：大型 Monorepo 子模块并行构建

对于 Google 级别的 Monorepo，团队可将不同微服务模块分配到不同 Worktree，各模块开发者在各自目录下工作，提交后通过共享对象库实现零延迟的跨模块引用，同时避免了子模块（`git submodule`）复杂的嵌套引用管理。

## 常见误区

### 误区一：Worktree 等同于轻量级克隆

很多人将 Worktree 理解为"轻量克隆"，但两者存在根本差异：克隆拥有独立的引用命名空间（`origin` 远程），可独立 `fetch`；而 Worktree 共享同一引用空间，任意 Worktree 执行 `git fetch` 都会更新所有 Worktree 共享的远程追踪引用（如 `origin/main`）。这意味着在一个 Worktree 中执行 `git fetch` 后，切换到另一个 Worktree 时该 Worktree 的 `origin/main` 已是最新状态，无需重复 fetch。

### 误区二：手动删除 Worktree 目录就完成了清理

直接用 `rm -rf ../hotfix` 删除 Worktree 目录后，`.git/worktrees/hotfix/` 中的元数据**仍然存在**，且对应分支仍处于"被占用"锁定状态。正确的清理方式是使用 `git worktree remove ../hotfix`；若已手动删除目录，则需执行 `git worktree prune` 来清理孤立元数据。

### 误区三：所有 Git 操作在 Worktree 中行为完全相同

`git submodule update` 和 `git bisect` 在 Worktree 中的行为与主工作目录存在细微差异。`git submodule` 默认仅初始化当前工作区对应的子模块配置；`git bisect` 会修改共享的 `BISECT_HEAD` 状态文件，可能与其他 Worktree 的操作产生干扰，建议在进行 `bisect` 时锁定其他 Worktree（`git worktree lock`）。

### 误区四：Worktree 中的 stash 是共享的

Git 的 `stash` 存储在 `refs/stash` 引用下，该引用属于共享对象数据库，因此**所有 Worktree 共享同一个 stash 列表**。在 Worktree A 中执行 `git stash` 保存的内容，在 Worktree B 中同样可以通过 `git stash list` 看到并应用——这既是便利也是潜在的混淆来源。

## 知识关联

### 与 git stash 的对比

`git stash` 将未提交修改序列化为一个特殊的 stash commit 并压入栈结构，适合短暂的上下文切换（秒级任务）；Git Worktree 则维护完整的工作区状态（含未跟踪文件、index 状态、编辑器上下文），适合需要长期并行维护的分支任务。当并行任务预计超过 30 分钟或涉及构建状态保留时，Worktree 优于 stash。

### 与 git clone --reference 的关系

`git clone --reference <本地仓库>` 通过 alternates 机制实现对象库共享，语义上与 Worktree 相近，但克隆仍拥有独立的引用命名空间和完整 `.git` 目录结构。Git Worktree 是 alternates 机制的一种更紧密的集成形式，省去了引用同步的额外开销。

### 与 sparse-checkout 的协同

Git 2.25 引入的 `sparse-checkout` 允许 Worktree 仅检出仓库的特定子目录子集。将两者结合，可在 Monorepo 中为每个服务创建独立 Worktree 且每个 Worktree 只包含该服务相关文件，实现存储和 I/O 的双重优化：

```bash
git worktree add ../service-auth main
cd ../service-auth
git sparse-checkout set services/auth shared/utils
```

### 在工程实践中的推荐搭配

Scott Chacon 与 Ben Straub 在《Pro Git》（第2版，2014年，Apress出版，ISBN 978-1-4842-0077-3）中