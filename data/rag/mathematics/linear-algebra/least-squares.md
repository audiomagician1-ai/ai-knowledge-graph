---
id: "least-squares"
concept: "最小二乘法"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 最小二乘法

## 概述

最小二乘法（Least Squares Method）是求解超定方程组的标准技术：当方程数目 $m$ 远超过未知数数目 $n$（即 $m > n$）时，方程组 $A\mathbf{x} = \mathbf{b}$ 通常无精确解，最小二乘法寻找使残差向量 $\mathbf{b} - A\hat{\mathbf{x}}$ 的欧氏长度平方 $\|A\mathbf{x} - \mathbf{b}\|^2$ 最小的近似解 $\hat{\mathbf{x}}$。这一思想的本质是在矩阵 $A$ 的列空间 $C(A)$ 中找到距离 $\mathbf{b}$ 最近的点。

最小二乘法由高斯（Carl Friedrich Gauss）于1795年发明，用于预测谷神星轨道，并于1809年在其著作《天体运动理论》中正式发表。法国数学家勒让德（Legendre）于1805年独立发表了该方法，引发了优先权争议。高斯的贡献在于同时给出了正态误差下最小二乘估计量是最优无偏估计的理论证明（即Gauss-Markov定理），使其不仅是计算工具，更是统计推断的基石。

最小二乘法在数据拟合、测量平差、信号处理和机器学习中无处不在。一旦数据点数量超过模型参数数量，就自动进入超定情形。理解最小二乘法要求同时掌握子空间投影几何和矩阵代数两条路线，两者殊途同归，共同指向正规方程。

## 核心原理

### 超定方程组与残差最小化

设 $A$ 为 $m \times n$ 矩阵（$m > n$，$\text{rank}(A) = n$），$\mathbf{b} \in \mathbb{R}^m$，当 $\mathbf{b} \notin C(A)$ 时方程组无解。最小二乘问题转化为：

$$\min_{\mathbf{x} \in \mathbb{R}^n} \|A\mathbf{x} - \mathbf{b}\|^2 = \min_{\mathbf{x}} \sum_{i=1}^{m}(a_i^T \mathbf{x} - b_i)^2$$

其中 $a_i^T$ 是 $A$ 的第 $i$ 行。目标函数关于 $\mathbf{x}$ 可展开为 $\mathbf{x}^T A^T A \mathbf{x} - 2\mathbf{b}^T A\mathbf{x} + \mathbf{b}^T \mathbf{b}$，对 $\mathbf{x}$ 求梯度并令其为零，直接推导出正规方程，无需借助几何直觉。

### 正规方程

最小化条件等价于正规方程（Normal Equations）：

$$A^T A \hat{\mathbf{x}} = A^T \mathbf{b}$$

这里 $A^T A$ 是 $n \times n$ 对称半正定矩阵；当 $A$ 列满秩时，$A^T A$ 严格正定，唯一解为：

$$\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}$$

矩阵 $(A^T A)^{-1} A^T$ 被称为 $A$ 的 **Moore-Penrose 伪逆**（记作 $A^+$）的一种特例（列满秩情形）。正规方程之所以称"正规"（normal），正是因为方程等价于要求残差向量 $\mathbf{b} - A\hat{\mathbf{x}}$ 与 $A$ 的每一列都正交，即残差与列空间 $C(A)$ 正交。

### 投影矩阵

最小二乘解对应的 $A\hat{\mathbf{x}}$ 是 $\mathbf{b}$ 在列空间 $C(A)$ 上的正交投影，投影向量 $\hat{\mathbf{b}} = A\hat{\mathbf{x}}$ 可写为：

$$\hat{\mathbf{b}} = A(A^T A)^{-1} A^T \mathbf{b} = P\mathbf{b}$$

其中投影矩阵 $P = A(A^T A)^{-1} A^T$ 满足两个判别性质：

- **幂等性**：$P^2 = P$（投影的投影不变）
- **对称性**：$P^T = P$（正交投影的特征）

