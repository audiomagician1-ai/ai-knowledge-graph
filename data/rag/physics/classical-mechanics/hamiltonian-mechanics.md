---
id: "hamiltonian-mechanics"
concept: "哈密顿力学初步"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 7
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 4
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
updated_at: 2026-03-31
---

# 哈密顿力学初步

## 概述

哈密顿力学是爱尔兰数学家威廉·罗文·哈密顿（William Rowan Hamilton）于1833年提出的经典力学表述体系。它以系统的广义坐标 $q_i$ 和广义动量 $p_i$ 作为独立变量，将力学问题转化为相空间中的几何流问题，而非拉格朗日力学中速度空间里的变分问题。这一转变使得运动方程从二阶微分方程组降低为一阶方程组，极大地简化了某些问题的分析。

哈密顿力学的重要性远超其作为"经典力学另一种写法"的表面印象。它直接催生了统计力学中刘维尔定理的证明，并为量子力学提供了最自然的数学框架——量子力学中的哈密顿算符 $\hat{H}$ 和泊松括号向对易子的替换，都直接继承自哈密顿力学的结构。

---

## 核心原理

### 哈密顿量的构造

哈密顿量 $H(q_i, p_i, t)$ 通过对拉格朗日量进行勒让德变换（Legendre Transform）得到：

$$H = \sum_{i} p_i \dot{q}_i - L(q_i, \dot{q}_i, t)$$

其中广义动量定义为 $p_i = \dfrac{\partial L}{\partial \dot{q}_i}$，勒让德变换将自变量从 $\dot{q}_i$ 切换为 $p_i$。对于保守系统且广义坐标不显含时间的情形，哈密顿量等于系统总机械能 $H = T + V$。但需注意，若势能含速度项（如电磁场中的带电粒子），则 $H \neq T + V$，而仍满足勒让德变换的定义式。

以一维谐振子为例：$L = \dfrac{1}{2}m\dot{x}^2 - \dfrac{1}{2}kx^2$，则 $p = m\dot{x}$，代入得 $H = \dfrac{p^2}{2m} + \dfrac{1}{2}kx^2$，这正是动能加弹性势能的总能量。

### 正则方程（哈密顿方程）

哈密顿力学的核心运动方程称为**正则方程**（Canonical Equations），由 $2n$ 个一阶方程构成（$n$ 为自由度数）：

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

这两组方程具有高度对称性：$q_i$ 和 $p_i$ 以近乎对等的地位出现，仅差一个负号。与拉格朗日方程相比，正则方程将 $n$ 个二阶ODE替换为 $2n$ 个一阶ODE，便于数值积分和定性分析。若 $H$ 不显含某坐标 $q_j$（即 $q_j$ 为循环坐标），则 $\dot{p}_j = 0$，广义动量 $p_j$ 守恒，这与拉格朗日力学中的结论完全一致。

### 相空间与哈密顿流

相空间（Phase Space）是以所有广义坐标 $(q_1, \ldots, q_n)$ 和广义动量 $(p_1, \ldots, p_n)$ 为坐标轴的 $2n$ 维空间。系统在某时刻的完整力学状态对应相空间中的一个点，系统的时间演化对应该点在相空间中描绘的一条轨迹，称为**相轨道**（Phase Trajectory）。

对于一维谐振子，相空间是二维 $(x, p)$ 平面，相轨道为以原点为中心的椭圆：$\dfrac{p^2}{2mE} + \dfrac{kx^2}{2E} = 1$，椭圆的形状由总能量 $E$ 决定。不同能量的相轨道互不相交，这一性质由**刘维尔定理**（Liouville's Theorem）保证：相空间中任意相体积元在哈密顿流下保持不变，数学表达为 $\dfrac{d\rho}{dt} = 0$，其中 $\rho$ 为相空间中的概率密度。

### 泊松括号

任意力学量 $f(q_i, p_i, t)$ 的时间演化可通过**泊松括号**（Poisson Bracket）表达：

