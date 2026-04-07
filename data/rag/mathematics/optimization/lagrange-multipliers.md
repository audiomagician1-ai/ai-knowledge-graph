---
id: "lagrange-multipliers"
concept: "拉格朗日乘数法"
domain: "mathematics"
subdomain: "optimization"
subdomain_name: "最优化"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 拉格朗日乘数法

## 概述

拉格朗日乘数法（Lagrange Multiplier Method）是求解等式约束优化问题的经典分析方法，由意大利数学家约瑟夫-路易·拉格朗日（Joseph-Louis Lagrange）于1788年在其著作《分析力学》（*Mécanique analytique*）中系统提出。其核心思想是：通过引入辅助变量λ（称为拉格朗日乘数），将约束优化问题转化为无约束的方程组求解问题，从而规避直接在约束曲面上搜索极值点的困难。

该方法解决的标准问题形式为：在满足等式约束 $g(x, y) = 0$ 的条件下，求目标函数 $f(x, y)$ 的极值。拉格朗日乘数法的数学保证来自一个几何事实：在约束极值点处，目标函数的梯度 $\nabla f$ 与约束函数的梯度 $\nabla g$ 必须共线，即二者平行而非相交。这一条件是整个方法的理论基石，也直接催生了后来的KKT条件（Karush-Kuhn-Tucker条件）在不等式约束情形下的推广。

拉格朗日乘数法在物理、经济学和机器学习中广泛应用，例如支持向量机（SVM）的对偶问题推导、最大熵模型的参数求解，以及经济学中在预算约束下的效用最大化，均直接依赖该方法。

---

## 核心原理

### 拉格朗日函数的构造

给定目标函数 $f(\mathbf{x})$ 和 $m$ 个等式约束 $g_i(\mathbf{x}) = 0$（$i = 1, 2, \ldots, m$），构造**拉格朗日函数**：

$$\mathcal{L}(\mathbf{x}, \boldsymbol{\lambda}) = f(\mathbf{x}) + \sum_{i=1}^{m} \lambda_i g_i(\mathbf{x})$$

其中 $\lambda_i \in \mathbb{R}$ 是对应第 $i$ 个约束的拉格朗日乘数，符号可正可负，这与KKT条件中不等式约束乘数必须非负有本质区别。$\mathcal{L}$ 是原始变量 $\mathbf{x}$ 和乘数 $\boldsymbol{\lambda}$ 的联合函数，维度从 $n$ 维扩展到 $n + m$ 维。

### 一阶必要条件（驻点方程组）

极值的必要条件是拉格朗日函数对所有变量的偏导数同时为零：

$$\frac{\partial \mathcal{L}}{\partial x_j} = \frac{\partial f}{\partial x_j} + \sum_{i=1}^{m} \lambda_i \frac{\partial g_i}{\partial x_j} = 0, \quad j = 1, \ldots, n$$

$$\frac{\partial \mathcal{L}}{\partial \lambda_i} = g_i(\mathbf{x}) = 0, \quad i = 1, \ldots, m$$

前 $n$ 个方程等价于梯度共线条件 $\nabla f = -\sum_i \lambda_i \nabla g_i$，后 $m$ 个方程正是原始约束条件的重新表达。整个方程组共 $n + m$ 个方程，求解 $n + m$ 个未知量（$n$ 个原始变量加 $m$ 个乘数），方程数与未知数匹配。

### 几何解释：梯度平行条件

以二维情形为例：在约束曲线 $g(x,y)=0$ 上移动时，目标函数 $f$ 的等值线在极值点处必须与约束曲线**相切**，而非横截。相切意味着两曲线在该点有相同的切线方向，即法线方向（即各自的梯度方向）平行，用公式表达为 $\nabla f = -\lambda \nabla g$。若两梯度不平行，则沿约束方向仍能增大或减小 $f$，该点就不是极值点。这一几何直觉是理解拉格朗日乘数法本质的关键，而 $\lambda$ 的数值大小则量化了两梯度的比例关系。

### 二阶充分条件

驻点方程组的解仅保证是**候选极值点**，不能直接判断极大、极小或鞍点。需进一步检验约束黑塞矩阵（Bordered Hessian Matrix），其行列式符号决定极值类型。对于单等式约束的二维问题，加边黑塞矩阵为：

