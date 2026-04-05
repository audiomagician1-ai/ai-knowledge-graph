---
id: "kkt-conditions"
concept: "KKT条件"
domain: "mathematics"
subdomain: "optimization"
subdomain_name: "最优化"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
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

# KKT条件

## 概述

KKT条件（Karush-Kuhn-Tucker Conditions）是求解含不等式约束优化问题的一阶必要条件，由William Karush于1939年在硕士论文中首先提出，Tucker和Kuhn于1951年独立重新发现并正式发表，这也是该条件长期被称为"KT条件"而忽略Karush贡献的原因。KKT条件将拉格朗日乘数法从等式约束推广到不等式约束，使得大量工程和机器学习问题得以形式化求解。

标准KKT问题的形式为：最小化 $f(x)$，满足不等式约束 $g_i(x) \leq 0$（$i=1,\ldots,m$）和等式约束 $h_j(x) = 0$（$j=1,\ldots,p$）。与纯等式约束的拉格朗日乘数法不同，不等式约束引入了"互补松弛"这一本质性的新机制，使得最优解的刻画比等式约束复杂得多。

KKT条件在支持向量机（SVM）的对偶推导、内点法、序列二次规划（SQP）等现代优化算法中直接使用。理解KKT条件是阅读大量机器学习理论文献的必要前提——例如SVM的稀疏性（只有支持向量对应的 $\alpha_i > 0$）直接来源于KKT的互补松弛条件。

## 核心原理

### 广义拉格朗日函数与KKT乘子符号约定

对含不等式约束的问题，构造广义拉格朗日函数：

$$L(x, \mu, \lambda) = f(x) + \sum_{i=1}^{m} \mu_i g_i(x) + \sum_{j=1}^{p} \lambda_j h_j(x)$$

其中 $\mu_i$ 是对应不等式约束 $g_i(x) \leq 0$ 的KKT乘子，$\lambda_j$ 是等式约束的拉格朗日乘子。关键区别在于：$\mu_i \geq 0$ 是强制要求，而等式约束乘子 $\lambda_j$ 无符号限制。这一符号约定不是任意的——若约束写成 $g_i(x) \geq 0$ 的形式，则对应乘子需满足 $\mu_i \leq 0$，符号随约束方向改变。

### 四个KKT条件的具体含义

KKT最优性条件由以下四组条件构成：

**（1）稳定性条件（Stationarity）：**

$$\nabla_x L = \nabla f(x^*) + \sum_{i=1}^{m} \mu_i \nabla g_i(x^*) + \sum_{j=1}^{p} \lambda_j \nabla h_j(x^*) = 0$$

这要求在最优点处，目标函数的梯度可以被约束函数梯度的线性组合所表示，系数即为KKT乘子。

**（2）原始可行性（Primal Feasibility）：**
$$g_i(x^*) \leq 0, \quad h_j(x^*) = 0$$

最优点必须满足所有原问题约束。

**（3）对偶可行性（Dual Feasibility）：**
$$\mu_i \geq 0$$

不等式约束的KKT乘子必须非负，这保证了对偶问题的有意义性。

**（4）互补松弛条件（Complementary Slackness）：**
$$\mu_i g_i(x^*) = 0, \quad \forall i$$

这是KKT条件中最具特色的部分：对每个不等式约束，要么 $\mu_i = 0$（约束非紧，为非激活约束），要么 $g_i(x^*) = 0$（约束取等，为激活约束），两者不能同时非零。

### 正则性条件（约束规范）

KKT条件是最优解的**必要条件**，但前提是最优点处需满足某种**正则性条件（Constraint Qualification）**。最常用的是线性无关约束规范（LICQ）：在最优点 $x^*$，所有激活约束的梯度线性无关。若不满足正则性条件，KKT条件可能对真实最优点失效。例如考虑 $g(x) = (x-1)^2 \leq 0$，其最优点 $x^*=1$ 处梯度为零，不满足LICQ，KKT乘子无法正常定义。在凸优化中，Slater条件（存在严格可行点 $g_i(x) < 0$）是一种更容易验证的充分正则性条件。

## 实际应用

**支持向量机的稀疏解：** SVM的原问题对偶化后，KKT互补松弛条件给出 $\alpha_i (y_i(w^T x_i + b) - 1) = 0$。这直接说明：当样本点不在间隔边界上时（$y_i(w^T x_i + b) > 1$），必有 $\alpha_i = 0$，该样本对决策边界无贡献。只有支持向量（$\alpha_i > 0$）才影响模型，这正是SVM稀疏性的理论根源。

**投资组合优化：** Markowitz均值-方差模型中，在预期收益不低于目标值 $\mu_0$ 的约束下最小化投资组合方差。KKT条件给出各资产权重与拉格朗日乘子的解析关系，乘子 $\lambda$ 的经济含义是收益率提高一单位所能换取的最小方差减少量（即风险价格）。

**二次规划的精确求解：** 对于含线性不等式约束的二次规划问题 $\min \frac{1}{2}x^TQx + c^Tx$，KKT条件退化为一组线性方程组（因为目标函数和约束函数的梯度均为线性），可通过枚举激活约束集合（Active Set Method）来精确求解。

## 常见误区

**误区一：KKT条件是充分条件。** KKT条件仅是满足正则性假设的局部最优解的必要条件，而非充分条件。满足KKT条件的点称为"KKT点"，不一定是最优解。**例外**：当目标函数为凸函数、不等式约束为凸函数、等式约束为仿射函数时，KKT条件才同时成为充要条件——这是凸优化的特殊结论，不能推广到一般非凸问题。

**误区二：KKT乘子的符号无所谓。** 部分教材将不等式约束写成 $g_i(x) \geq 0$ 形式，此时乘子变为非正（$\mu_i \leq 0$）。混淆约束方向与乘子符号会导致对偶可行性判断错误，进而得出错误的互补松弛分析。在读文献时必须首先确认约束的标准化方向。

**误区三：所有约束都需要写入KKT条件。** 非激活约束（$g_i(x^*) < 0$）处的KKT乘子 $\mu_i$ 必须为零（由互补松弛条件），因此在求解时可以先猜测激活约束集合（令部分 $g_i(x^*)=0$，其余 $\mu_i=0$），再验证解的可行性和乘子非负性，而不必同时处理所有约束，这正是Active Set算法的思路。

## 知识关联

KKT条件是拉格朗日乘数法的直接推广：等式约束 $h_j(x)=0$ 情形下，KKT条件退化为标准拉格朗日条件 $\nabla f = -\sum \lambda_j \nabla h_j$，此时无互补松弛条件，无乘子符号约束。学习KKT条件前需要熟练掌握拉格朗日乘数法对等式约束问题的几何意义，即最优点处等值面与约束曲面的法向量平行。

KKT条件是进入**凸优化**理论的核心工具。在凸优化中，强对偶性（Strong Duality）成立当且仅当Slater条件满足，此时原问题最优解与对偶问题最优解之间的差（对偶间隙）为零，而这一零对偶间隙与KKT条件等价。凸优化的内点法（如CVXPY底层使用的障碍函数法）通过对数障碍函数将不等式约束内化，其迭代过程本质上是逐步逼近KKT点的过程。此外，KKT条件也是二阶必要条件（涉及约束曲率修正的Hessian条件）分析的出发点，后者进一步区分鞍点与局部极小值。