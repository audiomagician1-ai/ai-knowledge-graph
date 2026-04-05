---
id: "se-cross-compile"
concept: "交叉编译"
domain: "software-engineering"
subdomain: "build-systems"
subdomain_name: "构建系统"
difficulty: 3
is_milestone: false
tags: ["平台"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 交叉编译

## 概述

交叉编译（Cross-Compilation）是指在一种计算机架构（宿主机，Host）上生成另一种计算机架构（目标机，Target）可执行代码的编译过程。例如，在 x86_64 的 Linux 工作站上生成 ARM Cortex-A53 的嵌入式 Linux 二进制文件，或在 Windows 上为 Nintendo Switch 的 ARM64 平台编译游戏代码。宿主机与目标机的指令集架构（ISA）、操作系统或ABI（应用二进制接口）的任意一项不同，都构成交叉编译场景。

交叉编译的需求最早来自嵌入式系统开发。1987年前后，GNU工具链（GCC）开始支持通过 `--target` 参数指定目标三元组（Target Triple），形如 `arm-linux-gnueabihf`，其中依次描述架构、操作系统和ABI。这一命名规范至今仍是交叉编译工具链配置的基础语言。在游戏引擎（如Unreal Engine）和跨平台SDK开发中，交叉编译使开发者无需为每个目标平台单独维护一台构建机，大幅压缩了CI/CD流水线的硬件成本。

交叉编译之所以复杂，根本原因在于编译过程中存在两套截然不同的系统环境：宿主机提供执行编译器本身所需的工具，而目标机的头文件、系统库（sysroot）和链接器脚本必须与目标硬件严格匹配。若两套环境混用，会导致 ABI 不兼容或链接时出现 `undefined reference` 错误。

---

## 核心原理

### 目标三元组与工具链命名

GNU 工具链使用三元组 `<arch>-<vendor>-<system>` 来唯一标识一个目标平台，例如 `aarch64-none-linux-gnu` 表示无特定厂商、运行 GNU/Linux 的 64 位 ARM 架构。LLVM/Clang 则扩展为四元组，加入了环境字段（environment field），如 `armv7-linux-gnueabihf`。交叉编译工具链中的每个工具都以该前缀命名：`aarch64-linux-gnu-gcc`、`aarch64-linux-gnu-ld`、`aarch64-linux-gnu-objdump`，以便构建系统在多工具链共存时精确定位正确的二进制工具。

### Sysroot：目标平台的文件系统镜像

Sysroot 是交叉编译的核心概念，它是目标平台根文件系统的一个子集，至少包含：
- `/usr/include`：目标平台的系统头文件（如 `sys/types.h`、`linux/ioctl.h`）
- `/usr/lib`：目标平台的共享库存根（`.so`）和静态库（`.a`）
- `/lib`：目标平台的动态链接器（`ld-linux-aarch64.so.1`）

在 GCC 中，通过 `--sysroot=/path/to/sysroot` 参数指定，Clang 对应参数相同。若 sysroot 版本与目标设备的实际运行库版本不一致（例如 sysroot 使用 glibc 2.17，而设备使用 glibc 2.31），运行时将出现符号版本不匹配错误。

### CMake 中的工具链文件（Toolchain File）

CMake 通过专用的工具链文件（`-DCMAKE_TOOLCHAIN_FILE=arm.cmake`）将交叉编译配置与项目逻辑分离。一个典型的工具链文件需要声明以下关键变量：

```cmake
set(CMAKE_SYSTEM_NAME Linux)              # 目标OS
set(CMAKE_SYSTEM_PROCESSOR aarch64)       # 目标架构
set(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_SYSROOT /opt/sysroots/aarch64-linux-gnu)
# 防止 CMake 在宿主机路径中搜索库
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

`CMAKE_FIND_ROOT_PATH_MODE_*` 系列变量设为 `ONLY` 是防止"头文件污染"的关键——若设为 `BOTH`，CMake 可能错误地链接到宿主机的 x86_64 `.so` 文件，造成链接通过但目标机运行崩溃。

### Unreal Build Tool 中的交叉编译

Unreal Engine 4.14 起官方提供了针对 Linux ARM 的交叉编译工具链（`v15_clang-8.0.1-centos7`），通过设置环境变量 `LINUX_MULTIARCH_ROOT` 指向工具链安装目录，UBT 会自动选择对应的 Clang 前端和目标平台的 sysroot。UBT 在 `Linux.Automation.cs` 文件中硬编码了支持的目标三元组列表，开发者若需新增自定义 ARM 变体，必须修改此文件并重新编译 UBT 本身。

---

## 实际应用

**嵌入式 Linux 固件开发**：在 Ubuntu 20.04 宿主机上，安装 `gcc-aarch64-linux-gnu` 软件包后，配合 Buildroot 或 Yocto 生成的 sysroot，可以为 Raspberry Pi 4（BCM2711，Cortex-A72）完整构建内核模块和用户态应用程序，整个过程无需任何 ARM 硬件参与。

**游戏主机开发**：PlayStation 和 Xbox 平台的 SDK 本质上是特定版本的交叉编译工具链加专有 sysroot 的打包形式。开发者在 Windows 上通过 Visual Studio 集成的交叉编译工具链为主机 CPU（如 PS5 的 Zen 2 变体）生成目标代码，链接时使用主机专属的 `.lib` 存根文件。

**Android NDK**：Android NDK r21 开始完全转为基于 Clang 的工具链，目标三元组为 `aarch64-linux-android21`（其中 `21` 是 API Level）。NDK 的 CMake 集成通过 `android.toolchain.cmake` 文件实现，其核心逻辑就是设置 `CMAKE_ANDROID_ARCH_ABI`、`CMAKE_ANDROID_NDK` 等变量来驱动上述标准交叉编译流程。

---

## 常见误区

**误区一：混淆"运行编译器的机器"与"运行编译结果的机器"**
初学者常将宿主机的头文件路径直接传递给交叉编译器。例如，在 x86_64 Ubuntu 上将 `-I/usr/include` 添加到交叉编译命令中，这会引入宿主机的 `stddef.h` 等文件，其中的类型定义（如 `size_t` 的大小）可能与目标平台不符，导致编译通过但运行时出现对齐错误或数据截断。

**误区二：认为静态链接可以绕过 sysroot 问题**
全静态编译（`-static`）确实可以避免运行时的 `.so` 缺失问题，但编译期仍需要目标平台的 `libc.a` 和相关头文件。此外，glibc 的静态链接存在已知的 DNS 解析和 `dlopen` 限制；在某些目标平台上，更适合使用 musl libc 的静态工具链（如 `aarch64-linux-musl-gcc`）来实现真正的自包含二进制。

**误区三：工具链版本可以随意替换**
一个针对 glibc 2.17 编译的二进制文件可以在 glibc 2.31 的目标机上运行（因为 glibc 保持向后兼容），但反过来则不行：用 glibc 2.31 的 sysroot 编译出的二进制在 glibc 2.17 的设备上会因符号版本（如 `GLIBC_2.25`）缺失而无法启动。这意味着交叉编译工具链应当**匹配目标设备上最低的 glibc 版本**，而不是最新版本。

---

## 知识关联

交叉编译以 CMake 的工具链文件机制为基础配置接口，没有对 `CMAKE_SYSTEM_NAME`、`CMAKE_SYSROOT` 等变量的理解，工具链配置将无从下手。对于 Unreal Engine 项目，Unreal Build Tool 负责将 UE 特有的构建逻辑（模块依赖、PCH策略）翻译为实际的编译器调用，交叉编译配置需要在 UBT 的平台抽象层之上进行，而非直接修改编译器命令。

在掌握交叉编译之后，**链接优化**（Link-Time Optimization，LTO）是自然的进阶方向。LTO 在交叉编译场景下有额外限制：必须确保 LTO 插件（如 LLVM 的 `LLVMgold.so`）本身是宿主机可执行的，同时其优化目标必须针对 Target 架构的指令集生成代码，因此 LTO 工具链的版本必须与交叉编译器版本严格一致，这在工具链管理层面比单平台 LTO 复杂得多。