$$\bar{H} = \begin{vmatrix} 0 & g_x & g_y \\ g_x & \mathcal{L}_{xx} & \mathcal{L}_{xy} \\ g_y & \mathcal{L}_{yx} & \mathcal{L}_{yy} \end{vmatrix}$$

若 $|\bar{H}| > 0$，驻点为极大值；若 $|\bar{H}| < 0$，驻点为极小值。

---

## 实际应用

**SVM对偶问题**：支持向量机的原始问题是在线性约束 $y_i(\mathbf{w}^T \mathbf{x}_i + b) \geq 1$ 下最小化 $\frac{1}{2}\|\mathbf{w}\|^2$。对等式约束（激活约束）部分引入拉格朗日乘数，构造拉格朗日函数后对 $\mathbf{w}$ 和 $b$ 求偏导并置零，消去原始变量后得到只含乘数 $\alpha_i$ 的对偶问题，这一推导步骤完全依赖拉格朗日乘数法。

**等熵约束下的熵最大化**：信息论中，在固定均值约束 $\sum_i p_i x_i = \mu$ 和归一化约束 $\sum_i p_i = 1$ 下最大化香农熵 $H = -\sum_i p_i \ln p_i$。构造含两个乘数 $\lambda_1, \lambda_2$ 的拉格朗日函数，对 $p_i$ 求偏导得 $-\ln p_i - 1 + \lambda_1 x_i + \lambda_2 = 0$，解出 $p_i = e^{\lambda_1 x_i + \lambda_2 - 1}$，正是指数族分布的形式。

**经济学中的效用最大化**：消费者在预算约束 $p_1 x_1 + p_2 x_2 = I$ 下最大化效用 $U(x_1, x_2)$。拉格朗日乘数 $\lambda^*$ 在最优解处等于**货币的边际效用**，即预算增加1单位时效用的增量，赋予了乘数直接的经济学解释。

---

## 常见误区

**误区一：将拉格朗日乘数法用于不等式约束**。拉格朗日乘数法只适用于**等式约束** $g(\mathbf{x}) = 0$；面对不等式约束 $g(\mathbf{x}) \leq 0$ 时，直接套用会漏掉约束不紧（即 $g(\mathbf{x}) < 0$）时内点极值的情形。处理不等式约束需要KKT条件，增加互补松弛条件 $\lambda_i g_i(\mathbf{x}) = 0$ 和非负条件 $\lambda_i \geq 0$，这是拉格朗日乘数法本身不具备的机制。

**误区二：驻点就是极值点**。求解驻点方程组只给出极值的**必要条件**，不是充分条件。一个典型反例是：对 $f(x,y)=xy$ 在约束 $x+y=1$ 下，拉格朗日方程给出唯一驻点 $(0.5, 0.5)$，该点是极大值；但若约束改为 $x^2 - y^2 = 1$，驻点可能是鞍点，必须通过加边黑塞矩阵或比较边界行为加以验证。

**误区三：乘数 $\lambda$ 没有实际意义**。许多人将 $\lambda$ 仅视为消元工具。实际上，最优解处的乘数值等于**目标函数关于约束右端项的灵敏度**：若约束改为 $g(\mathbf{x}) = c$，则 $\frac{df^*}{dc}\big|_{c=0} = -\lambda^*$。这一灵敏度解释在经济学（影子价格）和工程设计（裕度分析）中有重要应用。

---

## 知识关联

**前置知识**：拉格朗日乘数法要求掌握多元函数的偏导数与梯度运算，以及约束优化问题的标准形式（目标函数与约束函数的区分）。理解梯度的几何含义——梯度方向是函数等值线的法线方向——是直觉上理解梯度平行条件的必要基础。

**直接延伸：KKT条件**。KKT条件是拉格朗日乘数法从等式约束向混合约束（等式加不等式）的推广。KKT条件在等式约束上的部分 $\nabla f + \sum_i \lambda_i \nabla g_i = 0$ 与拉格朗日乘数法的驻点条件完全一致；新增的是针对不等式约束的**互补松弛条件** $\mu_j h_j(\mathbf{x}) = 0$ 和**非负条件** $\mu_j \geq 0$。因此，拉格朗日乘数法可视为KKT条件在仅有