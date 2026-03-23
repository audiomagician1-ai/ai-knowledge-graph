---
id: "orthogonal-matrices"
concept: "正交矩阵"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.4
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 正交矩阵

## 概述

正交矩阵是满足 $Q^T Q = Q Q^T = I$ 的实数方阵，其中 $I$ 为同阶单位矩阵，$Q^T$ 为 $Q$ 的转置。这个条件等价于说：$Q$ 的逆矩阵恰好等于它的转置，即 $Q^{-1} = Q^T$。从列向量角度看，$Q$ 的每一列构成 $\mathbb{R}^n$ 的一组标准正交基——列向量两两正交且模长均为 1。

正交矩阵的概念由19世纪数学家柯西（Cauchy）在研究二次型化简问题时系统引入。旋转矩阵是最直观的例子：二维平面中旋转角度 $\theta$ 的矩阵 $\begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$ 即为正交矩阵，其行列式为 $+1$。若行列式为 $-1$，则对应含反射的变换，如 Householder 反射矩阵。正交矩阵的行列式只能取 $+1$ 或 $-1$，这是由 $\det(Q^T Q) = \det(I) = 1$ 直接推出的。

正交矩阵的核心价值在于它保持向量的欧氏范数不变：$\|Qx\|_2 = \|x\|_2$。这一性质使得正交变换在数值计算中极为稳定——它不会放大舍入误差，是 QR 分解、奇异值分解等数值算法的基础构件。

## 核心原理

### 等价条件与行列式约束

设 $Q \in \mathbb{R}^{n \times n}$，以下四个条件相互等价：
1. $Q^T Q = I$
2. $Q Q^T = I$
3. $Q$ 的列向量构成 $\mathbb{R}^n$ 的标准正交基
4. $Q$ 的行向量构成 $\mathbb{R}^n$ 的标准正交基

条件 1 和条件 2 对方阵是等价的，但对非方矩阵则不然（非方矩阵只能满足其中一个，称为半正交矩阵）。由 $(\det Q)^2 = \det(Q^T)\det(Q) = \det(Q^T Q) = 1$，得 $\det Q = \pm 1$。行列式为 $+1$ 的正交矩阵构成特殊正交群 $SO(n)$，即纯旋转变换；行列式为 $-1$ 的包含奇数次反射。

### 范数保持性与几何意义

正交变换保持向量内积：$(Qu)^T(Qv) = u^T Q^T Q v = u^T v$。这意味着正交矩阵保持两向量间的夹角以及各向量的长度，是 $\mathbb{R}^n$ 中的等距变换。在三维图形学中，旋转矩阵 $R \in SO(3)$ 满足此性质，因此用于表示刚体旋转时不会产生拉伸或压缩。

Householder 矩阵是构造正交矩阵的重要工具：对单位向量 $v$，定义 $H = I - 2vv^T$，可验证 $H^T H = I$ 且 $\det H = -1$。QR 分解的标准数值算法正是通过连续左乘若干个 Householder 矩阵将 $A$ 化为上三角矩阵 $R$。

### QR 分解

任意实矩阵 $A \in \mathbb{R}^{m \times n}$（$m \geq n$）可分解为 $A = QR$，其中 $Q \in \mathbb{R}^{m \times m}$ 为正交矩阵，$R \in \mathbb{R}^{m \times n}$ 为上三角矩阵（下部为零块）。若 $A$ 列满秩，且规定 $R$ 的对角元均为正，则该分解唯一。

实现 QR 分解的三种主要方法：
- **Gram-Schmidt 正交化**：对 $A$ 的列向量依次正交化，数值稳定性较差，条件数会被放大至约 $\kappa(A)^2$。
- **Householder 变换**：用 $n$ 个（或 $n-1$ 个）Householder 矩阵连乘，数值稳定，运算量约为 $2mn^2 - \frac{2n^3}{3}$ 次浮点运算，是工业实现的首选。
- **Givens 旋转**：通过一系列平面旋转逐一消去元素，适合稀疏矩阵的 QR 分解，可选择性地只消零非零元素。

