---
id: "cg-energy-conservation"
concept: "能量守恒"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# 能量守恒（PBR材质中的多散射补偿与校正）

## 概述

在基于物理的渲染（PBR）框架中，能量守恒要求材质反射的总光能量不得超过入射光能量。具体表现为：对于任意入射方向 $\omega_i$，BRDF 在整个上半球的积分（即方向半球反射率）必须满足 $\int_\Omega f_r(\omega_i, \omega_o) \cos\theta_o \, d\omega_o \leq 1$。这一约束在物理上对应"光不能凭空产生"——粗糙表面不允许对所有出射方向同时产生高亮度响应。

经典 Cook-Torrance 微面元模型在引入菲涅耳项 $F$、法线分布函数 $D$、遮蔽-遮挡函数 $G$ 之后，**单次散射**路径下勉强满足能量守恒。然而研究表明，当表面粗糙度（roughness）较高时，微面元之间的**多次散射**（multi-scattering）贡献不可忽视。Heitz 等人在 2016 年的 EGSR 论文《Multiple-Scattering Microfacet BSDFs with the Smith Model》中首次系统量化了这一损失：粗糙度 $\alpha = 0.9$ 时，被单散射模型忽略的能量可高达入射光的 **40% 以上**，导致高粗糙度金属表面在渲染结果中呈现出不物理的"暗化"伪像。

能量守恒校正的意义不仅在于视觉正确性，还直接影响材质在路径追踪积分中的方差与收敛速度。若 BRDF 违反守恒约束，蒙特卡洛估计器将产生系统性偏差，无论增加样本数量都无法消除。

## 核心原理

### 单散射下的能量损失机制

Cook-Torrance 的镜面 BRDF 写作：

$$f_r(\omega_i, \omega_o) = \frac{F(\omega_i, h) \cdot D(h) \cdot G_2(\omega_i, \omega_o)}{4 \cos\theta_i \cos\theta_o}$$

其中 $G_2$ 为 Smith 联合遮蔽-遮挡函数。$G_2$ 的作用是剔除被相邻微面元遮挡的光线，但这些被遮挡的光线并非消失——它们在微面元之间发生二次乃至多次反射，最终仍有部分能量离开表面。单散射模型直接丢弃这部分光线，造成能量损失。损失量随 $\alpha$（GGX 粗糙度参数）增大而单调递增，在 $\alpha \to 1$ 时最为显著。

### Kulla-Conty 补偿项

2017 年，Kulla 和 Conty 在 SIGGRAPH 课程中提出了一种实时可用的**能量补偿方法**（Kulla-Conty Approximation）。其核心思路是预计算单次散射的**方向半球反射率**：

$$E(\mu) = \int_0^{2\pi}\int_0^{\pi/2} f_r \cos\theta \sin\theta \, d\theta \, d\phi$$

其中 $\mu = \cos\theta_i$。缺失的能量比例为 $1 - E(\mu)$，补偿 BRDF 被构造为：

$$f_{\text{ms}}(\omega_i, \omega_o) = \frac{(1-E(\mu_i))(1-E(\mu_o))}{\pi(1 - E_{\text{avg}})}$$

式中 $E_{\text{avg}} = 2\int_0^1 E(\mu)\mu \, d\mu$ 为对所有入射方向的余弦加权平均反射率。这两张查找表（$E(\mu, \alpha)$ 和 $E_{\text{avg}}(\alpha)$）通常以 $32\times32$ 分辨率预积分后存储为纹理，运行时仅需两次 texture fetch 即可完成补偿。

### 有色金属的能量守恒补偿

对于导体材质，菲涅耳项 $F$ 携带颜色信息（复数折射率 $\tilde{n} = n + ik$），导致不同波长的反射率各异。Kulla-Conty 方法需要额外引入**平均菲涅耳颜色**：

$$f_{\text{avg}} = \frac{\int_0^1 F(\mu) E(\mu) \mu \, d\mu}{\int_0^1 E(\mu) \mu \, d\mu}$$

