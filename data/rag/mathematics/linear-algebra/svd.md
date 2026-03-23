---
id: "svd"
concept: "奇异值分解"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 8
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 34.7
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 奇异值分解

## 概述

奇异值分解（Singular Value Decomposition，简称 SVD）是将任意 $m \times n$ 实矩阵 $A$ 分解为三个矩阵乘积 $A = U\Sigma V^T$ 的方法，其中 $U$ 是 $m \times m$ 正交矩阵，$\Sigma$ 是 $m \times n$ 对角矩阵，$V$ 是 $n \times n$ 正交矩阵。SVD 的突破性在于，它不要求矩阵 $A$ 是方阵，也不要求 $A$ 可对角化，这使它远比特征分解更具普适性。

SVD 的理论基础由意大利数学家贝尔特拉米（Eugenio Beltrami）在 1873 年首次发表于实对称矩阵情形，随后法国数学家若尔当（Camille Jordan）于 1874 年独立给出了更一般的结论。现代计算意义上的数值稳定 SVD 算法由戈勒布（Gene Golub）和卡汉（William Kahan）于 1965 年提出，奠定了今日数值线性代数的重要基石。

SVD 之所以重要，是因为它揭示了矩阵作为线性变换的"本质结构"：任何线性变换都可以分解为一次旋转（或反射）、一次沿坐标轴方向的伸缩、再加一次旋转。在数据压缩、推荐系统、自然语言处理和图像处理中，SVD 提供了提取"最重要信息"的数学工具。

---

## 核心原理

### 奇异值的定义与计算

$A$ 的奇异值定义为 $A^TA$（$n \times n$ 半正定矩阵）特征值的非负平方根。设 $A^TA$ 的特征值为 $\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_n \geq 0$，则第 $i$ 个奇异值为：

$$\sigma_i = \sqrt{\lambda_i}$$

对角矩阵 $\Sigma$ 的对角线依次排列 $\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r > 0$（$r = \text{rank}(A)$），其余位置为零。$V$ 的列向量是 $A^TA$ 的特征向量（称为**右奇异向量**），$U$ 的列向量是 $AA^T$ 的特征向量（称为**左奇异向量**）。非零奇异值对应部分满足关系 $Av_i = \sigma_i u_i$，这是 SVD 的核心等式。

### 几何意义

SVD 将矩阵 $A$ 代表的线性变换分解为三步几何操作：
1. **$V^T$**：在输入空间 $\mathbb{R}^n$ 中执行旋转（或反射），将标准基对齐到 $A^TA$ 的特征方向；
2. **$\Sigma$**：沿各坐标轴方向分别缩放 $\sigma_1, \sigma_2, \ldots, \sigma_r$ 倍（同时处理维度的升降）；
3. **$U$**：在输出空间 $\mathbb{R}^m$ 中再执行旋转（或反射）。

直观而言，SVD 说明每一个线性变换都能把某组正交方向（右奇异向量）映射为另一组正交方向（左奇异向量），缩放比例恰好是奇异值 $\sigma_i$。当 $\sigma_1 \gg \sigma_2 \gg \cdots$ 时，矩阵的"信息"高度集中于前几个奇异方向。

### 低秩近似（截断 SVD）

给定秩为 $r$ 的矩阵 $A$，取前 $k < r$ 个最大奇异值构造截断分解：

$$A_k = \sum_{i=1}^{k} \sigma_i u_i v_i^T$$

Eckart–Young 定理（1936 年）保证 $A_k$ 是所有秩不超过 $k$ 的矩阵中，在 Frobenius 范数意义下最接近 $A$ 的矩阵，即：

$$\|A - A_k\|_F = \sqrt{\sigma_{k+1}^2 + \sigma_{k+2}^2 + \cdots + \sigma_r^2}$$

这一性质使截断 SVD 成为数据降维的最优线性方法。

### SVD 与矩阵基本子空间的关系

