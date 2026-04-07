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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

双向路径追踪（Bidirectional Path Tracing，简称 BDPT）是由 Lafortune 和 Willems 于 1993 年、以及 Veach 和 Guibas 于 1994 年独立提出的蒙特卡洛渲染算法。与单向路径追踪从摄像机出发的单一策略不同，BDPT 同时从摄像机和光源各生成一条子路径，再将两条子路径的顶点相互连接，构成完整的光传输路径。这种"双向"结构使得算法能在同一帧内同时利用来自光源侧和摄像机侧的信息。

BDPT 的核心价值在于它对焦散（caustics）和光源被遮挡场景的高效处理。单向路径追踪在处理室内小型光源时，大量路径无法击中光源，导致高方差（噪点严重）；而 BDPT 通过从光源侧生成子路径并与摄像机子路径连接，极大地提升了这类场景下的采样效率。Veach 在 1997 年的博士论文中将 BDPT 纳入多重重要性采样（MIS）框架，奠定了现代无偏离线渲染器的理论基础。

## 核心原理

### 路径空间测度与完整路径的构成

BDPT 在路径空间 $\mathcal{P}$ 上进行积分。一条长度为 $k$ 的完整路径由摄像机子路径（长度 $s$）和光源子路径（长度 $t$）拼接而成，满足 $s + t = k + 2$（其中 2 代表摄像机和光源端点各贡献一个顶点）。对于每对 $(s, t)$ 组合，BDPT 独立构造一种采样策略，所有策略覆盖同一路径长度下的不同顶点子集。例如，当 $s=2, t=1$ 时，路径从摄像机出发经一次反弹后直接连到光源，等价于直接光照计算。

路径的贡献函数为：

$$
C = \frac{f(\bar{x})}{p(\bar{x})}
$$

其中 $\bar{x} = (x_0, x_1, \ldots, x_k)$ 是路径顶点序列，$f(\bar{x})$ 是路径吞吐量（包含 BSDF、几何因子 $G$ 和发光项的乘积），$p(\bar{x})$ 是该路径在当前采样策略下的概率密度。

### 几何连接项与可见性测试

将摄像机子路径末顶点 $c_{s-1}$ 与光源子路径末顶点 $l_{t-1}$ 相连时，需计算几何连接项（Geometry Term）：

$$
G(c_{s-1} \leftrightarrow l_{t-1}) = \frac{\cos\theta_c \cdot \cos\theta_l}{|c_{s-1} - l_{t-1}|^2} \cdot V(c_{s-1}, l_{t-1})
$$

其中 $\theta_c$ 和 $\theta_l$ 分别是连接方向与两顶点法线的夹角，$V$ 是可见性函数（0 或 1）。每次连接操作都需要额外发射一条影子光线（shadow ray）进行可见性测试，这是 BDPT 相比单向追踪额外开销的主要来源。

### 多重重要性采样权重

若直接将所有 $(s, t)$ 策略的贡献相加，方差会因各策略概率密度的悬殊差异而急剧上升。Veach-Guibas 的解决方案是为每种策略赋予 MIS 权重 $w_{s,t}$，采用平衡启发式（balance heuristic）：

$$
w_{s,t}(\bar{x}) = \frac{p_{s,t}(\bar{x})}{\sum_{s',t'} p_{s',t'}(\bar{x})}
$$

实践中常用的幂启发式（power heuristic，指数 $\beta=2$）进一步降低方差，使 BDPT 估计量保持无偏性的同时显著减少噪点。

## 实际应用

**焦散与光泽反射场景**：在包含玻璃球或水面等折射物体的场景中，从摄像机出发的路径极难通过折射路径偶然击中光源，导致焦散几乎无法收敛。BDPT 从光源侧生成穿过折射体的子路径，再与摄像机侧路径连接，可将焦散渲染所需样本数减少约一个数量级。

**室内小光源场景**：Cornell Box（康奈尔盒子）是 BDPT 效果最直观的测试场景。其顶部小面积光源使单向路径追踪在每样本 SPP 较低时极其嘈杂，而 BDPT 通过 $t=1$（直接连接光源）的策略稳定采样直接光照，在相同 SPP 下误差（RMSE）通常比单向追踪低 3–5 倍。

**工业级渲染器集成**：Mitsuba 渲染器（由 Wenzel Jakob 开发）将 BDPT 作为参考算法实现，其源代码中 `bdpt.cpp` 明确展示了路径顶点池的分配与连接逻辑，是学习 BDPT 工程实现的权威参考。

## 常见误区

**误区一：认为 BDPT 总比单向路径追踪快**。BDPT 在漫射主导（diffuse-dominant）、光源较大的开放场景中，因每次采样需要额外的影子光线和多策略权重计算，实际每样本耗时可能比单向追踪高 30%–50%，而方差降低却不明显。BDPT 的优势仅在特定光传输路径（如 LS+DE 型路径，即多次镜面反射后到达漫射面）上才能充分体现。

**误区二：混淆 BDPT 与光子映射**。两者都利用光源子路径，但原理不同：BDPT 通过显式连接两条子路径来估计路径积分，是无偏的；光子映射将光子存储在光子图（photon map）中并通过密度估计查询，是有偏但一致的算法。BDPT 中不存在密度估计步骤，也不维护全局光子数据结构。

**误区三：忽略奇异路径的处理**。当子路径顶点落在完全镜面（specular，即 delta BSDF）表面时，该顶点无法被"直接连接"——delta BSDF 在任意非零立体角上概率密度为零，连接项为零。BDPT 实现中必须跳过镜面顶点的连接操作，仅允许 $s=0$ 或 $t=0$ 等退化策略处理纯镜面路径。

## 知识关联

**前置概念**：单向路径追踪（Path Tracing）提供了俄罗斯轮盘赌终止、BSDF 采样和直接光照估计的基础。理解路径追踪的渲染方程离散化方式是掌握 BDPT 路径空间表述的前提，因为 BDPT 的路径吞吐量公式直接继承了路径追踪中的几何因子乘积结构。

**后续概念**：Metropolis 光传输（MLT）在 BDPT 的路径采样框架上引入了 Metropolis-Hastings 马尔可夫链，通过对高贡献路径的局部变异（mutation）进行集中采样，专门解决 BDPT 仍难以高效采样的极端焦散和狭窄光路场景。MLT 的路径变异操作（如双向变异 bidirectional mutation）直接复用了 BDPT 的子路径生成机制，因此 BDPT 是理解 MLT 的直接基础。