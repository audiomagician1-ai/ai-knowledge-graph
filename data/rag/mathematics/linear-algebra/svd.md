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

# 奇异值分解

## 概述

奇异值分解（Singular Value Decomposition，SVD）是将任意 $m \times n$ 实矩阵 $A$ 分解为三个矩阵乘积的定理：$A = U \Sigma V^T$，其中 $U$ 是 $m \times m$ 正交矩阵，$\Sigma$ 是 $m \times n$ 对角矩阵（对角元素非负），$V$ 是 $n \times n$ 正交矩阵。与特征值分解不同，SVD 对所有实矩阵（无论是否方阵、是否可对角化）均成立，这是它在理论上极为重要的根本原因。

SVD 的存在性最早由意大利数学家 Eugenio Beltrami 于 1873 年针对方阵给出证明，法国数学家 Camille Jordan 于 1874 年独立发现，现代一般形式的严格证明在 20 世纪初由线性算子理论完善。$\Sigma$ 的对角元素 $\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r > 0$（$r = \text{rank}(A)$）称为**奇异值**，它们是 $A^T A$（或 $AA^T$）非零特征值的正平方根，即 $\sigma_i = \sqrt{\lambda_i(A^T A)}$。

SVD 之所以在数值计算与数据科学中举足轻重，是因为它以数值稳定的方式揭示了矩阵的秩、范数、条件数等全部几何与代数信息。相比基于高斯消元的 LU 分解，Golub-Reinsch 算法（1965年）计算 SVD 的数值稳定性更高，代价是计算复杂度约为 $O(\min(m,n) \cdot mn)$。

---

## 核心原理

### 分解的存在性与唯一性

对任意秩为 $r$ 的 $m \times n$ 矩阵 $A$，$A^T A$ 是 $n \times n$ 半正定对称矩阵，因此它的特征值均非负。将这些特征值从大到小排列为 $\lambda_1 \geq \lambda_2 \geq \cdots \geq \lambda_n \geq 0$，取 $\sigma_i = \sqrt{\lambda_i}$，即得到奇异值。矩阵 $V$ 的列向量 $v_i$ 是 $A^T A$ 的单位正交特征向量（称为**右奇异向量**），$U$ 的列向量 $u_i = \frac{1}{\sigma_i} A v_i$（称为**左奇异向量**）。奇异值本身是唯一的，但当某奇异值有重数时，对应的奇异向量存在旋转自由度。

### 几何意义：线性变换的拉伸与旋转

设 $A: \mathbb{R}^n \to \mathbb{R}^m$，SVD 将这一线性映射分解为三个纯粹的几何操作：
1. $V^T$：在 $\mathbb{R}^n$ 中将标准正交基旋转为右奇异向量基（纯旋转/反射）；
2. $\Sigma$：沿各坐标轴按奇异值 $\sigma_i$ 进行**各向异性缩放**，并将维度从 $n$ 映射到 $m$；
3. $U$：在 $\mathbb{R}^m$ 中将缩放后的向量旋转到最终方向（纯旋转/反射）。

以 $2 \times 2$ 矩阵为例：单位圆经 $A$ 变换后变成椭圆，椭圆的两个半轴长度恰好是 $\sigma_1, \sigma_2$，方向对应 $u_1, u_2$。这是 SVD 几何意义的直接体现。

### 截断SVD与低秩逼近

将奇异值按大小排列后，可以仅保留前 $k$ 个最大奇异值，构造**截断SVD**：

$$A_k = \sum_{i=1}^{k} \sigma_i u_i v_i^T$$

Eckart-Young-Mirsky 定理（1936年）严格证明：$A_k$ 是所有秩不超过 $k$ 的矩阵中，在 Frobenius 范数和谱范数意义下最接近 $A$ 的矩阵。最小逼近误差为 $\|A - A_k\|_F = \sqrt{\sigma_{k+1}^2 + \cdots + \sigma_r^2}$。这一定理是图像压缩、推荐系统和主成分分析（PCA）的数学基石。

