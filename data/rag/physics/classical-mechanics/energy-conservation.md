---
id: "energy-conservation"
concept: "能量守恒"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 4
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 90.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.90
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Fundamentals of Physics (12th ed.)"
    author: "Halliday, Resnick & Walker"
    isbn: "978-1119773511"
  - type: "textbook"
    title: "The Feynman Lectures on Physics, Vol. I"
    author: "Richard P. Feynman"
    isbn: "978-0465024933"
  - type: "textbook"
    title: "Classical Mechanics (5th ed.)"
    author: "Tom W.B. Kibble, Frank H. Berkshire"
    isbn: "978-1860944352"
scorer_version: "scorer-v2.0"
---
# 能量守恒

## 概述

Richard Feynman 曾写道："有一个事实——如果你愿意，可以称之为一条定律——统治着已知的所有自然现象……那就是能量守恒。它说的是存在一个我们称为能量的量，在自然界发生的各种变化中，它的总量不变。"（Feynman Lectures, Vol. I, Ch.4）。能量守恒是物理学中最深刻、最普适的原理之一，从经典力学到量子场论，从化学反应到宇宙演化，它从未被违反过。

## 核心知识点

### 1. 功与动能定理

能量守恒的基础始于**功**的定义。力 $\vec{F}$ 对物体沿路径做的功为：

$W = \int \vec{F} \cdot d\vec{s}$

**功-动能定理（Work-Energy Theorem）**：合外力做的功等于物体动能的变化：

$W_{net} = \Delta K = \frac{1}{2}mv_f^2 - \frac{1}{2}mv_i^2$

这个定理是牛顿第二定律的直接推论（对 $F=ma$ 沿路径积分即得），但它将矢量问题转化为标量问题，大大简化了力学分析。

### 2. 保守力与势能

一个力是**保守力**，当且仅当它做的功只取决于起点和终点，而与路径无关。等价条件是沿任意闭合路径做功为零：$\oint \vec{F} \cdot d\vec{s} = 0$。

常见的保守力与对应势能：

| 保守力 | 势能函数 | 说明 |
|--------|---------|------|
| 重力（近地面） | $U = mgh$ | h 为相对参考面的高度 |
| 万有引力 | $U = -GMm/r$ | r 为质心距离 |
| 弹性力 | $U = \frac{1}{2}kx^2$ | x 为形变量 |
| 库仑力 | $U = kq_1q_2/r$ | r 为电荷间距 |

非保守力（如摩擦力、空气阻力）做的功取决于路径，无法定义势能函数。

### 3. 机械能守恒定律

在只有保守力做功的系统中，动能 K 与势能 U 之和（机械能 E）保持不变：

$E = K + U = \text{const}$

即 $\frac{1}{2}mv_1^2 + U_1 = \frac{1}{2}mv_2^2 + U_2$

**应用实例**：一个质量 0.5 kg 的球从 2 m 高处自由下落（忽略空气阻力）。初态：$K_1 = 0$, $U_1 = mgh = 0.5 \times 9.81 \times 2 = 9.81$ J。末态（着地）：$U_2 = 0$，所以 $K_2 = 9.81$ J，得 $v = \sqrt{2K/m} = \sqrt{2 \times 9.81 / 0.5} = 6.26$ m/s。

> 思考题：同样的球沿光滑斜面滑下 2 m 垂直高度，到底时速度是否相同？为什么？

### 4. 非保守力与能量耗散

现实中摩擦力等非保守力普遍存在。此时机械能不守恒，但总能量守恒——机械能的减少量等于内能（热能）的增加量：

$\Delta K + \Delta U + \Delta E_{thermal} = 0$

或者写成更一般的形式：$W_{non-conservative} = \Delta E_{mechanical}$

