---
id: "null-column-row-spaces"
concept: "四个基本子空间"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.406
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 四个基本子空间

## 概述

对于任意 $m \times n$ 矩阵 $A$，存在四个与之天然关联的子空间：零空间 $N(A)$（定义在 $\mathbb{R}^n$ 中）、列空间 $C(A)$（定义在 $\mathbb{R}^m$ 中）、行空间 $C(A^T)$（定义在 $\mathbb{R}^n$ 中）、左零空间 $N(A^T)$（定义在 $\mathbb{R}^m$ 中）。这四个子空间由 Gilbert Strang 在其经典教材《线性代数导论》中系统整理并命名为"四个基本子空间"，成为线性代数的核心结构框架。

这四个子空间分成两对正交补对：$N(A)$ 与 $C(A^T)$ 在 $\mathbb{R}^n$ 中互为正交补，$C(A)$ 与 $N(A^T)$ 在 $\mathbb{R}^m$ 中互为正交补。这一对称性使得研究 $Ax = b$ 的解的存在性与唯一性有了完整的几何图像。维数关系由秩-零化度定理（Rank-Nullity Theorem）精确刻画：$\text{rank}(A) + \text{nullity}(A) = n$，以及 $\text{rank}(A) + \text{nullity}(A^T) = m$。

## 核心原理

### 四个子空间的定义与维数

设矩阵 $A$ 的秩为 $r$，则四个子空间的维数如下：

| 子空间 | 符号 | 所在空间 | 维数 |
|--------|------|----------|------|
| 零空间（核） | $N(A)$ | $\mathbb{R}^n$ | $n - r$ |
| 列空间 | $C(A)$ | $\mathbb{R}^m$ | $r$ |
| 行空间 | $C(A^T)$ | $\mathbb{R}^n$ | $r$ |
| 左零空间 | $N(A^T)$ | $\mathbb{R}^m$ | $m - r$ |

**零空间** $N(A) = \{x \in \mathbb{R}^n \mid Ax = 0\}$，由 $A$ 的所有自由变量对应的特解张成，维数恰好等于自由变量个数 $n - r$。**列空间** $C(A)$ 是 $A$ 的列向量的所有线性组合构成的集合，$Ax = b$ 有解等价于 $b \in C(A)$。**行空间** $C(A^T)$ 与零空间同属 $\mathbb{R}^n$，由 $A$ 的行向量所张成，经行变换后其基可从行阶梯形的非零行直接读出。**左零空间** $N(A^T) = \{y \in \mathbb{R}^m \mid A^T y = 0\}$，即满足 $y^T A = 0$ 的所有行向量，其基可通过对增广矩阵 $[A \mid I_m]$ 做行化简后右侧对应行读出。

### 正交补关系：$\mathbb{R}^n$ 中的分裂

在 $\mathbb{R}^n$ 中，行空间 $C(A^T)$ 与零空间 $N(A)$ 正交互补，即：
$$\mathbb{R}^n = C(A^T) \oplus N(A), \quad C(A^T) \perp N(A)$$

**证明关键步骤**：若 $x \in N(A)$，则 $Ax = 0$；若 $v \in C(A^T)$，则 $v = A^T w$，故 $x \cdot v = x^T A^T w = (Ax)^T w = 0$，正交性得证。维数之和 $r + (n-r) = n$ 确保互补性。

这意味着任意向量 $x \in \mathbb{R}^n$ 可唯一分解为行空间分量与零空间分量：$x = x_r + x_n$，其中 $x_r \in C(A^T)$，$x_n \in N(A)$。对于方程 $Ax = b$，$Ax_r = b$ 而 $Ax_n = 0$，因此 $x_r$ 是 $Ax = b$ 在行空间中的唯一特解——这正是最小范数解。

### 正交补关系：$\mathbb{R}^m$ 中的分裂

在 $\mathbb{R}^m$ 中，列空间 $C(A)$ 与左零空间 $N(A^T)$ 正交互补：
$$\mathbb{R}^m = C(A) \oplus N(A^T), \quad C(A) \perp N(A^T)$$

