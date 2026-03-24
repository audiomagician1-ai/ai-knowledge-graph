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
quality_tier: "pending-rescore"
quality_score: 41.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 哈密顿力学初步

## 概述

哈密顿力学是经典力学的一种表述形式，由爱尔兰数学家威廉·罗文·哈密顿（William Rowan Hamilton）于1833年提出。它以广义坐标 $q_i$ 和广义动量 $p_i$ 作为独立变量，将力学问题转化为在**相空间**中研究系统的演化，而非在配置空间中求解运动方程。这一转变使原本 $n$ 个二阶微分方程变为 $2n$ 个一阶微分方程，在数学结构上更为对称优美。

哈密顿力学脱胎于拉格朗日力学，通过勒让德变换（Legendre Transform）将拉格朗日量 $L(q, \dot{q}, t)$ 转化为哈密顿量 $H(q, p, t)$。虽然两种表述在物理预言上完全等价，但哈密顿框架揭示了力学系统更深层的几何结构，成为量子力学、统计力学和混沌理论的直接出发点——量子力学中的算符对易关系 $[\hat{q}, \hat{p}] = i\hbar$ 正是泊松括号的量子化推广。

## 核心原理

### 哈密顿量的定义与构造

哈密顿量 $H$ 通过对拉格朗日量做勒让德变换得到。首先定义广义动量：

$$p_i = \frac{\partial L}{\partial \dot{q}_i}$$

随后构造哈密顿量：

$$H(q_i, p_i, t) = \sum_i p_i \dot{q}_i - L(q_i, \dot{q}_i, t)$$

对于保守系统，若约束不含时且动能是广义速度的二次齐次函数，则 $H$ 等于系统的**总机械能** $T + V$。例如单摆系统中，$H = \frac{p_\theta^2}{2ml^2} + mgl(1 - \cos\theta)$，其中 $p_\theta = ml^2\dot{\theta}$ 是关于摆角的广义动量。但需注意，若约束含时（如摆长随时间变化），$H \neq T + V$，此时哈密顿量不再等于总能量。

### 哈密顿正则方程

哈密顿力学的核心方程——**正则方程（Hamilton's canonical equations）**——为：

$$\dot{q}_i = \frac{\partial H}{\partial p_i}, \qquad \dot{p}_i = -\frac{\partial H}{\partial q_i}$$

对于一个有 $n$ 个自由度的系统，这给出 $2n$ 个联立的一阶常微分方程。以一维谐振子为例，$H = \frac{p^2}{2m} + \frac{1}{2}kq^2$，正则方程给出 $\dot{q} = p/m$，$\dot{p} = -kq$，直接导出 $\ddot{q} = -(k/m)q$，与牛顿方程完全一致。正则方程的对称性体现在：$q$ 和 $p$ 的地位几乎等同，仅差一个负号，这种内在对称性称为**辛对称性（symplectic symmetry）**。

### 相空间与刘维尔定理

相空间是以所有广义坐标 $q_1, \ldots, q_n$ 和广义动量 $p_1, \ldots, p_n$ 为坐标轴构成的 $2n$ 维空间。系统在某时刻的状态对应相空间中的一个**点**，随时间演化形成**相轨道（phase trajectory）**。对于能量守恒系统，相轨道被限制在满足 $H(q, p) = E$ 的超曲面上，即**等能面**。一维谐振子的相轨道是椭圆方程 $\frac{p^2}{2mE} + \frac{kq^2}{2E} = 1$ 描述的椭圆。

**刘维尔定理（Liouville's theorem，1838年）**是相空间中的重要结论：在哈密顿系统的演化下，相空间中代表点集合所占据的体积（相体积）保持不变。数学表达为相空间流的散度为零：$\sum_i \left(\frac{\partial \dot{q}_i}{\partial q_i} + \frac{\partial \dot{p}_i}{\partial p_i}\right) = 0$，这直接由正则方程的结构保证。

### 泊松括号

泊松括号（Poisson bracket）定义为：

