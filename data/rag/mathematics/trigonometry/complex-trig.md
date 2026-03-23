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
quality_tier: "pending-rescore"
quality_score: 35.5
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 复数的三角形式

## 概述

复数的三角形式是将复数 $z = a + bi$ 用其**模**和**辐角**重新表达的方式，具体写作 $z = r(\cos\theta + i\sin\theta)$，其中 $r = |z| = \sqrt{a^2 + b^2}$ 是复数的模，$\theta$ 是复数对应向量与正实轴的夹角，称为辐角。这种表示形式将复数的"大小"与"方向"分离，使乘除运算从代数展开变为模的乘除与辐角的加减，极大简化了高次幂和方根的计算。

三角形式的系统化使用可追溯到18世纪。瑞士数学家欧拉（Leonhard Euler）于1748年在《无穷分析引论》中证明了 $e^{i\theta} = \cos\theta + i\sin\theta$，即著名的欧拉公式，这为三角形式提供了深层的指数意义。与此同时，法国数学家棣莫弗（Abraham de Moivre）早在1722年就发现了以他命名的公式，直接从三角形式的乘法规律延伸而来。

学习三角形式的价值在于它让"复数的乘法等于旋转加缩放"这一几何直觉有了精确的代数表达。若两复数 $z_1 = r_1(\cos\theta_1 + i\sin\theta_1)$、$z_2 = r_2(\cos\theta_2 + i\sin\theta_2)$，则乘积的模等于 $r_1 r_2$，辐角等于 $\theta_1 + \theta_2$，这是代数形式无法直接"看见"的结构。

---

## 核心原理

### 模与辐角的定义

设复数 $z = a + bi$，其模定义为 $r = \sqrt{a^2 + b^2} \geq 0$，几何上等于复平面上点 $(a, b)$ 到原点的距离。辐角 $\theta$ 满足 $\cos\theta = \dfrac{a}{r}$，$\sin\theta = \dfrac{b}{r}$，即 $\tan\theta = \dfrac{b}{a}$（当 $a \neq 0$）。

需要特别注意：辐角不唯一，若 $\theta_0$ 是一个辐角，则 $\theta_0 + 2k\pi$（$k \in \mathbb{Z}$）均为辐角。为消除歧义，规定**主辐角** $\text{Arg}(z) \in (-\pi, \pi]$。例如复数 $z = -1 + i$ 的模为 $\sqrt{2}$，主辐角为 $\dfrac{3\pi}{4}$，因为它位于第二象限，$\tan\theta = -1$ 且 $\sin\theta > 0$。

### 三角形式的乘除法则

设 $z_1 = r_1(\cos\theta_1 + i\sin\theta_1)$，$z_2 = r_2(\cos\theta_2 + i\sin\theta_2)$，利用积化和差公式展开：

$$z_1 z_2 = r_1 r_2 \bigl[\cos(\theta_1+\theta_2) + i\sin(\theta_1+\theta_2)\bigr]$$

这一推导完全依赖 $\cos(\alpha+\beta) = \cos\alpha\cos\beta - \sin\alpha\sin\beta$ 及 $\sin(\alpha+\beta) = \sin\alpha\cos\beta + \cos\alpha\sin\beta$。同理：

$$\frac{z_1}{z_2} = \frac{r_1}{r_2}\bigl[\cos(\theta_1-\theta_2) + i\sin(\theta_1-\theta_2)\bigr] \quad (z_2 \neq 0)$$

这意味着复数除法在几何上对应**模相除、辐角相减**，即对 $z_1$ 表示的向量做反向旋转 $\theta_2$ 再缩放。

### 棣莫弗公式

将乘法法则递推 $n$ 次，可得**棣莫弗公式**（de Moivre's formula）：

$$\bigl[r(\cos\theta + i\sin\theta)\bigr]^n = r^n(\cos n\theta + i\sin n\theta)$$

此公式对所有整数 $n$ 成立（负整数情形通过取倒数再应用正整数情形推得）。利用棣莫弗公式可以将 $\cos 3\theta$ 展开为 $4\cos^3\theta - 3\cos\theta$：令 $r=1$，比较 $(\cos\theta + i\sin\theta)^3$ 展开式的实部即得。这是三角恒等式推导的强力工具，反映了三角形式与多倍角公式之间的内在联系。

