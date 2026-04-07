---
id: "se-bazel"
concept: "Bazel"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 3
is_milestone: false
tags: ["大规模"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Bazel

## 概述

Bazel 是 Google 于 2015 年开源发布的构建与测试工具，其内部版本名为 Blaze，已在 Google 内部使用超过十年。Bazel 的设计目标是支持超大规模代码库（Google 内部单一代码库包含数十亿行代码）的快速、可复现、可缓存构建，能够在数千台分布式机器上并行执行构建任务。

Bazel 之所以在业界受到广泛关注，是因为它提供了两个关键保证：**可复现性（Reproducibility）**和**正确性（Correctness）**。可复现性意味着相同的输入必然产生完全相同的输出——无论在哪台机器上构建、何时构建。正确性意味着 Bazel 只重新构建真正发生变化的部分，不会遗漏也不会多余地触发构建。这两个保证使得 Bazel 的增量构建和远程缓存机制极为可靠，是其区别于 Make、Gradle 等传统构建工具的根本所在。

Bazel 使用名为 **Starlark**（原称 Skylark）的领域专用语言编写构建规则，该语言是 Python 的严格子集，具有确定性和不可变性约束。构建描述文件分为 `BUILD`（或 `BUILD.bazel`）和 `WORKSPACE` 两类，前者定义构建目标，后者声明外部依赖。

## 核心原理

### 基于有向无环图（DAG）的依赖建模

Bazel 将整个代码库的构建关系建模为一个有向无环图（DAG），图中每个节点是一个**目标（Target）**，边表示依赖关系。每个目标由**标签（Label）**唯一标识，格式为 `//path/to/package:target_name`，例如 `//src/server:main_binary`。

Bazel 在执行构建前会先进行**加载（Loading）→ 分析（Analysis）→ 执行（Execution）**三个阶段。加载阶段解析所有 BUILD 文件；分析阶段根据规则生成**动作图（Action Graph）**，每个动作（Action）描述具体的命令、输入文件集合和输出文件集合；执行阶段才真正运行命令。三阶段分离使得 Bazel 能够在执行前完整推断整个构建图，从而实现精确的并行调度。

### 基于内容哈希的缓存机制

Bazel 使用每个动作的**输入文件内容哈希 + 命令字符串 + 环境变量**共同计算一个缓存键（Cache Key），而非依赖文件时间戳。这是 Bazel 可复现性的数学基础：只要缓存键相同，就直接使用缓存输出，完全跳过执行。

缓存分为两层：**本地动作缓存**（存储在磁盘的 `~/.cache/bazel` 目录下）和**远程缓存（Remote Cache）**。远程缓存通过 gRPC 协议与支持 Bazel Remote API 的服务器（如 BuildBuddy、Buildkite Remote Cache 或自建的 `bazel-remote`）通信。在 CI/CD 流水线中，开发者本地修改一行代码后触发构建，Bazel 只需重新执行受影响的少数动作，其余结果直接从远程缓存拉取，构建时间可从小时级降至分钟级。

### 沙箱隔离与密封性

Bazel 默认为每个动作创建**沙箱（Sandbox）**，每个动作只能看到其在 BUILD 文件中显式声明的输入文件，无法访问文件系统上的其他文件或未声明的环境变量。在 Linux 上，Bazel 使用 Linux 命名空间（`unshare` 系统调用）实现沙箱；在 macOS 上使用 `sandbox-exec`。

这种密封性（Hermeticity）强制要求开发者显式声明所有依赖，消除了因隐式依赖导致的"在我机器上能跑"问题。若某个 C++ 编译动作偷偷读取了未声明的头文件，沙箱会直接报错，而不是产生一个不稳定的构建结果。

### 规则系统与 Starlark

BUILD 文件中调用的 `cc_binary`、`java_library`、`py_test` 等都是**内置规则（Built-in Rules）**，开发者也可以用 Starlark 编写自定义规则。一个典型的规则定义包含 `attrs`（输入属性声明）、`implementation`（Python 风格的实现函数）和 `providers`（输出数据结构）三部分。Starlark 禁止 I/O 操作和随机性，所有函数必须是纯函数，这在语言层面保证了分析阶段的确定性。

## 实际应用

**Android/iOS 多平台应用构建**：Airbnb、Uber 等公司使用 Bazel 管理同时包含 Android、iOS 和后端服务的单一代码库（Monorepo）。通过配置 `android_binary` 和 `apple_framework` 规则，同一份业务逻辑代码可以交叉编译到多个平台，且不同平台的构建任务可完全并行。

**大规模 CI 加速**：在一个包含 5000 个构建目标的 Java 项目中，全量构建可能需要 40 分钟，但借助 Bazel 的增量构建和远程缓存，典型的 PR 构建仅需 3-5 分钟，因为大部分目标的缓存命中率超过 90%。

**工具链管理**：Bazel 通过 `toolchains` 机制和 `WORKSPACE` 中的 `http_archive` 规则下载并锁定特定版本的编译器（如 LLVM 15.0.6），确保所有开发者和 CI 机器使用完全相同的编译工具，消除因编译器版本差异导致的构建不一致。

## 常见误区

**误区一：Bazel 只适合超大型项目**。许多开发者认为 Bazel 的配置复杂度只有 Google 规模的团队才值得承受。实际上，Bazel 对中型 Monorepo（如 10-100 人团队）同样有价值，特别是在需要跨语言构建（如同时包含 Go、Python、TypeScript 的项目）或 CI 构建时间超过 15 分钟时，Bazel 的远程缓存收益非常显著。

**误区二：Bazel 的增量构建与 Make 的增量构建等价**。Make 使用文件时间戳判断是否重建，这在文件被 `touch` 后会错误触发重建，在时钟不同步的分布式环境中会产生错误结论。Bazel 使用内容哈希，时间戳完全无关，因此其增量判断在任何环境下都是正确的。

**误区三：在 BUILD 文件中可以使用 `glob` 通配符代替显式依赖声明**。`glob(["**/*.cpp"])` 虽然方便，但它会绕过 Bazel 的精确依赖追踪，导致任何新增文件都触发整个目标重建，破坏增量构建的效率。Bazel 官方建议仅在叶子节点的小范围内使用 `glob`，核心库应显式列出每个源文件。

## 知识关联

学习 Bazel 需要对**构建系统概述**中的依赖图、增量构建和构建规则有基本认识，Bazel 本质上是这些通用概念在极端规模约束下的具体实现。Bazel 的 Starlark 语言借鉴了 Python 语法，理解 Python 的函数式编程风格有助于编写自定义规则。

从 Bazel 出发，可以进一步学习 **Unreal Build Tool（UBT）**——Epic Games 为虚幻引擎设计的专用构建系统。UBT 同样面对超大规模 C++ 代码库（虚幻引擎源码约 300 万行），但其设计哲学与 Bazel 截然不同：UBT 使用 C# 编写构建逻辑而非 Starlark，且专注于游戏引擎的模块化架构，而非通用多语言支持。对比两者有助于理解不同领域对构建系统设计取舍的影响。此外，Bazel 的远程执行协议（Remote Execution API v2）已成为业界标准，Buck2（Meta）、Pants 等工具均与该协议兼容，理解 Bazel 的架构对掌握整个现代构建系统生态至关重要。