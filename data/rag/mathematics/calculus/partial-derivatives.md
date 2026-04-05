---
id: "partial-derivatives"
concept: "偏导数"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 偏导数

## 概述

偏导数是多元函数微分学的基本工具，描述一个多元函数沿某一坐标轴方向的瞬时变化率。对于二元函数 $f(x, y)$，关于变量 $x$ 的偏导数定义为：固定 $y$ 不变，只让 $x$ 发生微小变化，函数值变化量与自变量变化量之比的极限。其精确定义为：

$$\frac{\partial f}{\partial x} = \lim_{\Delta x \to 0} \frac{f(x + \Delta x, y) - f(x, y)}{\Delta x}$$

偏导数符号 $\partial$（读作"偏"）由德国数学家雅可比（Carl Gustav Jacob Jacobi）在19世纪30年代引入，以区别于单变量导数符号 $d$。这一符号的发明使得多元微分运算有了统一规范的书写方式。

偏导数的重要性体现在：几乎所有涉及多变量的物理、工程和机器学习问题都需要它。例如，热传导方程 $\frac{\partial u}{\partial t} = \alpha \nabla^2 u$ 中的每一项都是偏导数；神经网络的反向传播算法本质上就是对每个权重参数计算损失函数的偏导数，再进行梯度下降更新。

---

## 核心原理

### 偏导数的计算规则

计算偏导数时，将其他变量视为常数，然后使用单变量求导法则。例如，对 $f(x, y) = x^3 y^2 + \sin(xy) + e^y$：

- 对 $x$ 求偏导：$\frac{\partial f}{\partial x} = 3x^2 y^2 + y\cos(xy)$（将 $y$ 视为常数，$e^y$ 对 $x$ 的偏导为0）
- 对 $y$ 求偏导：$\frac{\partial f}{\partial y} = 2x^3 y + x\cos(xy) + e^y$（将 $x$ 视为常数）

注意 $e^y$ 一项：对 $x$ 求偏导时它消失，对 $y$ 求偏导时它保留。这一"消失"效应是偏导数计算中最容易出错的地方。

### 高阶偏导数与混合偏导数

对偏导数再次求偏导，可得到二阶偏导数。$f(x,y)$ 有四种二阶偏导数：

$$f_{xx} = \frac{\partial^2 f}{\partial x^2}, \quad f_{yy} = \frac{\partial^2 f}{\partial y^2}, \quad f_{xy} = \frac{\partial^2 f}{\partial x \partial y}, \quad f_{yx} = \frac{\partial^2 f}{\partial y \partial x}$$

其中 $f_{xy}$ 和 $f_{yx}$ 是混合偏导数（先对 $x$ 后对 $y$，以及先对 $y$ 后对 $x$）。**克莱罗定理（Clairaut's Theorem，1740年）** 保证：若混合偏导数在某点连续，则 $f_{xy} = f_{yx}$，即求偏导的顺序可以交换。但这一条件不可忽视——存在经典反例：

$$f(x,y) = \frac{xy(x^2 - y^2)}{x^2 + y^2}, \quad (x,y) \neq (0,0)$$

在原点处 $f_{xy}(0,0) = 1 \neq -1 = f_{yx}(0,0)$，因为混合偏导数在该点不连续。

### 全微分与偏导数的关系

全微分 $df$ 刻画函数在各方向上的综合变化：

$$df = \frac{\partial f}{\partial x}dx + \frac{\partial f}{\partial y}dy$$

**偏导数存在不等于全微分存在**，这是多元微分学区别于一元微分学的关键结论。反例：

$$f(x,y) = \begin{cases} \frac{xy}{x^2+y^2}, & (x,y)\neq(0,0) \\ 0, & (x,y)=(0,0) \end{cases}$$

在原点处，$f_x(0,0) = 0$，$f_y(0,0) = 0$，两个偏导数均存在，但 $f$ 在原点处甚至不连续，更谈不上可微。**可微的充分条件**是：偏导数在该点连续（充分非必要）。

---