$$\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)$$

任意力学量 $f(q, p, t)$ 的时间演化方程可写成 $\dot{f} = \{f, H\} + \frac{\partial f}{\partial t}$。若 $\{f, H\} = 0$ 且 $f$ 不显含时间，则 $f$ 是运动积分（守恒量）。正则坐标满足基本泊松括号：$\{q_i, p_j\} = \delta_{ij}$，$\{q_i, q_j\} = \{p_i, p_j\} = 0$。

## 实际应用

**开普勒问题（行星轨道）**：在极坐标中，二体问题的哈密顿量为 $H = \frac{p_r^2}{2\mu} + \frac{p_\theta^2}{2\mu r^2} - \frac{k}{r}$，其中 $\mu$ 为约化质量。由于 $\theta$ 是循环坐标（$H$ 不显含 $\theta$），正则方程立即给出 $\dot{p}_\theta = 0$，即角动量守恒，无需另立论据。

**绝热不变量**：对于缓慢变化参数的系统，相空间中封闭相轨道围成的面积 $J = \oint p \, dq$ 是绝热不变量。这一结论在量子力学建立前（玻尔-索末菲量子化条件，1916年）曾用于量子化条件 $J = nh$，是哈密顿力学直接服务于早期量子论的历史案例。

**分子动力学模拟**：现代计算中，分子动力学程序（如GROMACS、LAMMPS）本质上是对哈密顿正则方程的数值积分，辛积分算法（如Verlet算法）利用相体积守恒保证长时间模拟的能量稳定性。

## 常见误区

**误区一：哈密顿量总等于总能量。** 许多学生默认 $H = T + V$，但这一等式成立的前提是：约束不含时，且势能不含广义速度（即无速度相关势）。对于含时约束（如以恒定角速度旋转的约束面），变换到旋转坐标后 $H$ 仍守恒，但其值不等于惯性系中的 $T + V$。正确做法是严格按勒让德变换定义计算 $H$，然后单独判断 $H$ 是否为守恒量（判据：$\partial H / \partial t = 0$）。

**误区二：广义动量就是质量乘速度 $mv$。** 广义动量 $p_i = \partial L / \partial \dot{q}_i$ 的具体形式取决于广义坐标的选取和系统的约束。对于带电粒子在磁场中的运动，广义动量为 $p = mv + qA$（其中 $A$ 是矢势），包含额外的电磁项。在极坐标中，角向广义动量是角动量 $p_\theta = mr^2\dot{\theta}$，量纲亦与线动量不同。

**误区三：哈密顿力学仅是拉格朗日力学的"改写"，无额外内容。** 两者物理预言等价，但哈密顿力学在分析**对称性**和**守恒量**时更为系统——循环坐标直接对应守恒的广义动量，泊松括号提供了统一的守恒量判别工具。此外，辛结构和正则变换理论（如作用量-角变量方法）是拉格朗日框架中没有对应概念的独特工具。

## 知识关联

哈密顿力学直接建立在拉格朗日力学之上：拉格朗日量 $L$ 是哈密顿量 $H$ 的源头，勒让德变换是连接两者的唯一数学桥梁。学生需要熟练掌握从 $L$ 计算广义动量 $p_i$，以及反解 $\dot{q}_i(q, p, t)$ 以完成变量替换的技巧，否则无法正确写出哈密顿量。

在后续方向上，哈密顿力学直接支撑三个重要领域：其一，**哈密顿-雅可比方程**（Hamilton-Jacobi equation）$\frac{\partial S}{\partial t} + H\left(q, \frac{\partial S}{\partial q}, t\right) = 0$ 将力学问题转化为偏微分方程，是经典力学与波动力学之间的过渡；其二，**正则变换**理论允许选择最方便的相空间坐标，将某些复杂系统化为可积形式；其三，统计力学中的**玻尔兹曼分布** $\rho \propto e^{-H/k_BT}$ 正是以哈密顿量作为权重，刘维尔定理保证了平衡态统计分布的自洽性。
