---
id: "electromagnetic-waves"
concept: "电磁波"
domain: "physics"
subdomain: "waves-and-optics"
subdomain_name: "波动与光学"
difficulty: 4
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 电磁波

## 概述

电磁波是由相互垂直的振荡电场与磁场在空间中传播的横波，其中电场矢量 **E**、磁场矢量 **B** 以及传播方向 **k** 三者两两垂直，形成右手坐标系。与机械波不同，电磁波无需介质即可在真空中传播，真空中传播速度恒为 $c = 3.0 \times 10^8 \, \text{m/s}$。

1887年，德国物理学家海因里希·赫兹（Heinrich Hertz）首次在实验室中人工产生并探测到无线电波，从而验证了麦克斯韦在1865年基于电磁场理论所预言的电磁波的存在。赫兹使用振荡电路产生约66 MHz的无线电波，并用一个带缺口的金属环作为接收器，观察到感应电火花，证明了电磁扰动确实以波的形式向外传播。

电磁波覆盖的频率范围极其宽广，从赫兹量级的无线电波到 $10^{24}$ Hz 的高能γ射线，横跨约26个数量级。正是由于这种宽广的频谱，电磁波成为现代通信、医学成像、天文观测和能源传输等众多技术领域不可替代的物理基础。

## 核心原理

### 麦克斯韦方程组与波动方程的推导

在无源真空中，麦克斯韦方程组的旋度方程为：

$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}, \quad \nabla \times \mathbf{B} = \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}$$

对上述两式分别取旋度并利用 $\nabla \times (\nabla \times \mathbf{E}) = \nabla(\nabla \cdot \mathbf{E}) - \nabla^2 \mathbf{E}$，结合 $\nabla \cdot \mathbf{E} = 0$，可得到波动方程：

$$\nabla^2 \mathbf{E} = \mu_0 \varepsilon_0 \frac{\partial^2 \mathbf{E}}{\partial t^2}$$

由此直接读出电磁波在真空中的速度 $c = \dfrac{1}{\sqrt{\mu_0 \varepsilon_0}} \approx 3.0 \times 10^8 \, \text{m/s}$，其中 $\mu_0 = 4\pi \times 10^{-7} \, \text{T·m/A}$ 为真空磁导率，$\varepsilon_0 = 8.85 \times 10^{-12} \, \text{F/m}$ 为真空介电常数。这一推导是麦克斯韦理论的核心成就，他由此断言光本身就是一种电磁波。

### 电磁波的能量：坡印廷矢量

电磁波携带的能量流密度用**坡印廷矢量**（Poynting vector）描述：

$$\mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}$$

$\mathbf{S}$ 的方向即为能量传播方向，其量值（单位 W/m²）给出单位时间内通过单位面积垂直截面的电磁能量。在真空中，平面电磁波满足 $B = E/c$，因此瞬时能流密度 $S = E^2/(\mu_0 c)$。平均辐照度（光强）为：

$$I = \langle S \rangle = \frac{E_0^2}{2\mu_0 c} = \frac{1}{2} c \varepsilon_0 E_0^2$$

其中 $E_0$ 为电场振幅。需要注意，电磁波中电场和磁场的能量密度相等，各占总能量密度的一半，即 $u_E = \frac{1}{2}\varepsilon_0 E^2 = \frac{B^2}{2\mu_0} = u_B$。

### 电磁波的动量与辐射压力

电磁波不仅携带能量，还携带线动量。单位体积内电磁波的动量密度为：

$$\mathbf{g} = \frac{\mathbf{S}}{c^2} = \varepsilon_0 \mathbf{E} \times \mathbf{B}$$

当电磁波被物体完全吸收时，产生的辐射压强为 $P = I/c$；若被完全反射，则 $P = 2I/c$。1901年，列别捷夫在实验中首次测量到光压，完全吻合上述理论预测。这一动量关系还与光子的量子力学图像一致：单个光子的动量 $p = h\nu/c = h/\lambda$，其中 $h = 6.626 \times 10^{-34} \, \text{J·s}$ 为普朗克常数。

