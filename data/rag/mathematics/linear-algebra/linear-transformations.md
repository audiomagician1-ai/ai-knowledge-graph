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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 线性变换

## 概述

线性变换（Linear Transformation）是向量空间之间保持加法和标量乘法结构的映射。具体而言，从向量空间 $V$ 到向量空间 $W$ 的映射 $T: V \to W$ 称为线性变换，当且仅当对所有向量 $\mathbf{u}, \mathbf{v} \in V$ 和标量 $c$，满足两条公理：**可加性** $T(\mathbf{u} + \mathbf{v}) = T(\mathbf{u}) + T(\mathbf{v})$，以及**齐次性** $T(c\mathbf{v}) = cT(\mathbf{v})$。这两条合并即为：$T(c\mathbf{u} + d\mathbf{v}) = cT(\mathbf{u}) + dT(\mathbf{v})$，称为线性性条件。

线性变换的概念在19世纪随着矩阵代数的发展逐渐形成。凯莱（Arthur Cayley）在1858年的论文《矩阵论》中将矩阵乘法与线性变换的复合联系起来，奠定了用矩阵表示线性变换的基础。此后，皮亚诺（Giuseppe Peano）在1888年给出了向量空间的公理化定义，线性变换才有了严格的抽象框架。

线性变换之所以重要，在于它将几何直觉（旋转、缩放、投影、反射）与代数计算（矩阵乘法）统一起来。$\mathbb{R}^n$ 中任何线性变换均可由一个 $m \times n$ 矩阵完全确定，使得几何操作转化为数值计算。

## 核心原理

### 线性变换与矩阵的对应关系

设 $T: \mathbb{R}^n \to \mathbb{R}^m$ 是线性变换，$\mathbf{e}_1, \mathbf{e}_2, \ldots, \mathbf{e}_n$ 是 $\mathbb{R}^n$ 的标准基，则由线性性完全确定：

$$T(\mathbf{x}) = A\mathbf{x}, \quad A = [T(\mathbf{e}_1) \mid T(\mathbf{e}_2) \mid \cdots \mid T(\mathbf{e}_n)]$$

矩阵 $A$ 的第 $j$ 列恰好是 $T(\mathbf{e}_j)$ 的坐标向量。这意味着只需知道线性变换作用在基向量上的结果，即可完全重建整个变换。例如，将 $\mathbb{R}^2$ 中向量逆时针旋转 $\theta$ 角的旋转变换对应矩阵为：

$$R_\theta = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$$

当 $\theta = 90°$ 时，$R_{90°}$ 将 $\mathbf{e}_1 = (1,0)$ 映射到 $(0,1)$，将 $\mathbf{e}_2 = (0,1)$ 映射到 $(-1,0)$。

### 核（零空间）

线性变换 $T: V \to W$ 的**核**（Kernel，又称零空间 Null Space）定义为：

$$\ker(T) = \{\mathbf{v} \in V \mid T(\mathbf{v}) = \mathbf{0}\}$$

核是 $V$ 的子空间，其维数称为**零化度**（nullity）。核反映了变换"压缩"了哪些方向的信息——核非平凡（$\ker(T) \neq \{\mathbf{0}\}$）意味着 $T$ 不是单射，存在不同向量被映射到同一点。例如，投影变换 $T(x, y, z) = (x, y, 0)$ 的核是 $z$ 轴 $\{(0,0,z)\}$，维数为 1。

### 像（值域）

线性变换 $T$ 的**像**（Image，又称值域 Range）定义为：

$$\text{Im}(T) = \{T(\mathbf{v}) \mid \mathbf{v} \in V\} = \text{Span}\{T(\mathbf{e}_1), T(\mathbf{e}_2), \ldots, T(\mathbf{e}_n)\}$$

像是 $W$ 的子空间，其维数称为**秩**（rank）。像等于矩阵 $A$ 的列空间，因此计算像的维数等价于计算 $A$ 的列秩。

