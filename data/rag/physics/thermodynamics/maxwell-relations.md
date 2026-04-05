---
id: "maxwell-relations"
concept: "麦克斯韦关系"
domain: "physics"
subdomain: "thermodynamics"
subdomain_name: "热力学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 麦克斯韦关系

## 概述

麦克斯韦关系（Maxwell Relations）是热力学中四个关键的偏导数等式，由詹姆斯·克拉克·麦克斯韦于1871年在其著作《热的理论》（*Theory of Heat*）中系统整理提出。这四个关系将熵、温度、压强和体积这四个状态变量的偏导数联系起来，其根本来源是热力学势函数（内能、焓、亥姆霍兹自由能、吉布斯自由能）的混合偏导数与求导顺序无关这一数学性质。

麦克斯韦关系的重要性在于它将难以直接测量的量（如熵的偏导数）转化为实验室中可以直接测量的量（如压强对温度的偏导数）。例如，熵随压强的变化率 $(\partial S/\partial P)_T$ 在实验上几乎无法直接测定，但通过麦克斯韦关系，它等于 $-(\partial V/\partial T)_P$，而后者只需测量气体在不同温度下的体积即可。这一"变换"能力使麦克斯韦关系成为推导状态方程和计算热力学响应函数的核心工具。

## 核心原理

### 全微分条件与麦克斯韦关系的推导

若函数 $f(x, y)$ 是状态函数，其全微分 $df = M\,dx + N\,dy$ 的充要条件是：

$$\left(\frac{\partial M}{\partial y}\right)_x = \left(\frac{\partial N}{\partial x}\right)_y$$

这一数学条件（施瓦茨定理，Schwarz's theorem）直接应用于四个热力学势，即可导出四个麦克斯韦关系。

**内能** $U(S, V)$：其全微分为 $dU = T\,dS - P\,dV$，对比系数后求交叉偏导：

$$\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial P}{\partial S}\right)_V$$

**焓** $H(S, P)$：$dH = T\,dS + V\,dP$，得：

$$\left(\frac{\partial T}{\partial P}\right)_S = \left(\frac{\partial V}{\partial S}\right)_P$$

**亥姆霍兹自由能** $F(T, V)$：$dF = -S\,dT - P\,dV$，得：

$$\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$$

**吉布斯自由能** $G(T, P)$：$dG = -S\,dT + V\,dP$，得：

$$\left(\frac{\partial S}{\partial P}\right)_T = -\left(\frac{\partial V}{\partial T}\right)_P$$

### 助记方法——热力学正方形（Thermodynamic Square）

麦克斯韦在1871年的工作之后，后人发展了一种几何助记图，称为"波恩方块"或热力学正方形。四个顶点依次排列为 $V$、$T$、$P$、$S$（顺时针），四条边对应四个自然变量对，四个面对应四个热力学势。利用正方形的对角线方向和符号规则，可以机械地读出任意一个麦克斯韦关系，无需重新推导。

### 麦克斯韦关系的物理内涵

以吉布斯自由能导出的关系 $\left(\frac{\partial S}{\partial P}\right)_T = -\left(\frac{\partial V}{\partial T}\right)_P$ 为例，其右侧等于 $-V\alpha$，其中 $\alpha = \frac{1}{V}\left(\frac{\partial V}{\partial T}\right)_P$ 是等压热膨胀系数。这意味着：等温条件下增大压强，系统熵的变化由材料的热膨胀性质完全决定。对于大多数液体（$\alpha > 0$），加压会降低熵；而水在4°C以下 $\alpha < 0$，加压反而会增大熵，这是冰的压力融化现象的热力学根源。

## 实际应用

**计算等温压缩与绝热压缩之差**：利用由亥姆霍兹自由能导出的关系 $\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$，可以推导出等温压缩系数 $\kappa_T$ 与绝热压缩系数 $\kappa_S$ 之间的差：

$$\kappa_T - \kappa_S = \frac{TV\alpha^2}{C_P}$$

其中 $C_P$ 是等压热容。此公式在声学中用于计算声速（声波传播是绝热过程），对于液态水在20°C时，$\kappa_T - \kappa_S \approx 2.5 \times 10^{-11}\ \text{Pa}^{-1}$，这与实验值高度吻合。

**推导范德瓦耳斯气体的内压**：利用 $\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$，可将内能的体积偏导数改写为：

$$\left(\frac{\partial U}{\partial V}\right)_T = T\left(\frac{\partial P}{\partial T}\right)_V - P$$

将范德瓦耳斯方程 $P = \frac{nRT}{V - nb} - \frac{an^2}{V^2}$ 代入，得 $\left(\frac{\partial U}{\partial V}\right)_T = \frac{an^2}{V^2}$，正是分子间吸引力参数 $a$ 的体现。

**相变的克劳修斯-克拉佩龙方程**：$\left(\frac{\partial P}{\partial T}\right)_S$ 这一麦克斯韦关系的变形，配合相平衡条件，直接导出 $\frac{dP}{dT} = \frac{L}{T\Delta V}$，其中 $L$ 是潜热，$\Delta V$ 是两相比体积之差。

## 常见误区

**误区一：混淆自然变量，在错误的热力学势上应用关系**。麦克斯韦关系的成立前提是使用对应势函数的自然变量。例如 $\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial P}{\partial T}\right)_V$ 来自亥姆霍兹自由能 $F(T, V)$，其中 $T$ 和 $V$ 是自然变量。若将同样形式的偏导数写成 $\left(\frac{\partial S}{\partial V}\right)_P$，则与上式完全不同，无法用此麦克斯韦关系替换。每次使用前必须确认括号内保持不变的量与对应势函数的自然变量一致。

**误区二：认为麦克斯韦关系仅适用于理想气体**。麦克斯韦关系是纯粹的数学结果，来源于状态函数的全微分性质，对任何处于热平衡的均匀系统均严格成立——包括真实气体、液体、固体和磁性材料。上文中范德瓦耳斯气体和液态水的例子均已说明这一点。将其局限于理想气体是对其推导逻辑的误解。

**误区三：将麦克斯韦关系与热力学第二定律混淆**。麦克斯韦关系不依赖于熵增原理，它们是热力学势函数的数学性质（混合偏导数的对称性），在可逆或不可逆过程的分析中均可使用状态函数值——关键是所有偏导数描述的都是平衡态之间的关系，而非过程路径。

## 知识关联

麦克斯韦关系建立在亥姆霍兹自由能 $F = U - TS$ 和吉布斯自由能 $G = H - TS$ 的全微分结构之上，因此对自由能概念（包括勒让德变换将自然变量从 $S, V$ 转换为 $T, V$ 或 $T, P$）的掌握是理解麦克斯韦关系推导的直接基础。若尚未理解为何 $dF = -S\,dT - P\,dV$，则四个麦克斯韦关系将沦为四条需要死记的公式。

向下游看，麦克斯韦关系是推导热力学响应函数（热容、压缩系数、热膨胀系数）之间普遍关系的基本工具，也是统计力学中将配分函数与宏观可测量联系起来时进行一致性验证的手段。在物态方程研究、材料科学的热弹性耦合分析，以及量子多体物理的热力学极限计算中，麦克斯韦关系均作为核心等式频繁出现。