---
id: "vectors-intro"
concept: "向量基础"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 4
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 32.7
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.344
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 向量基础

## 概述

向量（Vector）是同时具有**大小**和**方向**的数学对象，与只有大小的标量（Scalar）形成对比。在欧几里得空间中，一个 $n$ 维向量被记为有序数组 $\mathbf{v} = (v_1, v_2, \ldots, v_n)$，其中每个分量 $v_i \in \mathbb{R}$。这种表示方式将几何直觉（箭头）与代数结构（数组）统一起来，是19世纪数学家威廉·哈密顿（William Hamilton）和赫尔曼·格拉斯曼（Hermann Grassmann）分别在四元数理论与《广义论》（1844年）中奠定的基础。

向量概念的重要性在于它提供了一种语言，可以同时描述物理量（力、速度、电场强度）和抽象结构（函数空间中的函数、矩阵的列）。特别地，$n$ 维实向量空间 $\mathbb{R}^n$ 中的向量运算——加法与数乘——满足8条公理，这8条公理定义了抽象的**线性空间（向量空间）**，使得同一套运算规则可以适用于完全不同的数学对象。

与梯度密切相关：梯度 $\nabla f$ 本身就是一个向量，其方向指向函数增长最快的方向，其每个分量是对应变量的偏导数。理解向量的坐标分量结构，是理解梯度"方向"属性的前提。

---

## 核心原理

### 向量的表示与范数

在 $\mathbb{R}^n$ 中，向量 $\mathbf{v} = (v_1, v_2, \ldots, v_n)$ 可以理解为从原点出发、指向坐标 $(v_1, v_2, \ldots, v_n)$ 的有向线段。向量的**欧氏范数（长度/模）**定义为：

$$\|\mathbf{v}\| = \sqrt{v_1^2 + v_2^2 + \cdots + v_n^2}$$

当 $\|\mathbf{v}\| = 1$ 时，称 $\mathbf{v}$ 为**单位向量**。任意非零向量都可以通过除以其范数得到单位向量：$\hat{\mathbf{v}} = \dfrac{\mathbf{v}}{\|\mathbf{v}\|}$，这一过程称为**归一化（Normalization）**。

**零向量** $\mathbf{0} = (0, 0, \ldots, 0)$ 是特殊的向量：它的大小为0，方向未定义，但它在向量加法中充当单位元，是向量空间公理中必须存在的元素。

### 向量加法

两个同维向量的加法定义为**对应分量相加**：

$$\mathbf{u} + \mathbf{v} = (u_1 + v_1,\ u_2 + v_2,\ \ldots,\ u_n + v_n)$$

几何上，这对应**平行四边形法则**：以 $\mathbf{u}$ 和 $\mathbf{v}$ 为两邻边构成平行四边形，对角线即为 $\mathbf{u} + \mathbf{v}$。等价地，也可以用**三角形法则**：将 $\mathbf{v}$ 的起点平移至 $\mathbf{u}$ 的终点，从 $\mathbf{u}$ 的起点到 $\mathbf{v}$ 的终点的有向线段即是和向量。

向量加法满足**交换律** $\mathbf{u} + \mathbf{v} = \mathbf{v} + \mathbf{u}$ 和**结合律** $(\mathbf{u} + \mathbf{v}) + \mathbf{w} = \mathbf{u} + (\mathbf{v} + \mathbf{w})$。向量 $\mathbf{v}$ 的**加法逆元**为 $-\mathbf{v} = (-v_1, -v_2, \ldots, -v_n)$，方向相反、大小相同。

### 数乘（标量乘法）

向量 $\mathbf{v}$ 与标量 $\lambda \in \mathbb{R}$ 的数乘定义为：

$$\lambda \mathbf{v} = (\lambda v_1,\ \lambda v_2,\ \ldots,\ \lambda v_n)$$

几何效果是对向量进行**拉伸或压缩**：若 $|\lambda| > 1$ 则放大，$0 < |\lambda| < 1$ 则缩小，$\lambda < 0$ 则方向反转。当 $\lambda = -1$ 时，$(-1)\mathbf{v} = -\mathbf{v}$，即得到加法逆元。

