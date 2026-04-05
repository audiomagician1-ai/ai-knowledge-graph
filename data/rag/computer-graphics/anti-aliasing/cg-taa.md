---
id: "cg-taa"
concept: "TAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "research"
    title: "High-Quality Temporal Supersampling"
    authors: ["Brian Karis"]
    venue: "SIGGRAPH 2014 (Epic Games)"
    year: 2014
  - type: "research"
    title: "Temporal Reprojection Anti-Aliasing in INSIDE"
    authors: ["Mikkel Gjoel"]
    venue: "GDC 2016"
    year: 2016
  - type: "textbook"
    title: "Real-Time Rendering"
    authors: ["Tomas Akenine-Moller", "Eric Haines", "Naty Hoffman"]
    year: 2018
    isbn: "978-1138627000"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---


# TAA（时间性抗锯齿）

## 概述

TAA（Temporal Anti-Aliasing，时间性抗锯齿）是一种通过在连续多帧间累积亚像素采样信息来消除锯齿的抗锯齿技术。其核心思想是：单帧渲染时只取一个抖动偏移的采样点，但将当前帧与历史帧按权重混合，等效于在时间维度上实现多重采样（MSAA）的效果，而无需在单帧内消耗多倍的渲染带宽。

TAA 最早由 Brian Karis 在2014年 SIGGRAPH 的演讲《High-Quality Temporal Supersampling》中系统性地提出并推广，虚幻引擎4随后将其作为默认抗锯齿方案。此前工业界虽已有时间性累积的尝试，但 Karis 的方案将抖动采样、历史帧重投影和色彩裁剪三个机制整合为完整管线，成为现代游戏引擎 TAA 的基础范式。

TAA 之所以重要，在于它能以极低的单帧额外开销（主要是一次全屏后处理 pass）实现接近8x 甚至16x 超采样的视觉效果。对于延迟渲染管线而言，MSAA 的硬件实现代价极高，而 TAA 则与延迟渲染天然兼容，这使其成为 AAA 游戏中几乎无可替代的主流方案。

---

## 核心原理

### 抖动采样（Jitter Sampling）

TAA 在每一帧渲染时，会对投影矩阵施加一个亚像素级别的偏移（Jitter），使得当前帧的采样点在像素内部的位置发生变化。常用的抖动序列包括 **Halton 序列**（基底通常取2和3）和 **Interleaved Gradient Noise**。以 Halton(2,3) 序列为例，连续8帧的采样点会均匀分布在单个像素的 UV 空间 [0,1)×[0,1) 内，实现空间上的准随机覆盖。

投影矩阵的 Jitter 修改方式为：将 NDC 空间的偏移量 `(jx, jy)` 加入投影矩阵的第三列的 x、y 分量，具体公式为：

$$P'_{02} = P_{02} + \frac{2 \cdot j_x}{屏幕宽度},\quad P'_{12} = P_{12} + \frac{2 \cdot j_y}{屏幕高度}$$

这一偏移量在空间上不超过 ±0.5 像素，不会改变几何体的可见性，但足以让连续帧的采样覆盖不同的亚像素区域。

### 历史帧重投影与混合

当前帧计算完成后，TAA 需要将当前帧颜色与上一帧（历史帧）的颜色进行混合。混合公式为：

$$C_{out} = \alpha \cdot C_{current} + (1 - \alpha) \cdot C_{history}$$

其中 **α 通常取 0.1 左右**（即历史帧权重约为90%），这意味着理论上需要约 $\frac{1}{0.1} = 10$ 帧才能使新的几何信息完全稳定融入。为了让历史帧像素对应到当前帧的正确位置，TAA 读取 **速度缓冲（Velocity Buffer / Motion Vector）**，将历史帧中该像素在上一帧的屏幕坐标通过运动向量进行偏移重采样，这一过程称为 **重投影（Reprojection）**。

### 历史帧色彩裁剪（Neighborhood Clamping/Clipping）

