---
id: "cg-bloom"
concept: "泛光"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 泛光（Bloom）

## 概述

泛光（Bloom）是一种模拟人眼或摄影镜头对强光源产生光晕扩散效果的后处理技术。当场景中存在极亮区域（如太阳、火焰、霓虹灯）时，光线会在现实中因镜头散射或视网膜过曝而向周围渗透，Bloom正是对这一物理现象的近似模拟。

Bloom技术在实时渲染领域的普及始于2000年代初，随着可编程着色器（Shader）的广泛应用而成熟。早期游戏通过简单的帧缓冲叠加实现，2004年前后Valve在《半条命2》中大规模应用了HDR渲染与Bloom的组合，标志着这一技术进入主流。

Bloom对画面质量的提升立竿见影，是区分"平坦感"画面与"有体积感"画面的重要手段。一张原本生硬的灯光渲染图，经过Bloom处理后，明亮区域会自然向外晕染，使观众感受到光源的能量强度，从而增强场景的真实感与氛围感。

---

## 核心原理

### 第一步：高亮提取（Bright Pass Filter）

Bloom的第一步是从当前帧的颜色缓冲（Color Buffer）中提取超过亮度阈值的像素。最常见的做法是计算每个像素的亮度值（Luminance），公式为：

$$L = 0.2126R + 0.7152G + 0.0722B$$

其中 R、G、B 为像素的线性空间颜色分量，系数来自 Rec.709 标准。当 $L$ 超过预设阈值（例如 1.0，即 HDR 渲染中超出 LDR 范围的部分）时，该像素被保留；低于阈值的像素归零。

为避免提取边界产生硬截断，实际工程中常用**软阈值（Soft Threshold / Knee）**策略：在阈值附近设置一个过渡区间 $[threshold - knee, threshold + knee]$，在该区间内按二次曲线平滑过渡，而不是突变为0，使高亮边缘的晕光更加自然。

### 第二步：多尺度高斯模糊（Multi-Pass Gaussian Blur）

提取出高亮图后，对其进行高斯模糊以模拟光晕的扩散。单次全分辨率高斯模糊的计算代价极高，因此实践中采用**降采样+分离式（Separable）高斯卷积**组合策略：

- 将高亮图逐级降采样至 1/2、1/4、1/8、1/16 分辨率，形成 Mip 链；
- 在每一级分辨率上分别做水平和垂直方向的一维高斯模糊（利用高斯核可分离性，将二维卷积分解为两次一维卷积，计算量从 $O(k^2)$ 降至 $O(2k)$）；
- 再逐级上采样并叠加，形成具有多种扩散半径的综合光晕。

这种多尺度方案（常称为 **Dual Kawase Blur** 或 **Kawasei Bloom**）在 Unreal Engine 4 的 Bloom 实现中被广泛采用，能以较少的采样次数覆盖大范围模糊。

### 第三步：叠加（Additive Blending）

最终将模糊后的高亮图以**加法混合（Additive Blending）**方式叠加回原始帧：

$$C_{final} = C_{scene} + C_{bloom} \times intensity$$

其中 $intensity$ 是 Bloom 强度参数，通常在 0.5 ～ 2.0 之间调整。加法混合的物理意义明确：光线叠加是能量相加，不会导致颜色变暗，符合光线的实际传播规律。叠加后再经过色调映射（Tone Mapping）压缩到 LDR 显示范围，Bloom 的过曝部分会自然地饱和为接近白色的高亮晕光。

---

## 实际应用

**游戏场景中的 HDR Bloom**：在 Unreal Engine 5 中，Bloom 参数面板提供了 Threshold（默认值 -1，即对所有亮度生效）、Intensity（默认 0.675）、Size Scale 等独立控制项。美术人员可以针对不同场景（室内昏暗 vs 室外正午）分别调整，避免全局一刀切。

**UI 和特效中的 Bloom**：霓虹灯风格游戏（如《赛博朋克 2077》）大量依赖 Bloom 的颜色渗透效果。设计时会故意让 UI 元素或粒子颜色值超过 1.0（在 HDR 渲染管线中），使其在 Bloom 通道中产生彩色光晕，而非单一白光，从而还原霓虹灯的彩色漫射感。

**移动端的轻量方案**：受限于移动 GPU 带宽，移动端常使用单次 Kawase 模糊（仅 4 次采样）替代完整多尺度 Bloom，并将降采样目标控制在 1/4 分辨率，在性能与效果间取得平衡。

---

## 常见误区

**误区一：阈值越高，Bloom 越真实**

提高阈值只会让更少的区域产生光晕，对于亮度本身就在 LDR（0～1）范围内的场景，阈值设为 1.0 以上会导致完全没有任何 Bloom 效果。真实的 Bloom 效果依赖 HDR 渲染管线——颜色值必须允许超过 1.0，Bloom 才能有效区分"正常亮"与"极亮"。在 LDR 管线强行使用 Bloom 时，应降低阈值至 0.7～0.9。

**误区二：高斯模糊半径越大越好**

过大的模糊半径会导致高亮区域的光晕蔓延到大片非相关区域，形成"画面发灰"或"油腻感"。这是滥用 Bloom 的典型特征，在2005年前后曾是PS3/Xbox 360时代的常见画质问题。正确做法是结合 Soft Knee 和适度的 intensity 参数，让光晕在视觉上刚好可感知但不抢占主体。

**误区三：Bloom 必须在线性空间执行**

Bloom 的颜色提取和模糊必须在**线性光照空间**（Linear Space）中进行，而非 Gamma 校正后的空间。若在 Gamma 空间做模糊，暗部会被错误地"拉亮"，导致光晕颜色失真（偏白而非保留原始色相）。这一点与一般图像模糊操作不同，是 Bloom 接入渲染管线时最易出错的环节。

---

## 知识关联

Bloom 建立在**后处理概述**所介绍的帧缓冲读写与屏幕空间处理框架之上——它依赖渲染管线末端对已渲染帧的二次处理能力，以及 MRT（多渲染目标）或 ping-pong 帧缓冲技术来存储中间结果。

Bloom 通常与**色调映射（Tone Mapping）**紧密配合：正确的顺序是先执行 Bloom（在 HDR 空间叠加），再执行色调映射（将 HDR 压缩至显示范围），颠倒顺序会使光晕失去 HDR 的宽动态范围优势。此外，**景深（Depth of Field）**、**镜头光晕（Lens Flare）**等后处理效果常与 Bloom 共享高亮提取的中间结果，避免重复计算，这是现代渲染引擎组织后处理 Pass 时的常见优化策略。