对于复数的 $n$ 次方根，设 $w^n = z$，则方根共有 **$n$ 个**，均匀分布在以原点为圆心、半径为 $r^{1/n}$ 的圆上，相邻两根之间的辐角差恰好是 $\dfrac{2\pi}{n}$。

---

## 实际应用

**计算高次幂：** 求 $(\sqrt{3} + i)^{10}$。先转化：$r = 2$，$\theta = \dfrac{\pi}{6}$，故原式 $= 2^{10}\!\left(\cos\dfrac{10\pi}{6} + i\sin\dfrac{10\pi}{6}\right) = 1024\!\left(\cos\dfrac{5\pi}{3} + i\sin\dfrac{5\pi}{3}\right) = 1024\!\left(\dfrac{1}{2} - \dfrac{\sqrt{3}}{2}i\right) = 512 - 512\sqrt{3}\,i$。若用代数形式直接展开，需经历十次多项式乘法，工作量天差地别。

**求单位复数的 $n$ 次方根：** 方程 $z^6 = 1$ 的六个解（六次单位根）为 $z_k = \cos\dfrac{2k\pi}{6} + i\sin\dfrac{2k\pi}{6}$，$k = 0,1,2,3,4,5$，在复平面上构成正六边形的六个顶点。这一结论在信号处理中的离散傅里叶变换（DFT）里有直接应用：$N$ 点 DFT 的旋转因子正是 $N$ 个均匀分布的单位根。

**平面旋转变换：** 将复平面上的点 $P$ 对应复数 $z$，令 $w = z \cdot (\cos\alpha + i\sin\alpha)$，则 $w$ 对应的点是 $P$ 绕原点旋转角度 $\alpha$ 后的像。这在计算机图形学的2D变换矩阵中有等价表示，但复数乘法只需一行计算。

---

## 常见误区

**误区一：辐角与反正切混淆。** 许多学生直接用 $\theta = \arctan\!\left(\dfrac{b}{a}\right)$ 求辐角，但 $\arctan$ 的值域只有 $\left(-\dfrac{\pi}{2}, \dfrac{\pi}{2}\right)$，无法区分第二、三象限。例如 $z = -1 - i$ 的主辐角是 $-\dfrac{3\pi}{4}$，而 $\arctan(1) = \dfrac{\pi}{4}$，二者相差 $\pi$。正确做法是先判断象限，再结合 $\cos\theta$ 和 $\sin\theta$ 的符号确定辐角。

**误区二：棣莫弗公式误用于和式。** 有学生认为 $(\cos\alpha + i\sin\alpha) + (\cos\beta + i\sin\beta) = \cos(\alpha+\beta) + i\sin(\alpha+\beta)$，将乘法规律错误地套到加法上。棣莫弗公式描述的是**乘幂**运算，加法没有类似的辐角相加规律，两个模为1的复数之和的模可以从0到2，辐角须重新计算。

**误区三：认为 $z = 0$ 也有三角形式。** 零复数的模为0，但辐角无法定义（任意角度的余弦/正弦与0相乘均为0），因此 $z = 0$ 不能写成三角形式。三角形式只对 $z \neq 0$ 有意义，这与极坐标中原点无极角的情况完全对应。

---

## 知识关联

**与复数初步的衔接：** 代数形式 $z = a + bi$ 和三角形式 $z = r(\cos\theta + i\sin\theta)$ 通过 $a = r\cos\theta$、$b = r\sin\theta$ 相互转化。单位圆上（$r=1$）的复数 $\cos\theta + i\sin\theta$ 正是三角形式最纯粹的特例，欧拉公式将其记作 $e^{i\theta}$，揭示了指数函数与三角函数的深层统一。

**向下联系——单位圆：** 单位圆上的参数化坐标 $(\cos\theta, \sin\theta)$ 是理解辐角为何能表征"方向"的几何基础。模 $r=1$ 的三角形式乘法在单位圆上表现为纯旋转，这直接说明了为何两个模为1的复数之积仍在单位圆上（辐角相加，模仍为1）。

**向上延伸——欧拉公式与复变函数：** 将三角形式推广，令 $\theta$ 取复数值，即进入复变函数中指数函数的定义领域。棣莫弗公式在整数 $n$ 推广到有理数、实数乃至复数时，分别对应多值复数根、复数指数和一般复幂运算，是后续学习留数定
