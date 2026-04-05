---
id: "cg-ndf"
concept: "法线分布函数"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 法线分布函数

## 概述

法线分布函数（Normal Distribution Function，NDF）描述微表面模型中，朝向恰好与半角向量 **h** 对齐的微表面所占的统计比例。在 Cook-Torrance BRDF 公式 `f_r = D(h)·G(l,v)·F(v,h) / (4·(n·l)·(n·v))` 中，D(h) 即法线分布函数项，它直接控制高光波瓣的形状与宽窄。该函数的值域为非负实数，且必须满足归一化约束：对半球面积分后乘以余弦因子等于 1，即 `∫ D(h)(n·h) dω = 1`。

NDF 的理论基础来自 1967 年 Torrance 和 Sparrow 对金属表面光散射的物理研究，他们将表面抽象为大量随机朝向的微小镜面（microfacet）。1977 年 Blinn 将该框架引入计算机图形学，提出了第一个实用的 NDF 形式。此后 Beckmann（1963 年，源自雷达散射领域）与 GGX（2007 年由 Walter 等人提出）相继成为行业主流，三者构成了当今实时与离线渲染中 NDF 的核心选项。

选择合适的 NDF 直接影响材质的视觉真实度：错误的 NDF 会导致金属高光"太圆太软"或塑料感过强，尤其在掠射角（grazing angle）下的高光拖尾表现差异显著。GGX 因其更长的高光尾部而在真实材质匹配上优于 Beckmann，这一差距在粗糙度 roughness > 0.4 时肉眼可辨。

---

## 核心原理

### Blinn-Phong NDF

Blinn-Phong NDF 是最早的解析形式：

```
D_Blinn(h) = ((α+2) / 2π) · (n·h)^α
```

其中 α 为光泽度指数（shininess），与感知粗糙度 r 的换算关系约为 `α = 2·r^(-2) - 2`。该函数在数学上简单，但它的高光波瓣在低粗糙度时能量集中过于均匀，缺乏真实材质在掠射角应有的亮度突起。Blinn-Phong NDF **不满足形状不变性**（shape-invariant），即对粗糙各向异性材质无法通过简单参数变换推广，这是它被逐渐淘汰的根本原因。

### Beckmann NDF

Beckmann NDF 来自高斯随机过程模型，假设微表面坡度（slope）服从二维高斯分布：

```
D_Beckmann(h) = exp(-(tan²θ_h) / α²) / (π · α² · cos⁴θ_h)
```

其中 θ_h 是半角向量与宏观法线的夹角，α 为粗糙度参数（即表面坡度的均方根值 RMS slope）。Beckmann 满足形状不变性，因此可以方便地扩展到各向异性版本。然而它的高斯坡度假设导致尾部衰减过快——在 `θ_h > 45°` 的区域，Beckmann 的 D 值比真实金属测量值低 1-2 个数量级，表现为高光边缘"切断"感。

### GGX（Trowbridge-Reitz）NDF

GGX 由 Walter 等人在 2007 年的 EGSR 论文中提出，其数学形式为：

```
D_GGX(h) = α² / (π · ((n·h)²·(α²-1) + 1)²)
```

其中 α = roughness²（Disney 约定，将感知线性度从 0 映射到 1）。GGX 的关键特征是**幂次为 2 的有理函数**而非指数函数，这使其尾部以 `θ_h^(-4)` 的速率缓慢衰减（Beckmann 为指数衰减），与铝、铜、不锈钢等材质的实测 BRDF 数据吻合度更高。GGX 同样满足形状不变性，其各向异性扩展只需将 α 拆分为 α_x 和 α_y 两个方向的粗糙度即可。

在实时渲染中，GGX NDF 的 Epic Games 简化实现（UE4，2013 年）将 α = roughness²，使粗糙度滑块在视觉上近似线性，这一约定已成为 PBR 管线事实标准。

### 归一化约束与能量守恒

