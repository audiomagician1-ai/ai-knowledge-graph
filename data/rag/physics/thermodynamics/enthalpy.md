---
id: "enthalpy"
concept: "焓"
domain: "physics"
subdomain: "thermodynamics"
subdomain_name: "热力学"
difficulty: 5
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-03-27
---


# 焓

## 概述

焓（Enthalpy）是热力学中用于描述系统能量状态的一个复合状态函数，定义为：

$$H = U + PV$$

其中 $H$ 为焓，$U$ 为系统的内能，$P$ 为系统压强，$V$ 为系统体积。由于 $U$、$P$、$V$ 均为状态量，焓 $H$ 本身也是一个状态量，其值仅由系统的当前热力学状态决定，与到达该状态的路径无关。

焓的概念由美国物理化学家Josiah Willard Gibbs在19世纪70年代的热力学研究中奠定了理论基础，而"焓"这一术语（源自希腊语"enthalpein"，意为"加热"）在20世纪初由荷兰物理学家Heike Kamerlingh Onnes正式引入并推广使用。焓之所以在热力学中格外重要，是因为实验室中绝大多数化学反应和物理变化都在恒定大气压下进行。在等压条件下，焓变 $\Delta H$ 恰好等于系统与外界交换的热量，使测量和计算大为简化。

## 核心原理

### 焓的热力学推导

从热力学第一定律出发：

$$\Delta U = Q - W$$

对于只有体积功的系统，$W = P\Delta V$（等压过程中压强不变），代入得：

$$Q_P = \Delta U + P\Delta V$$

注意到等压过程中：

$$\Delta(PV) = P\Delta V + V\Delta P = P\Delta V \quad (\Delta P = 0)$$

因此：

$$Q_P = \Delta U + \Delta(PV) = \Delta(U + PV) = \Delta H$$

这一推导清晰说明：**等压过程中系统吸收的热量 $Q_P$ 恰好等于焓变 $\Delta H$**。这不是偶然，而是焓的定义 $H=U+PV$ 专门为等压过程量身构造的结果。

### 焓与内能的区别：$PV$ 项的物理意义

$PV$ 项代表系统为了"占据"体积 $V$ 而克服外界压强 $P$ 所储存的能量，有时称为"流动功"（flow work）。对于理想气体，$PV = nRT$，因此焓包含了气体分子的热运动能量（内能部分）以及分子推开周围环境所做的功。举例来说，1 mol 理想气体在 298 K 时的 $PV$ 项约为 $1 \times 8.314 \times 298 \approx 2478 \text{ J}$，这一数值与其内能量级相当，不可忽略。

焓不能被直接测量绝对值——实验中只能测定焓变 $\Delta H$。国际规定，各元素在标准状态（298.15 K，100 kPa）下最稳定单质形态的标准摩尔生成焓 $\Delta_f H^\circ = 0$，以此作为参考基准。

### 等压焓变与热容的关系

在等压条件下，焓变与温度的关系通过定压热容 $C_P$ 表达：

$$C_P = \left(\frac{\partial H}{\partial T}\right)_P$$

当温度从 $T_1$ 升至 $T_2$ 时，焓变为：

$$\Delta H = \int_{T_1}^{T_2} C_P \, dT$$

对于理想气体，单原子气体的 $C_P = \frac{5}{2}R \approx 20.8 \text{ J·mol}^{-1}\text{·K}^{-1}$，双原子气体的 $C_P = \frac{7}{2}R \approx 29.1 \text{ J·mol}^{-1}\text{·K}^{-1}$。这些具体数值直接来自焓对温度偏导的物理定义。

注意定压热容 $C_P$ 与定容热容 $C_V$ 不同，对理想气体有 $C_P - C_V = R$，其中 $R = 8.314 \text{ J·mol}^{-1}\text{·K}^{-1}$。$C_P > C_V$ 的根本原因是等压加热时系统需额外做膨胀功，多出的能量正好体现在焓的 $PV$ 项上。

## 实际应用

**化学反应热的计算**：化学反应在恒压下释放或吸收的热量直接用 $\Delta H$ 表示。例如，氢气燃烧反应 $\text{H}_2(g) + \frac{1}{2}\text{O}_2(g) \rightarrow \text{H}_2\text{O}(l)$ 的标准摩尔焓变 $\Delta_r H^\circ = -285.8 \text{ kJ/mol}$，负号表示反应放热。利用赫斯定律（Hess's Law），可将多步反应的 $\Delta H$ 代数相加，得到目标反应的焓变，这完全依赖于焓的状态函数性质。

**蒸汽工程与相变计算**：水在 100°C、标准大气压下蒸发的摩尔汽化焓为 $\Delta_{vap}H = 40.7 \text{ kJ/mol}$。蒸汽发电厂通过查询水蒸气焓值表（以 $H$ 对温度和压强列表），计算汽轮机入口与出口的焓差，直接得到每千克蒸汽对外输出的最大功，整个计算过程无需单独追踪内能和体积功。

## 常见误区

**误区一：焓等于热量**。很多学生将 $H$ 与"热量"混淆。热量 $Q$ 是过程量，与路径有关；焓 $H$ 是状态函数，与路径无关。只有在**等压且只做体积功**的条件下，$Q_P = \Delta H$ 才严格成立。若过程不是等压（如密封容器中的爆炸反应），则 $Q \neq \Delta H$，此时应使用 $Q_V = \Delta U$（等容过程）。

**误区二：$\Delta H < 0$ 就意味着反应能自发进行**。焓变只衡量能量释放情况，放热反应（$\Delta H < 0$）在低温下通常自发，但决定反应自发性的是吉布斯自由能 $\Delta G = \Delta H - T\Delta S$，熵变 $\Delta S$ 的贡献在高温下可能主导结果，例如碳酸钙分解 $\Delta H > 0$ 却在高温下自发进行。

**误区三：焓变与温度无关**。部分学生认为 $\Delta H$ 是固定数值。实际上，$\Delta H$ 随温度变化，需用基尔霍夫定律（Kirchhoff's Law）修正：$\frac{d(\Delta H)}{dT} = \Delta C_P$，其中 $\Delta C_P$ 为产物与反应物定压热容之差。标准生成焓数据通常仅在 298.15 K 下给出，直接用于其他温度会引入误差。

## 知识关联

焓的引入以**热力学第一定律**为直接前提：若没有 $\Delta U = Q - W$ 的关系，就无法推导出 $Q_P = \Delta H$ 这一等压热量等式。学习焓之前必须明确内能 $U$ 的概念，以及体积功 $W = P\Delta V$ 的计算方式。

掌握焓之后，可以直接进入**热化学**（计算标准生成焓、燃烧焓、赫斯定律应用）以及**化学势与吉布斯自由能**的学习——吉布斯自由能 $G = H - TS$ 在焓的基础上引入熵 $S$，用于判断等温等压过程的自发方向。此外，焓也是理解**节流过程**（Joule-Thomson 效应）的关键：节流前后焓值守恒（$H_1 = H_2$），而非内能守恒，这是实际气体液化技术的核心热力学依据。