$V$ 的前 $r$ 列（对应正奇异值的右奇异向量）构成 $A$ 的**行空间**的标准正交基，后 $n-r$ 列构成**零空间**的正交基；$U$ 的前 $r$ 列构成 $A$ 的**列空间**的标准正交基，后 $m-r$ 列构成**左零空间**的正交基。因此，SVD 在一次分解中同时给出矩阵的四个基本子空间的正交基，这是高斯消元法无法直接提供的。

---

## 实际应用

**图像压缩**：一张 $512 \times 512$ 的灰度图像可视为矩阵 $A$。取前 $k = 50$ 个奇异值重建 $A_{50}$，存储量从 $512^2 = 262144$ 个数降至 $50 \times (512 + 512 + 1) \approx 51250$ 个数，压缩比约 5:1，同时保留了图像的主要结构特征。

**推荐系统（矩阵分解）**：Netflix Prize 竞赛（2009 年）的获胜方案核心即 SVD 的变体。用户-电影评分矩阵极为稀疏，通过 SVD 分解提取潜在因子，$\sigma_1$ 对应"最主流偏好"方向，前 $k \approx 100$ 个奇异值即可捕获大部分评分模式。

**伪逆与最小二乘**：当方程组 $Ax = b$ 无精确解时，Moore–Penrose 伪逆 $A^+ = V\Sigma^+ U^T$ 直接由 SVD 给出（$\Sigma^+$ 将非零奇异值取倒数），最小二乘解为 $\hat{x} = A^+ b$，避免了正规方程 $A^TA x = A^Tb$ 的数值不稳定问题。

**主成分分析（PCA）**：对中心化数据矩阵 $X$（$n \times p$），PCA 的主成分方向恰好是 $X$ 的右奇异向量 $V$ 的列，方差贡献量正比于 $\sigma_i^2$。因此 SVD 是计算 PCA 的首选数值方法，而非先计算协方差矩阵再做特征分解。

---

## 常见误区

**误区一：奇异值等于特征值**。仅当 $A$ 是对称半正定矩阵时，奇异值才与特征值相同。一般情况下，矩阵 $\begin{pmatrix}0 & 2\\ 0 & 0\end{pmatrix}$ 的特征值均为 0，但奇异值为 2 和 0，二者截然不同。特征值可以是负数或复数，而奇异值永远是非负实数。

**误区二：SVD 与特征分解在方阵上等价**。即使 $A$ 是方阵，SVD 分解中 $U$ 和 $V$ 通常是不同的正交矩阵（$U \neq V$），而特征分解 $A = P\Lambda P^{-1}$ 中仅有一个基矩阵 $P$。只有当 $A$ 是实对称正定矩阵时，二者的分解形式才真正统一（此时 $U = V$，奇异值等于特征值）。

**误区三：截断 SVD 总能任意减少误差**。截断误差下界为 $\sigma_{k+1}$，无法通过调整 $U$ 或 $V$ 使其更小——Eckart–Young 定理同时也是一个**下界**定理。当奇异值衰减缓慢（如 $\sigma_i \sim 1/i$），则低秩近似的精度有限，不能期望用少量奇异值重建精确矩阵。

---

## 知识关联

**前置知识的承接**：SVD 的构造直接依赖**正交矩阵**的性质——$U^TU = I$ 和 $V^TV = I$ 确保变换的旋转/反射本质，且保距性使奇异值的几何意义（伸缩量）得以清晰定义。**特征值与特征向量**的知识用于计算 $A^TA$ 和 $AA^T$ 的谱分解，从而获得 $V$ 和 $U$；正是因为 $A^TA$ 是对称半正定矩阵，其特征值必为非负实数，奇异值才有意义。

**向更高层次的延伸**：掌握 SVD 后，可自然推进到**主成分分析**（将 SVD 应用于数据矩阵实现降维）、**广义逆与最小二乘理论**（以 SVD 为核心的数值解法）、以及**矩阵补全**与**张量分解**等现代数据科学方法。在函数分析框架下，SVD 推广为无穷维 Hilbert 空间上紧算子的谱定理。
