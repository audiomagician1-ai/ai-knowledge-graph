---
id: "cg-disney-brdf"
concept: "Disney BRDF"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Disney BRDF

## 概述

Disney BRDF，全称 Disney Principled BRDF，是由 Brent Burley 在迪士尼研究院开发并于 2012 年 SIGGRAPH 课程"Physically-Based Shading at Disney"中正式发表的材质着色模型。该模型的核心设计目标是：用尽可能少的、对艺术家直观友好的参数，覆盖真实世界中从皮肤到金属、从织物到玻璃的绝大多数材质外观。

迪士尼在开发该模型之前，对 MERL 材质数据库中 100 种真实材质进行了系统测量和分析，归纳出这些材质在漫反射、镜面高光、菲涅尔响应等方面的统计规律，并以此为依据设计参数范围。这使得 Disney BRDF 虽然不是严格物理正确的模型，但其参数的每一个取值区间都有真实材质数据的支撑。

Disney BRDF 对图形学工业界的影响极为深远。Unreal Engine 4 的 PBR 管线、Substance Painter 的默认着色模型以及 Pixar 的 RenderMan 都以该模型为基础或直接采用其参数约定，使得"基于 Disney BRDF 的 PBR 工作流"成为整个影视与游戏行业的事实标准。

---

## 核心原理

### 参数系统设计

Disney BRDF 使用 **11 个归一化参数**（大多数取值范围为 [0, 1]），每个参数均有明确的物理或感知对应含义：

| 参数 | 范围 | 含义 |
|------|------|------|
| `baseColor` | RGB | 基础反照率 |
| `metallic` | 0–1 | 金属度 |
| `roughness` | 0–1 | 微表面粗糙度 |
| `subsurface` | 0–1 | 次表面散射近似强度 |
| `specular` | 0–1 | 非金属高光强度（替代 IOR） |
| `specularTint` | 0–1 | 高光向 baseColor 着色程度 |
| `anisotropic` | 0–1 | 各向异性程度 |
| `sheen` | 0–1 | 织物边缘光泽强度 |
| `sheenTint` | 0–1 | 光泽着色程度 |
| `clearcoat` | 0–1 | 清漆层强度 |
| `clearcoatGloss` | 0–1 | 清漆层光泽度 |

`specular=0.5` 对应 IOR=1.5，这是大多数电介质（塑料、皮肤、木材）的折射率，因此 0.5 是非金属材质的默认值。

### 漫反射项：改进的 Lambert

Disney 的漫反射项不直接使用 Lambertian 模型，而是引入了一个基于粗糙度的 Fresnel 修正，称为 **Disney Diffuse**：

$$f_d = \frac{\text{baseColor}}{\pi} \left(1 + (F_{D90} - 1)(1-\cos\theta_l)^5\right)\left(1 + (F_{D90} - 1)(1-\cos\theta_v)^5\right)$$

其中 $F_{D90} = 0.5 + 2 \cdot \text{roughness} \cdot \cos^2\theta_d$，$\theta_d$ 是半程向量与光线方向的夹角。这个修正使得粗糙材质在掠射角度呈现更强的漫反射亮度，与 MERL 数据库中真实材质的行为相吻合。

### 镜面反射项：GTR 分布函数

Disney 的高光项采用了自定义的 **GTR（Generalized Trowbridge-Reitz）** 法线分布函数，而非标准 GGX：

$$D_{GTR}(\theta_h) \propto \frac{1}{(\alpha^2 \cos^2\theta_h + \sin^2\theta_h)^\gamma}$$

当 $\gamma=2$ 时退化为标准 GGX（用于主高光层），当 $\gamma=1$ 时用于 clearcoat 层，生成更宽的高光尾部。这使得 clearcoat 层与主镜面层可以拥有不同的高光形状，分别描述汽车漆的底漆层和透明清漆层。

粗糙度到 $\alpha$ 的映射使用 $\alpha = \text{roughness}^2$，这是一个感知线性化处理——艺术家将 roughness 从 0.2 调到 0.4 的视觉变化量，与从 0.6 调到 0.8 的视觉变化量大致相同。

### 各向异性与 sheen

