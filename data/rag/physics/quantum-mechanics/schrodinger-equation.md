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
quality_tier: "A"
quality_score: 76.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 薛定谔方程

## 概述

薛定谔方程是量子力学中描述微观粒子波函数随时间演化的基本动力学方程，由奥地利物理学家埃尔温·薛定谔（Erwin Schrödinger）于1926年1月提出。它在量子力学中扮演与牛顿第二定律 $F=ma$ 在经典力学中相同的角色——给定初始条件和势场，方程唯一地决定粒子的波函数在此后所有时刻的状态。

薛定谔方程的诞生源于德布罗意物质波假说与经典波动方程的结合。薛定谔注意到，若粒子具有波长 $\lambda = h/p$ 的物质波，则描述其行为的方程必须与经典波动方程在形式上相容，同时又能反映量子化的能量关系 $E = \hbar\omega$。他用约6周时间推导出该方程，并在同年连续发表了四篇奠基性论文，彻底确立了波动力学的理论体系。

薛定谔方程之所以重要，在于它将粒子的动力学演化完全编码在波函数 $\Psi(\mathbf{r}, t)$ 的变化规律中。原子的能级结构、化学键的本质、半导体器件的工作原理，都可以通过求解薛定谔方程得到定量预测。

---

## 核心原理

### 含时薛定谔方程

含时薛定谔方程（Time-Dependent Schrödinger Equation，TDSE）的一般形式为：

$$i\hbar \frac{\partial \Psi(\mathbf{r}, t)}{\partial t} = \hat{H} \Psi(\mathbf{r}, t)$$

其中 $\hbar = h/(2\pi) \approx 1.055 \times 10^{-34}\ \text{J·s}$ 是约化普朗克常量，$i$ 是虚数单位，$\hat{H}$ 是哈密顿算符。对于在势场 $V(\mathbf{r}, t)$ 中运动的质量为 $m$ 的单粒子，哈密顿算符展开为：

$$\hat{H} = -\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r}, t)$$

第一项对应动能，其中 $\nabla^2$ 是拉普拉斯算符；第二项对应势能。方程左侧的 $i\hbar \partial/\partial t$ 可理解为能量算符作用于时间维度，这与普朗克-爱因斯坦关系 $E = \hbar\omega$ 直接对应。值得注意的是，方程对时间是**一阶**的，这意味着只需知道 $t=0$ 时刻的波函数 $\Psi(\mathbf{r}, 0)$，即可原则上确定所有未来时刻的波函数。

### 定态薛定谔方程

当势场不显含时间，即 $V = V(\mathbf{r})$ 时，可用分离变量法令 $\Psi(\mathbf{r}, t) = \psi(\mathbf{r}) \cdot f(t)$。将其代入含时方程后，时间部分给出 $f(t) = e^{-iEt/\hbar}$，空间部分则得到**定态薛定谔方程**（Time-Independent Schrödinger Equation，TISE）：

$$\hat{H}\psi(\mathbf{r}) = E\psi(\mathbf{r})$$

这是哈密顿算符的本征值方程。方程中 $E$ 是能量本征值，$\psi(\mathbf{r})$ 是对应的能量本征态（定态波函数）。一维情形下方程化为：

$$-\frac{\hbar^2}{2m}\frac{d^2\psi}{dx^2} + V(x)\psi = E\psi$$

定态波函数本身不随时间改变（概率密度 $|\psi|^2$ 与时间无关），但完整的波函数仍携带相位因子 $e^{-iEt/\hbar}$，这一相位在量子干涉现象中具有可观测效应。

### 算符形式与对应原理

薛定谔方程中的物理量以算符形式出现，这反映了量子力学的基本规则：将经典力学中的动量 $p$ 替换为算符 $\hat{p} = -i\hbar\nabla$，将坐标 $x$ 替换为乘法算符 $\hat{x} = x$。哈密顿算符 $\hat{H} = \hat{p}^2/(2m) + V(\hat{x})$ 正是由此构造而来，这种替换规则称为**正则量子化**。

动量算符和位置算符满足对易关系 $[\hat{x}, \hat{p}] = i\hbar$，这是海森堡不确定原理 $\Delta x \cdot \Delta p \geq \hbar/2$ 的数学根源。薛定谔方程的算符形式使得量子力学的矩阵力学（海森堡表象）与波动力学（薛定谔表象）得以统一——两者在数学上等价，1930年由狄拉克的变换理论正式证明。

---

## 实际应用

**氢原子能级**：对氢原子求解定态薛定谔方程，其中 $V(r) = -e^2/(4\pi\epsilon_0 r)$，得到的能量本征值为 $E_n = -13.6\ \text{eV}/n^2$（$n = 1, 2, 3, \ldots$）。这一结果与玻尔模型的预测一致，但薛定谔方程额外给出了完整的轨道角动量量子数 $\ell$ 和磁量子数 $m_\ell$，从而解释了氢原子谱线的精细结构。

**量子隧穿**：在矩形势垒 $V_0 > E$ 的情况下，定态方程在势垒区域的解不为零，而是指数衰减的 $\psi \propto e^{-\kappa x}$，其中 $\kappa = \sqrt{2m(V_0-E)}/\hbar$。正是薛定谔方程允许波函数渗入经典禁区，才从理论上预言了核衰变（α粒子隧穿）和隧道二极管等现象。

**谐振子能级**：一维量子谐振子的势能为 $V = m\omega^2 x^2/2$，求解定态方程得到等间距能级 $E_n = (n+1/2)\hbar\omega$。其中零点能 $E_0 = \hbar\omega/2 \neq 0$ 是纯粹的量子效应，是薛定谔方程与经典物理最直接的定量区别之一。

---

## 常见误区

**误区一：将薛定谔方程等同于"推导出来的"结果**。薛定谔方程无法从更基本的原理严格推导，它是量子力学的一条**基本公设**，其正确性只能通过与实验的吻合来验证。薛定谔本人的"推导"过程实际上是启发性的类比，不构成逻辑推导。

**误区二：认为定态就意味着粒子静止**。处于能量本征态 $\psi_n$ 的粒子，其概率密度 $|\psi_n(\mathbf{r})|^2$ 不随时间变化，但粒子仍有动量的不确定性——以氢原子基态为例，电子动能的期望值为 $\langle T \rangle = 13.6\ \text{eV}$，远非静止。"定态"指的是能量测量结果确定，而非运动静止。

**误区三：含时方程与定态方程适用范围混淆**。定态方程仅在哈密顿量不显含时间时成立；当存在时变外场（如激光场）时，必须使用含时薛定谔方程。许多教材从定态入手讲解，容易使学生误以为定态方程是更一般的形式，实则相反——含时方程才是最一般的表述。

---

## 知识关联

薛定谔方程以**波函数**为求解对象——没有对波函数 $\Psi(\mathbf{r},t)$ 的统计诠释（波恩规则：$|\Psi|^2$ 为概率密度）和归一化条件，方程的解在物理上没有意义。因此，掌握波函数的性质是理解方程边界条件（波函数连续、一阶导数连续）的前提。

解方程的直接结果通向多个具体量子体系：**无限深方势阱**是最简单的定态方程范例，给出 $E_n \propto n^2$ 的分立能级；**量子谐振子**引入升降算符方法，是代数解法的原型；**氢原子量子解**则是三维球坐标下方程的完整求解，产生 $n, \ell, m_\ell$ 三个量子数。理解薛定谔方程中哈密顿算符的结构，还直接引出**算符与可观测量**的一般理论，以及**量子隧穿**中波函数在经典禁区衰减的定量计算。