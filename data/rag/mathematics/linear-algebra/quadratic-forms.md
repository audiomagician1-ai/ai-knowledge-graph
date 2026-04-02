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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 二次型

## 概述

二次型（Quadratic Form）是关于 $n$ 个变量 $x_1, x_2, \ldots, x_n$ 的二次齐次多项式，其一般形式为 $f(x_1, x_2, \ldots, x_n) = \sum_{i=1}^{n}\sum_{j=1}^{n} a_{ij} x_i x_j$，其中每一项的次数恰好等于 2。例如 $f(x_1, x_2) = 3x_1^2 - 2x_1 x_2 + 5x_2^2$ 是一个典型的二元二次型。注意二次型中不含常数项，也不含一次项，这是与一般二次多项式的根本区别。

二次型的研究可追溯至 18 世纪欧拉对二次曲线和二次曲面的分类工作，高斯在 1801 年《算术研究》中系统研究了整数系数的二元二次型，用于解析数论中的整数表示问题。19 世纪西尔维斯特（Sylvester）引入了惯性定理，奠定了实二次型理论的现代基础。二次型在几何（二次曲线/曲面分类）、物理（动能、势能的表达）、统计（多元正态分布的密度函数）和优化（二次规划）中均有直接应用。

## 核心原理

### 矩阵表示

任意二次型都可以唯一地写成矩阵形式 $f(\mathbf{x}) = \mathbf{x}^T A \mathbf{x}$，其中 $\mathbf{x} = (x_1, x_2, \ldots, x_n)^T$，$A$ 是一个 $n \times n$ **实对称矩阵**，即 $A = A^T$。关键约定：令 $a_{ij} = a_{ji} = \dfrac{1}{2}(a_{ij} + a_{ji})$，将交叉项 $x_i x_j$（$i \neq j$）的系数平均分配给 $A$ 的 $(i,j)$ 和 $(j,i)$ 位置，从而保证矩阵的对称性。例如对于 $f = 2x_1^2 + 3x_1 x_2 + x_2^2$，其对称矩阵为：
$$A = \begin{pmatrix} 2 & 3/2 \\ 3/2 & 1 \end{pmatrix}$$
这种对称化处理保证了矩阵 $A$ 与二次型之间的**一一对应关系**——每个实二次型对应唯一的实对称矩阵，反之亦然。

### 标准形与合同变换

通过非退化线性变换 $\mathbf{x} = C\mathbf{y}$（$C$ 可逆），二次型可化为**标准形**（只含平方项）：$f = d_1 y_1^2 + d_2 y_2^2 + \cdots + d_n y_n^2$。此变换将矩阵 $A$ 变为 $C^T A C = \Lambda$（对角矩阵），称两个矩阵**合同**（Congruent）。合同关系与相似关系不同：相似要求 $P^{-1}AP = B$，而合同要求 $C^TAC = B$，两者的 $C$ 的出现方式不同，合同变换保持的是二次型的**惯性指数**，而非特征值。

实对称矩阵必可通过正交变换 $A = Q\Lambda Q^T$（谱定理）对角化，利用正交矩阵 $Q$ 作变换 $\mathbf{x} = Q\mathbf{y}$，二次型化为 $f = \lambda_1 y_1^2 + \lambda_2 y_2^2 + \cdots + \lambda_n y_n^2$，其中 $\lambda_i$ 为 $A$ 的特征值。这是将特征值理论直接应用于二次型分析的标准路径。

### 惯性定理与正定性

**西尔维斯特惯性定理**（1852年）指出：无论用何种非退化线性变换将实二次型化为标准形，其中正系数的个数 $p$（正惯性指数）和负系数的个数 $q$（负惯性指数）是唯一确定的，与所选变换无关。差值 $p - q$ 称为二次型的**符号差**（Signature）。

