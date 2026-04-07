---
id: "eigenvalues-eigenvectors"
concept: "特征值与特征向量"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 特征值与特征向量

## 概述

特征值与特征向量描述了线性变换的"固有拉伸方向"：若 $n$ 阶方阵 $A$ 对某个非零向量 $\boldsymbol{v}$ 满足 $A\boldsymbol{v} = \lambda\boldsymbol{v}$，则称标量 $\lambda$ 为 $A$ 的**特征值**，$\boldsymbol{v}$ 为对应的**特征向量**。特征向量在变换后方向不变（或反向），仅被 $\lambda$ 倍地缩放，这一性质使其成为理解矩阵行为的几何钥匙。

特征值的概念最早由欧拉（Leonhard Euler）在18世纪研究刚体旋转时隐式出现，柯西（Augustin-Louis Cauchy）在1840年代对实对称矩阵的谱性质给出了更系统的论述，"eigenvalue"这一德语借词（eigen意为"自身"）由希尔伯特在1904年前后引入现代数学。

在工程与科学中，$n$ 阶矩阵有 $n$ 个特征值（含重数，计于复数域），这些特征值完整地揭示了矩阵的行列式（等于所有特征值之积）和迹（等于所有特征值之和）两个核心标量，因此特征值理论是连接矩阵代数与几何变换的精确语言。

---

## 核心原理

### 特征多项式与特征方程

由 $A\boldsymbol{v} = \lambda\boldsymbol{v}$ 变形为 $(\lambda I - A)\boldsymbol{v} = \boldsymbol{0}$。要使此方程有非零解，系数矩阵必须奇异，即：

$$\det(\lambda I - A) = 0$$

展开后得到关于 $\lambda$ 的 $n$ 次多项式：

$$p(\lambda) = \lambda^n - \text{tr}(A)\lambda^{n-1} + \cdots + (-1)^n\det(A)$$

这称为 $A$ 的**特征多项式**，方程 $p(\lambda)=0$ 称为**特征方程**。以 $2\times2$ 矩阵为例：

$$A = \begin{pmatrix} 3 & 1 \\ 0 & 2 \end{pmatrix}, \quad p(\lambda) = (\lambda-3)(\lambda-2)$$

特征值为 $\lambda_1=3,\ \lambda_2=2$，两者之积 $6=\det(A)$，之和 $5=\text{tr}(A)$，验证了一般公式。

### 特征空间的计算

确定特征值 $\lambda_0$ 后，将其代入方程组 $(\lambda_0 I - A)\boldsymbol{v}=\boldsymbol{0}$，用行变换化简后求零空间，得到**特征空间** $V_{\lambda_0} = \ker(\lambda_0 I - A)$。特征空间的维数称为**几何重数**，记作 $g(\lambda_0)$；该特征值作为特征多项式根的重数称为**代数重数**，记作 $a(\lambda_0)$。两者满足：

$$1 \leq g(\lambda_0) \leq a(\lambda_0)$$

当且仅当所有特征值的几何重数等于代数重数时，矩阵可对角化。

### 实对称矩阵的谱定理

对实对称矩阵 $A=A^T$，特征值必然全为实数，且不同特征值对应的特征向量**必然正交**。这一结论不适用于一般矩阵：例如旋转矩阵

$$R = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$$

的特征多项式为 $\lambda^2+1=0$，特征值 $\pm i$ 均为复数，实平面内不存在真实的不变方向。对称矩阵的 $n$ 个特征向量可构成 $\mathbb{R}^n$ 的正交基，这是谱定理的核心结论。

### Cayley-Hamilton 定理

每个方阵都满足自身的特征方程：若 $p(\lambda)$ 为 $A$ 的特征多项式，则 $p(A)=O$（零矩阵）。对上例上三角矩阵，$p(A)=(A-3I)(A-2I)$ 必为零矩阵，这可直接验证，且提供了一种计算 $A^{-1}$ 和矩阵高次幂的实用路径。

---

## 实际应用

**主成分分析（PCA）**：协方差矩阵 $\Sigma$（必为实对称半正定矩阵）的最大特征值对应方差最大的方向。对 $p$ 维数据取前 $k$ 个特征向量作为投影基，可将维度从 $p$ 压缩到 $k$，同时保留最多的方差信息。

**稳定性分析**：微分方程 $\dot{\boldsymbol{x}} = A\boldsymbol{x}$ 的解含 $e^{\lambda t}\boldsymbol{v}$ 形式的分量。系统渐近稳定当且仅当 $A$ 的所有特征值的实部均为负数。例如，对控制系统设计，工程师通过配置期望特征值来改变闭环响应速度。

**Google PageRank**：网页排名向量是转移矩阵（列随机矩阵）对应特征值 $\lambda=1$ 的特征向量。Perron-Frobenius 定理保证正列随机矩阵的最大特征值恰好为1，且对应唯一正特征向量，这正是 PageRank 算法的数学基础。

**振动模态分析**：结构工程中质量矩阵 $M$ 和刚度矩阵 $K$ 满足广义特征值问题 $K\boldsymbol{v}=\omega^2 M\boldsymbol{v}$，特征值 $\omega^2$ 给出固有频率的平方，特征向量给出振型，用于预测共振频率。

---

## 常见误区

**误区一：特征向量是唯一的**。对给定特征值 $\lambda_0$，特征空间 $\ker(\lambda_0 I - A)$ 是一个子空间，其中任意非零向量都是特征向量，特征向量只是方向固定而非唯一。若 $\boldsymbol{v}$ 是特征向量，则 $c\boldsymbol{v}$（$c\neq 0$）也是。几何重数大于1时，存在多个线性无关的特征向量张成同一特征空间。

**误区二：重特征值的矩阵一定不可对角化**。矩阵 $A = 2I$（数量矩阵）有重特征值 $\lambda=2$，但它本身就是对角矩阵，每个向量都是特征向量。可对角化的关键条件是几何重数等于代数重数，而非特征值是否重复。真正无法对角化的例子是 Jordan 块 $\begin{pmatrix}2&1\\0&2\end{pmatrix}$，其几何重数为1而代数重数为2。

**误区三：特征值为零意味着矩阵没有意义**。$\lambda=0$ 是 $A$ 的特征值当且仅当 $\det(A)=0$，即 $A$ 奇异不可逆。此时对应特征向量恰好是 $A$ 的零空间的非零元素，$A$ 将这些向量映射到零向量，这在分析线性方程组是否有无穷多解时具有直接判断价值。

---

## 知识关联

**前置依赖**：计算特征多项式 $\det(\lambda I - A)$ 必须熟练掌握行列式的展开规则，尤其是 $n\geq 3$ 时的余子式展开；线性变换的核与像的概念直接对应特征空间计算中的零空间求法。

**后续主题**：当所有特征值的几何重数等于代数重数时，矩阵可**对角化**为 $A = P\Lambda P^{-1}$，其中 $\Lambda$ 对角线为特征值，这大幅简化矩阵幂运算。对不可对角化的情形，**Jordan 标准形**给出最接近对角形的分块结构。**奇异值分解（SVD）**是特征值理论对非方阵的推广：$A^TA$ 的特征值的非负平方根即为 $A$ 的奇异值。**二次型** $\boldsymbol{x}^T A\boldsymbol{x}$ 的符号由 $A$ 的特征值符号完全决定，从而引出**正定矩阵**（所有特征值大于零）的判别条件。