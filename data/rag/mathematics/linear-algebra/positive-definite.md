---
id: "positive-definite"
concept: "正定矩阵"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 正定矩阵

## 概述

正定矩阵（Positive Definite Matrix）是实对称矩阵的一个特殊子类，其核心定义为：对任意非零实向量 $\mathbf{x} \in \mathbb{R}^n$，均满足二次型 $\mathbf{x}^T A \mathbf{x} > 0$。这个严格不等式将正定矩阵与半正定矩阵（允许等号）、不定矩阵（二次型可正可负）明确区分开来。历史上，正定矩阵的系统研究可追溯至19世纪末Sylvester对二次型符号判定的工作，Sylvester判准（Sylvester's Criterion）至今仍是最常用的代数判定工具。

正定矩阵在数值线性代数中的重要性体现在它对线性方程组求解的稳定性保证上。当系数矩阵 $A$ 正定时，方程组 $A\mathbf{x} = \mathbf{b}$ 具有唯一解，且可以使用比LU分解更高效约一倍的Cholesky分解算法，条件数估计也更为可靠。在优化理论中，Hessian矩阵正定性是无约束极小值点的充分条件，这使得正定性判定成为二阶最优性条件分析的核心工具。

## 核心原理

### 等价判定条件

判断矩阵 $A$ 是否正定有多种等价途径，各有计算优势。**Sylvester判准**要求矩阵所有顺序主子式（Leading Principal Minors）均为正数：$\Delta_1 = a_{11} > 0$，$\Delta_2 = a_{11}a_{22} - a_{12}^2 > 0$，直至 $\Delta_n = \det(A) > 0$。对于 $3 \times 3$ 矩阵需验证 3 个顺序主子式，而非全部 $2^3 - 1 = 7$ 个主子式。**特征值判准**则要求 $A$ 的所有 $n$ 个特征值均为严格正实数——由于 $A$ 是实对称矩阵，特征值必为实数，此条件合理且可验证。两种判准的等价性本质来自谱定理：实对称矩阵可正交对角化，其二次型的符号完全由特征值符号决定。

### Cholesky分解

Cholesky分解是正定矩阵独有的矩阵分解形式：任意正定矩阵 $A$ 可唯一分解为 $A = L L^T$，其中 $L$ 是对角元素均为正实数的下三角矩阵。分解的递推公式为：

$$L_{jj} = \sqrt{a_{jj} - \sum_{k=1}^{j-1} L_{jk}^2}, \quad L_{ij} = \frac{1}{L_{jj}}\left(a_{ij} - \sum_{k=1}^{j-1} L_{ik}L_{jk}\right), \quad i > j$$

相比LU分解需要约 $\frac{2n^3}{3}$ 次浮点运算，Cholesky分解仅需约 $\frac{n^3}{3}$ 次运算，效率提高近一倍。由于无需选主元操作，Cholesky分解还具有天然的数值稳定性。若在执行分解过程中某步出现 $L_{jj}$ 的被开方数为负，则可判定矩阵非正定，这一性质被用作高效的正定性检验算法。

### 二次型的几何解释

$n$ 阶正定矩阵 $A$ 定义的二次型 $f(\mathbf{x}) = \mathbf{x}^T A \mathbf{x}$ 在 $\mathbb{R}^n$ 中描述一个以原点为唯一最低点的碗形超曲面。等值面 $\{\mathbf{x} : \mathbf{x}^T A \mathbf{x} = c\}$（$c > 0$）是以原点为中心的 $n$ 维椭球体，椭球的半轴长与矩阵 $A$ 的特征值 $\lambda_i$ 的平方根成反比：第 $i$ 条半轴长为 $\sqrt{c/\lambda_i}$，方向为对应特征向量。当 $A$ 为单位矩阵 $I$ 时，椭球退化为正球体。正定条件的几何含义即为：没有任何非零方向使二次型取零值或负值。

### 矩阵不等式与半序

