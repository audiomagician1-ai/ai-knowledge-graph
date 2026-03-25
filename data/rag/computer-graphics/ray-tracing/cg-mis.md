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
---
# 多重重要性采样

## 概述

多重重要性采样（Multiple Importance Sampling，MIS）由 Eric Veach 在其 1997 年的博士论文《Robust Monte Carlo Methods for Light Transport Simulation》中正式提出，是解决光线追踪中单一采样策略方差过大问题的核心技术。其基本思想是：当积分计算需要多种采样策略时，将各策略的样本按权重合并，使最终估计量方差低于任意单一策略。

在渲染方程的数值求解中，直接照明计算需要对光源方向和 BRDF 分布同时进行采样。单独使用光源采样时，对于镜面高光（光滑 BRDF）会产生极高方差；单独使用 BRDF 采样时，对于小面积强光源会漏掉大量能量贡献。MIS 通过对两种策略的样本加权组合，使估计量在两种极端情况下都保持低方差。

MIS 不仅适用于直接光照的光源/BRDF 联合采样，还可推广到双向路径追踪（BDPT）中路径连接策略的权重分配，以及光子映射与路径追踪的结合场景（SPPM、VCM 等），是现代物理渲染器（如 Mitsuba、Cycles、Arnold）中不可缺少的降噪手段。

---

## 核心原理

### 平衡启发式（Balance Heuristic）

设有 $n$ 种采样策略，第 $i$ 种策略的概率密度函数为 $p_i$，采样数量为 $n_i$。MIS 估计量的一般形式为：

$$\langle I \rangle_{\text{MIS}} = \sum_{i=1}^{n} \frac{1}{n_i} \sum_{j=1}^{n_i} w_i(x_{i,j}) \frac{f(x_{i,j})}{p_i(x_{i,j})}$$

其中 $w_i(x)$ 是第 $i$ 种策略在样本点 $x$ 处的 MIS 权重，需满足**权重分配条件**：$\sum_{i=1}^{n} w_i(x) = 1$（对 $f(x) \neq 0$ 的所有 $x$）。

Veach 证明，方差表现最优的权重形式是**平衡启发式**（Balance Heuristic）：

$$w_i(x) = \frac{n_i \, p_i(x)}{\sum_{k=1}^{n} n_k \, p_k(x)}$$

平衡启发式将每个样本的权重分配给"对该点最擅长的策略"，即哪个策略在该点的采样密度最高，就获得更大权重。

### 幂启发式（Power Heuristic）

实践中更常用的是**幂启发式**（Power Heuristic），在 $\beta = 2$ 时表现最佳：

$$w_i(x) = \frac{\left(n_i \, p_i(x)\right)^\beta}{\sum_{k=1}^{n} \left(n_k \, p_k(x)\right)^\beta}$$

Veach 通过大量实验验证，$\beta = 2$ 能进一步抑制单一策略采样密度极低时的"孤立噪点"（火花噪声），比平衡启发式在实际渲染图像中表现更佳。目前 PBRT 及 Blender Cycles 均默认使用 $\beta = 2$ 的幂启发式。

### 光源与 BRDF 的双策略联合采样

在直接照明计算中，$n = 2$，两种策略分别为：
- **光源采样**：按照光源面积/立体角分布采样方向，$p_{\text{light}}(\omega)$
- **BRDF 采样**：按照 BRDF 叶瓣分布采样方向，$p_{\text{bsdf}}(\omega)$

以 $n_1 = n_2 = 1$（各取一个样本）为例，光源样本 $\omega_l$ 的 MIS 权重为：

$$w_{\text{light}}(\omega_l) = \frac{p_{\text{light}}(\omega_l)^2}{p_{\text{light}}(\omega_l)^2 + p_{\text{bsdf}}(\omega_l)^2}$$

当着色点是理想镜面时，$p_{\text{bsdf}}$ 在镜面方向极大，此时 $w_{\text{light}}$ 趋近于 0，光源样本贡献被压制，避免了高方差项进入估计；BRDF 样本获得接近 1 的权重，正确反映镜面反射。对于漫反射表面，$p_{\text{bsdf}}$ 较平坦而 $p_{\text{light}}$ 集中于光源，两者权重平衡分配，双管齐下。

