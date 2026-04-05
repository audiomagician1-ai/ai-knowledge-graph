---
id: "platform-defines"
concept: "平台宏定义"
domain: "game-engine"
subdomain: "platform-abstraction"
subdomain_name: "平台抽象"
difficulty: 2
is_milestone: false
tags: ["编译"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 平台宏定义

## 概述

平台宏定义（Platform Macro Definition）是游戏引擎在编译阶段用于识别目标运行平台、操作系统及硬件能力的预处理器宏集合。通过在编译时（而非运行时）判断当前目标平台，引擎可以在同一套源代码中包含针对不同平台的专属实现，由编译器根据宏的值选择性地纳入或排除特定代码段。这一机制依赖C/C++预处理器的 `#ifdef`、`#if defined()`、`#elif`、`#endif` 指令构成的条件编译块来实现。

平台宏定义的系统性使用最早可追溯至1980年代Unix跨平台移植实践，但在游戏引擎领域真正规范化是在2000年代初主机平台（Console）迅速增多之后。虚幻引擎（Unreal Engine）在UE3时代（约2006年）开始引入其自有的标准化平台宏体系，如 `PLATFORM_WINDOWS`、`PLATFORM_PS4`、`PLATFORM_IOS` 等，彻底取代了依赖编译器内建宏（如 `_WIN32`、`__APPLE__`）的零散写法。Unity引擎则通过 `#if UNITY_STANDALONE_WIN`、`#if UNITY_ANDROID` 等脚本编译符号在C#层提供相同能力。

平台宏定义的意义在于将"哪个平台"的判断从运行期提前到编译期，消除运行时分支带来的性能开销，同时将不适用于某平台的代码彻底从该平台的二进制产物中排除，节省包体大小并避免引用不存在的系统API。

## 核心原理

### 编译器内建宏与引擎自定义宏的分层

最底层是编译器或工具链自动定义的内建宏，例如：MSVC编译器定义 `_WIN32`（32位和64位Windows均成立）和 `_WIN64`（仅64位），GCC/Clang在Android NDK下定义 `__ANDROID__`，Clang在iOS/macOS下定义 `__APPLE__` 并可进一步通过 `<TargetConditionals.h>` 中的 `TARGET_OS_IPHONE` 区分设备类型。引擎在这些内建宏之上构建自己的统一宏层，例如UE5的 `PLATFORM_WINDOWS` 宏在其内部定义为：

```cpp
#if defined(_WIN32) || defined(_WIN64)
  #define PLATFORM_WINDOWS 1
#else
  #define PLATFORM_WINDOWS 0
#endif
```

这样做的好处是引擎代码只需书写 `#if PLATFORM_WINDOWS`，不必关心底层编译器的差异。

### Feature Level宏与能力检测

除了"是哪个平台"之外，平台宏还负责描述该平台支持的图形API特性等级（Feature Level）。在UE5中，`PLATFORM_SUPPORTS_GEOMETRY_SHADERS`、`PLATFORM_SUPPORTS_TESSELLATION`、`PLATFORM_MAX_MOBILE_SHADOWMAP_CASCADES` 等宏描述特定平台的具体能力上限。以移动端为例，`RHI_FEATURE_LEVEL_ES3_1` 对应OpenGL ES 3.1或Metal特性集，而桌面端默认为 `RHI_FEATURE_LEVEL_SM5`（Shader Model 5）或更高。这些Feature Level宏允许渲染模块在编译期剔除移动设备无法执行的Shader路径。

### 条件编译的作用域规则

条件编译块的嵌套层次直接影响代码可维护性。一个典型的引擎平台分发模式如下：

```cpp
#if PLATFORM_WINDOWS
    // 调用 D3D12 API
#elif PLATFORM_PS5
    // 调用 GNM API
#elif PLATFORM_ANDROID
    // 调用 Vulkan / OpenGL ES API
#else
    #error "Unsupported platform"
#endif
```

值得注意的是，当宏被定义为 `0` 与"宏未定义"是两种不同状态：`#if PLATFORM_WINDOWS`（值为0时为假）与 `#ifdef PLATFORM_WINDOWS`（无论值为何都为真）的语义不同，UE引擎统一采用前者风格（所有平台宏均定义为0或1），避免 `#ifdef` 与 `#ifndef` 的混用歧义。

### 宏的传递方式：命令行与头文件

平台宏既可以通过编译器命令行参数 `-DPLATFORM_WINDOWS=1` 注入，也可以统一在引擎的平台头文件（如UE5的 `Platform.h` 或各平台专属的 `WindowsPlatform.h`）中集中定义。UE5的构建工具（UnrealBuildTool，UBT）在生成编译命令时自动注入当前目标平台对应的宏集合，开发者无需手动传参。

## 实际应用

**文件系统路径分隔符处理：** 在引擎文件管理模块中，`#if PLATFORM_WINDOWS` 块内使用反斜杠 `\` 作为路径分隔符，`#elif PLATFORM_UNIX || PLATFORM_MAC` 块内使用正斜杠 `/`，编译后每个平台的二进制只包含自身所需的分支，无任何运行时判断开销。

**线程模型差异：** PlayStation 5平台拥有7个可用CPU核心（其中1个为系统保留），UE5通过 `#if PLATFORM_PS5` 块内的 `PLATFORM_MAX_WORKER_THREADS_TO_SPAWN` 宏设定为6，而PC平台此宏值来自运行时CPU核心查询，两者在编译期就走入不同代码路径。

**Android ABI兼容：** NDK构建中通过 `#if defined(__arm__)` 与 `#if defined(__aarch64__)` 区分32位ARMv7与64位ARM64，分别选择对应的NEON SIMD内联汇编实现，保证在不支持64位的旧设备上也能编译通过。

**Nintendo Switch专属API：** Switch平台的NVN图形API头文件仅存在于任天堂授权SDK中，引擎通过 `#if PLATFORM_SWITCH` 将所有 `#include <nvn/nvn.h>` 包含指令保护起来，确保在非Switch平台的开发机上不会出现缺少头文件的编译错误。

## 常见误区

**误区一：把运行时平台检测与编译期宏混淆。**  
有些初学者会写出 `if (FPlatformProperties::IsConsole())` 来分支渲染路径，以为这与 `#if PLATFORM_PS5` 等价。实际上前者是运行时函数调用，两个分支的代码都会被编译进二进制；后者在编译期即排除无关代码，移动平台上被排除的PC渲染代码体积可达数十MB。在性能敏感路径（如渲染循环内）应优先使用编译期宏。

**误区二：认为 `__APPLE__` 宏等于iOS平台。**  
`__APPLE__` 在macOS、iOS、watchOS、tvOS下均为真。若直接用 `#ifdef __APPLE__` 保护仅适用于iOS的代码，在macOS平台编译时同样会触发，导致链接到不存在的iOS框架（如 `UIKit`）而失败。正确做法是结合 `TargetConditionals.h` 中的 `TARGET_OS_IPHONE` 宏，或使用引擎封装好的 `PLATFORM_IOS` 宏。

**误区三：将Feature Level宏当作运行时查询的替代品。**  
`PLATFORM_SUPPORTS_GEOMETRY_SHADERS` 表示"该平台的硬件规格理论上支持几何着色器"，但并不保证用户设备的驱动程序已正确实现该特性。Feature Level宏适合做编译期的代码裁剪，真正的硬件能力回退（Fallback）还需要结合运行时的 `RHISupportsGeometryShaders()` 函数进行双重检查。

## 知识关联

平台宏定义建立在**平台抽象概述**所描述的"一套代码，多平台运行"目标之上——平台抽象概述解释了为什么需要隔离平台差异，而平台宏定义是实现这一隔离的最基础编译期工具。理解平台宏定义后，学习者可以更顺畅地阅读任何主流引擎（UE、Unity、Godot）的跨平台底层代码，因为几乎所有平台分支逻辑都以 `#if PLATFORM_XXX` 的形式呈现。此外，平台宏定义与构建系统（如CMake的 `target_compile_definitions`、UBT的模块描述文件 `.Build.cs`）紧密协作：构建系统负责向编译器传递正确的宏值，平台宏定义负责在源码层消费这些值，两者共同构成游戏引擎跨平台编译管线的基石。