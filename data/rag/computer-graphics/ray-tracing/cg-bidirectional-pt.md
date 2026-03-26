---
id: "cg-bidirectional-pt"
concept: "双向路径追踪"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 双向路径追踪

## 概述

双向路径追踪（Bidirectional Path Tracing，简称 BDPT）是由 Lafortune 和 Willems 于 1993 年、以及 Veach 和 Guibas 于 1994 年分别独立提出的全局光照算法。与单向路径追踪从摄像机出发的单一策略不同，BDPT 同时从摄像机和光源各生成一条子路径（subpath），再将两条子路径的端点连接成完整光路，从而对被积函数进行采样。

BDPT 的核心价值在于它能高效处理单向路径追踪极难收敛的场景：焦散（caustics）、间接照明下的小光源、以及光线需要先经过漫反射再到达光源的 LS⁺DE 路径。在这些场景下，纯摄像机出发的路径追踪需要极大的样本数才能偶然命中光源，而 BDPT 通过从光源端延伸子路径后直接连接，大幅降低方差。

BDPT 的理论基础是 Veach 在 1997 年博士论文中完善的**多重重要性采样（MIS）**框架。算法为每条长度为 $k$ 的完整路径分配多种采样策略，通过 MIS 权重组合它们，使最终估计量无偏（unbiased）且方差最小化。

---

## 核心原理

### 路径空间与测量贡献函数

BDPT 在路径空间（path space）上进行积分。一条完整路径 $\bar{x} = x_0 x_1 \cdots x_k$ 中，$x_0$ 在光源表面，$x_k$ 在摄像机传感器上。路径的测量贡献为：

$$f(\bar{x}) = L_e(x_0 \to x_1) \cdot \left[\prod_{i=1}^{k-1} f_s(x_{i-1}, x_i, x_{i+1}) \cdot G(x_i, x_{i+1})\right] \cdot W_e(x_{k-1} \to x_k)$$

其中 $f_s$ 为 BSDF，$G(x_i, x_{i+1}) = \frac{|\cos\theta_i||\cos\theta_{i+1}|}{|x_i - x_{i+1}|^2}$ 为几何耦合项，$L_e$ 为光源辐射，$W_e$ 为摄像机的重要性函数。最终像素值是对所有路径积分 $\int f(\bar{x})\, d\mu(\bar{x})$ 的结果。

### 双向子路径生成与连接策略

BDPT 将路径构造拆分为两个独立的随机游走：
- **光源子路径**：从光源表面采样出发点 $y_0$，按 BSDF 或相位函数递归生成顶点 $y_1, y_2, \ldots, y_t$。
- **摄像机子路径**：从摄像机传感器采样 $z_0$，按 BSDF 递归生成顶点 $z_1, z_2, \ldots, z_s$。

对于长度为 $k = s + t + 1$ 的完整路径，共存在 $k+2$ 种连接策略（$(s, t)$ 的合法组合）：$(s=0, t=k)$ 退化为纯光源追踪，$(s=k, t=0)$ 退化为纯摄像机路径追踪，中间组合则为显式连接——取摄像机子路径末端 $z_{s-1}$ 与光源子路径末端 $y_{t-1}$，发出阴影测试射线验证可见性，再乘以连接段的 BSDF 和几何耦合项。

### MIS 权重与方差控制

每种连接策略 $(s, t)$ 对应一个概率密度 $p_{s,t}(\bar{x})$。BDPT 使用 **Veach 的平衡启发式（balance heuristic）**或**幂启发式（power heuristic，指数通常取 $\beta=2$）**计算 MIS 权重：

$$w_{s,t}(\bar{x}) = \frac{p_{s,t}(\bar{x})^{\beta}}{\sum_{(s',t')} p_{s',t'}(\bar{x})^{\beta}}$$

这保证了所有策略的加权组合是无偏估计量。平衡启发式可证明其方差上界不超过最优单一策略方差的两倍，幂启发式在实践中通常表现更好。每条路径产生的估计量为 $w_{s,t}(\bar{x}) \cdot f(\bar{x}) / p_{s,t}(\bar{x})$，所有策略的贡献累加到对应像素。

---

## 实际应用

**焦散渲染**：在浴室场景中，光线经过玻璃折射形成焦散。单向路径追踪需要数万 SPP 才能在地板上产生可辨认的焦散图案，而 BDPT 通过光源子路径穿过玻璃后直接与摄像机子路径连接，可在数百 SPP 内收敛。

**小光源与间接照明**：Cornell Box 中，当光源面积缩小至原始尺寸的 1/100 时，纯摄像机路径追踪因无法通过随机采样命中小光源而产生严重噪声。BDPT 的 $(s=k, t=1)$ 策略使光源端向场景发射路径，有效覆盖小光源贡献。

**生产渲染中的应用**：Mitsuba 渲染器（Wenzel Jakob 开发）内置了完整的 BDPT 实现，其 `bdpt` integrator 支持最大路径深度参数 `maxDepth`（默认值为 -1，即无限制），并可配置 `lightImage`（是否将 $s=1$ 策略的贡献写入独立的光源图像缓冲区）。PBRT v3/v4 同样包含 BDPT 积分器作为参考实现。

---

## 常见误区

**误区一：BDPT 在所有场景下都优于单向路径追踪**。对于漫反射主导、光源面积较大的开放室外场景，两条子路径连接的计算开销（每个像素需要处理 $O(s \cdot t)$ 个连接对）使 BDPT 每 SPP 的时间成本显著高于单向追踪，而方差改善幅度不足以弥补时间损失。BDPT 的优势仅在特定光路条件下才显著。

**误区二：连接两条子路径时不需要阴影测试**。每次显式连接 $z_{s-1}$ 和 $y_{t-1}$ 时，必须投射一条完整的可见性测试射线（shadow ray）来确认两点之间无遮挡，忽略这一步会引入偏差（bias）。对于包含数百个物体的复杂场景，阴影测试的光线相交计算可占 BDPT 总时间的 40%~60%。

**误区三：BDPT 能有效处理镜面-镜面路径（specular-specular chains）**。当连接路径中包含纯镜面反射顶点时，连接策略的概率密度趋向于零分母问题，导致 MIS 权重退化。BDPT 对 SDS（specular-diffuse-specular）路径的处理效果很差，这正是 Metropolis 光传输被提出来解决的问题之一。

---

## 知识关联

**前置依赖**：BDPT 直接扩展了单向**路径追踪**的随机游走机制——摄像机子路径的生成与标准路径追踪完全相同，光源子路径则是其对偶。理解蒙特卡洛积分中的重要性采样和方差来源，是理解 BDPT 为何能降低焦散噪声的必要条件。

**后续发展**：**Metropolis 光传输（MLT）**由 Veach 和 Guibas 于 1997 年提出，以 BDPT 生成的路径样本为起点，通过马尔可夫链变异（mutation）在路径空间中定向探索高贡献区域，克服了 BDPT 在 SDS 路径上的不足。MLT 的路径变异操作（如双向变异 bidirectional mutation）本质上是在 BDPT 已有的连接结构上施加扰动，因此掌握 BDPT 的连接策略与 MIS 权重计算是理解 MLT 变异接受率推导的直接前提。