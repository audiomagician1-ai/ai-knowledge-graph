---
id: "lagrangian-mechanics"
concept: "拉格朗日力学初步"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 拉格朗日力学初步

## 概述

拉格朗日力学是由约瑟夫-路易·拉格朗日（Joseph-Louis Lagrange）于1788年在其著作《分析力学》（*Mécanique Analytique*）中系统建立的经典力学表述体系。它将牛顿力学的矢量方程转化为基于能量的标量方程，核心工具是拉格朗日量 $L = T - V$，其中 $T$ 是系统动能，$V$ 是系统势能。

与牛顿力学不同，拉格朗日力学不需要分析每个约束力（如绳子张力、法向力），只需选取合适的广义坐标，用能量函数描述系统。这一特点使得处理具有多个约束条件的复杂系统时，方程数量可以从3N个（N个质点各有x、y、z分量）缩减到等于系统自由度的数目。例如，一个受约束在球面上运动的质点只需要两个广义坐标（$\theta$, $\phi$），而非三个笛卡尔坐标加一个约束方程。

## 核心原理

### 广义坐标与自由度

广义坐标 $q_i$（$i = 1, 2, \ldots, n$）是完全确定系统构型所需的最小独立变量集合。系统的自由度数 $n = 3N - k$，其中 $N$ 是质点数，$k$ 是完整约束的数目。广义坐标不必是长度或角度，可以是任何能唯一描述系统状态的量。例如，描述双摆系统需要两个角度 $\theta_1$ 和 $\theta_2$，而非四个笛卡尔坐标（$x_1, y_1, x_2, y_2$）加两个约束方程。广义速度 $\dot{q}_i = \frac{dq_i}{dt}$ 是对应广义坐标的时间导数。

### 哈密顿最小作用量原理

拉格朗日力学的变分基础是哈密顿最小作用量原理：系统从时刻 $t_1$ 到 $t_2$ 的真实运动，使得作用量 $S = \int_{t_1}^{t_2} L(q_i, \dot{q}_i, t)\, dt$ 取极值（通常是极小值）。数学表述为 $\delta S = 0$，其中 $\delta$ 表示在端点固定（$\delta q_i(t_1) = \delta q_i(t_2) = 0$）的条件下对路径作变分。这一原理不依赖于坐标系的选取，因此在任意广义坐标下均成立，这正是其相对于牛顿定律的根本优势。

### 拉格朗日方程的推导与形式

对作用量 $S$ 进行变分并利用端点条件做分部积分，可得到欧拉-拉格朗日方程：

$$\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = 0, \quad i = 1, 2, \ldots, n$$

每个广义坐标 $q_i$ 对应一个这样的方程，系统共有 $n$ 个方程，恰好等于自由度数。项 $\frac{\partial L}{\partial \dot{q}_i}$ 称为广义动量 $p_i$，项 $\frac{\partial L}{\partial q_i}$ 称为广义力。以单摆为例，选取摆角 $\theta$ 为广义坐标，$L = \frac{1}{2}ml^2\dot{\theta}^2 - mgl(1-\cos\theta)$，代入欧拉-拉格朗日方程直接得到 $ml^2\ddot{\theta} + mgl\sin\theta = 0$，即 $\ddot{\theta} + \frac{g}{l}\sin\theta = 0$，全程无需分析绳子张力。

### 循环坐标与守恒量

若拉格朗日量 $L$ 不显含某广义坐标 $q_j$，即 $\frac{\partial L}{\partial q_j} = 0$，则称 $q_j$ 为循环坐标（ignorable coordinate）。由欧拉-拉格朗日方程立即得到 $\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_j}\right) = 0$，即对应广义动量 $p_j = \frac{\partial L}{\partial \dot{q}_j}$ 守恒。例如，中心力场问题中角坐标 $\phi$ 是循环坐标，直接给出角动量守恒，这是诺特定理在拉格朗日框架下最直接的体现。

## 实际应用

