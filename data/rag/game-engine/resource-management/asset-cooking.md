---
id: "asset-cooking"
concept: "资源烘焙"
domain: "game-engine"
subdomain: "resource-management"
subdomain_name: "资源管理"
difficulty: 2
is_milestone: false
tags: ["构建"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 资源烘焙

## 概述

资源烘焙（Asset Baking）是游戏引擎在正式打包或运行前，将原始资产（如 PSD 贴图、FBX 模型、WAV 音频）转换为目标平台可直接消费的二进制格式的预处理过程。这一步骤发生在编辑器构建管线（Build Pipeline）中，输出结果通常缓存在专用目录（Unity 称之为 `Library/`，Unreal 称之为 `DerivedDataCache/`），以避免每次运行时重复计算。

资源烘焙的概念随 20 世纪 90 年代末主机平台的多元化而兴起。PS2 的 GS 芯片要求贴图以特定的 Swizzle 内存排布存储，PC 的 DX9 要求 DXT 压缩，这些差异使得"一份源文件、多份目标产物"的烘焙思路成为必然。Unreal Engine 3（2006 年随《战争机器》发布）将这套流程系统化为 Cook 步骤，此后成为行业标准术语。

烘焙的意义在于将"平台适配"从运行时成本转移到离线构建阶段。一张 4096×4096 的 PNG 贴图在烘焙为 ASTC 6×6 格式后，GPU 可直接解码，无需 CPU 中转；而若在运行时才做格式转换，不仅占用帧时间，还会导致显存峰值翻倍。

## 核心原理

### 格式转换与平台目标矩阵

烘焙的第一步是确定"平台-格式"映射表。典型的映射规则为：iOS/Android 高端设备使用 ASTC（Adaptive Scalable Texture Compression），Android 中低端使用 ETC2，PC/主机使用 BC7（Block Compression 7）。每种格式的压缩比和质量取舍不同：BC7 的 PSNR（峰值信噪比）可达 48 dB，而 ETC1 仅约 38 dB。烘焙系统需要为每个目标平台独立输出一份产物，这意味着一份源贴图可能产生 3-5 个不同的烘焙结果。

### 哈希指纹与增量重烘焙

为了不在每次修改后全量重新烘焙，烘焙系统会为每个源资产计算内容哈希（通常是 MD5 或 xxHash64），结合烘焙参数（分辨率上限、mipmap 层级、目标格式）生成一个复合键值。当源文件的哈希或参数发生变化时，才触发重新烘焙，否则直接读取缓存。Unreal 的 DDC（Derived Data Cache）正是基于这一机制，支持本地缓存和远程共享缓存服务器，团队协作时命中率可超过 95%，将首次构建时间从数小时压缩到数分钟。

### 烘焙流水线的工作流程

一个标准的烘焙流水线包含以下有序阶段：

1. **资产发现**：扫描工程目录，收集所有引用图（Asset Reference Graph）
2. **依赖排序**：对材质、Shader、贴图的依赖关系做拓扑排序，确保被依赖项先于依赖项烘焙
3. **格式处理器（Processor）调用**：针对不同资产类型（纹理、网格、音频）调用对应的格式处理器；音频烘焙会将 WAV 转为 Ogg Vorbis（品质参数 q=5 约对应 160 kbps）或 ADPCM
4. **产物写入缓存**：将编译结果写入缓存数据库，记录哈希键与文件路径的映射
5. **清单生成**：输出资产清单文件，供后续内容包（Bundle）系统使用

### 网格与骨骼动画的烘焙特殊性

贴图转码之外，网格烘焙涉及顶点属性的重新打包。例如，法线和切线向量从 float32×3 精度降至 INT16×4 的 Octahedron 编码，可将顶点缓冲大小减少约 40%。骨骼动画烘焙则会将关键帧曲线采样为等间隔帧序列（常见 30fps），并对旋转四元数做量化压缩，以换取 GPU Skinning 时更高的缓存命中率。

## 实际应用

**Unity 的 AssetBundle 构建流程**：在调用 `BuildPipeline.BuildAssetBundles()` 时，Unity 内部自动对标记资产执行烘焙，将贴图转为当前平台的压缩格式后才打入 `.bundle` 文件。开发者可通过 `TextureImporter.SetPlatformTextureSettings()` 为 iOS 单独指定 ASTC 4×4（高质量）、为 Android 指定 ETC2。

**Unreal 的 Cook 命令**：通过命令行 `UE4Editor-Cmd.exe MyProject.uproject -run=Cook -TargetPlatform=IOS` 执行，Cook 过程会将所有 `.uasset` 转换为平台专用格式，输出至 `Saved/Cooked/IOS/` 目录。对于大型项目（资产超过 10 万个），全量 Cook 耗时可达 6-8 小时，增量 Cook 配合 DDC 可降至 20 分钟以内。

**音频的差异化烘焙**：背景音乐通常烘焙为流式播放的 Ogg Vorbis，而高频触发的短音效（枪声、脚步）则烘焙为解压到内存的 ADPCM，以避免高并发解码的 CPU 峰值。

## 常见误区

**误区一：烘焙等同于压缩**。烘焙包含但不限于压缩。网格的顶点属性重排、Shader 的平台字节码编译（HLSL → SPIR-V）、贴图 Mip 链生成均属于烘焙步骤，但不一定减小文件体积。例如，将 JPEG 贴图烘焙为 BC1 后，磁盘体积可能反而增大，但 GPU 解码效率大幅提升。

**误区二：烘焙只在打包时才需要关心**。在 Unity 编辑器中，每次进入 Play Mode 时引擎会检测脏资产并触发局部重烘焙；在 Unreal 中，PIE（Play In Editor）模式默认使用未烘焙资产（Editor 格式），这会导致 PIE 中的渲染效果与真机存在差异，尤其体现在贴图压缩瑕疵和法线精度上。

**误区三：所有平台共用同一份烘焙缓存**。每个平台目标的烘焙键值均包含平台标识符，iOS 的 ASTC 产物与 Android 的 ETC2 产物是独立存储的两份缓存。混用缓存是导致"真机显示异常但编辑器正常"这类问题的常见根源之一。

## 知识关联

**前置概念**：资源管理概述建立了"源资产"与"运行时资产"的二元区分，烘焙正是连接这两者的具体机制。理解资产引用图（Asset Reference Graph）是保证烘焙依赖顺序正确的必要前提。

**后续概念**：烘焙产物是**内容包系统**（AssetBundle / PAK）的直接输入——只有经过平台化烘焙的资产才能被正确打入内容包并在目标设备上加载。此外，烘焙选择哪种纹理**压缩格式**（ASTC、BC7、ETC2 的块大小、位深度及硬件支持矩阵）直接决定了内存占用与画质的权衡，是内容包系统拆包策略的上游约束。