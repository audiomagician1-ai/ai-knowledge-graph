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
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 交叉编译

## 概述

交叉编译（Cross-Compilation）是指在一个平台（称为宿主机，Host）上编译出能够运行在另一个不同平台（称为目标机，Target）上的可执行代码的技术。例如，在 x86_64 的 Linux 工作站上编译生成能够在 ARM Cortex-A53 处理器上运行的二进制文件，这一过程中宿主机和目标机的指令集、操作系统或 ABI 至少有一项不同。

交叉编译起源于嵌入式系统开发。20世纪80年代，嵌入式设备计算资源极度受限，无法在目标设备上本地运行完整的编译器工具链，开发者只能借助功能更强大的工作站完成编译任务。GNU 工具链（gcc、binutils、glibc）在1990年代逐步完善了对多目标架构的支持，使得交叉编译工具链的构建从手工拼接转变为可系统化配置的流程。Crosstool-NG（2007年发布）进一步将交叉工具链的构建自动化。

在现代软件工程中，交叉编译被广泛应用于嵌入式 Linux 开发、Android NDK 构建、iOS 应用编译（Xcode 在 macOS 上生成 ARM64 二进制）以及 WebAssembly 目标编译等场景。没有交叉编译，工程师无法在资源受限的 IoT 设备上高效开发 C/C++ 代码，构建周期也将因在目标板上直接编译而延长数十倍。

---

## 核心原理

### 三元组：目标平台的唯一标识

交叉编译工具链通过**目标三元组（Target Triplet）**来精确描述目标平台，格式为 `<arch>-<vendor>-<os>` 或 `<arch>-<vendor>-<kernel>-<abi>`。常见示例：

- `arm-linux-gnueabihf`：ARMv7 硬浮点 ABI、Linux 内核、GNU C 库
- `aarch64-linux-gnu`：ARM 64位、Linux、GNU ABI
- `riscv64-unknown-elf`：RISC-V 64位裸机目标

在 CMake 中，通过 Toolchain 文件指定三元组：

```cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER   aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
```

三元组的 ABI 字段（如 `gnueabihf` 中的 `hf` 代表硬件浮点）决定了浮点运算是通过 FPU 寄存器还是软件模拟完成，混用不同 ABI 编译的库将导致链接失败。

### Sysroot：隔离目标平台的库与头文件

Sysroot 是一个模拟目标系统文件系统根目录的本地目录，包含目标平台的 C/C++ 头文件、共享库（`.so`）和静态库（`.a`）。编译器选项 `--sysroot=/path/to/sysroot` 告诉工具链在该目录下而非宿主机的 `/usr/include` 和 `/usr/lib` 中查找依赖。

典型 sysroot 结构：
```
/sysroot/
  usr/include/   ← 目标平台头文件
  usr/lib/       ← 目标平台共享库 (.so)
  lib/           ← 动态链接器 (ld-linux-aarch64.so.1)
```

