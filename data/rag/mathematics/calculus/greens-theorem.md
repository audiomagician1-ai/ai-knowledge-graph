---
id: "greens-theorem"
concept: "格林公式"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 格林公式

## 概述

格林公式（Green's Theorem）建立了平面区域 $D$ 上的二重积分与其边界曲线 $L$ 上的第二类曲线积分之间的精确等价关系。设 $P(x,y)$ 和 $Q(x,y)$ 在闭区域 $D$ 上具有一阶连续偏导数，$L$ 为 $D$ 的正向边界（即沿边界行进时区域始终在左侧），则格林公式表述为：

$$\oint_L P\,dx + Q\,dy = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right) dA$$

这一公式由英国数学家乔治·格林（George Green）于1828年在其自费出版的论文《论数学分析在电磁理论中的应用》中首次提出，当时几乎无人关注，直到其去世后才经威廉·汤姆森（开尔文勋爵）推广而广为人知。

格林公式的重要性在于它将一维边界上的积分与二维区域内部的微分信息直接挂钩。在实际计算中，当曲线积分的被积函数复杂而对应的偏导差 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}$ 简单时，可将前者转化为更易计算的二重积分；反之亦然。

## 核心原理

### 正向边界的约定

格林公式要求边界曲线 $L$ 取**正向**（逆时针方向）。若区域 $D$ 含有"洞"（即多连通区域），则外边界取逆时针，内边界取顺时针，两者共同构成 $\partial D$ 的正向。若边界方向取反，公式右侧需乘以 $-1$。这一方向约定并非任意选择，而是源于外法向量与切向量的右手关系：站在边界上沿正向行进，区域 $D$ 始终在行进方向的左侧。

### 公式的证明思路

格林公式的标准证明将等式拆分为两个独立命题分别验证：

$$\oint_L P\,dx = -\iint_D \frac{\partial P}{\partial y}\,dA, \quad \oint_L Q\,dy = \iint_D \frac{\partial Q}{\partial x}\,dA$$

以 $X$-型区域（即可表示为 $a \le x \le b$，$\varphi_1(x) \le y \le \varphi_2(x)$）为例，对 $\iint_D \frac{\partial P}{\partial y}\,dA$ 先对 $y$ 积分，由牛顿-莱布尼茨公式得到上下边界处的函数值之差，再将这两段边界恰好识别为曲线积分 $\oint_L P\,dx$ 的组成部分，从而完成等式。$Y$-型区域的另一半证明完全类似。

### 旋度的平面形式

公式右端 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}$ 本质上是向量场 $\mathbf{F} = (P, Q, 0)$ 的旋度在 $z$ 轴方向的分量，即 $(\nabla \times \mathbf{F}) \cdot \hat{k}$。当这个量处处为零时，称向量场 $\mathbf{F}$ 在 $D$ 上**无旋**，此时对 $D$ 内任意闭合曲线 $\oint_L P\,dx + Q\,dy = 0$，且 $P\,dx + Q\,dy$ 为全微分，即存在势函数 $u$ 使得 $du = P\,dx + Q\,dy$。这一结论是判断曲线积分与路径无关性的核心判据。

### 利用格林公式计算面积

令 $P = -y$，$Q = x$，则 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} = 1 - (-1) = 2$，代入格林公式得：

$$S_D = \iint_D dA = \frac{1}{2}\oint_L x\,dy - y\,dx$$

这给出了用边界曲线的参数方程直接计算面积的公式。例如椭圆 $x = a\cos t$，$y = b\sin t$（$t \in [0, 2\pi]$），代入得 $S = \frac{1}{2}\int_0^{2\pi}(ab\cos^2 t + ab\sin^2 t)\,dt = \pi ab$，简洁地再现了椭圆面积公式。

## 实际应用

**化简闭合曲线积分**：计算 $\oint_L (x^2 - y)\,dx + (x + \sin^2 y)\,dy$，其中 $L$ 为任意包围原点的正向简单闭合曲线。计算偏导差：$\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} = 1 - (-1) = 2$。由格林公式，积分值等于 $2 \cdot S_D$，其中 $S_D$ 为 $L$ 围成的面积，从而无需参数化曲线便可给出答案。

**处理奇点（挖洞法）**：当被积函数在区域内某点不满足连续可微条件时，如 $P = \frac{-y}{x^2+y^2}$，$Q = \frac{x}{x^2+y^2}$ 在原点无定义，直接使用格林公式失效。此时以原点为圆心作半径为 $\varepsilon$ 的小圆 $l_\varepsilon$（取顺时针），对挖去小圆后的环形区域应用格林公式，由于该区域内 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} = 0$，故原曲线积分等于沿 $l_\varepsilon$ 的积分，后者可直接参数化计算得 $2\pi$，这正是绕原点一圈的结果，与路径形状无关。

## 常见误区

**误区一：忽视边界方向导致符号错误**。格林公式要求 $L$ 为正向（逆时针），若题目给出的曲线为顺时针，必须在公式结果前加负号。许多学生在多连通区域问题中遗漏内边界取顺时针这一规定，将内边界也取逆时针，导致结果差 $2 \times$（内边界积分值）。

**误区二：对含奇点区域直接套用公式**。格林公式的前提是 $P$、$Q$ 在闭区域 $D$（含边界）上有一阶连续偏导数。若 $D$ 内存在使 $P$ 或 $Q$ 无定义的点（如分母为零），不能直接将 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} = 0$ 的结论用于整个区域，必须先用挖洞法处理奇点。

**误区三：混淆"无旋"与"路径无关"的适用范围**。$\frac{\partial Q}{\partial x} = \frac{\partial P}{\partial y}$ 在单连通区域中可保证路径无关性，但在多连通区域（如去掉原点的平面）中不能得出同样结论。上述 $\frac{-y}{x^2+y^2}dx + \frac{x}{x^2+y^2}dy$ 在去掉原点后偏导相等，但绕原点一周积分为 $2\pi \ne 0$，恰好说明这一点。

## 知识关联

格林公式是第二类曲线积分理论的自然延伸：掌握曲线积分的参数化计算方法后，格林公式提供了一条"绕过参数化"的捷径，将边界积分转换为区域内部的二重积分。路径无关性与原函数（势函数）的存在性判断，正是格林公式在单连通区域上取 $\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} = 0$ 时的直接推论。

向上拓展至三维空间，格林公式对应的推广即为**斯托克斯定理**：$\oint_{\partial \Sigma} \mathbf{F} \cdot d\mathbf{r} = \iint_\Sigma (\nabla \times \mathbf{F}) \cdot d\mathbf{S}$。格林公式本质上是斯托克斯定理在平面（取 $\Sigma$ 为 $xy$ 平面上区域 $D$，法向量取 $\hat{k}$）的特殊情形。与此并列的**高斯散度定理**则将格林公式中"旋度"的角色换为"散度"，建立三维区域与封闭曲面之间的类比关系，三者共同构成微积分基本定理在多维空间中的完整图像。