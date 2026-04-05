---
id: "maxwells-equations"
concept: "麦克斯韦方程组"
domain: "physics"
subdomain: "electromagnetism"
subdomain_name: "电磁学"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 麦克斯韦方程组

## 概述

麦克斯韦方程组是由英国物理学家詹姆斯·克拉克·麦克斯韦于1865年在论文《电磁场的动力学理论》中系统整理并完善的四个偏微分方程，它将电场、磁场、电荷和电流统一在同一理论框架下。麦克斯韦并非凭空创造这四个方程——高斯、安培、法拉第等人的实验结论已经各自存在，但麦克斯韦发现安培定律在时变电场情形下存在逻辑矛盾，并通过引入"位移电流"这一概念修正了安培定律，从而使整个方程组在数学上自洽。

这一修正的意义远超修补漏洞本身。正是因为位移电流的引入，麦克斯韦方程组在真空中预言了以速度 $c = 1/\sqrt{\varepsilon_0\mu_0} \approx 3\times10^8\,\text{m/s}$ 传播的横波，这个数值与当时已知的光速完全吻合，从而在理论上揭示了光本质上是电磁波。这一预言直到1887年由赫兹通过实验证实，奠定了整个现代无线通信技术的物理基础。

## 核心原理

### 四个方程的积分形式与微分形式

麦克斯韦方程组共包含四个方程，以微分形式（SI单位制）书写如下：

1. **高斯电场定律**：$\nabla \cdot \mathbf{E} = \dfrac{\rho}{\varepsilon_0}$
   — 电场的散度等于自由电荷密度除以真空介电常数，描述电荷如何成为电场线的源或汇。

2. **高斯磁场定律**：$\nabla \cdot \mathbf{B} = 0$
   — 磁场散度恒为零，说明自然界中不存在磁单极子，磁场线永远闭合。

3. **法拉第感应定律**：$\nabla \times \mathbf{E} = -\dfrac{\partial \mathbf{B}}{\partial t}$
   — 时变磁场产生旋转电场，负号来自楞次定律，体现感应效应对原变化的"抗拒"。

4. **修正的安培定律（含位移电流）**：$\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\varepsilon_0\dfrac{\partial \mathbf{E}}{\partial t}$
   — 旋转磁场由传导电流 $\mathbf{J}$ 和位移电流 $\varepsilon_0\partial\mathbf{E}/\partial t$ 共同激发。

四个方程中涉及的物理量：$\mathbf{E}$ 为电场强度（V/m），$\mathbf{B}$ 为磁感应强度（T），$\rho$ 为自由电荷体密度（C/m³），$\mathbf{J}$ 为传导电流密度（A/m²），$\varepsilon_0 = 8.854\times10^{-12}\,\text{F/m}$ 为真空介电常数，$\mu_0 = 4\pi\times10^{-7}\,\text{H/m}$ 为真空磁导率。

### 位移电流：麦克斯韦的关键修正

麦克斯韦发现，对正在充电的平行板电容器两端板之间的区域，原始安培定律 $\nabla\times\mathbf{B}=\mu_0\mathbf{J}$ 会给出矛盾结果：选取穿过导线的平面和穿过两极板间隙的曲面，对同一安培回路的积分结果不同。为消除此矛盾，他引入位移电流密度 $\mathbf{J}_D = \varepsilon_0\dfrac{\partial\mathbf{E}}{\partial t}$。在电容器充电过程中，极板间无传导电流，但随时间变化的电场产生位移电流，使磁场旋度方程在所有曲面选取下保持一致。位移电流不是真正的电荷运动，而是时变电场对磁场的贡献——这一概念纯粹来自麦克斯韦的理论推断，而非直接实验观测。

### 方程组的对称性与电磁波推导

