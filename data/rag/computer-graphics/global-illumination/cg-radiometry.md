---
id: "cg-radiometry"
concept: "辐射度量学"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 2
is_milestone: false
tags: ["物理"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 辐射度量学

## 概述

辐射度量学（Radiometry）是用精确数学量描述电磁辐射能量传播的科学体系，在图形学中专门处理可见光波段（约380nm至780nm）的能量计算。它为渲染方程中的每一个积分项提供物理意义——没有辐射度量学的定义，渲染方程中的 $L_i$、$L_o$ 等符号将毫无意义。辐射度量学与光度量学（Photometry）的区别在于：前者处理纯物理能量，单位为瓦特（W）；后者通过人眼视觉响应曲线 $V(\lambda)$ 加权，单位为流明（lm）。

辐射度量学的现代体系在20世纪中期随计算机图形学的诞生而被引入渲染领域，James Kajiya在1986年发表的渲染方程论文中正式将辐射亮度（Radiance）确立为光线传播的核心度量量。这一选择不是偶然的——Radiance在沿无散射介质中直线传播时保持恒定，这一物理性质使光线追踪算法在数学上得以自洽。

## 核心原理

### 辐射通量（Radiant Flux）$\Phi$

辐射通量是单位时间内通过任意曲面的总辐射能量，定义为：

$$\Phi = \frac{dQ}{dt}$$

单位为瓦特（W）。辐射通量是辐射度量学中最基础的量，一个100W的理想点光源向四周均匀辐射，其 $\Phi = 100\,\text{W}$。所有其他辐射量都可以视为辐射通量对面积、立体角或两者的微分导出量。

### 辐照度（Irradiance）$E$ 与辐射出射度（Radiant Exitance）$M$

辐照度是到达单位面积表面的辐射通量，而辐射出射度是从单位面积表面离开的辐射通量，两者定义形式相同：

$$E = \frac{d\Phi}{dA}$$

单位为 $\text{W/m}^2$。二者的区别仅在于方向：辐照度描述入射，出射度描述出射。在渲染方程中，对入射半球积分辐照度可以得到表面接收到的总能量。辐照度满足Lambert余弦定律：当光线与表面法线夹角为 $\theta$ 时，$E = E_0 \cos\theta$，这解释了为什么斜射光照比垂直照射弱，也是漫反射BRDF中余弦项的物理来源。

### 辐射强度（Radiant Intensity）$I$

辐射强度描述点光源在特定方向上的单位立体角辐射通量：

$$I = \frac{d\Phi}{d\omega}$$

单位为 $\text{W/sr}$（瓦特每球面度）。球面度（sr）是立体角的单位，整个球面对应 $4\pi$ 球面度。一个各向同性的100W点光源在任意方向的辐射强度为 $100/(4\pi) \approx 7.96\,\text{W/sr}$。辐射强度适合描述点光源特性，但对于面光源或描述光线在介质中的传播，则需要更精细的量。

### 辐射亮度（Radiance）$L$

辐射亮度是辐射度量学中最精细也最重要的量，定义为单位投影面积、单位立体角上的辐射通量：

$$L = \frac{d^2\Phi}{d\omega\, dA\cos\theta}$$

单位为 $\text{W/(m}^2\cdot\text{sr)}$。分母中的 $\cos\theta$ 将实际面积 $dA$ 投影到垂直于观察方向的平面，确保Radiance对旋转观察方向保持一致性。Radiance具有一个关键物理性质：在真空（无参与介质）中沿光线方向传播时，$L$ 不随距离衰减。这正是光线追踪可以沿光线方向直接累积Radiance的物理基础。辐照度与辐射亮度的关系为：

$$E = \int_{\Omega} L_i(\omega)\cos\theta\, d\omega$$

这个积分遍及入射半球 $\Omega$，正是渲染方程右侧积分的直接原型。

## 实际应用

**HDR图像与真实亮度存储**：现代HDR格式（如OpenEXR）存储的每个像素值实际上是该方向上的Radiance值，单位为 $\text{W/(m}^2\cdot\text{sr)}$。这与传统LDR图像存储感知亮度（0到255）有本质不同。基于物理的渲染引擎（如Mitsuba、Cycles）在内部全程以Radiance为计算单位，最终通过色调映射（Tone Mapping）转换为可显示值。

**面光源采样**：在路径追踪中对面光源采样时，需要将辐射出射度 $M$（或已知Radiance $L_{emit}$）转换为对渲染点的辐照度贡献。转换公式为：

$$dE = L_{emit} \cdot \cos\theta_i \cdot \cos\theta_o \cdot \frac{dA}{r^2}$$

其中 $\theta_i$ 是光线到接收点法线的夹角，$\theta_o$ 是光线到发射点法线的夹角，$r$ 是两点距离。这个几何项（Geometry Term）是面光源渲染中产生噪声的主要来源之一，当 $r \to 0$ 时项值发散。

**环境光贴图（HDRI）的物理校准**：Polyhaven等网站提供的HDRI环境贴图在采集时记录了真实场景的Radiance，通过对全球面积分可以还原现实中的辐照度。一张在正午晴天采集的HDRI，其顶部天空区域的Radiance约为 $10^4\,\text{W/(m}^2\cdot\text{sr)}$ 量级，而太阳圆盘方向的Radiance可达 $10^7\,\text{W/(m}^2\cdot\text{sr)}$ 量级。

## 常见误区

**误区一：Radiance随距离衰减**。许多初学者将"距离越远光线越暗"的直觉应用于Radiance，认为Radiance应随 $1/r^2$ 衰减。实际上衰减的是辐射强度 $I$（点光源的 $\text{W/sr}$）和辐照度 $E$。Radiance本身在无损介质中不变：离光源更远时，虽然单位面积接收到的功率（辐照度）下降了，但同时观察到光源所对应的立体角也等比减小，两者恰好抵消，Radiance不变。光线追踪沿光线传播直接相加Radiance的合法性正是依赖于此。

**误区二：辐照度与辐射亮度混用于BRDF的输入输出**。BRDF的定义为 $f_r = dL_r / dE_i$，分子是出射Radiance，分母是入射辐照度的微元。如果错误地将BRDF写成 $L_r / L_i$ 的比值，则漏掉了余弦加权因子 $\cos\theta_i$，导致渲染结果亮度偏高且物理上能量不守恒。漫反射表面的Lambertian BRDF值为常数 $\rho/\pi$，其中 $\rho$ 是反照率（0到1），分母的 $\pi$ 正是从辐照度到Radiance转换时对半球积分 $\cos\theta$ 产生的。

**误区三：将辐射度量量与光度量量混淆**。Lux（勒克斯）是光度学辐照度单位，Nit（尼特，$\text{cd/m}^2$）是光度学辐射亮度单位，它们通过683 lm/W的光视效能峰值与物理量相连。在基于物理的渲染中使用Lux或Nit输入灯光参数是合法的，但需要乘以光谱响应曲线才能还原物理Radiance，而大多数渲染器简化地假设白光条件直接进行标量换算。

## 知识关联

辐射度量学为渲染方程的每一项提供了精确的物理量定义：渲染方程中 $L_o$、$L_i$ 均为Radiance，积分变量 $d\omega_i$ 是立体角微元，余弦项 $\cos\theta_i$ 来源于Irradiance与Radiance的转换关系。理解辐射度量学后，路径追踪算法中每次光线弹射所累积的量（Radiance）、蒙特卡洛估计器的权重（BRDF × cosine / pdf）以及重要性采样的设计目标（使pdf正比于被积函数）都将获得清晰的物理解释。在全局光照的后续实现中，光子映射存储的是辐射通量 $\Phi$ 而非Radiance，需要除以密度估计的面积才能还原Irradiance，这一转换直接应用了本文的量纲关系。