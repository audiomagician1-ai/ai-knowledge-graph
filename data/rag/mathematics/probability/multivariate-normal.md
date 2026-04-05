---
id: "multivariate-normal"
concept: "多元正态分布"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 8
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

# 多元正态分布

## 概述

多元正态分布（Multivariate Normal Distribution）是一维正态分布向多维空间的推广，描述多个连续随机变量的联合分布，其中每个变量以及任意线性组合都服从正态分布。若随机向量 $\mathbf{X} = (X_1, X_2, \ldots, X_k)^T$ 服从多元正态分布，记作 $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$，其中 $\boldsymbol{\mu}$ 为均值向量，$\boldsymbol{\Sigma}$ 为 $k \times k$ 协方差矩阵。

多元正态分布的数学基础由高斯（Carl Friedrich Gauss）在18世纪末至19世纪初处理天文观测误差时逐步建立，后由皮尔逊（Karl Pearson）于1896年系统化为二元正态分布的相关系数理论。20世纪初，随着矩阵运算的成熟，完整的 $k$ 维推广才被严格定义并广泛应用于统计学。

多元正态分布之所以在概率论与统计学中占据核心地位，原因在于其对线性变换的封闭性——任何多元正态分布的线性变换仍服从多元正态分布，这一性质使得在高维数据分析、贝叶斯推断和机器学习中的计算变得可处理。

---

## 核心原理

### 概率密度函数与参数

当协方差矩阵 $\boldsymbol{\Sigma}$ 为正定矩阵（即非退化情形）时，$k$ 维随机向量 $\mathbf{X}$ 的概率密度函数为：

$$f(\mathbf{x}) = \frac{1}{(2\pi)^{k/2} |\boldsymbol{\Sigma}|^{1/2}} \exp\!\left(-\frac{1}{2}(\mathbf{x} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})\right)$$

其中：
- $\boldsymbol{\mu} \in \mathbb{R}^k$ 是均值向量，决定分布的中心位置；
- $\boldsymbol{\Sigma}$ 是 $k \times k$ 正定对称协方差矩阵，决定各维度的方差及维度间的线性相关性；
- $|\boldsymbol{\Sigma}|$ 表示 $\boldsymbol{\Sigma}$ 的行列式；
- 指数中的二次型 $(\mathbf{x} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})$ 称为**马氏距离（Mahalanobis Distance）**的平方，衡量点 $\mathbf{x}$ 到均值中心的加权距离，等概率密度面是以 $\boldsymbol{\mu}$ 为中心的椭球面。

当 $k=2$ 时，$\boldsymbol{\Sigma}$ 由两个方差 $\sigma_1^2, \sigma_2^2$ 和相关系数 $\rho \in (-1, 1)$ 完全决定，此时 $|\boldsymbol{\Sigma}| = \sigma_1^2 \sigma_2^2 (1 - \rho^2)$。

### 线性变换封闭性

设 $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$，$\mathbf{A}$ 是 $m \times k$ 的常数矩阵，$\mathbf{b}$ 是 $m$ 维常数向量，则：

$$\mathbf{Y} = \mathbf{A}\mathbf{X} + \mathbf{b} \sim \mathcal{N}(\mathbf{A}\boldsymbol{\mu} + \mathbf{b},\ \mathbf{A}\boldsymbol{\Sigma}\mathbf{A}^T)$$

这一性质的直接推论是：多元正态分布的任意**边缘分布**均为正态分布——取 $\mathbf{A}$ 为提取特定行的矩阵即可。例如，$(X_1, X_2, \ldots, X_k)^T \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ 则每个 $X_i \sim \mathcal{N}(\mu_i, \sigma_{ii})$，其中 $\sigma_{ii}$ 是 $\boldsymbol{\Sigma}$ 的第 $i$ 个对角元素。

### 不相关与独立的等价关系

在多元正态分布中，不相关与独立**等价**，这是一维正态分布没有的特殊性质。具体而言，若 $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$，则分量 $X_i$ 与 $X_j$ 相互独立当且仅当 $\text{Cov}(X_i, X_j) = \sigma_{ij} = 0$（即 $\boldsymbol{\Sigma}$ 中对应位置为零）。等价地，当 $\boldsymbol{\Sigma}$ 为对角矩阵时，所有分量相互独立，联合密度分解为各边缘密度之积。

