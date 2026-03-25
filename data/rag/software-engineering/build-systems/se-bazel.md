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
# Bazel

## 概述

Bazel 是 Google 于 2015 年对外开源的构建系统，其前身是 Google 内部使用多年的 Blaze 系统。Google 工程师在管理数十亿行代码的单一代码仓库（Monorepo）时开发了 Blaze，目标是实现快速、可靠且可扩展的构建。Bazel 这个名字本身是 Blaze 的变位词（anagram）。目前 Bazel 由 Google 持续维护，版本已迭代至 7.x，并拥有活跃的开源社区。

Bazel 最核心的设计哲学是**可复现性（Reproducibility）**和**正确的增量构建（Correct Incremental Builds）**。传统构建工具如 Make 依赖文件时间戳来判断是否需要重新构建，容易产生"构建结果因机器不同而不同"的问题。Bazel 通过对每个构建动作的输入（源文件、依赖、工具链）进行精确的哈希指纹计算，确保相同输入必然产生相同输出，从而实现跨机器、跨时间的构建结果一致性。

Bazel 尤其适合大型多语言项目：它原生支持 Java、C++、Python、Go、Kotlin、Scala 等语言，并通过规则扩展机制（rules）支持更多技术栈。在 Google 规模下，一次完整构建可能涉及数万个目标（targets），Bazel 的并行化和分布式缓存能力在此场景下体现出显著优势。

---

## 核心原理

### 构建图与 BUILD 文件

Bazel 将整个项目表示为一个**有向无环图（DAG）**，图中的节点称为**目标（target）**。开发者在每个目录下创建名为 `BUILD` 或 `BUILD.bazel` 的文件，使用 Starlark 语言（一种 Python 子集）声明目标及其依赖关系。

一个典型的 `BUILD` 文件如下：

```python
java_library(
    name = "greeter",
    srcs = ["Greeter.java"],
    deps = ["//third_party:guava"],
)

java_binary(
    name = "app",
    srcs = ["Main.java"],
    deps = [":greeter"],
)
```

目标的完整标签格式为 `//path/to/package:target_name`，例如 `//src/main:app`。顶层的 `WORKSPACE` 文件（或新版的 `MODULE.bazel`）定义外部依赖来源，类似 Maven 的 `pom.xml` 但作用于整个仓库。

### 沙箱化执行与 Hermetic 构建

Bazel 的每个构建动作在**沙箱（sandbox）**中执行，沙箱仅包含该动作明确声明的输入文件，无法访问系统的任意文件。这一机制强制开发者完整声明依赖，避免隐式依赖导致的不可复现问题。在 Linux 上 Bazel 默认使用 Linux namespaces 实现文件系统隔离；在 macOS 上使用 `sandbox-exec`。

这种"密封构建（Hermetic Build）"意味着构建不依赖本地环境变量、随机 PATH 中的工具或未声明的系统库。要使用特定版本的编译器，必须通过工具链（toolchain）规则显式注册，Bazel 会管理该工具的下载和调用。

### 内容可寻址缓存与远程缓存

Bazel 的缓存机制基于**内容可寻址存储（Content-Addressable Storage，CAS）**。每个构建动作的缓存 Key 是由其所有输入文件内容的 SHA-256 哈希、命令行参数和环境变量共同组成的哈希值。只要 Key 命中缓存，Bazel 直接复用输出，无需重新执行该动作。

Bazel 支持三层缓存：
1. **本地磁盘缓存**：默认位于 `~/.cache/bazel`
2. **远程缓存（Remote Cache）**：通过 gRPC 协议连接到兼容 Remote Execution API（REAPI）的服务，如 Google Cloud Storage 或自建的 Buildbarn、BuildBuddy
3. **远程执行（Remote Execution）**：不仅缓存结果，还将构建动作分发到远程机器集群并行执行，可将大型项目的构建时间从小时级压缩到分钟级

---

## 实际应用

**Android 应用构建**：Google 官方的 Android 构建系统 `rules_android` 使用 Bazel 管理大型 Android 工程，将数百个模块拆分为独立的 `android_library` 和 `android_binary` 目标，修改单个模块只重新构建受影响的目标，而非整个 APK。

**多语言 Monorepo**：Stripe、Spotify 等公司将前端（TypeScript）、后端（Java/Scala）、移动端（iOS/Android）代码放在同一仓库，使用 Bazel 统一构建。`rules_nodejs`、`rules_swift`、`rules_kotlin` 等社区规则集覆盖各语言的构建逻辑。

**Docker 镜像构建**：`rules_docker`（已演化为 `rules_oci`）允许用 Bazel 目标声明 Docker 镜像的层次结构，并基于构建图的变更检测，只重新打包真正变化的镜像层，避免每次 CI 都全量重建镜像。

**测试分片与缓存**：Bazel 的 `bazel test` 命令原生支持测试结果缓存。若测试代码及其所有依赖均未变化，Bazel 直接报告上次通过的测试结果，跳过实际执行，这在大型代码库中可节省 70%~90% 的 CI 测试时间。

---

## 常见误区

**误区一：Bazel 的 BUILD 文件等同于 Makefile**

许多初学者认为 `BUILD` 文件只是"更复杂的 Makefile"。实际上两者存在根本差异：Makefile 描述的是**命令序列**（如何构建），而 `BUILD` 文件描述的是**声明式依赖图**（构建什么、依赖谁）。Bazel 根据这张图自动推导构建顺序和并行策略，开发者无需指定执行步骤。这也意味着 Bazel 目标的依赖必须完整声明，否则沙箱化执行会直接报错——而 Makefile 中漏写依赖可能悄悄运行成功，留下隐患。

**误区二：增量构建一定比全量构建快**

Bazel 的增量构建优势依赖于正确、完整的依赖声明。如果某个底层库（如通用工具模块）被大量目标依赖，修改该库会导致大量目标失效缓存，触发广泛重建。此时增量构建代价接近全量构建。解决方法是合理拆分构建目标粒度，避免过于宽泛的依赖关系，将频繁变更的代码与稳定代码在依赖图中隔离。

**误区三：Bazel 开箱即用，无需配置**

与 Maven、Gradle 相比，Bazel 的初期配置成本较高：需要编写 `WORKSPACE`/`MODULE.bazel`、为每个目录创建 `BUILD` 文件、配置工具链等。部分团队使用 `Gazelle` 工具（针对 Go 和 Java）自动生成 `BUILD` 文件来降低维护负担，但理解 Bazel 的构建图模型仍是必要前提。

---

## 知识关联

**与构建系统概述的关系**：理解通用构建系统概念（目标、依赖、增量构建）是使用 Bazel 的基础。Bazel 是这些概念的一种具体且严格的实现——它通过沙箱和哈希指纹将"增量正确性"从"尽力而为"变成了可数学保证的属性。

**与 CMake/Gradle 的对比**：CMake 面向 C/C++ 的生成式构建，Gradle 面向 JVM 生态的脚本式构建，两者均不强制声明完整依赖。Bazel 的严格性是其可复现性的代价，也是其在大规模场景下相比 Gradle 具备一致性优势的原因。Gradle 从 Bazel 借鉴了部分缓存思路，推出了 Build Cache 功能，但实现机制不同。

**Starlark 语言**：Bazel 的 `BUILD` 文件和宏（macro）使用 Starlark，掌握其语法（特别是不支持递归、无全局可变状态等限制）有助于编写自定义规则，扩展 Bazel 支持新语言或新构建模式。