当 `anisotropic > 0` 时，粗糙度被拆分为两个方向的分量：
$$\alpha_x = \text{roughness}^2 / \sqrt{1 - 0.9 \cdot \text{anisotropic}}, \quad \alpha_y = \text{roughness}^2 \cdot \sqrt{1 - 0.9 \cdot \text{anisotropic}}$$

`sheen` 项是一个基于 $\cos\theta_d$ 的 Fresnel-like 项，专门用于模拟织物、天鹅绒等材质的边缘光泽，其峰值出现在切线方向，而非正对光源方向。

---

## 实际应用

**汽车漆材质**：`metallic=0`（底漆是电介质），`clearcoat=1.0`，`clearcoatGloss=0.9`，`roughness=0.1`，`baseColor` 设为目标颜色。清漆层使用 $\gamma=1$ 的 GTR 产生宽而柔和的高光，底漆层的 roughness 可以适当调高来模拟珠光效果。

**人类皮肤**：`subsurface=0.6–0.8`，`specular=0.35`（对应皮肤 IOR≈1.4），`roughness=0.6`，`baseColor` 使用橙红色调。Disney BRDF 的次表面项是 Hanrahan-Krueger BRDF 的近似，并非真正的体积散射，但对于远景角色渲染已足够。

**拉丝金属**：`metallic=1.0`，`anisotropic=0.8`，`roughness=0.3`，并指定 tangent 方向对应拉丝纹理的切线。各向异性模型将在水平方向产生拉长的高光条带，与不锈钢拉丝表面的外观高度吻合。

**磨砂塑料**：`metallic=0`，`specular=0.5`，`roughness=0.7`，`specularTint=0`（保持高光为白色）。这是 Disney BRDF 参数空间中最"中性"的设置之一，也是验证渲染器实现是否正确的常用基准材质。

---

## 常见误区

**误区一：认为 metallic=1 的材质没有漫反射**  
正确理解：Disney BRDF 中，当 `metallic=1` 时，diffuse 项被乘以 `(1-metallic)=0`，漫反射贡献确实被完全消除，这符合金属不产生漫反射的物理事实。但误区在于：有些实现错误地将 `baseColor` 作为纯粹的反照率保留给漫反射，而在金属材质中，`baseColor` 实际上控制的是镜面反射的 F0 颜色（如金的金黄色高光就来自这里）。

**误区二：roughness=0 等同于完美镜面**  
Disney BRDF 中，roughness 经过 $\alpha = \text{roughness}^2$ 的映射后，$\alpha=0$ 在 GTR 分布函数中确实退化为 Dirac delta 函数，理论上是完美镜面。但在实际渲染中，roughness 极小值（如 0.02）会导致 PDF 采样极端困难，产生噪点，需要配合重要性采样或使用 roughness clamp（通常 clamp 到 0.04）。

**误区三：Disney BRDF 是能量守恒的**  
迪士尼团队在设计时明确指出，该模型**不保证能量守恒**——特别是漫反射的 Fresnel 修正项在某些角度组合下会导致输出能量超过输入。Unreal Engine 对此进行了修正，而 Substance Painter 的实现则额外引入了能量补偿项。这是使用原始 Disney BRDF 时必须清楚的局限性。

---

## 知识关联

**前置概念**：理解 BRDF 基础中的微表面理论（Microfacet Theory）是读懂 GTR 分布函数公式的前提，特别是 NDF、几何遮蔽项 G 以及菲涅尔方程 F 的含义——Disney BRDF 的镜面项同样采用 $f_s = \frac{DFG}{4(\omega_i \cdot n)(\omega_o \cdot n)}$ 的标准微表面框架，只是将 D 换成了 GTR。

**横向关联**：Disney BRDF 与 Cook-Torrance BRDF 的区别在于后者没有专为艺术家设计的参数归一化层，也没有 clearcoat、sheen 等用于特殊材质的附加项。与 Oren-Nayar 模型相比，Disney 的漫反射项更轻量但同样考虑了粗糙度对漫反射形状的影响。

**延伸方向**：Disney BRDF 在 2015 年被进一步扩展为 **Disney BSDF**，加入了透明折射项（`specularTransmission` 参数），用于玻璃、水晶等透明材质，并引入了薄层（thin surface）近似