数乘满足两条分配律：
- 对向量加法分配：$\lambda(\mathbf{u} + \mathbf{v}) = \lambda\mathbf{u} + \lambda\mathbf{v}$
- 对标量加法分配：$(\lambda + \mu)\mathbf{v} = \lambda\mathbf{v} + \mu\mathbf{v}$

以及结合律 $\lambda(\mu \mathbf{v}) = (\lambda\mu)\mathbf{v}$ 和单位元性质 $1 \cdot \mathbf{v} = \mathbf{v}$。上述8条性质（4条加法公理 + 4条数乘公理）合在一起，正是**线性空间的定义公理**。

---

## 实际应用

**物理中的力的合成**：在二维平面内，一个物体受到两个力 $\mathbf{F}_1 = (3, 4)$ N 和 $\mathbf{F}_2 = (-1, 2)$ N，合力为 $\mathbf{F}_1 + \mathbf{F}_2 = (2, 6)$ N，其大小为 $\sqrt{4 + 36} = \sqrt{40} \approx 6.32$ N。这一计算直接依赖向量加法的分量规则。

**计算机图形学中的颜色混合与变换**：RGB颜色空间中，一个像素颜色被表示为三维向量 $(r, g, b)$，其中每个分量取值 $[0, 255]$。对图像进行亮度调整，就是对每个像素的颜色向量乘以标量 $\lambda$（亮度系数），这是数乘的直接应用。

**机器学习中的词向量（Word Embedding）**：著名的 Word2Vec 模型（2013年，Google）将每个词映射为一个高维实数向量（通常为100至300维）。其中最著名的结论是：$\text{vec}(\text{"king"}) - \text{vec}(\text{"man"}) + \text{vec}(\text{"woman"}) \approx \text{vec}(\text{"queen"})$，这一语义关系完全依靠向量加法和数乘来表达，说明向量运算在高维抽象空间中依然保持其结构意义。

---

## 常见误区

**误区1：混淆"向量相等"与"向量同位"**

许多初学者认为两个向量只有在起点相同时才能相等。事实上，自由向量的相等只需判断**大小相同且方向相同**，起点位置无关紧要。例如，平行四边形中对边对应的向量互相相等（共有4对）。只有在解析几何中将向量固定为以原点为起点的**位置向量**时，才有起点的约定。

**误区2：认为数乘只能改变大小**

当标量 $\lambda < 0$ 时，数乘 $\lambda\mathbf{v}$ 不仅改变大小还会**翻转方向**（旋转180°）。例如 $(-2)(1, 3) = (-2, -6)$，其方向与 $(1, 3)$ 完全相反。这与"缩放"的直觉不同——负标量带来方向的反转，这在力学中对应反向力，在信号处理中对应相位反转。

**误区3：向量范数的三角不等式被忽视**

初学者容易以为 $\|\mathbf{u} + \mathbf{v}\| = \|\mathbf{u}\| + \|\mathbf{v}\|$ 恒成立，但正确结论是**三角不等式**：$\|\mathbf{u} + \mathbf{v}\| \leq \|\mathbf{u}\| + \|\mathbf{v}\|$，等号成立的条件是 $\mathbf{u}$ 与 $\mathbf{v}$ 同向（即 $\mathbf{v} = \lambda\mathbf{u}$，$\lambda \geq 0$）。这一不等式的几何含义是：三角形两边之和大于第三边。

---

## 知识关联

**与前置概念的衔接**：向量的每个分量 $v_i$ 都属于实数集 $\mathbb{R}$，因此数集分类中对实数域的理解是向量分量合法性的基础。此外，梯度 $\nabla f = \left(\frac{\partial f}{\partial x_1}, \ldots, \frac{\partial f}{\partial x_n}\right)$ 是一个 $n$ 维向量，其分量加法和数乘规则完全符合本文所定义的向量运算——方向导数公式 $D_{\mathbf{u}}f = \nabla f \cdot \mathbf{u}$ 中的 $\mathbf{u}$ 必须是单位向量，体现了归一化的必要性。

**通向内积（点乘）**：向量加法和数乘只描述了向量空间的线性结构，尚不能度量两个向量之间的**角度**。引入内积 $\mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^n u_i v_