第三和第四个方程呈现出深刻的对偶对称性：时变磁场产生电场，时变电场产生磁场，两者互相激发。在无源真空区域（$\rho=0,\,\mathbf{J}=0$）中，对法拉第定律取旋度并代入修正安培定律，可得：
$$\nabla^2\mathbf{E} = \mu_0\varepsilon_0\dfrac{\partial^2\mathbf{E}}{\partial t^2}$$
这是标准波动方程，波速 $v = 1/\sqrt{\mu_0\varepsilon_0}$，代入数值恰好等于光速 $c$。同理可得磁场满足相同形式的波动方程。这意味着电场和磁场的振动方向互相垂直，且均垂直于传播方向，光是横波的结论由此直接导出。

## 实际应用

**平行板电容器的位移电流计算**：对极板面积 $A$、间距 $d$ 的电容器，充电时极板间电场 $E = Q/(\varepsilon_0 A)$，位移电流 $I_D = \varepsilon_0 A\,dE/dt = dQ/dt$，恰好等于传导电流，验证了位移电流的引入在数量上是自洽的。

**无线电波发射天线**：振荡电流在天线中产生时变磁场（第四方程），时变磁场感应出时变电场（第三方程），两者交替激发向外辐射，形成频率与电流振荡频率相同的电磁波。麦克斯韦方程组不仅解释了波的存在，还规定了其传播速度、偏振特性和能量传输方向。

**物质中的形式推广**：在线性各向同性介质中，$\varepsilon_0$ 替换为 $\varepsilon = \varepsilon_r\varepsilon_0$，$\mu_0$ 替换为 $\mu = \mu_r\mu_0$，方程组形式不变但波速变为 $v = c/\sqrt{\varepsilon_r\mu_r}$，由此得出介质折射率 $n = \sqrt{\varepsilon_r\mu_r}$，将光学与电磁学直接相连。

## 常见误区

**误区一：认为位移电流是真实的粒子电流**。许多初学者将位移电流 $\varepsilon_0\partial\mathbf{E}/\partial t$ 理解为某种"虚拟电荷"在空间移动。实际上，位移电流密度的单位是 A/m²，其贡献等效于电流密度，但它的本质是电场对时间的变化率，并不涉及任何带电粒子的运动，在真空中同样存在，与传导电流的物理机制完全不同。

**误区二：将四个方程视为独立的、互不相关的定律**。麦克斯韦方程组的核心价值在于四个方程作为整体的自洽性——恰恰是第三和第四方程的耦合形成了电磁波，单独的法拉第定律或单独的安培定律都无法预言电磁波的存在。缺少位移电流项的安培定律不仅给出错误的物理图像，在数学上还会违反电荷守恒（连续性方程 $\partial\rho/\partial t + \nabla\cdot\mathbf{J}=0$ 无法从不含位移电流的方程组中导出）。

**误区三：认为麦克斯韦方程组只适用于真空**。方程的微分形式在物质内部同样成立，区别仅在于需要引入极化强度 $\mathbf{P}$ 和磁化强度 $\mathbf{M}$，将方程改写为含 $\mathbf{D}=\varepsilon_0\mathbf{E}+\mathbf{P}$ 和 $\mathbf{H}=\mathbf{B}/\mu_0-\mathbf{M}$ 的形式，这正是分析介质中波传播、光在玻璃中折射等问题的出发点。

## 知识关联

麦克斯韦方程组以高斯定律（提供方程一和方程二的散度结构）、法拉第电磁感应定律（提供方程三）和安培定律（提供方程四的传导电流项）为直接前驱，但它并非三者的简单拼合——位移电流的加入是本质性的新物理内容。

从麦克斯韦方程组出发，直接延伸出两个后续主题：**电磁波**（将方程组在真空中解耦为波动方程，研究频率、波长、偏振和干涉）和**坡印廷矢量**（通过 $\mathbf{S}=\mathbf{E}\times\mathbf{H}/\mu_0$ 描述电磁场携带的能量流密度，单位 W/m²，从麦克斯韦方程组结合能量守恒直接导出）。此外，麦克斯韦方程组与洛伦兹变换之间存在天然的相容性——爱因斯坦1905年建立狭义相对论时，正是以麦克斯韦方程组在所有惯性系中形式不变作为基本假设之一。