# Unreal Build Tool（UBT）

## 概述

Unreal Build Tool（简称 UBT）是 Epic Games 自 Unreal Engine 4 时代起以 C# 编写的专属构建系统，在 UE5 中以 .NET 6 运行时执行，可执行文件位于 `Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll`。UBT 不依赖 Visual Studio 的 MSBuild 体系或传统 Makefile，而是直接接管编译器调用、模块依赖图解析、跨平台工具链抽象、预编译头（PCH）策略以及 Unity Build 合并等全部构建决策。官方文档（Epic Games, 2023, *Unreal Build System Overview*）明确指出，UBT 支持的目标平台超过 20 个，包括 Windows（MSVC/Clang-cl）、macOS/iOS（Apple Clang）、Linux（GCC/Clang）、PlayStation 5、Xbox Series X/S 以及 Nintendo Switch，单一工具能够在不修改任何构建逻辑的前提下跨平台生成正确的编译命令。

UBT 必须与 **Unreal Header Tool（UHT）** 协同才能完成完整的构建流程。UHT 在编译器介入之前扫描所有带有 `UCLASS()`、`UPROPERTY()`、`UFUNCTION()` 等宏的头文件，生成 `.generated.h` 和 `.gen.cpp` 反射代码；UBT 随后将这些生成文件注入编译图，确保反射数据在链接阶段就位。若跳过 UHT 步骤而直接调用编译器，将因缺少 `StaticClass()` 等自动生成符号而产生链接错误。UE5.3 引入的 **Unreal Header Tool v2**（代号 ZenGen）基于 Verse 工具链重构了 UHT 的解析器，解析速度提升约 40%，并对 `USTRUCT` 的嵌套模板有了更精确的支持（Epic Games, 2023, *UE5.3 Release Notes*）。

理解 UBT 的架构对于任何需要自定义编译策略、优化增量编译时间或向引擎贡献插件的开发者都不可或缺。本文从模块系统、目标描述、构建流程、UHT 联动、编译优化五个维度进行系统阐述。

---

## 核心原理

### 模块系统（Module System）

UBT 的基本组织单元是**模块（Module）**，每个模块对应源代码目录中唯一一个以 `.Build.cs` 为后缀的 C# 文件。模块类必须继承自 `ModuleRules`，并在构造函数中通过 `ReadOnlyTargetRules Target` 参数获取目标平台、配置等上下文信息。典型的模块定义如下：

```csharp
public class MyGame : ModuleRules {
    public MyGame(ReadOnlyTargetRules Target) : base(Target) {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(
            new string[] { "Core", "CoreUObject", "Engine", "InputCore" });
        PrivateDependencyModuleNames.AddRange(
            new string[] { "Slate", "SlateCore", "RenderCore" });
        PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));
    }
}
```

`PublicDependencyModuleNames` 与 `PrivateDependencyModuleNames` 的本质区别在于**依赖传播方向**：前者的头文件 include 路径和链接符号会向上传递给所有依赖本模块的模块（即传递性公开），后者仅在本模块的 `.cpp` 文件内可见。若将 `Slate` 错误地放入 `PublicDependencyModuleNames`，会导致所有上游模块都被迫引入 Slate 头文件目录，造成不必要的编译依赖扩散，增量编译时间显著变长。

UBT 将模块分为多种类型，通过 `Type` 属性指定：
- `Runtime`：打包到最终二进制，随游戏发布；
- `Editor`：仅在编辑器模式下编译，`-Game` 构建时剔除；
- `DeveloperTool`：开发工具，不进入 Shipping 配置；
- `ThirdParty`：预编译第三方库，UBT 仅处理其头文件和链接库路径。

### 目标描述文件（Target Rules）

与模块描述平级的另一核心概念是**目标（Target）**，对应 `.Target.cs` 文件。目标描述决定了最终生成的可执行文件或动态库的类型、入口模块列表以及全局编译开关。UE5 标准项目通常包含两个目标文件：`MyGame.Target.cs`（游戏目标）和 `MyGameEditor.Target.cs`（编辑器目标）。

```csharp
public class MyGameTarget : TargetRules {
    public MyGameTarget(TargetInfo Target) : base(Target) {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V2;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_3;
        ExtraModuleNames.Add("MyGame");
    }
}
```

`TargetType` 枚举包含 `Game`、`Editor`、`Client`、`Server`、`Program` 五种类型，UBT 依据此值决定是否链接编辑器子系统、是否剥离服务端逻辑等。`DefaultBuildSettings = BuildSettingsVersion.V2` 是 UE5 引入的重要变更，它将 PCH 策略从旧版的隐式共享改为强制显式，强制每个模块声明自己的 PCH 源文件，从而避免跨模块的头文件污染。

### 依赖图解析与链接顺序

UBT 在读取全部 `.Build.cs` 文件后，会构建一个**有向无环图（DAG）**表示模块间的依赖关系。设模块集合为 $V$，依赖关系为有向边集合 $E$，则 UBT 对 DAG 执行拓扑排序：

$$
\text{链接顺序} = \text{TopologicalSort}(G(V, E))
$$

若图中存在环形依赖（循环依赖），UBT 会在解析阶段抛出 `CircularDependencyException` 并中止构建，错误信息会打印出完整的依赖环路径，例如 `ModuleA -> ModuleB -> ModuleC -> ModuleA`。这与 CMake 的隐式循环依赖不同——CMake 在某些配置下会静默忽略循环依赖，产生难以排查的链接错误；UBT 的提前检测机制使问题更容易定位。

---

## 关键方法与构建流程

### UBT 完整构建流程

