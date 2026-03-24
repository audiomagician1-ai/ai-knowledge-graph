---
id: "se-gitignore"
concept: "忽略规则"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 1
is_milestone: false
tags: ["配置"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 忽略规则

## 概述

忽略规则是 Git 版本控制中用于声明哪些文件或目录**不应被追踪**的机制。Git 通过读取名为 `.gitignore` 的文本文件，在执行 `git status`、`git add`、`git commit` 等命令时自动跳过匹配的路径。这一机制使仓库能够专注于源代码本身，而不把编译产物、日志文件、操作系统缓存等无关内容混入版本历史。

`.gitignore` 文件最早随 Git 1.3.0（2005年）正式引入，与 Git 本身的诞生仅相隔数月，说明 Linus Torvalds 在设计时很快意识到"排除噪声文件"与"追踪文件变更"同等重要。在此之前，开发者只能依赖 CVS 的 `.cvsignore` 文件做类似的事，但 Git 将该机制大幅扩展，支持递归匹配、否定规则等更丰富的语法。

忽略规则直接影响仓库的"干净程度"。一个未正确配置 `.gitignore` 的 Node.js 项目会把 `node_modules/`（可能含有数万个文件）意外提交，导致仓库体积膨胀数百 MB，并在每次 `git status` 时产生海量无意义的未追踪文件提示。

---

## 核心原理

### 模式匹配语法

`.gitignore` 使用 **glob 模式**，而非正则表达式。常用规则如下：

| 模式 | 含义 |
|------|------|
| `*.log` | 忽略所有以 `.log` 结尾的文件 |
| `build/` | 仅忽略名为 `build` 的**目录**（尾部斜杠标志） |
| `**/temp` | 忽略任意层级下名为 `temp` 的文件或目录（`**` 表示跨目录） |
| `!important.log` | **否定规则**：即使前面的规则命中，也强制追踪此文件 |
| `doc/*.txt` | 仅忽略 `doc/` 直接子目录下的 `.txt`，不递归 |

否定规则（`!`）有一个关键限制：**若父目录已被忽略，则无法用 `!` 解除其子文件的忽略状态**。例如先写 `logs/`，再写 `!logs/keep.log`，后者不会生效，因为 Git 整体跳过了 `logs/` 目录的扫描。

### 规则文件的优先级与作用域

Git 按以下三个层级查找忽略规则，**优先级由高到低**：

1. **仓库级** `.gitignore`：位于项目根目录，跟随仓库一起被提交，所有协作者共享。
2. **目录级** `.gitignore`：可放置于仓库内任意子目录，仅对该目录及其子目录生效。
3. **全局** `.gitignore_global`（或自定义路径）：通过 `git config --global core.excludesFile ~/.gitignore_global` 配置，作用于该用户在本机的**所有** Git 仓库，**不**提交到仓库中，适合放置 `.DS_Store`、`Thumbs.db`、`*.swp` 等操作系统或编辑器产生的个人文件。

另有 `.git/info/exclude` 文件，效果等同于本地全局忽略，但作用域仅限当前仓库，同样不会被提交，适合临时的本机调试需求。

### 规则对已追踪文件无效

`.gitignore` **只对从未被 `git add` 追踪过的文件生效**。若某文件已存在于 Git 的索引（index）中，即便后来在 `.gitignore` 里添加了对应规则，该文件仍会继续被追踪。必须先执行：

```bash
git rm --cached <文件路径>
```

从索引中删除该文件（`--cached` 参数保留本地磁盘文件），然后提交此变更，`.gitignore` 规则才会对其生效。这是初学者最常遇到的"规则写了却不起作用"的根本原因。

---

## 实际应用

**Python 项目**的 `.gitignore` 通常包含：

```
__pycache__/
*.pyc
.env
dist/
*.egg-info/
```

其中 `.env` 文件存储数据库密码、API 密钥等敏感信息，必须忽略，否则推送到 GitHub 等公开平台会造成安全事故。

**Java/Maven 项目**需忽略：

```
target/
*.class
*.jar
.idea/
```

`target/` 是 Maven 的编译输出目录，每次构建均会重新生成，提交它毫无意义且体积庞大。

**全局配置实践**：macOS 用户应在 `~/.gitignore_global` 中添加 `.DS_Store`，Windows 用户应添加 `Thumbs.db` 和 `desktop.ini`。这两类文件由操作系统自动创建，与项目逻辑无关，理应通过全局配置统一排除，而不必在每个项目的 `.gitignore` 中重复声明。

GitHub 在创建新仓库时提供的"Add .gitignore"功能，本质上是从官方维护的 [github/gitignore](https://github.com/github/gitignore) 模板库中拉取对应语言的预设规则文件，涵盖超过 150 种语言和框架。

---

## 常见误区

**误区一：认为 `.gitignore` 能删除已提交的文件**

`.gitignore` 只影响**未来**的 `git add` 行为，对已经存在于提交历史中的文件没有任何追溯效果。要从历史中彻底清除某文件，需使用 `git filter-branch` 或 `git filter-repo` 工具重写历史，这是完全不同的操作。

**误区二：全局 `.gitignore_global` 会影响协作者**

全局配置文件存储在本地用户目录，**不会**被推送到远程仓库，因此其他协作者的环境完全不受影响。这意味着团队共享的忽略规则（如忽略 `node_modules/`）必须写在仓库级 `.gitignore` 中并提交，而不能只放在个人全局配置里。

**误区三：`build/` 和 `build` 是等价写法**

`build/`（带尾部斜杠）表示只匹配**目录**，不会忽略同名文件。`build`（不带斜杠）则同时匹配同名的文件和目录。在存在名为 `build` 的构建脚本文件时，两种写法的行为差异将直接导致该文件是否被追踪。

---

## 知识关联

学习忽略规则需要先掌握 **Git 基础**中的暂存区（staging area）概念：理解 `git add` 将文件从工作区移入索引的机制，才能明白为何对已追踪文件需要 `git rm --cached` 才能解除追踪。

忽略规则还与 **`git stash`** 有细微交互——默认情况下，`git stash` 不会储藏被忽略的文件，除非显式传入 `--include-untracked` 和 `--all` 参数。

在团队协作场景下，忽略规则的配置质量直接关系到 **代码审查（Code Review）** 的效率：一个混入了大量二进制编译产物的 Pull Request，会让审查者难以辨别真正发生变更的源代码行。
