---
id: "linear-transformations"
concept: "线性变换"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 34.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 线性变换

## 概述

线性变换（Linear Transformation）是从一个向量空间 $V$ 到另一个向量空间 $W$ 的映射 $T: V \to W$，满足两条严格的代数约束：加法保持性 $T(\mathbf{u} + \mathbf{v}) = T(\mathbf{u}) + T(\mathbf{v})$，以及标量乘法保持性 $T(c\mathbf{v}) = cT(\mathbf{v})$。这两条性质可合并为一个判据：对任意向量 $\mathbf{u}, \mathbf{v}$ 和标量 $a, b$，有 $T(a\mathbf{u} + b\mathbf{v}) = aT(\mathbf{u}) + bT(\mathbf{v})$。这意味着线性变换在结构层面"尊重"向量空间的运算，不会把直线变成曲线，也不会把原点移走（$T(\mathbf{0}) = \mathbf{0}$ 是线性变换的必然推论）。

线性变换的思想可追溯至 18 世纪欧拉和拉格朗日对坐标变换的研究，但系统性的抽象框架由 19 世纪的格拉斯曼（Hermann Grassmann）和凯莱（Arthur Cayley）建立。凯莱在 1858 年的论文中首次用矩阵乘法统一描述了有限维向量空间上的线性变换，奠定了矩阵作为线性变换"计算代理"的地位。

线性变换之所以重要，在于几乎所有物理中的叠加原理、信号处理中的傅里叶分析、机器学习中的神经网络层，都建立在线性变换的可叠加、可分解性质之上。理解线性变换的结构（特别是其核与像），直接揭示了方程组 $A\mathbf{x} = \mathbf{b}$ 解的存在性与唯一性。

## 核心原理

### 线性变换与矩阵的对应关系

在有限维向量空间中，$T: \mathbb{R}^n \to \mathbb{R}^m$ 的线性变换与 $m \times n$ 矩阵之间存在一一对应。具体地，若选定 $\mathbb{R}^n$ 的标准基 $\{\mathbf{e}_1, \ldots, \mathbf{e}_n\}$，则矩阵 $A$ 的第 $j$ 列恰好等于 $T(\mathbf{e}_j)$。这意味着只要知道线性变换作用在每个基向量上的结果，就能完全确定该变换对整个空间中任意向量的作用。例如，平面旋转角 $\theta$ 的线性变换对应矩阵为
$$A = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$$
其列向量 $(\cos\theta, \sin\theta)^T$ 和 $(-\sin\theta, \cos\theta)^T$ 正是 $\mathbf{e}_1, \mathbf{e}_2$ 旋转后的像。

### 核（Kernel）：零化空间

线性变换 $T: V \to W$ 的**核**定义为被映射到零向量的所有向量构成的集合：
$$\ker(T) = \{\mathbf{v} \in V \mid T(\mathbf{v}) = \mathbf{0}\}$$
核是 $V$ 的子空间，其维数称为 $T$ 的**零化度**（nullity）。核的大小直接反映了变换"压缩"信息的程度：若 $\ker(T) = \{\mathbf{0}\}$（即零化度为 0），则 $T$ 是单射；若核包含非零向量，则存在不同的向量被映射到同一点，方程 $T(\mathbf{x}) = \mathbf{b}$ 若有解则解不唯一。对矩阵 $A$ 而言，$\ker(T_A)$ 就是齐次方程组 $A\mathbf{x} = \mathbf{0}$ 的解空间（零空间）。

### 像（Image）：值域结构

线性变换的**像**（image，也称值域）是所有输出向量的集合：
$$\text{im}(T) = \{T(\mathbf{v}) \mid \mathbf{v} \in V\}$$
像是 $W$ 的子空间，其维数称为 $T$ 的**秩**（rank）。对矩阵 $A$ 而言，$\text{im}(T_A)$ 恰好是 $A$ 的列空间——即 $A$ 各列向量的线性组合所张成的空间。方程 $A\mathbf{x} = \mathbf{b}$ 有解当且仅当 $\mathbf{b} \in \text{im}(T_A)$。

