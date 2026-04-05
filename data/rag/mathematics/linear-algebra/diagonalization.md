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

# 对角化

## 概述

矩阵对角化是指将一个 $n \times n$ 矩阵 $A$ 通过相似变换化为对角矩阵 $\Lambda$ 的过程，即寻找可逆矩阵 $P$ 使得 $P^{-1}AP = \Lambda$，其中 $\Lambda = \text{diag}(\lambda_1, \lambda_2, \ldots, \lambda_n)$ 的对角元素恰好是 $A$ 的特征值。这一变换不改变矩阵的行列式、迹和特征多项式，但将复杂的矩阵运算大幅简化。

对角化思想可追溯至18世纪欧拉和拉格朗日对二次型化简的研究，他们在分析刚体旋转和振动问题时发现了主轴变换的几何意义。1850年代柯西系统整理了行列式理论，1878年弗罗贝尼乌斯（Frobenius）正式建立了矩阵相似理论，使对角化有了严格的代数基础。

对角化之所以重要，在于对角矩阵的幂运算极为简单：$\Lambda^k = \text{diag}(\lambda_1^k, \ldots, \lambda_n^k)$，因此 $A^k = P\Lambda^k P^{-1}$，这使得求解线性递推关系、计算矩阵指数、分析动力系统长期行为等问题都变得高效可行。

## 核心原理

### 可对角化的充要条件

矩阵 $A$ 可对角化，**当且仅当** $A$ 有 $n$ 个线性无关的特征向量。这等价于：对 $A$ 的每一个特征值 $\lambda_i$，其几何重数（即特征空间 $\ker(A - \lambda_i I)$ 的维数）等于其代数重数（即 $\lambda_i$ 作为特征多项式 $\det(\lambda I - A)$ 根的重数）。

两个常用的充分条件：（1）若 $A$ 的 $n$ 个特征值两两不同，则 $A$ 必可对角化；（2）实对称矩阵必可对角化（更强：必可正交对角化）。注意第一个是充分而非必要条件——有重特征值的矩阵也可能可对角化，例如单位矩阵 $I_n$ 的唯一特征值 $\lambda = 1$ 代数重数为 $n$，几何重数也为 $n$，因此 $I_n$ 本身已是对角形。

### 对角化的操作步骤

设 $A$ 为 $n$ 阶矩阵，对角化流程为：
1. 求特征多项式 $\det(\lambda I - A) = 0$，解出所有特征值 $\lambda_1, \ldots, \lambda_n$（计重数）。
2. 对每个特征值 $\lambda_i$，求解齐次方程组 $(A - \lambda_i I)\mathbf{x} = \mathbf{0}$，得到基础特征向量。
3. 将所有特征向量按列排列构成矩阵 $P = [\mathbf{p}_1, \mathbf{p}_2, \ldots, \mathbf{p}_n]$。
4. 验证 $P$ 可逆，则 $P^{-1}AP = \text{diag}(\lambda_1, \ldots, \lambda_n)$，其中对角线顺序与 $P$ 中列向量顺序对应。

关键等式 $AP = P\Lambda$ 揭示了本质：矩阵 $P$ 的第 $j$ 列 $\mathbf{p}_j$ 满足 $A\mathbf{p}_j = \lambda_j \mathbf{p}_j$，这正是特征向量定义。因此 $P$ 的各列必须恰好是对应特征值的特征向量，列的排列顺序决定了 $\Lambda$ 对角线元素的顺序。

### 相似变换的几何解释

相似变换 $P^{-1}AP$ 的几何意义是**换基**：$P$ 的列向量构成新基，在这组基下，线性变换 $A$ 的矩阵表示变为沿各坐标轴方向的纯伸缩变换 $\Lambda$。每个特征方向被拉伸 $\lambda_i$ 倍，不发生旋转或剪切，这就是"对角"形状的几何本质。相似矩阵具有相同的特征值、相同的行列式（$\det A = \lambda_1\lambda_2\cdots\lambda_n$）和相同的迹（$\text{tr}(A) = \lambda_1 + \lambda_2 + \cdots + \lambda_n$），这三个量在相似变换下保持不变。

