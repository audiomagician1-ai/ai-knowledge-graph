---
id: "cg-sharpening"
concept: "锐化"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 锐化

## 概述

锐化（Sharpening）是一类图像后处理技术，其目的是增强图像中边缘与细节的视觉对比度，使原本因采样、抗锯齿、压缩或上采样而变得模糊的图像看起来更加清晰。锐化的本质是一种**高频增强**操作：人眼感知"清晰"的关键在于边缘处的亮度跳变幅度，锐化滤波器通过检测并放大这些局部亮度变化来模拟更高分辨率的视觉效果。

锐化技术在摄影后期软件（如 Photoshop）中早已广泛应用，但将其引入实时渲染的里程碑事件是 AMD 于 2019 年发布的 **CAS（Contrast Adaptive Sharpening，对比度自适应锐化）** 算法。CAS 随 FidelityFX SDK 公开了源码，使得它被集成进 Vulkan、DirectX 12 等主流图形 API 的后处理管线。同年，NVIDIA DLSS 也引入了类似的锐化步骤来弥补超分辨率输出的软化问题。

锐化在实时图形中的重要性源于两个实际需求：其一，TAA（时域抗锯齿）会对相邻帧的像素做加权混合，导致画面产生"鬼影模糊"；其二，动态分辨率（Dynamic Resolution Scaling）和超分辨率技术在放大图像时会引入低通滤波效应。锐化作为后处理的最后一步，可以廉价地补回这部分细节损失。

---

## 核心原理

### Unsharp Mask（USM，反锐化蒙版）

尽管名字含有"反锐化"，USM 实际上是最经典的锐化方法，其公式为：

$$I_{\text{sharp}} = I_{\text{orig}} + \lambda \cdot (I_{\text{orig}} - I_{\text{blur}})$$

其中 $I_{\text{orig}}$ 是原始图像，$I_{\text{blur}}$ 是通过高斯模糊（半径通常取 0.5–2 像素）得到的低频版本，$\lambda$ 是锐化强度系数（典型值为 0.5–2.0）。括号内的差值 $(I_{\text{orig}} - I_{\text{blur}})$ 正是图像的**高频分量**，叠加回原图即实现锐化。USM 的代价是：$\lambda$ 过大时，边缘两侧会出现明显的亮环/暗环，称为 **Halo 伪影**（光晕伪影）。

### CAS（对比度自适应锐化）

CAS 由 Timothy Lottes 设计，核心思想是**根据局部对比度自适应调整锐化强度**，以避免在已经高对比度的区域产生过度锐化和 Halo。CAS 使用一个 3×3 像素邻域，取中心像素及其上下左右四个邻居（十字形核），计算局部最大值 $M$ 与最小值 $m$，然后推导出自适应权重：

$$w = -\frac{1}{4} \cdot \frac{\sqrt{\min(M, 1-M)}}{\sqrt{\min(M, 1-M)} + \text{sharpness}}$$

最终输出为中心像素与四邻居的加权混合。整个算法在 GPU 上只需约 **13 次纹理采样**即可完成，延迟极低（在 1080p 分辨率下典型 GPU 耗时约 0.1 ms）。`sharpness` 参数范围为 $[0, 1]$，值越小锐化越强（AMD FidelityFX 中默认值为 0）。

### RCAS（Robust Contrast Adaptive Sharpening，鲁棒对比度自适应锐化）

RCAS 是 AMD 在 FSR 1.0（2021 年发布）中为超分辨率场景专门设计的改进版 CAS。与 CAS 不同，RCAS 在执行锐化前会对邻域像素做**噪声抑制**：通过将 Luma 最大值限制在邻居的均值附近，RCAS 可以避免将噪声像素或压缩伪影当作边缘来增强。RCAS 同样使用 3×3 邻域，但在权重计算中加入了一个 `rcas-limit` 上限（默认 0.25），防止任意像素的权重绝对值超过该值，从而在锐化强度与抗噪之间取得平衡。FSR 1.0 的标准用法是先做 EASU（边缘感知空间超采样上采样）再接 RCAS 锐化，两者合称完整的 FSR 1.0 管线。

---

## 实际应用

**游戏引擎后处理管线集成**：在 Unreal Engine 5 中，CAS 锐化通过 `r.Tonemapper.Sharpen` 控制台变量暴露给开发者，其范围为 0–10，引擎内部将该值映射到 CAS 的 `sharpness` 参数。通常建议在 TAA 启用时将此值设为 0.5–1.0，以抵消 TAA 的模糊副作用。

**FSR 超分辨率管线**：在 FSR 1.0 的 "Quality" 模式下，渲染分辨率为目标的 77%，由 RCAS 负责在最终输出前补回因上采样损失的高频细节。如果跳过 RCAS 步骤，输出图像的边缘清晰度会明显低于原生渲染。

**截图与视频导出**：在离线渲染场景下，USM 的高斯半径通常取 1.0–1.5 像素，$\lambda$ 取 0.8–1.2，这是商业打印和 4K 视频母版常用的参数范围，能在 Halo 伪影可接受的前提下提升感知清晰度。

---

## 常见误区

**误区一：锐化能恢复丢失的信息**。锐化只是增大了边缘处的亮度对比，它不能重建真正丢失的高频细节，更无法恢复因压缩或采样不足而消失的纹理。过度锐化反而会将压缩噪声和 JPEG 块状伪影一并放大，使图像质量下降。

**误区二：锐化强度越大越好**。CAS 的 `sharpness` 参数设为最小值（0）时，并非表示"无锐化"，而是"最强锐化"——AMD 的参数方向与直觉相反。此外，在高频纹理（如砖墙、金属网格）区域，过强的 CAS 会导致莫尔纹（Moiré）状的振铃伪影，需在美术审查中重点关注。

**误区三：CAS 和 RCAS 可以互换**。CAS 设计用于对原生分辨率图像做轻微锐化，而 RCAS 专为超分辨率输出设计，内置了噪声抑制机制。将 RCAS 用于原生图像时，其噪声抑制逻辑可能会错误地平滑某些真实的高频细节，效果反而不如 CAS。

---

## 知识关联

锐化以**后处理概述**所介绍的全屏后处理框架为基础：锐化 Pass 通常以 HDR Tonemapping 之后的 LDR 图像作为输入，排列在后处理链的最末端，以避免后续操作再次引入模糊。理解锐化需要掌握卷积核、高频分量的概念，这些知识在学习 Bloom（泛光）和景深（Depth of Field）时同样会用到，三者都依赖对图像频域特性的操控，只是方向相反——Bloom 和 DoF 是有意引入低通滤波，而锐化是有意补偿低通损失。CAS 的亮度自适应权重思路也与 FXAA 中基于局部对比度跳过平滑的策略有相似之处，两者都体现了"感知驱动"的滤波设计哲学。