三种 NDF 均需满足以下约束以保证物理正确：

```
∫_Ω D(h) · (n·h) · dω_h = 1
```

若 NDF 不满足此约束，则高光项总能量可能超过 1，违反能量守恒。Blinn-Phong 中的前置系数 `(α+2)/2π` 正是为此归一化而存在。Beckmann 和 GGX 在推导时已内嵌归一化，但在数值实现中需注意当 `n·h ≈ 0` 时的除零保护。

---

## 实际应用

**游戏引擎选型**：Unity HDRP 和 Unreal Engine 4/5 均默认使用 GGX NDF，参数 roughness 直接输入后引擎内部计算 `α = roughness²`。美术人员在调节金属球高光时，roughness = 0.0 产生完美镜面，roughness = 0.5 时 GGX 的高光拖尾使球面边缘仍可见明亮反光，而 Beckmann 在同等参数下边缘已接近黑色。

**离线渲染与材质匹配**：在 Mitsuba 或 PBRT 等离线渲染器中，当需要拟合实测 BRDF 数据（如 MERL 数据库中的 100 种材质）时，GGX 对铝、镍等金属的拟合误差比 Beckmann 平均低约 30%，主要差距出现在 `θ_h > 60°` 的高光尾部区域。

**各向异性材质**：拉丝金属（brushed metal）需要各向异性 NDF。GGX 各向异性版本为：`D_GGX_aniso = 1 / (π·α_x·α_y·((t·h/α_x)²+(b·h/α_y)²+(n·h)²)²)`，其中 t 为切线方向，b 为副切线方向。Blinn-Phong 由于缺乏形状不变性，无法用类似方式扩展。

---

## 常见误区

**误区一：roughness 参数在不同 NDF 之间通用**。Beckmann 的 α 是坡度均方根值，GGX 的 α 通常等于 roughness²，两者含义不同。将 Beckmann 的 α=0.3 直接移植到 GGX，会得到更锐利的高光，因为 GGX 的等效"视觉粗糙度"约为 `sqrt(α) ≈ 0.55`。切换 NDF 时必须重新校准参数。

**误区二：GGX 总是最佳选择**。对于布料、皮肤等具有前向散射峰（forward-scattering lobe）或双高光叶（dual-lobe）特征的材质，单个 GGX 叶拟合效果很差。布料通常使用 Charlie NDF（基于正弦函数的分布）或 Ashikhmin 模型，皮肤则需要多层次表面散射配合，单靠 NDF 无法解决。

**误区三：NDF 越复杂精度越高**。GTR（Generalized Trowbridge-Reitz，Disney 2012）引入可调幂次参数 γ，当 γ=2 时退化为 GGX，γ=∞ 退化为 Beckmann。但 GTR 在 γ≠2 时不满足形状不变性，导致对应的 Smith G 项难以解析求解，在实时渲染中反而引入误差更大的近似，实用价值反不及标准 GGX。

---

## 知识关联

学习 NDF 需要已掌握 Cook-Torrance 模型的整体框架，明白 D(h) 只是 BRDF 分母和三个主项之一，孤立地调大 D 值会破坏与 G（几何遮蔽）项的联动——Smith G 项的推导本身依赖与 D(h) 相同的粗糙度假设，例如 GGX 的 Smith G₁ 为 `G₁(v) = 2(n·v) / ((n·v)(1+sqrt(1+α²·tan²θ_v)))`，必须与 GGX NDF 配套使用而不能混用 Beckmann 的 D 与 GGX 的 G。

在掌握 NDF 之后，进阶方向是多次散射 NDF 修正（Heitz 2016 年的 Multiple-Scattering Microfacet BSDF），该工作指出单次散射假设在高粗糙度（roughness > 0.6）时会损失 10%-40% 的能量，需要通过补偿项（如 Kulla-Conty 近似）恢复能量守恒，而补偿项的形状同样由所选 NDF 决定。