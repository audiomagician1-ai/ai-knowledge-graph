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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Cherry-pick与补丁

## 概述

`git cherry-pick` 是Git提供的一个命令，用于将某个特定提交（commit）的变更单独应用到当前分支，而无需合并整个来源分支。与 `git merge` 或 `git rebase` 不同，cherry-pick 操作的粒度是**单次提交**，它会根据该提交的差异（diff）在目标分支上重新生成一个新的提交对象，新提交拥有不同的SHA-1哈希值，但内容变更相同。

该命令由Linus Torvalds在Git早期版本（约2005年）的工作流设计中纳入，最初用于Linux内核开发团队的补丁（patch）管理流程。在内核开发中，维护者需要将不同贡献者提交的修复从 `mm`（内存管理）树或 `net` 树"精选"到主线（mainline）中，cherry-pick 因此成为多分支并行维护的关键手段。

在商业软件开发中，cherry-pick最典型的应用场景是**热修复回港（backport）**：当生产环境发现紧急Bug，开发人员在 `main` 分支上修复后，需要将该修复选择性地移植到 `release/2.4`、`release/2.3` 等旧版本维护分支，而不引入两个版本之间积累的其他功能变更。

---

## 核心原理

### cherry-pick 的工作机制

执行 `git cherry-pick <commit-hash>` 时，Git内部执行以下步骤：
1. 计算目标提交与其父提交之间的差异（即 `git diff <parent> <commit>`）；
2. 将该差异作为补丁（patch）应用到当前 `HEAD` 所指向的工作树；
3. 使用当前分支的上下文生成新的提交，新SHA-1与原始提交**不同**，但 `commit message` 默认保留，并会附加 `(cherry picked from commit <original-hash>)` 的追踪注释。

支持同时精选多个提交：
```bash
git cherry-pick A..B        # 精选从A之后到B的所有提交（不含A）
git cherry-pick A^..B       # 精选从A到B的所有提交（含A）
```

### 补丁文件（.patch）与 git am

当团队不共用同一Git仓库时（如开源项目通过邮件列表协作），可以将提交导出为标准Unix邮箱格式的 `.patch` 文件，再在另一仓库中应用。

```bash
git format-patch -1 <commit-hash>   # 将单次提交导出为 0001-xxx.patch
git am 0001-fix-memory-leak.patch   # 将补丁文件应用为新提交
```

`git format-patch` 生成的文件包含完整的提交元数据（作者、时间戳、提交信息）和 `diff` 内容，这与 `git diff > fix.patch` 然后 `git apply` 的方式的区别在于：`git am` 会完整保留原始作者信息，而 `git apply` 只修改文件不创建提交。

### 冲突处理与 `-x` 标志

cherry-pick 遭遇冲突时不会自动终止，而是暂停并标记冲突文件，开发者手动解决后执行 `git cherry-pick --continue` 恢复流程，或执行 `git cherry-pick --abort` 还原到操作前状态。

强烈建议在进行回港操作时添加 `-x` 标志：

```bash
git cherry-pick -x <commit-hash>
```

`-x` 会在提交信息末尾自动追加 `(cherry picked from commit abc1234)` 这一行，使回港历史可追溯，方便日后审计哪些修复已被移植到哪些分支。

---

## 实际应用

### 热修复回港（Hotfix Backport）

假设项目维护 `main`、`release/3.0`、`release/2.9` 三条分支。开发人员在 `main` 上修复了一个SQL注入漏洞（提交哈希 `f3a8c21`），需要将其同步到两个旧版本：

```bash
git checkout release/3.0
git cherry-pick -x f3a8c21

git checkout release/2.9
git cherry-pick -x f3a8c21
```

由于 `release/2.9` 中相关代码可能与 `main` 分支存在结构差异，cherry-pick 可能产生冲突，此时需要手工调整补丁内容，确保修复逻辑在旧版代码上下文中正确实现，而非简单地"套用"代码片段。

### 从错误分支提救提交

当开发者误将本应在 `feature/payment` 上的提交推送到了 `develop` 分支时，可以用 cherry-pick 将该提交"捞"到正确分支，再用 `git revert` 在 `develop` 上撤销该误操作，实现无损迁移。

### GitHub Pull Request 的 cherry-pick 等效操作

GitHub界面的 "Cherry pick" 按钮（出现在已合并PR的页面）本质上执行的正是 `git cherry-pick <merge-commit-hash> -m 1`，`-m 1` 参数指定以合并提交的第一父节点（目标分支）为主线基准来提取差异。

---

## 常见误区

### 误区一：cherry-pick 不会造成重复提交历史

很多开发者认为 cherry-pick 过后，原分支合并时Git会"识别"出重复内容而自动跳过。**这是错误的。** 由于 cherry-pick 产生的新提交哈希与原始提交不同，若后续将来源分支合并回目标分支，Git会将这两次提交视为不同变更，可能出现内容重复但形式不同的**双重补丁冲突**。解决方式是在合并时使用 `git rerere`（记录冲突解决方案）或在团队流程中明确规定 cherry-pick 后原分支不再合并回。

### 误区二：cherry-pick 等同于 rebase

`git rebase` 是将一段连续提交历史"重放"到新基点，操作的是**一组提交的序列关系**；而 cherry-pick 操作的是**离散的、用户指定的单个或多个提交**，两者的使用意图截然不同。rebase 会重写整段分支历史，cherry-pick 只在目标分支末尾附加新提交。

### 误区三：`-x` 标志在所有工作流中多余

部分团队认为有 PR 链接就足够追踪来源，省略 `-x`。然而在使用 `.patch` 文件通过邮件分发补丁（如Linux内核、Emacs等项目）的工作流中，没有中心化的PR系统，`-x` 附加的原始哈希是唯一的来源溯源依据，省略它会使补丁审计链断裂。

---

## 知识关联

**前置知识关联：** cherry-pick 的前提是理解Git的提交对象模型（commit object）和SHA-1哈希机制——正是因为每次 cherry-pick 生成全新哈希，才会出现双重补丁问题。变更日志管理（CHANGELOG）与 cherry-pick 直接交互：回港的修复条目需要同时更新旧版本分支的 `CHANGELOG.md`，而 `-x` 标志提供的原始哈希可以作为条目的精确引用。

**后续知识衔接：** 掌握 cherry-pick 后，学习 `git bisect` 时会更高效——bisect 用于定位引入Bug的提交，而一旦定位到目标提交，最常见的下一步操作正是对其执行 cherry-pick 回港或 revert 撤销，两个命令在Bug追踪与热修复的完整流程中形成自然的工作闭环。