QR 分解在求解最小二乘问题 $\min_x \|Ax - b\|_2$ 时特别有用：将 $A = QR$ 代入后，利用正交矩阵保持范数的性质，问题化简为解上三角方程组 $R_1 x = Q_1^T b$，其中 $R_1$ 是 $R$ 的前 $n$ 行。

## 实际应用

**线性方程组求解**：LAPACK 库中的 `dgeqrf` 函数实现基于 Householder 的 QR 分解，用于求解满秩最小二乘问题，比直接用法方程 $A^T A x = A^T b$ 的数值条件好约一个数量级（条件数从 $\kappa(A)^2$ 降至 $\kappa(A)$）。

**特征值计算**：QR 算法（Francis 双步 QR 迭代，1961年）是计算一般矩阵全部特征值的标准算法。每一步对矩阵做正交相似变换 $A_{k+1} = Q_k^T A_k Q_k$，保持特征值不变，同时使矩阵逐渐收敛到拟上三角（Schur）形式。

**信号处理与通信**：正交频分复用（OFDM）中，离散傅里叶变换矩阵经归一化后为酉矩阵（复数域上的"正交矩阵"），满足 $U^* U = I$，保证了子载波间的正交性，消除载波间干扰。

**机器人学**：旋转矩阵 $R \in SO(3)$ 表示机器人关节的姿态。由于 $R^{-1} = R^T$，从世界坐标系变换到机器人本体坐标系只需转置操作，计算成本极低。

## 常见误区

**误区一：混淆正交矩阵与正交投影矩阵**。正交投影矩阵 $P$ 满足 $P^2 = P$（幂等性）且 $P^T = P$，例如 $P = Q(Q^T Q)^{-1}Q^T$。但正交投影矩阵通常不是正交矩阵——它将向量投影到子空间，必然缩短（或保持）向量长度，而不像正交矩阵那样保持长度。只有当投影到全空间（即 $P = I$）时，两者才重合。

**误区二：认为正交矩阵的特征值均为实数**。虽然正交矩阵的实特征值只能是 $\pm 1$，但正交矩阵可以有复数特征值。例如旋转矩阵 $\begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$（旋转 90°）的特征值为 $\pm i$，均为复数，模长为 1。正交矩阵特征值的模长必为 1，这一结论在复数域上才是完整的。

**误区三：QR 分解中 Q 列数等于 A 列数**。对 $m \times n$（$m > n$）矩阵 $A$，有"瘦 QR 分解"（thin QR）：$A = Q_1 R_1$，其中 $Q_1 \in \mathbb{R}^{m \times n}$ 只是半正交矩阵（$Q_1^T Q_1 = I_n$ 但 $Q_1 Q_1^T \neq I_m$），$R_1 \in \mathbb{R}^{n \times n}$ 为方上三角矩阵。这与完整 QR 分解（full QR，$Q$ 为 $m \times m$ 正交矩阵）是两种不同形式，使用时需要区分。

## 知识关联

**前置知识**：正交矩阵的定义直接依赖内积空间中的正交性概念——列向量正交性由 $\mathbb{R}^n$ 的标准内积 $\langle u, v \rangle = u^T v$ 定义，而单位化则来自范数 $\|v\| = \sqrt{\langle v, v \rangle}$。Gram-Schmidt 过程将内积空间中的正交化算法具体化为构造 $Q$ 的计算步骤。

**后续概念**：奇异值分解（SVD）将任意实矩阵 $A$ 分解为 $A = U \Sigma V^T$，其中 $U$ 和 $V$ 均为正交矩阵，$\Sigma$ 为对角奇异值矩阵。SVD 可视为 QR 分解的推广：QR 分解只用一个正交矩阵"从左边"消去 $A$，而 SVD 用两个正交矩阵从两侧同时作用，将 $A$ 化为最简对角形式，揭示了 $A$ 的完整几何结构（伸缩量和旋转方向）。
