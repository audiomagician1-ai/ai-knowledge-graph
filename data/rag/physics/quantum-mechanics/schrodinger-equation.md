---
id: "schrodinger-equation"
concept: "薛定谔方程"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 94.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "primary"
    title: "Quantisierung als Eigenwertproblem"
    author: "Erwin Schrodinger"
    journal: "Annalen der Physik"
    year: 1926
  - type: "textbook"
    title: "Introduction to Quantum Mechanics (3rd ed.)"
    author: "David J. Griffiths, Darrell F. Schroeter"
    isbn: "978-1107189638"
  - type: "textbook"
    title: "Principles of Quantum Mechanics (2nd ed.)"
    author: "R. Shankar"
    isbn: "978-0306447907"
scorer_version: "scorer-v2.0"
---
# 薛定谔方程

## 概述

1926年，薛定谔在六周内连续发表了四篇论文，提出了一个波动方程来描述量子系统的行为。薛定谔方程之于量子力学，正如牛顿第二定律之于经典力学——给定系统的势能函数和初始状态，原则上可以预测系统在任何未来时刻的量子态。保罗·狄拉克评价说："物理学的大部分以及全部化学的数学理论所需要的基本物理定律，已经完全被人们所知了。"（Dirac, 1929）——他指的正是薛定谔方程。

## 核心知识点

### 1. 含时薛定谔方程（TDSE）

量子力学的基本运动方程：

$$i\hbar \frac{\partial}{\partial t}\Psi(\vec{r}, t) = \hat{H}\Psi(\vec{r}, t)$$

其中：
- $\Psi(\vec{r}, t)$：波函数，包含系统的全部信息
- $\hat{H}$：哈密顿算符（系统总能量的算符）
- $\hbar = h/(2\pi) = 1.055 \times 10^{-34}$ J·s
- $i = \sqrt{-1}$：虚数单位

对于单粒子在势场 $V(\vec{r}, t)$ 中运动：

$$i\hbar \frac{\partial \Psi}{\partial t} = \left[-\frac{\hbar^2}{2m}\nabla^2 + V(\vec{r}, t)\right]\Psi$$

关键特性：
- **线性方程**：如果 $\Psi_1$ 和 $\Psi_2$ 都是解，则 $c_1\Psi_1 + c_2\Psi_2$ 也是解（叠加原理）
- **一阶时间导数**：给定 $\Psi(\vec{r}, 0)$，方程唯一确定所有 $t > 0$ 的 $\Psi(\vec{r}, t)$（确定性演化）
- **保概率**：$\int |\Psi|^2 d^3r = 1$ 在时间演化中保持不变（幺正演化）

### 2. 定态薛定谔方程（TISE）

当势能 $V$ 不随时间变化时，可以**分离变量**：$\Psi(\vec{r}, t) = \psi(\vec{r})e^{-iEt/\hbar}$。代入 TDSE 得到定态方程：

$$\hat{H}\psi(\vec{r}) = E\psi(\vec{r})$$

即：$-\frac{\hbar^2}{2m}\nabla^2\psi + V(\vec{r})\psi = E\psi$

这是一个**本征值问题**：$E$ 是能量本征值，$\psi$ 是对应的本征函数。边界条件（如无穷远处 $\psi \to 0$）限制了允许的 $E$ 值——这就是**能量量子化**的数学起源。

一般解是所有本征态的叠加：$\Psi(\vec{r}, t) = \sum_n c_n \psi_n(\vec{r})e^{-iE_n t/\hbar}$

### 3. 经典可解体系

| 体系 | 势能 $V(x)$ | 能量本征值 | 关键特征 |
|------|------------|-----------|---------|
| 无限深方势阱 | 阱内 0，阱外 $\infty$ | $E_n = \frac{n^2\pi^2\hbar^2}{2mL^2}$ | 量子化能级，零点能 $E_1 \neq 0$ |
| 量子谐振子 | $\frac{1}{2}m\omega^2 x^2$ | $E_n = (n + \frac{1}{2})\hbar\omega$ | 等间距能级，零点能 $\frac{1}{2}\hbar\omega$ |
| 氢原子 | $-\frac{e^2}{4\pi\epsilon_0 r}$ | $E_n = -\frac{13.6 \text{ eV}}{n^2}$ | 与玻尔模型一致，但给出完整量子数 |
| 有限方势垒 | $V_0$（$0 < x < a$） | 连续谱 | 量子隧穿：$T \sim e^{-2\kappa a}$ |

例如，无限深势阱中基态能量 $E_1 = \frac{\pi^2\hbar^2}{2mL^2}$。对于电子（$m = 9.11 \times 10^{-31}$ kg）在 $L = 1$ nm 的阱中，$E_1 \approx 0.38$ eV——这个量级正好与原子和分子中电子的能量相当。

> 思考题：为什么无限深势阱的基态能量不为零？（提示：这与海森堡不确定性原理 $\Delta x \cdot \Delta p \geq \hbar/2$ 有什么关系？）

### 4. 算符与可观测量

量子力学中，每个可观测的物理量对应一个**厄米算符**。薛定谔方程中的哈密顿算符是最重要的例子：

| 物理量 | 算符 | 本征值方程 |
|--------|------|-----------|
| 位置 | $\hat{x} = x$ | $\hat{x}\psi = x\psi$ |
| 动量 | $\hat{p} = -i\hbar\nabla$ | $\hat{p}\psi = p\psi$ → 平面波 |
| 动能 | $\hat{T} = -\frac{\hbar^2}{2m}\nabla^2$ | — |
| 能量 | $\hat{H} = \hat{T} + \hat{V}$ | $\hat{H}\psi_n = E_n\psi_n$ |
| 角动量 z分量 | $\hat{L}_z = -i\hbar\frac{\partial}{\partial\phi}$ | $\hat{L}_z Y_l^m = m\hbar Y_l^m$ |