### 秩-零化度定理

秩与零化度满足经典的**秩-零化度定理**（Rank-Nullity Theorem）：

$$\text{rank}(T) + \text{nullity}(T) = \dim(V)$$

例如，若 $T: \mathbb{R}^5 \to \mathbb{R}^3$ 的秩为 2，则零化度必为 3，核是 $\mathbb{R}^5$ 中的一个三维子空间。该定理直接给出了判断 $T$ 是单射（$\text{nullity} = 0$）或满射（$\text{rank} = \dim(W)$）的充要条件。

## 实际应用

**计算机图形学中的坐标变换**：三维图形的旋转、缩放与错切均是线性变换，可用 $3 \times 3$ 矩阵表示并通过矩阵复合实现连续变换。但平移不是线性变换（因为 $T(\mathbf{0}) \neq \mathbf{0}$），因此实际使用 $4 \times 4$ 齐次坐标矩阵，将平移纳入仿射变换框架。

**主成分分析（PCA）**：PCA 的核心步骤是求数据协方差矩阵对应的线性变换的像空间。选取使方差最大的方向（即像空间中的主轴）进行降维，本质是将高维数据投影到秩为 $k$ 的像上，其中 $k$ 远小于原维数。

**微分方程中的线性算子**：微分算子 $D: f \mapsto f'$ 作用在多项式空间 $P_n$ 上是线性变换，其核恰好是常数函数构成的一维空间 $\{c \mid c \in \mathbb{R}\}$，其秩为 $n$，满足秩-零化度定理：$n + 1 = n + 1$。

## 常见误区

**误区一：认为线性变换必须保持原点不动**。这其实是线性变换的必然结论而非额外条件——令 $c = 0$，由齐次性得 $T(\mathbf{0}) = T(0 \cdot \mathbf{v}) = 0 \cdot T(\mathbf{v}) = \mathbf{0}$。因此 $f(x) = 2x + 1$ 这类仿射函数**不是**线性变换，因为 $f(0) = 1 \neq 0$。初学者常混淆"线性函数"（代数课）与"线性变换"（线性代数）的概念。

**误区二：混淆核和像的维数方向**。核是定义域 $V$ 的子空间，像是陪域 $W$ 的子空间。若 $T: \mathbb{R}^4 \to \mathbb{R}^6$ 的矩阵秩为 3，则核维数为 $4 - 3 = 1$（在 $\mathbb{R}^4$ 中），像维数为 3（在 $\mathbb{R}^6$ 中），不能混为一谈。秩-零化度定理约束的是 $\text{rank} + \text{nullity} = \dim(\text{定义域})$，而不涉及陪域维数。

**误区三：认为矩阵相同则线性变换相同**。线性变换依赖于基的选取。同一个线性变换在不同基下的矩阵表示不同，两个矩阵 $A$ 和 $B$ 表示同一变换当且仅当它们相似，即存在可逆矩阵 $P$ 使得 $B = P^{-1}AP$。这正是相似变换的本质含义。

## 知识关联

**依赖前置概念**：矩阵乘法使线性变换的复合具体化——若 $T_1$ 对应矩阵 $A$，$T_2$ 对应矩阵 $B$，则复合变换 $T_2 \circ T_1$ 对应矩阵 $BA$，乘法顺序反映复合顺序。向量空间的子空间结构保证了核和像作为子空间的合法性。

**延伸至特征值与特征向量**：特征向量正是线性变换作用后方向不变（仅长度缩放）的特殊向量：$T(\mathbf{v}) = \lambda\mathbf{v}$。理解线性变换如何"拉伸"不同方向是理解特征分解的几何基础。特征值为零等价于特征向量在 $\ker(T)$ 中，将核的概念与特征分析直接相连。不可对角化的线性变换（如约当形式）体现了当特征向量不足以张成整个空间时，变换的几何结构更为复杂。