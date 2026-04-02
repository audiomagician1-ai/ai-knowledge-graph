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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 三角不等式

## 概述

三角不等式是指含有三角函数（正弦、余弦、正切等）的不等式，求解目标是找出使不等式成立的自变量 $x$ 的取值范围。与三角方程求特定解不同，三角不等式的解是实数轴上的区间集合，且由于三角函数的周期性，其解集通常包含无穷多个区间，需用 $k\pi$（$k \in \mathbb{Z}$）或 $2k\pi$（$k \in \mathbb{Z}$）来表示完整解集。

三角不等式的系统研究伴随着三角学的发展而成熟，在微积分前身的分析学中，数学家如欧拉在18世纪的工作中已大量运用正弦、余弦函数的单调区间来处理不等关系。进入现代中学课程，三角不等式成为高考数学的重要考点，尤其在确定函数定义域（如 $\sin x > 0$ 限定 $x$ 的范围）和解析几何中角度约束问题中频繁出现。

三角不等式的难点在于：三角函数在不同区间上的单调性方向相反，且解集是无限周期重复的，若仅凭代数变形而忽视图像分析，极易遗漏解或写错方向。掌握三角不等式不仅要求熟悉三角函数的值域、单调区间，还需要准确将不等号方向与函数图像上升/下降趋势对应起来。

---

## 核心原理

### 基于单位圆与图像的解法

最基本的三角不等式如 $\sin x > a$（其中 $-1 \leq a \leq 1$），其解法依赖正弦函数图像：在单位圆中，$\sin x = a$ 对应纵坐标为 $a$ 的水平线与单位圆的两个交点。以 $\sin x > \frac{1}{2}$ 为例：

- 在 $[0, 2\pi)$ 内，$\sin x = \frac{1}{2}$ 的解为 $x = \frac{\pi}{6}$ 和 $x = \frac{5\pi}{6}$；
- 正弦函数在 $\left(\frac{\pi}{6},\ \frac{5\pi}{6}\right)$ 上大于 $\frac{1}{2}$；
- 加入周期性，完整解集为：$2k\pi + \frac{\pi}{6} < x < 2k\pi + \frac{5\pi}{6}$，$k \in \mathbb{Z}$。

余弦不等式 $\cos x > a$ 的结构不同：以 $\cos x > \frac{\sqrt{2}}{2}$ 为例，$\cos x = \frac{\sqrt{2}}{2}$ 的解在 $[0,2\pi)$ 内为 $x = \frac{\pi}{4}$ 和 $x = \frac{7\pi}{4}$，余弦大于该值的区间是靠近 $x=0$（或 $2\pi$）的区间，解集为 $-\frac{\pi}{4} + 2k\pi < x < \frac{\pi}{4} + 2k\pi$，$k \in \mathbb{Z}$，体现出余弦函数关于 $x=0$ 对称的单调特征。

### 辅助角与换元处理复合型不等式

当不等式形如 $a\sin x + b\cos x > c$ 时，需先将左端化为辅助角形式：

$$a\sin x + b\cos x = \sqrt{a^2+b^2}\,\sin\!\left(x + \varphi\right)$$

其中 $\tan\varphi = \dfrac{b}{a}$（$\varphi$ 的象限由 $a,b$ 的符号决定）。令 $t = x + \varphi$，原不等式转化为 $\sqrt{a^2+b^2}\sin t > c$，即 $\sin t > \dfrac{c}{\sqrt{a^2+b^2}}$，再按基本正弦不等式求 $t$ 的范围，最后回代 $x = t - \varphi$ 并整理。

例：$\sin x + \sqrt{3}\cos x > 1$，化为 $2\sin\!\left(x+\dfrac{\pi}{3}\right) > 1$，即 $\sin\!\left(x+\dfrac{\pi}{3}\right) > \dfrac{1}{2}$，解得 $2k\pi + \dfrac{\pi}{6} < x+\dfrac{\pi}{3} < 2k\pi + \dfrac{5\pi}{6}$，最终 $2k\pi - \dfrac{\pi}{6} < x < 2k\pi + \dfrac{\pi}{2}$，$k \in \mathbb{Z}$。

### 正切不等式与其特殊性

