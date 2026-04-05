---
id: "dot-product"
concept: "内积(点乘)"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 5
is_milestone: false
tags: ["核心"]

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

# 内积（点乘）

## 概述

内积（又称点积或数量积）是定义在两个向量之间、返回一个标量的二元运算。对于 $\mathbb{R}^n$ 中的两个列向量 $\mathbf{a} = (a_1, a_2, \ldots, a_n)$ 和 $\mathbf{b} = (b_1, b_2, \ldots, b_n)$，其内积定义为对应分量之积的求和：$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i$。这个运算的结果是一个实数（或复数），而非新的向量，这一点与向量叉积有根本区别。

内积的几何解释最早由19世纪数学家赫尔曼·格拉斯曼（Hermann Grassmann）在1844年的《线性扩张论》中系统化，随后威廉·汉密顿爵士在四元数框架下进一步发展了相关理论。点积名称来源于书写符号"·"，而"内积"这一更通用的名称则源于函数空间理论，强调该运算可推广至无穷维空间中的函数之间。

理解内积的意义在于：它是连接向量代数运算与几何度量（长度、角度）的唯一桥梁。向量的模长、两向量夹角、正交性判断，全部依赖内积来定量刻画。没有内积，线性代数就失去了几何直觉，仅剩抽象的线性映射。

## 核心原理

### 代数定义与计算

在 $\mathbb{R}^n$ 中，内积的代数表达式为：

$$\mathbf{a} \cdot \mathbf{b} = a_1 b_1 + a_2 b_2 + \cdots + a_n b_n$$

用矩阵记号可以写成 $\mathbf{a}^T \mathbf{b}$，即将行向量乘以列向量。例如，$\mathbf{a} = (1, 3, -2)$，$\mathbf{b} = (4, -1, 2)$，则 $\mathbf{a} \cdot \mathbf{b} = 1 \times 4 + 3 \times (-1) + (-2) \times 2 = 4 - 3 - 4 = -3$。内积满足交换律（$\mathbf{a} \cdot \mathbf{b} = \mathbf{b} \cdot \mathbf{a}$）、对第一个向量的线性（$(\alpha\mathbf{a}+\beta\mathbf{c}) \cdot \mathbf{b} = \alpha(\mathbf{a} \cdot \mathbf{b}) + \beta(\mathbf{c} \cdot \mathbf{b})$）、正定性（$\mathbf{a} \cdot \mathbf{a} \geq 0$，等号成立当且仅当 $\mathbf{a} = \mathbf{0}$）。这三条性质是将内积推广为抽象内积空间的公理基础。

### 几何解释：夹角公式

内积的几何版本由余弦定理直接导出：

$$\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$$

其中 $\theta \in [0°, 180°]$ 是两向量之间的夹角，$|\mathbf{a}| = \sqrt{\mathbf{a} \cdot \mathbf{a}}$ 为向量模长。由此可得夹角计算公式：

$$\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$$

当 $\mathbf{a} \cdot \mathbf{b} > 0$ 时，$\theta < 90°$（锐角）；$\mathbf{a} \cdot \mathbf{b} = 0$ 时，$\theta = 90°$（正交）；$\mathbf{a} \cdot \mathbf{b} < 0$ 时，$\theta > 90°$（钝角）。正交性判断只需验证内积是否为零，无需计算实际角度，这在 $n$ 维空间中尤为高效。

### 向量投影

$\mathbf{a}$ 在 $\mathbf{b}$ 方向上的标量投影（scalar projection）定义为：

$$\text{proj}_{\mathbf{b}} a = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|}$$

对应的向量投影（vector projection）为：

$$\text{proj}_{\mathbf{b}} \mathbf{a} = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|^2}\mathbf{b} = \frac{\mathbf{a} \cdot \mathbf{b}}{\mathbf{b} \cdot \mathbf{b}}\mathbf{b}$$

投影公式是正交分解的核心：任意向量 $\mathbf{a}$ 可分解为平行于 $\mathbf{b}$ 的分量 $\text{proj}_{\mathbf{b}}\mathbf{a}$ 与垂直于 $\mathbf{b}$ 的余量 $\mathbf{a} - \text{proj}_{\mathbf{b}}\mathbf{a}$，且这两部分内积为零。Gram-Schmidt 正交化过程的每一步正是重复应用此投影-减法操作，将任意基向量逐一正交化。

### 柯西-施瓦茨不等式

内积满足最重要的不等式之一：

$$|\mathbf{a} \cdot \mathbf{b}| \leq |\mathbf{a}||\mathbf{b}|}$$

等号成立当且仅当 $\mathbf{a}$ 与 $\mathbf{b}$ 线性相关（即平行）。这一不等式直接保证了 $\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$ 的值域落在 $[-1, 1]$ 之间，从而夹角定义是自洽的。

## 实际应用

**机器学习中的余弦相似度**：在文本分类和推荐系统中，两个文档或用户向量的相似度用 $\text{cos\_sim}(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$ 衡量，直接利用内积的夹角公式。值域为 $[-1, 1]$，接近 1 表示高度相似，接近 0 表示无关。

**物理学做功计算**：力 $\mathbf{F}$ 沿位移 $\mathbf{d}$ 所做的功 $W = \mathbf{F} \cdot \mathbf{d} = |\mathbf{F}||\mathbf{d}|\cos\theta$，只有力在位移方向上的分量才对做功有贡献，这正是内积的几何投影含义的直接物理体现。

**神经网络的线性层**：全连接层的计算本质是对每个神经元计算权重向量与输入向量的内积再加偏置：$z = \mathbf{w} \cdot \mathbf{x} + b$。GPU 之所以擅长神经网络推断，正是因为其并行计算大量内积（矩阵乘法）的硬件架构。

**信号处理中的相关性**：两个离散信号序列 $\{a_i\}$ 和 $\{b_i\}$ 的互相关系数通过内积计算，用于检测信号中是否含有特定模式，例如雷达信号的匹配滤波。

## 常见误区

**误区一：内积结果是向量**。初学者常将内积与向量叉积混淆。$\mathbf{a} \cdot \mathbf{b}$ 的结果是一个标量（实数），不是向量。叉积 $\mathbf{a} \times \mathbf{b}$ 才返回向量，且叉积仅定义在 $\mathbb{R}^3$（及 $\mathbb{R}^7$）中，而内积可定义在任意维度。

**误区二：内积为零意味着向量之一为零向量**。$\mathbf{a} \cdot \mathbf{b} = 0$ 只表示两向量正交（夹角为90°），两者均可以是非零向量。例如 $(1, 0)$ 和 $(0, 1)$ 内积为零但均不是零向量。将"内积为零"等同于"向量为零"是混淆了标量乘法与内积的错误。

**误区三：内积的正定性在复数域同样简单成立**。在 $\mathbb{C}^n$ 中，直接使用 $\sum a_i b_i$ 不满足正定性——$(i, 0) \cdot (i, 0) = i^2 = -1 < 0$。复数内积必须定义为 $\langle \mathbf{a}, \mathbf{b} \rangle = \sum \bar{a}_i b_i$（取第一个向量的共轭），才能保证 $\langle \mathbf{a}, \mathbf{a} \rangle = \sum |a_i|^2 \geq 0$。

## 知识关联

**前置知识**：向量的分量表示和向量加法是计算内积的直接前提。理解向量作为有序数组以及坐标运算，才能将内积公式 $\sum a_i b_i$ 付诸计算。向量模长 $|\mathbf{a}| = \sqrt{\sum a_i^2}$ 本身就是 $\mathbf{a}$ 与自身的内积开根号。

**后续概念**