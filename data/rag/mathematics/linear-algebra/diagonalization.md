---
id: "diagonalization"
concept: "对角化"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 对角化

## 概述

对角化是指将一个方阵 $A$ 通过相似变换转化为对角矩阵 $\Lambda$ 的过程，即寻找可逆矩阵 $P$，使得 $P^{-1}AP = \Lambda$，其中 $\Lambda$ 的对角元素恰好是 $A$ 的全部特征值。这一过程将矩阵从一般形式压缩为最简洁的对角结构，极大地简化了矩阵幂运算、微分方程求解等计算。

对角化思想的雏形可追溯到18世纪欧拉（Euler）对二次型化简的研究，而严格的线性代数框架由柯西（Cauchy）在1829年处理实对称矩阵时奠定。一个 $n \times n$ 矩阵可对角化的充要条件是它恰好拥有 $n$ 个线性无关的特征向量，这一判断标准将对角化问题彻底归结为特征空间的维数分析。

对角化的价值在于指数级地降低重复计算的代价：若 $A = P\Lambda P^{-1}$，则 $A^k = P\Lambda^k P^{-1}$，而 $\Lambda^k$ 只需对每个对角元素取 $k$ 次幂，避免了 $k-1$ 次完整的矩阵乘法。这一性质直接支撑了斐波那契数列的闭合公式推导、马尔可夫链长期状态预测等经典应用。

## 核心原理

### 可对角化的充要条件

$n$ 阶矩阵 $A$ 可对角化，当且仅当 $A$ 的每个特征值 $\lambda_i$ 的**几何重数**等于其**代数重数**。

- **代数重数**（algebraic multiplicity）：特征值 $\lambda_i$ 作为特征多项式 $\det(\lambda I - A) = 0$ 之根的重数，记为 $m_i$。
- **几何重数**（geometric multiplicity）：对应特征空间 $\ker(\lambda_i I - A)$ 的维数，记为 $d_i$。

对任意特征值，始终有 $1 \leq d_i \leq m_i$。当某个特征值满足 $d_i < m_i$ 时，矩阵**不可对角化**。例如，矩阵 $\begin{pmatrix}2 & 1 \\ 0 & 2\end{pmatrix}$ 的特征值 $\lambda = 2$ 代数重数为 2，但几何重数为 1（特征空间仅由 $(1,0)^T$ 张成），故此矩阵不可对角化。

若 $A$ 有 $n$ 个**互不相同**的特征值，则 $A$ 必可对角化（充分条件，非必要）。

### 对角化的构造步骤

设 $A$ 的特征值为 $\lambda_1, \lambda_2, \ldots, \lambda_n$（含重复），对应线性无关特征向量为 $\xi_1, \xi_2, \ldots, \xi_n$，则：

$$P = [\xi_1 \mid \xi_2 \mid \cdots \mid \xi_n], \quad \Lambda = \text{diag}(\lambda_1, \lambda_2, \ldots, \lambda_n)$$

满足 $AP = P\Lambda$，即 $P^{-1}AP = \Lambda$。注意 $P$ 的列顺序必须与 $\Lambda$ 对角元素顺序**严格对应**——$P$ 的第 $j$ 列是 $\lambda_j$ 对应的特征向量，否则等式不成立。

### 实对称矩阵的正交对角化

实对称矩阵（$A = A^T$）不仅一定可对角化，还能通过**正交矩阵** $Q$（满足 $Q^T = Q^{-1}$）实现对角化，即 $Q^TAQ = \Lambda$。这是因为实对称矩阵不同特征值对应的特征向量必然相互正交（可由 $\lambda_i \xi_i^T \xi_j = \xi_i^T A \xi_j = \lambda_j \xi_i^T \xi_j$ 推出，当 $\lambda_i \neq \lambda_j$ 时 $\xi_i^T \xi_j = 0$）。对重特征值对应的特征空间，需额外用 Gram-Schmidt 正交化处理，最终得到标准正交特征向量集合构成 $Q$。

### 相似变换的几何含义