例如，一个 2 kg 的木块从 3 m 高的粗糙斜面滑下，到达底部时速度仅为 5 m/s（而非理想情况下的 7.67 m/s）。摩擦力将 $mgh - \frac{1}{2}mv^2 = 58.86 - 25 = 33.86$ J 的机械能转化为热能。

### 5. 能量守恒的深层基础：诺特定理

1918年，数学家 Emmy Noether 证明了一个深刻的定理：**每一个连续对称性都对应一个守恒量**。能量守恒对应的是**时间平移对称性**——物理定律在不同时刻具有相同的形式。

| 对称性 | 守恒量 |
|--------|--------|
| 时间平移 | 能量 |
| 空间平移 | 动量 |
| 空间旋转 | 角动量 |

这意味着能量守恒不是一条独立的经验规律，而是自然界时间平移不变性的必然结果。如果某天发现能量不守恒了，那就意味着物理定律本身随时间在改变。

### 6. 能量守恒的普适性

能量守恒远超经典力学的范围：

- **热力学第一定律**：$\Delta U = Q - W$，系统内能变化等于吸收的热量减去对外做的功。能量守恒是热力学的基石。
- **质能等价**：爱因斯坦的 $E = mc^2$ 揭示质量是能量的一种形式。核裂变中铀-235 的质量亏损 0.09%，释放约 200 MeV/核。
- **粒子物理**：每一次粒子碰撞和衰变都严格遵守能量守恒（包括质能等价），这是发现中微子的关键线索——1930年泡利正是因为 beta 衰变中能量"缺失"而提出中微子假说。

## 关键要点

1. **功-动能定理** $W_{net} = \Delta K$ 将力的矢量问题转化为标量能量问题
2. 保守力做功与路径无关，可定义势能；**机械能守恒**要求只有保守力做功
3. 非保守力（摩擦等）将机械能转化为热能，但**总能量仍守恒**
4. 能量守恒的深层基础是**时间平移对称性**（诺特定理，1918）
5. 从力学到热力学到 $E=mc^2$，能量守恒从未被违反

## 常见误区

1. **"摩擦力违反了能量守恒"**：错。摩擦力违反的是机械能守恒，但总能量（机械能+热能）仍然守恒。没有任何已知过程违反总能量守恒。
2. **混淆"能量守恒"与"机械能守恒"**：机械能守恒是能量守恒在无非保守力条件下的特例。很多学生在有摩擦力的题目中错误使用机械能守恒。
3. **"势能是物体自身的属性"**：势能属于系统而非单个物体。说"球具有 mgh 的势能"实际上是"球-地球系统的引力势能为 mgh"的简写。
4. **选错势能零点**：势能零点的选择是任意的，但在同一问题中必须保持一致。很多错误源于中途更换参考面。

## 知识衔接

### 先修知识
- **势能** — 保守力与势能函数的概念是理解机械能守恒的前提
- **牛顿第二定律** — 功-动能定理是 F=ma 沿路径积分的直接结果

### 后续学习
- **碰撞** — 弹性碰撞同时守恒动能和动量，非弹性碰撞中动能转化为内能
- **万有引力** — 引力势能 $U = -GMm/r$ 及逃逸速度推导
- **简谐运动** — 弹性势能与动能的周期性互相转化
- **热力学第一定律** — 能量守恒推广到热系统

## 参考文献

1. Feynman, R.P. (1963). *The Feynman Lectures on Physics*, Vol. I, Ch.4: Conservation of Energy. ISBN 978-0465024933.
2. Halliday, D., Resnick, R. & Walker, J. (2021). *Fundamentals of Physics* (12th ed.), Ch.7-8. Wiley. ISBN 978-1119773511.
3. Noether, E. (1918). Invariante Variationsprobleme. *Nachrichten von der Gesellschaft der Wissenschaften zu Goettingen*, 235-257.
4. Kibble, T.W.B. & Berkshire, F.H. (2004). *Classical Mechanics* (5th ed.). Imperial College Press. ISBN 978-1860944352.
