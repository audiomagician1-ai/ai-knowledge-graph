---
id: "ta-multi-platform"
concept: "多平台管线"
domain: "technical-art"
subdomain: "pipeline-build"
subdomain_name: "管线搭建"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 多平台管线

## 概述

多平台管线（Multi-Platform Pipeline）是技术美术在项目中为PC、主机（Console）与移动端（Mobile）构建的一套差异化资产处理与输出流程。其核心任务不是维护三套独立工程，而是通过统一的源资产（Source Asset）在构建阶段自动分流，针对每个目标平台的硬件特性输出对应规格的贴图、Mesh与着色器变体。

这一概念随着跨平台商业游戏的兴起而系统化。2011年前后，Unity引入了Platform Overrides机制，允许同一张贴图在Inspector中为iOS、Android、Standalone分别设置压缩格式和最大尺寸；Unreal Engine则在4.x时代引入了Device Profile系统，通过`.ini`配置文件的层级继承来驱动平台差异。这两种思路代表了多平台管线设计的两条主线：**资产级覆写**与**设备配置驱动**。

多平台管线的价值在于它直接决定游戏能否在不同设备上同时达到目标帧率与显存预算。以一张角色皮肤贴图为例，PC版本可保留4096×4096 BC7格式（约8MB显存），主机版本降为2048×2048 BC7，移动端则必须转为ASTC 6x6（约900KB），三者来自同一张源文件，靠管线自动完成分发。

---

## 核心原理

### 平台能力矩阵与资产规格表

多平台管线首先需要建立一张**平台能力矩阵**，将硬件限制量化为具体数字约束。典型的三平台规格对比如下：

- **PC（DirectX 12 / Vulkan）**：支持BC1–BC7、ASTC（通过扩展），显存预算通常≥4GB，Shader Model 6.x，纹理最大分辨率16384×16384。
- **Console（PS5 / Xbox Series X）**：主要使用BC1/BC3/BC7，GDK平台额外支持XeSS纹理压缩，显存预算约10–16GB但受严格带宽限制，支持Mesh Shader与RT。
- **Mobile（iOS Metal / Android Vulkan）**：iOS强制ASTC（4x4至12x12），Android的ASTC支持率在OpenGL ES 3.1+设备上超过95%（截至2023年数据），但仍需准备ETC2兜底；GPU为Tile-Based架构，Overdraw成本远高于桌面端。

这张矩阵构成了管线中所有自动化决策的依据。

### 差异化构建流程（Build-Time Differentiation）

差异化不发生在运行时判断，而是在**构建阶段（Build Time）**完成资产分流。一个典型的多平台贴图处理节点链如下：

```
Source PSD (8K, 32-bit linear)
    └─ 导出管线
        ├─ PC Output      → 4K BC7, mip生成, sRGB转换
        ├─ Console Output → 2K BC7, 平台SDK工具链压缩
        └─ Mobile Output  → 2K ASTC 6x6 (质量 = medium), sRGB转换
```

在基于Python的资产管线（如Houdini Digital Asset或自研工具链）中，平台路由通常通过一个`platform_config.json`配置文件控制，其中记录每类资产（Albedo / Normal / Roughness）在每个平台的`max_resolution`、`compression_format`与`mip_bias`参数，构建脚本读取该文件后并行生成各平台包。

### 着色器变体的平台管理

多平台管线中着色器膨胀是最大的隐性成本。一个支持PC、PS5、移动端的着色器，若不加控制，在Unity的ShaderVariantCollection机制下可膨胀至数千个变体。具体控制手段包括：

- **平台关键字剥离（Shader Keyword Stripping）**：在`IPreprocessShaders`接口（Unity）或UE的`r.ShaderPipelineCache`中，为Mobile平台移除所有`#pragma multi_compile _ SHADOWS_SOFT`等桌面端专用变体。
- **Feature Level分层**：UE的Material Quality Level（Low / Medium / High）映射到Mobile / Console / PC三级，每级使用不同的节点子图（SubGraph），避免Mobile执行虚空指令。
- **PSO预编译**：PS5与Xbox使用管线状态对象（Pipeline State Object）预编译，要求在出包时静态确定所有着色器组合，这迫使管线在构建时完全枚举变体而非依赖运行时编译。

