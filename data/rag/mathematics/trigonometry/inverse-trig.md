---
id: "inverse-trig"
concept: "反三角函数"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 反三角函数

## 概述

反三角函数是三角函数在限制定义域后的逆函数，用于从已知三角函数值反推出对应角度。由于 sin、cos、tan 本身是周期函数，不具备全局可逆性，必须将其定义域限制在特定区间内才能构造反函数。三个最常用的反三角函数分别为反正弦函数 arcsin、反余弦函数 arccos 和反正切函数 arctan。

"arc"前缀来源于拉丁语"arcus"（弧），意指"对应弧度的角"。历史上，莱布尼茨在17世纪末已使用类似符号，但现代 arcsin 等记法在18世纪由欧拉和他的同时代数学家逐步规范化。在工程计算、物理分析（如求入射角、相位角）及计算机图形学中，反三角函数是将"已知比值求角度"这一任务的标准工具。

## 核心原理

### 定义域与值域的严格规定

三个反三角函数的定义域和值域各不相同，必须精确记忆：

| 函数 | 定义域 | 值域 |
|------|--------|------|
| arcsin x | $[-1,\ 1]$ | $\left[-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right]$ |
| arccos x | $[-1,\ 1]$ | $\left[0,\ \pi\right]$ |
| arctan x | $(-\infty,\ +\infty)$ | $\left(-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right)$ |

arcsin 和 arccos 的定义域受到正弦、余弦值域 $[-1,1]$ 的限制，而 arctan 的定义域为全体实数，因为正切函数可取任意实数值。arctan 的值域是开区间，$\pm\dfrac{\pi}{2}$ 不可达，这与正切函数在这两点处无定义直接对应。

### 主值区间的选取逻辑

选取主值区间并非任意，而是有明确依据：
- **arcsin** 的主值区间 $\left[-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right]$ 对应正弦函数单调递增的一段，保证了从 $-1$ 到 $1$ 的一一对应。
- **arccos** 的主值区间 $[0,\ \pi]$ 对应余弦函数单调递减的一段。注意，arccos 的值域不含负角，这与 arcsin 形成明显差异。
- **arctan** 的主值区间 $\left(-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right)$ 对应正切函数在第一、四象限单调递增的一段。

一个关键结论：$\arcsin x + \arccos x = \dfrac{\pi}{2}$，对所有 $x \in [-1,1]$ 成立。这一恒等式由 arcsin 和 arccos 的主值区间互补得出，可用于化简表达式。

### 反三角函数与三角函数的复合

复合运算需区分两种方向，结果差异显著：

**先取反三角，再取三角**（结果直接还原）：
$$\sin(\arcsin x) = x, \quad x \in [-1, 1]$$
$$\cos(\arccos x) = x, \quad x \in [-1, 1]$$
$$\tan(\arctan x) = x, \quad x \in \mathbb{R}$$

**先取三角，再取反三角**（结果受主值区间约束）：
$$\arcsin(\sin\theta) = \theta \iff \theta \in \left[-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right]$$

若 $\theta$ 不在主值区间内，则需先将 $\theta$ 化为等价角再处理。例如：
$$\arcsin\!\left(\sin\dfrac{2\pi}{3}\right) = \arcsin\!\left(\dfrac{\sqrt{3}}{2}\right) = \dfrac{\pi}{3} \neq \dfrac{2\pi}{3}$$

这是因为 $\dfrac{2\pi}{3}$ 不在 arcsin 的值域 $\left[-\dfrac{\pi}{2},\ \dfrac{\pi}{2}\right]$ 内，而 $\sin\dfrac{2\pi}{3} = \sin\dfrac{\pi}{3}$，最终结果为 $\dfrac{\pi}{3}$。

## 实际应用

**求直角三角形的角度**：已知斜边为 5、对边为 3，则该角 $\theta = \arcsin\!\left(\dfrac{3}{5}\right) \approx 36.87°$。这是 arcsin 最直接的几何应用场景。

**物理中的折射角计算**：斯涅尔定律 $n_1 \sin\theta_1 = n_2 \sin\theta_2$ 中，若已知 $n_1, n_2, \theta_1$，则折射角 $\theta_2 = \arcsin\!\left(\dfrac{n_1 \sin\theta_1}{n_2}\right)$，arcsin 使角度的求解成为显式公式。

**计算机图形学中的向量夹角**：两个单位向量 $\vec{a},\vec{b}$ 的夹角通过 $\theta = \arccos(\vec{a} \cdot \vec{b})$ 计算，值域 $[0,\pi]$ 恰好覆盖向量夹角的全部可能范围，不会产生歧义。

**arctan 的双参数变体**：编程语言中的 `atan2(y, x)` 函数利用 arctan 原理，通过判断象限将值域扩展至 $(-\pi, \pi]$，解决了单参数 arctan 无法区分第二、三象限角度的缺陷。

## 常见误区

**误区一：混淆 arcsin 与 arccos 的值域范围**  
arcsin 的值域包含负值（最小为 $-\dfrac{\pi}{2}$），而 arccos 的值域全为非负值（最小为 $0$）。因此 $\arccos(-1) = \pi$，而 $\arcsin(-1) = -\dfrac{\pi}{2}$，两者截然不同。很多学生将 arccos 的值域误记为 $\left[-\dfrac{\pi}{2}, \dfrac{\pi}{2}\right]$，导致计算结果符号出错。

**误区二：认为 $\arcsin(\sin\theta) = \theta$ 普遍成立**  
该等式仅在 $\theta \in \left[-\dfrac{\pi}{2}, \dfrac{\pi}{2}\right]$ 时成立。对 $\theta = \pi$，$\arcsin(\sin\pi) = \arcsin(0) = 0 \neq \pi$。忽略主值区间的限制是反三角函数计算中最频繁出现的错误类型。

**误区三：将 $\arcsin x$ 写成 $\sin^{-1} x$ 时误解为倒数**  
部分教材（尤其是英文教材）使用 $\sin^{-1} x$ 表示 arcsin，但这里的 $-1$ 是函数逆的符号，不代表 $\dfrac{1}{\sin x}$。后者是余割函数 $\csc x$。两种记法并存容易造成混淆，在混用中英文资料时需特别注意。

## 知识关联

**前置概念**：学习反三角函数前，需要熟悉正弦、余弦、正切函数的图像，特别是各自的单调区间。arcsin 对应 sin 在 $\left[-\dfrac{\pi}{2}, \dfrac{\pi}{2}\right]$ 上的图像关于直线 $y=x$ 的对称图形；arccos 对应 cos 在 $[0,\pi]$ 上的图像的对称图形；arctan 则对应 tan 在 $\left(-\dfrac{\pi}{2}, \dfrac{\pi}{2}\right)$ 上图像的对称图形，且有两条水平渐近线 $y = \pm\dfrac{\pi}{2}$。

**后续概念**：在三角方程的求解中，反三角函数提供方程的一个特解（主值解），而通解则需要在主值基础上加上周期项。例如，方程 $\sin x = a$（$|a| \leq 1$）的通解为 $x = (-1)^k \arcsin a + k\pi$（$k \in \mathbb{Z}$），其中 arcsin $a$ 正是通解的起点。理解主值区间的位置，是从反三角函数过渡到三角方程通解写法的关键步骤。