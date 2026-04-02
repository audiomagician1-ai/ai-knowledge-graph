---
id: "angular-momentum-qm"
concept: "量子角动量"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 量子角动量

## 概述

量子角动量是描述微观粒子旋转状态的物理量，其数学结构与经典角动量 **L = r × p** 截然不同。经典力学中角动量可取任意连续值，而量子力学中角动量的大小和空间分量均被严格量子化，只能取离散值。这一性质由1913年玻尔的氢原子模型初步揭示，但真正严格的量子角动量理论由海森堡、狄拉克等人在1920年代通过对易关系框架建立。

量子角动量分为**轨道角动量**（来自粒子的空间运动）和**自旋角动量**（粒子固有属性，无经典对应），两者均服从相同的代数结构。轨道角动量量子化直接决定了原子中电子的能级结构，是氢原子光谱线系（巴尔末系、赖曼系等）得到精确解释的理论基础。正是因为角动量量子化，元素周期表中各族元素的化学性质才呈现出有规律的重复。

对量子角动量的掌握，要求学生已具备算符与可观测量的基础，尤其是对易子的计算方法。量子角动量的完整理论是后续导出光学跃迁选择定则的直接前提——选择定则本质上是角动量守恒对光子吸收/辐射过程的约束。

---

## 核心原理

### 角动量算符的对易关系

量子角动量的一切性质源于三个分量算符 $\hat{L}_x, \hat{L}_y, \hat{L}_z$ 之间的基本对易关系：

$$[\hat{L}_x, \hat{L}_y] = i\hbar\hat{L}_z, \quad [\hat{L}_y, \hat{L}_z] = i\hbar\hat{L}_x, \quad [\hat{L}_z, \hat{L}_x] = i\hbar\hat{L}_y$$

可紧凑写作 $\hat{\mathbf{L}} \times \hat{\mathbf{L}} = i\hbar\hat{\mathbf{L}}$。这三个关系说明，角动量的三个分量不能同时精确测量（它们互不对易）。但总角动量平方算符 $\hat{L}^2 = \hat{L}_x^2 + \hat{L}_y^2 + \hat{L}_z^2$ 与每个分量均对易：$[\hat{L}^2, \hat{L}_i] = 0$，因此可以同时给定 $\hat{L}^2$ 和 $\hat{L}_z$ 的本征值。

### 量子数与本征值谱

$\hat{L}^2$ 和 $\hat{L}_z$ 的共同本征态 $|l, m\rangle$ 满足：

$$\hat{L}^2 |l, m\rangle = \hbar^2 l(l+1)|l, m\rangle, \quad \hat{L}_z |l, m\rangle = m\hbar |l, m\rangle$$

其中**轨道量子数** $l = 0, 1, 2, 3, \ldots$（分别对应 s, p, d, f 轨道），**磁量子数** $m = -l, -l+1, \ldots, l-1, l$，共 $2l+1$ 个取值。注意角动量大小为 $\hbar\sqrt{l(l+1)}$ 而非 $\hbar l$——两者之差来自量子零点涨落，是纯粹的量子效应。对于 $l=1$ 的 p 轨道，角动量大小为 $\hbar\sqrt{2} \approx 1.414\hbar$，而非经典直觉给出的 $\hbar$。

升降算符 $\hat{L}_{\pm} = \hat{L}_x \pm i\hat{L}_y$ 的作用为：

$$\hat{L}_{\pm}|l,m\rangle = \hbar\sqrt{l(l+1) - m(m\pm 1)}\,|l, m\pm 1\rangle$$

这一公式是代数求解角动量本征谱的核心工具，无需求解微分方程即可推导出所有本征值。

### 角动量耦合与 Clebsch-Gordan 系数

当体系含两个角动量 $\hat{\mathbf{J}}_1$（量子数 $j_1$）和 $\hat{\mathbf{J}}_2$（量子数 $j_2$）时，总角动量 $\hat{\mathbf{J}} = \hat{\mathbf{J}}_1 + \hat{\mathbf{J}}_2$ 的量子数 $j$ 满足**三角不等式**：

$$|j_1 - j_2| \leq j \leq j_1 + j_2, \quad j \text{ 以整数步长变化}$$