## 实际应用

**热力学中的状态方程**：理想气体 $PV = nRT$ 中，可以计算任一变量对其他变量的偏导数。例如 $\left(\frac{\partial P}{\partial T}\right)_V = \frac{nR}{V}$，其中下标 $V$ 明确标注了固定变量，这是热力学中偏导数记号的标准写法。有趣的是，热力学中存在"循环关系"：$\left(\frac{\partial P}{\partial T}\right)_V \cdot \left(\frac{\partial T}{\partial V}\right)_P \cdot \left(\frac{\partial V}{\partial P}\right)_T = -1$，这个结果反直觉（不等于 $+1$），是偏导数的重要性质。

**机器学习中的反向传播**：对于损失函数 $L(w_1, w_2, \ldots, w_n)$，梯度下降的参数更新公式为 $w_i \leftarrow w_i - \eta \frac{\partial L}{\partial w_i}$，其中 $\eta$ 为学习率。对每个权重 $w_i$ 计算偏导数，就是将其他所有权重视为固定常数，这正是偏导数定义的直接应用。一个含有百万参数的神经网络，就需要计算百万个偏导数。

**隐函数求导**：对方程 $F(x, y) = 0$ 确定的隐函数 $y = f(x)$，其导数公式为 $\frac{dy}{dx} = -\frac{F_x}{F_y}$（要求 $F_y \neq 0$）。例如圆 $x^2 + y^2 - 1 = 0$，$F_x = 2x$，$F_y = 2y$，故 $\frac{dy}{dx} = -\frac{x}{y}$。

---

## 常见误区

**误区一：偏导数存在意味着函数连续**。一元微分学中，可导必连续；但多元函数中，偏导数存在与连续性没有必然关系。上文的分段函数例子就说明了这一点——偏导数存在，但函数在原点不连续。这是因为偏导数只沿坐标轴方向趋近，而连续性要求从所有方向趋近。

**误区二：混合偏导数求导顺序总可以互换**。初学者常默认 $\frac{\partial^2 f}{\partial x \partial y} = \frac{\partial^2 f}{\partial y \partial x}$ 恒成立。实际上，这需要混合偏导数连续这一额外条件（克莱罗定理的前提）。在工程问题中，绝大多数函数满足此条件；但在分析数学中，顺序交换需要严格验证。

**误区三：$\frac{\partial f}{\partial x}$ 中的 $\partial x$ 可以像 $dx$ 一样参与代数运算**。在一元微分学中，$\frac{dy}{dx}$ 在某些情形可以"分离"（如分离变量法）。但 $\frac{\partial f}{\partial x}$ 是一个整体记号，$\partial f$ 和 $\partial x$ 单独没有意义。热力学循环关系 $\left(\frac{\partial P}{\partial T}\right)_V \cdot \left(\frac{\partial T}{\partial V}\right)_P \cdot \left(\frac{\partial V}{\partial P}\right)_T = -1$（而非 $+1$）正是因为偏导数不能像分数一样直接相消。

---

## 知识关联

**前置概念衔接**：偏导数的计算直接使用单变量导数的所有法则（链式法则、乘积法则、商式法则），因为固定其他变量后，偏导数退化为单变量函数的导数。理解极限的 $\varepsilon$-$\delta$ 定义有助于理解为何偏导数存在不等价于可微。

**通向梯度**：将函数 $f(x_1, x_2, \ldots, x_n)$ 对所有变量的偏导数组成向量，就得到梯度 $\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \ldots, \frac{\partial f}{\partial x_n}\right)$。梯度是偏导数的向量化封装，方向导数则可以用梯度通过点积 $D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$ 来统一表达。

**通向优化**：无约束优化的必要条件是所有偏导数同时为零，即 $\frac{\partial f}{\partial x_i} = 0$（$i = 1, \ldots, n$），形成方程组。进一步判断极值类型需要海森矩阵（Hessian Matrix），其元素恰好是所有二阶偏导数 $H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$，偏导数的知识直接支撑了多元函数极值判别法。