残差向量对应的补投影矩阵为 $I - P$，它将 $\mathbf{b}$ 投影到 $C(A)$ 的正交补，即左零空间 $N(A^T)$。这四个子空间的分解关系在此得到最直观的几何体现：$\mathbf{b} = \hat{\mathbf{b}} + (\mathbf{b} - \hat{\mathbf{b}})$，前者属于 $C(A)$，后者属于 $N(A^T)$，两者严格正交。

### 数值计算：QR分解优先

直接计算 $A^T A$ 再求逆会将 $A$ 的条件数平方（$\kappa(A^T A) = \kappa(A)^2$），引入数值不稳定性。实践中通过对 $A$ 做 QR 分解 $A = QR$ 将正规方程转化为 $R\hat{\mathbf{x}} = Q^T \mathbf{b}$，用回代法求解，数值稳定性远优于直接法。MATLAB 中的 `\` 运算符和 NumPy 的 `linalg.lstsq` 均默认采用 QR 或 SVD 路线，而非显式构造 $A^T A$。

## 实际应用

**直线拟合**：给定 $m$ 个数据点 $(t_i, b_i)$，拟合直线 $b = x_1 + x_2 t$，设计矩阵为 $A = \begin{bmatrix}1 & t_1 \\ \vdots & \vdots \\ 1 & t_m\end{bmatrix}$。正规方程 $A^T A \hat{\mathbf{x}} = A^T \mathbf{b}$ 展开后得到斜率和截距的经典公式：$\hat{x}_2 = \frac{m\sum t_i b_i - \sum t_i \sum b_i}{m \sum t_i^2 - (\sum t_i)^2}$。

**测量平差**：大地测量中观测方程数远超未知点坐标数，使用最小二乘平差确保残差平方和最小，同时可利用 $\hat{\sigma}^2 = \frac{\|\mathbf{b} - A\hat{\mathbf{x}}\|^2}{m-n}$ 估计观测噪声方差，分母 $m-n$ 是自由度（剩余自由度）。

**多项式拟合**：对 $d$ 次多项式拟合，设计矩阵每行为 $[1, t_i, t_i^2, \ldots, t_i^d]$，当 $d$ 接近 $m-1$ 时 $A^T A$ 的条件数急剧增大（Vandermonde矩阵病态），改用正交多项式基（如 Legendre 多项式）可显著改善数值性质。

## 常见误区

**误区一：认为正规方程总是数值求解的最佳路径。** 许多教材以正规方程作为最终答案，但直接对 $A^T A$ 求逆在矩阵条件数较大时极不稳定。例如，若 $A$ 的奇异值最大为 $10^8$、最小为 $1$，则 $A^T A$ 的条件数达 $10^{16}$，接近双精度浮点数的精度极限，导致求解结果完全失去意义。实际代码中应直接调用 `linalg.lstsq` 而非手动计算 `(A.T @ A)` 的逆。

**误区二：混淆"最小二乘解"与"精确解"的存在性条件。** 若 $A$ 列不满秩（$\text{rank}(A) < n$），$A^T A$ 奇异，最小二乘解不唯一——解集是一个仿射子空间，此时需要引入额外约束（如最小范数解 $\hat{\mathbf{x}} = A^+\mathbf{b}$，由 SVD 给出）。只有在 $A$ 列满秩的前提下，"最小二乘解唯一"才成立。

**误区三：误以为残差正交于 $A$ 的行空间。** 正规方程要求 $A^T(\mathbf{b} - A\hat{\mathbf{x}}) = \mathbf{0}$，这意味着残差 $\mathbf{e} = \mathbf{b} - A\hat{\mathbf{x}}$ 正交于 $A$ 的**列空间** $C(A)$（即属于左零空间 $N(A^T)$），而非行空间 $C(A^T)$。行空间存在于 $\mathbb{R}^n$ 中，而 $\mathbf{e}$ 存在于 $\mathbb{R}^m$ 中，两者所在空间不同，无法直接比较正交性。

## 知识关联

**依赖内积空间**：残差最小化的几何解释（正交投影）直接建立在内积诱导的范数 $\|\mathbf{v}\|^2 = \langle \mathbf{v}, \mathbf{v} \rangle$ 之上。若改变内积定义为 $\langle \mathbf{u}, \mathbf{v} \rangle_W = \mathbf{