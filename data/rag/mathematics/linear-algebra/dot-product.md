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
quality_tier: "pending-rescore"
quality_score: 35.5
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 内积（点乘）

## 概述

内积（Inner Product），又称点积（Dot Product）或数量积，是定义在两个向量之间、返回一个标量的二元运算。对于 $n$ 维实向量 $\mathbf{a} = (a_1, a_2, \ldots, a_n)$ 和 $\mathbf{b} = (b_1, b_2, \ldots, b_n)$，其内积定义为各对应分量乘积之和：

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{n} a_i b_i = a_1 b_1 + a_2 b_2 + \cdots + a_n b_n$$

这一运算最早在19世纪由物理学家和数学家赫尔曼·格拉斯曼（Hermann Grassmann）系统化整理，随后威廉·金顿·克利福德（William Kingdon Clifford）在1878年将其与外积并列，建立了现代向量代数的框架。内积之所以重要，在于它将几何概念（角度、长度、正交性）与代数计算（分量运算）直接联系起来，成为线性代数、信号处理、机器学习等领域最基础的计算工具。

## 核心原理

### 代数定义与几何意义的等价性

内积的代数公式与几何公式是等价的，连接二者的是余弦定理：

$$\mathbf{a} \cdot \mathbf{b} = |\mathbf{a}| \, |\mathbf{b}| \cos\theta$$

其中 $|\mathbf{a}|$ 和 $|\mathbf{b}|$ 分别是两个向量的模长，$\theta$ 是它们之间的夹角（$0 \leq \theta \leq \pi$）。由此可以直接计算两向量夹角：

$$\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{a}| \, |\mathbf{b}|}$$

例如 $\mathbf{a} = (3, 4)$，$\mathbf{b} = (4, 3)$，则 $\mathbf{a} \cdot \mathbf{b} = 12 + 12 = 24$，$|\mathbf{a}| = |\mathbf{b}| = 5$，所以 $\cos\theta = 24/25$，夹角约为 $16.26°$。当内积为零时，$\cos\theta = 0$，即 $\theta = 90°$，两向量正交——这是判断正交性的核心判据。

### 向量在另一向量上的投影

内积直接给出了向量投影的长度。$\mathbf{a}$ 在 $\mathbf{b}$ 方向上的标量投影为：

$$\text{proj}_{\mathbf{b}} |\mathbf{a}| = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|}$$

而 $\mathbf{a}$ 在 $\mathbf{b}$ 方向上的向量投影为：

$$\text{proj}_{\mathbf{b}} \mathbf{a} = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{b}|^2} \mathbf{b} = \frac{\mathbf{a} \cdot \mathbf{b}}{\mathbf{b} \cdot \mathbf{b}} \mathbf{b}$$

注意分母 $\mathbf{b} \cdot \mathbf{b} = |\mathbf{b}|^2$，本身也是内积。投影公式在 Gram-Schmidt 正交化过程中反复使用——每一步都通过内积计算投影分量，再减去该分量以获得垂直部分。

### 内积的四条基本性质

实数域上，内积满足以下四条性质，缺一不可：

1. **交换律**：$\mathbf{a} \cdot \mathbf{b} = \mathbf{b} \cdot \mathbf{a}$
2. **线性性（对第一个参数）**：$(\alpha\mathbf{a} + \beta\mathbf{b}) \cdot \mathbf{c} = \alpha(\mathbf{a} \cdot \mathbf{c}) + \beta(\mathbf{b} \cdot \mathbf{c})$，$\alpha, \beta \in \mathbb{R}$
3. **正定性**：$\mathbf{a} \cdot \mathbf{a} \geq 0$，且等号当且仅当 $\mathbf{a} = \mathbf{0}$ 时成立
4. **诱导范数**：$|\mathbf{a}| = \sqrt{\mathbf{a} \cdot \mathbf{a}}$，即内积的正定性诱导出向量的欧几里得模长

