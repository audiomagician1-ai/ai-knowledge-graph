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
quality_tier: "B"
quality_score: 47.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 和差化积公式

## 概述

和差化积公式是三角学中将两个三角函数之**和**或**差**转化为**乘积**形式的一组恒等式，具体包括正弦和差、余弦和差共四个公式。这组公式与"积化和差"互为逆运算，在化简含有不同角度的三角表达式时不可替代。

这组公式的历史可追溯至17世纪，欧洲数学家在研究对数运算时，为了将乘法转化为加法（方便笔算），率先推导出积化和差公式；其逆过程——和差化积——随即也被系统整理。在中国高中数学课程中，和差化积公式被列为必考内容，是从基础三角恒等式通向倍角公式、辅助角公式等高级工具的重要桥梁。

和差化积公式之所以重要，在于它能将**同名函数不同角度的加减**统一化为含有和角与差角的乘积，从而暴露出可约分的公因子或特殊值，使求值、化简和方程求解变得高效。例如，求解 $\sin 75° + \sin 15°$ 的精确值，直接计算繁琐，而利用和差化积一步即得 $\sqrt{6}/2$。

---

## 核心原理

### 四个基本公式

设 $A$、$B$ 为任意实数角，和差化积的四个公式如下：

$$\sin A + \sin B = 2\sin\frac{A+B}{2}\cos\frac{A-B}{2}$$

$$\sin A - \sin B = 2\cos\frac{A+B}{2}\sin\frac{A-B}{2}$$

$$\cos A + \cos B = 2\cos\frac{A+B}{2}\cos\frac{A-B}{2}$$

$$\cos A - \cos B = -2\sin\frac{A+B}{2}\sin\frac{A-B}{2}$$

其中每个公式右侧均为两个三角函数的**乘积**，括号内的角分别为原两角的**半和**与**半差**。

### 推导过程（以正弦之和为例）

利用正弦加法定理：

$$\sin(\alpha+\beta) = \sin\alpha\cos\beta + \cos\alpha\sin\beta$$
$$\sin(\alpha-\beta) = \sin\alpha\cos\beta - \cos\alpha\sin\beta$$

令 $\alpha = \dfrac{A+B}{2}$，$\beta = \dfrac{A-B}{2}$，则 $\alpha+\beta = A$，$\alpha-\beta = B$。

将两式相加：

$$\sin A + \sin B = 2\sin\frac{A+B}{2}\cos\frac{A-B}{2}$$

这说明和差化积公式**完全由正弦/余弦加减法定理导出**，换元是关键步骤——引入半和角与半差角是本质操作。

### 符号规律与记忆要点

四个公式中存在三条关键规律：

1. **同名变乘积**：$\sin+\sin$ 变为 $\sin\cos$，$\cos+\cos$ 变为 $\cos\cos$，$\cos-\cos$ 变为 $\sin\sin$。
2. **负号位置**：只有 $\cos A - \cos B$ 前出现负号 $-2$，其余三个公式系数均为正 $+2$；这一负号源于正弦加法定理相减时余弦项相消、正弦项叠加的代数结构。
3. **半和在前，半差在后**：$\dfrac{A+B}{2}$ 永远对应第一个函数，$\dfrac{A-B}{2}$ 对应第二个函数；两者顺序颠倒将产生符号错误。

---

## 实际应用

### 例1：精确值计算

求 $\cos 75° - \cos 15°$ 的值。

利用 $\cos A - \cos B = -2\sin\dfrac{A+B}{2}\sin\dfrac{A-B}{2}$：

$$\cos 75° - \cos 15° = -2\sin 45°\sin 30° = -2 \cdot \frac{\sqrt{2}}{2} \cdot \frac{1}{2} = -\frac{\sqrt{2}}{2}$$

### 例2：化简与因式分解

证明：$\dfrac{\sin 3x + \sin x}{\cos 3x + \cos x} = \tan 2x$

分子：$\sin 3x + \sin x = 2\sin 2x \cos x$

分母：$\cos 3x + \cos x = 2\cos 2x \cos x$

两式相除，$2\cos x$ 约去：$\dfrac{2\sin 2x \cos x}{2\cos 2x \cos x} = \dfrac{\sin 2x}{\cos 2x} = \tan 2x$，得证。

### 例3：三角方程求解

解方程 $\sin 3x + \sin x = 0$（$x \in [0, 2\pi]$）。

化积：$2\sin 2x \cos x = 0$，得 $\sin 2x = 0$ 或 $\cos x = 0$。

$\sin 2x = 0 \Rightarrow x = 0, \dfrac{\pi}{2}, \pi, \dfrac{3\pi}{2}, 2\pi$；$\cos x = 0 \Rightarrow x = \dfrac{\pi}{2}, \dfrac{3\pi}{2}$。

合并得 $x \in \left\{0, \dfrac{\pi}{2}, \pi, \dfrac{3\pi}{2}, 2\pi\right\}$，共5个解。

---

## 常见误区

**误区一：混淆半和与半差的对应函数**

$\sin A + \sin B$ 结果是 $\sin\cdot\cos$，其中 $\sin$ 对应半和角，$\cos$ 对应半差角。学生常误写成 $2\cos\dfrac{A+B}{2}\sin\dfrac{A-B}{2}$（此式实为 $\sin A - \sin B$ 的展开），导致符号或公式整体出错。建议死记：**正弦之和，先正弦后余弦**。

**误区二：忘记 $\cos A - \cos B$ 前的负号**

四个公式中只有余弦差有前置负号，学生做题时最容易在此处丢分。负号的来源是：余弦加法中两式相减时，$\cos\alpha\cos\beta$ 项被消去，留下的 $\sin\alpha\sin\beta$ 项系数为 $-2$。若记不住规律，可临时推导验证：令 $A = \pi, B = 0$，则 $\cos\pi - \cos 0 = -1 - 1 = -2$，而 $-2\sin\dfrac{\pi}{2}\sin\dfrac{\pi}{2} = -2 \cdot 1 \cdot 1 = -2$，与左侧吻合。

**误区三：将和差化积用于异名函数**

和差化积仅适用于**同名函数**（同为正弦或同为余弦）。对于 $\sin A + \cos B$ 这类异名混合式，不能直接套用上述公式，必须先通过余角关系 $\cos B = \sin(90°-B)$ 等方法统一函数名称后再化积。

---

## 知识关联

**前置知识**：和差化积的推导完全依赖**正弦与余弦的加减法定理**（即 $\sin(A\pm B)$、$\cos(A\pm B)$ 展开式），掌握这两对公式是理解换元推导过程的前提。

**后续应用**：和差化积是推导**倍角公式**的重要途径之一——令 $A = B$，则 $\sin A + \sin A = 2\sin A\cos 0 = 2\sin A$（退化），但更重要的是反向视角：积化和差与和差化积合称一对逆变换，在推导**辅助角公式** $a\sin x + b\cos x = \sqrt{a^2+b^2}\sin(x+\varphi)$ 的过程中，和差化积作为中间工具被频繁使用。此外，在高等数学的**傅里叶级数**展开中，和差化积帮助正交化三角函数系，是其底层代数工具之一。