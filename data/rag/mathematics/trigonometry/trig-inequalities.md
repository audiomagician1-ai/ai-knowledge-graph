---
id: "trig-inequalities"
concept: "三角不等式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 三角不等式

## 概述

三角不等式是指含有三角函数（正弦、余弦、正切等）的不等式，求解目标是找出使不等式成立的角度范围或实数集合。与三角方程求特定解不同，三角不等式的解通常是一段连续的区间，需要综合运用三角函数的单调性、周期性与有界性才能求解。

三角不等式的系统研究伴随着三角函数分析化的历史发展。18世纪欧拉将三角函数定义为实数到实数的映射后，不等式的区间解法才得以规范化表达。在高中数学及大学竞赛中，三角不等式是考察学生将函数图像、单调区间与不等号方向结合运用的重要题型。

三角不等式的重要性体现在其解集结构上：由于三角函数的周期性，解集通常包含无穷多个区间段，需用通解的形式表达，例如 $k\pi + \alpha \leq x \leq k\pi + \beta$（$k \in \mathbb{Z}$）。这与代数不等式解集仅为有限区间的情形有本质区别。

---

## 核心原理

### 基于单调区间的求解框架

求解三角不等式的基本思路：先将不等式转化为 $\sin x > a$、$\cos x < a$ 或 $\tan x \geq a$ 等标准形式，再利用函数在特定区间上的单调性确定解集。

以 $\sin x > \frac{1}{2}$ 为例，在 $[-\frac{\pi}{2}, \frac{\pi}{2}]$ 上正弦函数单调递增，方程 $\sin x = \frac{1}{2}$ 的解为 $x = \frac{\pi}{6}$；在 $[0, \pi]$ 的另一侧，对称解为 $x = \frac{5\pi}{6}$。故在 $[0, 2\pi]$ 内，$\sin x > \frac{1}{2}$ 的解为 $\frac{\pi}{6} < x < \frac{5\pi}{6}$，加上周期性得通解：

$$\frac{\pi}{6} + 2k\pi < x < \frac{5\pi}{6} + 2k\pi, \quad k \in \mathbb{Z}$$

### 余弦不等式的解集对称性

余弦函数关于 $x = 0$（以及 $x = 2k\pi$）对称，因此 $\cos x \leq a$（$-1 \leq a \leq 1$）的解集在 $[0, 2\pi]$ 内呈现关于 $\pi$ 对称的形态。设 $\cos\alpha = a$（$0 \leq \alpha \leq \pi$），则：

$$\cos x \leq a \iff \alpha \leq x \leq 2\pi - \alpha \pmod{2\pi}$$

通解为：$2k\pi + \alpha \leq x \leq 2k\pi + (2\pi - \alpha)$，即 $2k\pi + \alpha \leq x \leq (2k+2)\pi - \alpha$，$k \in \mathbb{Z}$。

注意正弦不等式的解集在一个周期内是**单连通区间**，而余弦不等式 $\cos x \geq a > 0$ 的解集在 $[0, 2\pi]$ 内是**两段分离区间**（靠近 $0$ 和 $2\pi$ 各一段），这是二者的关键结构差异。

### 正切不等式与区间限制

正切函数的周期为 $\pi$（而非 $2\pi$），且在每个开区间 $\left(-\frac{\pi}{2} + k\pi,\ \frac{\pi}{2} + k\pi\right)$ 上严格单调递增。因此 $\tan x > a$ 的通解为：

$$\arctan a + k\pi < x < \frac{\pi}{2} + k\pi, \quad k \in \mathbb{Z}$$

当 $a = 1$ 时，$\arctan 1 = \frac{\pi}{4}$，解为 $\frac{\pi}{4} + k\pi < x < \frac{\pi}{2} + k\pi$，每段区间长度为 $\frac{\pi}{4}$。正切不等式求解时必须明确排除间断点 $x = \frac{\pi}{2} + k\pi$，这是与正弦、余弦不等式的重要区别。

### 辅助角法处理复合形式

形如 $a\sin x + b\cos x > c$ 的不等式，先利用辅助角公式变形为：

$$\sqrt{a^2 + b^2}\,\sin(x + \varphi) > c, \quad \tan\varphi = \frac{b}{a}$$

