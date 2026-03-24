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
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 正定矩阵

## 概述

正定矩阵（Positive Definite Matrix）是实对称矩阵的一种特殊类型，其精确定义为：若实对称矩阵 $A \in \mathbb{R}^{n \times n}$ 满足对所有非零向量 $\mathbf{x} \in \mathbb{R}^n$，均有二次型 $\mathbf{x}^T A \mathbf{x} > 0$，则称 $A$ 为正定矩阵，记作 $A \succ 0$。这一严格大于零的不等式是正定性的核心，将正定矩阵与半正定矩阵（$\mathbf{x}^T A \mathbf{x} \geq 0$）明确区分开来。

正定矩阵的概念在19世纪末由西尔维斯特（James Joseph Sylvester）系统化，他在1852年提出了著名的行列式判别法则——西尔维斯特判据。这一工具使得正定性的验证从抽象的代数条件转化为可计算的顺序主子式检验。正定矩阵在物理中对应稳定的势能面，在统计学中对应合法的协方差矩阵，在数值计算中是线性方程组高效求解的前提条件。

正定矩阵的重要性在于它是多变量微积分中极小值点的充分条件：若函数 $f(\mathbf{x})$ 在驻点处的Hessian矩阵正定，则该驻点为严格局部极小值点。这一结论是无约束优化理论的基石。

## 核心原理

### 等价判定条件

正定矩阵有五个经典的等价判定条件，可根据计算便利性灵活选用：

1. **二次型定义**：对所有非零向量 $\mathbf{x}$，$\mathbf{x}^T A \mathbf{x} > 0$。
2. **特征值条件**：$A$ 的所有特征值 $\lambda_i > 0$（$i = 1, 2, \ldots, n$）。
3. **西尔维斯特判据**：$A$ 的所有顺序主子式均为正，即 $\Delta_k = \det(A_{k \times k}) > 0$，$k = 1, 2, \ldots, n$。
4. **Cholesky分解存在性**：存在唯一的下三角矩阵 $L$（对角元素严格为正），使得 $A = LL^T$。
5. **合同变换条件**：$A$ 合同于单位矩阵 $I$，即存在可逆矩阵 $P$ 使得 $P^T A P = I$。

西尔维斯特判据在实际计算中最为直观：对于 $2 \times 2$ 矩阵 $A = \begin{pmatrix} a & b \\ b & c \end{pmatrix}$，正定条件恰好是 $a > 0$ 且 $ac - b^2 > 0$。

### Cholesky分解

Cholesky分解是正定矩阵专属的矩阵分解方法，其形式为 $A = LL^T$，其中 $L$ 为下三角矩阵且对角元素均为正实数。该分解的计算公式为：

$$L_{jj} = \sqrt{A_{jj} - \sum_{k=1}^{j-1} L_{jk}^2}$$

$$L_{ij} = \frac{1}{L_{jj}}\left(A_{ij} - \sum_{k=1}^{j-1} L_{ik} L_{jk}\right), \quad i > j$$

与LU分解相比，Cholesky分解利用了正定矩阵的对称性，计算量约为LU分解的一半，浮点运算次数约为 $\frac{n^3}{3}$。更重要的是，Cholesky分解在数值上天然稳定，无需选主元策略，因为正定性保证分解过程中不会出现零主元或数值放大问题。利用Cholesky分解求解线性方程组 $A\mathbf{x} = \mathbf{b}$ 时，将问题分解为两步回代：先解 $L\mathbf{y} = \mathbf{b}$，再解 $L^T\mathbf{x} = \mathbf{y}$。

### 正定矩阵的代数运算封闭性

若 $A \succ 0$ 且 $B \succ 0$，则：
- $A + B \succ 0$（正定矩阵对加法封闭）
- $cA \succ 0$ 对任意 $c > 0$ 成立
- $A^{-1} \succ 0$（正定矩阵的逆仍为正定矩阵）
- $A^k \succ 0$ 对任意正整数 $k$ 成立

