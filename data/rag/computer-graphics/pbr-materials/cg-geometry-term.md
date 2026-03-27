---
id: "cg-geometry-term"
concept: "几何遮蔽项"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
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


# 几何遮蔽项

## 概述

几何遮蔽项（Geometry Term，记作 G）是Cook-Torrance微表面BRDF中专门用于模拟微观表面自遮挡效应的分量。当光线从光源方向 **l** 照射微表面时，部分微小凸起会遮挡相邻区域（称为"阴影"，Shadowing）；同理，当反射光从视线方向 **v** 出射时，相邻凸起也会拦截部分出射光（称为"遮蔽"，Masking）。几何遮蔽项的数值范围严格限定在 [0, 1] 之间，0 表示完全遮蔽，1 表示无遮蔽。

该概念在1967年由Torrance和Sparrow在其物理光学论文中首次以解析形式引入图形学领域。1981年Cook与Torrance将其纳入完整的反射模型后，G 项的精确建模始终是PBR材质研究的难点。粗糙表面（粗糙度 α 接近1）时G项对最终渲染结果影响极为显著，而极光滑表面（α 趋近于0）时G项趋近于1，影响可忽略。

## 核心原理

### 单向Smith遮蔽函数 G₁

Smith于1967年推导出一种将法线分布函数（NDF）与几何遮蔽分离建模的框架。对于单个方向 **v**，Smith G₁ 函数定义为：

$$G_1(\mathbf{v}, \alpha) = \frac{2(\mathbf{n} \cdot \mathbf{v})}{(\mathbf{n} \cdot \mathbf{v}) + \sqrt{\alpha^2 + (1-\alpha^2)(\mathbf{n} \cdot \mathbf{v})^2}}$$

其中 α 是粗糙度参数（通常是艺术家输入粗糙度的平方，即 α = roughness²），**n** 为宏观表面法线。这个G₁专门配合GGX（Trowbridge-Reitz）NDF使用，两者在微表面统计假设上相互一致——均假设微表面高度服从正态分布，坡度分布服从GGX形式。

### 分离式与Height-Correlated双向模型

最简单的双向几何项是将入射和出射方向的G₁直接相乘：

$$G_{\text{separable}}(\mathbf{l}, \mathbf{v}, \alpha) = G_1(\mathbf{l}, \alpha) \cdot G_1(\mathbf{v}, \alpha)$$

然而这种分离式模型存在物理错误：它假设光线方向 **l** 的阴影函数与视线方向 **v** 的遮蔽函数在统计上完全独立。实际上，当 **l** 和 **v** 方向相近时，遭受阴影的微表面更有可能同时遭受遮蔽，两者存在正相关性。Height-Correlated模型（高度相关模型）正是为修正这一问题而设计的：

$$G_{\text{correlated}}(\mathbf{l}, \mathbf{v}, \alpha) = \frac{1}{1 + \Lambda(\mathbf{l}) + \Lambda(\mathbf{v})}$$

其中 Λ（Lambda）函数是Smith辅助函数，对于GGX NDF具体形式为：

$$\Lambda(\mathbf{v}) = \frac{-1 + \sqrt{1 + \alpha^2 \tan^2\theta_v}}{2}$$

θ_v 是 **v** 与表面法线的夹角。Height-Correlated版本在 **l** 与 **v** 夹角较小时能量损失更少，而分离式版本在相同条件下会过度压暗高光，产生不符合物理的"能量漏洞"。

### Schlick近似与实时渲染中的简化

Schlick在1994年提出了G₁的低成本近似公式，避免了平方根运算：

$$G_{\text{Schlick}}(\mathbf{v}, k) = \frac{\mathbf{n} \cdot \mathbf{v}}{(\mathbf{n} \cdot \mathbf{v})(1-k) + k}$$

其中 k 的取值因光照类型而异：直接光照使用 $k = \frac{(\alpha+1)^2}{8}$，IBL（基于图像的光照）使用 $k = \frac{\alpha^2}{2}$。这两种 k 的不同取法是为了在各自的积分域内最小化与Height-Correlated Smith G 的误差。实时渲染管线（如Unreal Engine 4）采用该近似，并将双向形式写为 $G = G_{\text{Schlick}}(\mathbf{l}, k) \cdot G_{\text{Schlick}}(\mathbf{v}, k)$，运算代价仅为两次Schlick G₁调用。

## 实际应用

在Unreal Engine 4的PBR管线中，材质粗糙度（Roughness）输入会先经过 α = roughness² 的重映射再传入几何遮蔽项，这一设计使粗糙度在感知上更加线性——粗糙度从0.5变化到1.0时，高光的明暗变化幅度与从0到0.5相近。若直接使用原始粗糙度值而不平方，低粗糙度区间高光会异常尖锐，高粗糙度区间变化迟钝。

在离线渲染器（如Arnold、RenderMan）中，通常直接使用Height-Correlated Smith G 的完整形式，因为其能更精确地保持能量守恒。实测数据表明，在掠射角（**v** 与法线夹角超过70°）情况下，分离式Smith G比Height-Correlated版本暗约15%~30%，这在车漆、皮革等掠射高光明显的材质上会产生明显误差。

## 常见误区

**误区一：认为 G 项越大越亮，因此应尽量使其接近1**
G 项的核心职责是维持能量守恒，而非单纯提亮。当 G 过大（即忽略遮蔽）时，BRDF在掠射角积分后能量超过入射能量，导致亮度物理错误。正确的G项会在高粗糙度的掠射方向适当压暗，这恰好对应真实材质在该方向的能量损失行为。

**误区二：Schlick近似形式与Height-Correlated Smith G 可以随意互换**
Schlick近似本质上是分离式结构（两个G₁相乘），并非真正的Height-Correlated模型。在金属材质的掠射高光中，两者差异肉眼可见。若使用Height-Correlated模型的 Λ 函数形式，则不能再套用Schlick的 k 值公式，两套参数体系不可混用。

**误区三：G 项与法线贴图的凸凹细节等价**
法线贴图修改的是宏观可见的法线方向，影响漫反射和高光的方向分布；而 G 项建模的是亚像素级别的微表面统计遮蔽，与贴图分辨率无关。即使将法线贴图精度提升到4K，仍无法替代 G 项对能量守恒的修正作用。

## 知识关联

几何遮蔽项是Cook-Torrance BRDF公式 $f_r = \frac{D \cdot F \cdot G}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$ 中的G因子，与法线分布函数D（GGX/Beckmann）和菲涅尔项F共同构成完整的镜面反射BRDF。理解G项需要先掌握Cook-Torrance模型中微表面假设（即宏观表面由无数随机朝向的微小镜面组成），因为G₁中的Λ函数直接由NDF的斜率分布积分推导而来——更换NDF（如从GGX换为Beckmann）必须同步更换对应的Λ公式，否则统计模型内部不一致。

从G项延伸出的高级方向包括多次散射BRDF修正（如Heitz 2016年提出的随机游走微表面模型），该方向专门解决单次散射假设下G项无法捕捉多次微表面反弹导致的能量损失问题，在高粗糙度金属材质上可额外恢复约10%的能量。