补偿项颜色被缩放为 $f_{\text{avg}}^k$（$k$ 为散射次数），这样有色金属在高粗糙度下仍能在补偿光中保留正确的色调偏移，而非退化为白色。

## 实际应用

**虚幻引擎5（UE5）的实现**：UE5 的 Lumen 和 Substrate 材质系统采用了 Kulla-Conty 补偿，预积分表以 $64\times64$ 分辨率存储，支持各向异性 GGX（额外引入切线方向粗糙度 $\alpha_t$）。在 Substrate 中，每个材质层的补偿项独立计算后叠加，确保分层材质整体仍满足守恒约束。

**离线渲染器（如 Arnold、RenderMan）**：这类渲染器使用路径追踪直接模拟多次散射，不依赖 Kulla-Conty 近似。Arnold 4.0 引入的 `standard_surface` 着色器通过递归追踪微面元间光线来精确处理多散射，代价是较高粗糙度下每像素需要额外 3-8 条间接光线才能收敛。

**车漆与磨砂金属材质**：汽车车漆的透明涂层（clearcoat）下方的金属底层粗糙度通常在 $\alpha = 0.6 \sim 0.8$ 范围内，不做多散射补偿会使反光区域边缘出现明显的能量凹陷（energy dip），正是 Kulla-Conty 方案在产品可视化领域被广泛采用的主要动机。

## 常见误区

**误区一：认为 $G$ 函数已经保证能量守恒**。$G_2$（Smith 遮蔽函数）确实通过剔除几何遮挡的微面元避免了能量"凭空增加"，但它同时也剔除了本应参与多次散射后最终逸出的光线。$G_2$ 保证的是"不超过1"，而非"恰好等于1"——两者之间的差值正是多散射补偿要填补的部分。误认为加入 $G_2$ 就完成了守恒校正，会导致忽略高粗糙度下 10%~40% 的能量损失。

**误区二：漫反射项不需要能量守恒校正**。Lambert 漫反射模型的 BRDF 恒为 $f_d = \rho/\pi$（$\rho$ 为反照率），对于 $\rho \leq 1$ 的材质，Lambert 本身满足守恒约束，因此这一说法表面上成立。但在镜面与漫反射**联合**使用时，必须用 $(1-F)$ 因子对漫反射项做菲涅耳加权，否则总反射率将超过1。Oren-Nayar 模型通过引入粗糙度参数 $\sigma$（单位为度，典型值 20°~34°）修正了漫反射的相互遮蔽，但同样存在与单散射漫射模型类似的能量损失问题，需要类似的预积分补偿。

**误区三：Kulla-Conty 补偿与菲涅耳效果冲突**。补偿项 $f_{\text{ms}}$ 并非直接叠加到原始 BRDF 上，而是作为**附加分量**，其总量受 $1 - E(\mu_i)$ 和 $1 - E(\mu_o)$ 双重限制。这意味着补偿量在低粗糙度（$\alpha < 0.3$）时接近零，不会破坏材质在光滑区域的菲涅耳高光轮廓，二者在数学上相互正交。

## 知识关联

**前置概念——Cook-Torrance 模型**：能量守恒校正直接针对 Cook-Torrance 单散射 BRDF 的已知缺陷展开。理解 $D$、$G$、$F$ 各项的物理含义是量化能量损失来源的前提——$D$ 控制微面元朝向分布，$G$ 控制几何遮蔽，正是 $G$ 对被遮蔽微面元的处理方式引入了能量损失。

**后续概念——材质分层**：多层材质（如透明涂层 + 金属底层）要求每一层的能量输入等于上层透射的输出。若底层 BRDF 不满足守恒约束，层间能量传递的物理一致性将被破坏。Kulla-Conty 补偿在分层框架中须对每层独立应用，并在层间接口处用透射率 $T = 1 - R_{\text{layer}}$ 衔接，这正是材质分层系统设计时面临的核心挑战之一。