### 奇异值与矩阵基本量的关系

- **秩**：$\text{rank}(A)$ = 非零奇异值的个数 $r$
- **谱范数**：$\|A\|_2 = \sigma_1$（最大奇异值）
- **Frobenius范数**：$\|A\|_F = \sqrt{\sigma_1^2 + \sigma_2^2 + \cdots + \sigma_r^2}$
- **条件数**：$\kappa(A) = \sigma_1 / \sigma_r$（用于衡量线性方程组的数值稳定性）
- **伪逆**：$A^+ = V \Sigma^+ U^T$，其中 $\Sigma^+$ 将每个非零 $\sigma_i$ 替换为 $1/\sigma_i$

---

## 实际应用

**图像压缩**：一张 $1000 \times 1000$ 的灰度图像可以视为秩高达1000的矩阵。通过保留前50个奇异值，存储量从 $10^6$ 个数值降低到 $50 \times (1000 + 1000 + 1) \approx 10^5$ 个，压缩比约10:1，同时在视觉上保留绝大部分信息。

**推荐系统（隐语义模型）**：Netflix 竞赛（2006-2009）的获胜算法核心之一是对用户-电影评分矩阵（约48万用户 × 1.7万电影）进行截断SVD，将矩阵分解为用户隐因子与电影隐因子，$k$ 通常取20-100，大幅低于原始维度。

**主成分分析（PCA）**：对中心化数据矩阵 $X$（$n$ 个样本，$p$ 个特征）做 SVD，其右奇异向量即为 PCA 的主成分方向，奇异值的平方除以 $n-1$ 等于对应方差。这是比对协方差矩阵求特征值更数值稳定的 PCA 实现路径。

**最小二乘问题的广义解**：当 $Ax = b$ 无精确解时（超定系统），最小范数最小二乘解为 $x^+ = A^+ b = V \Sigma^+ U^T b$，SVD 给出了这个解的完整数值稳定算法。

---

## 常见误区

**误区一：奇异值就是特征值**。奇异值是 $A^T A$ 特征值的正平方根，而非 $A$ 本身的特征值。对于方阵 $A$，其特征值可以是负数或复数，但奇异值始终是非负实数。例如，矩阵 $A = \begin{pmatrix} 0 & 2 \\ 0 & 0 \end{pmatrix}$ 的特征值均为0，但奇异值为2和0——两者完全不同。

**误区二：$U$ 的列是 $A$ 的特征向量**。$U$ 的列是 $AA^T$ 的特征向量，$V$ 的列是 $A^T A$ 的特征向量，两者都不是 $A$ 本身的特征向量（除非 $A$ 是对称正定矩阵，此时 $U = V$，奇异值等于特征值）。

**误区三：截断SVD保留最大奇异值总是最优压缩策略**。Eckart-Young定理保证的"最优"是在矩阵范数意义下的全局最优，但在特定应用（如语音降噪）中，感知质量并不完全与 Frobenius 范数对齐，有时需要根据信号特性选择性保留某些奇异值而非严格按大小排序。

---

## 知识关联

**前序知识**：SVD 的推导依赖**特征值与特征向量**——奇异值定义为 $A^T A$ 的特征值开方，右奇异向量就是 $A^T A$ 的特征向量。**正交矩阵**的性质（$Q^T Q = I$、保长度、表示旋转/反射）直接决定了 $U$ 和 $V$ 的几何解释，以及为何 SVD 数值稳定（正交变换不放大舍入误差）。没有这两个概念，就无法区分 SVD 与普通矩阵乘法分解的本质差异。

**横向联系**：SVD 与 QR 分解都用于求解最小二乘问题，但 SVD 额外揭示秩亏情况；SVD 与 LU 分解相比数值稳定但计算更昂贵；紧 SVD（Compact SVD，只保留 $r$ 个非零奇异值）与满 SVD 在实现层面需要区分。在统计学中，SVD 与协方差矩阵的谱分解通过 $A = X / \sqrt{n-1}$ 直接相连，是理解 PCA 变换矩阵的代数基础。