---
id: "se-ninja"
concept: "Ninja"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 83.0
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

# Ninja 构建系统

## 概述

Ninja 是一个专注于速度的小型构建执行器，由 Google 工程师 Evan Martin 于 2010 年创建，最初用于加速 Chromium 浏览器项目的构建过程。Chromium 的代码库规模庞大，传统的 Make 工具在增量构建时需要花费数十秒甚至数分钟来评估依赖关系，而 Ninja 通过极简的设计哲学将这个评估时间压缩到毫秒级别。Ninja 的第一个公开版本于 2012 年发布，其核心目标只有一个：在给定构建描述文件（`.ninja` 文件）的情况下，尽可能快地完成增量构建。

与 CMake 或 MSBuild 这类"高层级"构建系统不同，Ninja 并不负责检测编译器、管理依赖库或生成跨平台配置。Ninja 的 `.ninja` 文件几乎不可能由人工手写维护——它的定位是作为 CMake、GN、Meson 等高层级工具的**后端执行器**。CMake 在配置阶段通过 `cmake -G Ninja` 参数生成 `.ninja` 文件，之后由 Ninja 负责实际的编译调度与执行。这种分工使得 Ninja 在整个构建工具链中承担"执行引擎"的角色。

Ninja 之所以重要，在于它将增量构建的哲学推向极致：只重新编译真正发生变化的文件。在一个包含数千个源文件的 C++ 项目中，修改单个头文件后，Ninja 能够在不到一秒的时间内完成依赖图遍历并启动最小必要的重新编译任务。

## 核心原理

### 极简的 .ninja 文件格式

Ninja 的构建描述文件格式刻意设计得极其简单，只有六个顶层关键字：`rule`、`build`、`default`、`pool`、`subninja`、`include`。一个典型的规则定义如下：

```
rule cc
  command = gcc -c $in -o $out
  depfile = $out.d
  deps = gcc
```

其中 `$in` 和 `$out` 是 Ninja 内置变量，分别代表输入文件和输出文件列表。`depfile` 和 `deps = gcc` 告诉 Ninja 读取 GCC 生成的 `.d` 格式依赖文件，从而实现头文件级别的精确增量构建。这种依赖追踪机制是 Ninja 相比简单 Makefile 的关键优势之一。

### 构建图与并行执行策略

Ninja 在启动时将整个 `.ninja` 文件解析为一张有向无环图（DAG），图中每个节点代表一个文件，每条边代表构建依赖关系。Ninja 的并行执行默认线程数为当前机器的逻辑 CPU 核心数加 2（即 `N+2` 个并行任务），这个公式的设计考虑了 I/O 等待期间的 CPU 利用率。用户可以通过 `-j` 参数手动指定并行度，例如 `ninja -j 8` 强制使用 8 个并行任务。

Ninja 使用时间戳和文件哈希的组合来判断文件是否过期。与 Make 仅依赖时间戳不同，Ninja 通过 `restat` 规则属性支持"输出未变化则不触发下游重建"的优化——如果一次编译产生的目标文件内容与之前完全相同，Ninja 不会标记其下游目标为需要重建。

### 最小化启动开销

Ninja 的二进制文件本身极为精简，在 Linux 系统上通常小于 200KB。其设计刻意避免任何复杂的脚本语言解析、变量展开逻辑或条件判断——这些功能都必须由生成 `.ninja` 文件的上游工具（如 CMake）在配置阶段完成。Ninja 的解析器对 `.ninja` 文件采用单遍扫描，不支持循环、条件分支或函数定义。正是这种"无脑执行"的设计使得 Ninja 的启动时间通常在 10 毫秒以内，而 GNU Make 在处理复杂 Makefile 时光是解析阶段就可能消耗数百毫秒。

## 实际应用

**在 CMake 项目中使用 Ninja**：只需在 CMake 配置时指定生成器即可：
```bash
cmake -S . -B build -G Ninja
cmake --build build
```
生成的 `build/build.ninja` 文件包含所有编译规则，后续每次执行 `ninja -C build` 时只会重新编译修改过的源文件。

**Android NDK 构建**：Android 的 NDK 构建系统从 r14 版本开始默认使用 Ninja 作为后端，取代了原有的 GNU Make 方案。对于包含大量 C/C++ 模块的 Android 项目，切换到 Ninja 后端通常可以将增量构建时间缩短 40%–70%。

**Chromium 项目的 GN + Ninja 工作流**：Chromium 使用 GN（Generate Ninja）工具替代 CMake 来生成 `.ninja` 文件。在一台 32 核工作站上，Chromium 的全量构建通过 Ninja 的并行调度可以在约 20 分钟内完成，而早期使用 Make 的版本需要超过 1 小时。

**与 ccache 集成**：Ninja 可以通过在规则的 `command` 字段中将编译器替换为 `ccache gcc` 来无缝集成编译缓存工具，无需任何特殊配置，因为 Ninja 对命令内容完全透明。

## 常见误区

**误区一：Ninja 可以独立使用来管理项目构建**。由于 `.ninja` 文件格式缺乏条件逻辑、平台检测和依赖查找能力，几乎没有项目会直接手写 `.ninja` 文件。Ninja 必须配合 CMake、GN 或 Meson 等工具使用，自行维护 `.ninja` 文件在中型项目中即不可行也无意义。

**误区二：Ninja 的速度优势主要来自更好的并行算法**。实际上，Ninja 与 Make 在并行调度算法上差异不大，都是基于 DAG 的拓扑排序。Ninja 的速度优势主要来自两点：一是极低的解析和启动开销（毫秒级 vs. Make 的百毫秒级），二是基于 `depfile` 的精确头文件依赖追踪减少了不必要的重新编译。对于全量构建（首次构建），Ninja 相对于 Make 的速度提升非常有限。

**误区三：Ninja 与 MSBuild 是平行替代关系**。MSBuild 是一个完整的构建系统，负责从项目描述到编译执行的全流程；Ninja 只负责执行阶段。在 Windows 上，CMake 可以生成 MSBuild 项目文件或 `.ninja` 文件，两者是同一层级中 CMake 可选的不同后端，而非 Ninja 取代 MSBuild。

## 知识关联

学习 Ninja 需要先理解 **CMake** 的配置阶段——CMake 的 `cmake -G Ninja` 命令负责生成 Ninja 所需的 `.ninja` 文件，理解 CMake 的 `CMakeLists.txt` 如何被翻译为构建规则有助于读懂生成的 `.ninja` 文件内容。**MSBuild** 提供了对比视角：MSBuild 将项目描述（`.vcxproj`）和构建执行合为一体，而 Ninja 刻意只做执行层，这种对比清晰展示了"生成器与执行器分离"架构的权衡。

进阶学习可以转向 **Gradle**：Gradle 面向 JVM 生态（Java/Kotlin/Android），内置了依赖管理、插件系统等高层功能，是 Ninja 所刻意回避的功能范畴。对比 Ninja 的"极简执行器"定位与 Gradle 的"全功能构建平台"定位，能够帮助理解构建工具在功能边界上的不同设计决策。此外，了解 **GN**（Chromium 的元构建系统）可以深入理解 Ninja 文件格式的最大化利用方式。