这一分裂直接决定了 $Ax = b$ 的相容性：$b$ 必须落在 $C(A)$ 中方程才有解，否则 $b$ 在 $N(A^T)$ 方向上有非零分量，方程无解。$b$ 在 $C(A)$ 上的正交投影 $\hat{b} = Ax^*$ 给出最小二乘意义下的最优近似解。

### 从行化简中读取四个基

对矩阵 $A$ 做行化简得到行阶梯形 $R$：
- **列空间的基**：取 $A$ 中对应主元列（非化简后的 $R$，而是原矩阵 $A$ 的对应列）；
- **行空间的基**：取 $R$ 的前 $r$ 个非零行（行化简保持行空间不变）；
- **零空间的基**：从 $Rx = 0$ 的自由变量解出 $n - r$ 个特解向量；
- **左零空间的基**：对 $[A \mid I_m]$ 做行化简至 $[R \mid E]$，$E$ 中后 $m - r$ 行即为所求基。

## 实际应用

**判断线性方程组解的结构**：对一个 $3 \times 4$ 矩阵 $A$，若 $r = 2$，则 $N(A)$ 为 $\mathbb{R}^4$ 中的二维平面，$C(A)$ 为 $\mathbb{R}^3$ 中的二维平面，$C(A^T)$ 为 $\mathbb{R}^4$ 中的二维平面，$N(A^T)$ 为 $\mathbb{R}^3$ 中的一维直线。方程 $Ax = b$ 若有解，则通解形如 $x = x_p + c_1 n_1 + c_2 n_2$，其中 $n_1, n_2$ 是零空间的两个基向量。

**图像处理中的信号分解**：在压缩感知（Compressed Sensing）中，测量矩阵 $A$ 的零空间维数 $n - r$ 刻画了信息丢失的程度。若零空间非平凡（$n > r$），则原信号在零空间方向上的分量无法从测量值 $Ax$ 中恢复，这正是 $A$ 不可逆情形下信号重建需要额外稀疏约束的数学根源。

**图的关联矩阵**：对节点数为 $m$、边数为 $n$ 的连通图，其关联矩阵 $A$ 的秩 $r = m - 1$（树的边数），零空间维数为 $n - (m-1)$（回路数），左零空间维数为 $1$（由全 $1$ 向量张成），对应 Kirchhoff 电路定律中电位的任意性。

## 常见误区

**误区一：认为列空间的基可以直接从行化简后的主元列读出**。行化简改变了列向量，$R$ 的主元列与 $A$ 的主元列一般不同。正确做法是：在 $R$ 中找到主元所在的列编号（如第1、3列），然后回到原矩阵 $A$ 取对应列（$A$ 的第1、3列），这些才是 $C(A)$ 的基。

**误区二：混淆零空间与左零空间的所在空间**。$N(A) \subset \mathbb{R}^n$ 而 $N(A^T) \subset \mathbb{R}^m$，当 $m \neq n$ 时二者根本不在同一空间中，不能相互比较。特别地，对 $4 \times 3$ 矩阵，$N(A)$ 在 $\mathbb{R}^3$ 中而 $N(A^T)$ 在 $\mathbb{R}^4$ 中。

**误区三：认为秩等于 $n$ 时零空间只含零向量，但列空间仍可能不覆盖整个 $\mathbb{R}^m$**。当 $r = n < m$ 时，$N(A) = \{0\}$（方程最多一个解），但 $C(A)$ 仅是 $\mathbb{R}^m$ 中的 $n$ 维子空间，$Ax = b$ 对大多数 $b$ 无解。唯有 $r = m = n$（方阵满秩）时才能同时保证解的存在性与唯一性。

## 知识关联

四个基本子空间的维数计算依赖**行阶梯形与秩**：秩 $r$ 由主元个数确定，自由变量数 $n - r$ 直接给出零空间维数；行化简过程保持行空间不变这一事实是从 $R$ 读取行空间基的理论依据。**向量空间**的子空间公理保证了这四个集合确实构成子空间，而正交补的直和分解则依赖内积空间结构。

四个基本子空间直接为**最小二乘法**奠定几何基础