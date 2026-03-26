---
id: "cg-beer-lambert"
concept: "Beer-Lambert定律"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Beer-Lambert定律

## 概述

Beer-Lambert定律（又称比尔-朗伯定律）描述了光线穿越均匀吸收介质时，其强度随传播距离呈指数衰减的规律。该定律由德国物理学家奥古斯特·比尔（August Beer）和约翰·亨利·朗伯（Johann Heinrich Lambert）分别在1852年和1760年独立研究提出，后合并为统一的数学表达式。

在体积渲染领域，Beer-Lambert定律是最基础的光衰减模型，用于描述云雾、烟尘、水体等参与介质对光线的吸收效应。不同于表面渲染中光与物体的单次交互，体积渲染需要沿光线路径对连续分布的粒子群进行积分，Beer-Lambert定律给出了这一积分在纯吸收介质条件下的解析解，避免了数值积分的计算代价。

## 核心原理

### 基本公式与变量含义

Beer-Lambert定律的核心公式为：

$$I(d) = I_0 \cdot e^{-\mu_a \cdot d}$$

其中：
- $I_0$ 为入射光强度（进入介质前的初始值）
- $I(d)$ 为光线穿透距离 $d$ 之后的剩余强度
- $\mu_a$ 为**吸收系数**（absorption coefficient），单位为 $\text{m}^{-1}$ 或 $\text{cm}^{-1}$，表示单位长度内介质对光子的吸收能力
- $d$ 为光线在介质中的传播距离

从公式可见，当 $\mu_a \cdot d = 1$ 时，光强衰减至原来的 $1/e \approx 36.8\%$；当 $\mu_a \cdot d = 4.6$ 时，光强已不足原始值的 1%。

### 光学深度（Optical Depth）

将指数上的乘积 $\tau = \mu_a \cdot d$ 称为**光学深度**（Optical Depth 或 Optical Thickness）。光学深度是无量纲量，是介质"厚度"的一种光学度量，与物理厚度和介质密度的乘积成正比。

对于密度非均匀的介质（真实烟雾、云层中密度随位置变化），光学深度需要沿光线路径积分：

$$\tau = \int_{t_0}^{t_1} \mu_a(t) \, dt$$

此时透射率（Transmittance）定义为：

$$T = e^{-\tau} = \exp\!\left(-\int_{t_0}^{t_1} \mu_a(t)\,dt\right)$$

透射率 $T \in [0, 1]$，表示光线从 $t_0$ 到 $t_1$ 这段路径未被吸收的比例，是体积渲染中合成最终颜色时的关键权重。

### 与Ray Marching的结合

在Ray Marching框架下，光线被离散为若干步长为 $\Delta t$ 的采样段。每一步的局部透射率近似为：

$$T_i = e^{-\mu_a(t_i) \cdot \Delta t}$$

沿光线的累积透射率通过连乘得到：

$$T_{\text{total}} = \prod_{i} T_i = \exp\!\left(-\sum_i \mu_a(t_i)\cdot\Delta t\right)$$

这一离散化过程是实时体积渲染中的标准实现路径，每步直接用指数函数更新透射率累积值，不需要额外的数值积分器。

## 实际应用

**大气散射与雾效**：游戏引擎（如Unreal Engine）中的指数雾（Exponential Height Fog）直接基于Beer-Lambert定律，设定大气密度随高度按指数衰减，则水平能见度距离可由吸收系数的倒数 $1/\mu_a$ 估算。若 $\mu_a = 0.01\,\text{m}^{-1}$，则能见度约为100米。

**云体渲染**：Nubis等云渲染系统在计算阳光穿透云层时，通过对云层密度场采样并积分得到光学深度 $\tau$，再用 $e^{-\tau}$ 得到各采样点受到的直接光照透射率，从而模拟出云层厚处偏暗、稀薄处明亮的视觉效果。

**水下场景**：水对红光的吸收系数约为 $\mu_a(\text{red}) \approx 0.35\,\text{m}^{-1}$，对蓝光约为 $\mu_a(\text{blue}) \approx 0.005\,\text{m}^{-1}$。代入Beer-Lambert公式即可解释为什么水下10米处红色物体看起来几乎全黑，而蓝绿色依然可见——这也是体积渲染中实现水下颜色偏移的物理依据。

## 常见误区

**误区一：将Beer-Lambert定律等同于完整的体积渲染方程**。Beer-Lambert定律仅描述**吸收**（absorption）导致的光衰减，不包含散射（scattering）和自发光（emission）。完整的辐射传输方程（Radiative Transfer Equation, RTE）还包含外散射（out-scattering）损耗项和内散射（in-scattering）增益项。在烟雾或云雾等强散射介质中，仅用Beer-Lambert定律会严重低估介质的实际亮度。

**误区二：认为吸收系数 $\mu_a$ 与波长无关**。Beer-Lambert定律本身不限定 $\mu_a$ 为常数，实际介质的 $\mu_a$ 强烈依赖光的波长，这正是彩色吸收的物理来源。在体积渲染中若要模拟彩色介质（如红色烟雾），必须对RGB三个通道分别使用不同的 $\mu_a$ 值进行独立计算。

**误区三：步长 $\Delta t$ 越大，累积透射率误差越小**。实际上，离散累乘 $\prod e^{-\mu_a \Delta t}$ 在 $\mu_a$ 均匀时与连续积分等价，但当介质密度变化剧烈时，过大步长会低估光学深度，导致透射率偏高（介质看起来比实际更透明）。正确做法是在密度梯度大的区域缩小步长或使用自适应步长策略。

## 知识关联

**前置概念——Ray Marching**：Ray Marching提供了沿视线逐步采样三维密度场的遍历框架，而Beer-Lambert定律则在每一步上给出透射率的更新规则，两者配合构成最基础的体积渲染循环。没有Ray Marching，Beer-Lambert定律的路径积分只能对均匀介质求解析解，无法处理空间变密度场。

**后续概念——参与介质（Participating Media）**：参与介质将Beer-Lambert定律从纯吸收场景拓展到同时考虑散射和发射的完整物理模型。吸收系数 $\mu_a$、散射系数 $\mu_s$ 和消光系数 $\mu_t = \mu_a + \mu_s$ 共同构成参与介质的材质参数体系，Beer-Lambert定律中的 $e^{-\mu_a d}$ 将升级为 $e^{-\mu_t d}$ 形式的消光衰减，这是理解单次散射和多次散射模型的入口。