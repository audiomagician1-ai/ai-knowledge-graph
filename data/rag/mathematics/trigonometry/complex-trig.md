---
id: "complex-trig"
concept: "复数的三角形式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 复数的三角形式

## 概述

复数的三角形式是将复数 $z = a + bi$ 用其模（距离原点的长度）和辐角（与正实轴的夹角）来表达的方式，记为 $z = r(\cos\theta + i\sin\theta)$，其中 $r = |z| = \sqrt{a^2 + b^2}$，$\theta$ 为辐角。这种表示法将复数的代数信息转化为几何信息，使乘法和乘方运算变得极为简洁。

该表达形式的系统化理论由18世纪数学家亚伯拉罕·棣莫弗（Abraham de Moivre）奠定，他于1722年发现了后来以其名字命名的公式。欧拉于1748年进一步将其整合进指数形式 $z = re^{i\theta}$（欧拉公式），但三角形式本身作为教学入口仍具有不可替代的直观性。

三角形式之所以重要，在于它将复数乘法的"旋转+缩放"本质显式化。两个复数相乘时，模相乘而辐角相加——这一规律在代数形式 $(a+bi)(c+di)$ 中完全隐藏，但在三角形式中一目了然。这正是理解傅里叶变换、交流电路相量分析等高级应用的几何基础。

---

## 核心原理

### 模与辐角的定义

设复数 $z = a + bi$ 对应复平面上的点 $(a, b)$，则：

- **模**（modulus）：$r = |z| = \sqrt{a^2 + b^2}$，即原点到该点的距离，恒满足 $r \geq 0$。
- **辐角**（argument）：$\theta = \arg(z)$，即从正实轴到向量 $\overrightarrow{Oz}$ 的有向角。辐角不唯一，所有满足条件的角构成集合 $\{\theta + 2k\pi \mid k \in \mathbb{Z}\}$。

为了唯一性，通常规定**主辐角** $\text{Arg}(z) \in (-\pi, \pi]$。从 $a, b$ 求主辐角时不能简单地写 $\theta = \arctan(b/a)$，因为 $\arctan$ 值域仅为 $(-\pi/2, \pi/2)$，必须根据点 $(a, b)$ 所在象限进行修正：第二象限需加 $\pi$，第三象限需减 $\pi$。

### 三角形式的建立

由模与辐角的关系，可以写出：
$$a = r\cos\theta, \quad b = r\sin\theta$$

因此复数的三角形式为：
$$z = r(\cos\theta + i\sin\theta)$$

验证：将 $r=1, \theta=\pi/2$ 代入，得 $z = \cos(\pi/2) + i\sin(\pi/2) = 0 + i = i$，与单位圆上 $90°$ 处的点完全吻合。

数学界常将 $\cos\theta + i\sin\theta$ 缩写为 $\text{cis}\,\theta$，但高中教材一般保留完整写法。

### 乘法、除法与棣莫弗公式

设 $z_1 = r_1(\cos\theta_1 + i\sin\theta_1)$，$z_2 = r_2(\cos\theta_2 + i\sin\theta_2)$，则：

$$z_1 \cdot z_2 = r_1 r_2 \bigl[\cos(\theta_1 + \theta_2) + i\sin(\theta_1 + \theta_2)\bigr]$$

这一结果由和角公式直接展开得到：
$$(\cos\theta_1\cos\theta_2 - \sin\theta_1\sin\theta_2) + i(\sin\theta_1\cos\theta_2 + \cos\theta_1\sin\theta_2) = \cos(\theta_1+\theta_2) + i\sin(\theta_1+\theta_2)$$

除法类似，模相除而辐角相减：
$$\frac{z_1}{z_2} = \frac{r_1}{r_2}\bigl[\cos(\theta_1 - \theta_2) + i\sin(\theta_1 - \theta_2)\bigr], \quad z_2 \neq 0$$

将乘法规则反复应用 $n$ 次，即得**棣莫弗公式**（de Moivre's theorem）：

$$\bigl[r(\cos\theta + i\sin\theta)\bigr]^n = r^n(\cos n\theta + i\sin n\theta), \quad n \in \mathbb{Z}$$

