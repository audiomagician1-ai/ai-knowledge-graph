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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 算符与可观测量

## 概述

在量子力学中，经典物理中的每一个可观测物理量（如位置、动量、能量）都对应一个作用于希尔伯特空间的**线性算符**。这一对应关系不仅是形式上的替换，而是量子力学的基本公设之一：测量某个物理量的可能结果，恰好是对应算符的本征值。例如，位置算符 $\hat{x}$ 在坐标表象下就是乘以 $x$，而动量算符 $\hat{p} = -i\hbar \frac{\partial}{\partial x}$，其中 $\hbar \approx 1.055 \times 10^{-34}\ \text{J·s}$。

这一框架由狄拉克（Paul Dirac）在1930年出版的《量子力学原理》中系统化，他引入了左矢（bra）和右矢（ket）记号，将算符表示为 $\hat{A}|\psi\rangle$，使抽象的希尔伯特空间运算变得直观可操作。海森堡早在1925年以矩阵力学形式提出了类似思想，证明物理量应以矩阵而非数值表示。

这一框架之所以不可绕过，是因为它解释了量子测量结果为何是**离散的**——氢原子能级只能取 $E_n = -13.6/n^2\ \text{eV}$，这正是哈密顿算符的离散本征值，而非连续变化的经典能量。

---

## 核心原理

### 厄米算符（Hermitian Operator）

可观测量必须对应**厄米算符**，即满足 $\hat{A} = \hat{A}^\dagger$ 的算符，其中 $\hat{A}^\dagger$ 是 $\hat{A}$ 的厄米共轭。厄米性保证两个关键性质：

1. 所有本征值均为**实数**（因为测量值必须是实数）。
2. 属于不同本征值的本征态彼此**正交**：$\langle a_i | a_j \rangle = \delta_{ij}$。

验证动量算符的厄米性：对任意归一化波函数 $\phi, \psi$，有 $\langle \phi | \hat{p} \psi \rangle = \langle \hat{p} \phi | \psi \rangle$，这依赖于波函数在无穷远处趋于零的边界条件。若边界条件不满足（如无限深方势阱外的续延问题），算符可能只是**对称**（symmetric）而非严格厄米，此区别在数学物理中至关重要。

### 本征值方程与谱分解

算符 $\hat{A}$ 的本征值方程为：
$$\hat{A}|\psi_n\rangle = a_n|\psi_n\rangle$$
其中 $a_n$ 是本征值，$|\psi_n\rangle$ 是对应本征态。若 $\hat{A}$ 的谱是离散的，系统任意态可展开为：
$$|\Psi\rangle = \sum_n c_n |\psi_n\rangle, \quad c_n = \langle \psi_n | \Psi \rangle$$
测量 $\hat{A}$ 得到 $a_n$ 的概率为 $|c_n|^2$（玻恩规则），测量后系统**坍缩**到 $|\psi_n\rangle$。这一展开定理对厄米算符成立，构成了量子力学"测量假设"的完整数学表述。

测量期望值公式为：
$$\langle \hat{A} \rangle = \langle \Psi | \hat{A} | \Psi \rangle = \sum_n a_n |c_n|^2$$

### 对易关系（Commutation Relations）

两个算符 $\hat{A}$ 与 $\hat{B}$ 的**对易子**定义为：
$$[\hat{A}, \hat{B}] = \hat{A}\hat{B} - \hat{B}\hat{A}$$

- 若 $[\hat{A}, \hat{B}] = 0$，两者**对易**，可同时精确测量，且共享完整的本征态基。
- 最重要的**正则对易关系**：$[\hat{x}, \hat{p}] = i\hbar$，这直接导出海森堡不确定性原理 $\sigma_x \sigma_p \geq \hbar/2$。
- 哈密顿量 $\hat{H}$ 与某算符 $\hat{A}$ 对易 $[\hat{H}, \hat{A}] = 0$，意味着 $\hat{A}$ 对应的物理量**守恒**（不随时间演化），这是诺特定理的量子力学版本。

