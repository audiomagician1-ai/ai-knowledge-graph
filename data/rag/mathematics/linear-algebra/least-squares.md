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
quality_tier: "pending-rescore"
quality_score: 36.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 最小二乘法

## 概述

最小二乘法（Least Squares Method）是一种在方程组无精确解时寻找"最优近似解"的数学方法。其核心思想是：当线性方程组 $A\mathbf{x} = \mathbf{b}$ 无解时，寻找向量 $\hat{\mathbf{x}}$，使得残差向量 $\mathbf{b} - A\hat{\mathbf{x}}$ 的欧几里得范数的平方 $\|A\mathbf{x} - \mathbf{b}\|^2$ 最小。"二乘"即"平方"，最小化的对象是误差的平方和，而非误差之和或绝对值之和。

该方法由德国数学家卡尔·弗里德里希·高斯（Carl Friedrich Gauss）于1795年首次使用，并由法国数学家勒让德（Adrien-Marie Legendre）于1805年在其著作中公开发表。高斯用最小二乘法预测了谷神星的轨道，这是其在天文计算中的第一次重大应用。历史上关于发明权存在争议，但两人的独立发现共同奠定了这一方法的地位。

最小二乘法之所以重要，是因为超定方程组（方程数 $m$ 多于未知数 $n$，即 $m > n$）在数据拟合、传感器测量、经济建模等实际场景中无处不在——测量误差使得精确解几乎不可能存在。此时最小二乘解给出了在列空间 $C(A)$ 上的最佳逼近。

---

## 核心原理

### 超定方程组与残差最小化

当 $A$ 为 $m \times n$ 矩阵（$m > n$）且 $\mathbf{b} \notin C(A)$ 时，方程组 $A\mathbf{x} = \mathbf{b}$ 无解。最小二乘法将问题转化为：

$$\min_{\mathbf{x} \in \mathbb{R}^n} \|A\mathbf{x} - \mathbf{b}\|^2 = \min_{\mathbf{x}} \sum_{i=1}^{m}(a_i^T \mathbf{x} - b_i)^2$$

几何上，$A\mathbf{x}$ 遍历列空间 $C(A)$，而 $\mathbf{b}$ 不在其中。最小化残差范数等价于在 $C(A)$ 中找到距 $\mathbf{b}$ 最近的点，即 $\mathbf{b}$ 在 $C(A)$ 上的正交投影 $\hat{\mathbf{b}} = A\hat{\mathbf{x}}$。最优残差 $\mathbf{e} = \mathbf{b} - A\hat{\mathbf{x}}$ 必须垂直于列空间，即 $\mathbf{e} \perp C(A)$，这意味着 $\mathbf{e}$ 落在 $A$ 的左零空间 $N(A^T)$ 中。

### 正规方程（Normal Equations）

由正交条件 $A^T(\mathbf{b} - A\hat{\mathbf{x}}) = \mathbf{0}$，直接推导出正规方程：

$$A^T A \hat{\mathbf{x}} = A^T \mathbf{b}$$

当 $A$ 的各列线性无关（即 $A$ 列满秩，$\text{rank}(A) = n$）时，$A^T A$ 是 $n \times n$ 的可逆对称正定矩阵，最小二乘解唯一：

$$\hat{\mathbf{x}} = (A^T A)^{-1} A^T \mathbf{b}$$

其中 $(A^T A)^{-1} A^T$ 称为 $A$ 的**伪逆**（Moore-Penrose pseudoinverse），记作 $A^+$。当 $A$ 列满秩时 $A^+ = (A^TA)^{-1}A^T$，它是 $A$ 的"左逆"，满足 $A^+ A = I_n$，但 $AA^+ \neq I_m$。

### 投影矩阵（Projection Matrix）

将最小二乘解代入，得到 $\mathbf{b}$ 在 $C(A)$ 上的投影：

$$\hat{\mathbf{b}} = A\hat{\mathbf{x}} = A(A^T A)^{-1} A^T \mathbf{b} = P\mathbf{b}$$

其中投影矩阵 $P = A(A^T A)^{-1} A^T$，维度为 $m \times m$。$P$ 具有两个关键性质：
- **幂等性**：$P^2 = P$（对已在列空间中的向量再投影结果不变）
- **对称性**：$P^T = P$（正交投影特有性质，斜投影矩阵不对称）