再用标准正弦不等式方法求解。例如 $\sqrt{3}\sin x + \cos x > 1$，变形为 $2\sin\left(x + \frac{\pi}{6}\right) > 1$，即 $\sin\left(x + \frac{\pi}{6}\right) > \frac{1}{2}$，令 $t = x + \frac{\pi}{6}$，先求 $t$ 的范围再回代得到 $x$ 的解集。

---

## 实际应用

**物理中的振动区间分析**：在简谐振动 $y = A\sin(\omega t + \varphi)$ 中，求质点位移满足 $y > \frac{A}{2}$ 的时间段，本质是求解 $\sin(\omega t + \varphi) > \frac{1}{2}$，这是三角不等式在运动学中的直接应用。

**竞赛题型——绝对值与三角结合**：例如求满足 $|\sin x| < \frac{\sqrt{3}}{2}$ 的解集。先拆解为 $-\frac{\sqrt{3}}{2} < \sin x < \frac{\sqrt{3}}{2}$，分别求上下界后取交集，在 $[0, 2\pi]$ 内解为 $0 \leq x < \frac{\pi}{3}$ 或 $\frac{2\pi}{3} < x < \frac{4\pi}{3}$ 或 $\frac{5\pi}{3} < x \leq 2\pi$，展示了绝对值与正弦不等式叠加的复杂解集。

**确定函数值域问题**：求 $f(x) = \frac{1}{2 - \cos x}$ 的值域，等价于对所有实数 $x$，分析 $\cos x \in [-1, 1]$ 后得 $2 - \cos x \in [1, 3]$，从而值域为 $\left[\frac{1}{3}, 1\right]$，这里隐含了 $\cos x \geq -1$ 与 $\cos x \leq 1$ 两个三角不等式的约束。

---

## 常见误区

**误区一：忽略周期性导致漏解**。学生常只求出 $[0, 2\pi]$ 内的解后便停止，未加 $2k\pi$（或正切情形的 $k\pi$）表示无穷族解。例如 $\cos x \leq 0$ 的完整通解为 $\frac{\pi}{2} + 2k\pi \leq x \leq \frac{3\pi}{2} + 2k\pi$，省略 $k \in \mathbb{Z}$ 会导致解不完整。

**误区二：混淆不等号方向在对称区间上的翻转**。正弦函数在 $[\frac{\pi}{2}, \frac{3\pi}{2}]$ 上单调**递减**，当利用单调性从 $\sin x < \sin\alpha$ 推导 $x$ 的范围时，需特别注意在递减段不等号方向与 $x$ 增减方向相反。许多学生在此段错误地保持了与递增段相同的不等号方向。

**误区三：将三角不等式的解集误认为有限集**。部分学生看到 $\sin x = \frac{1}{2}$ 只有两个主值解，便以为 $\sin x > \frac{1}{2}$ 的解也只有有限个区间。实际上由于周期 $2\pi$，解集是可数无穷多个开区间的并集，必须用含整数参数 $k$ 的通解表示。

---

## 知识关联

**依赖三角方程**：三角不等式的求解以三角方程为基础——求解边界不等式 $\sin x = a$ 或 $\cos x = a$ 正是三角方程的内容，再根据函数图像判断不等号方向对应的区间。若三角方程的通解形式（如 $x = n\pi + (-1)^n\arcsin a$）掌握不熟练，则三角不等式的通解表达也会出错。

**连接函数单调性理论**：三角不等式的核心求解工具是三角函数在各单调区间上的增减性，这要求学生熟记 $\sin x$ 在 $[-\frac{\pi}{2}, \frac{\pi}{2}]$ 递增、$\cos x$ 在 $[0, \pi]$ 递减、$\tan x$ 在 $(-\frac{\pi}{2}, \frac{\pi}{2})$ 递增等基本单调区间，并将其应用于不等式解集的区间判断。

**为数列与极限奠定基础**：在分析数列 $a_n = \sin n$ 或级数收敛性时，经常需要确定满足某三角不等式的正整数 $n$ 的集合，这是三角不等式在离散数学和数学分析初步中的延伸应用。