例如，两个 $j_1 = j_2 = 1$ 的角动量耦合，可得 $j = 0, 1, 2$，对应三个子空间，维度分别为 1、3、5，总和 $1+3+5=9 = (2\times1+1)^2$，维度守恒。

从非耦合基 $|j_1, m_1\rangle|j_2, m_2\rangle$ 变换到耦合基 $|j, m\rangle$ 的变换系数称为 **Clebsch-Gordan 系数**（C-G 系数）：

$$|j, m\rangle = \sum_{m_1+m_2=m} \langle j_1, m_1; j_2, m_2 | j, m\rangle\, |j_1, m_1\rangle|j_2, m_2\rangle$$

C-G 系数在原子物理、核物理和粒子物理中无处不在，标准值可查阅 Particle Data Group 发布的表格。

---

## 实际应用

**氢原子光谱的精细结构**：氢原子中电子的轨道角动量 $l$ 与自旋 $s=1/2$ 耦合，总角动量 $j = l \pm 1/2$（当 $l>0$ 时）。这种 LS 耦合导致能级分裂，例如钠 D 线（589 nm）实为两条谱线（$D_1$ 589.6 nm，$D_2$ 589.0 nm），差值正是由 $3p_{1/2}$ 和 $3p_{3/2}$ 两个 $j$ 值对应的能级差引起。

**施特恩-格拉赫实验**：1922 年施特恩和格拉赫将银原子束通过非均匀磁场，发现原子束分裂为 **2 条**而非连续分布。银原子基态 $l=0$，自旋 $s=1/2$，故磁量子数 $m_s = \pm 1/2$，只有两个取值——这是角动量空间量子化的直接实验证据，也是自旋概念的历史起点。

**核磁共振（NMR）**：质子自旋 $I=1/2$ 在外磁场中分裂为 $m_I = +1/2$（平行）和 $m_I = -1/2$（反平行）两个能级，能量差为 $\Delta E = \gamma\hbar B_0$，其中 $\gamma$ 为旋磁比。1 T 外磁场下质子的共振频率约为 42.6 MHz。整个 NMR 技术（以及医学 MRI）完全建立在角动量量子化的基础上。

---

## 常见误区

**误区一：角动量大小等于 $l\hbar$**。许多初学者把 $\hat{L}_z$ 的本征值 $m\hbar$ 与角动量大小混淆。正确的大小是 $\hbar\sqrt{l(l+1)}$，对 $l=1$ 而言是 $\hbar\sqrt{2}$，不是 $\hbar$。这个"额外的"量子涨落无法通过任何测量消除，是海森堡不确定原理在角动量上的体现——若角动量大小恰为 $l\hbar$，则角动量矢量严格指向某轴，与 $L_x, L_y$ 必须有涨落矛盾。

**误区二：耦合后 $j$ 可取任意值**。在两角动量 $j_1, j_2$ 耦合时，$j$ 不是连续变化，也不是仅取 $j_1+j_2$，而是从 $|j_1-j_2|$ 到 $j_1+j_2$ 以**整数**步长取一系列离散值。例如 $j_1=3/2, j_2=1/2$ 耦合，$j$ 只能取 1 和 2，不存在 $j=1.5$ 的态。忽略这一步长规则会导致在多电子体系耦合计算中遗漏或多算子空间。

**误区三：轨道角动量量子数 $l$ 可取半整数**。对于描述粒子**空间运动**的轨道角动量，$l$ 必须为非负整数（$0,1,2,\ldots$），因为对应的球谐函数 $Y_l^m(\theta,\phi)$ 要求波函数在 $\phi \to \phi+2\pi$ 时单值回到原值。而自旋角动量不受此限制，可取半整数（如电子 $s=1/2$，$\Delta^{++}$ 重子 $s=3/2$）。将两类约束混用是初学者的高频错误。

---

## 知识关联

**向上衔接算符理论**：量子角动量的整个代数结构依赖对易子 $[A, B] = AB - BA$ 的运算规则，以及厄米算符本征值为实数的定理——这些均属于算符与可观测量的核心内容。升降算符方法也是算符代数技术的典型应用。

**向