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
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 增量构建

## 概述

增量构建（Incremental Build）是构建系统的一种优化策略：**只重新编译或处理自上次构建以来发生变化的源文件及其依赖项**，而不是每次都从头编译所有文件。其对立概念是"全量构建"（Clean Build），即清空所有中间产物后重新构建整个项目。

增量构建的思想最早随 Make 工具的诞生而普及。Make 由 Stuart Feldman 于 1976 年在贝尔实验室开发，通过比较目标文件与源文件的**修改时间戳（mtime）**来判断是否需要重新构建。这一机制沿用至今，并在后续工具（如 Gradle、Bazel、Ninja）中得到显著扩展和改进。

增量构建对大型项目意义尤为重大。以 Chromium 浏览器为例，其全量构建耗时通常超过 1 小时，而一次只修改单个 `.cc` 文件的增量构建仅需数秒。掌握增量构建的工作原理，有助于开发者配置正确的构建规则、避免"幽灵构建"等难以调试的问题。

---

## 核心原理

### 1. 基于时间戳的判断（Timestamp-Based）

最传统的增量构建判断方式，由 Make 首先采用。规则很简单：

> 若目标文件（target）的最后修改时间 **早于** 任意一个依赖文件（prerequisite）的最后修改时间，则该目标需要重新构建。

用伪公式表示：

```
需要重建 ⟺ mtime(target) < max(mtime(dep₁), mtime(dep₂), ...)
```

时间戳方案的优点是开销极低（只需一次 `stat` 系统调用），缺点在于：
- **文件内容没有实际变化，但时间戳被更新**（如 `touch` 命令或 `git checkout`）时，会触发不必要的重建；
- 跨机器同步文件时，时间戳无意义，无法复用构建缓存。

### 2. 基于内容哈希的判断（Content Hash-Based）

为解决时间戳的缺陷，Bazel、Buck、Gradle（部分任务）等现代构建工具改用**对文件内容计算哈希值**（常用 MD5 或 SHA-256）并持久化存储，每次构建时将新哈希与记录值比较：

```
需要重建 ⟺ hash(file_current) ≠ hash(file_last_build)
```

以 Bazel 为例，它将输入文件的 SHA-256 哈希连同构建规则的哈希一起用于计算"动作键"（Action Key），只有动作键发生变化时才执行该动作。这使得 Bazel 的远程缓存（Remote Cache）可以跨开发者共享：只要源文件内容相同，不同机器上的构建产物可以直接复用。

哈希方案的缺点是**计算哈希本身有开销**，对包含大量小文件的项目（如 Node.js 的 `node_modules`），哈希扫描可能成为性能瓶颈。

### 3. 依赖追踪（Dependency Tracking）

时间戳和哈希仅能判断"已知依赖"是否变化，而**自动发现隐式依赖**是增量构建正确性的关键。

以 C/C++ 编译为例，源文件 `a.c` 通过 `#include "b.h"` 引入头文件，若构建系统不知道这条依赖关系，则修改 `b.h` 时不会触发 `a.c` 的重新编译，导致**构建结果错误但不报错**（即"陈旧构建"问题）。

现代工具的解决方案：
- **GCC/Clang** 的 `-MMD -MF` 选项：编译时自动生成 `.d` 依赖文件，内容形如 `a.o: a.c b.h`，Make/Ninja 在下次构建时读取这些文件以更新依赖图；
- **Ninja** 在其 `.ninja` 规则中支持 `depfile` 字段，实现与上述 GCC 输出的无缝集成；
- **Gradle** 的 Task 输入/输出注解（`@InputFiles`、`@OutputDirectory`）让开发者显式声明任务依赖，框架据此维护增量状态。

---

## 实际应用

**场景一：Java 项目的 Gradle 增量编译**

Gradle 从 7.x 开始默认启用 Java 增量编译。当你只修改 `UserService.java`，Gradle 会：
1. 检测 `UserService.java` 的内容哈希发生变化；
2. 分析该类的 ABI（Application Binary Interface）是否改变（即公共方法签名是否变化）；
3. 若 ABI 未变，仅重编译 `UserService.java` 本身，不触及依赖它的其他类；
4. 若 ABI 改变（如新增了一个 `public` 方法），则级联重编译所有依赖该类的源文件。

**场景二：前端 Webpack 的持久化缓存**

Webpack 5 引入了基于文件系统的持久化缓存（`cache.type: 'filesystem'`），将模块的哈希与编译结果存储在 `.cache/webpack/` 目录。第二次构建时，未变化的模块直接从缓存读取，大型项目二次构建时间可从 60 秒降至 5 秒以内。

---

## 常见误区

**误区一：时间戳更新就一定需要重建**

有开发者认为，只要文件的 `mtime` 改变了就应该重建。实际上，`git stash pop` 或某些 IDE 的自动格式化操作会刷新时间戳，但文件内容可能完全没有变化。使用基于内容哈希的工具（如 Bazel）可以避免这类假阳性重建；而纯时间戳工具（如 Make）则无法区分这种情况。

**误区二：增量构建的结果与全量构建完全等价**

这是最危险的误区。当依赖追踪不完整时（例如，构建脚本中的隐式依赖未声明），增量构建可能产生**与全量构建不同的错误结果**，且不会有任何报错提示。Bazel 通过"沙盒执行"（Sandbox Execution）强制每个动作只能访问已声明的输入，以此在构建阶段就暴露缺失依赖，而不是等到运行时才出错。

**误区三：删除构建产物再重建等于全量构建**

执行 `make clean` 或删除 `build/` 目录确实会强制全量重建，但如果**构建系统的依赖图文件（如 Gradle 的 `.gradle/` 缓存元数据）没有清除**，某些工具仍会参考旧的依赖状态。真正意义上的全量构建需要同时清除源码变更历史记录和构建系统的元数据缓存。

---

## 知识关联

**前置概念**：学习增量构建需要先理解**构建系统概述**中的基本概念，包括"目标（target）""规则（rule）""依赖图（dependency graph）"等术语。增量构建本质上是在依赖图上进行最小化子图重算的过程。

**横向关联**：
- **Makefile 语法**：Make 的 `%.o: %.c` 模式规则是增量构建时间戳机制的直接载体；
- **构建缓存（Build Cache）**：增量构建的哈希机制是本地构建缓存的基础，Bazel 的远程缓存进一步将其扩展到分布式场景；
- **持续集成（CI）**：CI 系统中若每次都触发全量构建，则增量构建的哈希缓存可通过 artifact 存储在 CI 流水线的不同步骤之间传递，显著加快流水线执行速度。
