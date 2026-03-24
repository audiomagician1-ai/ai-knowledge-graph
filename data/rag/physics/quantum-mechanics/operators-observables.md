---
id: "operators-observables"
concept: "算符与可观测量"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 算符与可观测量

## 概述

在量子力学中，经典力学里的物理量（如位置、动量、能量）被替换为作用于希尔伯特空间上的**算符（operator）**。一个可观测量（observable）必须对应一个**厄米算符**（Hermitian operator，又称自伴算符），其数学定义为 $\hat{A} = \hat{A}^\dagger$，即算符等于其自身的共轭转置。这一要求不是任意约定，而是保证测量结果为实数的必要条件——只有厄米算符的本征值才保证全部为实数。

量子力学的算符形式体系由狄拉克（Paul Dirac）在20世纪20年代末系统化，他于1930年出版的《量子力学原理》（*The Principles of Quantum Mechanics*）将算符语言推广为标准框架。在此之前，海森堡的矩阵力学（1925年）和薛定谔的波动力学（1926年）各自独立发展，而算符语言将两者统一到同一形式体系中。

算符框架的核心意义在于：量子系统的状态 $|\psi\rangle$ 本身不是可观测量，只有通过算符作用才能提取物理信息。对可观测量 $\hat{A}$ 的测量期望值由 $\langle \hat{A} \rangle = \langle \psi | \hat{A} | \psi \rangle$ 给出，这一公式将希尔伯特空间的抽象内积与实验室中的测量数据直接联系起来。

---

## 核心原理

### 厄米算符与本征值方程

厄米算符的**本征值方程**写为：

$$\hat{A} |\phi_n\rangle = a_n |\phi_n\rangle$$

其中 $|\phi_n\rangle$ 称为本征态，$a_n$ 为对应本征值。厄米性保证了两个关键结论：

1. **所有本征值 $a_n$ 为实数**（这对应测量结果的实数性）。
2. **不同本征值对应的本征态相互正交**，即 $\langle \phi_m | \phi_n \rangle = \delta_{mn}$。

以一维无限深势阱中的哈密顿算符 $\hat{H} = -\frac{\hbar^2}{2m}\frac{d^2}{dx^2}$ 为例，其本征值为 $E_n = \frac{n^2\pi^2\hbar^2}{2mL^2}$（$n=1,2,3,\ldots$），这些离散本征值正是量子化能级的来源。薛定谔方程本质上就是哈密顿算符的本征值方程（定态情形）。

### 对易关系与不确定性原理

两个算符 $\hat{A}$ 与 $\hat{B}$ 的**对易子（commutator）**定义为：

$$[\hat{A}, \hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A}$$

最基础的正则对易关系为：

$$[\hat{x}, \hat{p}] = i\hbar$$

这一关系不依赖于任何具体表象，是量子力学区别于经典力学的核心代数结构。由此可以严格推导出**Robertson不确定性关系**：

$$\sigma_A \sigma_B \geq \frac{1}{2}|\langle[\hat{A}, \hat{B}]\rangle|$$

对于位置和动量，代入 $[\hat{x}, \hat{p}] = i\hbar$，立即得到海森堡不确定性原理 $\sigma_x \sigma_p \geq \hbar/2$。对易子为零意味着两个可观测量可以同时被精确测量（具有共同本征态基），非零则意味着二者不可同时精确确定。

### 算符的坐标表示与动量表示

在坐标表象中，位置算符和动量算符分别表示为：

$$\hat{x} = x \cdot \quad (\text{乘以} x), \qquad \hat{p} = -i\hbar \frac{\partial}{\partial x}$$

这一具体表示形式使抽象算符方程变为偏微分方程，是薛定谔波函数方法的基础。在动量表象中，两者对调：$\hat{p} = p \cdot$，$\hat{x} = i\hbar \frac{\partial}{\partial p}$。两种表象通过傅里叶变换相互联系，验证了同一对易关系 $[\hat{x},\hat{p}]=i\hbar$ 在不同表象下的一致性。

### 测量假设与投影

