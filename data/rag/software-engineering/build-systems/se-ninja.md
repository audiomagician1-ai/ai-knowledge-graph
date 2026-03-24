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
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Ninja 构建系统

## 概述

Ninja 是一个专为速度而设计的小型构建系统，由 Google 工程师 Evan Martin 于 2010 年开发，最初用于加速 Chromium 浏览器的构建过程。Chromium 项目庞大，在当时使用 Make 构建时单次全量构建需要数小时，增量构建也因 Makefile 解析开销过大而缓慢。Ninja 的诞生正是为了解决这一具体痛点：将构建系统的职责缩减到极致——只执行构建，不生成构建规则。

与 Make 不同，Ninja 的设计哲学是"不应该由人类手写"。Ninja 的输入文件（`.ninja` 文件）语法极为简单，仅包含规则（rule）和构建边（build edge）两种核心概念，整个语言规范文档不足 500 行。这种设计使 Ninja 在解析构建图时几乎没有额外计算，能在毫秒级时间内完成依赖分析，随后并行执行所有可并行的构建任务。

Ninja 在现代 C/C++ 生态中几乎无处不在：LLVM、Android AOSP、以及大量使用 CMake 的项目都默认将 Ninja 作为后端执行器。CMake 从 3.14 版本开始将 `Ninja` 列为官方推荐生成器之一，命令为 `cmake -G Ninja`。

## 核心原理

### 构建图与依赖跟踪

Ninja 将整个构建过程表示为一张有向无环图（DAG），图中每个节点是一个文件，每条边代表一条构建命令。`.ninja` 文件中的 `build` 语句声明输出文件、使用的规则以及输入文件：

```
build foo.o: cc foo.c
```

Ninja 通过对比输出文件与输入文件的修改时间戳（mtime）判断是否需要重新构建，这与 Make 的机制相同。但 Ninja 的特殊之处在于它还支持**依赖文件（depfile）**机制：编译器（如 GCC/Clang）在编译时可以生成 `.d` 文件，列出所有隐式头文件依赖，Ninja 在构建后自动读取并将这些依赖写入 `.ninja_deps` 数据库（SQLite 格式）。这样，当某个头文件发生变化时，Ninja 能准确识别哪些 `.cpp` 文件需要重新编译，避免漏编或过度编译。

### 并行执行模型

Ninja 默认并行度等于当前机器的 CPU 逻辑核心数，可通过 `-j N` 参数手动指定。其并行调度基于构建图的拓扑排序：所有入度为零（即依赖已满足）的构建节点会立即被提交到线程池执行。每当一个任务完成，Ninja 重新检查哪些节点的依赖已全部就绪，并立即调度它们，从而实现接近理论最优的并行效率。

相比之下，传统 `make -j` 的并行机制是在递归 Make 的子进程层面实现的，存在进程创建开销以及父子进程之间的同步损耗。Ninja 的单进程调度模型避免了这些开销，在核心数较多（如 32 核以上）时优势更为明显。

### `.ninja` 文件语法结构

Ninja 文件由以下几类语句组成：

- **rule**：定义一条构建规则，包含 `command` 变量，描述实际执行的 shell 命令。`$in` 和 `$out` 是内置变量，分别指向输入和输出文件列表。
- **build**：将具体文件与规则关联，声明依赖关系。
- **variable**：全局或局部变量赋值，用于避免重复书写编译器路径、编译选项等。
- **pool**：限制某类任务的并发度，例如链接任务通常内存消耗极大，可用 `pool link_pool` 将并发链接数限制为 4。

```
pool link_pool
  depth = 4

rule link
  command = clang++ $in -o $out
  pool = link_pool
```

### 重新生成检测

Ninja 文件本身也被纳入依赖管理。`.ninja` 文件中可以声明一条特殊的 `build build.ninja` 规则，当 CMakeLists.txt 或其他构建配置文件发生变化时，Ninja 会在执行构建前自动重新运行 CMake 重新生成 `.ninja` 文件，无需用户手动干预。

## 实际应用

### 与 CMake 配合使用

最常见的使用场景是通过 CMake 生成 Ninja 构建文件：

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 16
```

CMake 生成的 `build.ninja` 通常包含 `all`、`clean`、`install` 等伪目标（phony target），与 Makefile 的使用体验类似但执行速度更快。在一个包含约 2000 个编译单元的项目中，Ninja 的增量构建启动时间通常在 100ms 以内，而 Make 在同等规模下仅解析 Makefile 就需要数秒。

### Android NDK 构建

Android AOSP 从 Android 7.0（Nougat，2016 年）开始将 Ninja 作为主要构建后端。AOSP 的构建系统（Soong）先将 `Android.bp` 文件转换为 `.ninja` 文件，再由 Ninja 执行实际编译。完整 AOSP 构建涉及数十万条构建边，Ninja 对大规模构建图的高效处理是其被选中的核心原因。

### 直接编写 `.ninja` 文件

对于需要自定义构建流程的场景，也可以直接编写轻量的 `.ninja` 文件，适合嵌入式项目或脚本生成的构建系统。由于语法极简，一个 50 行以内的 `.ninja` 文件即可描述一个中等规模嵌入式项目的完整构建逻辑。

## 常见误区

**误区一：Ninja 可以替代 CMake**  
Ninja 只负责执行构建命令，它不会自动探测编译器路径、处理平台差异或管理依赖库版本。CMake 承担的是"生成 Ninja 文件"的角色，两者分工明确、不可互换。直接使用 Ninja 意味着必须手动或通过其他工具生成 `.ninja` 文件。

**误区二：Ninja 比 Make 功能更强大**  
Ninja 恰恰相反——它是刻意设计得比 Make 功能更少。Ninja 不支持条件判断、循环、函数定义等元编程特性，也不提供自动变量推导规则。这种"功能缺失"是设计选择，换来的是极低的解析开销和可预测的执行行为。

**误区三：`-j` 参数越大越好**  
在链接阶段，每个链接任务可能消耗 1–8 GB 内存（取决于项目规模）。盲目设置 `-j 32` 可能导致内存耗尽、系统 OOM。正确做法是使用 `pool` 机制单独限制链接任务的并发度，而对编译任务使用较高的并发数。

## 知识关联

学习 Ninja 之前需要掌握 CMake 的基本使用，特别是 CMake 生成器（Generator）的概念——CMake 支持生成 Makefile、Ninja、Visual Studio 工程等多种格式，理解这一层抽象有助于明白 Ninja 在整个构建流程中的位置。

Ninja 本身是构建执行层的终点，其上层工具包括 CMake、Meson、GN（Chromium 使用的元构建系统）等，它们都能以 Ninja 作为后端输出。若需要进一步提升大型项目的构建速度，可以在 Ninja 之上引入分布式编译工具（如 `distcc` 或 `icecc`）或编译缓存工具（如 `ccache`），这些工具与 Ninja 的 `rule` 中的 `command` 字段直接集成，替换编译器调用命令即可生效。
