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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 参与介质

## 概述

参与介质（Participating Media）是指能够与穿过其内部的光线发生交互作用的三维空间体，包括烟雾、云层、雾气、牛奶、皮肤组织等材料。与不透明表面渲染中光线只在二维表面发生交互不同，参与介质要求在光线穿越体积的整个路径上对吸收（Absorption）、外散射（Out-Scattering）、内散射（In-Scattering）和自发射（Emission）四种物理过程进行积分计算。

参与介质理论的数学基础由辐射传输方程（Radiative Transfer Equation，RTE）奠定，其完整形式最早由物理学家钱德拉塞卡（Subrahmanyan Chandrasekhar）于1950年在其著作《辐射传输》中系统化整理。该方程最初用于天体物理学中描述星际气体与光的相互作用，后被引入计算机图形学，成为体积渲染的核心数学工具。

参与介质渲染与表面渲染的本质区别在于：光能量在三维空间中连续衰减与增强，不能简化为离散的表面采样问题。正确模拟参与介质能够产生体积光（Volumetric Light Shaft）、次表面散射（SSS）、云内多次散射等视觉现象，这些效果在电影特效、气象可视化和医学图像渲染中不可或缺。

## 核心原理

### 体积渲染方程（VRE）

完整的体积渲染方程（Volumetric Rendering Equation）描述光线从起点 $t_0$ 到终点 $t_1$ 沿方向 $\omega$ 传播时辐射亮度 $L$ 的变化：

$$L(\mathbf{x}, \omega) = \int_{t_0}^{t_1} T(t_0, t) \cdot \left[ \sigma_s(\mathbf{x}(t)) \cdot L_{\text{scatter}}(\mathbf{x}(t), \omega) + \sigma_a(\mathbf{x}(t)) \cdot L_e(\mathbf{x}(t), \omega) \right] dt + T(t_0, t_1) \cdot L_{\text{bg}}$$

其中透射率函数 $T(t_0, t)$ 由Beer-Lambert定律推导而来：

$$T(t_0, t) = \exp\left(-\int_{t_0}^{t} \sigma_t(\mathbf{x}(s)) \, ds\right)$$

消光系数 $\sigma_t = \sigma_a + \sigma_s$，即吸收系数与散射系数之和。 $L_{\text{bg}}$ 为背景辐射亮度，代表穿透介质后的背景贡献。

### 四种光-介质交互过程

**吸收（Absorption）**：以吸收系数 $\sigma_a$（单位 $\text{m}^{-1}$）量化，介质将光能转化为热能或化学能，导致辐射亮度单调递减。血红素对绿光强烈吸收而对红光透过率高，是皮肤渲染中差异化 $\sigma_a$ 波长分量的典型依据。

**外散射（Out-Scattering）**：以散射系数 $\sigma_s$ 量化，光子被介质粒子偏转至其他方向离开当前路径，也导致该方向辐射亮度减少。散射系数和吸收系数共同决定**单次散射反照率**（Single Scattering Albedo）$\alpha = \sigma_s / \sigma_t$，$\alpha$ 趋近1.0意味着介质以散射为主（如云层），趋近0则以吸收为主（如深色烟雾）。

