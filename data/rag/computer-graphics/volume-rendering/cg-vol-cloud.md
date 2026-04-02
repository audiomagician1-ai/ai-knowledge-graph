---
id: "cg-vol-cloud"
concept: "体积云实现"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 体积云实现

## 概述

体积云实现是利用三维噪声函数构建云的密度场，并通过光线步进（Ray Marching）结合光照散射模型，在实时或离线渲染管线中生成具有真实感云层的技术。与传统贴片云（Billboard Cloud）不同，体积云将云视为参与介质（Participating Media），每个空间采样点既会吸收光线也会向各方向散射光线，从而还原云的蓬松半透明外观。

这一技术在游戏领域的普及以2015年《地平线：零之黎明》（Horizon: Zero Dawn）与2016年《无人深空》（No Man's Sky）为代表节点，两者均在商业引擎中将噪声驱动密度场实时渲染推向大众视野。Guerrilla Games工程师在GDC 2015的分享中披露了基于Worley噪声叠加FBM（Fractional Brownian Motion）的云形态建模方案，奠定了现代实时体积云的技术基础。

体积云实现的核心难点在于：单条光线穿越云层需要数十至数百次密度采样，每个采样点还需朝光源方向再次步进估算透射率，导致每帧计算量极大。因此，噪声纹理烘焙、采样步长自适应以及时间重投影累积（Temporal Reprojection）成为工程实现中不可回避的优化课题。

---

## 核心原理

### 密度场构建：噪声叠加策略

云的密度场 $\rho(\mathbf{x})$ 通常由多层噪声叠加得到。主流方案将Perlin噪声作为宏观云形的低频基底，叠加三层Worley噪声（频率比约为1:2:4）产生云内部的细节卷曲结构：

$$\rho(\mathbf{x}) = \text{remap}\!\left(\text{Perlin}(\mathbf{x}),\ -(W_1 + 0.5W_2 + 0.25W_3),\ 1,\ 0,\ 1\right)$$

其中 $W_i$ 表示第 $i$ 层Worley噪声，`remap`函数将值域线性映射到 $[0,1]$。此外，卷云层与积云层通常分开建模：积云底部平坦（用梯度裁切实现）、顶部蓬松（Worley噪声细节充分保留），而卷云则用更稀疏的FBM纹理处理。

### 光照模型：Beer-Lambert定律与散射相函数

光线从光源穿越密度为 $\rho$ 的介质时，透射率 $T$ 遵循Beer-Lambert定律：

$$T = e^{-\sigma_t \int_0^d \rho(\mathbf{x})\, \mathrm{d}s}$$

其中 $\sigma_t$ 是消光系数（Extinction Coefficient），$d$ 为积分路径长度。在体积云中，$\sigma_t$ 典型值约为 $0.04 \sim 0.1$（单位：每米，依云类型调整）。

散射方向分布由**Henyey-Greenstein相函数**描述：

$$p(\theta) = \frac{1}{4\pi} \cdot \frac{1 - g^2}{(1 + g^2 - 2g\cos\theta)^{3/2}}$$

其中 $g \in [-1, 1]$ 为各向异性参数，云层通常取 $g \approx 0.6 \sim 0.85$，表示强前向散射。实现中常叠加两个HG相函数（一前向一弱后向）并加权，以模拟云边缘的银边（Silver Lining）效果。

### Ray Marching积分与采样优化

体积云的Ray Marching积分分两步：**视线步进**采集密度并累积散射颜色，**阴影步进**从每个样本点向光源方向积分透射率。设视线步长为 $\Delta t$，每步沿光源方向额外进行6次短步进（步长指数递增，通常为 $[1, 2, 4, 8, 16, 32]$ 倍基础步长），可用较少样本近似长程遮挡。

自适应步长策略：当当前样本点密度低于阈值（如 $\rho < 0.01$）时，将步长扩大3倍快速穿越空云区；一旦检测到密度突变，立即缩短步长至原值重新采样。这一策略可将视线步进次数从128次压缩至32～64次，帧率提升显著。

---

## 实际应用

**游戏引擎中的3D云纹理预烘焙**：将128×128×128分辨率的Perlin-Worley混合噪声预烘焙为3D RGBA纹理，R通道存储宏观形态，GBA三通道分别存储三层细节Worley噪声。运行时GPU采样该纹理而非实时计算噪声，将单次密度查询时间从约50纳秒降至约2纳秒（Nvidia RTX 3080实测）。

**时间重投影累积降噪**：将每帧渲染分辨率降至1/16（即渲染16帧拼合一帧完整图像），利用前帧深度与运动向量做重投影混合，可在几乎无质量损失的情况下将体积云的渲染时间控制在0.5ms以内（1080p，PS5硬件）。

**高度梯度与气象分层**：云层密度乘以高度衰减函数 $h(y) = \text{saturate}\!\left(\frac{y - y_{\min}}{y_{\max} - y_{\min}}\right)$，底部做锐截，顶部做软过渡，可区分对流层不同云系（积云约600m～2000m，高积云约2000m～6000m）。

---

## 常见误区

**误区一：认为步进次数越多效果越好**  
步进次数超过128次后，积云的视觉增益极为有限，因为云密度场在大尺度上是低频信号，过度采样只会浪费GPU时间而非增加细节。细节增益主要来自更高分辨率的3D噪声纹理，而非更密集的步进。

**误区二：忽略消光系数 $\sigma_t$ 的物理单位标定**  
直接用 $[0,1]$ 范围的噪声值作为 $\sigma_t$ 而不做单位换算，会导致云层要么完全不透明要么近乎透明，失去分层感。正确做法是将噪声密度 $\rho \in [0,1]$ 与标定的消光系数（如 $0.05 \text{ m}^{-1}$）相乘后再代入Beer-Lambert公式积分。

**误区三：对所有云层使用同一HG参数 $g$**  
卷云（Cirrus）由冰晶组成，散射特性与水云（液态水滴）差异显著：冰晶前向散射更强，$g$ 可达0.9，而积云取0.65更接近物理。混用参数会导致卷云在逆光时缺乏光晕效果，积云在顺光时过于刺眼。

---

## 知识关联

**前置概念—Ray Marching**：体积云的全部密度积分与阴影步进均依赖Ray Marching的逐步采样框架。理解步长控制与提前终止条件（Early Exit：当累积透射率 $T < 0.01$ 时停止步进）是实现体积云的直接前提，这一阈值选取直接影响渲染的性能与正确性。

**横向关联—参与介质渲染（Participating Media）**：体积云是参与介质渲染在大气尺度的具体应用。其使用的Beer-Lambert透射率公式与单次散射积分方程，与体积雾、烟雾、次表面散射共享同一辐射传输方程（Radiative Transfer Equation, RTE）的推导来源，学习体积云有助于理解更通用的体积渲染框架。

**横向关联—大气散射（Atmospheric Scattering）**：体积云的光照颜色（白天偏暖白、云底偏冷灰）受天空环境光影响，通常需要与Rayleigh-Mie大气散射模型联合采样，以获得正确的云底环境光遮蔽（Ambient Occlusion by Atmosphere）效果。