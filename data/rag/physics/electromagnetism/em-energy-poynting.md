---
id: "em-energy-poynting"
concept: "电磁能与坡印廷矢量"
domain: "physics"
subdomain: "electromagnetism"
subdomain_name: "电磁学"
difficulty: 5
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 电磁能与坡印廷矢量

## 概述

电磁场本身携带能量，这一认识是经典电磁学的重大突破。电场能量密度 $u_E = \frac{1}{2}\varepsilon_0 E^2$，磁场能量密度 $u_B = \frac{1}{2\mu_0} B^2$，两者之和构成电磁场的总能量密度 $u = \frac{1}{2}\varepsilon_0 E^2 + \frac{1}{2\mu_0} B^2$。在真空平面电磁波中，电场与磁场的能量密度恰好相等，各贡献一半总能量。

1884年，英国物理学家约翰·亨利·坡印廷（John Henry Poynting）从麦克斯韦方程组出发，推导出描述电磁能量流动的矢量场，该矢量以其名字命名为坡印廷矢量。坡印廷的这一工作将能量守恒定律从力学领域推广到电磁场，表明电磁能量像流体一样在空间中传输，而非仅储存于电荷或导体之中。

坡印廷矢量的意义不仅在于描述辐射波的能量传播，还澄清了直流电路中能量传输的真实路径：导线输送的电功率实际上通过导线周围的电磁场传递，而非通过导线内部的电子传递。这一结论极具反直觉性，却是坡印廷定理的直接推论。

## 核心原理

### 坡印廷矢量的定义与方向

坡印廷矢量定义为：

$$\mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}$$

其单位为 $\text{W/m}^2$（瓦特每平方米），表示单位时间内通过单位面积的电磁能量，方向由 $\mathbf{E} \times \mathbf{B}$ 的叉积确定，即垂直于 $\mathbf{E}$ 和 $\mathbf{B}$ 所在平面，指向能量流动方向。对于沿 $+z$ 方向传播的平面波，$\mathbf{E}$ 沿 $x$ 方向、$\mathbf{B}$ 沿 $y$ 方向，则 $\mathbf{S} = \frac{1}{\mu_0} E B \hat{z}$，与波的传播方向一致。

### 坡印廷定理（能量守恒方程）

从麦克斯韦方程组出发，可以推导出微分形式的坡印廷定理：

$$\frac{\partial u}{\partial t} + \nabla \cdot \mathbf{S} = -\mathbf{J} \cdot \mathbf{E}$$

其中 $u$ 为电磁能量密度，$\mathbf{J} \cdot \mathbf{E}$ 为单位体积内电磁场对电流做功的功率密度（即焦耳热损耗或对自由电荷做功的功率）。该方程的物理意义是：某体积内电磁能量的减少率，等于通过该体积边界面流出的能量通量加上场对电流做的功率。对封闭曲面 $\mathcal{A}$ 积分得到积分形式：

$$-\frac{d}{dt}\int_V u \, dV = \oint_{\mathcal{A}} \mathbf{S} \cdot d\mathbf{A} + \int_V \mathbf{J} \cdot \mathbf{E} \, dV$$

### 平面波的时均坡印廷矢量与辐照度

对于角频率为 $\omega$ 的单色平面波，电场 $E = E_0 \cos(kz - \omega t)$，磁场 $B = \frac{E_0}{c} \cos(kz - \omega t)$，其瞬时坡印廷矢量为 $S = \frac{E_0^2}{\mu_0 c} \cos^2(kz - \omega t) \hat{z}$。对时间取平均，$\cos^2$ 的平均值为 $\frac{1}{2}$，得时均坡印廷矢量（辐照度）：

$$\langle S \rangle = \frac{E_0^2}{2\mu_0 c} = \frac{1}{2} c \varepsilon_0 E_0^2$$

该量即光强，单位 $\text{W/m}^2$，与场振幅的平方成正比。

### 辐射压

电磁波携带动量，单位体积内电磁场的动量密度为：

