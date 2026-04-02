---
id: "cg-mis"
concept: "多重重要性采样"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 多重重要性采样

## 概述

多重重要性采样（Multiple Importance Sampling，MIS）是由Eric Veach于1995年在其博士论文中提出的蒙特卡洛积分技术，专门用于解决渲染方程中被积函数由多个因子乘积构成时，单一采样策略无法高效估计积分的问题。其核心思想是将来自不同概率分布的样本按照各自分布对被积函数的"匹配程度"进行加权组合，最终得到方差更低的无偏估计量。

该方法的提出背景是光线追踪中的直接光照计算：渲染方程的被积函数形如 $f_r(\omega_i, \omega_o) \cdot L_i(\omega_i) \cdot \cos\theta_i$，其中BRDF项 $f_r$ 和入射辐射度 $L_i$ 各有适合自己的采样分布，单独使用任一分布都会导致另一项引发高方差。MIS通过同时使用两种策略并合并估计，将两者的优势统一在一个框架下。

MIS在现代离线渲染器（如Mitsuba、PBRT）和实时路径追踪（如NVIDIA的ReSTIR）中被广泛采用，是减少"萤火虫"噪点（fireflies）的标准手段，尤其在处理高光镜面材质加上小面积强光源的场景时效果显著。

## 核心原理

### 组合估计量与权重函数

MIS的基本形式是，假设使用 $n$ 种采样策略，第 $i$ 种策略的PDF为 $p_i$，每种策略各取 $n_i$ 个样本，则MIS估计量为：

$$\hat{I}_{MIS} = \sum_{i=1}^{n} \frac{1}{n_i} \sum_{j=1}^{n_i} w_i(X_{ij}) \frac{f(X_{ij})}{p_i(X_{ij})}$$

其中 $w_i(x)$ 是第 $i$ 个策略在样本 $x$ 处的权重函数，满足约束条件：当 $f(x) \neq 0$ 时，$\sum_i w_i(x) = 1$；当 $p_i(x) = 0$ 时，$w_i(x) = 0$。只要满足这两个条件，该估计量对任意权重函数均为无偏估计。

### 平衡启发式与幂启发式

Veach在论文中证明，**平衡启发式（Balance Heuristic）**是最优的线性权重函数族：

$$w_i^{balance}(x) = \frac{n_i p_i(x)}{\sum_k n_k p_k(x)}$$

这意味着哪种策略在该样本位置的PDF更高，就赋予更大权重，直觉上等价于"谁更擅长生成这个位置的样本，谁就更可信"。

在实践中，性能更好的是**幂启发式（Power Heuristic）**，其形式为：

$$w_i^{power}(x) = \frac{(n_i p_i(x))^\beta}{\sum_k (n_k p_k(x))^\beta}$$

Veach建议并在大量实验中验证 $\beta = 2$ 为最佳指数，幂启发式通过放大PDF差距使权重更集中，进一步压低方差。PBRT v4源代码中`PowerHeuristic`函数即以 $\beta=2$ 的幂启发式实现。

### 光源与BRDF联合采样的具体流程

在直接光照计算中，MIS的两种策略分别是：

1. **按光源采样**：在光源面积上采样一个点，将方向 $\omega_i$ 指向该点，PDF为 $p_{light}(\omega_i)$；适合处理辐射度 $L_i$ 强烈集中在光源方向的情形。

2. **按BRDF采样**：按BRDF的概率分布生成 $\omega_i$，PDF为 $p_{brdf}(\omega_i)$；适合高光叶瓣极窄、光源面积较大的情形。

每个样本点同时计算两种策略在该点的PDF，用幂启发式权重将贡献混合。一个典型实现中，直接光照的最终估计为各自各取一个样本后加权求和，总样本数为2，而非简单地将两个独立估计量平均。

## 实际应用

**高光材质 + 小面积光源**：若只用BRDF采样，高光叶瓣宽度为1°而光源张角为0.1°，命中率极低，产生噪点。若只用光源采样，光源方向不在BRDF峰值处时贡献极小。MIS权重在两种情形下均能自动退化到更合适的策略，实测在这类场景中可将方差降低10倍以上。

**区域光 + 漫反射材质**：对于完全漫反射表面，BRDF是常数，此时 $p_{brdf}$ 是余弦加权分布，对均匀分布的面光源两种策略效率相近，MIS的开销（多计算一次PDF）换来的方差降低有限，但仍不会比单一策略更差——这是MIS的理论保证之一。

**路径追踪中的NEE（Next Event Estimation）**：现代路径追踪器的NEE实现就是MIS的直接体现：在每个弹射点，同时执行一次光源采样和一次BRDF采样，用幂启发式合并贡献，并在路径延伸时跳过对光源的偶然击中（或用MIS校正避免双重计数）。

## 常见误区

**误区1：认为MIS是两个独立估计量的简单平均**。实际上，MIS并非 $\frac{1}{2}(\hat{I}_{light} + \hat{I}_{brdf})$，这种平均无法消除双重计数问题，且方差是两者最大值的量级。MIS权重函数的作用是将每个样本的贡献按"相对适合程度"分配，使得同一区域不会被两种策略重复过度计数。

**误区2：以为权重函数需要最优化求解**。Veach的证明表明，对于任意满足约束的权重函数，MIS估计量均无偏；幂启发式 $\beta=2$ 并非通过优化推导出的精确最优解，而是经验上在多类渲染场景下表现最好的参数选择。将 $\beta$ 调至更高（如5或10）会使权重退化为接近"赢者通吃"，在PDF比值不极端时反而增加方差。

**误区3：对不可见样本仍然施加完整贡献**。使用光源采样策略时，若采样点被遮挡，贡献应为零，但此时仍需用该样本的 $p_{light}$ 和 $p_{brdf}$ 计算权重（贡献为零，权重本身不影响结果）；若直接跳过权重计算或将权重设为1，会破坏MIS估计量的无偏性。

## 知识关联

**前置概念——重要性采样**：MIS的出发点是单一重要性采样的局限性：当PDF $p(x)$ 与被积函数 $f(x)$ 形状不匹配时，少数样本的贡献会异常高，产生高方差。MIS通过将多种分布的优势叠加，使得在被积函数任何高值区域都至少有一种策略能高效采样。如果已知只有一种策略最适合整个积分域，退化到单一重要性采样，MIS的权重函数会自动将该策略的权重趋向1。

**延伸方向**：ReSTIR（Reservoir-based Spatiotemporal Importance Resampling，2020年SIGGRAPH）将MIS的思路扩展到时空复用框架，通过蓄水池采样（Reservoir Sampling）在相邻像素和时间帧之间共享和合并样本，本质上是对更大样本集施加的MIS加权，能在实时路径追踪中以每帧1-2个样本实现接近离线质量的直接光照效果。