对两个对称矩阵 $A$ 和 $B$，定义 $A \succ B$（$A$ 正定地大于 $B$）当且仅当差矩阵 $A - B$ 正定。这种关系构成对称矩阵集合上的偏序（Loewner偏序），满足传递性和加法兼容性，但不是全序——存在不可比较的对称矩阵对。Loewner偏序是半定规划（SDP）问题中约束条件的数学基础，约束 $A \succeq 0$（半正定）定义了半定规划的可行域——一个凸锥。

## 实际应用

**多元正态分布的协方差矩阵**：$n$ 维多元正态分布 $\mathcal{N}(\boldsymbol{\mu}, \Sigma)$ 要求协方差矩阵 $\Sigma$ 正定（退化分布要求半正定）。$\Sigma$ 正定保证了概率密度函数 $f(\mathbf{x}) = \frac{1}{(2\pi)^{n/2}|\Sigma|^{1/2}} \exp\left(-\frac{1}{2}(\mathbf{x}-\boldsymbol{\mu})^T \Sigma^{-1} (\mathbf{x}-\boldsymbol{\mu})\right)$ 中行列式 $|\Sigma| > 0$ 和逆矩阵 $\Sigma^{-1}$ 的存在性。数值计算协方差矩阵时常用Cholesky分解替代直接求逆，将计算误差降低约1-2个数量级。

**有限元分析中的刚度矩阵**：结构力学的有限元方法中，全局刚度矩阵 $K$ 在施加固定边界条件后成为正定矩阵，物理含义是任何非零位移场都储存正的应变能 $\frac{1}{2}\mathbf{u}^T K \mathbf{u} > 0$。工程软件中广泛使用稀疏Cholesky分解（如CHOLMOD库）求解大规模方程组 $K\mathbf{u} = \mathbf{f}$，对百万自由度问题仍能保持高效稳定。

**机器学习中的核矩阵**：支持向量机和高斯过程中使用的核函数 $k(\mathbf{x}_i, \mathbf{x}_j)$ 生成的 Gram 矩阵 $K_{ij} = k(\mathbf{x}_i, \mathbf{x}_j)$ 须为半正定矩阵（Mercer定理要求）。RBF核 $k(\mathbf{x}, \mathbf{y}) = \exp(-\|\mathbf{x}-\mathbf{y}\|^2/2\sigma^2)$ 生成的 Gram 矩阵在数据点无重复时严格正定，保证了对偶问题的凸性和唯一解。

## 常见误区

**误区一：混淆正定矩阵与对角元素全正矩阵**。对角元素全为正数不足以保证正定性。反例：矩阵 $A = \begin{pmatrix} 1 & 2 \\ 2 & 1 \end{pmatrix}$ 对角元素均为1，但 $\det(A) = 1 - 4 = -3 < 0$，不满足Sylvester判准，实际为不定矩阵（特征值为 $3$ 和 $-1$）。正定性要求的是所有顺序主子式均正，这是远比对角正更强的条件。

**误区二：认为正定矩阵的逆仍需重新验证正定性**。正定矩阵 $A$ 的逆 $A^{-1}$ 自动正定，无需另行验证。证明：设 $\lambda_i$ 为 $A$ 的特征值，则 $A^{-1}$ 的特征值为 $1/\lambda_i$；由 $\lambda_i > 0$ 立即得 $1/\lambda_i > 0$。类似地，两个同阶正定矩阵之和仍正定（对任意非零 $\mathbf{x}$，$\mathbf{x}^T(A+B)\mathbf{x} = \mathbf{x}^TA\mathbf{x} + \mathbf{x}^TB\mathbf{x} > 0$），但两个正定矩阵之积一般不再对称，不适用正定性的标准定义。

**误区三：将Cholesky分解与LDL^T分解混同**。LDL^T 分解 $A = L D L^T$（$D$ 为对角矩阵，$L$ 为单位下三角矩阵）适用于所有非奇异对称矩阵，通过检查 $D$ 的对角元素符号来判断正定性，无需开平方运算，数值上更稳定。而Cholesky分解 $A = LL^T$ 仅在矩阵正定时存在，且 $L$ 的对角元素为正实数。选择哪种分解取决于应用场景：Cholesky计算效率略高，LDL^T 适用范围更广。

## 知识关联

**前置知识的作用**：正定矩阵与二次型的联系最为直接——正定矩阵的定义本身