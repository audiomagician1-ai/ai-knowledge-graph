---
id: "sum-difference-formulas"
concept: "和差化积公式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-03-27
---


# 和差化积公式

## 概述

和差化积公式是三角学中将两个角的三角函数之**和或差**转化为**积**的形式的一组恒等式。具体而言，它把形如 $\sin A + \sin B$、$\sin A - \sin B$、$\cos A + \cos B$、$\cos A - \cos B$ 的表达式，改写为含有两角之和与两角之差的乘积形式。与之对应的"积化和差"方向相反，两者互为逆运算。

这组公式最早可以追溯到16世纪欧洲天文学的计算需求。当时天文学家用"积化和差"方法简化乘法运算（称为Prosthaphaeresis），而和差化积则是在整理三角恒等式体系时作为其逆形式被系统归纳。18世纪随着欧拉对三角函数的代数化整理，这四个公式才以现代形式固定下来。

和差化积公式在化简含和差结构的三角表达式、求解三角方程、以及信号处理中的频率叠加分析中具有不可替代的作用。例如，方程 $\sin 3x + \sin x = 0$ 若不借助和差化积，直接求解极为繁琐；使用公式后可立即转化为乘积形式，从而分步求解。

---

## 核心原理

### 四个基本公式

和差化积公式共有四个标准形式，设 $A$、$B$ 为任意实数：

$$\sin A + \sin B = 2\sin\frac{A+B}{2}\cos\frac{A-B}{2}$$

$$\sin A - \sin B = 2\cos\frac{A+B}{2}\sin\frac{A-B}{2}$$

$$\cos A + \cos B = 2\cos\frac{A+B}{2}\cos\frac{A-B}{2}$$

$$\cos A - \cos B = -2\sin\frac{A+B}{2}\sin\frac{A-B}{2}$$

其中每个公式右侧均含有 $\dfrac{A+B}{2}$（两角之和的一半）与 $\dfrac{A-B}{2}$（两角之差的一半）这两个关键角。**余弦和差公式右侧的负号**是最容易出错的细节。

### 推导路径：从积化和差逆推

四个公式均可由积化和差公式逆向得到。以正弦和为例：

由积化和差知：
$$\sin\alpha\cos\beta = \frac{1}{2}[\sin(\alpha+\beta)+\sin(\alpha-\beta)]$$

令 $\alpha = \dfrac{A+B}{2}$，$\beta = \dfrac{A-B}{2}$，则 $\alpha+\beta = A$，$\alpha-\beta = B$，代入右侧即得：

$$2\sin\frac{A+B}{2}\cos\frac{A-B}{2} = \sin A + \sin B$$

整个推导过程的关键在于**换元**：用两个新变量替换原来的 $A$、$B$，再利用已知的积化和差等式反向读出结论。其余三个公式的推导思路完全相同，分别对应不同的积化和差基础公式。

### 结构特征与记忆规律

四个公式呈现两条对称规律：
1. **正弦参与和差时**，乘积中一个因子含 $\sin$，另一个含 $\cos$；
2. **余弦参与和差时**，乘积中两个因子同号（均为 $\cos$ 或均为 $\sin$），但余弦之差额外带负号。

具体记忆口诀："正和正余积，正差余正积，余和两余积，余差负两正"（此处"正"指正弦，"余"指余弦）。

---

## 实际应用

### 求解三角方程

方程 $\cos 5x + \cos 3x = 0$，使用公式 $\cos A + \cos B = 2\cos\dfrac{A+B}{2}\cos\dfrac{A-B}{2}$，令 $A=5x$，$B=3x$，得：

$$2\cos 4x \cos x = 0$$

于是 $\cos 4x = 0$ 或 $\cos x = 0$，分别给出 $x = \dfrac{(2k+1)\pi}{8}$ 或 $x = \dfrac{(2k+1)\pi}{2}$（$k\in\mathbb{Z}$）。若不拆分为乘积，直接展开则需要四倍角展开，计算量大得多。

### 化简含和差的三角表达式

化简 $\dfrac{\sin 75° - \sin 15°}{\cos 75° + \cos 15°}$：

分子：$\sin 75° - \sin 15° = 2\cos 45°\sin 30° = 2\cdot\dfrac{\sqrt{2}}{2}\cdot\dfrac{1}{2} = \dfrac{\sqrt{2}}{2}$

分母：$\cos 75° + \cos 15° = 2\cos 45°\cos 30° = 2\cdot\dfrac{\sqrt{2}}{2}\cdot\dfrac{\sqrt{3}}{2} = \dfrac{\sqrt{6}}{2}$

结果：$\dfrac{\sqrt{2}/2}{\sqrt{6}/2} = \dfrac{\sqrt{2}}{\sqrt{6}} = \dfrac{\sqrt{3}}{3}$

### 物理中的拍频现象

两列频率分别为 $f_1$ 和 $f_2$ 的声波叠加时，合振动可写作 $\sin(2\pi f_1 t) + \sin(2\pi f_2 t)$，利用和差化积：

$$2\sin\left(\pi(f_1+f_2)t\right)\cos\left(\pi(f_1-f_2)t\right)$$

其中 $\cos(\pi(f_1-f_2)t)$ 描述的正是频率为 $|f_1-f_2|$ 的**拍**，这是拍频现象的数学根源。

---

## 常见误区

### 误区一：混淆角的系数

将 $\sin A + \sin B$ 中的 $\dfrac{A+B}{2}$ 写成 $A+B$，或将系数 2 遗漏。正确公式右侧前置系数**必须为 2**，且两个角均为原来两角的**半和**与**半差**，而非和与差本身。

### 误区二：余弦之差忘记负号

$\cos A - \cos B$ 的结果是 $-2\sin\dfrac{A+B}{2}\sin\dfrac{A-B}{2}$，负号容易被遗漏。直觉上认为"差对差"结果应为正，但由积化和差逆推可清楚看到负号的来源：$\cos(\alpha-\beta) - \cos(\alpha+\beta) = 2\sin\alpha\sin\beta$，右侧正好是余弦**大减小**的形式，当 $A < B$ 时自然为负。

### 误区三：把和差化积与辅助角公式混用

$a\sin\theta + b\cos\theta = \sqrt{a^2+b^2}\sin(\theta+\varphi)$ 是辅助角公式，处理的是**同角**正余弦的线性组合；而和差化积处理的是**不同角**的同名三角函数相加减。两者形式相近但适用对象根本不同，不可互换。

---

## 知识关联

**前置依赖**：和差化积公式的推导以**积化和差公式**为直接基础，而积化和差本身来源于正弦、余弦的**和差角公式**（$\sin(A\pm B)$ 与 $\cos(A\pm B)$）。若和差角公式尚不熟练，换元推导步骤将难以理解。

**后续延伸**：掌握和差化积后，**倍角公式**可视为其特殊情形——令 $A = B$ 代入 $\sin A + \sin B$，右侧 $2\sin A\cos 0 = 2\sin A$ 退化为恒等式；而令 $B = 0$ 代入 $\cos A + \cos B$ 则得 $1 + \cos A = 2\cos^2\dfrac{A}{2}$，这正是**半角公式**的标准形式。因此，和差化积是连接积化和差与倍角/半角体系的枢纽性工具，四类公式构成一个可以相互推导的闭合网络。