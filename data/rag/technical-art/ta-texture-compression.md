---
id: "ta-texture-compression"
concept: "纹理压缩"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 纹理压缩

## 概述

纹理压缩是将位图纹理数据以有损或特定编码方式存储，使GPU能够在**不完全解压缩**的情况下直接采样的技术。与通用压缩算法（如ZIP）不同，纹理压缩格式专门设计为GPU硬件可直接解码的格式，采样时每个像素的解码仅需一个固定时钟周期，因此不会增加运行时的显存带宽压力。

纹理压缩技术的主要标准起源于1990年代末。S3 Texture Compression（S3TC）于1998年由S3 Graphics提出，后被OpenGL和DirectX标准化为DXT系列（即BC1–BC5），奠定了PC端纹理压缩的基础。移动平台则独立发展出ETC（Ericsson Texture Compression），并在OpenGL ES 2.0中强制支持ETC1，随后Khronos Group在2012年推出了ASTC（Adaptive Scalable Texture Compression），成为目前最灵活的跨平台方案。

理解纹理压缩对技术美术至关重要：一张未压缩的2048×2048 RGBA8纹理占用16 MB显存，而使用BC7压缩后仅需4 MB（8:1压缩比），ASTC 4×4可达到相同压缩比。在移动游戏中显存预算往往只有512 MB–1 GB，错误的压缩格式选择会直接导致内存超限或画质崩溃。

---

## 核心原理

### 块压缩的基本机制

所有主流纹理压缩格式均采用**固定尺寸块编码**策略。以BC/DXT系列为例，纹理被划分为4×4像素的块，每块固定编码为8字节（BC1）或16字节（BC2/BC3/BC5/BC7），而原始RGBA8的4×4块占64字节，BC1的压缩比因此为**8:1**（仅RGB）或**6:1**（含1位Alpha）。

每个4×4块内存储两个"端点颜色"和16个2位索引（BC1情况下），GPU在采样时通过插值这两个端点还原各像素颜色。由于所有16个像素共享同一对端点，若该块内颜色变化剧烈（如锐利边缘），则会产生"块状瑕疵"——这是纹理压缩有损性的根源，频率越高的细节（法线贴图的高频法线变化）越容易出现误差积累。

### 主流格式对比

| 格式 | 压缩比 | Alpha支持 | 适用平台 | 典型用途 |
|------|--------|-----------|---------|---------|
| BC1 (DXT1) | 8:1 | 1-bit | PC/主机 | 不透明漫反射 |
| BC3 (DXT5) | 4:1 | 8-bit | PC/主机 | 带透明的漫反射 |
| BC5 | 4:1 | 无 | PC/主机 | 法线贴图（RG双通道） |
| BC7 | 4:1 | 8-bit | PC/主机 DirectX 11+ | 高质量漫反射/PBR贴图 |
| ETC1 | 8:1 | 不支持 | Android（旧） | OpenGL ES 2.0漫反射 |
| ETC2 | 4:1–8:1 | 8-bit | Android（OpenGL ES 3.0+）| 漫反射/法线 |
| ASTC 4×4 | 8:1 | 8-bit | iOS A8+，Android高端 | 全类型贴图 |
| ASTC 8×8 | 2:1 | 8-bit | 同上（低质量模式） | 远景/次要贴图 |

**ASTC（自适应可变块尺寸）**是唯一支持从4×4（最高质量）到12×12（最低质量，压缩比约36:1）可变块尺寸的格式，且原生支持HDR和LDR、RGB与RGBA，以及3D纹理压缩，由ARM Holdings开发并于2012年提交至Khronos。

### 法线贴图压缩的特殊处理

PBR工作流中的法线贴图需要特别注意：直接用BC3压缩XYZ法线会导致Z分量精度损失，推荐做法是使用**BC5（双通道RG压缩）**仅存储法线的X和Y分量，在Shader中通过`sqrt(1 - x² - y²)`重建Z分量（假设法线向量已归一化）。ASTC格式则可直接压缩法线XYZ三通道，因为其量化误差更均匀，两通道重建法等效精度比BC5稍低但更简便。

---

## 实际应用

**Unity引擎的平台分发策略**：Unity的Texture Import Settings中，PC平台默认使用BC7（高质量）或BC1/BC3，iOS使用ASTC，Android则需要根据目标设备决定——支持OpenGL ES 3.0及以上设备使用ETC2，旧设备回退ETC1（此时需将Alpha通道单独拆分为独立贴图）。Unreal Engine 5同样在Android构建中提供ETC2与ASTC的并行打包选项（称为"Android multi-format"），会增加安装包体积但扩大兼容性覆盖。

**Substance Painter导出配置实践**：导出PBR贴图集时，技术美术通常为Roughness/Metallic/AO的打包贴图（RGB通道各一个灰度图）选择BC7或ASTC 4×4，因为这类贴图中轻微的色彩串扰会影响材质精确度；而对于BaseColor贴图（人眼对误差敏感度低），可降级使用BC1（无Alpha）或ASTC 6×6节省预算。

**流式加载中的Mip链**：纹理压缩与Mip Map配合使用时，每一级Mip同样以压缩格式存储。一张BC7的2048×2048纹理含完整Mip链总计占用约 2.67 MB（而非单级的4 MB），因为各Mip级内存之和约为最大级的1.33倍（等比级数）。

---

## 常见误区

**误区一：压缩格式越新越好，全部使用ASTC即可**
ASTC虽然灵活，但在不支持ASTC的设备上（如Android 4.x旧机型）GPU无法硬件解码，引擎会回退软件解码，导致帧率暴跌。此外ASTC编码速度远慢于ETC2，在CI/CD构建流程中若纹理数量庞大，选择合适的格式会显著影响构建时间。

**误区二：法线贴图应当使用BC3（DXT5）压缩**
BC3压缩RGBA四通道时，XYZ法线分量会被分别压缩到不同通道，各通道量化误差相互独立，重建法线会产生明显非均匀误差，在光照计算时表现为高光锯齿。正确做法是使用BC5压缩RG双通道（每通道独立8位Block），误差分布更均匀，高频法线保留更准确。

**误区三：运行时可以随时切换压缩格式而无性能损耗**
纹理压缩格式在导入时固定，GPU只能对硬件原生支持的格式直接采样。若运行时通过脚本转换格式（如从PNG解压再重新压缩为BC7），会在CPU上产生数十至数百毫秒的编码延迟（Intel Texture Works压缩一张1024×1024 BC7需约0.5秒），不适用于实时场景。

---

## 知识关联

**前置依赖（PBR材质基础）**：学习纹理压缩时需已掌握BaseColor、Normal、Roughness、Metallic各贴图的语义，才能判断哪些通道对压缩误差敏感（法线XY精度、Roughness灰度精度），从而为不同贴图类型选择最合适的压缩格式与块尺寸。BC5专用于法线贴图、BC7用于高精度PBR贴图的决策逻辑，都建立在对各贴图数据特性的理解上。

**横向关联（Mip Map与流式纹理）**：纹理压缩与Mip Map系统深度耦合，所有压缩格式要求纹理分辨率为4的倍数（ASTC要求对齐到块尺寸的倍数），非POT或非对齐分辨率会导致边缘块填充（padding），实际占用内存高于理论值。在UE5的Virtual Texture（虚拟纹理）系统中，每个Virtual Tile固定为128×128像素，压缩格式选择同样影响Tile的内存密度。