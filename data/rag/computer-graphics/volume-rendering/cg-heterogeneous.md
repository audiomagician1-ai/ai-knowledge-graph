---
id: "cg-heterogeneous"
concept: "异构体积"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 异构体积

## 概述

异构体积（Heterogeneous Volume）是指在空间不同位置具有不同散射、吸收和发射系数的参与介质。与均匀体积（Homogeneous Volume）不同，异构体积的消光系数 σ_t 是空间坐标的函数：σ_t(x)，这使得沿光线的透射率计算不能简化为简单的指数衰减，必须通过数值积分来处理。现实世界中的云、烟雾、火焰、大气散射以及医学CT体数据都属于典型的异构体积。

异构体积的渲染难题在于，普通的均匀介质可用解析公式 T(t) = exp(−σ_t · t) 计算透射率，但异构介质需要计算 T(a,b) = exp(−∫_a^b σ_t(x(t)) dt)，这个积分在复杂的密度场中没有闭合解。1968年 Woodcock 等人在核反应堆中子输运模拟中提出了虚碰撞技术（fictitious collision），即后来图形学领域广泛采用的 Delta Tracking 算法。

Delta Tracking 之所以成为异构体积渲染的标准工具，是因为它将无法直接采样的非均匀消光系数转化为均匀采样问题，同时保证无偏性（unbiased）。该方法在 2011 年前后被路径追踪渲染器大规模采用，如今是 Arnold、Mantra、RenderMan 等生产级渲染器处理体积的核心手段。

## 核心原理

### 最大消光系数与虚碰撞

Delta Tracking 的基础是引入一个全局（或局部格子）最大消光系数 σ_max，满足 σ_max ≥ σ_t(x) 对体积内所有位置 x 成立。算法在这个均匀的"上界介质"中以指数分布采样候选碰撞距离：

t ~ Exp(σ_max)，即以 σ_max 为参数的负指数分布

到达候选点 x 后，以概率 σ_t(x) / σ_max 接受该点为真实碰撞（real collision），以概率 1 − σ_t(x) / σ_max 将其视为虚碰撞（null collision）并继续追踪。这一接受-拒绝过程保证了真实碰撞的空间分布在统计意义上完全等价于直接对非均匀介质采样，整个过程无需计算任何积分。

### 透射率估计：Ratio Tracking

当需要估计两点间透射率（用于阴影计算或多散射）而不是采样碰撞距离时，Delta Tracking 的透射率估计变体称为 Ratio Tracking，由 Novák 等人于 2014 年在 SIGGRAPH 论文中系统化。其无偏估计量为：

T̂(a,b) = ∏_i (1 − σ_t(x_i) / σ_max)

其中 x_i 是沿光线以 σ_max 均匀采样所有虚碰撞点。与简单的 Delta Tracking 不同，Ratio Tracking 不会在第一个真实碰撞处停止，而是遍历整条光线段，因此方差更低但每条光线的开销更高。实践中当 σ_t(x) / σ_max 比值普遍接近 0（即介质非常稀疏或 σ_max 远大于实际密度）时，Ratio Tracking 的开销显著增大，此时需要采用层次化 σ_max 策略。

### 层次化最大消光与超级体素

为避免 σ_max 过高导致过多虚碰撞（tracking efficiency 下降），生产渲染器将体积空间划分为均匀格子，每个格子 v_ij 存储局部最大消光系数 σ_max^(ij)。当光线穿越格子边界时动态更新当前有效的 σ_max。OpenVDB 格式（由 DreamWorks 于 2012 年开源）天然支持这种多分辨率稀疏体素结构，配合 Delta Tracking 使用时，空体素格子的 σ_max = 0 可被直接跳过，大幅提升稀疏介质（如云的边缘区域）的渲染效率。典型实现中格子分辨率选择在 8³ 到 16³ 体素之间，可将 tracking efficiency 从均匀 σ_max 的 20%～30% 提升至 60%～80%。

## 实际应用

**云渲染**：Pixar 在《寻找多莉》（2016）中使用了基于 Delta Tracking 的异构体积渲染处理大量动态云体，每帧体积数据量超过数百 GB，通过层次化 σ_max 格子将每条光线的平均虚碰撞次数控制在 10～20 次以内。

**医学可视化**：CT 扫描数据本质是 256³ 到 512³ 的异构体积，每个体素具有不同的 Hounsfield 值映射到 σ_t。Delta Tracking 可直接在这类数据上工作，无需转换为显式的几何表面，能够准确渲染骨骼与软组织之间的过渡区域。

**火焰与烟雾模拟**：流体模拟输出的速度场和密度场每帧都有空间变化，异构体积渲染直接读取这些场数据。以 Houdini 为例，其内置的 Karma 渲染器通过 Delta Tracking 处理模拟输出的 VDB 文件，温度场同时驱动发射项 σ_e(x)，实现发光火焰效果。

**大气散射**：行星大气密度随高度指数衰减（Rayleigh 散射：σ_t(h) ∝ exp(−h/H_R)，H_R ≈ 8km），属于分析可知的异构介质，可对 σ_max 做高度切片优化，在实时渲染中也可采用 Delta Tracking 的简化版本。

## 常见误区

**误区一：σ_max 越大越精确**。事实上 σ_max 仅影响算法效率，不影响结果的无偏性。过高的 σ_max 不会使渲染更准确，只会产生更多虚碰撞，使每条光线需要采样更多次才能找到真实碰撞点，平均碰撞次数正比于 σ_max / σ_avg。正确做法是让 σ_max 尽量紧贴真实最大值。

**误区二：Delta Tracking 和 Ray Marching 都是数值积分，可以互换**。Ray Marching 通过固定步长离散积分，结果存在系统性偏差（biased），步长越大误差越大；Delta Tracking 通过随机采样实现无偏估计，增加路径数量而非减小步长来收敛。两者的误差收敛方式根本不同：Ray Marching 的偏差不随采样数增加消失，而 Delta Tracking 的方差以 1/√N 速率下降。

**误区三：异构体积渲染只需在均匀介质公式中插值密度即可**。在路径追踪框架中，透射率的无偏采样要求使用接受-拒绝的概率框架，简单地用采样点密度替换公式中的 σ_t 会引入系统偏差，尤其在密度梯度剧烈的区域（如云的内外边界）误差极为显著。

## 知识关联

学习异构体积需要扎实理解**参与介质**的基础知识，特别是消光系数 σ_t = σ_a + σ_s 的分解、Beer-Lambert 定律及辐射传输方程（RTE）的体积版本。没有这些概念，Delta Tracking 中"真实碰撞"和"虚碰撞"的概率构造将难以理解。

从均匀参与介质到异构体积，关键跨越在于消光系数从标量常数变为空间场函数 σ_t(x)，导致透射率计算从解析式退化为蒙特卡洛采样问题。Delta Tracking 的 tracking efficiency η = σ_avg / σ_max 是衡量算法在特定体积数据上性能的专用指标，优化异构体积渲染器时应始终监控此值。在多散射情形下，每个散射事件后光线方向改变，但 Delta Tracking 在每段新光线上独立工作，这一局部无记忆性（Markov 性质）保证了整体路径估计的无偏性。