重投影后的历史帧像素颜色可能与当前帧周围像素的色彩范围差异悬殊，直接混合会产生"鬼影（Ghosting）"。TAA 采用**邻域色彩裁剪**来抑制这一问题：采样当前像素的 3×3 邻域（共9个像素），计算其颜色的 AABB 包围盒（通常在 YCoCg 色彩空间中计算，因为该空间下 AABB 更紧凑），然后将历史帧颜色裁剪（Clip）或钳制（Clamp）到该包围盒内。

色彩裁剪比简单钳制更精确：它将历史帧颜色向 AABB 最近面投影，而非直接截断，能更好地保留颜色信息的方向性。

---

## 实际应用

**虚幻引擎4/5 的 TAA 实现**中，默认 α 值为 0.1，抖动序列使用 Halton(2,3) 的前8个样本循环。对于静止场景，累积8帧后的效果在视觉上接近 8xMSAA。UE5 在此基础上发展出了 TSR（Temporal Super Resolution），将 TAA 的历史帧累积思路扩展至超分辨率输出。

**Unity HDRP** 的 TAA 实现允许开发者独立调整 "Speed Rejection"（基于运动向量长度动态降低历史帧权重）和 "Jitter Frame Count"（默认8帧）。当像素的运动向量长度超过阈值时，系统会将 α 提升至接近1.0，强制使用当前帧数据以避免快速运动物体的拖影。

在**延迟渲染管线**中，TAA pass 通常安排在光照计算、景深、运动模糊之前，因为 TAA 需要未经后处理的线性光照值（HDR 空间），之后才做色调映射（Tone Mapping）。若顺序错误，在 LDR 空间做 TAA 会导致高亮区域的收敛行为异常。

---

## 常见误区

**误区一：α 值越小，抗锯齿效果越好**
降低 α（加大历史帧权重）确实能积累更多样本，使稳定画面更平滑，但代价是新出现的物体或快速移动的边缘需要更多帧才能收敛，鬼影持续时间更长。实际工程中需要在"稳定性"和"响应速度"之间折中，α = 0.1 是大多数引擎选择的经验值。

**误区二：TAA 可以完全依赖深度缓冲做重投影**
对于静态场景，用深度缓冲反推世界坐标再投影确实可行，但对于蒙皮动画、顶点动画、粒子系统等无法从深度缓冲中获取准确运动信息的物体，必须在几何 pass 中显式输出运动向量到速度缓冲，否则重投影坐标错误会直接导致鬼影。这是 TAA 对渲染管线的一项强制性要求。

**误区三：TAA 与 MSAA 效果等价**
TAA 在稳定静止画面时等效于时间维度的超采样，但 MSAA 在几何边缘处对每个样本独立执行深度/模板测试，能精确识别多边形边缘。TAA 的色彩裁剪机制会在边缘处引入轻微模糊，且对着色器内部的高频细节（如法线贴图产生的镜面高光闪烁）处理效果不如几何边缘。

---

## 知识关联

**前置知识**：理解抗锯齿概述中的"采样定理"和"重建滤波"是理解 TAA 为何需要抖动采样的基础——锯齿本质上是采样率不足导致的频谱混叠，TAA 通过时间维度扩充有效采样率来解决该问题。

**直接衍生问题**：TAA 的历史帧混合机制直接导致了 **TAA 鬼影**（重投影失败时的拖影）和 **TAA 锐度损失**（历史帧混合等效于低通滤波）两个核心缺陷，这两个概念是 TAA 优化工作的主要方向。**速度缓冲**是 TAA 正确运行的必要数据来源，而**抖动模式**（Halton、Sobol 等序列的选取）直接影响 TAA 的收敛质量。

**后续发展**：**DLSS**（深度学习超采样）在架构上继承了 TAA 的历史帧累积思路，但将色彩重建网络替换为 NVIDIA 训练的卷积神经网络，能在上采样的同时抑制鬼影并恢复锐度，是 TAA 技术路线的重要延伸。