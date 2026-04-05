---
id: "se-incremental-build"
concept: "增量构建"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 增量构建

## 概述

增量构建（Incremental Build）是构建系统的一种优化策略：**只重新构建自上次构建以来发生变化的文件及其依赖项**，而跳过未变化的部分。与每次从零开始的全量构建（Clean Build）相比，增量构建通过记录已构建产物的元信息，在下次构建时判断哪些输入已失效，从而大幅缩短构建时间。

增量构建的思想最早体现在1977年由Stuart Feldman为Unix开发的 `make` 工具中。`make` 通过比较目标文件（target）与依赖文件（prerequisite）的最后修改时间戳（mtime）来决定是否重新执行构建规则——这一机制奠定了此后40余年增量构建的基本范式。

在大型前端项目中，全量构建往往耗时数分钟；而经过合理配置的增量构建可将日常开发中的重新构建时间压缩至数秒甚至毫秒级别。这直接影响开发者的热重载体验、CI流水线的执行效率，以及团队整体的迭代速度。

---

## 核心原理

### 文件时间戳检测

最简单也是历史最悠久的失效判断机制。`make` 的规则可形式化为：

```
若 mtime(target) < max(mtime(prerequisite_i))，则重新构建 target
```

当任何依赖文件的修改时间晚于目标产物时，该目标被标记为"过期（stale）"并触发重建。时间戳方法的优点是开销极低，仅需一次系统调用 `stat()`；缺点是在以下场景会误判：文件内容实际未变但时间戳被更新（如 `touch` 命令、版本控制切换分支后未修改的文件），或跨机器/跨时区构建时时间戳不可信。

### 内容哈希比对

为克服时间戳的局限，现代构建工具改用**文件内容的加密哈希**作为失效依据。常见算法包括 MD5（128位）、SHA-1（160位）和 xxHash（非加密但速度极快）。构建系统在每次构建后将输入文件的哈希值存入缓存数据库（如 Gradle 的 `.gradle/buildOutputCleanup/cache.properties`，或 Webpack 的 `node_modules/.cache`）。下次构建时重新计算当前文件哈希并与存储值比对：

```
hash_current(file) == hash_cached(file) → 跳过构建
hash_current(file) != hash_cached(file) → 标记失效，触发重建
```

Vite 在开发模式下使用 `etag`（基于文件内容）缓存已转换的模块；Webpack 5 引入的持久化缓存（Persistent Cache）默认采用文件内容哈希，将缓存命中率从 Webpack 4 的内存缓存提升至跨会话复用。

### 依赖图追踪

仅检测直接输入文件不够——当一个 TypeScript 文件引用了已修改的类型声明时，它也必须重新编译。构建系统需要维护一张**有向无环图（DAG）**，节点为文件/模块，有向边表示"依赖于"关系。当某节点失效时，系统沿边向上传播，将所有**传递依赖**该节点的上游节点一并标记为失效。

Webpack 通过解析 `import`/`require` 语句在运行时动态构建依赖图，存储于内存的 `ModuleGraph` 对象；Vite 则借助浏览器原生 ESM 的按需加载特性，将依赖图的构建推迟到模块实际被请求时，使冷启动速度远快于 Webpack。`tsc --incremental` 则将依赖信息序列化为 `.tsbuildinfo` 文件（JSON格式），记录每个源文件的签名和引用关系，下次编译直接读取该文件而无需重新解析所有源码。

### 构建输出缓存（Build Cache）

依赖追踪解决了"哪些需要重建"的问题，而构建缓存解决的是"重建的结果能否复用"的问题。以 Gradle 的构建缓存为例：每个任务的**缓存键（cache key）**由任务类型、输入文件哈希、JVM版本、任务参数等组成；若两次构建的缓存键完全一致，则直接从本地或远程缓存服务器取回上次产物，完全跳过任务执行。这使得不同开发者机器或CI节点之间可以共享构建成果，实现**分布式增量构建**。

---

## 实际应用

**Webpack 5 持久化缓存配置**：在 `webpack.config.js` 中设置 `cache: { type: 'filesystem', buildDependencies: { config: [__filename] } }`，Webpack 会将模块编译结果存入磁盘。实测在中型项目（约500个模块）中，二次构建时间可从首次的约30秒降至2～4秒。

**TypeScript 增量编译**：在 `tsconfig.json` 中启用 `"incremental": true`，编译器生成 `.tsbuildinfo` 文件。当仅修改一个工具函数文件时，`tsc` 只重新检查依赖该文件的模块，在10,000行规模的项目中可将类型检查时间从8秒降至不足1秒。

**Vite 的模块热替换（HMR）**：Vite 利用其精确的 ESM 依赖图，在文件变化时仅向浏览器推送失效的模块边界，而非整页刷新。对于修改一个 Vue 单文件组件的 `<style>` 块的场景，Vite 可做到只替换样式而完全保留组件状态，这依赖于将 `<template>`、`<script>`、`<style>` 视为三个独立的虚拟模块并分别追踪。

---

## 常见误区

**误区一：时间戳比较已经足够可靠**  
在本地单机开发中时间戳通常有效，但在 Git 切换分支后，未修改的文件的 mtime 会被更新为 checkout 的时间，导致构建系统误判大量文件失效、触发不必要的全量重建。使用内容哈希则不受此影响——只有字节内容真正变化的文件才会失效。

**误区二：增量构建总是安全的，不需要偶尔执行全量构建**  
增量构建的正确性依赖于依赖图的完整性。若某构建工具存在依赖追踪漏洞（如未追踪动态 `import()` 的所有分支，或宏展开引入的隐式依赖），则缓存中可能留存过期的构建产物，导致运行时出现难以排查的 Bug。在发布前或出现奇怪编译错误时，执行 `make clean` 或 Webpack 的 `--no-cache` 进行全量构建是必要的验证手段。

**误区三：增量构建与热模块替换（HMR）是同一概念**  
HMR 是运行时的模块替换机制，作用于已启动的开发服务器；增量构建是编译阶段的产物复用策略，作用于构建过程本身。二者可以协同工作——Vite 先通过增量构建确定哪些模块需重新转换，再通过 HMR 将这些模块推送给浏览器——但各自解决不同层面的问题。

---

## 知识关联

**前置概念**：理解**构建系统概述**（如 Makefile 的目标-依赖规则、构建图的基本结构）是理解增量构建失效判断逻辑的前提。熟悉 **Webpack/Vite** 的模块解析机制（`resolve`、loader 管道）有助于理解两者依赖图的构建方式差异——Webpack 静态分析 + 运行时合并，Vite 按需解析 + 原生 ESM。

**后续概念**：**预编译头（Precompiled Headers, PCH）**是 C/C++ 编译器层面的增量构建优化，将 `<iostream>`、`<vector>` 等频繁包含的头文件预先编译为 `.pch` / `.gch` 二进制文件并缓存，本质上是对"不变的重量级依赖"做了粒度更细的哈希缓存——这与增量构建中"跳过未变化输入"的核心逻辑一脉相承，只是应用在编译单元（Translation Unit）而非模块文件的级别。