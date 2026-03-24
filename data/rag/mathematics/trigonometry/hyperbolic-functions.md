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
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 双曲函数

## 概述

双曲函数是一组以自然指数函数 $e^x$ 的组合为基础定义的函数族，包括双曲正弦（sinh）、双曲余弦（cosh）、双曲正切（tanh）及其倒数形式。与普通三角函数描述单位圆上的点不同，双曲函数描述的是单位双曲线 $x^2 - y^2 = 1$ 上的点：若令 $x = \cosh t$，$y = \sinh t$，则 $\cosh^2 t - \sinh^2 t = 1$ 恒成立，这一几何背景赋予了"双曲"这个名称。

双曲函数的现代形式由意大利数学家文森佐·里卡蒂（Vincenzo Riccati）于1757年前后首次系统引入，他使用的记号 $\text{Sh}$ 和 $\text{Ch}$ 是今日 $\sinh$、$\cosh$ 的前身。约翰·海因里希·兰伯特（Johann Heinrich Lambert）随后于1768年在其著作中独立研究并推广了这些函数。双曲函数在物理学（悬链线方程）、相对论（洛伦兹变换）、工程学（传输线理论）中均有直接应用。

## 核心原理

### 三个基本函数的指数定义

双曲函数完全由自然指数函数精确定义，无需借助几何直观：

$$\sinh x = \frac{e^x - e^{-x}}{2}$$

$$\cosh x = \frac{e^x + e^{-x}}{2}$$

$$\tanh x = \frac{e^x - e^{-x}}{e^x + e^{-x}} = \frac{\sinh x}{\cosh x}$$

这三个定义揭示了奇偶性：$\sinh x$ 是奇函数（$\sinh(-x) = -\sinh x$），$\cosh x$ 是偶函数（$\cosh(-x) = \cosh x$），因此 $\cosh(0) = 1$、$\sinh(0) = 0$。$\tanh x$ 作为奇函数除以偶函数，结果仍是奇函数，且其值域严格限定在 $(-1, 1)$ 之间，当 $x \to +\infty$ 时 $\tanh x \to 1$，但永远无法等于1。

### 基本恒等式及与三角函数的对比

双曲函数满足与三角恒等式高度相似但符号有差异的恒等式，这一规律由奥斯本规则（Osborn's Rule，1902年）概括：将三角恒等式改写为双曲恒等式时，将 $\cos$ 换成 $\cosh$、$\sin$ 换成 $\sinh$，但凡遇到两个 $\sin$ 相乘的项，需将该项变号。

**基本恒等式：**
$$\cosh^2 x - \sinh^2 x = 1$$

对比三角函数的 $\cos^2 x + \sin^2 x = 1$，注意符号从加法变为减法。

**二倍角公式：**
$$\sinh(2x) = 2\sinh x \cosh x$$
$$\cosh(2x) = \cosh^2 x + \sinh^2 x = 2\cosh^2 x - 1 = 1 + 2\sinh^2 x$$

**加法公式：**
$$\sinh(x + y) = \sinh x \cosh y + \cosh x \sinh y$$
$$\cosh(x + y) = \cosh x \cosh y + \sinh x \sinh y$$

注意后者两项均为正号，而三角函数的 $\cos(x+y) = \cos x \cos y - \sin x \sin y$ 含负号。

### 导数与反双曲函数

双曲函数的导数形式简洁，与三角导数类似但无负号出现：

$$\frac{d}{dx}\sinh x = \cosh x, \quad \frac{d}{dx}\cosh x = \sinh x, \quad \frac{d}{dx}\tanh x = 1 - \tanh^2 x = \text{sech}^2 x$$

区别在于 $\frac{d}{dx}\cos x = -\sin x$ 含负号，而 $\frac{d}{dx}\cosh x = \sinh x$ 不含负号。

反双曲函数可以通过自然对数精确表达，例如：
$$\sinh^{-1} x = \ln(x + \sqrt{x^2 + 1}), \quad x \in \mathbb{R}$$
$$\cosh^{-1} x = \ln(x + \sqrt{x^2 - 1}), \quad x \geq 1$$
$$\tanh^{-1} x = \frac{1}{2}\ln\frac{1+x}{1-x}, \quad |x| < 1$$

