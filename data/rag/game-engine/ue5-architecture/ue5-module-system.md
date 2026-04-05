---
id: "ue5-module-system"
concept: "UE5模块系统"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
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

# UE5模块系统

## 概述

UE5模块系统（Module System）是Unreal Engine 5将引擎代码拆分为独立编译单元的组织机制，每个模块对应一个动态链接库（.dll）或静态库（.lib），通过`.Build.cs`文件声明其依赖关系与编译选项。这一机制由Epic Games在UE3时代引入雏形，并在UE4/UE5中发展为覆盖引擎、编辑器与游戏项目的三层模块体系。

UE5的模块数量超过400个，仅引擎核心层（Engine）就包含`Core`、`CoreUObject`、`Engine`、`Renderer`等数十个模块。理解模块划分直接决定了开发者能否正确设置项目依赖、避免循环引用以及控制编译时间——一个错误的模块依赖会导致Unreal Build Tool（UBT）抛出链接错误或产生不必要的重编译。

## 核心原理

### 模块的物理结构与`.Build.cs`

每个UE5模块在磁盘上对应一个文件夹，其中必须包含同名的`.Build.cs`文件。以引擎自带的`Slate`模块为例，其`Slate.Build.cs`声明了对`Core`、`CoreUObject`、`InputCore`、`SlateCore`四个模块的公开依赖（`PublicDependencyModuleNames`）。依赖分为三类：

- **PublicDependencyModuleNames**：依赖暴露给所有引用本模块的模块，头文件路径自动传递。  
- **PrivateDependencyModuleNames**：依赖仅在本模块内部可见，不向外传播。  
- **DynamicallyLoadedModuleNames**：运行时通过`FModuleManager::LoadModuleChecked<>()`动态加载，不产生编译期链接依赖。

`.Build.cs`由UBT（Unreal Build Tool）在编译前解析，UBT本身是一个C#程序，位于`Engine/Source/Programs/UnrealBuildTool/`目录下。

### 模块的加载时机与类型

UE5将模块分为五种加载阶段（`ELoadingPhase`）：`Default`、`PreDefault`、`PostConfigInit`、`PostEngineInit`以及`PreEarlyLoadingScreen`。在`uplugin`或`uproject`的JSON描述文件中，每个模块条目都可以指定`LoadingPhase`字段。`Core`模块属于`PostConfigInit`最早可用的基础层，而依赖渲染管线的`Renderer`模块则在`Default`阶段加载。

模块类型（`Type`字段）同样关键：`Runtime`类型在最终发行包中存在，`Editor`类型仅在编辑器构建中存在，`DeveloperTool`类型在非发行包的所有构建中存在。错误地将仅用于编辑器的功能放入`Runtime`模块，会导致打包体积膨胀或Shipping版本编译失败。

### 分层依赖规则与循环依赖禁止

UE5模块依赖图必须是有向无环图（DAG）。官方定义的依赖层级由低到高为：  
`Core` → `CoreUObject` → `Engine` → `UnrealEd`（仅编辑器）。  
上层模块可依赖下层，但下层绝不能反向依赖上层。例如`CoreUObject`不得依赖`Engine`，因为`CoreUObject`需要在`Engine`之前初始化`UObject`反射系统。若确实需要跨层通信，UE5提供了**委托（Delegate）**和**接口（IInterface）**两种解耦机制。

## 实际应用

**为新游戏功能创建独立模块**：在UE5项目的`Source/`目录下新建`MyGameCore`文件夹，编写`MyGameCore.Build.cs`并在`MyGame.uproject`的`Modules`数组中注册，将`LoadingPhase`设为`Default`，`Type`设为`Runtime`。随后可以在该模块中实现核心游戏逻辑，与编辑器工具模块`MyGameEditor`完全分离，保证Shipping包不携带编辑器代码。

**减少重编译范围**：当`Renderer`模块的私有实现发生变化时，由于其内部细节通过`PrivateDependencyModuleNames`隔离，不依赖`Renderer`私有头文件的模块不需要重编译。在实际大型项目中，合理拆分模块可将增量编译时间从数分钟缩短至数十秒。

**动态加载插件模块**：UE5插件（Plugin）本质上是一组模块的集合加上资源包。通过`FModuleManager::Get().LoadModuleChecked<IMyPlugin>("MyPlugin")`，可以在运行时按需加载插件模块，实现DLC或热更新插件机制。`IModuleInterface`是所有模块必须实现的接口，其`StartupModule()`和`ShutdownModule()`方法对应模块的生命周期。

## 常见误区

**误区一：认为所有依赖都应声明为Public**。将本应私有的依赖放入`PublicDependencyModuleNames`会使该依赖传播给所有间接依赖本模块的模块，显著扩大重编译范围。正确做法是仅在头文件中暴露给外部使用的类型所属模块才设为Public，其余一律声明为Private。

**误区二：混淆模块（Module）与插件（Plugin）的关系**。插件是模块的容器，一个插件可以包含多个模块（例如`ChaosVehicles`插件包含`ChaosVehicles`和`ChaosVehiclesEditor`两个模块），但模块本身不依赖插件概念——引擎自带模块不属于任何插件而直接位于`Engine/Source/Runtime/`或`Engine/Source/Editor/`目录下。

**误区三：认为模块系统与C++命名空间等价**。UE5模块是编译与链接单元的划分，而C++命名空间仅是符号的逻辑分组，两者正交。同一模块内的类可以属于不同命名空间，不同模块的类也可以位于相同命名空间。UBT通过`MODULENAME_API`宏（例如`CORE_API`、`ENGINE_API`）控制符号导出，这与命名空间无关。

## 知识关联

UE5模块系统以**游戏引擎概述**中讲解的"引擎分层架构"思想为前提——没有对引擎整体分层的认识，就难以理解为何`Core`必须处于最底层。

在此基础上，**UObject系统**所在的`CoreUObject`模块是模块系统中最重要的单个模块之一，它提供了反射、序列化与垃圾回收的基础设施，所有继承自`UObject`的类都必须通过`CoreUObject`暴露的API操作，因此几乎每个Runtime模块都需要声明对`CoreUObject`的依赖。

对于渲染侧，**Nanite虚拟几何体**和**Lumen全局光照**分别对应`Renderer`模块下的子系统，它们的C++实现集中在`Engine/Source/Runtime/Renderer/`目录的`NaniteVisualize`和`Lumen`子目录中，属于同一个`Renderer`模块而非独立模块，这意味着无法单独禁用Nanite或Lumen的编译而不影响整个`Renderer`模块。**Chaos物理系统**则以独立插件`ChaosVehicles`加核心模块`Chaos`（位于`Engine/Source/Runtime/Experimental/Chaos/`）的形式存在，是模块系统中"实验性模块"通过路径命名约定标识的典型案例。**World Partition**的流送管理代码位于`Engine`模块内的`WorldPartition`子目录，同样不是独立模块，而是依托`Engine`模块的运行时支持。