三维角动量分量满足 $[\hat{L}_x, \hat{L}_y] = i\hbar\hat{L}_z$（及其轮换），因此 $L_x$ 与 $L_y$ **不能**同时精确确定，只有 $\hat{L}^2$ 与任意一个分量（通常取 $\hat{L}_z$）才能对易，形成完全对易可观测量集合（CSCO）。

---

## 实际应用

**谐振子的阶梯算符**：定义升降算符 $\hat{a}^\pm = \frac{1}{\sqrt{2m\hbar\omega}}(m\omega\hat{x} \mp i\hat{p})$，可以证明 $[\hat{a}^-, \hat{a}^+] = 1$，且哈密顿量化为 $\hat{H} = \hbar\omega(\hat{a}^+\hat{a}^- + 1/2)$。由此无需解微分方程，仅通过代数方法即可得到能级 $E_n = (n+1/2)\hbar\omega$，并计算矩阵元 $\hat{a}^+|n\rangle = \sqrt{n+1}|n+1\rangle$。

**自旋算符**：电子自旋用泡利矩阵表示，$\hat{S}_z = \frac{\hbar}{2}\sigma_z$，$\sigma_z = \begin{pmatrix}1 & 0 \\ 0 & -1\end{pmatrix}$，本征值为 $\pm\hbar/2$，对应自旋向上/向下两个态。斯特恩-格拉赫实验（1922年）中银原子束被磁场分裂为两束，直接观测到 $\hat{S}_z$ 的离散本征谱。

**选择定则**：在氢原子跃迁中，利用角动量算符与偶极矩算符的对易性，可以推导出电偶极跃迁的选择定则 $\Delta l = \pm 1$，$\Delta m = 0, \pm 1$，这正是通过计算矩阵元 $\langle n'l'm'|\hat{r}|nlm\rangle$ 是否为零得出的。

---

## 常见误区

**误区一：所有算符都是可观测量**。实际上，宇称算符 $\hat{P}$ 是厄米的但在弱相互作用中不守恒；而时间演化算符 $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$ 是**幺正**而非厄米算符，时间 $t$ 在量子力学中是参数而非算符（相对论量子力学例外）。只有厄米算符对应可测量量，幺正算符描述演化。

**误区二：对易量的本征态总是唯一的**。当本征值发生**简并**时（同一本征值对应多个线性独立的本征态），引入另一个与 $\hat{A}$ 对易的算符 $\hat{B}$，才能完全消除简并，确定唯一的物理态。氢原子能级 $E_n$ 对应 $n^2$ 重简并，需要同时用 $\hat{H}$、$\hat{L}^2$、$\hat{L}_z$ 三个算符（CSCO）才能唯一标记量子态 $|n, l, m\rangle$。

**误区三：期望值等于某次测量的结果**。$\langle \hat{A} \rangle$ 是多次重复测量的统计平均，单次测量只能得到某个本征值 $a_n$，而 $\langle \hat{A} \rangle$ 可以是本征值之外的任何值（例如，自旋处于叠加态时 $\langle \hat{S}_z \rangle$ 可以是 $0$，但每次测量只得 $\pm\hbar/2$）。

---

## 知识关联

**与薛定谔方程的联系**：薛定谔方程 $i\hbar \partial_t |\Psi\rangle = \hat{H}|\Psi\rangle$ 本质上是哈密顿算符的本征值问题——定态薛定谔方程 $\hat{H}|\psi_n\rangle = E_n|\psi_n\rangle$ 就是求 $\hat{H}$ 的本征谱。掌握算符语言后，能量本征态问题化为线性代数问题，这是全部量子力学计算的出发点。

**通向量子角动量**：$[\hat{L}_i, \hat{L}_j] = i\hbar\epsilon_{ijk}\hat{L}_k$ 的代数结构直接决定了角动量量子数 $l = 0, 1/2, 1, 3/2, \ldots$ 的取值规则，自旋与轨道角动量的合成（C-G系数）完全建立在这一对易代数之上。

**通向微扰理论**：微扰论的核心操作是计算矩阵元 $\langle n|\hat{H}'|m \rangle$，其中 $\hat{H}'$ 是微扰哈密顿算符，而分母中出现能量差 $E_n - E_m$——若 