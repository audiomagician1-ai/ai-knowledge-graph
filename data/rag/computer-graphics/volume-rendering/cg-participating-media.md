---
id: "cg-participating-media"
concept: "参与介质"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.394
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 参与介质

## 概述

参与介质（Participating Media）是指光线在穿越时会发生吸收（Absorption）、散射（Scattering）或自发光（Emission）的物质，包括烟雾、云层、牛奶、皮肤组织、大气等。与表面渲染中光仅在几何边界上发生交互不同，参与介质中光与物质的交互发生在三维体积内的每一个微元体积上，因此无法用单一的BRDF来描述其外观。

参与介质的数学化描述可追溯至20世纪初的辐射传输理论，物理学家Subrahmanyan Chandrasekhar在1950年出版的《辐射传输》（*Radiative Transfer*）中系统建立了辐射传输方程（Radiative Transfer Equation，RTE），这一方程后来被图形学研究者直接移植为体积渲染方程的理论基石。James Kajiya与Brian Von Herzen在1984年发表的论文《Ray Tracing Volume Densities》将RTE引入计算机图形学，首次实现了基于物理的体积渲染。

理解参与介质的意义在于：现实世界中几乎所有非真空的光传播路径都涉及参与介质效应。没有参与介质模型，渲染大气散射产生的丁达尔效应（Tyndall Effect）、云的多重散射、蜡烛火焰的体积光等现象在物理上均无法正确表达。

## 核心原理

### 四种光学现象与系数定义

参与介质通过四种基本物理过程影响穿越其中的辐射：

1. **吸收（Absorption）**：介质粒子将光能转化为热能，用吸收系数 $\mu_a$（单位：m⁻¹）描述，其物理含义是单位路径长度上被吸收的光能比例。
2. **外散射（Out-scattering）**：光子被偏转离开原方向，用散射系数 $\mu_s$ 描述。
3. **内散射（In-scattering）**：来自其他方向的光被散射进入当前光线方向。
4. **自发光（Emission）**：介质粒子本身发光，例如高温火焰。

消光系数（Extinction Coefficient）定义为 $\mu_t = \mu_a + \mu_s$，表示介质对光线的总衰减能力。单次散射反照率（Single-scattering Albedo）$\omega_0 = \mu_s / \mu_t$ 描述散射与总消光的比例：$\omega_0 = 1$ 表示纯散射介质（如白云），$\omega_0 = 0$ 表示纯吸收介质（如黑烟）。

### 体积渲染方程（VRE）

完整的体积渲染方程描述沿射线方向 $\mathbf{d}$ 从起点 $t_0$ 到终点 $t_1$ 的辐射积累：