---

## 实际应用

### 角色资产的平台差异化输出

以一个AAA手游向PC移植项目为例，角色模型原始精度为80,000三角形，PC版本直接使用，主机版本使用LOD1（40,000三角形）作为基础，移动端使用LOD2（15,000三角形）并且剔除次级配件（如耳环、腰带扣等独立Mesh）。这些LOD并非美术手动制作三套，而是在资产入库时通过Houdini的`polyloft` + `polyreduce`节点以70%和20%的目标比例自动生成，并写入同一FBX文件的不同LOD层级，由构建脚本按平台提取对应层级打包。

### 移动端Tile-Based架构的特殊处理

移动端GPU（如Apple A17 Pro的GPU或高通Adreno 750）使用TBDR（Tile-Based Deferred Rendering）架构，Framebuffer读写完全在片上SRAM中完成，这意味着多平台管线必须为移动端禁用所有需要`Framebuffer Fetch`替代方案的后处理Pass。在Unity URP管线中，Mobile平台的`Renderer Feature`列表需剔除SSAO（改用SSAO的预烘焙版本）、Screen Space Reflection，以及任何采样`_CameraOpaqueTexture`超过一次的Pass，否则会触发Tile Memory Flush，导致显存带宽飙升3–5倍。

---

## 常见误区

### 误区一：用运行时`#if UNITY_IOS`替代构建时分流

很多初学者在Shader或C#脚本中直接使用平台宏做运行时判断，认为这等同于多平台管线。实际上，`#if UNITY_IOS`在Unity中是**编译期**宏，会在非iOS构建中被完全剥离，但在资产层面（贴图压缩、Mesh精度）它毫无作用——这些必须通过Asset Importer Settings或脚本化构建（`BuildPipeline.BuildAssetBundles`配合`BuildTarget`枚举）在构建时处理。将逻辑塞入运行时判断不仅不能减小包体，还会在构建目标不对时产生错误的资产引用。

### 误区二：移动端ASTC压缩参数全局统一

ASTC的块大小（4x4到12x12）对质量与压缩率影响显著：4x4压缩比约为8:1，接近BC7质量；12x12压缩比达到约22:1，但会在高频细节区域产生明显块状伪影。实际项目中，法线贴图必须使用ASTC 4x4（保留精度），Albedo可用6x6，环境Cubemap的远景面可用8x8。将所有贴图统一设为ASTC 6x6是一种过于粗糙的策略，会导致法线贴图精度损失直接表现为高光锯齿。

### 误区三：认为主机与PC管线可以共用同一压缩链

PS5的SDK（GNM/GNMX）要求贴图以GNF（Gnm Native Format）格式存储，并通过`orbis-image2gnf`工具链转换，这个过程会重新排列Mip层级的内存布局以匹配PS5的内存系统寻址模式。如果直接将PC构建的DDS文件复制到PS5包中，虽然格式兼容性可能通过，但会产生5–15%的贴图采样性能损耗，因为Mip的Tile排列不符合GCN/RDNA架构的最优布局。

---

## 知识关联

**前置概念——资产烘焙管线**：多平台管线的输入是已完成烘焙的高精度资产（法线、AO、厚度图等），烘焙管线产出统一规格的16位EXR或32位PSD源文件，多平台管线从这个统一源头开始分流。若烘焙阶段就已输出压缩格式，则多平台管线的分流灵活性会大幅受损。

**后续概念——版本迁移策略**：当项目引擎从Unity 2021升级到Unity 6，或从UE4升级到UE5时，各平台的压缩格式支持、Shader Feature Level定义以及Device Profile的配置结构都会发生变化。版本迁移策略需要盘点多平台管线中所有硬编码的平台参数，评估哪些`platform_config.json`条目需要更新，哪些Shader关键字剥离规则已被新版引擎内置，从而避免升级后出现平台特定的资产回退或性能劣化。