$$\frac{df}{dt} = \{f, H\} + \frac{\partial f}{\partial t}$$

其中泊松括号定义为：

$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$

基本泊松括号关系为 $\{q_i, p_j\} = \delta_{ij}$，$\{q_i, q_j\} = 0$，$\{p_i, p_j\} = 0$。若 $\{f, H\} = 0$ 且 $\partial f/\partial t = 0$，则 $f$ 是守恒量。

---

## 实际应用

**中心力场问题**：对于平面运动的质点在 $V(r)$ 势场中，取极坐标 $(r, \theta)$ 作为广义坐标，$p_r = m\dot{r}$，$p_\theta = mr^2\dot{\theta}$（角动量），则 $H = \dfrac{p_r^2}{2m} + \dfrac{p_\theta^2}{2mr^2} + V(r)$。由于 $\theta$ 是循环坐标，$p_\theta = L$（角动量）立即守恒，将问题化为一维等效势问题。

**正则变换与作用-角变量**：哈密顿力学允许通过正则变换寻找"最优坐标系"。对于谐振子，引入作用变量 $J = \oint p\, dq = 2\pi E/\omega$（沿相轨道一周的积分），可使哈密顿量仅依赖 $J$，对应的角变量以匀速旋转，大幅简化求解。

**天体力学摄动论**：在计算行星轨道的长期演化时，哈密顿正则方程配合正则摄动理论，可以系统地计算各阶近似，例如计算地球轨道离心率因其他行星引力而发生的周期性变化（约 $10^5$ 年量级）。

---

## 常见误区

**误区一：哈密顿量总等于总机械能**
许多学生默认 $H = T + V$，但这仅在广义坐标不显含时间且势能不含广义速度时成立。对于在匀速旋转参考系中运动的质点，哈密顿量包含科里奥利力对应的 $\boldsymbol{\Omega} \cdot \boldsymbol{L}$ 项，不等于 $T + V$；带电粒子在磁场中运动时，$H = \dfrac{(\boldsymbol{p} - q\boldsymbol{A})^2}{2m} + q\phi$，动能项中必须出现矢量势 $\boldsymbol{A}$。

**误区二：$q_i$ 和 $p_i$ 的地位完全对等**
正则方程在形式上对 $q$ 和 $p$ 几乎对称，但二者的物理地位并不相同——坐标描述系统的构型，动量描述系统的运动状态。正则变换可以混合 $q$ 和 $p$（例如令新坐标 $Q = p$，新动量 $P = -q$），但这种混合变换在物理解释上需要谨慎，新"坐标"不再有通常的空间位置含义。

**误区三：相轨道可以相交**
由于正则方程的解对初始条件有唯一性，相空间中过同一点的相轨道只有一条。看似相交的相图（例如不稳定平衡点附近的鞍点结构）实际上是多条不同的轨道在有限时间内无限趋近但并不相交，或仅在时间趋于无穷时汇聚于该不动点。

---

## 知识关联

**与拉格朗日力学的联系**：哈密顿量通过勒让德变换由拉格朗日量构造，正则方程与拉格朗日方程等价，但所用变量空间不同（相空间 vs 切丛）。拉格朗日力学中已定义的循环坐标和守恒量，在哈密顿框架下通过正则方程和泊松括号得到更系统的处理。

**通向量子力学**：哈密顿力学的泊松括号 $\{q_i, p_j\} = \delta_{ij}$ 在量子化时对应正则对易关系 $[\hat{q}_i, \hat{p}_j] = i\hbar\delta_{ij}$，海森堡方程 $\dfrac{d\hat{f}}{dt} = \dfrac{1}{i\hbar}[\hat{f}, \hat{H}]$ 正是哈密顿运动方程的量子版本，二者形式上一一对应。

**通向统计力学**：刘维尔定理是统计力学的数学基石，正则系综的配分函数 $Z = \int e^{-H/k_BT}\, dq\, dp$ 直接在相空间上定义，哈密顿量决定了热力学平衡的玻尔兹曼权重分布。