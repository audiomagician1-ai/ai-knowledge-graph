---
id: "se-cmake"
concept: "CMake"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 2
is_milestone: true
tags: ["C++"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.375
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# CMake

## 概述

CMake 是由 Kitware 公司开发的跨平台构建系统生成器（Build System Generator），首个正式版本发布于 2000 年，用于解决 ITK（Insight Toolkit）医学图像处理项目在多平台编译上的困难。CMake 本身不直接编译代码，而是读取用户编写的 `CMakeLists.txt` 配置文件，生成对应平台的原生构建系统文件（如 Makefile、Visual Studio `.sln`、Ninja `build.ninja`），再由这些构建系统完成实际编译链接。

CMake 的设计理念围绕"描述构建意图而非构建步骤"展开。开发者用 CMake 语言声明一个可执行程序需要哪些源文件、依赖哪些库、适用哪些编译选项，而不必为 Linux、Windows、macOS 各写一套 Makefile 或项目文件。这一层抽象使得 CMake 成为 C/C++ 生态中实际占据主导地位的构建配置工具，LLVM、OpenCV、Qt 6 等重量级项目均以 CMake 作为官方构建系统。

CMake 3.0（2014 年发布）引入了"Modern CMake"风格，以 **Target（目标）** 为中心组织构建信息，取代了早期基于全局变量的写法。理解这一版本节点是区分现代 CMake 和过时用法的关键分界线。

---

## 核心原理

### CMakeLists.txt 文件结构

每个 CMake 项目的根目录必须包含一个 `CMakeLists.txt`，子目录可通过 `add_subdirectory()` 命令引入各自的 `CMakeLists.txt`，形成树状结构。一个最小可用的配置如下：

```cmake
cmake_minimum_required(VERSION 3.20)
project(MyApp VERSION 1.0 LANGUAGES CXX)

add_executable(my_app main.cpp utils.cpp)
target_compile_features(my_app PRIVATE cxx_std_17)
```

`cmake_minimum_required` 必须是文件的第一条有效命令，它锁定 CMake 的行为策略（Policy）版本，防止新版 CMake 改变语义导致构建失败。`project()` 命令设置项目名称并定义 `PROJECT_SOURCE_DIR`、`PROJECT_BINARY_DIR` 等内置变量。

### Target（目标）与属性传播

Target 是 Modern CMake 的核心抽象单元，代表一个编译产物——可执行文件（`add_executable`）、静态库或动态库（`add_library`）、或纯接口库（`INTERFACE` 类型）。每个 Target 携带三类属性，通过关键字控制传播范围：

| 关键字 | 含义 |
|---|---|
| `PRIVATE` | 仅对本 Target 生效 |
| `PUBLIC` | 对本 Target 及所有链接它的 Target 生效 |
| `INTERFACE` | 仅对链接本 Target 的其他 Target 生效，本身不使用 |

例如，一个头文件库（Header-only library）应使用 `INTERFACE` 传播包含路径：

```cmake
add_library(my_header_lib INTERFACE)
target_include_directories(my_header_lib INTERFACE include/)
```

当另一个 Target 执行 `target_link_libraries(app PRIVATE my_header_lib)` 时，`include/` 路径会自动传递给 `app`，无需手动重复设置。这种传播机制消除了手动管理头文件路径的大量重复代码。

### Generator（生成器）

CMake 在配置阶段（`cmake -S . -B build`）必须指定一个 Generator，决定生成哪种构建系统文件。常用 Generator 包括：

- `Unix Makefiles`：生成标准 `Makefile`，Linux 默认
- `Ninja`：生成 `build.ninja`，构建速度快，推荐搭配
- `Visual Studio 17 2022`：生成 `.sln` 和 `.vcxproj` 文件
- `Xcode`：生成 macOS 的 Xcode 项目

指定方式为 `cmake -G "Ninja" -S . -B build`。Generator 一旦选定，同一 build 目录不可更改，必须清空 build 目录重新配置。CMake 3.15 引入了 `cmake --build build` 统一构建命令，屏蔽了不同 Generator 之间的调用差异（`make` vs `ninja` vs `msbuild`）。

### 构建类型与缓存变量

`CMAKE_BUILD_TYPE` 变量控制优化与调试信息，标准取值为 `Debug`、`Release`、`RelWithDebInfo`（带调试信息的 Release）、`MinSizeRel`。设置方式：

```bash
cmake -DCMAKE_BUILD_TYPE=Release -S . -B build
```

CMake 变量分为普通变量和缓存变量（Cache Variable）。缓存变量存储在 `build/CMakeCache.txt` 中，跨次配置持久化，可通过 `cmake-gui` 或 `ccmake` 可视化编辑。`option()` 命令是定义布尔型缓存变量的便捷写法，常用于控制功能开关：`option(BUILD_TESTS "Build unit tests" ON)`。

---

## 实际应用

**查找并链接第三方库：** CMake 提供 `find_package()` 命令搜索已安装的库。以 OpenSSL 为例：

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(my_app PRIVATE OpenSSL::SSL OpenSSL::Crypto)
```

`OpenSSL::SSL` 这种 `命名空间::组件` 格式是 Modern CMake 的 Imported Target，其中已内置了头文件路径和链接选项，不再需要手动写 `include_directories`。

**与 Conan/vcpkg 集成：** 当使用 Conan 2.x 时，执行 `conan install` 后会生成 `conan_toolchain.cmake`，通过 `cmake -DCMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake` 传入，CMake 的 `find_package()` 便能自动找到 Conan 管理的依赖包。vcpkg 同样通过 toolchain 文件集成，路径通常为 `vcpkg/scripts/buildsystems/vcpkg.cmake`。

**安装规则：** `install()` 命令定义 `cmake --install build` 时的文件拷贝规则，是制作可分发包的标准方式，与 CPack 配合可生成 `.deb`、`.rpm`、NSIS 安装包。

---

## 常见误区

**误区一：在 target 命令出现前使用全局命令设置编译选项。** 许多旧教程使用 `include_directories()`、`add_definitions()`、`link_libraries()` 等全局命令，这些命令对当前目录下所有 Target 生效，极易污染不相关的 Target。正确做法是始终使用 `target_include_directories()`、`target_compile_definitions()`、`target_link_libraries()`，并明确指定 `PRIVATE/PUBLIC/INTERFACE`。

**误区二：混淆"源码目录"与"构建目录"，在源码目录内执行 cmake。** 在源码目录直接运行 `cmake .`（in-source build）会将 `CMakeCache.txt`、生成的 Makefile 等大量文件散落在源码目录中，污染版本控制。标准实践是始终使用 `cmake -S . -B build` 进行 out-of-source 构建。

**误区三：误以为修改 CMakeLists.txt 后需要手动重新运行 cmake。** CMake 会自动检测 `CMakeLists.txt` 的修改时间，当构建系统（如 ninja）执行时若检测到配置文件变更，会自动重新触发 CMake 的配置步骤，无需手动干预。但新增源文件到 `file(GLOB ...)` 采集到的变量中，CMake 无法感知，这也是官方不推荐 `GLOB` 的原因。

---

## 知识关联

**前置概念：** 理解"构建系统概述"中编译、链接两阶段的区分，有助于理解为何 CMake 要将 `target_compile_options` 和 `target_link_options` 分开设置。Conan/vcpkg 的 toolchain 文件机制在学习 CMake 的 `CMAKE_TOOLCHAIN_FILE` 变量时会直接复用。

**后续概念：** CMake 生成的 `build.ninja` 文件是学习 Ninja 构建系统的最佳真实样本——通过观察 `cmake -G Ninja` 后生成的文件，可以具体看到编译规则（rule）和目标（build）节点的组织方式。交叉编译在 CMake 中依赖 toolchain 文件设置 `CMAKE_SYSTEM_NAME`、`CMAKE_C_COMPILER` 等变量，是对 CMake Generator 和 Target 概念的综合运用。预编译头（PCH）在 CMake 3.16 中通过 `target_precompile_headers()` 命令原生支持，直接作用于 Target 对象。