$$\mathbf{g} = \frac{\mathbf{S}}{c^2} = \varepsilon_0 (\mathbf{E} \times \mathbf{B})$$

当电磁波被完全吸收时，作用在物体单位面积上的辐射压为：

$$P_{\text{rad}} = \frac{\langle S \rangle}{c}$$

若电磁波被完全反射，辐射压加倍，$P_{\text{rad}} = \frac{2\langle S \rangle}{c}$。太阳光在地球轨道处的辐照度约为 $1361 \, \text{W/m}^2$（太阳常数），由此可算出完全吸收时辐射压约为 $4.5 \times 10^{-6} \, \text{Pa}$，这正是太阳帆航天器设计的物理依据。

## 实际应用

**直流电路的能量传输**：考虑一段横截面半径为 $r$、长为 $l$ 的载流导线，其表面存在沿轴向的电场 $E$（由沿线的电压降产生）和环绕轴线的磁场 $B = \frac{\mu_0 I}{2\pi r}$。表面的坡印廷矢量 $\mathbf{S}$ 指向导线内部，大小为 $\frac{EI}{2\pi r l}$，对导线侧面积分恰好等于该段导线的欧姆耗散功率 $I^2 R = I V$，证实电功率经由导线外的电磁场流入导线转化为热能。

**激光捕获（光镊）**：聚焦激光束的梯度力来源于光强梯度所产生的辐射压差，可捕获直径约为 $1\,\mu\text{m}$ 的微粒。1997年诺贝尔物理学奖（朱棣文等）的激光冷却原子技术也依赖辐射压对原子动量的精确调控，其力的量级约为 $10^{-20}\,\text{N}$，量级虽小却足以改变原子速度。

**天线辐射功率计算**：赫兹偶极子辐射的总功率可通过在远场对 $\langle S \rangle$ 积分球面得到，结果为 $P = \frac{\mu_0 \omega^4 p_0^2}{12\pi c}$，其中 $p_0$ 为偶极矩振幅，功率与频率四次方成正比，这解释了天空散射蓝光比红光强烈得多的瑞利散射本质。

## 常见误区

**误区一：认为电路中能量在导线内部传输**。许多人以为电流在导线中流动时，能量沿导线内部传递。实际上，根据坡印廷定理，能量通量由导线外的 $\mathbf{E} \times \mathbf{B}$ 决定，能量从外部电磁场径向流入导线，而非沿导线轴向在导体内传播。

**误区二：混淆瞬时坡印廷矢量与时均值**。对于单色波，$S$ 的瞬时值以 $2\omega$ 频率振荡，不代表稳定的能量流，实验可测的辐照度是其时间平均值 $\langle S \rangle = E_0^2 / (2\mu_0 c)$。在计算光对物体的辐射压或辐射功率时，必须使用时均值而非峰值。

**误区三：认为辐射压只与光强有关而与反射率无关**。完全吸收与完全反射对应的辐射压相差一倍：完全吸收 $P = \langle S \rangle / c$，完全反射 $P = 2\langle S \rangle / c$。这是因为完全反射时动量变化量是入射动量的两倍，故太阳帆应选用高反射率材料而非黑体材料。

## 知识关联

坡印廷矢量的推导依赖麦克斯韦方程组中的法拉第定律 $\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$ 和安培-麦克斯韦定律 $\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}$，通过矢量恒等式 $\nabla \cdot (\mathbf{E} \times \mathbf{B}) = \mathbf{B} \cdot (\nabla \times \mathbf{E}) - \mathbf{E} \cdot (\nabla \times \mathbf{B})$ 直接推导而来，因此麦克斯韦方程组的完整性（特别是位移电流项 $\varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}$）是坡印廷定理成立的前提。能量密度公式 $u_E = \frac{1}{2}\varepsilon_0 E^2$ 与静电学中电容器能量 $U = \frac{1}{2}CV^2$ 的微分形式完全一致，$u_B = \frac{B^2}{2\mu_0}