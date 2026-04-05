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
updated_at: 2026-03-30
---

# 泛光（Bloom）

## 概述

泛光（Bloom）是一种模拟真实相机镜头和人眼对强光反应的后处理效果，当场景中某个区域的亮度超过特定阈值时，其光芒会向周围扩散并渗透，产生发光晕圈。这种现象在物理上源于光学系统的衍射和散射：人眼的晶状体以及相机镜头在接收极强光线时，无法将其完美聚焦，导致光线溢出到邻近像素区域。Bloom 效果正是在屏幕空间对这一物理现象的近似重现。

Bloom 效果在早期游戏（如 2004 年《半条命 2》）中已有应用，但由于计算成本，早期实现较为粗糙。随着可编程着色器普及，基于高斯模糊的标准 Bloom 流程逐渐成为实时图形学的行业标准。现代游戏引擎（如 Unreal Engine 5 和 Unity）均内置 Bloom 后处理组件，并支持多种参数调节。

Bloom 之所以重要，在于它能以极低的额外成本（通常仅需 2–4 个额外渲染Pass）大幅提升画面的真实感和视觉冲击力，尤其在 HDR（高动态范围）渲染管线中，Bloom 与色调映射（Tone Mapping）配合，是展现高亮区域动态范围的关键手段。

---

## 核心原理

### 第一步：高亮提取（Bright Pass / Threshold Filter）

Bloom 流程的第一步是从帧缓冲中提取亮度超过阈值的像素。最简单的方法是对每个像素的亮度 L 进行判断：

$$C_{bright} = \max(C - threshold, 0)$$

其中 $C$ 是原始像素颜色，$threshold$ 是亮度阈值（典型值为 1.0，在 HDR 空间中亮度超过 1.0 的区域即为"过曝"区域）。然而硬截断会在亮区与暗区之间产生明显的锯齿状边界，因此更常用的是**软膝（Soft Knee）**曲线：

$$C_{bright} = C \cdot \frac{\max(L - threshold + knee, 0)^2}{4 \cdot knee + \epsilon}$$

其中 $knee$ 控制过渡区间的平滑程度（典型值 0.1–0.5），$\epsilon$ 防止除零。Soft Knee 能让亮度稍低于阈值的像素也参与部分 Bloom，避免硬边。

### 第二步：高斯模糊（Gaussian Blur）

提取出高亮图像后，对其施加高斯模糊以模拟光芒的扩散。高斯核的权重公式为：

$$G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2 + y^2}{2\sigma^2}}$$

由于二维高斯核可分离为两个一维卷积（水平 + 垂直各一次），实际实现中通常进行**两个 Pass 的可分离高斯模糊**，将一次 $n \times n$ 卷积的 $O(n^2)$ 操作降为 $O(2n)$。典型 Bloom 会对高亮图像应用 5–7 次迭代模糊，或者在降分辨率（通常降至原始分辨率的 1/4 甚至 1/8）的图像上进行，这是因为在低分辨率下模糊范围等效更大，同时节省带宽。

Unity URP 中的 Bloom 默认在 1/2 分辨率下执行 3 次下采样模糊，每次下采样分辨率减半，形成一个**模糊金字塔**，最后逐级上采样叠加，这一方法由 Marius Bjørge 在 2014 年 GDC 演讲中提出，被称为 **Dual Kawase Blur**（双重川濑模糊）的改进变体。

### 第三步：叠加（Composite / Additive Blend）

最终将模糊后的高亮纹理与原始帧缓冲图像进行**加法混合**：

$$C_{final} = C_{original} + intensity \cdot C_{bloom}$$

其中 $intensity$ 是 Bloom 强度参数（通常为 0.5–2.0），控制光晕的明亮程度。注意这里使用加法而非 Alpha 混合，因为光线叠加本质上是能量累加，加法混合在物理上更正确。过高的 $intensity$ 会导致整体画面过曝，因此在 HDR 管线中叠加后通常紧接着进行色调映射。

---

## 实际应用

**霓虹灯与发光 UI 元素**：在赛博朋克风格游戏（如《赛博朋克 2077》）中，霓虹灯管、发光文字等 UI 元素的材质 Emissive 强度会被设置为大于 1.0 的 HDR 颜色，触发 Bloom 阈值后产生强烈光晕，视觉上极具冲击力。材质的自发光颜色设置为 `(3.0, 0.0, 1.5)` 这样超过标准范围的 HDR 值，是常见技巧。

**武器与爆炸特效**：枪口焰、爆炸中心等瞬时高亮区域天然满足 Bloom 阈值，无需额外处理即可产生闪光感。美术人员可以通过提高粒子系统的 Emission 颜色强度（而非改变粒子大小）来控制 Bloom 范围。

**白天场景中的太阳与天空**：天空盒中太阳方向的像素亮度极高，在 Bloom 处理后会向周围扩散，模拟真实镜头的耀斑感。需要注意的是，若天空整体亮度过高（如 HDR 全白天），则需要精心调整阈值，否则全屏 Bloom 会破坏画面细节。

---

## 常见误区

**误区一：Bloom 阈值越低越好，能让画面更"发光"**

降低阈值会使更多像素参与 Bloom，导致低亮度物体（如普通木箱、地板）也产生光晕，完全破坏真实感。正确做法是将阈值保持在 HDR 空间的 1.0 附近，仅让真正"过曝"的区域发光，其余区域通过提高材质 Emissive 值来触发 Bloom，而不是降低全局阈值。

**误区二：Bloom 就是把图像模糊一下再叠加，分辨率无所谓**

在全分辨率下对高亮图进行高斯模糊，不仅计算代价高，而且模糊半径受限（因为大半径的高斯核权重随距离指数下降，很快趋近于零，效果不明显）。利用下采样金字塔，可以用相同的卷积核尺寸（如 3×3 或 5×5）在不同分辨率层级产生不同尺度的扩散，叠加后形成更自然的多尺度光晕，这是单层全分辨率模糊无法做到的。

**误区三：Bloom 效果在 SDR（LDR）管线中与 HDR 管线中没有区别**

在 SDR 管线中，像素颜色被钳制在 `[0, 1]`，无法区分亮度为 0.9 的"普通亮"与物理上应该是 5.0 的"极亮"——两者都被截断为近似值，Bloom 阈值很难精准区分真正需要发光的区域。HDR 管线保留了完整的亮度动态范围，Bloom 阈值在此空间中才能准确筛选出物理意义上的强光区域，效果更加精准且可控。

---

## 知识关联

**前置知识**：理解 Bloom 需要掌握后处理的基本框架——即渲染结果先写入帧缓冲纹理，再经过一系列屏幕空间 Pass 处理后输出。Bloom 是最典型的多 Pass 后处理效果，其"提取→模糊→叠加"三步结构在后处理概述中讲解的离屏渲染（Offscreen Rendering）和渲染纹理（Render Texture）机制是前提。

**延伸方向**：Bloom 的高亮提取逻辑与色调映射（Tone Mapping）紧密耦合，在 HDR 渲染管线中两者必须以正确顺序配合——通常 Bloom 在 Tone Mapping 之前处理，以保证 HDR 亮度的正确性。此外，Bloom 的模糊Pass 所使用的高斯核与景深（Depth of Field）效果的散焦模糊共享技术基础，学习景深效果时可直接复用 Bloom 的模糊实现。Kawase 模糊等优化算法也是进一步学习高性能后处理时的重要参考。