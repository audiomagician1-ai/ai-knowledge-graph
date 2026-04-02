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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 透射BRDF（BTDF与BSDF统一框架）

## 概述

透射BRDF，正式名称为**双向透射分布函数（BTDF, Bidirectional Transmittance Distribution Function）**，描述光线穿透介质界面时能量如何在各透射方向上分布。与BRDF描述反射出射辐射率不同，BTDF的入射方向 $\omega_i$ 与出射方向 $\omega_o$ 位于表面法线的**两侧**，即光线从正面射入、从背面射出。BTDF定义为：

$$f_t(\omega_i, \omega_o) = \frac{dL_o(\omega_o)}{L_i(\omega_i)\cos\theta_i\, d\omega_i}$$

其中 $\theta_i$ 是入射角，$L_i$ 是入射辐射率，$L_o$ 是透射出射辐射率。

历史上，BTDF作为独立概念由Nicodemus等人于1977年在NIST报告中与BRDF同时系统化定义。进入PBR时代后，Pharr与Humphreys在2004年出版的《Physically Based Rendering》中将BTDF正式纳入渲染器实现体系，推动了透明材质（玻璃、水、皮肤）的物理精确渲染。BTDF之所以重要，在于自然界中绝大多数非金属材质都同时具备反射和透射行为，仅用BRDF无法正确模拟玻璃、薄膜或半透明织物的外观。

## 核心原理

### BSDF统一框架：BRDF与BTDF的融合

**双向散射分布函数（BSDF）**是BRDF与BTDF的总称，将整个球面上的散射行为统一描述：

$$f_s(\omega_i, \omega_o) = f_r(\omega_i, \omega_o) + f_t(\omega_i, \omega_o)$$

其中 $f_r$ 为反射分量，$f_t$ 为透射分量。BSDF满足**广义亥姆霍兹互易律**（Helmholtz Reciprocity），但由于折射介质的折射率差异，BTDF的互易形式需要修正：

$$f_t(\omega_i, \omega_o) = f_t(\omega_o, \omega_i) \cdot \frac{\eta_o^2}{\eta_i^2}$$

其中 $\eta_i$ 和 $\eta_o$ 分别是入射侧和透射侧的折射率。这个 $\eta^2$ 修正因子是BTDF与BRDF在互易性上最本质的区别，忽略它会导致能量不守恒。

### 微表面折射模型

现代PBR中的BTDF基于Walter等人于**2007年EGSR**提出的**GGX微表面折射模型**（即"Microfacet Transmission"）。该模型将粗糙介质界面视为微观法线随机分布的微小平面集合，每个微平面按菲涅耳折射定律发生折射。完整的微表面BTDF公式为：

$$f_t(\omega_i, \omega_o) = \frac{|\omega_i \cdot \omega_h||\omega_o \cdot \omega_h|}{|\omega_i \cdot \mathbf{n}||\omega_o \cdot \mathbf{n}|} \cdot \frac{\eta_o^2 \cdot (1 - F) \cdot G \cdot D}{(\eta_i(\omega_i \cdot \omega_h) + \eta_o(\omega_o \cdot \omega_h))^2}$$

其中：
- $D$ 为法线分布函数（通常使用GGX/Trowbridge-Reitz）
- $G$ 为几何遮蔽函数（Smith Shadowing-Masking）
- $F$ 为菲涅耳透射系数（$1-F$ 即透射比例）
- $\omega_h$ 为折射半向量，计算公式为 $\omega_h = -\text{normalize}(\eta_i \omega_i + \eta_o \omega_o)$

折射半向量的方向与反射情形的半向量计算方式不同——反射半向量是入射与出射的平均方向，而折射半向量需按折射率加权，并指向与通常惯例相反的一侧。

### 菲涅耳方程与能量守恒

透射能量由**菲涅耳方程**约束。对于非极化光，透射系数 $T = 1 - F(\theta_i, \eta)$，其中 $F$ 由Schlick近似或精确的菲涅耳公式给出。能量守恒要求：

$$\int_{\Omega^+} f_r \cos\theta \, d\omega + \int_{\Omega^-} f_t \cos\theta \, d\omega \leq 1$$

在实现BSDF重要性采样时，需要以菲涅耳值 $F$ 作为概率权重，以 $F$ 的概率采样BRDF分量，以 $1-F$ 的概率采样BTDF分量，才能无偏地估计整体散射积分。

## 实际应用

**玻璃与透明塑料渲染**是BTDF最直接的应用场景。在Blender Cycles和Unreal Engine的"Glass"材质节点中，底层正是使用GGX微表面BTDF，粗糙度参数 $\alpha$ 直接控制GGX的 $D$ 函数宽度——$\alpha=0$ 时产生完美镜面折射（清玻璃），$\alpha=0.5$ 时产生模糊透射（磨砂玻璃）。

**薄表面（Thin-Surface）近似**是另一重要应用。对于厚度可忽略的薄玻璃或塑料膜，光线从正面射入后几乎不发生折射位移，此时BTDF可简化为：透射方向直接为 $-\omega_i$（穿透方向），省去折射方向计算，同时将折射率差异折叠进透射颜色（Tint）中。Disney Principled BSDF中的 `Transmission`参数结合`Thin`选项即采用此模式。

**皮肤与蜡烛的次表面散射**利用BTDF描述光线进入介质的初始透射事件。BSSRDF模型将BTDF作为光线进入皮肤的入口分量，再与体积散射积分结合，最终产生半透明感。

## 常见误区

**误区一：认为BTDF仅是"反向的BRDF"**。实际上，由于折射率变化导致的立体角压缩（$\eta^2$ 因子），BTDF在介质密度更大的一侧出射时辐射率会被放大，这是纯粹的物理效应而非bug。忽略 $\eta^2/\eta^2$ 修正将导致从水下向空气折射时画面明显偏暗。

**误区二：混淆折射半向量与反射半向量**。在代码实现中，折射半向量必须用 $\omega_h = -\text{normalize}(\eta_i \omega_i + \eta_o \omega_o)$ 计算，且需要确保 $\omega_h$ 与法线 $\mathbf{n}$ 同侧。若直接复用反射半向量公式，几何项 $G$ 和法线分布项 $D$ 的采样权重都会出错，产生错误的亮斑。

**误区三：在双面渲染中忽略折射率方向判断**。当光线从介质内部射出时，$\eta_i$ 和 $\eta_o$ 需要对调（例如玻璃内 $\eta_i=1.5$，空气中 $\eta_o=1.0$）。许多初学者用固定顺序硬编码折射率，导致全内反射（TIR）判断错误，在掠射角下出现不应有的透射分量。

## 知识关联

**前置概念**：BTDF建立在BRDF基础上，复用了微表面模型的 $D$（GGX法线分布）和 $G$（Smith几何项）组件，仅在半向量定义和 $\eta^2$ 修正上有所不同。理解Cook-Torrance BRDF中 $D$、$G$、$F$ 三项的物理含义是推导微表面BTDF公式的前提。

**横向关联**：BTDF与菲涅耳方程的结合产生了Disney Principled BSDF中的`Transmission`工作流，该工作流在电影级渲染（RenderMan、Arnold）和实时渲染（Unreal Engine 5的Substrate材质系统）中均有完整实现。Walter 2007年的GGX论文同时提出了GGX分布作为各向同性粗糙表面的标准，这既服务于反射BRDF，也服务于透射BTDF，二者共享同一套参数化方式（粗糙度 $\alpha$），使艺术家可以用统一的参数控制材质的反射模糊度与透射模糊度。