当 $r=1$ 时，公式简化为 $(\cos\theta + i\sin\theta)^n = \cos n\theta + i\sin n\theta$。利用此公式可以极为高效地推导多倍角公式：令 $n=3$，展开左边并比较实虚部，立刻得到 $\cos 3\theta = 4\cos^3\theta - 3\cos\theta$，以及 $\sin 3\theta = 3\sin\theta - 4\sin^3\theta$。

---

## 实际应用

**求高次幂**：计算 $(\sqrt{3}+i)^{10}$。直接展开代数形式极为繁琐，但转化为三角形式后：$r = 2$，$\theta = \pi/6$，于是 $(\sqrt{3}+i)^{10} = 2^{10}(\cos\frac{10\pi}{6} + i\sin\frac{10\pi}{6}) = 1024(\cos\frac{5\pi}{3} + i\sin\frac{5\pi}{3}) = 1024(\frac{1}{2} - \frac{\sqrt{3}}{2}i) = 512 - 512\sqrt{3}\,i$。

**求单位根**：方程 $z^n = 1$ 的全部 $n$ 个解（$n$ 次单位根）为 $z_k = \cos\frac{2k\pi}{n} + i\sin\frac{2k\pi}{n}$，$k = 0, 1, \ldots, n-1$。这些点在复平面单位圆上均匀分布，相邻两点的辐角间隔恰好是 $\frac{2\pi}{n}$。当 $n=3$ 时，三个根构成等边三角形的顶点。

**证明三角恒等式**：利用棣莫弗公式展开 $(\cos\theta + i\sin\theta)^5$，实部给出 $\cos 5\theta$ 的展开式，虚部给出 $\sin 5\theta$ 的展开式，一步完成通常需要多次应用和角公式才能完成的推导。

---

## 常见误区

**误区一：忽略辐角的象限修正**。初学者常用 $\theta = \arctan(b/a)$ 直接计算辐角，但对于第二、三象限的复数，此公式给出错误结果。例如 $z = -1 + \sqrt{3}\,i$ 位于第二象限，$\arctan(\sqrt{3}/(-1)) = \arctan(-\sqrt{3}) = -\pi/3$，但正确的主辐角应为 $\pi - \pi/3 = 2\pi/3$。必须先判断象限再决定是否修正。

**误区二：认为棣莫弗公式仅对正整数 $n$ 成立**。公式对全体整数 $n \in \mathbb{Z}$ 均成立（负整数情形可由除法规则推出）。进一步地，当 $n$ 为有理数 $p/q$ 时，公式给出 $z^{p/q}$ 的一个值，但此时结果不唯一，需额外处理多值问题。许多学生误以为 $z^{1/2} = \sqrt{r}\,(\cos\frac{\theta}{2}+i\sin\frac{\theta}{2})$ 是唯一的平方根，而实际上还有第二个根对应辐角 $\frac{\theta}{2}+\pi$。

**误区三：混淆模的乘法与加法**。三角形式下两复数相乘时，模是**相乘**（$r_1 r_2$），辐角是**相加**（$\theta_1+\theta_2$）。学生有时受加法思维影响，误将模也做加法。一个快速验证：$|z_1 z_2| = |z_1||z_2|$ 是复数模的乘法性质，可代入具体数字（如 $z_1 = 1+i, z_2 = 1+i$，模均为 $\sqrt{2}$，乘积为 $2i$，模为 $2 = \sqrt{2}\times\sqrt{2}$）立即检验。

---

## 知识关联

**依赖的前置知识**：复数三角形式直接建立在**复数初步**（复平面、实部虚部概念）之上，坐标点 $(a,b)$ 与 $a+bi$ 的对应关系是理解模与辐角的基础。同时，将 $(a,b)$ 转化为极坐标 $(r,\theta)$ 的步骤依赖**单位圆**上的三角函数定义——$\cos\theta$ 和 $\sin\theta$ 在此被理解为单位向量的分量，而非仅仅是直角三角形的比值。

**向后延伸**：三角形式是理解**欧拉公式** $e^{i\theta} = \cos\theta + i\sin\theta$ 的桥梁，后者将三角形式压缩为更紧凑的指数形式 $z = re^{i\theta}$。在大学数学中，棣莫弗公式的多值推广引出**复数的根式**和**黎曼面**概念；在工程应用中，三角形式直接演变为描述正弦交流电的**相量（phasor）**表示法，辐角对应初相，模对应峰值电压或电流。