二次型的**正定性**通过以下等价条件刻画（对实对称矩阵 $A$）：
- $f(\mathbf{x}) > 0$ 对所有 $\mathbf{x} \neq \mathbf{0}$ 成立（正定的定义）；
- $A$ 的所有特征值 $\lambda_i > 0$；
- $A$ 的所有**顺序主子式**均大于零，即 $\Delta_1 = a_{11} > 0$，$\Delta_2 = \det\begin{pmatrix}a_{11}&a_{12}\\a_{21}&a_{22}\end{pmatrix} > 0$，……，$\Delta_n = \det(A) > 0$（**赫尔维茨判据**）；
- $A$ 与单位矩阵 $I$ 合同，即存在可逆矩阵 $C$ 使得 $C^TAC = I$；
- 正惯性指数 $p = n$（即 $q = 0$）。

类似地，**半正定**要求所有 $\lambda_i \geq 0$，**负定**要求所有 $\lambda_i < 0$，**不定**则特征值中既有正值又有负值。

## 实际应用

**椭圆与双曲线的识别**：二元二次型 $f = ax^2 + bxy + cy^2 = 1$ 表示的曲线类型由判别式 $\Delta = b^2 - 4ac$ 决定。若 $\Delta < 0$ 且 $a > 0$，曲线为椭圆（对应矩阵正定）；若 $\Delta > 0$，曲线为双曲线（矩阵不定）。这直接源于二次型正定性的判断。

**多元统计中的马氏距离**：在多元正态分布中，样本点 $\mathbf{x}$ 到均值 $\boldsymbol{\mu}$ 的马氏距离定义为 $d^2 = (\mathbf{x}-\boldsymbol{\mu})^T \Sigma^{-1} (\mathbf{x}-\boldsymbol{\mu})$，其中 $\Sigma^{-1}$ 为协方差矩阵的逆。由于协方差矩阵 $\Sigma$ 正定，$\Sigma^{-1}$ 也正定，故此表达式恰好是一个正定二次型，其值恒非负，几何上对应超椭球面。

**二次规划**：最优化问题 $\min \frac{1}{2}\mathbf{x}^T Q \mathbf{x} + \mathbf{c}^T \mathbf{x}$ 的目标函数含有二次型 $\mathbf{x}^T Q \mathbf{x}$。当 $Q$ 正定时，目标函数是严格凸函数，保证问题有唯一最优解，这是支持向量机（SVM）求解的数学基础之一。

## 常见误区

**误区一：混淆矩阵合同与矩阵相似**。二次型在非退化线性变换下对应的是合同变换 $C^TAC$，不是相似变换 $C^{-1}AC$。合同变换保持正定性（若 $A$ 正定，则 $C^TAC$ 也正定），保持惯性指数，但一般**不保持特征值**。例如 $A = I$ 与 $B = 4I$ 合同（取 $C = 2I$），但特征值不同（分别为 1 和 4）。

**误区二：将正定的顺序主子式条件误用为所有主子式**。赫尔维茨判据要求的是**顺序**主子式（即左上角 $k \times k$ 子矩阵的行列式，$k = 1, 2, \ldots, n$）全为正，而非矩阵 $A$ 的所有 $2^n - 1$ 个主子式。例如矩阵 $\begin{pmatrix}2 & 3\\ 3 & 5\end{pmatrix}$ 的顺序主子式为 2 和 $10-9=1$，均正，故正定；但它的某个非顺序主子式（如 $(2,2)$ 位置的 $1\times1$ 子式）并不影响判定。

**误区三：以为只有对角矩阵才能表示二次型**。二次型 $f = x_1^2 + 2x_1x_2 + x_2^2 = (x_1+x_2)^2 \geq 0$ 对应的矩阵为 $\begin{pmatrix}1 & 1\\1 & 1\end{pmatrix}$，是半正定（非负定）的，行列式为零，存在非零向量使 $f = 0$（如 $\mathbf{x} = (1, -1)^T$）。这说明非负性不等于正定性，正定要求对所有非零向量严格大于零。

## 知识关联

学习二次型需要扎实的**矩阵乘法**基础：$\mathbf{x}^T A \mathbf{x}$ 的展开涉及 $1 \times n$、$n \times n$、$n \times 1$ 三个矩阵的连续乘法，理解这一运算的维度变化和展开规则是写出二次型矩阵形式的前提。

**特征值与特征向量**为二次型的标准化提供了核心工具：实对称矩阵的