相似变换 $P^{-1}AP$ 的本质是**换基**：$P$ 的列向量构成新坐标基，在该基下线性变换 $A$ 的矩阵表示变为 $\Lambda$。对角化意味着存在一组特征向量基，使得 $A$ 在该基下表现为纯粹的伸缩变换，每个基向量 $\xi_i$ 被 $A$ 作用后只沿自身方向缩放 $\lambda_i$ 倍，无任何旋转或剪切分量。

## 实际应用

**矩阵幂与斐波那契数列**：令 $A = \begin{pmatrix}1 & 1 \\ 1 & 0\end{pmatrix}$，其特征值为 $\varphi = \frac{1+\sqrt{5}}{2} \approx 1.618$（黄金比例）和 $\psi = \frac{1-\sqrt{5}}{2}$。对角化后可得第 $n$ 个斐波那契数的 Binet 公式：$F_n = \frac{\varphi^n - \psi^n}{\sqrt{5}}$，将递推问题转化为解析闭合式。

**主成分分析（PCA）**：数据协方差矩阵是实对称矩阵，对其进行正交对角化 $Q^T \Sigma Q = \Lambda$ 后，$Q$ 的列（主成分方向）构成新坐标轴，$\Lambda$ 的对角元素（特征值）给出各方向的方差大小，直接用于降维决策。

**微分方程组解耦**：对线性常系数方程组 $\dot{\mathbf{x}} = A\mathbf{x}}$，令 $\mathbf{x} = P\mathbf{y}$，则 $\dot{\mathbf{y}} = \Lambda \mathbf{y}$，方程组解耦为 $n$ 个独立标量方程 $\dot{y}_i = \lambda_i y_i$，各解为 $y_i(t) = c_i e^{\lambda_i t}$，从而 $\mathbf{x}(t) = P \cdot \text{diag}(e^{\lambda_1 t}, \ldots, e^{\lambda_n t}) \cdot P^{-1} \mathbf{x}(0)$。

## 常见误区

**误区一：特征值有重根则不可对角化。**
这是最常见的错误。重根只是警示信号，不是必然结论。例如 $3I$（三阶单位矩阵的3倍）特征值 $\lambda = 3$ 代数重数为 3，但其特征空间就是整个 $\mathbb{R}^3$，几何重数也为 3，$3I$ 本身已经是对角矩阵。判断的唯一依据是**几何重数是否等于代数重数**，而非仅看是否有重根。

**误区二：对角化后的 $\Lambda$ 是唯一的。**
$\Lambda$ 的对角元素集合固定（即 $A$ 的特征值），但**排列顺序**随 $P$ 的列序不同而变化，因此对角化分解 $P^{-1}AP = \Lambda$ 不唯一。即便固定特征值顺序，每个特征向量可乘任意非零标量，$P$ 仍有无穷多种选择。

**误区三：相似矩阵必有相同的特征向量。**
相似矩阵 $A$ 与 $B = P^{-1}AP$ 的特征值相同（因特征多项式相同），但特征向量不同：若 $A\xi = \lambda\xi$，则 $B(P^{-1}\xi) = \lambda(P^{-1}\xi)$，即 $B$ 的特征向量是 $P^{-1}\xi$ 而非 $\xi$ 本身。

## 知识关联

对角化以**特征值与特征向量**为直接基础——特征多项式提供候选特征值，各特征空间的维数决定可对角化性。没有特征值分解的准备，构造变换矩阵 $P$ 无从谈起。

当矩阵**不可对角化**时，最接近的简化形式是 **Jordan 标准形**：在对角块之外，Jordan 块的超对角线位置填入 1，捕捉了几何重数小于代数重数时"缺失"的特征向量信息。Jordan 标准形是对角化的推广，对角矩阵是 Jordan 标准形的特例（所有 Jordan 块均为 $1 \times 1$）。

**矩阵指数** $e^{At}$ 的高效计算完全依赖对角化：若 $A = P\Lambda P^{-1}$，则 $e^{At} = Pe^{\Lambda t}P^{-1}$，其中 $e^{\Lambda t} = \text{diag}(e^{\lambda_1 t}, \ldots, e^{\lambda_n t})$；对不可对角化情形则需借助 Jordan 标准形展开 $e^{Jt}$，此时涉及多项式与指数函数之积，计算显著复杂化。