## 实际应用

**线性递推数列的通项公式**：斐波那契数列满足 $F_{n+1} = F_n + F_{n-2}$，可写成 $\begin{pmatrix} F_{n+1} \\ F_n \end{pmatrix} = A^n \begin{pmatrix} 1 \\ 1 \end{pmatrix}$，其中 $A = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}$。对角化 $A$ 后，两个特征值为黄金比例 $\varphi = \frac{1+\sqrt{5}}{2} \approx 1.618$ 和 $\psi = \frac{1-\sqrt{5}}{2}$，由此得到比内公式 $F_n = \frac{\varphi^n - \psi^n}{\sqrt{5}}$。

**主成分分析（PCA）**：数据协方差矩阵是实对称矩阵，必可正交对角化为 $P^T\Sigma P = \Lambda$。$P$ 的列向量（主成分方向）给出数据方差最大的正交方向，$\Lambda$ 的对角元素（特征值）即各方向上的方差大小，这是高维数据降维的理论基础。

**微分方程组**：对线性自治系统 $\dot{\mathbf{x}} = A\mathbf{x}$，若 $A$ 可对角化，令 $\mathbf{x} = P\mathbf{y}$，则方程解耦为 $\dot{y}_i = \lambda_i y_i$，各分量独立求解为 $y_i(t) = y_i(0)e^{\lambda_it}$，从而 $\mathbf{x}(t) = Pe^{\Lambda t}P^{-1}\mathbf{x}(0)$。系统稳定性完全由特征值的实部正负决定。

## 常见误区

**误区一：有重特征值就一定不能对角化。** 这是最常见的错误判断。矩阵 $A = \begin{pmatrix} 2 & 0 \\ 0 & 2 \end{pmatrix}$ 有重特征值 $\lambda = 2$（代数重数2），但特征空间是整个 $\mathbb{R}^2$（几何重数2），$A$ 本身已是对角矩阵。真正不能对角化的反例是 $B = \begin{pmatrix} 2 & 1 \\ 0 & 2 \end{pmatrix}$（Jordan块），其特征空间只有一维，导致几何重数1 < 代数重数2。

**误区二：混淆相似变换与合同变换。** 对角化使用的是相似变换 $P^{-1}AP$，变换矩阵 $P$ 的列是特征向量，不要求 $P$ 是正交矩阵。而二次型化标准形使用合同变换 $P^T AP$，要求将实对称矩阵化为对角形（正交对角化时 $P$ 恰好满足 $P^{-1} = P^T$，两种变换重合）。将一般矩阵强行套用合同变换公式是错误的。

**误区三：误以为对角化后的特征值顺序固定。** $P^{-1}AP = \Lambda$ 中对角线的顺序完全由 $P$ 中列向量的排列顺序决定，同一矩阵存在无穷多种对角化形式（交换 $P$ 的列，相应交换 $\Lambda$ 的对角元素）。使用对角化计算 $A^k$ 时，必须保证 $P$ 和 $\Lambda$ 中特征向量与特征值的对应关系一致，否则结果错误。

## 知识关联

对角化以**特征值与特征向量**为直接前提，特征多项式 $\det(\lambda I - A)$ 的求解和特征空间 $\ker(A-\lambda I)$ 的计算是对角化操作的核心步骤，没有这两个工具无法执行对角化。

当矩阵不可对角化时（即存在某特征值的几何重数小于代数重数），需要引入 **Jordan 标准形**作为退而求其次的"最简形"。Jordan 标准形在对角线上放置特征值，在超对角线上放置1，是不可对角化矩阵的最优相似简化，对角化是 Jordan 标准形的特例（所有 Jordan 块大小为1）。

**矩阵指数** $e^A = Pe^{\Lambda}P^{-1}$ 的实际计算完全依赖对角化：$e^\Lambda = \text{diag}(e^{\lambda_1}, \ldots, e^{\lambda_n})$，将矩阵指数化为标量指数的组合。若 $A$ 不可对角化，则须通过 Jordan 标准形计算矩阵指数，需要用到 $e^{Jt}$ 含多项式因子的展开式，计算复杂度显著上升。