### 秩—零化度定理

对于线性变换 $T: V \to W$，若 $V$ 是有限维空间（维数为 $n$），则有著名的**秩—零化度定理**（Rank-Nullity Theorem）：
$$\dim(\ker(T)) + \dim(\text{im}(T)) = \dim(V) = n$$
即：零化度 + 秩 = 定义域维数。这一定理精确量化了"信息压缩"与"信息保留"之间的守恒关系。例如，一个 $3 \times 5$ 矩阵代表的线性变换 $T: \mathbb{R}^5 \to \mathbb{R}^3$，其秩最大为 3（受制于值域维数），因此零化度至少为 $5 - 3 = 2$，意味着核至少是二维的，方程组必定有无穷多解。

## 实际应用

**计算机图形学中的几何变换**：3D 图形渲染中，缩放、旋转、剪切均是线性变换。将多个变换复合时，只需将对应矩阵相乘（顺序不可交换），即 $(T_2 \circ T_1)$ 对应矩阵乘积 $A_2 A_1$。平移不是线性变换（因为它将原点移动），这也是图形学必须引入 $4 \times 4$ 齐次坐标矩阵的直接原因。

**主成分分析（PCA）中的降维**：PCA 的本质是寻找一个线性变换 $T: \mathbb{R}^n \to \mathbb{R}^k$（$k < n$），使得投影后数据的方差最大。这个变换的矩阵由协方差矩阵的前 $k$ 个特征向量组成，核的维数为 $n - k$，记录了被"丢弃"的信息方向数量。

**线性常微分方程中的微分算子**：微分算子 $D: C^1(\mathbb{R}) \to C^0(\mathbb{R})$，$D(f) = f'$，是一个线性变换（因为 $(af + bg)' = af' + bg'$）。其核为所有常数函数构成的空间（$\ker(D) = \{f \mid f' = 0\}$，维数为 1），这正是"不定积分有任意常数 $C$"的代数解释。

## 常见误区

**误区一：认为所有保原点的映射都是线性变换**。函数 $f(x) = x^2$ 满足 $f(0) = 0$，但 $f(2 \cdot 1) = 4 \neq 2f(1) = 2$，不是线性变换。判断线性性必须同时验证加法和数乘两条性质，而非仅凭"过原点"或"看起来像直线"来判断。常见的陷阱还包括绝对值函数 $|x|$（满足 $|cx| = |c||x| \neq c|x|$ 当 $c < 0$ 时）。

**误区二：混淆核为零与行列式为零的含义**。很多学生认为"矩阵行列式非零 ↔ 核只含零向量"仅适用于方阵。实际上，秩—零化度定理告诉我们，对于 $m \times n$ 矩阵（$m \neq n$），即使每列线性无关（零化度为 0），行列式也没有定义；而一个 $3 \times 5$ 矩阵的线性变换**永远不可能**是单射，因为其零化度至少为 2，这与行列式无关。

**误区三：认为线性变换的像就是整个值域空间**。$T: \mathbb{R}^3 \to \mathbb{R}^3$ 的像可能只是 $\mathbb{R}^3$ 中的一个平面（当秩为 2 时），甚至是一条直线（秩为 1）。秩是刻画像的维数的精确量，而不是"有多少输出分量"。

## 知识关联

**前置概念**：矩阵乘法提供了线性变换的计算工具——两个线性变换的复合 $T_2 \circ T_1$ 精确对应矩阵乘积 $A_2 A_1$，这使得"复合变换"的计算转化为矩阵运算。向量空间提供了核与像作为子空间的合法性保障——若没有向量空间的封闭性定义，"核是子空间"这一结论无从建立。

**后续概念**：特征值与特征向量研究线性变换的不变方向——满足 $T(\mathbf{v}) = \lambda\mathbf{v}$ 的非零向量 $\mathbf{v}$ 在变换下仅发生伸缩而不改变方向。特征分析本质上是寻找线性变换在某种意义下"最简单"的表示形式（对角化），它直接依