在 CMake Toolchain 文件中设置：
```cmake
set(CMAKE_SYSROOT /opt/sysroot-aarch64)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

`FIND_ROOT_PATH_MODE` 的 `ONLY` 设置防止 CMake 的 `find_package()` 错误地找到宿主机版本的库，这是交叉编译配置中最常见的错误来源之一。

### 工具链的五个组成工具

一套完整的 GNU 交叉工具链包含以下五类工具，均以目标三元组为前缀命名：

| 工具 | 示例（AArch64） | 职责 |
|------|----------------|------|
| 编译器 | `aarch64-linux-gnu-gcc` | 将 C/C++ 源码编译为目标机器码 |
| 汇编器 | `aarch64-linux-gnu-as` | 将汇编代码转为目标 `.o` 文件 |
| 链接器 | `aarch64-linux-gnu-ld` | 将 `.o` 文件链接为可执行文件 |
| 归档工具 | `aarch64-linux-gnu-ar` | 打包静态库 `.a` |
| 调试器 | `aarch64-linux-gnu-gdb` + GDB Server | 远程调试目标板 |

---

## 实际应用

### Android NDK 交叉编译

Android NDK 内置了完整的交叉工具链，支持 `armeabi-v7a`、`arm64-v8a`、`x86`、`x86_64` 四种 ABI。CMake 通过以下命令激活 NDK 工具链：

```bash
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=android-21
```

`ANDROID_PLATFORM=android-21` 指定最低 API 级别为 Android 5.0，NDK 会自动选择对应的 sysroot。

### 嵌入式 Linux（Buildroot/Yocto）

Buildroot 在配置时通过 `BR2_TOOLCHAIN_EXTERNAL_PATH` 指定外部交叉工具链路径，并自动为所有软件包生成对应的 CMake Toolchain 文件，输出路径在 `output/host/usr/share/buildroot/toolchainfile.cmake`。Yocto 则通过 SDK 导出机制，将 `environment-setup-aarch64-poky-linux` 脚本内的环境变量（如 `CC=aarch64-poky-linux-gcc`）与 CMake 集成。

### WebAssembly 目标编译

Emscripten 工具链将 C/C++ 交叉编译为 WebAssembly 字节码，其宿主机可以是任何桌面操作系统，目标是浏览器或 Node.js 环境。CMake 通过 `emcmake cmake ..` 自动加载 Emscripten 的 Toolchain 文件，输出 `.wasm` 和 `.js` 胶水代码。

---

## 常见误区

**误区一：宿主机安装了相同版本的库就不需要 sysroot**
许多初学者认为，如果宿主机（x86_64 Ubuntu）和目标机（aarch64 Debian）的 libssl 版本相同，就可以直接链接宿主机的库。这是错误的：宿主机的 `.so` 文件是 x86_64 ELF 格式，链接器会直接报错 `skipping incompatible /usr/lib/x86_64-linux-gnu/libssl.so when searching for -lssl`。必须提供目标架构的 AArch64 版本 `.so`。

**误区二：`CMAKE_CROSSCOMPILING` 变量需要手动设置为 `ON`**
CMake 会在检测到 `CMAKE_SYSTEM_NAME` 与当前宿主系统不同时自动将 `CMAKE_CROSSCOMPILING` 设置为 `TRUE`，无需手动干预。若强行设置该变量而不提供正确的 `CMAKE_SYSTEM_PROCESSOR` 和编译器路径，`try_compile()` 检测依赖时会产生误判，错误地认为某些功能不可用。

**误区三：交叉编译生成的工具可以直接在构建步骤中调用**
部分 CMake 项目在构建过程中需要先编译一个"代码生成器"可执行文件，再用其生成 C 代码（如 Protobuf 的 `protoc`）。若此可执行文件也被交叉编译为目标架构，则宿主机无法直接执行。正确做法是通过 `CMAKE_CROSSCOMPILING_EMULATOR`（如 QEMU user-mode）或单独为宿主机编译该工具，并用 `IMPORTED` target 导入。

---

## 知识关联

**与 CMake Toolchain 文件的关系**：CMake 的交叉编译支持完全依赖 Toolchain 文件（`-DCMAKE_TOOLCHAIN_FILE=...`）这一机制，该文件在 CMake 初始化的最早阶段被加载，早于 `project()` 命令，因此它是唯一能可靠设置编译器三元组和 sysroot 的位置。

**与 pkg-config 的协调**：交叉编译环境中 `pkg-config` 默认查询宿主机的 `.pc` 文件，需通过 `PKG_CONFIG_SYSROOT_DIR` 和 `PKG_CONFIG_PATH` 环境变量重定向到目标 sysroot 下的 `lib/pkgconfig` 目录，CMake 的 `FindPkgConfig` 模块在 `CMAKE_SYSROOT` 已设置时会自动处理这一重定向（CMake 3.6+ 版本）。

**与容器化构建的结合**：Docker 镜像（如 `dockcross/linux-aarch64`）将交叉工具链、sysroot 和构建脚本打包，使得交叉编译环境可复现。执行 `docker run --rm dockcross/linux-aarch64 > ./dockcross && chmod +x ./dockcross && ./dockcross cmake ..` 可无需本地安装工具链完成 AArch64 目标的构建。
