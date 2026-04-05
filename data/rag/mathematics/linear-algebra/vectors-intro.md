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

# 向量基础

## 概述

向量（Vector）是同时具有**大小**和**方向**的量，区别于只有大小的标量（如温度25°C、质量3kg）。在数学中，一个 $n$ 维向量表示为有序数组 $\mathbf{v} = (v_1, v_2, \ldots, v_n)$，其中每个 $v_i \in \mathbb{R}$。向量最早由19世纪爱尔兰数学家威廉·哈密顿（William Hamilton）和德国数学家赫尔曼·格拉斯曼（Hermann Grassmann）分别在四元数与外代数研究中系统化，现代向量符号体系在1880年代由约西亚·吉布斯（Josiah Gibbs）整理成形。

向量的重要性在于它提供了描述**空间关系**的精确语言。物理中的速度、力、电场强度都是向量量；在机器学习中，一张28×28像素的图像被表示为784维向量，文字被表示为词嵌入向量（如Word2Vec中的300维向量）。没有向量语言，就无法精确表达"以每秒5米的速度向东北方向运动"这类信息。

向量基础是线性代数的出发点，因为线性代数研究的核心对象——线性变换——就是将一个向量空间映射到另一个向量空间的函数。掌握向量的表示、加法和数乘，意味着掌握了构造整个线性代数体系的砖块。

---

## 核心原理

### 向量的表示方式

向量有多种等价表示形式。**列向量**是最常用的标准形式：
$$\mathbf{v} = \begin{pmatrix} v_1 \\ v_2 \\ v_3 \end{pmatrix}$$
**行向量**则写作 $\mathbf{v}^T = (v_1,\ v_2,\ v_3)$，其中上标 $T$ 表示转置。在几何上，二维向量 $(3, 4)$ 对应从原点出发、向右3单位、向上4单位的有向线段，其**模长**（欧几里得范数）为：
$$\|\mathbf{v}\| = \sqrt{v_1^2 + v_2^2 + \cdots + v_n^2}$$
对于向量 $(3, 4)$，模长为 $\sqrt{9 + 16} = 5$。单位向量满足 $\|\hat{v}\| = 1$，通过 $\hat{v} = \mathbf{v} / \|\mathbf{v}\|$ 获得，表示只保留方向信息、舍弃大小信息的向量。

### 向量加法

两个**同维**向量的加法定义为**对应分量相加**：若 $\mathbf{u} = (u_1, u_2, u_3)$，$\mathbf{v} = (v_1, v_2, v_3)$，则：
$$\mathbf{u} + \mathbf{v} = (u_1 + v_1,\ u_2 + v_2,\ u_3 + v_3)$$
例如，$(1, 2, 3) + (4, -1, 0) = (5, 1, 3)$。几何上，向量加法遵循**平行四边形法则**：将 $\mathbf{u}$ 的终点与 $\mathbf{v}$ 的起点相接，合向量就是从 $\mathbf{u}$ 的起点到 $\mathbf{v}$ 的终点的有向线段（首尾相接法）。

向量加法满足以下4条代数性质（$\mathbf{0}$ 为零向量，$-\mathbf{v}$ 为 $\mathbf{v}$ 的逆向量）：
- **交换律**：$\mathbf{u} + \mathbf{v} = \mathbf{v} + \mathbf{u}$
- **结合律**：$(\mathbf{u} + \mathbf{v}) + \mathbf{w} = \mathbf{u} + (\mathbf{v} + \mathbf{w})$
- **零元素**：$\mathbf{v} + \mathbf{0} = \mathbf{v}$
- **逆元素**：$\mathbf{v} + (-\mathbf{v}) = \mathbf{0}$

注意：**不同维度**的向量相加没有定义，$(1,2)+(1,2,3)$ 是非法操作。

### 数乘（标量乘法）

数乘是将一个标量 $\lambda \in \mathbb{R}$ 与向量 $\mathbf{v}$ 相乘的运算：
$$\lambda \mathbf{v} = (\lambda v_1,\ \lambda v_2,\ \ldots,\ \lambda v_n)$$
例如，$3 \cdot (2, -1, 4) = (6, -3, 12)$。几何意义是：$|\lambda| > 1$ 时向量被**拉伸**，$0 < |\lambda| < 1$ 时被**压缩**，$\lambda < 0$ 时方向**反转**，$\lambda = 0$ 时变为零向量。

