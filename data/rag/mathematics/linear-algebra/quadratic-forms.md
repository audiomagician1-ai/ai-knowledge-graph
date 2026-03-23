---
id: "quadratic-forms"
concept: "二次型"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 二次型

## 概述

二次型（Quadratic Form）是指 $n$ 个变量 $x_1, x_2, \ldots, x_n$ 的二次齐次多项式，其一般形式为 $f(x_1, x_2, \ldots, x_n) = \sum_{i=1}^{n}\sum_{j=1}^{n} a_{ij} x_i x_j$，其中每一项的次数恰好为 2。历史上，高斯（Gauss）在19世纪初研究整数的分类问题时系统整理了二次型理论，西尔维斯特（Sylvester）于1852年引入"惯性定理"并定义了二次型的正定、负定等概念，为现代线性代数奠定了重要基础。

二次型在几何上描述了二次曲面（如椭球面、双曲面、抛物面）的形状，在物理上描述了弹性势能和动能等二次量，在优化理论中判断驻点类型（极大值、极小值或鞍点）时不可或缺。$n=2$ 时，二次型 $f = ax_1^2 + 2bx_1x_2 + cx_2^2$ 就对应平面上的二次曲线方程，正定性决定了该曲线是否为椭圆。

## 核心原理

### 矩阵表示

任何二次型都可以用一个**实对称矩阵** $A$ 唯一表示，写成 $f(\mathbf{x}) = \mathbf{x}^T A \mathbf{x}$，其中 $\mathbf{x} = (x_1, x_2, \ldots, x_n)^T$，矩阵 $A$ 满足 $A = A^T$。将二次型化为矩阵形式时，对角元素 $a_{ii}$ 取 $x_i^2$ 的系数，而非对角元素 $a_{ij}\ (i \neq j)$ 取 $x_i x_j$ 系数的**一半**，即 $a_{ij} = a_{ji} = \frac{1}{2}(\text{系数})$。例如，$f = x_1^2 + 4x_1x_2 + 3x_2^2$ 对应的矩阵为 $A = \begin{pmatrix} 1 & 2 \\ 2 & 3 \end{pmatrix}$，其中 $a_{12} = a_{21} = 2$（即 $4x_1x_2$ 系数除以 2）。强制要求对称性保证了矩阵 $A$ 的唯一性，若不施加对称约束，则 $x_1x_2$ 的系数在 $a_{12}$ 和 $a_{21}$ 之间的分配方式无穷多。

### 标准形与合同变换

通过非退化线性变换 $\mathbf{x} = C\mathbf{y}$（$C$ 为可逆矩阵），二次型可化为**标准形**（只含平方项）：$f = \lambda_1 y_1^2 + \lambda_2 y_2^2 + \cdots + \lambda_n y_n^2$。矩阵语言表达为 $C^T A C = \Lambda$，即 $A$ 与 $\Lambda$ **合同**（congruent）。注意合同变换不同于相似变换：相似变换要求 $P^{-1}AP = \Lambda$，保持特征值不变；合同变换要求 $C^TAC = \Lambda$，保持的是**符号规律**。由于 $A$ 是实对称矩阵，存在正交矩阵 $Q$（即 $Q^T = Q^{-1}$）使得 $Q^TAQ = \text{diag}(\lambda_1, \ldots, \lambda_n)$，此时对应的标准形系数恰好就是 $A$ 的 $n$ 个实特征值。

### 惯性定理与符号差

**西尔维斯特惯性定理**指出：无论用何种非退化线性变换将二次型化为标准形，标准形中**正系数的个数 $p$**（称为正惯性指数）和**负系数的个数 $q$**（称为负惯性指数）都是唯一确定的，$p + q \leq n$，且 $p - q$ 称为二次型的**符号差**（signature）。这意味着，尽管具体的标准形系数值随变换不同而改变，但正项数和负项数始终不变。例如 $f = x_1^2 + x_2^2 - x_3^2$ 和 $f' = 2y_1^2 + 5y_2^2 - 3y_3^2$ 是同一个实对称矩阵（秩3）在不同变换下的两种标准形，二者都有 $p=2, q=1$。二次型的**秩**定义为 $r = p + q$，即矩阵 $A$ 的秩。