但注意 $AB$ 不一定正定，即使 $A \succ 0$ 且 $B \succ 0$，因为 $AB$ 未必对称。只有当 $AB = BA$（即两者可交换）时，$AB$ 才保持正定性。

## 实际应用

**多元正态分布的协方差矩阵**：$n$ 维多元正态分布 $\mathcal{N}(\boldsymbol{\mu}, \Sigma)$ 中，协方差矩阵 $\Sigma$ 必须严格正定（非退化情况），其概率密度函数中包含 $\Sigma^{-1}$ 和 $\det(\Sigma)$，两者均依赖正定性才能良定义。Cholesky分解 $\Sigma = LL^T$ 被用于从多元正态分布中高效采样：先生成标准正态向量 $\mathbf{z}$，再令 $\mathbf{x} = L\mathbf{z} + \boldsymbol{\mu}$。

**有限元方法中的刚度矩阵**：结构力学的有限元分析产生的整体刚度矩阵 $K$ 为正定矩阵（在施加充分边界条件后），其中 $\mathbf{u}^T K \mathbf{u}$ 表示结构的弹性应变能，物理上必须为正值。这使得Cholesky分解成为有限元求解器（如NASTRAN、ABAQUS）中线性方程组求解的标准算法。

**机器学习中的核矩阵**：支持向量机中的核矩阵 $K_{ij} = k(\mathbf{x}_i, \mathbf{x}_j)$ 必须是半正定矩阵（Mercer条件），而当所有训练样本两两不同时通常严格正定。高斯核 $k(\mathbf{x}, \mathbf{y}) = \exp(-\|\mathbf{x}-\mathbf{y}\|^2 / 2\sigma^2)$ 产生的Gram矩阵即为正定矩阵，其Cholesky分解用于加速高斯过程回归的后验推断，时间复杂度为 $O(n^3)$。

## 常见误区

**误区一：将"对称矩阵"与"正定矩阵"混淆**。正定矩阵必然是对称矩阵，但对称矩阵不一定正定。例如矩阵 $\begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$ 是对称矩阵，但其特征值为 $\{1, -1\}$，含有负特征值，因此不是正定矩阵而是不定矩阵。检验正定性时必须同时验证对称性和所有特征值（或顺序主子式）为正。

**误区二：用所有主子式代替顺序主子式**。西尔维斯特判据要求的是顺序（左上角）主子式 $\Delta_1, \Delta_2, \ldots, \Delta_n$ 均为正，而非矩阵的所有主子式（包括非顺序的）均为正。反例：矩阵 $A = \begin{pmatrix} 1 & 2 \\ 2 & 3 \end{pmatrix}$ 的顺序主子式 $\Delta_1 = 1 > 0$，$\Delta_2 = 3 - 4 = -1 < 0$，故 $A$ 不正定，但其右下角 $1 \times 1$ 子式为 $3 > 0$，若误用所有子式会导致错误判断。

**误区三：认为正定矩阵的Cholesky分解不唯一**。对于实正定矩阵，若要求 $L$ 的对角元素严格为正，则 $A = LL^T$ 的Cholesky分解是唯一的。唯一性证明依赖于正定性：假设存在两个这样的分解 $A = L_1 L_1^T = L_2 L_2^T$，则 $L_2^{-1} L_1 = L_2^T (L_1^T)^{-1}$，左边为下三角，右边为上三角，故两边均为对角矩阵，再由对角元素为正可得 $L_1 = L_2$。

## 知识关联

正定矩阵与**二次型**的关系最为直接：$n$ 元实二次型 $f = \mathbf{x}^T A \mathbf{x}$（$A$ 为实对称矩阵）是正定二次型，当且仅当 $A$ 为正定矩阵。二次型的标准化（通过正交变换对角化）将正定性转化为所有标准型系数为正，即对应正定矩阵的特征值全为正。

正定矩阵与**特征值理论**的联系体现在谱分解 $A = Q \Lambda Q^T$（$Q$ 为正交矩阵，$\Lambda = \text{diag}(\lambda_1, \ldots, \lambda_n)$），正定性等价于