数乘满足以下分配律，连接了加法与乘法两种运算：
$$\lambda(\mathbf{u} + \mathbf{v}) = \lambda\mathbf{u} + \lambda\mathbf{v}$$
$$(\lambda + \mu)\mathbf{v} = \lambda\mathbf{v} + \mu\mathbf{v}$$

加法和数乘合在一起构成的代数结构被称为**向量空间**（Vector Space），它需要满足8条公理，向量加法的4条与数乘的4条——这8条公理精确刻画了"类向量"行为的本质。

---

## 实际应用

**物理中的力的合成**：一个物体同时受到力 $\mathbf{F}_1 = (3, 0)\ \text{N}$ 和 $\mathbf{F}_2 = (0, 4)\ \text{N}$，合力为 $\mathbf{F}_1 + \mathbf{F}_2 = (3, 4)\ \text{N}$，大小为5N，方向为与水平方向成 $\arctan(4/3) \approx 53.1°$ 角。这直接对应牛顿第二定律中力的叠加原理。

**计算机图形学中的位移**：三维游戏引擎中，角色当前位置为向量 $\mathbf{p} = (10, 0, 5)$，移动速度为 $\mathbf{v} = (2, 0, -1)$（单位：米/帧），经过3帧后位置为 $\mathbf{p} + 3\mathbf{v} = (10, 0, 5) + (6, 0, -3) = (16, 0, 2)$，这里用到了数乘和向量加法的组合。

**自然语言处理中的词向量运算**：Word2Vec模型中，"国王"、"男人"、"女人"、"女王"均被表示为300维向量。著名的实验结果是：$\text{vec}(\text{国王}) - \text{vec}(\text{男人}) + \text{vec}(\text{女人}) \approx \text{vec}(\text{女王})$，这表明语义关系可以用向量加法和数乘来捕捉。

---

## 常见误区

**误区1：向量等同于坐标点**。许多初学者把向量 $(3, 4)$ 和平面上的点 $(3, 4)$ 混为一谈。点是空间中的位置，本身没有方向；向量是有方向的位移量，$(3, 4)$ 的标准含义是"从任意起点出发，向右3、向上4"的位移。点 $A(1,1)$ 到点 $B(4,5)$ 定义了向量 $\overrightarrow{AB} = (3, 4)$，两者概念不同。

**误区2：向量加法可以跨维度进行**。有学生会尝试将二维向量 $(1, 2)$ 与三维向量 $(1, 2, 3)$ 相加，认为结果是 $(2, 4, 3)$。这是错误的——向量加法仅对**同维**向量有定义，不同维度的向量属于不同的向量空间，强行相加在数学上无意义，就如同试图把苹果的个数加到速度上。

**误区3：数乘改变向量的"本质"**。部分学习者认为 $-1 \cdot \mathbf{v}$ 是一个与 $\mathbf{v}$ 完全不同的向量。实际上 $-\mathbf{v}$ 与 $\mathbf{v}$ 共线，模长相同，只是方向相反。对于任意非零实数 $\lambda$，$\lambda\mathbf{v}$ 与 $\mathbf{v}$ 总在同一条直线上（称为共线），这是数乘运算"只改变大小/方向，不改变所在直线"的核心性质，后续线性相关性分析依赖这一点。

---

## 知识关联

**与前置知识的联系**：向量的分量 $v_i$ 取值于实数集 $\mathbb{R}$，理解**数集分类**（实数、复数等）能帮助区分实向量空间 $\mathbb{R}^n$ 与复向量空间 $\mathbb{C}^n$。而**梯度与方向导数**本身就是向量概念的应用——函数 $f(x,y)$ 的梯度 $\nabla f = (\partial f/\partial x,\ \partial f/\partial y)$ 正是一个二维向量，方向导数 $D_{\mathbf{u}}f = \nabla f \cdot \hat{u}$ 需要用到向量的模长和方向概念。

**与后续知识的衔接**：本