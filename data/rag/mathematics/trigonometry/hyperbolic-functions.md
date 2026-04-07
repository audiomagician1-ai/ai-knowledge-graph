---
id: "hyperbolic-functions"
concept: "双曲函数"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 7
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 双曲函数

## 概述

双曲函数是以自然指数函数的特定组合形式定义的一族函数，与圆（三角）函数具有形式上的对称美感，但其几何背景完全不同。三角函数的参数描述单位圆上的点，而双曲函数的参数描述单位双曲线 $x^2 - y^2 = 1$ 上点的坐标——具体地说，若 $t$ 为双曲线扇形面积的两倍，则对应点的横坐标为 $\cosh t$，纵坐标为 $\sinh t$。

双曲函数由意大利数学家文森佐·里卡蒂（Vincenzo Riccati）于1757年前后引入，莱昂哈德·欧拉随后系统化了相关理论。19世纪以来，双曲函数在解析几何、微分方程和相对论力学中均发挥了不可替代的作用，例如悬链线的方程恰好是 $y = a\cosh(x/a)$，描述仅受重力与张力作用的均匀柔性绳的自然下垂形状。

双曲函数之所以在高等数学中具有独特地位，在于它们提供了不定积分 $\int \frac{1}{\sqrt{x^2 \pm a^2}}\,dx$ 的精确表达式，而这类积分若用三角换元则无法完成，必须依赖双曲换元。

---

## 核心原理

### 三个基本函数的指数定义

双曲正弦、双曲余弦、双曲正切的定义式直接给出其计算规则：

$$\sinh x = \frac{e^x - e^{-x}}{2}, \quad \cosh x = \frac{e^x + e^{-x}}{2}, \quad \tanh x = \frac{\sinh x}{\cosh x} = \frac{e^x - e^{-x}}{e^x + e^{-x}}$$

其中 $e \approx 2.71828$ 为自然对数的底。$\sinh x$ 是奇函数（$\sinh(-x) = -\sinh x$），$\cosh x$ 是偶函数（$\cosh(-x) = \cosh x$），$\tanh x$ 是奇函数且值域严格限制在 $(-1, 1)$ 内。此外还有双曲余切 $\coth x = \cosh x/\sinh x$、双曲正割 $\text{sech}\,x = 1/\cosh x$、双曲余割 $\text{csch}\,x = 1/\sinh x$，共同构成完整体系。

### 双曲恒等式与对应的三角恒等式

双曲函数满足一套与三角恒等式高度对应但**符号有差异**的等式，这一现象由奥斯本规则（Osborn's rule，1902年）描述：将三角恒等式中的 $\sin$ 换为 $\sinh$、$\cos$ 换为 $\cosh$，凡出现两个正弦函数之积（含隐含乘积）的项，符号取反，即得对应双曲恒等式。

最基本的双曲恒等式为：

$$\cosh^2 x - \sinh^2 x = 1$$

注意此处是**减号**，而圆函数对应式为 $\cos^2\theta + \sin^2\theta = 1$（加号）。其他常用恒等式包括：

$$\sinh(x+y) = \sinh x\cosh y + \cosh x\sinh y$$
$$\cosh(x+y) = \cosh x\cosh y + \sinh x\sinh y$$
$$\tanh(x+y) = \frac{\tanh x + \tanh y}{1 + \tanh x\tanh y}$$

### 导数与不定积分

双曲函数的导数公式与三角函数类似，但符号再次出现关键差异：

$$(\sinh x)' = \cosh x, \quad (\cosh x)' = \sinh x, \quad (\tanh x)' = \text{sech}^2 x = \frac{1}{\cosh^2 x}$$

注意 $(\cosh x)' = +\sinh x$，而不是像 $(\cos x)' = -\sin x$ 那样带负号。利用这些导数，可以建立以下积分公式，这是双曲换元法的理论基础：

$$\int \frac{dx}{\sqrt{x^2 + a^2}} = \sinh^{-1}\!\left(\frac{x}{a}\right) + C = \ln\!\left(x + \sqrt{x^2+a^2}\right) + C$$
$$\int \frac{dx}{\sqrt{x^2 - a^2}} = \cosh^{-1}\!\left(\frac{x}{a}\right) + C = \ln\!\left(x + \sqrt{x^2-a^2}\right) + C \quad (x > a > 0)$$

