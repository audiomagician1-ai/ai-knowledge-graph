---
id: "trig-identities"
concept: "三角恒等式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 5
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 三角恒等式

## 概述

三角恒等式是指对所有使表达式有意义的角度值均成立的三角函数等式。与三角方程不同，恒等式不需要"求解"某个特定角——无论将任何允许的角度代入，等号两侧始终相等。最基础的三角恒等式直接来自单位圆上点坐标的定义：若角 θ 对应单位圆上的点 (x, y)，则 cos θ = x，sin θ = y，而 tan θ = y/x（x ≠ 0）。

三角恒等式的系统化整理可追溯至古希腊天文学家希帕克斯（约公元前190—120年），他为计算弦长建立了早期的三角关系表。9世纪阿拉伯数学家花拉子米及其后继者将这些关系整理为正弦、余弦的明确等式，并发现了更多变换规律。欧拉在18世纪通过复指数公式 $e^{i\theta} = \cos\theta + i\sin\theta$ 将所有三角恒等式统一在一个代数框架下，使证明变得系统而简洁。

理解三角恒等式的实用价值在于：它们是化简复杂三角表达式、求解三角方程、推导积分公式的核心工具。例如，没有毕达哥拉斯恒等式，就无法完成 $\int \cos^2\theta\, d\theta$ 的化简；没有商数恒等式，正切函数的许多性质将无从推导。

---

## 核心原理

### 商数恒等式与倒数恒等式

最基础的一组恒等式来自六个三角函数之间的定义关系：

$$\tan\theta = \frac{\sin\theta}{\cos\theta}, \quad \cot\theta = \frac{\cos\theta}{\sin\theta}$$

$$\sec\theta = \frac{1}{\cos\theta}, \quad \csc\theta = \frac{1}{\sin\theta}, \quad \cot\theta = \frac{1}{\tan\theta}$$

这六个等式称为**商数恒等式**和**倒数恒等式**。它们直接由单位圆定义导出，本质上是"重新命名"的定义，而非独立发现的规律。正因如此，它们是所有其他恒等式推导的出发点。注意 sec θ 和 csc θ 在中学课程中常被忽略，但在微积分中频繁出现。

### 毕达哥拉斯恒等式

毕达哥拉斯恒等式是三角恒等式中地位最特殊的一组，共有三个，全部来自勾股定理应用于单位圆：

**第一恒等式（基本型）：**
$$\sin^2\theta + \cos^2\theta = 1$$

证明：单位圆上的点满足 $x^2 + y^2 = 1$，将 $x = \cos\theta$，$y = \sin\theta$ 代入即得。

**第二恒等式（除以 $\cos^2\theta$）：**
$$\tan^2\theta + 1 = \sec^2\theta \quad (\cos\theta \neq 0)$$

**第三恒等式（除以 $\sin^2\theta$）：**
$$1 + \cot^2\theta = \csc^2\theta \quad (\sin\theta \neq 0)$$

三个恒等式本质上是同一个几何事实的三种代数变形，但在具体化简中各有用武之地：第二型常用于含 $\tan\theta$ 的积分换元，第三型常用于含 $\cot\theta$ 的化简。

### 奇偶性恒等式与余角恒等式

奇偶性恒等式描述了三角函数对负角的响应方式：

$$\sin(-\theta) = -\sin\theta \quad (\text{正弦为奇函数})$$
$$\cos(-\theta) = \cos\theta \quad (\text{余弦为偶函数})$$
$$\tan(-\theta) = -\tan\theta \quad (\text{正切为奇函数})$$

余角恒等式描述了 $\theta$ 与 $\frac{\pi}{2} - \theta$ 之间的关系，其中"余弦"（cosine）的命名正来源于此：

$$\sin\left(\frac{\pi}{2} - \theta\right) = \cos\theta, \quad \cos\left(\frac{\pi}{2} - \theta\right) = \sin\theta$$

这意味着正弦与余弦互为"余函数"（co-function），正切与余切同理。余角恒等式是将和差公式（下一阶段内容）应用于特殊角 $\frac{\pi}{2}$ 的特例。

---

## 实际应用

**化简三角表达式：** 给定表达式 $\frac{\sin^2\theta}{1 - \cos\theta}$，利用毕达哥拉斯恒等式 $\sin^2\theta = 1 - \cos^2\theta = (1-\cos\theta)(1+\cos\theta)$，可直接约分得到 $1 + \cos\theta$。此类因式分解技巧在高中及大学入学考试中高频出现。

**验证恒等式的方法：** 证明 $\sec^2\theta - \tan^2\theta = 1$ 时，将左侧写成 $\frac{1}{\cos^2\theta} - \frac{\sin^2\theta}{\cos^2\theta} = \frac{1 - \sin^2\theta}{\cos^2\theta} = \frac{\cos^2\theta}{\cos^2\theta} = 1$。标准做法是只变形一侧，使其等于另一侧，而非同时对两侧操作。

**三角代换积分：** 在计算 $\int \sqrt{1-x^2}\, dx$ 时，令 $x = \sin\theta$，利用 $1 - \sin^2\theta = \cos^2\theta$ 将根号消去，被积函数变为 $\cos^2\theta$，再用半角公式（本质上也是三角恒等式的推论）完成积分。

---

## 常见误区

**误区一：混淆恒等式与方程。** 学生常将 $\sin^2\theta + \cos^2\theta = 1$ 当作方程去"求解 θ"，但这个等式对任意实数 θ 均成立，没有需要求解的未知量。真正的三角方程如 $2\sin\theta - 1 = 0$ 才需要在某个区间内寻找特定解。

**误区二：误写毕达哥拉斯恒等式的变形。** 由 $\sin^2\theta + \cos^2\theta = 1$ 变形时，常见错误是将 $\sin^2\theta = 1 - \cos^2\theta$ 错写为 $\sin\theta = 1 - \cos\theta$（漏掉平方）。两者含义完全不同：前者是恒等式，后者是仅在特定 θ 值成立的条件等式。

**误区三：认为"证明恒等式"可以交叉相乘。** 若要证明 $A = B$，先假设 $A = B$ 再推导出已知成立的结论，这是循环论证，在数学上不合法。正确做法是从单侧出发，通过已知恒等式对其变形，最终化简为另一侧的形式。

---

## 知识关联

**前置知识——单位圆：** 三角恒等式中的每一个等式，包括 $\sin^2\theta + \cos^2\theta = 1$ 以及所有余角、奇偶性关系，都是单位圆几何性质的代数表达。没有单位圆定义，三角函数只是抽象符号，恒等式的几何意义将无法理解。

**后续——和差化积公式：** 和差公式如 $\sin(\alpha \pm \beta) = \sin\alpha\cos\beta \pm \cos\alpha\sin\beta$ 并非独立于本页内容——它们的推导过程依赖毕达哥拉斯恒等式和奇偶性恒等式，而倍角公式、半角公式又是和差公式的直接推论，形成一条逻辑链。

**后续——双曲函数：** 双曲正弦 $\sinh x = \frac{e^x - e^{-x}}{2}$ 和双曲余弦 $\cosh x = \frac{e^x + e^{-x}}{2}$ 满足类比恒等式 $\cosh^2 x - \sinh^2 x = 1$，与毕达哥拉斯恒等式 $\cos^2\theta + \sin^2\theta = 1$ 结构相同但符号相异，这一差异来源于单位双曲线 $x^2 - y^2 = 1$ 替代了单位圆 $x^2 + y^2 = 1$。
