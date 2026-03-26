---
id: "se-precompiled-header"
concept: "预编译头"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 2
is_milestone: false
tags: ["C++"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 预编译头

## 概述

预编译头（Precompiled Header，简称 PCH）是一种编译器优化技术，将频繁被多个翻译单元包含的头文件（通常是标准库头文件或第三方库头文件）预先编译为二进制中间格式，后续编译时直接加载该二进制文件而无需重新解析原始头文件文本。MSVC 编译器将 PCH 文件扩展名定为 `.pch`，GCC/Clang 则使用 `.gch` 或 `.pchi`，不同编译器的 PCH 格式互不兼容。

PCH 技术最早由微软在 Visual C++ 编译器中大规模推广，其背景是 Windows 头文件 `windows.h` 展开后超过 20 万行代码，每个翻译单元都重复解析这些代码极其低效。Clang 在 2007 年发布时也引入了 PCH 支持，并在此基础上发展出了模块（Modules）系统。在大型 C++ 项目中，使用 PCH 可以将构建时间缩短 30%–70%，这一数字来自 Mozilla、LLVM 等开源项目的实测报告。

PCH 之所以重要，是因为 C++ 的 `#include` 机制本质上是文本替换，编译器每次编译 `.cpp` 文件都必须从头解析所有包含的头文件。对于包含 `<vector>`、`<string>`、`<algorithm>` 等标准库头文件的项目，单个翻译单元的头文件解析开销可能占总编译时间的 50% 以上。

## 核心原理

### 二进制缓存机制

编译器在生成 PCH 时，将头文件内容解析为抽象语法树（AST）并序列化到磁盘。以 Clang 为例，PCH 文件存储的是 Clang 内部的序列化 AST 格式，加载时直接反序列化到内存，跳过词法分析和语法分析阶段。GCC 的 PCH 机制略有不同，它存储的是编译器内部的符号表快照。关键约束是：生成 PCH 时使用的编译器标志（`-std=c++17`、`-O2` 等）必须与使用 PCH 时完全一致，否则编译器拒绝加载该 PCH 文件。

### CMake 中的 PCH 配置

CMake 从 3.16 版本开始内置 PCH 支持，使用 `target_precompile_headers()` 命令：

```cmake
target_precompile_headers(my_target
    PRIVATE
        <vector>
        <string>
        <unordered_map>
        "my_project_common.h"
)
```

CMake 会自动处理 PCH 文件的生成和复用。使用 `REUSE_FROM` 参数可以让多个目标共享同一份 PCH，避免重复生成：

```cmake
target_precompile_headers(target_b REUSE_FROM target_a)
```

注意 `REUSE_FROM` 要求两个目标使用完全相同的编译选项，否则 CMake 3.16+ 会在配置阶段报错。

### Unity Build 与 PCH 的关系

Unity Build（统一构建）是另一种构建加速技术，将多个 `.cpp` 文件合并为一个大翻译单元，通过减少翻译单元数量来减少头文件解析次数。CMake 通过 `set_target_properties(my_target PROPERTIES UNITY_BUILD ON)` 启用此功能。PCH 和 Unity Build 可以同时使用，但两者的优化方向不同：PCH 减少每个翻译单元的头文件解析时间，Unity Build 减少翻译单元总数和链接器的符号处理量。在实践中，Unity Build 的副作用更多（如命名空间污染、宏冲突），而 PCH 的侵入性较小。

### C++20 模块与 PCH 的演进

C++20 引入的模块接口单元（Module Interface Unit，`.ixx` 或 `.cppm` 文件）是 PCH 的语义层面替代方案。模块使用 `export module my_module;` 声明，编译后生成二进制模块接口（BMI），概念上类似 PCH 但具有显式的依赖边界和符号可见性控制。CMake 3.28 正式支持 C++20 模块的自动依赖扫描。当前（2024 年）工具链支持尚不统一，PCH 仍是最稳定的跨编译器构建加速方案。

## 实际应用

**Qt 项目加速构建**：Qt 框架的头文件（如 `<QWidget>`、`<QApplication>`）展开后代码量巨大。在 CMake 管理的 Qt 项目中，将常用 Qt 头文件放入 PCH，可以将增量构建时间从数分钟降至几十秒。典型配置是创建 `pch.h` 文件包含所有 Qt 公共头文件，再通过 `target_precompile_headers` 注册。

**游戏引擎 Unreal Engine**：Unreal Engine 要求每个模块必须有名为 `[ModuleName].h` 的 PCH 头文件，构建系统 UnrealBuildTool 自动为每个模块生成对应的 PCH。这是目前工业界最大规模的 PCH 强制使用案例，Unreal 的构建系统甚至不允许关闭 PCH，因为禁用后全量构建时间会从约 40 分钟增加到 2 小时以上。

**调试信息与 PCH 冲突**：在启用 `/Zi`（MSVC 调试信息）时，PCH 文件会包含调试符号，导致 `.pch` 文件体积从几十 MB 膨胀到几百 MB。解决方案是改用 `/Z7` 将调试信息内嵌到 `.obj` 文件而非单独的 `.pdb`，或使用 CMake 的 `CMAKE_MSVC_DEBUG_INFORMATION_FORMAT` 变量控制调试格式。

## 常见误区

**误区一：PCH 中放的头文件越多越好**。PCH 文件中包含的头文件必须是稳定的（即不会频繁修改的），因为 PCH 中任何一个头文件发生变化都会导致整个 PCH 失效，触发所有使用该 PCH 的翻译单元重新编译。将自己项目中频繁修改的头文件放入 PCH，反而会导致增量构建比不使用 PCH 时更慢。正确做法是只将第三方库和标准库头文件放入 PCH。

**误区二：PCH 可以跨不同编译标志的目标共享**。开发者有时尝试让 Debug 和 Release 两个构建类型共享同一个 PCH 文件。这是不可行的，因为 PCH 文件在生成时已经将 `-DNDEBUG`、`-O2` 等编译选项编码进去，加载时编译器会校验这些选项是否匹配。CMake 的 `REUSE_FROM` 机制会在构建时自动检测这种不一致并报错，而手动管理 PCH 路径时则会出现难以排查的编译错误。

**误区三：PCH 与 `#pragma once` 或 `#ifndef` 守卫功能重叠**。Include guard 防止单个翻译单元内的重复包含，PCH 解决的是跨翻译单元的重复解析问题，两者在不同层面工作，缺一不可。即使头文件有 `#pragma once`，在没有 PCH 的情况下，10 个 `.cpp` 文件仍然会各自独立解析该头文件一次。

## 知识关联

学习预编译头需要先理解 CMake 的目标（target）模型，特别是 `target_compile_options` 和 `target_include_directories` 的传播机制，因为 PCH 的生效依赖于编译选项与 PCH 生成时一致。`target_precompile_headers` 的 `PRIVATE/PUBLIC/INTERFACE` 修饰符与 CMake 其他 target 命令的语义完全相同，PUBLIC 会将 PCH 传播给链接到该目标的其他目标。

预编译头与 C++20 模块系统（Modules）存在技术上的继承关系：MSVC 的 Header Units 功能（`/exportHeader` 标志）实质上是将传统头文件以模块接口单元的方式编译，是 PCH 向 C++20 模块过渡的桥梁技术。理解 PCH 的二进制缓存原理，有助于后续理解模块 BMI 文件的生成和依赖扫描机制。