$\tan x > a$ 的处理与正弦、余弦不等式有本质差异：正切函数在每个周期 $\left(-\dfrac{\pi}{2}+k\pi,\ \dfrac{\pi}{2}+k\pi\right)$ 内严格单调递增，因此 $\tan x > a$ 的解为：

$$\arctan a + k\pi < x < \frac{\pi}{2} + k\pi,\quad k \in \mathbb{Z}$$

注意每个周期内解是一个开区间，不含端点 $\dfrac{\pi}{2}+k\pi$（正切无定义处）。这与正弦、余弦不等式的解集结构（每个 $2\pi$ 周期对应一段弧）明显不同。

---

## 实际应用

**函数定义域问题**：求 $f(x)=\lg(\sin x)$ 的定义域，需解 $\sin x > 0$，即 $2k\pi < x < 2k\pi + \pi$（$k \in \mathbb{Z}$），这是对数函数要求真数为正与正弦不等式的结合。

**角度范围约束**：在三角形 $ABC$ 中，已知 $\cos A > \cos B$（$A,B \in (0,\pi)$），由余弦函数在 $(0,\pi)$ 上单调递减，可直接得出 $A < B$，这是三角不等式在几何推理中的应用。

**物理与工程中的周期约束**：描述简谐振动相位区间时，需解如 $\cos(\omega t + \phi) \geq \dfrac{\sqrt{3}}{2}$ 的不等式，直接对应振幅超过某阈值的时间段，其解为以 $\dfrac{2\pi}{\omega}$ 为周期的无穷多区间。

---

## 常见误区

**误区一：混淆"$\geq$"与"$>$"对端点的处理**。$\sin x \geq \dfrac{1}{2}$ 的解集包含端点 $\dfrac{\pi}{6}+2k\pi$ 和 $\dfrac{5\pi}{6}+2k\pi$，用闭区间 $\left[\dfrac{\pi}{6}+2k\pi,\ \dfrac{5\pi}{6}+2k\pi\right]$ 表示；而 $\sin x > \dfrac{1}{2}$ 使用开区间。学生常将两者端点处理搞混，在考试中丢失关键的边界分。

**误区二：余弦不等式的解集方向写反**。$\cos x < \dfrac{1}{2}$ 的解在 $[0,2\pi)$ 内是 $\left(\dfrac{\pi}{3},\ \dfrac{5\pi}{3}\right)$，而非两端靠近 $0$ 和 $2\pi$ 的部分。许多学生错误套用正弦不等式的"内侧/外侧"记忆法，导致把余弦不等式的解集方向搞反。正确方法是回归余弦图像：余弦在 $(0,\pi)$ 递减，$\cos x < \dfrac{1}{2}$ 从 $\dfrac{\pi}{3}$ 开始成立。

**误区三：忘记正切不等式各周期的定义域限制**。解 $\tan x > \sqrt{3}$ 时，$x = \dfrac{\pi}{2}+k\pi$ 处正切无意义，解集上界不能写成闭区间，且每个周期的区间长度为 $\dfrac{\pi}{6}$（从 $\dfrac{\pi}{3}+k\pi$ 到 $\dfrac{\pi}{2}+k\pi$ 的开区间），而非整个 $\pi$ 周期。

---

## 知识关联

**与三角方程的关系**：三角方程（如 $\sin x = \dfrac{1}{2}$）给出的是不等式解集的**端点**，即每次求解三角不等式，必须先准确找到对应三角方程的解作为临界值，再根据不等号方向和函数单调性确定哪侧区间满足条件。三角方程解法中的通解公式（$x = \arcsin a + 2k\pi$ 或 $x = \pi - \arcsin a + 2k\pi$）直接构成三角不等式解集的两端边界。

**与三角函数图像分析的联系**：三角不等式的求解本质上是在函数图像上读取"图像位于水平线 $y=a$ 上方或下方"的 $x$ 区间，因此熟悉 $\sin x$、$\cos x$、$\tan x$ 在标准区间上的增减表和关键值（如 $\sin\dfrac{\pi}{6}=\dfrac{1}{2}$，$\cos\dfrac{\pi}{3}=\dfrac{1}{2}$，$\tan\dfrac{\pi}{4}=1$）是快速求解的前提。

**向微积分过渡**：三角不等式所训练的"从方程解到区间解"的思维，以及利用函数单调性判断不等号方向的方法，直接对应微积分中利用导数正负判断函数增减区间的逻辑，是分析学中处理函数比