一次完整的 `Development Editor` 构建按以下顺序执行：

1. **命令行解析**：UBT 接收目标名称、平台、配置等参数，例如 `UnrealBuildTool MyGameEditor Win64 Development`；
2. **`.Build.cs` 加载**：UBT 通过 Roslyn 编译器动态编译所有 `.Build.cs` 和 `.Target.cs` 文件，构建 `ModuleRules` 实例；
3. **UHT 调用**：UBT 扫描所有带 UE 宏的头文件，调用 `UnrealHeaderTool` 生成 `.generated.h` 和 `.gen.cpp`；UE5.3+ 中此步骤可被 ZenGen 替代；
4. **动作图（Action Graph）构建**：UBT 将每个编译单元（`.cpp` 文件）映射为一个 `Action` 节点，包含编译器路径、编译参数、输入输出文件；
5. **增量检测**：通过比较文件时间戳或 `.response` 哈希，跳过未修改的编译单元；
6. **并行执行**：依据 CPU 核心数（默认为逻辑核心数减 1）并行调度 Action，使用本地执行器或（若配置了 `XGE`/`FASTBuild`/`Incredibuild`）分布式执行器；
7. **链接**：所有目标文件就绪后，调用链接器生成最终 `.exe`/`.dll`/`.so`。

### Unity Build（统一构建）

UBT 的一项重要优化是 **Unity Build**（又称 Jumbo Build），通过将多个 `.cpp` 文件合并为单一的 `Module.cpp` 编译单元，减少编译器启动开销和模板实例化重复：

$$
T_{\text{unity}} = \frac{N}{k} \cdot T_{\text{compile\_merged}} \ll N \cdot T_{\text{compile\_single}}
$$

其中 $N$ 为模块内源文件数量，$k$ 为每组合并文件数（默认值为 16，可通过 `MinFilesUsingPrecompiledHeader` 配置）。在引擎源码规模下，Unity Build 可将全量编译时间从数小时缩短至 40 分钟左右（Epic 内部基准，i9-13900K 平台）。但 Unity Build 会掩盖头文件依赖缺失问题：某个 `.cpp` 文件可能因偶然与包含所需头文件的另一文件合并而通过编译，独立编译时则失败。因此在排查头文件问题时，应在 `.Build.cs` 中临时设置 `bUseUnity = false`。

### 预编译头（PCH）策略

UBT 支持三种 PCH 模式，通过 `PCHUsage` 枚举配置：

| 模式 | 含义 |
|---|---|
| `NoPCHs` | 禁用 PCH，全量展开，编译最慢 |
| `UseSharedPCHs` | 使用引擎提供的共享 PCH（旧版默认，UE4 遗留） |
| `UseExplicitOrSharedPCHs` | 优先使用模块显式 PCH，无则回退共享 PCH（UE5 推荐） |

显式 PCH 通过在模块中创建 `MyModule.h` + `MyModule.cpp`（仅含 `#include "MyModule.h"`）并设置 `PrivatePCHHeaderFile = "MyModule.h"` 来声明，UBT 会为该头文件单独生成 `.pch` 文件并在后续编译中复用。

---

## 实际应用

### 插件开发中的模块注册

UE5 插件通过 `.uplugin` JSON 文件声明模块列表，UBT 在解析项目时会自动发现并注册插件模块：

```json
{
  "Modules": [
    {
      "Name": "MyPlugin",
      "Type": "Runtime",
      "LoadingPhase": "Default"
    },
    {
      "Name": "MyPluginEditor",
      "Type": "Editor",
      "LoadingPhase": "PostEngineInit"
    }
  ]
}
```

`LoadingPhase` 控制模块在引擎启动序列中的加载时机，共有 `EarliestPossible`、`PostConfigInit`、`PostSplashScreen`、`PreEarlyLoadingScreen`、`PreLoadingScreen`、`PreDefault`、`Default`、`PostDefault`、`PostEngineInit` 九个阶段。若编辑器扩展模块在 `Default` 阶段加载，可能因依赖的子系统尚未初始化而崩溃，必须推迟到 `PostEngineInit`。

### 自定义编译宏与平台差异处理

`.Build.cs` 文件可根据 `Target.Platform` 和 `Target.Configuration` 动态添加编译宏：

```csharp
if (Target.Platform == UnrealTargetPlatform.Win64) {
    PublicDefinitions.Add("MY_PLATFORM_WINDOWS=1");
    PublicSystemLibraries.Add("d3d12.lib");
} else if (Target.Platform == UnrealTargetPlatform.Linux) {
    PublicDefinitions.Add("MY_PLATFORM_LINUX=1");
    AddEngineThirdPartyPrivateStaticDependencies(Target, "OpenGL");
}
```

例如，某 VR 项目在 PC 平台需要链接 OpenXR SDK，在 Quest 平台需要链接 OVR Platform SDK，通过 `.Build.cs` 中的平台判断可以在不修改任何 C++ 源码的前提下完成条件链接。

### 分布式编译配置

对于大型团队，UBT 支持通过 `BuildConfiguration.xml`（位于 `Engine/Saved/UnrealBuildTool/`）配置 Incredibuild 或 FASTBuild 分布式编译器。关键参数 `bAllowXGE`、`bAllowFASTBuild` 控制分布式后端选择，`MaxParallelActions` 设置本地并发上限，`bStressTestUnity` 可在 CI 环境中强制启用 Unity Build 以验证合并后的编译正确性。

---

## 常见误区

**误区一：将所有依赖放入 `PublicDependencyModuleNames`**
这是最常见的错误。将 `Slate`、`RenderCore`、`RHI` 