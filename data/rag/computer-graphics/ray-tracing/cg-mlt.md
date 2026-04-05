---
id: "cg-mlt"
concept: "Metropolis光传输"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 5
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# Metropolis光传输

## 概述

Metropolis光传输（Metropolis Light Transport，MLT）是由Eric Veach和Leonidas Guibas于1997年在SIGGRAPH上提出的全局光照算法，其核心思想是将统计物理学中的Metropolis-Hastings采样算法移植到光路空间中，通过马尔可夫链在路径空间内游走来高效采样对图像贡献较大的光路。与双向路径追踪每次独立生成路径不同，MLT会在当前路径的邻域内产生"突变"路径，从而聚焦于高贡献区域的采样。

MLT的命名来源于1953年由Nicholas Metropolis等人发表的《Equation of State Calculations by Fast Computing Machines》，原算法用于蒙特卡洛积分热力学状态方程。Veach将其推广至渲染方程的路径积分形式，使得算法可以在高维路径空间（路径顶点坐标、法线、BSDF参数构成的流形空间）中进行有效采样。

MLT最重要的价值在于它能处理双向路径追踪难以高效采样的光路——例如焦散（caustics）、光线穿越多个镜面反射后照亮漫反射面的SDS路径（Specular-Diffuse-Specular），以及通过细小缝隙的间接照明。在这些场景中，MLT通过马尔可夫链的局部突变保持对高贡献路径的持续探索，收敛速度远优于独立采样方法。

## 核心原理

### 路径空间积分与目标分布

MLT将图像亮度表达为路径空间上的积分。设路径 $\bar{x} = (x_0, x_1, \ldots, x_k)$ 为一条长度为 $k+1$ 的光路，其对图像贡献为测量贡献函数 $f(\bar{x})$，即该路径携带的辐射度乘以几何传播项的乘积。MLT的目标是按照归一化分布 $p(\bar{x}) \propto f(\bar{x})$ 对路径空间采样，使得采样密度与贡献成正比，从而减少方差。

整体图像亮度估计量为：

$$I = \int_\Omega f(\bar{x})\, d\mu(\bar{x}) \approx \frac{1}{N} \sum_{i=1}^N \frac{f(\bar{x}_i)}{p(\bar{x}_i)}$$

当 $p(\bar{x}) \propto f(\bar{x})$ 时，每个样本对 $I$ 的贡献趋于均等，方差趋近于零。

### Metropolis-Hastings接受-拒绝准则

马尔可夫链从当前路径 $\bar{x}$ 出发，通过突变函数（mutation）生成候选路径 $\bar{y}$。接受概率为：

$$a(\bar{x} \to \bar{y}) = \min\!\left(1,\; \frac{f(\bar{y})\, T(\bar{y} \to \bar{x})}{f(\bar{x})\, T(\bar{x} \to \bar{y})}\right)$$

其中 $T(\bar{x} \to \bar{y})$ 是从 $\bar{x}$ 突变到 $\bar{y}$ 的转移概率密度。若接受，链移动到 $\bar{y}$；若拒绝，链停留在 $\bar{x}$（当前路径被再次记录）。这一准则保证了平稳分布恰好是 $p(\bar{x}) \propto f(\bar{x})$，即细致平衡（detailed balance）条件成立。

### 突变策略（Mutation Strategies）

MLT的效率高度依赖突变策略的设计，Veach原文提出了三种主要突变类型：

**双向突变（Bidirectional Mutation）**：利用双向路径追踪的连接操作，随机截断当前路径并从两端重新生长部分子路径后重新连接，能够大幅改变路径拓扑结构，帮助马尔可夫链跨越低概率区域（即"大步突变"）。

**扰动突变（Perturbation）**：对当前路径中的一个或多个顶点施加小扰动，具体包括镜面扰动（在镜面反射方向附近按 $\Delta\theta \sim \text{Exponential}(\sigma)$ 偏转）和非镜面扰动（对漫反射顶点在半球面上的小立体角内重采样）。扰动突变保留路径拓扑结构，专注于细化当前高贡献区域的采样，对焦散收敛尤为重要。