## 实际应用

**悬链线方程：** 一条均匀柔软的链条在重力作用下自由悬挂，其形状由悬链线方程描述：$y = a \cosh\left(\dfrac{x}{a}\right)$，其中 $a = T_0 / \rho g$（$T_0$ 为最低点张力，$\rho$ 为线密度，$g$ 为重力加速度）。这与抛物线形状完全不同，伽利略曾错误地认为悬链线是抛物线，直到1691年才由雅各布·伯努利等人纠正。

**相对论中的洛伦兹变换：** 在狭义相对论中，惯性参考系之间的变换可以写成双曲旋转形式。令 $\phi = \tanh^{-1}(v/c)$（称为快度），则时空坐标变换变为 $t' = t\cosh\phi - x\sinh\phi$，与欧几里得旋转中 $\sin/\cos$ 的作用完全类比，但因 $\cosh^2\phi - \sinh^2\phi = 1$ 而保持闵可夫斯基度规不变。

**神经网络激活函数：** $\tanh x$ 被广泛用作神经网络激活函数，其值域为 $(-1, 1)$，在 $x = 0$ 处导数为1（最大值），饱和区梯度趋向0，这直接导致深层网络的梯度消失问题。相比之下，$\text{ReLU}$ 函数正是为解决这一问题而提出的。

## 常见误区

**误区1：认为双曲函数具有周期性。** 普通三角函数 $\sin x$ 和 $\cos x$ 均以 $2\pi$ 为周期，但 $\sinh x$、$\cosh x$、$\tanh x$ 均非周期函数。$\cosh x \geq 1$ 恒成立，且 $\cosh x \to +\infty$ 当 $|x| \to \infty$，与有界振荡的三角函数完全相反。双曲函数的"周期性"仅存在于其在复数域的延伸：$\sinh(x + 2\pi i) = \sinh x$（利用欧拉公式），仅在复平面上成立。

**误区2：将 $\cosh^2 x - \sinh^2 x = 1$ 与 $\cos^2 x + \sin^2 x = 1$ 混淆符号。** 许多初学者将双曲恒等式中的减号写成加号。记忆方法：双曲线方程 $x^2 - y^2 = 1$ 本身即是减法，而圆方程 $x^2 + y^2 = 1$ 是加法，两者对应的函数恒等式符号与各自的曲线方程一致。此外，由此还可得 $\sinh^2 x = \cosh^2 x - 1 \geq 0$，即 $\cosh x \geq 1$，而 $|\cos x| \leq 1$ 正好相反。

**误区3：认为反双曲函数的定义域与反三角函数相同。** $\arcsin x$ 的定义域为 $[-1, 1]$，但 $\sinh^{-1} x$ 的定义域是全体实数 $\mathbb{R}$，因为 $\sinh x$ 本身是从 $\mathbb{R}$ 到 $\mathbb{R}$ 的双射。同理，$\tanh^{-1} x$ 的定义域是开区间 $(-1, 1)$，当 $x \to \pm 1$ 时 $\tanh^{-1} x \to \pm\infty$，与有界的 $\arctan x$ 取值在 $(-\pi/2, \pi/2)$ 之间形成鲜明对比。

## 知识关联

**与指数函数的关系：** 双曲函数的所有性质都可以直接从 $e^x$ 的性质推导，特别是 $e^x = \cosh x + \sinh x$ 这一分解公式，将指数函数拆分为偶函数部分（$\cosh x$）和奇函数部分（$\sinh x$）。这与傅里叶分析中将任意函数分解为奇偶部分的思想一脉相承。

**与三角恒等式的结构关系：** 通过欧拉公式 $e^{ix} = \cos x + i\sin x$，可以建立双曲函数与三角函数的精确代换关系：$\sinh(ix) = i\sin x$，$\cosh(ix) = \cos x$。这说明双曲函数实际上是三角函数在虚数轴上的"旋转"，两套恒等式通过复数分析在更高层次上统一。这一联系也解释了奥斯本规则中符号变化的深层原因：每出现两个 $\sinh$ 相乘，就产生一个 $i^2 = -1$ 的因子，使符号翻转。