$$L(\mathbf{x}, \mathbf{d}) = \int_{t_0}^{t_1} T(t_0, t) \left[ \mu_a(\mathbf{x}_t) L_e(\mathbf{x}_t, \mathbf{d}) + \mu_s(\mathbf{x}_t) \int_{S^2} f_p(\mathbf{x}_t, \mathbf{d}', \mathbf{d}) L(\mathbf{x}_t, \mathbf{d}') \, d\mathbf{d}' \right] dt$$

其中：
- $T(t_0, t) = \exp\!\left(-\int_{t_0}^{t} \mu_t(\mathbf{x}_s) \, ds\right)$ 是透射率（Transmittance），即Beer-Lambert定律在非均匀介质下的推广形式
- $L_e$ 是自发光辐射
- $f_p$ 是相函数（Phase Function），决定散射方向的分布
- $\int_{S^2} \cdots d\mathbf{d}'$ 是对全球面方向的积分，表示所有方向的内散射贡献

这一积分方程通常无解析解，需要数值方法求解。

### 透射率与光学深度

透射率 $T$ 的指数形式中，$\tau = \int_{t_0}^{t} \mu_t \, ds$ 称为光学深度（Optical Depth）或光学厚度。当 $\tau < 0.1$ 时介质被称为光学薄（Optically Thin），光线基本不受影响；当 $\tau > 3$ 时称为光学厚（Optically Thick），光线传播极为有限。云层的光学深度通常在 $\tau = 10 \sim 100$ 之间，这正是为何厚云层内部几乎看不到光源直接位置的原因。

对非均匀介质（Heterogeneous Media），$\mu_t$ 随空间位置变化，此时光学深度只能通过沿射线的数值积分（如步进采样）来估算。

## 实际应用

**大气渲染**：地球大气的瑞利散射（Rayleigh Scattering）和米氏散射（Mie Scattering）均是参与介质的具体实例。瑞利散射系数与波长的四次方成反比（$\mu_s \propto \lambda^{-4}$），这直接解释了天空为蓝色而日落为红色的现象。Nishita等人在1993年使用参与介质框架实现了第一个实时大气渲染模型。

**烟雾与云的离线渲染**：电影《奇异博士》（2016）中魔法烟雾效果使用了基于VRE的路径追踪体积渲染，Weta Digital的Manuka渲染器和Pixar的RenderMan均实现了完整的参与介质路径追踪，采用Delta追踪（Delta Tracking / Woodcock Tracking）算法处理异构密度场。

**医学体绘制**：CT/MRI数据的体绘制同样依赖参与介质模型，其中传递函数（Transfer Function）本质上是将体素密度值映射为局部的 $\mu_a$、$\mu_s$ 和 $L_e$。

**实时渲染近似**：游戏引擎中常用Ray Marching方法对VRE进行降维近似，Unreal Engine 5的体积雾使用3D纹理缓存光照，将散射计算的复杂度从每帧每射线降低为每帧一次体素化计算。

## 常见误区

**误区一：将参与介质等同于Beer-Lambert定律**。Beer-Lambert定律仅描述无散射的纯吸收介质中的指数衰减，是参与介质中 $\mu_s = 0, L_e = 0$ 时VRE的特殊退化形式。真实的烟雾、云、皮肤组织中散射效应同样重要，仅用Beer-Lambert定律处理会完全忽略内散射带来的次表面辉光和颜色偏移，例如用纯吸收模型渲染白云会得到全黑的结果而非白色。

**误区二：认为均匀介质（$\mu_t$ 为常数）的渲染等同于非均匀介质的渲染**。均匀介质的透射率有解析解 $T = e^{-\mu_t \cdot d}$，可在射线步进前直接计算终点。而非均匀介质必须逐步采样积分，且对采样间距非常敏感——若步长过大会产生明显的能量误差，无法用简单增大采样数量补偿，因为密度梯度尖锐区域需要自适应采样策略。

**误区三：认为单次散射已足够真实**。仅计算一次散射的模型无法再现云层内部的柔和漫射光（需要数十次乃至数百次散射），在 $\omega_0$ 接近1的高散射反照率介质（如新鲜积雪 $\omega_0 \approx 0.99$）中，忽略多重散射会导致亮度严重偏低，相差可达数个数量级。

## 知识关联

**与Beer-Lambert定律的关系**：Beer-Lambert定律是学习参与介质的直接前置知识，VRE中的透射率项 $T(t_0, t)$ 是Beer-Lambert定律从均匀、纯吸收介质到非均匀、含散射介质的完整推广，掌握指数衰减的物理意义是理解光学深度概念的基础。

**通向相函数**：VRE中的 $f_p$ 项是参与介质渲染的下一个核心概念——相函数描述散射方向的角分布，不同的相函数模型（各向同性、Henyey-Greenstein相函数、Mie散射相函数）直接决定介质的视觉外观特征，例如前向散射主导的云层与后向散射主导的大气气溶胶呈现出截然不同的光晕形状。

**通向体积阴影与异构体积**：参与介质的消光系数场一旦与方向光结合，就需要计算从光源到介质内部每一点的透射率，即体积阴影（Volume Shadow）问题。当介质的密度场由流体模拟或噪声函数生成时，便进入异构体积（Heterogeneous Volume）的处理范畴，需要专门的空间加速结构（如VDB稀疏体素格式）来高效存储和采样变化的 $\mu_t(\mathbf{x})$ 场。