**镜头扰动（Lens Perturbation）**：固定路径的光源端，对相机端射线方向施加小扰动，然后通过Snell-Descartes折射规则将扰动传播至整条路径。此策略在渲染玻璃球等折射焦散时特别有效，因为镜头扰动可以沿折射链追踪高贡献路径的局部邻域。

### 初始化：能量归一化与b值估计

MLT需要预先估计图像总亮度 $b = \int_\Omega f(\bar{x})\, d\mu(\bar{x})$，以便将马尔可夫链样本正确归一化到物理亮度单位。通常用 $N_{\text{init}}$ 条（典型值为 $10^5 \sim 10^6$）独立路径蒙特卡洛估计 $b$，估计误差会直接影响最终图像的整体亮度偏差，但不影响图像的相对分布（即噪声结构）。

## 实际应用

**焦散渲染**：在渲染水面下的焦散图案时，常规路径追踪需要极高采样数才能找到经水面折射汇聚的光路。MLT一旦找到一条有效焦散路径，便通过扰动突变在其邻域持续采样，能在远低于独立采样所需样本数的情况下重建清晰的焦散花纹。

**走廊与间接光照**：在"走廊"场景中，光源通过多次漫反射照亮深处区域，有效路径在路径空间中占据极小体积。MLT的双向突变能定期生成新的有效路径，而扰动突变则细化已发现路径的采样，两者配合使走廊深处的噪声均匀分布而非集中于未采样区域。

**Veach的MLT原文测试场景**：原论文中著名的"Veach走廊"场景包含五盏不同大小的灯，最小灯仅从极小立体角可见。在相同时间预算下，MLT的RMSE比双向路径追踪低约5倍，展示了马尔可夫链策略在低接受率区域的显著优势。

**现代变体MMLT（Multiplexed MLT）**：Hachisuka等人2014年提出的MMLT将技术复用（MIS）整合进突变策略，通过在不同长度路径之间切换的"多路复用突变"消除了原始MLT中链混合速度慢的问题，已被集成到Mitsuba渲染器中作为生产渲染选项。

## 常见误区

**误区一：误认为MLT收敛速度总是优于双向路径追踪。** 实际上，当场景光路分布较为均匀（如室外场景、无遮挡的漫反射环境）时，马尔可夫链的局部探索反而造成样本之间高度相关，导致方差降低速度慢于独立的双向路径追踪。MLT的优势仅在于路径空间中存在离散高亮区域（焦散、SDS路径）时才体现。

**误区二：认为拒绝当前突变等价于浪费计算。** 在Metropolis-Hastings框架中，被拒绝时链停留在 $\bar{x}$，该路径被**再次**计入像素贡献，即"重复计数"而非丢弃。这是算法保证平稳分布所必需的机制，与MCMC中的一般理解一致。忽略这一点会导致高亮区域贡献被低估，产生系统性偏暗的偏差。

**误区三：突变步长越小收敛越好。** 扰动突变步长过小会使链"冻结"在局部极大值附近，造成相邻路径相关性极高，方差虽表面低却带来极强的低频噪声（块状artifact）。步长过大则接受率骤降（镜面扰动中典型目标接受率为23%，源自高维MCMC最优步长理论）。实践中通常混合使用大步双向突变（约占20%）和小步扰动突变（约占80%）来平衡探索与利用。

## 知识关联

MLT以双向路径追踪为基础：双向突变策略直接复用双向路径追踪的子路径生成与连接操作，MLT可被理解为在双向路径追踪的采样空间上附加了Metropolis-Hastings再权重层。掌握双向路径追踪中路径测量贡献函数 $f(\bar{x})$ 的构造方式（包括几何传播项 $G$、BSDF项和光源/相机重要性的乘积分解）是理解MLT接受概率计算的前提。

在渲染研究谱系上，MLT直接催生了能量再分配路径追踪（Energy Redistribution Path Tracing，ERPT，Cline等人2005年）和上述MMLT。路径引导（Path Guiding）方法虽然不使用马尔可夫链，但其核心目标（让采样分布逼近 $f(\bar{x})$）与MLT完全一致，可视为用在线学习的显式概率模型替代马尔可夫