**阿特伍德机**：两个质量 $m_1$、$m_2$ 通过轻绳连接绕滑轮运动，系统只有一个自由度。取绳子一端位移 $x$ 为广义坐标，$L = \frac{1}{2}(m_1+m_2)\dot{x}^2 - (m_1 - m_2)gx$，代入拉格朗日方程得加速度 $a = \frac{(m_1-m_2)g}{m_1+m_2}$，整个推导无需计算绳中张力。

**球面摆**：质量 $m$ 的质点约束在半径 $l$ 的球面上，自由度为2，广义坐标取极角 $\theta$ 和方位角 $\phi$。拉格朗日量为 $L = \frac{1}{2}ml^2(\dot{\theta}^2 + \sin^2\theta\, \dot{\phi}^2) + mgl\cos\theta$。由于 $\phi$ 是循环坐标，广义动量 $p_\phi = ml^2\sin^2\theta\,\dot{\phi}$（即绕竖轴的角动量）守恒，这一结论在牛顿力学框架下需要额外推导。

**弹簧耦合振子**：两个质量均为 $m$ 的小球由三根弹簧连接（弹簧常数分别为 $k$, $K$, $k$），两个广义坐标 $q_1$, $q_2$ 描述两球位移，拉格朗日方程给出耦合方程组，通过正则坐标变换可解耦为两个简正模。这类问题若用牛顿力学处理，矩阵化程度相同，但广义坐标的选取可以显著简化方程形式。

## 常见误区

**误区一：认为拉格朗日力学只适用于保守系统**。拉格朗日方程的标准形式 $\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0$ 确实要求所有力均可由势函数导出，但对于非保守力（如摩擦力），可在方程右侧引入广义力 $Q_i = \sum_j \mathbf{F}_j^{(\text{nc})} \cdot \frac{\partial \mathbf{r}_j}{\partial q_i}$，从而推广为 $\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = Q_i$。

**误区二：将拉格朗日量 $L = T - V$ 中的减号误认为是 $T + V$**。能量守恒给出的总能量是 $E = T + V$，而拉格朗日量是 $T - V$，两者符号相反。混淆这一点会导致方程符号全部出错。单摆的正确拉格朗日量中势能项为 $-mgl\cos\theta$（取悬挂点为零势能面时取负号），若写成 $T + V$ 则推导出的摆方程符号将与实验矛盾。

**误区三：认为广义坐标的数量等于质点数**。广义坐标数等于系统**自由度数**，不等于质点数。一个由两个质点构成、受到一个完整约束的系统，自由度为 $3 \times 2 - 1 = 5$，需要5个广义坐标而非2个或6个。

## 知识关联

**与能量守恒的联系**：拉格朗日量 $L = T - V$ 直接建立在动能 $T$ 和势能 $V$ 的基础上。若 $L$ 不显含时间 $t$，即 $\frac{\partial L}{\partial t} = 0$，则广义能量函数（哈密顿量）$H = \sum_i p_i\dot{q}_i - L$ 守恒，这正是能量守恒定律在拉格朗日框架下的精确表述。

**与牛顿第二定律的等价性**：对于笛卡尔坐标下无约束的单质点，将 $L = \frac{1}{2}m(\dot{x}^2+\dot{y}^2+\dot{z}^2) - V(x,y,z)$ 代入欧拉-拉格朗日方程，可以直接推导出 $m\ddot{x} = -\frac{\partial V}{\partial x}$ 等，即牛顿第二定律。两者在无约束保守系统中完全等价，拉格朗日力学的优势仅在有约束时才完全显现。

**通向哈密顿力学**：通过勒让德变换 $H(q_i, p_i, t) = \sum_i p_i\dot{q}_i - L$，将广义速度 $\dot{q}_i$ 替换为广义动量 $p_i = \frac{\partial L}{\partial \dot{q}_i}$，可以从拉格朗日框架过渡到哈密顿框架，得到一阶的哈密