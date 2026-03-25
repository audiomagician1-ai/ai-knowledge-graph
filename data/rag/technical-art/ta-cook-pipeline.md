---
id: "ta-cook-pipeline"
concept: "资产烘焙管线"
domain: "technical-art"
subdomain: "pipeline-build"
subdomain_name: "管线搭建"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 资产烘焙管线

## 概述

资产烘焙管线（Asset Baking Pipeline）是指将编辑器中使用的源资产（Source Asset）转换为游戏运行时可直接加载的目标资产（Cooked Asset）的自动化处理流程。这一转换过程不仅仅是格式转换，还包括压缩、合并、去冗余、平台适配等一系列优化操作。典型的烘焙结果包括：将 PSD 纹理压缩为 BC7/ASTC 格式、将 FBX 网格转换为引擎内部的二进制 Mesh 数据、将 HLSL Shader 源码编译为平台特定的字节码等。

资产烘焙管线的概念在 Unreal Engine 3 时代（约 2006 年前后）随着主机平台的多样化需求而逐渐成熟，当时 Epic 将这一过程称为"Cooking"，至今 UE5 仍沿用 `UnrealPak` 与 `CookCommandlet` 来完成这一任务。Unity 则通过其 AssetBundle 构建管线和后来的 Addressables 系统实现类似功能。烘焙管线的根本价值在于：编辑器需要保留高精度、可编辑的源数据，而运行时设备的内存、带宽和解码能力都极为有限，烘焙过程正是两者之间不可缺少的适配层。

## 核心原理

### 资产依赖图（Asset Dependency Graph）

烘焙管线的调度核心是有向无环图（DAG）。每个资产节点记录自身的输入资产列表和产出资产列表，例如一个材质（Material）节点依赖若干纹理节点和 Shader 节点，Shader 节点又依赖 HLSL 源文件节点。系统在启动烘焙时，从根资产出发做拓扑排序，确保依赖项总在被依赖项之前完成处理。如果某个叶节点的源文件未发生变化（通过对比文件哈希值，常用 SHA-256 或 xxHash），则跳过该节点的重新烘焙，即"增量烘焙"机制。这一机制可使日常迭代时的烘焙时间缩短 70%–90%，具体数字取决于资产修改范围。

### 处理器（Processor）与转换规则

每类资产类型对应一个专属 Processor，负责执行具体的转换逻辑。以纹理 Processor 为例，其执行顺序为：解码源格式→生成 Mipmap（通常使用 Kaiser 滤波）→按目标平台选择压缩格式（PC 用 BC7，Android 用 ASTC 4×4 或 ETC2，iOS 用 ASTC）→写入目标二进制文件。处理器的配置参数存储在资产的 Import Setting 或独立的 `.ruleset` 文件中，允许美术人员针对不同纹理类型（UI、法线、HDR）指定差异化规则，而不必修改管线代码本身。

### 增量构建与缓存策略

工业级烘焙管线必须实现分布式缓存，即将每次烘焙产出的资产以「输入内容哈希 → 输出二进制」的键值对形式存储到共享缓存服务器（如 Unity Accelerator 或自建的 Redis + 对象存储方案）。当另一台机器需要烘焙相同输入时，直接从缓存拉取结果，完全跳过本地计算。缓存命中的判断依据是**内容寻址哈希**，公式为：

```
CacheKey = Hash(ProcessorVersion + SourceAssetHash + ProcessorConfig)
```

其中 `ProcessorVersion` 版本号的变更会强制使全部旧缓存失效，确保处理器升级后不使用过期结果。

### 输出打包阶段

烘焙完成的单个资产文件需要进一步打包为 Bundle 或 Chunk。Bundle 的划分策略直接影响运行时内存占用和加载粒度：过细的划分导致大量 I/O 请求，过粗则浪费内存。常见策略包括：按场景划分、按逻辑模块划分、按热度划分（高频访问资产合并到同一 Bundle）。UE 的 `PrimaryAssetLabel` 和 Unity 的 Addressables Group 均是这一策略的配置载体。

## 实际应用

**手游项目的纹理烘焙配置**：一款面向中端 Android 设备的手游通常将 UI 纹理压缩为 ASTC 6×6（节省约 60% 内存相对 RGBA32），3D 角色漫反射贴图使用 ASTC 4×4，法线贴图则使用 BC5（仅存 RG 两通道，运行时重建 Z 分量）。这些规则写入针对不同目录的 Texture Preset，烘焙脚本在 CI 服务器上自动读取并批量处理。

**Shader 变体烘焙**：Shader 变体（Shader Variant）组合爆炸是烘焙管线中最棘手的问题之一。一个含 10 个关键字（keyword）的 Shader 理论上有 2¹⁰ = 1024 种变体。烘焙时需提前收集场景中实际使用的变体列表（ShaderVariantCollection），只编译必要变体，可将编译数量从数千降至数十，显著缩短烘焙时间并减小包体。

**本地化资产替换**：多语言项目在烘焙阶段将本地化文本、语音包作为独立资产组处理，通过在打包配置中指定 `LocaleFilter` 参数，为每个语言区域生成独立的 Bundle，避免玩家下载全量多语言资产。

## 常见误区

**误区一：烘焙等同于简单的格式转换**。许多初学者认为烘焙只是"把 PNG 改成压缩格式"。实际上，烘焙管线还需处理资产引用重定向（Reference Patching）——即将源资产中指向其他编辑器路径的引用，替换为运行时的资产 ID 或地址，否则游戏运行时无法正确加载依赖资产。这部分逻辑在自研引擎中需要显式实现，往往是管线 Bug 的高发区。

**误区二：增量烘焙只需比较文件修改时间**。文件时间戳在版本控制系统（如 Git）切换分支、CI 拉取代码等场景下会被重置或不准确，导致跳过实际需要重新烘焙的资产或反复烘焙未变更资产。正确做法是使用文件内容的哈希值作为变更判断依据，这也是现代构建系统（Gradle、Bazel、UE 的 DerivedDataCache）的标准做法。

**误区三：烘焙产出目录可以直接提交 Git**。烘焙产出文件体积大、二进制频繁变更，提交 Git 会导致仓库膨胀。正确做法是将烘焙产出存入专用的制品存储（Artifact Storage），通过构建哈希索引而非 Git 历史进行版本管理，本地开发时按需拉取，而非全量同步。

## 知识关联

资产烘焙管线直接承接**导入管线**的产出——导入管线负责将外部文件（FBX、PSD 等）解析并存入引擎编辑器的内部格式（如 UAsset 或 Unity 的 `.asset`），而烘焙管线的输入正是这些编辑器内部格式文件。如果导入阶段配置了错误的精度或通道信息，将在烘焙阶段被放大为运行时问题，因此两个阶段的配置需要联动设计。

向后延伸，理解烘焙管线是搭建**多平台管线**的前提：每个目标平台需要独立的烘焙配置（不同压缩格式、不同分辨率 Mipmap 起始层级、不同 Shader 编译目标），多平台管线本质上是在单一烘焙管线框架上叠加平台分支逻辑。此外，减少不必要的全量重烘焙、合理划分 Bundle 粒度，是**迭代速度优化**中最直接有效的手段，而这两点都需要以对烘焙管线内部机制的深入掌握为基础。