---

## 实际应用

### PBRT 中的一次反弹直接光照

在 PBRT v3/v4 的 `DirectLightingIntegrator` 中，每次计算直接光照时同时执行两次采样：一次从光源表面均匀采样入射方向，一次从 BRDF 分布采样；两个样本的贡献分别乘以幂启发式权重后累加。对于面积光源与粗糙金属 BRDF 的组合，实验数据表明 MIS 相比单纯 BRDF 采样可将方差降低约 **10 倍至 100 倍**，具体倍数取决于光源大小与 BRDF 粗糙度的匹配程度。

### 处理 Delta 分布的特殊情况

当 BRDF 含有 Delta 分量（理想镜面、理想折射）时，$p_{\text{bsdf}}$ 在 Delta 方向为无穷大，光源采样几乎无法命中该方向，$w_{\text{light}}$ 应强制设为 0，仅保留 BRDF 采样路径。实现上通常用一个标志位 `specular` 跳过光源采样分支。若不做此处理，会引入错误的无穷大权重，导致渲染图像出现大面积黑块或白块。

### 双向路径追踪中的 MIS 路径连接

在 BDPT 中，Veach 将所有能生成相同路径的采样技术统一纳入 MIS 框架：长度为 $k$ 的路径可由相机子路径长 $s$ 和光源子路径长 $t = k - s$ 的任意组合连接而成，共 $k+1$ 种连接方式，每种方式的权重通过平衡启发式计算。这一框架使 BDPT 能同时高效处理直接照明、焦散和镜面-漫-镜（SDS）路径。

---

## 常见误区

### 误区一：MIS 权重只依赖于采样策略，与被积函数无关

实际上，MIS 权重 $w_i(x)$ 不仅依赖于各策略的 PDF 值，还隐式依赖于被积函数 $f(x)$ 的结构——权重设计的目标正是让高密度策略在 $f$ 值大的区域压制低密度策略的贡献。如果两种策略的 PDF 之比始终恒定（例如两者都是常数但数值不同），幂启发式退化为固定比例分配，此时 MIS 并不带来任何方差改善。

### 误区二：采样数量越多越好，不需要平衡 $n_i$

当 $n_1 \gg n_2$ 时，平衡启发式中 $n_1 p_1$ 项主导，策略 2 的样本权重被压得极小，等同于浪费了策略 2 的计算预算。实践中应根据各策略对积分的预期贡献比例分配 $n_i$，而不是一律用最多样本。PBRT 的实现默认 $n_1 = n_2 = 1$，在单 GPU 核心预算下经实验证明接近最优分配。

### 误区三：MIS 可以完全消除方差

MIS 只能保证方差不超过最优单一策略方差的某个倍数（Veach 证明平衡启发式的方差上界为最优单策略的 4 倍以内），而无法将方差降至零。对于"所有策略都糟糕"的被积函数区域（如遮挡物后方的路径），MIS 无法自动生成更好的采样策略，仍需引入专用的采样技术（如 Manifold Next Event Estimation）来补充。

---

## 知识关联

多重重要性采样建立在**重要性采样**（Importance Sampling）的基础上：重要性采样要求设计与被积函数形状匹配的 PDF，而 MIS 解决了单一 PDF 无法同时匹配被积函数多个因子（光源项、BRDF 项、可见性项）的问题。理解 MIS 需要熟悉蒙特卡洛积分的方差分析方法，尤其是估计量期望与方差的 PDF 依赖关系。

在更高级的光传输算法中，MIS 是 **VCM（Vertex Connection and Merging）** 和 **UPBP（Unified Points, Beams, and Paths）** 的理论基石，这些算法将路径追踪与光子映射视为不同采样策略，通过 MIS 统一合并。此外，**ReSTIR（Reservoir-based Spatiotemporal Importance Resampling）** 算法中的空间/时间重用也借鉴了 MIS 的权重思想，对实时光线追踪领域影响深远。
