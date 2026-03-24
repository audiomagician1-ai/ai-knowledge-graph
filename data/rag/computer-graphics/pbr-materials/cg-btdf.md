---
id: "cg-btdf"
concept: "透射BRDF"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 透射BRDF（BTDF与BSDF统一框架）

## 概述

透射BRDF在术语上是一个有意思的悖论——严格来说，描述透射现象的函数叫做**BTDF（Bidirectional Transmittance Distribution Function，双向透射分布函数）**，而非BRDF。两者共同构成了**BSDF（Bidirectional Scattering Distribution Function，双向散射分布函数）**这一统一框架：BSDF = BRDF + BTDF。BRDF仅处理反射半球（法线同侧），而BTDF处理折射半球（法线异侧），BSDF则覆盖整个球面的光散射行为。

BTDF的理论基础来源于Helmholtz互易原理和能量守恒。1967年，Nicodemus正式给出了BRDF的数学定义，而BTDF作为其自然对偶被随之提出。两者形式相似：BTDF定义为出射透射辐亮度与入射辐照度之比，单位同为 sr⁻¹。在玻璃、水、薄膜等透明或半透明材质的物理渲染中，仅使用BRDF会导致透射效果完全缺失，因此BSDF是渲染真实感透明物体的必要工具。

需要特别注意的是，BTDF在数学上**不满足与BRDF相同形式的互易性**。BRDF满足 f_r(ωᵢ→ωₒ) = f_r(ωₒ→ωᵢ)，但BTDF由于折射率差异，满足的是修正形式：f_t(ωᵢ→ωₒ) · nᵢ² = f_t(ωₒ→ωᵢ) · nₒ²，其中nᵢ和nₒ分别是入射侧和出射侧的折射率。

---

## 核心原理

### 1. 微表面折射模型（Microfacet Transmission）

类比反射的微表面BRDF，透射的微表面BTDF由Walter等人在2007年的论文《Microfacet Models for Refraction through Rough Surfaces》中正式提出，是目前PBR管线中使用最广泛的透射模型。其完整公式为：

$$f_t(\omega_i, \omega_o) = \frac{|\omega_i \cdot \mathbf{h}_t|\ |\omega_o \cdot \mathbf{h}_t|}{|\omega_i \cdot \mathbf{n}|\ |\omega_o \cdot \mathbf{n}|} \cdot \frac{n_o^2 \cdot (1 - F) \cdot G \cdot D}{(n_i(\omega_i \cdot \mathbf{h}_t) + n_o(\omega_o \cdot \mathbf{h}_t))^2}$$

其中 **hₜ** 是折射微表面法线（由Snell定律确定），F是菲涅尔透射项（1-反射菲涅尔值），G是Smith遮蔽函数，D是法线分布函数（通常使用GGX/Trowbridge-Reitz分布）。分母中的 (nᵢ+nₒ)² 项是BTDF与BRDF分母的关键区别，由折射半矢量的雅可比变换产生。

### 2. 折射半矢量的特殊性

在BRDF中，半矢量 **h** = normalize(ωᵢ + ωₒ)，始终位于反射半球。而在BTDF中，折射半矢量定义为：**hₜ** = -normalize(nᵢ·ωᵢ + nₒ·ωₒ)，它指向入射介质一侧，且其方向由折射率比值 η = nᵢ/nₒ 直接影响。当η=1（折射率相同）时，hₜ退化到表面切面方向，意味着光线直穿而过不发生偏折。在实际实现中，必须确保 **hₜ** 与 ωᵢ 在法线同侧，否则需要翻转符号，这是初学者容易踩坑的地方。

### 3. 能量守恒与菲涅尔分配

完整的BSDF必须在反射和透射之间正确分配能量，由菲涅尔方程决定：

- 反射权重：F(ωᵢ, **h**)（Schlick近似：F₀ + (1-F₀)(1-cosθ)⁵）
- 透射权重：1 - F(ωᵢ, **h**)