**测量公理**：测量物理量 $A$ 时，结果必定是对应算符 $\hat{A}$ 的某个本征值 $a_n$，概率为 $|c_n|^2 = |\langle\psi_n|\Psi\rangle|^2$。测量后系统"坍缩"到对应的本征态 $\psi_n$。

### 5. 薛定谔方程的统计诠释

$|\Psi(\vec{r}, t)|^2$ 是**概率密度**——在位置 $\vec{r}$ 附近找到粒子的概率正比于此值。这是 Max Born 于1926年提出的统计诠释（Born, 1926, 获1954年诺贝尔奖）。

核心约束——**归一化条件**：

$$\int_{-\infty}^{\infty} |\Psi(\vec{r}, t)|^2 d^3r = 1$$

粒子必定在空间中某处——总概率为1。薛定谔方程保证：如果波函数在 $t=0$ 时归一化，则在所有后续时刻保持归一化。

**期望值**：物理量 $A$ 的期望值为 $\langle A \rangle = \int \Psi^* \hat{A} \Psi \, d^3r$。例如位置期望值 $\langle x \rangle = \int \Psi^* x \Psi \, dx$——这是多次测量的统计平均值，而非单次测量的结果。

### 6. 适用范围与推广

薛定谔方程的标准形式适用于：
- **非相对论性粒子**（$v \ll c$）：相对论情况需要 Dirac 方程（自旋-1/2 粒子）或 Klein-Gordon 方程（自旋-0）
- **无粒子产生/湮灭**：量子场论处理粒子数变化
- **忽略自旋-轨道耦合等效应时**：精确处理需要引入自旋

即便如此，薛定谔方程已经足以精确描述：原子结构（周期表的理论基础）、化学键（分子轨道理论）、固体能带结构（半导体物理）、量子隧穿（扫描隧道显微镜、alpha衰变）等广泛的物理和化学现象。

## 关键要点

1. **含时薛定谔方程** $i\hbar\partial\Psi/\partial t = \hat{H}\Psi$ 是量子力学的基本运动方程
2. 定态方程 $\hat{H}\psi = E\psi$ 是本征值问题，边界条件导致能量量子化
3. $|\Psi|^2$ 是概率密度（Born 统计诠释），不是实体波
4. 方程是线性的——叠加原理成立，一般解是本征态的线性组合
5. 适用于非相对论量子体系，是理解原子、分子、固体物理的数学核心

## 常见误区

1. **"薛定谔方程可以推导出来"**：不能。它是量子力学的**基本假设**（公设），就像牛顿第二定律不能从更基本的原理推导一样。它的正确性由实验验证。
2. **"波函数是某种物质波"**：$\Psi$ 是复数函数，没有直接的物理实在性。只有 $|\Psi|^2$ 具有可观测意义（概率密度）。
3. **混淆含时与定态方程的适用条件**：定态方程只在势能不含时间时有效。含时势（例如激光场驱动）必须用 TDSE。
4. **"量子化总是出现"**：只有束缚态（如势阱中的粒子）的能量是量子化的。自由粒子（如散射态）的能量是连续的。
5. **"薛定谔方程能精确解所有问题"**：只有少数体系（氢原子、谐振子等）有解析解。多电子原子、分子需要近似方法（变分法、微扰论、数值计算）。

## 历史脉络

| 年份 | 事件 | 意义 |
|------|------|------|
| 1924 | 德布罗意物质波 $\lambda = h/p$ | 粒子具有波动性 |
| 1925 | 海森堡矩阵力学 | 量子力学的第一种数学形式 |
| 1926 | 薛定谔波动力学 | 波动方程形式，更直观 |
| 1926 | Born 统计诠释 | $|\Psi|^2$ 是概率密度 |
| 1927 | 海森堡不确定性原理 | $\Delta x \cdot \Delta p \geq \hbar/2$ |
| 1926 | 薛定谔证明等价性 | 矩阵力学 = 波动力学 |

## 知识衔接

### 先修知识
- **波函数** — $\Psi$ 的物理意义和数学性质是方程的基础
- **物质波（德布罗意波）** — $\lambda = h/p$ 是薛定谔方程的启发来源

### 后续学习
- **无限深方势阱** — 薛定谔方程最简单的解析解，演示量子化的出现
- **量子谐振子** — 用算子方法求解，产生子/湮灭算子引入
- **氢原子量子解** — 三维薛定谔方程在球坐标下的分离变量，给出完整量子数 $(n, l, m_l)$
- **量子隧穿** — 粒子穿透经典禁区的量子效应

## 参考文献

1. Schrodinger, E. (1926). Quantisierung als Eigenwertproblem (I-IV). *Annalen der Physik*, 79-81.
2. Born, M. (1926). Zur Quantenmechanik der Stossprozesse. *Zeitschrift fur Physik*, 37, 863-867.
3. Griffiths, D.J. & Schroeter, D.F. (2018). *Introduction to Quantum Mechanics* (3rd ed.). Cambridge University Press. ISBN 978-1107189638. Ch.1-4.
4. Shankar, R. (1994). *Principles of Quantum Mechanics* (2nd ed.). Springer. ISBN 978-0306447907. Ch.1-5.
