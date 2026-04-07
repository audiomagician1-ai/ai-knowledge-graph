---
id: "se-ci-cache"
concept: "构建缓存优化"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 2
is_milestone: false
tags: ["性能"]

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


# 构建缓存优化

## 概述

构建缓存优化是指在 CI/CD 流水线中，通过保存已完成的构建产物、依赖包和编译结果，使后续构建能够跳过重复的计算步骤，从而缩短构建时间的一类技术。其核心思路是"如果输入没变，输出也不会变"——将这一判断自动化，就能避免每次提交都从零开始构建。

该技术随着 2010 年代 Docker 多阶段构建和容器化 CI 的普及而被广泛采用。在此之前，构建服务器通常是长期运行的固定机器，依赖已经存在于磁盘上；而一次性容器化 Runner（如 GitHub Actions、GitLab CI 的 ephemeral runner）每次启动都是干净环境，导致 `npm install` 或 `pip install` 等步骤每次都要重新下载全部依赖，一个中型 Node.js 项目的依赖安装时间往往超过 3 分钟。构建缓存优化直接解决这一痛点。

对团队而言，构建缓存优化的价值不只是速度。当每次提交的反馈时间从 15 分钟压缩到 2 分钟，开发者在等待 CI 结果时不会切换上下文，代码审查流程也随之加速，这是构建缓存带来的次级效益。

## 核心原理

### 缓存键（Cache Key）的设计

缓存能否命中，取决于缓存键的设计是否准确反映"输入变化"。缓存键通常是一段字符串，由文件内容哈希或特定文件路径拼接而成。以 GitHub Actions 为例：

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

这里 `hashFiles('**/package-lock.json')` 会计算 lock 文件的 SHA-256 摘要，只要 `package-lock.json` 内容不变，哈希值相同，缓存就命中。如果错误地用 `package.json` 替代 `package-lock.json` 作为键的来源，那么在版本范围不变但实际安装版本已更新的情况下，缓存会错误命中，导致使用过期依赖。

良好的缓存键设计还应包含"回退键"（restore-keys），当精确键未命中时，使用前缀匹配找到最近的可用缓存作为起点，再做增量安装，而不是完全放弃缓存。

### 增量构建（Incremental Build）

增量构建的原理是追踪每个构建任务的"输入集合"，只有当输入发生变化时才重新执行该任务。Gradle 的增量编译通过分析 Java 类的依赖图，判断哪些类受到改动影响；Bazel 和 Buck 则使用内容寻址（content-addressed）存储，每个构建动作用其所有输入文件的哈希组合作为唯一标识。

以 Turborepo 为例，它为 monorepo 场景提供任务级增量缓存：计算公式为 `task_hash = hash(source_files + env_vars + task_definition + dependency_outputs)`。只要 hash 匹配，该包的构建输出直接从缓存还原，不执行任何命令，Turborepo 官方数据显示这可以让 monorepo 的重复构建速度提升 85% 以上。

### 远程缓存（Remote Cache）

本地缓存只对单台机器有效，而 CI 的 Runner 通常是无状态的，缓存需要持久化到外部存储。远程缓存将构建产物存储在共享的对象存储（如 S3、GCS）或专用缓存服务器中，不同 Runner 甚至不同开发者的本地机器都可以拉取同一份缓存。

Bazel 的远程缓存协议（Remote Execution API，REAPI）是该领域的开放标准，定义了 `ContentAddressableStorage`（CAS）接口。Nx Cloud、Turborepo Remote Cache、GitHub Actions Cache API 均采用类似的"上传时以 hash 为 key，下载时按 key 查找"机制。远程缓存命中意味着构建任务完全不需要在本机执行，直接下载已有产物，对于编译耗时数十秒的 C++/Rust 模块尤其有价值。

### Docker 层缓存

Docker 镜像的 `Dockerfile` 中每条指令生成一个层（layer），Docker 构建时会检查该层及之前所有层的指令和上下文是否变化。因此，将变化频率低的指令（如 `RUN apt-get install`、`COPY package*.json ./` + `RUN npm ci`）放在 `Dockerfile` 前部，将变化频率高的 `COPY . .` 放在后部，可以最大化层缓存复用率。在 BuildKit 中，`--cache-from` 参数可以指定远程镜像作为缓存来源，实现跨 Runner 的 Docker 层缓存共享。

## 实际应用

**Node.js 项目的依赖缓存**：在 GitHub Actions 中，使用 `actions/setup-node@v3` 时指定 `cache: 'npm'`，该 Action 会自动以 `package-lock.json` 的哈希为键缓存 `~/.npm` 目录。实测一个拥有 800 个依赖包的项目，冷启动安装需要 4 分 20 秒，缓存命中后降至 18 秒。

**Python 项目的虚拟环境缓存**：缓存路径应指向 `.venv` 或 pip 的全局缓存目录（`~/.cache/pip`），键为 `requirements.txt` 或 `poetry.lock` 的哈希值。注意缓存键还需包含 Python 版本，否则在矩阵构建中不同 Python 版本会错误共享缓存。

**Gradle 多模块项目**：在 CI 中挂载 `~/.gradle/caches` 和 `~/.gradle/wrapper`，并开启 Gradle 的 `--build-cache` 标志，可使 Gradle 的 Build Cache（Task Output Cache）生效。当某个模块的源码未改变时，该模块的编译任务输出直接从本地或远程 Build Cache 还原，整个多模块项目的构建时间可减少 40%–70%。

## 常见误区

**误区一：缓存键越粗粒度越好，命中率越高**。将整个 `src/` 目录的哈希作为缓存键，会导致任意一行代码改动都使依赖缓存失效——而依赖变化和代码变化根本是两件事。正确做法是将依赖缓存键绑定到 lock 文件，将构建产物缓存键绑定到实际影响产物的源文件集合，两者分别管理。

**误区二：缓存了 `node_modules` 目录本身比缓存 npm 缓存目录更快**。实际上 `node_modules` 包含大量小文件，压缩和解压一个 200MB 的 `node_modules` 目录往往需要 60 秒以上，有时比直接运行 `npm ci`（借助已缓存的 `~/.npm` 下载目录）还慢。缓存 npm 下载缓存目录后执行 `npm ci` 通常是更优方案。

**误区三：远程缓存总是比不用缓存快**。当远程缓存存储在地理位置较远的区域，而构建产物体积很大（如数百 MB 的编译产物）时，下载时间可能超过本地重新构建的时间。应监控缓存命中节省的时间与缓存上传/下载时间之比，仅对时间收益为正的任务启用远程缓存。

## 知识关联

构建缓存优化依赖对 lock 文件（`package-lock.json`、`poetry.lock`、`Cargo.lock`）机制的理解——lock 文件的存在是缓存键稳定性的前提，没有 lock 文件的项目无法做到可靠的依赖缓存。与之关联的下游实践是**并行构建**和**构建矩阵优化**：当每个任务的耗时因缓存而大幅缩短后，任务间的调度编排和并发度配置成为下一个瓶颈。此外，在 monorepo 场景中，构建缓存优化与**受影响范围分析**（affected analysis）配合使用——先判断哪些包受本次提交影响，再对受影响包执行增量构建，二者共同构成 monorepo CI 提速的完整方案。