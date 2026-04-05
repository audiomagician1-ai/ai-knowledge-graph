---
id: "product-sum-formulas"
concept: "积化和差公式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 积化和差公式

## 概述

积化和差公式是三角学中将两个三角函数之**乘积**转化为三角函数**和或差**的一组恒等式。其核心价值在于降低三角表达式的次数——乘积形式在积分、化简中往往难以处理，而和差形式可以直接利用基本积分公式或逐项求值。历史上，这组公式在对数发明之前（16世纪）曾被天文学家用于简化乘法运算，称为"积化和差法"（prosthaphaeresis），是当时替代繁琐手算乘法的实用工具。

积化和差共有四条公式，分别处理 sin·cos、cos·cos、sin·sin 三种乘积类型（sin·cos 因两个角的顺序会产生两条）。这四条公式均由和差角公式相加或相减直接推导而来，因此与和差化积公式构成互逆关系：积化和差将"积"变"和差"，和差化积将"和差"变"积"。

## 核心原理

### 四条公式的完整形式

设 A、B 为任意角，积化和差的四条公式如下：

$$\sin A \cdot \cos B = \frac{1}{2}[\sin(A+B) + \sin(A-B)]$$

$$\cos A \cdot \sin B = \frac{1}{2}[\sin(A+B) - \sin(A-B)]$$

$$\cos A \cdot \cos B = \frac{1}{2}[\cos(A+B) + \cos(A-B)]$$

$$\sin A \cdot \sin B = -\frac{1}{2}[\cos(A+B) - \cos(A-B)]$$

注意第四条公式前有**负号**，这是 sin·sin 公式与 cos·cos 公式的最本质区别，也是最常出错之处。

### 从和差角公式推导

以 $\sin A \cdot \cos B$ 为例，展示推导路径：

写出两个已知公式：
$$\sin(A+B) = \sin A \cos B + \cos A \sin B$$
$$\sin(A-B) = \sin A \cos B - \cos A \sin B$$

两式相加，$\cos A \sin B$ 项消去：
$$\sin(A+B) + \sin(A-B) = 2\sin A \cos B$$

两边除以 2，得到第一条积化和差公式。cos·cos 公式由两个余弦和差式相加得到；sin·sin 公式由两个余弦和差式相减得到，相减后出现负号，这正是结果带负号的来源。记住**"cos 相加，sin 相减，sin·sin 带负号"**这一推导规律，无需死记硬背。

### 特殊情形：A = B 时退化为二倍角公式

当 A = B 时，积化和差公式退化为：

$$\sin A \cdot \cos A = \frac{1}{2}\sin 2A$$

$$\cos^2 A = \frac{1}{2}[1 + \cos 2A]$$

$$\sin^2 A = \frac{1}{2}[1 - \cos 2A]$$

这三个降幂公式正是二倍角公式的直接推论，体现积化和差公式在**降幂**方面的核心功能——将平方项转为一次余弦项，这在定积分计算中极为常用，例如计算 $\int_0^\pi \sin^2 x \, dx$ 时必须先用此降幂。

## 实际应用

### 计算具体乘积值

计算 $\sin 75° \cdot \cos 15°$：

$$\sin 75° \cdot \cos 15° = \frac{1}{2}[\sin(75°+15°) + \sin(75°-15°)]$$
$$= \frac{1}{2}[\sin 90° + \sin 60°] = \frac{1}{2}\left[1 + \frac{\sqrt{3}}{2}\right] = \frac{2+\sqrt{3}}{4}$$

若直接用 $\sin 75°$ 和 $\cos 15°$ 的展开式相乘，步骤远比上述繁琐，积化和差将计算量减少约一半。

### 三角函数乘积的积分

在高等数学中，计算 $\int \sin 3x \cos 5x \, dx$ 时，直接对乘积积分无标准公式可用，必须先积化和差：

$$\sin 3x \cos 5x = \frac{1}{2}[\sin 8x + \sin(-2x)] = \frac{1}{2}[\sin 8x - \sin 2x]$$

然后逐项积分：

$$\int \sin 3x \cos 5x \, dx = \frac{1}{2}\left(-\frac{\cos 8x}{8} + \frac{\cos 2x}{2}\right) + C$$

这是积化和差公式在大学数学中最高频的应用场景。

### 化简连乘表达式

计算乘积 $\prod_{k=1}^{n-1} \sin\frac{k\pi}{n}$ 等数论中的三角乘积时，也需要反复使用积化和差拆解相邻项。例如可以证明 $\prod_{k=1}^{n-1} \sin\frac{k\pi}{n} = \frac{n}{2^{n-1}}$，此结果的推导路径中积化和差是关键步骤之一。

## 常见误区

**误区一：忽略 sin·sin 公式的负号**

公式 $\sin A \sin B = -\frac{1}{2}[\cos(A+B) - \cos(A-B)]$ 中的负号极易遗漏。记忆方法是：由 $\cos(A+B)$ 和 $\cos(A-B)$ 相减推出，相减结果为 $2\sin A \sin B$ 前有负号，因此整理后公式带负号。如写成 $+\frac{1}{2}[\cos(A+B)-\cos(A-B)]$，计算结果方向相反，是典型错误。

**误区二：混淆积化和差与和差化积的适用方向**

积化和差的输入是**乘积**（如 $\sin A \cos B$），输出是**和差**。而和差化积的输入是**和差**（如 $\sin A + \sin B$），输出是**乘积**。两组公式变换方向相反，不可混用。当题目出现两个三角函数相乘时，才考虑积化和差；出现相加减时，才考虑和差化积。

**误区三：认为积化和差使表达式更"复杂"**

初学者有时觉得一项乘积变成两项之和是"复杂化"，因而回避使用。但在积分语境中，两个一次三角函数之和比一个乘积形式处理容易得多；在化简含有特殊角的乘积时，积化和差通常使后续步骤大幅缩短。判断使用时机的标准是：后续操作（积分、求值、化简）是否对**和差形式**更友好。

## 知识关联

积化和差公式的直接先决知识是**和差角公式**（$\sin(A\pm B)$ 及 $\cos(A\pm B)$），因为四条积化和差公式完全由和差角公式的线性组合推导，若和差角公式不熟练，推导过程容易出错。同时需要掌握**二倍角公式**，因为 A=B 的特殊情形与二倍角公式高度重叠，区分各公式的适用形式是后续正确选择公式的基础。

与**和差化积公式**的关系是互逆的代数操作：令和差化积中的 $\alpha = A+B$、$\beta = A-B$，则 $A = \frac{\alpha+\beta}{2}$、$B = \frac{\alpha-\beta}{2}$，代入积化和差公式即可推回和差化积公式，两组公式本质上是同一组恒等式的两种书写角度。在高等数学的**傅里叶分析**中，积化和差是证明三角函数系正交性的核心工具——计算 $\int_{-\pi}^{\pi} \sin mx \cos nx \, dx = 0$ 时，必须先用积化和差将被积函数拆开，才能逐项积分得零。