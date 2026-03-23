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
quality_tier: "pending-rescore"
quality_score: 39.8
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 多元正态分布

## 概述

多元正态分布（Multivariate Normal Distribution），又称多维高斯分布，是单变量正态分布向多维空间的推广。若随机向量 $\mathbf{X} = (X_1, X_2, \ldots, X_k)^T$ 服从多元正态分布，记作 $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$，其中 $\boldsymbol{\mu}$ 是 $k$ 维均值向量，$\boldsymbol{\Sigma}$ 是 $k \times k$ 的协方差矩阵，且 $\boldsymbol{\Sigma}$ 必须是半正定的。

多元正态分布的系统研究可追溯至19世纪。弗朗西斯·高尔顿（Francis Galton）在研究父子身高遗传时于1888年引入了二元正态分布的概念，其学生卡尔·皮尔逊（Karl Pearson）进一步将其数学化。真正完整的多元正态理论在20世纪初随着矩阵代数的成熟而建立起来。

多元正态分布之所以在统计学、机器学习和信号处理中占据核心地位，根本原因在于其数学上的封闭性：多元正态分布的边缘分布、条件分布以及线性变换后的分布仍然是正态分布，这一性质使得高斯过程、卡尔曼滤波器、线性判别分析等方法都能以解析形式求解，而无需数值近似。

## 核心原理

### 概率密度函数

当 $\boldsymbol{\Sigma}$ 为正定矩阵（即满秩）时，$k$ 维随机向量 $\mathbf{X}$ 的概率密度函数为：

$$f(\mathbf{x}) = \frac{1}{(2\pi)^{k/2} |\boldsymbol{\Sigma}|^{1/2}} \exp\left(-\frac{1}{2}(\mathbf{x} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})\right)$$

其中 $|\boldsymbol{\Sigma}|$ 是协方差矩阵的行列式，$\boldsymbol{\Sigma}^{-1}$ 是其逆矩阵。指数项中的二次型 $(\mathbf{x} - \boldsymbol{\mu})^T \boldsymbol{\Sigma}^{-1} (\mathbf{x} - \boldsymbol{\mu})$ 被称为**马哈拉诺比斯距离（Mahalanobis Distance）**的平方，它度量了 $\mathbf{x}$ 到均值 $\boldsymbol{\mu}$ 的统计距离，并自动考虑了各变量的方差和相互相关性。马哈拉诺比斯距离等于常数的等高线在二维情形下是椭圆，其形状和方向完全由 $\boldsymbol{\Sigma}$ 决定。

### 协方差矩阵的几何意义

协方差矩阵 $\boldsymbol{\Sigma}$ 的特征分解 $\boldsymbol{\Sigma} = \mathbf{U} \boldsymbol{\Lambda} \mathbf{U}^T$ 揭示了概率密度等高线（椭球）的几何结构：特征向量矩阵 $\mathbf{U}$ 确定椭球的**方向**（主轴方向），特征值 $\lambda_i$ 确定椭球沿各主轴的**半轴长度**（等于 $\sqrt{\lambda_i}$）。当 $\boldsymbol{\Sigma}$ 为对角矩阵时，各分量相互独立，椭球主轴与坐标轴对齐；当 $\boldsymbol{\Sigma}$ 中存在非零非对角元素时，椭球旋转，反映变量间的线性相关性。

### 边缘分布与条件分布

将 $\mathbf{X}$ 分块为 $\mathbf{X} = (\mathbf{X}_1^T, \mathbf{X}_2^T)^T$，对应均值和协方差也分块：

$$\boldsymbol{\mu} = \begin{pmatrix} \boldsymbol{\mu}_1 \\ \boldsymbol{\mu}_2 \end{pmatrix}, \quad \boldsymbol{\Sigma} = \begin{pmatrix} \boldsymbol{\Sigma}_{11} & \boldsymbol{\Sigma}_{12} \\ \boldsymbol{\Sigma}_{21} & \boldsymbol{\Sigma}_{22} \end{pmatrix}$$

**边缘分布**直接从分块读取：$\mathbf{X}_1 \sim \mathcal{N}(\boldsymbol{\mu}_1, \boldsymbol{\Sigma}_{11})$，无需积分运算。

**条件分布** $\mathbf{X}_1 | \mathbf{X}_2 = \mathbf{x}_2$ 仍为多元正态分布，其均值和协方差分别为：

