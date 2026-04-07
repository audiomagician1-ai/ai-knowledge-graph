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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# HDR管线

## 概述

HDR管线（High Dynamic Range Pipeline，高动态范围渲染管线）是指在整个渲染流程中，以高于显示器物理亮度上限的浮点精度存储和计算光照数据，直到最终输出阶段才将其压缩至可显示范围的完整工作流。与传统8位LDR管线不同，HDR管线的帧缓冲使用16位或32位浮点格式（如 `GL_RGBA16F` 或 `GL_RGBA32F`），可表示远超 [0, 1] 范围的亮度值，例如太阳直射光可达 100,000 lux，而阴影区域仅有 0.001 lux，两者在同一场景中共存时若使用8位格式将不可避免地发生截断。

这一概念在1984年由工业光魔（ILM）的Ken Perlin等人在电影特效领域率先实践，游戏领域则在2003年前后随着可编程着色器的普及而逐步引入。HDR管线之所以重要，在于它将"光照计算"与"显示能力"两个本质上无关的步骤完全解耦——物理正确的光照计算在线性空间中进行，而如何在显示器上呈现则由后续的色调映射和伽马校正负责，这种分离使得同一份渲染结果可以适配不同的输出设备和色彩空间标准。

## 核心原理

### 线性空间与浮点帧缓冲

HDR管线的基础要求是所有光照运算必须在线性光照空间中进行。当纹理资产以sRGB格式存储时（这是美术的默认工作空间，伽马值约为2.2），管线在采样阶段须将其转换为线性值：`linear = sRGB ^ 2.2`。若跳过这一步直接在sRGB空间做光照叠加，两盏相同强度的灯叠加后亮度会比正确结果偏暗约47%，因为非线性编码破坏了物理叠加的线性性质。

浮点帧缓冲的选择直接决定精度与带宽的平衡：`GL_RGBA32F` 每像素16字节，精度最高，适合离线渲染；实时游戏通常采用 `GL_RGBA16F`，每像素8字节，可表示的最大值约为 65504，足以容纳物理真实的光照强度范围。部分移动平台使用 `GL_R11F_G11F_B10F`，以牺牲蓝色通道精度换取6字节/像素的带宽优势。

### HDR到LDR的映射阶段

HDR管线在最终输出前必须执行从高动态范围到显示动态范围的映射，即**色调映射（Tone Mapping）**。这一步的位置至关重要：必须在泛光（Bloom）、景深（DoF）等所有后处理效果完成之后、伽马校正之前执行。若在色调映射前先做伽马校正，会导致Bloom等效果在错误的非线性空间中运算，产生亮度错误和色相偏移。

常见的Reinhard算子公式为：

```
L_out = L_in / (1 + L_in)
```

其中 `L_in` 为HDR亮度值，`L_out` 为映射后的 [0, 1] 值。更精确的扩展版本引入场景平均亮度 `L_avg` 进行曝光校正：

```
L_scaled = L_in * (a / L_avg)
L_out = L_scaled / (1 + L_scaled)
```

其中 `a` 为曝光参数（俗称"中灰键值"，默认取0.18），`L_avg` 通常通过对对数亮度做全屏降采样平均获得。

### 自动曝光与眼适应

真实的HDR管线不仅做静态色调映射，还需模拟人眼从明亮环境进入暗室时的适应过程。自动曝光系统在每帧计算帧缓冲的平均亮度，然后用一阶指数平滑将当前曝光 `EV` 向目标值靠近：

```
EV_current = EV_current + (EV_target - EV_current) * (1 - e^(-delta_time / tau))
```

其中 `tau` 是适应时间常数，典型值为"瞳孔收缩（明适应）0.1秒，瞳孔放大（暗适应）0.4秒"，对应人眼生理数据。平均亮度计算通常借助 `Compute Shader` 对帧缓冲做 Histogram（直方图）统计，剔除极端2%~3%的像素后取加权均值，避免小面积高亮光源（如场景中的灯泡）过度主导曝光结果。

## 实际应用

在虚幻引擎4/5中，HDR管线的帧缓冲格式默认为 `PF_FloatRGBA`（即 RGBA16F），渲染目标在 `SceneColor` 阶段完成所有光照计算后，经过泛光、镜头光晕等效果，最终在 `PostProcessing` Pass 中依次执行：自动曝光调整 → ACES色调映射（Academy Color Encoding System，2014年由电影学院制定的行业标准）→ sRGB伽马编码 → 输出至交换链。

Unity HDRP（High Definition Render Pipeline）同样遵循这一流程，其 `Volume` 系统允许美术在场景中放置曝光体积，以 EV100 为单位手动控制区域曝光，EV100 = 0 对应18%灰卡在100 ISO、f/1、1/100秒条件下的标准曝光，与摄影领域的概念完全统一。

## 常见误区

**误区一：认为HDR管线等同于开启HDR显示输出（HDR10/Dolby Vision）。**  
实际上，这是两个独立的概念。HDR渲染管线是渲染内部的工作流，而HDR10是面向用户的显示标准（峰值亮度1000 nit，色域BT.2020）。一个游戏可以使用HDR管线渲染但仍输出至SDR显示器（此时色调映射压缩至 [0, 1] 后再编码为sRGB），也可以在启用HDR10输出时将 `L_out` 范围扩展至 [0, 10000 nit] 并使用PQ（Perceptual Quantizer）传输曲线编码。

**误区二：以为色调映射应在所有后处理之前执行，以防止后处理操作超出范围。**  
这个做法会导致Bloom在LDR空间中计算，非常亮的光源（如 `L_in = 10.0`）被色调映射压缩至接近1.0后，其泛光扩散范围远小于真实情况，因为LDR空间中1.0与0.9之间的差异比HDR空间中10.0与1.0之间的差异小得多。正确顺序是将色调映射置于后处理链末尾。

**误区三：将线性空间工作流等同于直接禁用伽马校正。**  
线性空间工作流并非不做伽马校正，而是在最终输出时做一次精确的 `linear → sRGB` 转换（`out = linear^(1/2.2)` 或使用标准的分段sRGB公式），确保显示器的 `2.2` 次方幂次与渲染管线的线性空间互相抵消，使最终显示亮度与物理计算一致。

## 知识关联

HDR管线建立在**色调映射**的概念之上——理解Reinhard、ACES、Filmic等色调映射算子的数学形式，是正确配置HDR管线输出阶段的前提。HDR管线中的浮点帧缓冲与自动曝光机制，直接影响泛光（Bloom）、镜头光斑（Lens Flare）等后处理效果的物理准确性：这些效果依赖HDR亮度数据来生成有意义的强度差异，而这些差异在LDR帧缓冲中会因截断而丢失。学习HDR管线还要求理解色彩空间转换（sRGB ↔ 线性）以及GPU帧缓冲格式的精度与带宽权衡，为后续针对具体平台（PC、主机、移动）优化后处理效率奠定基础。