当对处于状态 $|\psi\rangle = \sum_n c_n |\phi_n\rangle$ 的系统测量可观测量 $\hat{A}$ 时，得到本征值 $a_n$ 的概率为 $|c_n|^2 = |\langle \phi_n | \psi \rangle|^2$。测量后系统**坍缩**到对应本征态 $|\phi_n\rangle$，这一过程由投影算符 $\hat{P}_n = |\phi_n\rangle\langle\phi_n|$ 描述。投影算符满足 $\hat{P}_n^2 = \hat{P}_n$（幂等性）以及 $\sum_n \hat{P}_n = \hat{I}$（完备性），后者表明所有本征态构成完备基。

---

## 实际应用

**谐振子的阶梯算符**：一维量子谐振子引入升降算符 $\hat{a}^\dagger$ 和 $\hat{a}$，满足 $[\hat{a}, \hat{a}^\dagger] = 1$。哈密顿量化简为 $\hat{H} = \hbar\omega(\hat{a}^\dagger\hat{a} + \frac{1}{2})$，粒子数算符 $\hat{N} = \hat{a}^\dagger\hat{a}$ 的本征值为非负整数 $n$，直接给出能级 $E_n = (n+\frac{1}{2})\hbar\omega$。这一纯代数方法完全绕开了求解微分方程的过程。

**自旋算符**：自旋-1/2粒子的泡利矩阵 $\sigma_x, \sigma_y, \sigma_z$ 满足对易关系 $[\sigma_i, \sigma_j] = 2i\epsilon_{ijk}\sigma_k$。自旋算符 $\hat{S}_z = \frac{\hbar}{2}\sigma_z$ 的本征值为 $\pm\hbar/2$，对应自旋向上和向下两个本征态 $|\uparrow\rangle$ 和 $|\downarrow\rangle$。核磁共振（NMR）技术的物理基础正是自旋算符的本征值结构。

**守恒量判断**：若算符 $\hat{A}$ 与哈密顿量满足 $[\hat{A}, \hat{H}] = 0$，则 $\hat{A}$ 对应的物理量守恒，其期望值不随时间变化（Ehrenfest定理的推广）。例如，中心势场中角动量算符 $[\hat{L}, \hat{H}] = 0$，因此角动量守恒。

---

## 常见误区

**误区一：将算符等同于矩阵**。虽然在有限维希尔伯特空间中算符可以表示为矩阵，但连续谱算符（如位置算符 $\hat{x}$）无法用有限阶矩阵表示。位置算符的"本征态" $\delta(x-x_0)$ 是广义函数而非平方可积函数，不属于严格意义上的希尔伯特空间，需要用黎格尔德-盖尔范德三元组（rigged Hilbert space）来处理。

**误区二：对易量可以同时具有确定值等价于算符完全相同**。$[\hat{A}, \hat{B}] = 0$ 只意味着存在共同本征态基，而不是 $\hat{A} = \hat{B}$。例如，$\hat{H}$ 与 $\hat{N}$（谐振子粒子数算符）对易，但二者差一个常数 $\hbar\omega/2$ 且物理意义完全不同。

**误区三：厄米性与幺正性混淆**。厄米算符 $\hat{A}^\dagger = \hat{A}$ 描述可观测量；幺正算符 $\hat{U}^\dagger = \hat{U}^{-1}$ 描述时间演化（如 $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$）和对称变换。$\hat{H}$ 是厄米算符，但时间演化算符 $e^{-i\hat{H}t/\hbar}$ 是幺正算符，本征值为模为1的复数，而非实数。

---

## 知识关联

**与薛定谔方程的联系**：薛定谔方程 $i\hbar\frac{\partial}{\partial t}|\psi\rangle = \hat{H}|\psi\rangle$ 本质上是哈密顿算符驱动的态矢量演化方程，定态薛定谔方程就是 $\hat{H}$ 的本征值方程。掌握算符语言后，薛定谔方程从一个偏微分方程提升为抽象算符方程，具有表象无关的普适性。

**通向量子角动量**：角动量算符 $\hat{L} = \hat{r} \times \hat{p}$ 及其分量满足 $[\hat{L}_x, \hat{L}_y] = i\hbar\hat{L}_z$（及轮换），这一对易关系完全决定了角动量的量子化条件（$l = 0, \frac{1}{2}, 1, \frac{3}{2},\ldots$）和磁量子数范
