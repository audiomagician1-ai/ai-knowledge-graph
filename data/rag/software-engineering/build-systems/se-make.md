---
id: "se-make"
concept: "Make/Makefile"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 2
is_milestone: false
tags: ["经典"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
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

# Make/Makefile

## 概述

Make 是1976年由 Stuart Feldman 在贝尔实验室开发的自动化构建工具，最初用于管理 C 语言程序的编译流程。其核心设计思想是通过比较文件的**修改时间戳**（mtime）来判断哪些目标需要重新构建，从而避免对未改动文件进行不必要的重新编译。这一设计至今仍是 Make 工作机制的基础。

Makefile 是 Make 工具读取的配置文件，用于描述目标（target）、依赖（prerequisite）和命令（recipe）之间的关系。一个典型的 C 项目中，Makefile 会明确声明 `.o` 目标文件依赖于哪个 `.c` 源文件和哪些 `.h` 头文件，Make 在每次构建前会遍历整个依赖图，仅重新编译那些依赖关系中有更新文件的目标。

Make 之所以在诞生近50年后仍被广泛使用，原因在于它语法简洁且无需额外安装——几乎所有 Linux/Unix 系统都预装了 GNU Make（版本通常为 4.x）。对于规模适中的 C/C++ 项目，一个手写的 Makefile 往往比 CMake 生成的构建文件更易于调试和理解。

---

## 核心原理

### 规则的三要素结构

Makefile 中每条规则的语法格式固定为：

```
目标: 依赖列表
<Tab>命令
```

注意**命令行必须以制表符（Tab）而非空格开头**，这是 Make 解析器的硬性要求，也是初学者最常犯的语法错误。目标通常是文件名，依赖列表是该目标所依赖的文件或其他目标的名称，命令则是 Shell 指令。例如：

```makefile
main.o: main.c utils.h
    gcc -c main.c -o main.o
```

当 `main.c` 或 `utils.h` 的修改时间晚于 `main.o` 时，Make 会执行 `gcc` 编译命令。

### 自动变量与模式规则

Make 提供了一组自动变量，专门用于在规则命令中引用目标和依赖，避免重复书写文件名：

| 变量 | 含义 |
|------|------|
| `$@` | 当前规则的目标文件名 |
| `$<` | 第一个依赖文件名 |
| `$^` | 所有依赖文件名（去重） |
| `$*` | 模式规则中 `%` 匹配的词干 |

结合**模式规则**（Pattern Rule），可以用一条规则覆盖所有 `.c` → `.o` 的编译步骤：

```makefile
%.o: %.c
    gcc -c $< -o $@
```

这条规则使用 `%` 作为通配符，匹配任意文件名词干，是减少 Makefile 冗余代码的标准做法。

### 伪目标（Phony Target）

当目标名称与实际文件名无关时，需要用 `.PHONY` 声明其为伪目标，防止 Make 将其与同名文件混淆：

```makefile
.PHONY: clean all

clean:
    rm -f *.o main
```

如果当前目录下存在名为 `clean` 的文件，且没有 `.PHONY` 声明，Make 会因为该文件"不需要更新"而跳过 `clean` 目标的命令执行。

### 变量与递归展开

Makefile 中有两种变量赋值方式：`=`（递归展开，Recursively Expanded）和 `:=`（立即展开，Simply Expanded）。递归展开变量在**每次使用时**重新求值，可能导致无限递归；立即展开变量在**赋值时**就确定值，性能更可预测：

```makefile
CC := gcc                    # 立即展开，推荐方式
CFLAGS := -Wall -O2
OBJS := main.o utils.o

app: $(OBJS)
    $(CC) $(CFLAGS) $^ -o $@
```

---

## 实际应用

**多模块 C 项目构建**：一个包含 `src/` 和 `include/` 目录的中型 C 项目中，Makefile 会通过 `VPATH` 变量或 `$(wildcard src/*.c)` 函数自动收集源文件列表，并用 `$(patsubst %.c,%.o,...)` 函数批量生成目标文件列表，从而实现全自动的增量编译。

**生成依赖文件**：通过 `gcc -MMD -MP` 选项让编译器自动生成 `.d` 后缀的依赖描述文件，再在 Makefile 中用 `-include $(DEPS)` 引入，可以精确追踪头文件变动，确保修改 `.h` 文件后相关 `.c` 文件都会被重新编译。这是专业 C/C++ 项目 Makefile 的标准实践。

**并行构建加速**：执行 `make -j4` 命令可以让 Make 同时运行最多4个独立的编译任务，对于多个互不依赖的 `.o` 文件，可以大幅缩短总编译时间。GNU Make 的并行调度基于依赖图的拓扑排序，能自动识别哪些任务可以并发执行。

---

## 常见误区

**误区一：Tab 与空格混用**  
许多代码编辑器默认将 Tab 自动转换为空格，导致 Makefile 中的命令行以空格而非 Tab 开头，Make 解析时会报错 `*** missing separator`。解决方法是在编辑器中为 `.mk` 和 `Makefile` 文件单独配置禁止 Tab 展开。

**误区二：认为修改头文件不需要重新编译**  
Make 只会检查 Makefile 中**显式声明**的依赖关系。如果规则中只写了 `main.o: main.c` 而遗漏了 `utils.h`，那么修改 `utils.h` 后 Make 不会重新编译 `main.o`，导致构建结果与源代码不一致。这正是前文提到的自动生成 `.d` 依赖文件方案所解决的问题。

**误区三：将 Make 与 CMake 的职责混淆**  
Make 直接执行构建命令，是**构建系统**（Build System）；CMake 生成 Makefile 或其他构建文件，是**构建系统生成器**（Build System Generator）。在 CMake 项目中，实际执行编译的仍然是 Make（或 Ninja），CMake 本身并不编译代码。

---

## 知识关联

**与构建系统概述的关联**：Make 是理解增量构建和依赖图这两个核心概念最直观的载体。构建系统概述中抽象描述的"仅重新构建过时目标"原则，在 Makefile 的时间戳比较机制中得到了最原始的具体实现。

**与 CMake 的关联**：CMake 的 `Makefile` 生成后端（通过 `cmake -G "Unix Makefiles"` 触发）会产生结构复杂的多层 Makefile，理解手写 Makefile 的规则语法有助于读懂 CMake 生成物并在必要时手动干预构建过程。

**通向 MSBuild 的路径**：MSBuild 是微软生态中功能与 Make 对应的构建引擎，同样基于目标（Target）和任务（Task）的依赖关系驱动构建。与 Makefile 的纯文本 Tab 缩进语法不同，MSBuild 使用 XML 格式的 `.proj` 文件，并引入了属性组（PropertyGroup）和条件表达式等更结构化的配置机制，是学习完 Make 后自然过渡到 Windows 平台构建工具的下一步。