### 正定性判别

二次型 $f = \mathbf{x}^T A \mathbf{x}$ 称为**正定**的，当且仅当对所有非零向量 $\mathbf{x} \neq \mathbf{0}$ 均有 $f(\mathbf{x}) > 0$。正定性的等价判别条件有三个：
1. **特征值条件**：$A$ 的所有特征值 $\lambda_i > 0$（$i = 1, 2, \ldots, n$）；
2. **顺序主子式条件（Sylvester判别法）**：$A$ 的所有 $k$ 阶顺序主子式 $\Delta_k > 0$（$k = 1, 2, \ldots, n$），即 $a_{11} > 0$，$\begin{vmatrix}a_{11}&a_{12}\\a_{21}&a_{22}\end{vmatrix} > 0$，……，$\det(A) > 0$；
3. **合同标准形条件**：正惯性指数 $p = n$（标准形全为正系数）。

类似地，若所有 $\lambda_i < 0$ 则为**负定**；若 $\lambda_i$ 有正有负则为**不定**。半正定要求 $\lambda_i \geq 0$ 且至少一个为零。

## 实际应用

**多元函数极值判别**：设 $f(x, y)$ 在驻点 $(x_0, y_0)$ 处的黑塞矩阵（Hessian Matrix）为 $H = \begin{pmatrix} f_{xx} & f_{xy} \\ f_{yx} & f_{yy} \end{pmatrix}$，对应的二次型 $\mathbf{h}^T H \mathbf{h}$ 的正定性直接判断极值类型：$H$ 正定则为极小值，$H$ 负定则为极大值，$H$ 不定则为鞍点。这一方法将多元微积分的极值问题转化为二次型的正定性问题。

**主成分分析（PCA）中的方差二次型**：数据协方差矩阵 $\Sigma$ 本身是半正定对称矩阵，数据沿方向 $\mathbf{v}$ 的方差为 $\mathbf{v}^T \Sigma \mathbf{v}$，这是一个二次型。PCA 求解最大方差方向等价于在 $\|\mathbf{v}\|=1$ 约束下最大化该二次型，其解为 $\Sigma$ 的最大特征值对应的特征向量。

**椭球面方程**：三元正定二次型 $\mathbf{x}^T A \mathbf{x} = 1$ 在三维空间中定义了一个椭球面。通过正交变换化为标准形 $\frac{y_1^2}{a^2} + \frac{y_2^2}{b^2} + \frac{y_3^2}{c^2} = 1$，其中 $a = 1/\sqrt{\lambda_1}$，$b = 1/\sqrt{\lambda_2}$，$c = 1/\sqrt{\lambda_3}$，三个半轴长度完全由矩阵特征值决定。

## 常见误区

**误区一：混淆二次型矩阵与系数矩阵**。直接把 $x_1x_2$ 的系数（如4）填入 $a_{12}$ 是错误的。二次型矩阵要求对称，$a_{12} = a_{21}$，必须将混合项系数**除以2**分配给对称位置。错误写法是把 $f = 4x_1x_2$ 的矩阵写成 $\begin{pmatrix}0&4\\0&0\end{pmatrix}$，正确写法是 $\begin{pmatrix}0&2\\2&0\end{pmatrix}$。

**误区二：将合同等价与相似等价混淆**。两个实对称矩阵 $A$ 与 $B$ 合同等价（$\exists$ 可逆 $C$ 使 $C^TAC=B$）和相似等价（$\exists$ 可逆 $P$ 使 $P^{-1}AP=B$）是不同的等价关系。合同等价保持正惯性指数和负惯性指数，相似等价保持特征值。对实对称矩阵，相似等价推出合同等价，但反之不成立：$\text{diag}(1,1)$ 和 $\text{diag}(1,4)$ 合同（正惯性指数均为2）但不相似（特征值不同）。

**误区三：用行列式正负判断正定性**。有人认为 $\det(A) > 0$ 就足以判断 $A$ 正定，这是错误的。矩阵 $A = \begin{pmatrix}-1&0\\0&-2\end{pmatrix}$ 的 $\det(A) = 2 > 0$，但 $A$ 是负定矩阵，不是正定矩阵。Sylvester判别法要求
