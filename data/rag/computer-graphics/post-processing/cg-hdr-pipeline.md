---
id: "cg-hdr-pipeline"
concept: "HDR管线"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# HDR管线

## 概述

HDR管线（High Dynamic Range Pipeline）是指在渲染系统中，将场景亮度值保留在线性高动态范围内进行计算，最终通过色调映射输出到显示设备的完整工作流程。其核心特征是：中间所有光照计算均在浮点精度（通常为16位或32位浮点）的HDR帧缓冲中进行，亮度值不被截断到[0,1]范围，而是允许超过1.0的高亮区域存在。

HDR管线的概念随实时图形硬件的发展逐渐普及。早期的LDR（Low Dynamic Range）管线直接在8位整数帧缓冲中执行所有计算，导致超亮区域被硬性截断为纯白，丢失细节。2002年前后，随着NVIDIA GeForce FX系列引入fp16帧缓冲支持，以及Valve在《半条命2》中广泛应用HDR光照，实时HDR管线成为现代游戏引擎的标准配置。如今Unity、Unreal Engine 4/5均默认开启HDR渲染路径。

HDR管线的意义在于：它将物理上正确的亮度范围（真实世界太阳表面约1.6×10⁹ cd/m²，阴影约0.01 cd/m²，动态范围超过10个数量级）压缩进可计算空间，再以艺术可控的方式映射至显示器的实际亮度范围（SDR显示器约80–300 nits）。

---

## 核心原理

### 线性工作空间与Gamma校正的分离

HDR管线要求所有光照计算在线性空间中进行，而不是在经过Gamma编码的空间中操作。当纹理以sRGB格式存储时，管线在采样时会自动进行sRGB到线性的解码（approximate_gamma ≈ 2.2）；只有在最终输出阶段，才将线性结果重新编码为sRGB供SDR显示器使用，或输出为PQ/HLG曲线供HDR显示器使用。

若在非线性空间直接叠加光照，则两个灰度值0.5的表面相加后应为1.0（线性），但在Gamma空间中0.5对应线性亮度约0.214，相加后0.428对应线性1.0显然是错误的。HDR管线通过严格分离线性计算与编码阶段来避免这类色彩偏差。

### HDR帧缓冲格式

HDR管线通常使用以下几种帧缓冲格式：
- **R16G16B16A16_FLOAT**：每通道16位浮点，fp16格式，可表示约±65504的数值范围，精度在[1, 2)区间为1/1024，是主流HDR渲染格式；
- **R11G11B10_FLOAT**：共32位，红绿各11位、蓝10位浮点，无Alpha通道，节省带宽但蓝色精度较低；
- **R32G32B32A32_FLOAT**：每通道32位单精度浮点，精度最高但带宽是fp16的两倍，常用于离线渲染。

在移动端，RGBA16F的带宽开销较大，因此部分管线选择R11G11B10F作为HDR中间缓冲。

### 色调映射作为管线终点

HDR管线的最后一步是色调映射（Tone Mapping），将线性HDR亮度值映射至[0,1]的LDR输出范围。这一步通常包含以下决策：

1. **曝光控制**：通过乘以曝光系数`exposure`调整场景整体亮度，常见公式为 `mapped = 1 - exp(-color * exposure)`（Reinhard变体）；
2. **S曲线映射**：如ACES（Academy Color Encoding System）Filmic曲线，具体公式为：
   `f(x) = (x(2.51x + 0.03)) / (x(2.43x + 0.59) + 0.14)`，该曲线由A=2.51, B=0.03, C=2.43, D=0.59, E=0.14五个参数定义，提供胶片感的高光压缩与阴影提升；
3. **自适应曝光（Auto Exposure / Eye Adaptation）**：通过计算场景亮度直方图的几何平均值（即对数平均亮度），模拟人眼瞳孔调节，动态更新曝光系数，调节速度通常以0.1–2秒的平滑时间控制。

---

## 实际应用

**游戏引擎中的HDR渲染路径**：在Unreal Engine 5中，启用HDR管线只需在项目设置中开启"Linear HDR Rendering"，其渲染器在GBuffer阶段使用fp16精度存储光照累积结果，在最终Post Process阶段依次执行：Bloom → Lens Flare → Auto Exposure → Tone Mapping → Color Grading → Gamma/PQ输出，整个链条在线性空间贯通。

**Bloom效果的HDR依赖**：HDR管线是实现物理可信Bloom的必要条件。LDR管线中高亮区域被截断为1.0，提取高光时无法区分"白色"和"极亮白色"；而HDR管线中，像素亮度可以是5.0或20.0，Bloom阈值（如threshold=1.0）仅提取真正超亮的区域，形成自然的光晕扩散效果。

**HDR显示器输出**：当目标平台支持HDR10（Peak Luminance 1000 nits，色域BT.2020）时，HDR管线的输出路径从sRGB Gamma编码切换为PQ（Perceptual Quantizer，SMPTE ST 2084）曲线编码，峰值亮度信息通过HDMI 2.0/2.1的元数据（MaxCLL、MaxFALL）传递至显示器，使画面在HDR显示设备上呈现真实的高对比度范围。

---

## 常见误区

**误区一：认为开启HDR帧缓冲后不需要色调映射**
部分初学者认为HDR管线"自然地"能在显示器上呈现更多亮度层次，省去色调映射。实际上，HDR帧缓冲只是中间计算容器，其亮度值对显示硬件没有意义——显示器仍然只接受[0,1]（SDR）或特定PQ编码（HDR10）的信号。没有色调映射步骤，直接输出fp16缓冲会导致所有超过1.0的值被显卡驱动截断，效果与LDR无异甚至更差。

**误区二：以为HDR管线会让所有颜色都更亮更饱和**
HDR管线本身不改变场景视觉亮度，它的作用是"保留"而非"增加"亮度信息。若灯光美术未在物理正确范围内设置光源强度（如用Lux/Candela单位），HDR管线带来的只是浮点精度的提升，并不会自动产生强烈的光影对比。只有配合基于物理的光照（PBR）和合理的曝光设置，HDR管线才能发挥应有效果。

**误区三：混淆HDR渲染管线与HDR显示标准**
"HDR管线"是渲染侧的概念，指线性浮点工作流；"HDR10 / Dolby Vision"是显示侧的标准，指显示器硬件能呈现的亮度范围。即便只针对SDR显示器，使用HDR管线进行中间计算再输出sRGB也是正确且必要的做法——这与最终是否输出到HDR显示器完全无关。

---

## 知识关联

HDR管线直接依赖**色调映射**作为其输出阶段的核心操作：没有色调映射，HDR管线的浮点亮度值无法正确呈现在任何显示设备上。Reinhard、ACES Filmic、Filmic Blender等不同色调映射算子的选择，决定了HDR管线最终的视觉风格，尤其在高光压缩曲线的斜率和拐点位置上各有差异。

在更基础的层面，HDR管线与**Gamma校正**紧密耦合——线性工作空间的维护要求对所有输入纹理进行sRGB解码、对所有输出进行Gamma/PQ再编码，这一工作在渲染API层（如Vulkan的`VK_FORMAT_R8G8B8A8_SRGB`与`VK_FORMAT_R8G8B8A8_UNORM`格式区分）自动或手动执行。同时，**Bloom、镜头光晕、自适应曝光**等后处理效果均以HDR帧缓冲数据作为输入，其效果质量直接受HDR管线精度的影响。