互补投影矩阵 $I - P$ 将 $\mathbf{b}$ 投影到 $N(A^T)$ 上，即 $(I-P)\mathbf{b} = \mathbf{e}$ 就是最优残差向量。注意 $\text{rank}(P) = n$，$\text{rank}(I-P) = m - n$，两个子空间维度之和为 $m$，对应 $\mathbb{R}^m$ 的完整正交分解。

---

## 实际应用

**直线拟合**是最小二乘法的经典应用。设有 $m$ 个数据点 $(t_i, b_i)$，拟合直线 $b = c + dt$，则构成方程组：

$$A = \begin{pmatrix} 1 & t_1 \\ 1 & t_2 \\ \vdots & \vdots \\ 1 & t_m \end{pmatrix}, \quad \mathbf{x} = \begin{pmatrix} c \\ d \end{pmatrix}$$

正规方程 $A^TA\hat{\mathbf{x}} = A^T\mathbf{b}$ 展开后得到：

$$\begin{pmatrix} m & \sum t_i \\ \sum t_i & \sum t_i^2 \end{pmatrix} \begin{pmatrix} \hat{c} \\ \hat{d} \end{pmatrix} = \begin{pmatrix} \sum b_i \\ \sum t_i b_i \end{pmatrix}$$

这正是统计学中线性回归斜率和截距的封闭式公式。例如对3个点 $(1,1),(2,2),(3,2)$，$A^TA = \begin{pmatrix}3&6\\6&14\end{pmatrix}$，解得 $\hat{d} = 0.5$，$\hat{c} = 1/3$。

**多项式拟合**时，将 $A$ 的各列替换为 $1, t, t^2, \ldots, t^k$，同样适用正规方程，这是信号处理中多项式趋势去除的标准做法。

---

## 常见误区

**误区1：认为最小二乘解必须满足 $A\hat{\mathbf{x}} = \mathbf{b}$。**
最小二乘解 $\hat{\mathbf{x}}$ 满足的是正规方程 $A^TA\hat{\mathbf{x}} = A^T\mathbf{b}$，而非原方程。$\hat{\mathbf{b}} = A\hat{\mathbf{x}}$ 是 $\mathbf{b}$ 的投影，通常 $\hat{\mathbf{b}} \neq \mathbf{b}$。将 $\hat{\mathbf{x}}$ 代回原方程并不能消去残差，这是超定系统的本质。

**误区2：$A^TA$ 总是可逆的。**
$A^TA$ 可逆的充要条件是 $A$ 列满秩（$\text{rank}(A) = n$）。若 $A$ 的列向量线性相关，$A^TA$ 奇异，最小二乘解不唯一——此时存在一个解的仿射子空间，各解的范数最小者由伪逆 $A^+$ 给出（利用奇异值分解）。

**误区3：直接用正规方程求解数值上足够精确。**
在计算机实现中，$A^TA$ 的条件数是 $A$ 条件数的平方（$\kappa(A^TA) = \kappa(A)^2$），即使 $A$ 条件数适中，$A^TA$ 的条件数也可能极大，导致数值不稳定。实际应用（如MATLAB的 `\` 运算符）使用 $A$ 的 $QR$ 分解而非显式计算 $A^TA$ 来求解正规方程，以保证数值稳定性。

---

## 知识关联

最小二乘法依赖**内积空间**中正交性的概念——残差 $\mathbf{e}$ 与列空间的正交条件 $A^T\mathbf{e} = \mathbf{0}$ 直接来自欧几里得内积的性质。没有内积定义的空间中无法讨论"最小距离"意义下的投影。

**四个基本子空间**为最小二乘法提供了几何框架：最优残差 $\mathbf{e}$ 落在左零空间 $N(A^T)$ 中，而投影 $\hat{\mathbf{b}}$ 落在列空间 $C(A)$ 中，二者构成 $\mathbb{R}^m$ 的正交补分解。若 $\mathbf{b}$ 在 $C(A)$ 中，则最小二乘问题退化为精确求解。

向前看，最小二乘法直接构成**线性回归**的数学基础：统计线性回归模型 $Y = X\beta + \varepsilon$ 中，参数的最小二乘估计量 $\hat{\beta} = (X^TX