### 电磁波谱的分类

按频率从低到高，电磁波谱依次划分为：

| 类型 | 典型频率/波长 | 产生机制 |
|------|-------------|----------|
| 无线电波 | $< 300 \, \text{GHz}$（$> 1 \, \text{mm}$） | LC振荡电路 |
| 微波 | $1 \sim 300 \, \text{GHz}$ | 磁控管、速调管 |
| 红外线 | $0.3 \, \text{THz} \sim 430 \, \text{THz}$ | 分子振动、热辐射 |
| 可见光 | $430 \sim 750 \, \text{THz}$（$400 \sim 700 \, \text{nm}$） | 原子外层电子跃迁 |
| 紫外线 | $750 \, \text{THz} \sim 30 \, \text{PHz}$ | 原子内层电子跃迁 |
| X射线 | $30 \, \text{PHz} \sim 30 \, \text{EHz}$ | 内层电子跃迁、轫致辐射 |
| γ射线 | $> 10^{19} \, \text{Hz}$ | 原子核跃迁 |

尽管各类电磁波在产生机制和应用上差异巨大，它们在真空中的传播速度均为 $c$，且均满足 $c = \lambda \nu$。

## 实际应用

**微波炉加热原理**：微波炉工作频率为2.45 GHz，对应波长12.2 cm。水分子（H₂O）在此频率附近具有强烈的偶极转动共振，吸收微波能量后转化为热能。而玻璃、陶瓷等非极性材料对2.45 GHz微波几乎透明，因此容器不发热。

**移动通信波段分配**：4G LTE主要使用700 MHz至2.6 GHz频段，5G新增毫米波频段（24～100 GHz），毫米波波长短、方向性强，单基站覆盖半径仅约100 m，需密集部署。频率越高，大气中的水汽和氧气对电磁波的吸收衰减越显著（如60 GHz处氧气吸收峰达15 dB/km），这直接制约了不同频段的传播距离。

**太阳帆航天器**：利用光压推进的太阳帆（如2010年日本发射的IKAROS探测器，帆面积196 m²）在距太阳1 AU处受到的辐射压强约为 $4.6 \times 10^{-6} \, \text{N/m}^2$，对质量仅数百千克的航天器可提供持续加速。

## 常见误区

**误区一：电磁波中磁场由电场"产生"（或反之）**
部分教材描述电磁波为"变化电场产生磁场，变化磁场产生电场，如此交替传播"，这一说法存在误导性。实际上，麦克斯韦方程组是场的整体约束方程，电场与磁场是同一电磁场的两个分量，并不存在哪个"先产生"哪个的时间因果关系。正确理解是：电磁场作为整体满足波动方程，在空间中以速度 $c$ 传播。

**误区二：在介质中电磁波速度变为 $v = c/n$，但频率不变**
光从真空进入折射率为 $n$ 的介质后，速度变为 $v = c/n$，波长变为 $\lambda' = \lambda_0/n$，但频率 $\nu$ 保持不变（由介质与真空的边界条件决定）。许多学生错误地认为进入介质后波长不变而频率改变，但这与边界处相位连续的物理要求相矛盾。

**误区三：频率越高，电磁波的穿透力一定越强**
X射线（$\sim 10^{18}$ Hz）能穿透人体软组织，但γ射线穿透铅板的能力也有限，而微波（$\sim 10^9$ Hz）对含水组织的穿透深度反而受限于共振吸收。穿透能力由电磁波与特定材料的相互作用截面决定，与频率的关系并非单调。例如，无线电波可以穿透建筑物，但可见光则不能。

## 知识关联

**与麦克斯韦方程组的联系**：电磁波的存在直接由麦克斯韦方程组在无源条件下推导而出，波速 $c = 1/\sqrt{\mu_0\varepsilon_0}$ 是麦克斯韦方程组的直接推论。不理解位移电流项 $\varepsilon_