$$\boldsymbol{\mu}_{1|2} = \boldsymbol{\mu}_1 + \boldsymbol{\Sigma}_{12} \boldsymbol{\Sigma}_{22}^{-1} (\mathbf{x}_2 - \boldsymbol{\mu}_2)$$

$$\boldsymbol{\Sigma}_{1|2} = \boldsymbol{\Sigma}_{11} - \boldsymbol{\Sigma}_{12} \boldsymbol{\Sigma}_{22}^{-1} \boldsymbol{\Sigma}_{21}$$

注意条件协方差 $\boldsymbol{\Sigma}_{1|2}$ 不依赖于观测值 $\mathbf{x}_2$，只依赖于原始协方差结构，这是多元正态分布独有的性质。

### 线性变换的封闭性

若 $\mathbf{X} \sim \mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$，$\mathbf{A}$ 是 $m \times k$ 矩阵，$\mathbf{b}$ 是 $m$ 维向量，则：

$$\mathbf{A}\mathbf{X} + \mathbf{b} \sim \mathcal{N}(\mathbf{A}\boldsymbol{\mu} + \mathbf{b},\ \mathbf{A}\boldsymbol{\Sigma}\mathbf{A}^T)$$

特别地，取 $\mathbf{A} = \boldsymbol{\Sigma}^{-1/2}$（$\boldsymbol{\Sigma}$ 的平方根逆矩阵），$\mathbf{b} = -\boldsymbol{\Sigma}^{-1/2}\boldsymbol{\mu}$，可以将任何非奇异多元正态分布**标准化**为 $\mathcal{N}(\mathbf{0}, \mathbf{I})$，即各分量独立的标准正态分布，这一操作称为**白化变换（Whitening Transform）**。

## 实际应用

**卡尔曼滤波器中的状态估计**：在线性动态系统中，若初始状态和噪声均为多元正态分布，则任意时刻的状态后验分布仍为多元正态分布，卡尔曼增益矩阵 $\mathbf{K} = \boldsymbol{\Sigma}_{k|k-1}\mathbf{H}^T(\mathbf{H}\boldsymbol{\Sigma}_{k|k-1}\mathbf{H}^T + \mathbf{R})^{-1}$ 正是利用了条件分布公式推导出的最优线性更新规则，GPS导航和航天器轨道追踪均依赖此框架。

**高斯判别分析（Gaussian Discriminant Analysis）**：在二分类问题中，若假设每类的特征向量 $\mathbf{X}|y=c \sim \mathcal{N}(\boldsymbol{\mu}_c, \boldsymbol{\Sigma})$，且两类共享同一协方差矩阵，则贝叶斯最优决策边界退化为线性超平面（线性判别分析LDA）；若允许各类拥有不同协方差矩阵 $\boldsymbol{\Sigma}_c$，则决策边界为二次曲面（QDA）。

**多元正态分布的KL散度**：两个多元正态分布 $p = \mathcal{N}(\boldsymbol{\mu}_1, \boldsymbol{\Sigma}_1)$ 与 $q = \mathcal{N}(\boldsymbol{\mu}_2, \boldsymbol{\Sigma}_2)$ 之间的KL散度有解析表达式，在变分自编码器（VAE）的损失函数中，重参数化技巧结合此公式使得梯度可通过采样传播，是生成模型训练的关键步骤。

## 常见误区

**误区一：分量服从正态分布则联合分布必为多元正态**。这是严重的错误。两个边缘分布均为 $\mathcal{N}(0,1)$ 的随机变量，其联合分布完全可以不是二元正态。经典反例是令 $X \sim \mathcal{N}(0,1)$，$S$ 以概率 $1/2$ 取 $+1$ 或 $-1$，$Y = SX$，则 $Y \sim \mathcal{N}(0,1)$ 但 $(X, Y)$ 的联合分布不是二元正态——因为 $P(Y=X) + P(Y=-X) = 1$，样本只分布在两条直线上，而非填充二维平面。

**误区二：不相关等价于独立**。对于一般随机变量，不相关不代表独立。但对于多元正态分布，若 $\text{Cov}(X_i, X_j) = 0$，则 $X_i$ 与 $X_j$ 相互独立。这一等价性是多元正态分布的特殊性质，体现在协方