正是这四条性质，使得内积可以被推广到更抽象的函数空间（如 $L^2$ 空间），其中两个函数 $f, g$ 的内积定义为 $\langle f, g \rangle = \int_a^b f(x)g(x)\,dx$。

### 矩阵形式与高维计算

将列向量 $\mathbf{a}$ 和 $\mathbf{b}$ 用矩阵乘法表示，内积等价于：

$$\mathbf{a} \cdot \mathbf{b} = \mathbf{a}^T \mathbf{b}$$

这一转换使得内积计算可以利用高效的矩阵乘法实现，在处理 1000 维、10000 维的向量（如 NLP 中的词向量）时，GPU 并行加速的矩阵乘法比逐元素求和快数个数量级。

## 实际应用

**余弦相似度（文本检索）**：两文档向量 $\mathbf{a}, \mathbf{b}$ 的相似度定义为 $\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{|\mathbf{a}||\mathbf{b}|}$，取值范围 $[-1, 1]$。搜索引擎通过将查询词和文档均转化为 TF-IDF 向量，用内积除以两模长，快速排序最相关结果。

**物理做功**：力 $\mathbf{F}$ 沿位移 $\mathbf{d}$ 方向的做功 $W = \mathbf{F} \cdot \mathbf{d} = Fd\cos\theta$。当力与位移垂直（$\theta = 90°$）时，内积为零，做功为零，这正是为何匀速圆周运动中向心力不做功。

**神经网络前向传播**：全连接层的核心计算是 $z = \mathbf{w} \cdot \mathbf{x} + b$，其中 $\mathbf{w}$ 是权重向量，$\mathbf{x}$ 是输入向量，$b$ 是偏置标量。内积计算占据了深度学习模型推理 80% 以上的计算量。

**信号处理中的相关性检测**：两信号序列 $x[n]$ 和 $y[n]$ 在特定延迟下的互相关等于将它们视为向量后计算内积，内积最大值对应的延迟即为信号的最佳对齐点。

## 常见误区

**误区一：混淆内积（标量）与外积（向量）**。内积 $\mathbf{a} \cdot \mathbf{b}$ 结果是一个**标量**，而外积 $\mathbf{a} \times \mathbf{b}$ 结果是一个**向量**，二者完全不同。特别是，外积只在三维空间有直接的向量形式，且 $\mathbf{a} \times \mathbf{b} = -\mathbf{b} \times \mathbf{a}$（反交换），而内积满足 $\mathbf{a} \cdot \mathbf{b} = \mathbf{b} \cdot \mathbf{a}$（交换律）。

**误区二：认为内积为零仅意味着一个向量是零向量**。$\mathbf{a} \cdot \mathbf{b} = 0$ 有三种可能：$\mathbf{a} = \mathbf{0}$、$\mathbf{b} = \mathbf{0}$，或**两向量正交**（$\theta = 90°$）。在实际计算中，两个非零向量内积为零是极有意义的情况，例如三维空间中 $(1, 0, 0) \cdot (0, 1, 0) = 0$，正是标准基向量正交性的体现。

**误区三：将复数域内积与实数域内积混用**。复向量的内积定义为 $\langle \mathbf{a}, \mathbf{b} \rangle = \sum_i \overline{a_i} b_i$（需对第一个参数取共轭），而非直接相乘求和。若不取共轭，则 $\langle \mathbf{a}, \mathbf{a} \rangle$ 可能不是实数，无法保证正定性。例如 $\mathbf{a} = (1, i)$ 时，若不取共轭则 $1\cdot1 + i\cdot i = 1 - 1 = 0$，错误地得到非零向量的"模长"为零。

## 知识关联

**前置知识**：向量基础（向量的分量表示、模长计算、向量加减法）是计算内积的前提。没有分量坐标的概念，就无法套用求和公式；没有模长定义，就无法理解内积与角度的几何等价关系。

**直接延伸**：内积的四条公理（正定性、对称性、双线性）被抽象提炼后，定义了**内积空间**（Inner Product Space），即配备了内积结构的向量空间。$\mathbb{R}^n$ 上的标准内积只是