### 反双曲函数与对数表达

由于 $\sinh x$ 和 $\tanh x$ 均为严格单调函数，其反函数全域定义；$\cosh x$ 在 $[0,+\infty)$ 上单调，反函数 $\cosh^{-1}$ 定义在 $[1,+\infty)$。三个反双曲函数均可用自然对数显式表示：

$$\sinh^{-1} x = \ln\!\left(x + \sqrt{x^2+1}\right), \quad x \in \mathbb{R}$$
$$\cosh^{-1} x = \ln\!\left(x + \sqrt{x^2-1}\right), \quad x \geq 1$$
$$\tanh^{-1} x = \frac{1}{2}\ln\frac{1+x}{1-x}, \quad |x| < 1$$

这意味着反双曲函数本质上是对数函数，而非独立的超越函数类型。

---

## 实际应用

**悬链线工程计算**：两端固定、自然下垂的均匀链条形状满足方程 $y = a\cosh(x/a)$，其中参数 $a$ 等于链条底部张力除以单位长度重力。圣路易斯拱门的形状实际上是**倒悬链线**，即 $y = A - a\cosh(x/a)$，建筑师埃罗·沙里宁设计时采用了该曲线的变体以兼顾美观与结构强度。

**双曲换元积分**：计算 $\int\sqrt{x^2+1}\,dx$ 时，令 $x = \sinh t$，则 $\sqrt{x^2+1} = \cosh t$，$dx = \cosh t\,dt$，积分化为 $\int \cosh^2 t\,dt = \frac{1}{2}(t + \sinh t\cosh t) + C$，最终回代得 $\frac{x\sqrt{x^2+1}}{2} + \frac{\ln(x+\sqrt{x^2+1})}{2} + C$。

**相对论力学**：狭义相对论中，洛伦兹变换可以用双曲函数的"快度"参数 $\phi$ 表示为 $t' = t\cosh\phi - x\sinh\phi$，$x' = x\cosh\phi - t\sinh\phi$（$c=1$ 单位制），其结构与旋转矩阵一致，但用双曲函数取代了圆函数。

**神经网络激活函数**：$\tanh x$ 因其输出范围 $(-1,1)$ 且在原点处斜率为1（即 $\tanh'(0) = 1$），被广泛用作早期深度学习模型的激活函数，其梯度公式 $\tanh'(x) = 1 - \tanh^2 x$ 便于反向传播计算。

---

## 常见误区

**误区一：$\cosh x \geq 1$ 而非 $\cosh x \geq 0$。** 很多学生误以为 $\cosh x$ 的最小值为0（类比 $\cos\theta$ 的值域）。实际上，由 $\cosh x = \frac{e^x + e^{-x}}{2} \geq \frac{2\sqrt{e^x \cdot e^{-x}}}{2} = 1$（AM-GM不等式），$\cosh x$ 的最小值恰好是1，在 $x=0$ 处取到，且 $\cosh x \to +\infty$ 当 $|x| \to \infty$。这使得 $\cosh x$ 的值域为 $[1, +\infty)$，与 $\cos\theta \in [-1,1]$ 完全不同。

**误区二：混淆导数符号。** 学生常将 $(\cosh x)' = \sinh x$ 错记为带负号，原因是习惯了 $(\cos x)' = -\sin x$。双曲函数的导数链为 $\sinh \to \cosh \to \sinh \to \cdots$，始终为正号循环，而三角函数为 $\sin \to \cos \to -\sin \to -\cos \to \cdots$，出现符号交替。

**误区三：将 $\tanh x$ 的渐近线错判为 $y = \pm\infty$。** $\tanh x$ 有两条水平渐近线 $y = 1$（$x \to +\infty$）和 $y = -1$（$x \to -\infty$），且 $|\tanh x| < 1$ 对所有实数 $x$ 严格成立。这一有界性是 $\tanh$ 而非 $\sinh$ 或 $\cosh$ 被选作神经网络激活函数的直接原因。

---

## 知识关联

**依赖指数函数**：三个基本双曲函数的定义式 $\sinh x = (e^x - e^{-x})/2$、$\cosh x = (e^x + e^{-x})/2$ 要求掌握 $e^x$ 的代数运算和 $e^x > 0$ 的性质；若不熟悉指数函数的单调性与极限行为，将无法推导 $\tanh x$