**内散射（In-Scattering）**：来自其他方向的光子因散射转入当前路径，使辐射亮度增加。内散射项 $L_{\text{scatter}}$ 需对整个球面 $4\pi$ 立体角积分，乘以相函数 $f_p(\omega, \omega')$ 描述散射方向的概率分布，这是参与介质计算中最昂贵的操作。

**自发射（Emission）**：高温气体（如火焰）或荧光介质本身释放辐射能量，由 $\sigma_a \cdot L_e$ 项描述，依据基尔霍夫热辐射定律，发射率与吸收系数直接相关。

### 光学厚度与均匀/非均匀分类

光学厚度（Optical Depth）定义为 $\tau = \int_{t_0}^{t_1} \sigma_t \, ds$，是判断介质渲染复杂度的关键量。当 $\tau \ll 1$ 时介质为光学稀薄（optically thin），单次散射近似有效；当 $\tau \gg 1$ 时介质为光学稠密，需要多次散射算法（如路径追踪或扩散近似）。均匀介质中 $\sigma_t$ 为常数，透射率退化为 $e^{-\sigma_t d}$；非均匀介质（如云、烟）中密度随空间变化，需要数值积分，常用Ray Marching以固定步长 $\Delta t$ 离散累加。

## 实际应用

**云层渲染**：云属于高反照率（$\alpha \approx 0.999$）的光学稠密介质，多次散射导致云内部呈现均匀白色。Pixar在《飞屋环游记》（2009年）制作云景时使用了基于扩散近似的多次散射方案，将云的 $\sigma_s$ 设为远大于 $\sigma_a$，并通过预计算光照场加速内散射积分。

**医学体积可视化**：CT扫描数据的体绘制将Hounsfield单位映射为 $\sigma_a$ 和 $\sigma_s$，骨骼（HU约+1000）与软组织（HU约0至+100）对X射线的不同衰减特性，在光学渲染中转化为差异化的消光系数，使医生能够区分组织类型。

**实时游戏中的体积雾**：Frostbite引擎采用基于Froxel（Frustum Voxel）的参与介质方案，将视锥体划分为约160×90×64的三维格栅，每个体素独立存储 $\sigma_a$、$\sigma_s$ 和发射项，以Ray Marching步长0.5m到4m自适应积分，实现实时体积光和雾效。

## 常见误区

**误区一：将参与介质透射率等同于表面透明度**。表面材质的透明度是一个标量参数，而参与介质的透射率 $T(t_0, t_1)$ 是沿光线路径对 $\sigma_t$ 进行积分的指数函数，同一介质对不同路径长度的光线透射率完全不同。厚度为10cm的均匀牛奶（典型 $\sigma_t \approx 100 \text{ m}^{-1}$）透射率约为 $e^{-10}$，而1cm厚度则为 $e^{-1} \approx 0.368$，两者相差约22000倍，不能用单一透明度值描述。

**误区二：忽略内散射，仅实现吸收与外散射**。省略内散射项（即只实现Beer-Lambert衰减）在烟雾等高吸收介质中误差尚可接受，但对于云、皮肤、蜡烛等高散射反照率介质会导致严重失真——这类介质在真实中因多次内散射而呈现明亮的次表面发光效果，纯吸收模型会错误地将其渲染为深色、不透明的团块。

**误区三：将均匀介质的解析解直接应用于非均匀体积**。均匀介质 $T = e^{-\sigma_t d}$ 的解析形式常被误用于密度不均匀的烟雾，导致透射率高估或低估。正确做法是使用Ray Marching的数值近似 $T \approx \prod_i e^{-\sigma_t(\mathbf{x}_i)\Delta t}$，步长 $\Delta t$ 须根据密度梯度自适应选择，在密度剧变区域需要减小步长以控制积分误差。

## 知识关联

**前置概念**：Beer-Lambert定律提供了均匀介质中光强随距离指数衰减的基本公式 $I = I_0 e^{-\mu d}$，参与介质将其扩展为对非均匀空间密度的路径积分形式，并在此基础上叠加了内散射和发射项，使衰减描述从单方向传播推广至全角度辐射场。

**后续概念**：相函数（Phase Function）专门描述参与介质中内散射方向分布的概率密度，是VRE内散射项 $L_{\text{scatter}}$ 的核心子问题，Henyey-Greenstein相函数是最广泛使用的解析近似形式。体积阴影在参与介质场景中需要沿光源方向额外追踪阴影射线并积分 $\sigma_t$，产生体积透射阴影。烟雾模拟和流体渲染通过物理模拟生成随时间变化的 $\sigma_a$、$\sigma_s$ 三维场，再输入参与介质方程完成渲染，形成模拟与渲染的完整管线。异构体积将参与介质的密度场以OpenVDB等稀疏数据结构存储，解决非均匀体积的高效采样问题。