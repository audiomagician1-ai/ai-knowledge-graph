---
id: "newtons-second-law"
concept: "牛顿第二定律"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 3
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 94.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Fundamentals of Physics (12th ed.)"
    author: "Halliday, Resnick & Walker"
    isbn: "978-1119773511"
  - type: "textbook"
    title: "An Introduction to Mechanics (2nd ed.)"
    author: "Daniel Kleppner, Robert Kolenkow"
    isbn: "978-0521198110"
  - type: "historical"
    title: "Philosophiae Naturalis Principia Mathematica"
    author: "Isaac Newton"
    year: 1687
scorer_version: "scorer-v2.0"
---
# 牛顿第二定律

## 概述

牛顿第二定律是经典力学的核心定律，建立了力、质量和加速度之间的定量关系。1687年，牛顿在《自然哲学的数学原理》中将其表述为"运动的变化正比于所施加的力，变化的方向沿该力的直线方向"（Principia, Axioms, Law II）。现代形式 $\vec{F} = m\vec{a}$ 看似简单，但它是一个微分方程——给定力和初始条件，原则上可以预测任何宏观物体在任何时刻的运动状态。从抛体运动到行星轨道，从弹簧振子到火箭推进，整个经典力学的定量预测都从这个方程出发。

## 核心知识点

### 1. $\vec{F} = m\vec{a}$ 的精确含义

**标量形式**：$F_{net} = ma$，作用在物体上的合外力等于质量乘以加速度。

**矢量形式**：$\vec{F}_{net} = m\vec{a}$，力和加速度是矢量，方向相同。在直角坐标系中分解为三个独立方程：

$$\sum F_x = ma_x, \quad \sum F_y = ma_y, \quad \sum F_z = ma_z$$

**更一般的形式（动量形式）**：牛顿原始表述更接近动量变化率的形式：

$$\vec{F}_{net} = \frac{d\vec{p}}{dt} = \frac{d(m\vec{v})}{dt}$$

当质量恒定时简化为 $\vec{F} = m\vec{a}$；当质量变化时（例如火箭喷射燃料），必须使用动量形式。

关键概念辨析：
- **$\vec{F}$ 是合外力**：不是单个力，而是作用在物体上所有力的矢量和
- **$m$ 是惯性质量**：衡量物体抵抗加速度的能力，是标量，始终为正
- **$\vec{a}$ 是瞬时加速度**：$\vec{a} = d\vec{v}/dt = d^2\vec{r}/dt^2$，是速度对时间的变化率

### 2. 自由体图（Free Body Diagram）

自由体图是应用牛顿第二定律的**系统方法**——将物体隔离出来，画出作用在它上面的所有力：

例如，一个质量 $m = 5$ kg 的木块放在倾角 $\theta = 30°$ 的斜面上（无摩擦）：

**受力分析**：
- 重力 $\vec{W} = mg = 49.05$ N（竖直向下）
- 法向力 $\vec{N}$（垂直斜面向上）

**分解坐标**（沿斜面 x 轴、垂直斜面 y 轴）：
- x 方向：$mg\sin\theta = ma_x$ → $a_x = g\sin 30° = 4.905$ m/s²
- y 方向：$N - mg\cos\theta = 0$ → $N = mg\cos 30° = 42.48$ N

> 思考题：如果斜面有摩擦系数 $\mu_k = 0.2$，加速度变为多少？（答案：$a = g(\sin\theta - \mu_k\cos\theta) = 3.21$ m/s²）

### 3. 力的叠加原理

多个力同时作用于一个物体时，每个力独立产生效果，合力等于各力的矢量和：

$$\vec{F}_{net} = \vec{F}_1 + \vec{F}_2 + \cdots + \vec{F}_n = \sum_{i=1}^{n} \vec{F}_i$$

这意味着：
- 力可以按坐标轴分解并独立求和
- 水平和竖直方向的运动可以独立分析（例如抛体运动）
- 叠加原理是线性的——这正是 $F=ma$ 作为线性方程的体现

### 4. 常见力的类型与量级

| 力的类型 | 符号 | 公式 | 典型量级 |
|---------|------|------|---------|
| 重力（近地面） | $\vec{W}$ | $mg$, $g = 9.81$ m/s² | 1 kg 物体约 9.8 N |
| 法向力 | $\vec{N}$ | 由约束决定 | 等于压力的反力 |
| 摩擦力（动） | $\vec{f}_k$ | $\mu_k N$ | $\mu_k$ 通常 0.1-1.0 |
| 弹性力 | $\vec{F}_s$ | $-kx$（胡克定律） | 取决于弹簧常数 |
| 张力 | $\vec{T}$ | 由约束决定 | 绳子/弦中的拉力 |
| 空气阻力 | $\vec{F}_d$ | $\frac{1}{2}C_d \rho A v^2$ | 低速时可忽略 |

### 5. 经典应用场景