对于电介质（玻璃的典型折射率n=1.5，F₀ ≈ 0.04），在法向入射时仅4%能量被反射，96%透射；而在掠射角（θ接近90°）时几乎全反射。金属材质由于消光系数k>>0，透射项趋于0，因此金属材质无需BTDF。在Disney BSDF（2015年提出）中，通过"transmission"参数在0到1之间插值控制BRDF与BTDF的混合比例。

### 4. 薄表面近似与体积透射

**薄表面模型（Thin Surface Approximation）**假设介质厚度趋近于0，光线折射后立即从背面射出，无需追踪内部折射偏移。此模型适用于窗玻璃、气泡薄膜等场景，实现简单且计算开销低。相比之下，**厚介质模型**需要追踪光线在介质内部的路径，并结合Beer-Lambert定律处理体积吸收：I = I₀ · e^(-μₐ · d)，其中μₐ是吸收系数，d是光线在介质内传播的距离。这种吸收效应使得彩色玻璃呈现随厚度变化的颜色饱和度。

---

## 实际应用

**玻璃材质渲染**是BTDF最直接的应用场景。在Unreal Engine 5的材质系统中，通过将Shading Model设置为"Thin Translucent"或使用折射节点，内部调用的正是Walter的微表面BTDF。粗糙度参数控制GGX的α值，α=0时对应完美透明玻璃（镜面折射），α=0.5时产生磨砂玻璃的模糊透射效果。

**钻石切割面的色散**需要对不同波长使用不同折射率：钻石对红光（700nm）折射率约2.410，对紫光（400nm）约2.465。在光谱渲染中，针对每个波长采样独立的BTDF得到色散效果，这也是钻石产生彩虹光芒的物理原因。

**皮肤与蜡的次表面散射预处理**也涉及BTDF：光子先以BTDF进入皮肤表面，在皮下组织经历多次散射（由单独的体积散射模型处理），再以BTDF从不同位置射出。因此BTDF是次表面散射（SSS）管线的入口和出口函数。

---

## 常见误区

**误区一：直接将BRDF的重要性采样方法用于BTDF。** BRDF的反射方向通过 ωₒ = 2(ωᵢ·**h**)**h** - ωᵢ 计算；BTDF的折射方向必须用Snell定律：ωₜ = (nᵢ/nₒ)ωᵢ + (nᵢ/nₒ·cosθᵢ - cosθₜ)**n**。若发生全内反射（cosθₜ²<0），没有折射方向，此时能量全部转移给BRDF项，必须单独处理这一边界条件，否则会出现能量凭空消失的artifact。

**误区二：认为BTDF不需要乘以 |cosθ| 项。** 渲染方程的正确形式中，所有BSDF采样都需要乘以 |ωᵢ · **n**| 项。BTDF在折射方向 ωₒ 位于法线异侧，|ωₒ · **n**| 依然是正值（取绝对值），不能因为方向"穿过"表面就省略这一几何项，否则得到的辐照度积分在能量上会偏高。

**误区三：混淆薄表面和厚介质BTDF的适用场景。** 薄表面模型无法模拟玻璃球内部的焦散和颜色吸收随厚度的变化；而对汽车玻璃等几何上确实很薄的物体使用厚介质模型，会引入不必要的内部反弹采样开销且结果与薄表面模型差异极小。正确判据是：若物体厚度对可见折射偏移和Beer-Lambert吸收的影响在画面精度要求内可忽略，选薄表面；否则选厚介质+体积散射。

---

## 知识关联

**前置知识——BRDF基础：** BTDF的微表面结构（NDF、Smith G项）与BRDF完全共享同一套数学工具，GGX的D和G项在两者中形式相同，仅半矢量的计算方式不同。理解BRDF中的Cook-Torrance框架是推导Walter BTDF公式分母雅可比变换项的必要基础。菲涅尔方程在BRDF中决定镜面权重，在BSDF中同时决定反射与透射的能量分配比例，是连接两者的核心纽带。

**延伸方向：** BTDF向上延伸至**体积渲染（Volume Rendering）**，其中相函数（Phase Function，如Henyey-Greenstein）是BTDF在粒子介质中的类比；向左延伸至**光谱渲染**，需要对波长参数化折射率；向右延伸至**BSSRDF（双向次表面散射反射分布函数）**，
