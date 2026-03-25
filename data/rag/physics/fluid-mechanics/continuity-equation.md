---
id: "continuity-equation"
concept: "连续性方程"
domain: "physics"
subdomain: "fluid-mechanics"
subdomain_name: "流体力学"
difficulty: 4
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 连续性方程

## 概述

连续性方程（Continuity Equation）是流体力学中描述质量守恒定律的数学表达式，它规定在流体流动的任意控制体（control volume）内，单位时间流入的质量等于流出的质量加上控制体内质量的变化率。对于定常流动（steady flow），控制体内的质量不随时间变化，因此流入量严格等于流出量。

该方程的雏形可追溯至18世纪。1752年，莱昂哈德·欧拉（Leonhard Euler）在其流体力学论文中首次将质量守恒原理以微分方程的形式系统化，为连续性方程奠定了理论框架。达朗贝尔（d'Alembert）和拉格朗日（Lagrange）随后对其进行了完善，形成了我们今天所使用的标准形式。

连续性方程之所以重要，在于它是分析管道流量、河道水流分布、心血管血流速率等一切流体问题的必要约束条件。无论是设计自来水管网还是计算飞机机翼附近的气流分布，都必须首先满足连续性方程所规定的质量守恒条件，否则任何流速或压力的计算结果都将失去物理意义。

---

## 核心原理

### 积分形式与微分形式

连续性方程存在两种等价的数学表达形式。

**积分形式**适用于分析有限尺寸的控制体：

$$\frac{\partial}{\partial t}\iiint_V \rho \, dV + \oiint_S \rho \vec{v} \cdot \hat{n} \, dS = 0$$

其中，$\rho$ 为流体密度（kg/m³），$\vec{v}$ 为速度向量（m/s），$\hat{n}$ 为控制面的外法向单位向量，$V$ 为控制体体积，$S$ 为其表面积。第一项表示控制体内总质量随时间的变化率，第二项为通过边界净流出的质量流量。

**微分形式**通过对积分形式应用高斯散度定理推导而来：

$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \vec{v}) = 0$$

展开后写作：

$$\frac{\partial \rho}{\partial t} + \frac{\partial(\rho u)}{\partial x} + \frac{\partial(\rho v)}{\partial y} + \frac{\partial(\rho w)}{\partial z} = 0$$

其中 $u, v, w$ 分别是 $x, y, z$ 方向的速度分量。

### 不可压缩流体的简化

对于不可压缩流体（incompressible fluid），密度 $\rho$ 为常数，$\partial \rho / \partial t = 0$ 且 $\rho$ 可以从散度算子中提出。微分形式随即简化为：

$$\nabla \cdot \vec{v} = 0 \quad \text{即} \quad \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} + \frac{\partial w}{\partial z} = 0$$

这一方程表明，不可压缩流体的速度场是一个**无散场**（divergence-free field）。在实际工程中，液态水在压力变化不超过数十兆帕的条件下均可视为不可压缩流体，体积压缩率约为 $4.6 \times 10^{-10}$ Pa⁻¹，误差可以忽略不计。

### 管流中的截面连续性

对于一维定常管道流动，连续性方程简化为最直观的形式。取管道两个截面1和2，质量流量守恒：

$$\rho_1 A_1 v_1 = \rho_2 A_2 v_2 = \dot{m} = \text{常数}$$

对于不可压缩流体（$\rho_1 = \rho_2$），进一步简化为体积流量守恒：

$$A_1 v_1 = A_2 v_2 = Q$$

这直接说明：管道横截面积 $A$ 越小，流速 $v$ 越大。例如，若管道从截面积 $40\ \text{cm}^2$ 收缩至 $10\ \text{cm}^2$，则流速将增大至原来的 **4倍**。这一结论是喷嘴、文丘里管（Venturi tube）以及消防水枪等装置的设计基础。

---

## 实际应用

**文丘里流量计（Venturi Meter）**：通过在管道中设置收缩段，利用连续性方程确定收缩段与宽管段的流速之比，再结合伯努利方程测量两处的压差，即可反算管道中的体积流量 $Q$。文丘里管的收缩比通常为 $d_2/d_1 = 0.3 \sim 0.75$，精度可达 ±0.5%至 ±1.5%。

**河流水文分析**：水文工程师利用连续性方程分析河道分叉处的流量分配。若一条河流在某处分成两条支流，截面积分别为 $A_1$ 和 $A_2$，通过测量各截面的平均流速即可验证质量守恒，从而评估分洪工程的设计合理性。

**心脏超声多普勒检测**：在医学超声心动图中，医生通过连续性方程计算心脏主动脉瓣的有效瓣口面积（Effective Orifice Area, EOA）。利用 $A_1 v_1 = A_2 v_2$，分别测量左心室流出道面积与流速，以及主动脉瓣口流速，便可诊断主动脉瓣狭窄程度（正常 EOA > 2.0 cm²，重度狭窄 < 1.0 cm²）。

---

## 常见误区

**误区一：认为"流速相等则质量守恒"。**
连续性方程要求守恒的是**质量流量** $\rho A v$，而非流速本身。对于可压缩流体（如高速气体），即便截面积不变，密度发生变化时流速也必须相应改变以保证质量守恒。忽视密度项直接套用 $A_1v_1 = A_2v_2$ 会在马赫数大于 0.3 的气体流动中引入显著误差。

**误区二：将连续性方程与定常流动绑定。**
连续性方程本身适用于**非定常流动**（unsteady flow）。积分形式中的 $\partial \rho / \partial t$ 项正是用于处理密度随时间变化的情况。误以为该方程只能用于定常流动，会导致在分析水锤效应（water hammer）、脉动血流等非定常问题时错误地忽略时间项。

**误区三：混淆"不可压缩"与"密度均匀"。**
"不可压缩"意味着流体微团在运动过程中密度不随时间变化，即 $D\rho/Dt = 0$（随体导数为零）。但两种不同密度的不可压缩流体（如盐水与淡水）分层流动时，空间中不同位置的密度 $\rho(x,y,z)$ 仍可以不同——此时微分形式仍为 $\nabla \cdot \vec{v} = 0$，而非 $\rho = \text{常数到处成立}$。

---

## 知识关联

**前置概念——流体静力学**：流体静力学建立了压强与深度的关系（$\Delta p = \rho g h$），引入了密度、压力等基本物理量的定义。连续性方程在此基础上进一步讨论流体**运动**时这些量如何满足质量守恒，是从静到动的关键跨越。

**后续概念——伯努利方程**：伯努利方程（Bernoulli's equation）描述流体沿流线的能量守恒：$p + \frac{1}{2}\rho v^2 + \rho gh = \text{常数}$。在实际求解管道流动问题时，连续性方程与伯努利方程必须**联立使用**——连续性方程提供截面流速之比（$v_2/v_1 = A_1/A_2$），伯努利方程则建立压强与流速的定量关系，两者缺一不可。

**后续概念——理想流体流动**：理想流体流动理论（无黏、不可压缩）以连续性方程 $\nabla \cdot \vec{v} = 0$ 为约束，结合无旋条件 $\nabla \times \vec{v} = 0$，引出速度势函数 $\phi$ 和流函数 $\psi$ 的概念，最终导向拉普拉斯方程 $\nabla^2 \phi = 0$ 的求解体系——这一体系是翼型绕流、源汇叠加等势流理论的完整框架。