**阿特伍德机（Atwood Machine）**：两个质量 $m_1$ 和 $m_2$（$m_1 > m_2$）通过轻绳挂在无摩擦滑轮两侧。对每个物体列方程：
- $m_1$：$m_1 g - T = m_1 a$
- $m_2$：$T - m_2 g = m_2 a$

联立解得：$a = \frac{(m_1 - m_2)g}{m_1 + m_2}$，$T = \frac{2m_1 m_2 g}{m_1 + m_2}$

例如 $m_1 = 3$ kg，$m_2 = 2$ kg 时，$a = 1.96$ m/s²，$T = 23.52$ N。

**终端速度**：自由落体时，空气阻力 $F_d = \frac{1}{2}C_d\rho Av^2$ 随速度增大。当 $F_d = mg$ 时加速度为零，物体以恒定的**终端速度**下降。跳伞运动员（展开姿势）的终端速度约 55 m/s ≈ 200 km/h。

### 6. 适用范围与局限

牛顿第二定律在以下条件下成立：
- **惯性参考系**：观察者处于不加速的参考系中。在非惯性系中需要引入惯性力（如科里奥利力、离心力）
- **低速**：物体速度远小于光速 $c$（$v \ll 3 \times 10^8$ m/s）。高速情况下需要相对论修正：$\vec{F} = \frac{d}{dt}(\gamma m\vec{v})$
- **宏观尺度**：适用于日常尺度的物体。在原子尺度需要量子力学
- **经典极限下精确**：在上述条件下，牛顿第二定律的预测精度极高。NASA 用它规划行星际探测器的轨道，精度优于 km 级

## 关键要点

1. $\vec{F}_{net} = m\vec{a}$ 将力（原因）与加速度（运动变化）定量联系，是经典力学的预测核心
2. 动量形式 $\vec{F} = d\vec{p}/dt$ 更一般，适用于变质量系统（火箭）
3. 自由体图是系统化解题的必要步骤：隔离物体→画全力→建坐标→列方程
4. 力的叠加原理：合力 = 各力矢量和，允许独立分解各方向
5. 适用条件：惯性参考系 + 低速 + 宏观尺度

## 常见误区

1. **"$F=ma$ 中的 F 是物体受到的最大力"**：$F$ 是合外力（所有力的矢量和），不是任何单个力。一个被推着匀速运动的物体合力为零（推力 = 摩擦力），加速度为零。
2. **"重的物体下落更快"**：在真空中所有物体自由落体加速度相同（$a=g$）。伽利略的比萨斜塔实验（虽然可能是传说）和阿波罗 15 号在月球上的锤子-羽毛实验都证明了这一点。差异来源于空气阻力，与质量无关。
3. **"力是维持运动的原因"**：这是亚里士多德的观点，已被牛顿第一定律否定。力改变运动状态（产生加速度），不维持运动。
4. **在非惯性系中直接用 $F=ma$**：在加速电梯中，需要引入惯性力（伪力）。否则会发现"力不平衡但物体静止"的矛盾。
5. **混淆质量与重量**：质量 $m$（kg）是惯性属性，在任何地方不变；重量 $W = mg$（N）是力，取决于当地重力加速度。宇航员在月球上质量不变但重量只有地球的 1/6。

## 历史脉络

| 年份 | 事件 | 意义 |
|------|------|------|
| ~350 BC | 亚里士多德"力是运动之因" | 统治西方 2000 年的错误观念 |
| 1638 | 伽利略《两种新科学的对话》 | 惯性概念、自由落体定律 |
| 1687 | 牛顿《原理》发表 | 三大定律+万有引力，经典力学诞生 |
| 1905 | 爱因斯坦狭义相对论 | 高速修正：$F = d(\gamma mv)/dt$ |

## 知识衔接

### 先修知识
- **牛顿第一定律** — 惯性和惯性参考系的概念是第二定律的前提
- **矢量分解** — 力和加速度的矢量分解是解题的数学基础

### 后续学习
- **牛顿第三定律** — 作用力与反作用力，多体问题的基础
- **摩擦力** — 静摩擦和动摩擦的定量分析
- **圆周运动** — 向心加速度 $a_c = v^2/r$ 与向心力
- **功与能** — 对 $F=ma$ 沿路径积分得到功-动能定理
- **动量与冲量** — 对 $F=dp/dt$ 积分得到冲量-动量定理

## 参考文献

1. Newton, I. (1687). *Philosophiae Naturalis Principia Mathematica*. Axioms, Law II.
2. Halliday, D., Resnick, R. & Walker, J. (2021). *Fundamentals of Physics* (12th ed.), Ch.5. Wiley. ISBN 978-1119773511.
3. Kleppner, D. & Kolenkow, R. (2013). *An Introduction to Mechanics* (2nd ed.), Ch.2-3. Cambridge University Press. ISBN 978-0521198110.
4. Feynman, R.P. (1963). *The Feynman Lectures on Physics*, Vol. I, Ch.9: Newton's Laws of Dynamics.