### 条件分布

对 $\mathbf{X} = (\mathbf{X}_1^T, \mathbf{X}_2^T)^T$ 按块分解，均值和协方差矩阵对应分块为：

$$\boldsymbol{\mu} = \begin{pmatrix}\boldsymbol{\mu}_1 \\ \boldsymbol{\mu}_2\end{pmatrix},\quad \boldsymbol{\Sigma} = \begin{pmatrix}\boldsymbol{\Sigma}_{11} & \boldsymbol{\Sigma}_{12} \\ \boldsymbol{\Sigma}_{21} & \boldsymbol{\Sigma}_{22}\end{pmatrix}$$

则给定 $\mathbf{X}_2 = \mathbf{x}_2$ 时，$\mathbf{X}_1$ 的条件分布仍为正态分布：

$$\mathbf{X}_1 \mid \mathbf{X}_2 = \mathbf{x}_2 \sim \mathcal{N}\!\left(\boldsymbol{\mu}_1 + \boldsymbol{\Sigma}_{12}\boldsymbol{\Sigma}_{22}^{-1}(\mathbf{x}_2 - \boldsymbol{\mu}_2),\ \boldsymbol{\Sigma}_{11} - \boldsymbol{\Sigma}_{12}\boldsymbol{\Sigma}_{22}^{-1}\boldsymbol{\Sigma}_{21}\right)$$

条件均值 $\boldsymbol{\mu}_1 + \boldsymbol{\Sigma}_{12}\boldsymbol{\Sigma}_{22}^{-1}(\mathbf{x}_2 - \boldsymbol{\mu}_2)$ 是 $\mathbf{x}_2$ 的线性函数，这正是线性回归的理论基础；条件方差 $\boldsymbol{\Sigma}_{11} - \boldsymbol{\Sigma}_{12}\boldsymbol{\Sigma}_{22}^{-1}\boldsymbol{\Sigma}_{21}$（Schur 补）不依赖于 $\mathbf{x}_2$ 的具体取值。

---

## 实际应用

**主成分分析（PCA）的理论基础**：当数据服从多元正态分布 $\mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$ 时，对 $\boldsymbol{\Sigma}$ 进行特征值分解 $\boldsymbol{\Sigma} = \mathbf{Q}\boldsymbol{\Lambda}\mathbf{Q}^T$，新坐标系下各主成分相互独立，方差为对应特征值 $\lambda_i$。椭球等密度线的主轴方向即为特征向量方向，轴长正比于 $\sqrt{\lambda_i}$。

**贝叶斯线性回归**：若先验分布设为 $\boldsymbol{\beta} \sim \mathcal{N}(\mathbf{0}, \tau^2 \mathbf{I})$，似然为 $\mathbf{y} \mid \boldsymbol{\beta} \sim \mathcal{N}(\mathbf{X}\boldsymbol{\beta}, \sigma^2 \mathbf{I})$，利用多元正态条件分布公式，后验分布 $\boldsymbol{\beta} \mid \mathbf{y}$ 仍为多元正态分布，均值即为岭回归估计量。

**高斯过程（Gaussian Process）**：高斯过程可视为无限维多元正态分布，任意有限个时间点上的函数值联合服从多元正态分布，协方差由核函数（如 RBF 核 $k(x, x') = \exp(-\|x - x'\|^2 / 2l^2)$）决定，广泛应用于贝叶斯优化和时空数据建模。

---

## 常见误区

**误区一：边缘正态推出联合正态**

若 $X_1 \sim \mathcal{N}(0,1)$ 且 $X_2 \sim \mathcal{N}(0,1)$，不能断定 $(X_1, X_2)^T$ 服从二元正态分布。反例：令 $X_2 = X_1 \cdot \text{sign}(U)$（$U$ 为独立均匀分布），则各边缘均为标准正态，但联合分布的概率质量集中在两条对角线附近，密度函数与二元正态完全不同，$X_1^2 + X_2^2$ 的分布也与自由度2的卡方分布不符。

**误区二：协方差矩阵半正定时密度函数消失**

当 $\boldsymbol{\Sigma}$ 半正定（奇异）时，多元正态分布退化，概