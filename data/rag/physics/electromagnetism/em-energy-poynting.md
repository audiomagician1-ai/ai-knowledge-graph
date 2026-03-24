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
---
# 电磁能与坡印廷矢量

## 概述

电磁场本身携带能量，这一认识是19世纪电磁学的重大突破。电场和磁场各自储存能量，单位体积内的电场能量密度为 $u_E = \frac{1}{2}\varepsilon_0 E^2$，磁场能量密度为 $u_B = \frac{1}{2\mu_0} B^2$，两者之和构成总电磁能量密度 $u = \frac{1}{2}\varepsilon_0 E^2 + \frac{1}{2\mu_0} B^2$。

1884年，英国物理学家约翰·亨利·坡印廷（John Henry Poynting）发表论文，引入以他名字命名的矢量，描述电磁能量在空间中的流动方向和强度。坡印廷矢量定义为 $\mathbf{S} = \frac{1}{\mu_0}(\mathbf{E} \times \mathbf{B})$，单位为瓦特每平方米（W/m²），表示单位时间内穿过单位面积的电磁能量。这一概念彻底改变了人们对电路中能量传输方式的理解——电能并非沿导线内部流动，而是在导线周围的电磁场中传播。

坡印廷矢量的重要性在于它使能量守恒定律在电磁场中得以精确表达。在激光技术、无线通信、太阳能利用和天体物理学中，计算电磁能流密度都必须借助坡印廷矢量。光压（辐射压）的存在也直接由坡印廷矢量的动量特性所预言，并在实验中得到验证。

## 核心原理

### 坡印廷定理与能量守恒

坡印廷定理是电磁场中的能量守恒方程，其微分形式为：

$$\frac{\partial u}{\partial t} + \nabla \cdot \mathbf{S} = -\mathbf{J} \cdot \mathbf{E}$$

其中 $u$ 是电磁能量密度，$\mathbf{S}$ 是坡印廷矢量，$\mathbf{J}$ 是自由电流密度，$-\mathbf{J} \cdot \mathbf{E}$ 表示单位体积内电磁场对电荷做功的功率（即电磁能转化为机械能或热能的速率）。积分形式则表明：某体积内电磁能的减少率等于通过包围该体积的闭合曲面向外流出的能量加上场对电荷做的功。

### 平面电磁波中的坡印廷矢量

对于沿 $z$ 轴传播的平面电磁波，电场 $\mathbf{E}$ 沿 $x$ 轴方向，磁场 $\mathbf{B}$ 沿 $y$ 轴方向，坡印廷矢量 $\mathbf{S} = \frac{1}{\mu_0}(\mathbf{E} \times \mathbf{B})$ 恰好沿 $z$ 轴方向，即与波的传播方向一致。真空中平面电磁波满足 $E = cB$（$c \approx 3\times10^8$ m/s），此时瞬时能流密度为 $S = \frac{E^2}{\mu_0 c} = \varepsilon_0 c E^2$。对时间取平均后得到平均强度（辐照度）$I = \frac{1}{2}\varepsilon_0 c E_0^2$，其中 $E_0$ 是电场振幅。值得注意的是，平面波中任意时刻电场能量密度与磁场能量密度相等，均为总能量密度的一半。

### 辐射压与电磁动量

电磁场不仅携带能量，还携带动量。电磁场的体积动量密度为 $\mathbf{g} = \frac{\mathbf{S}}{c^2} = \varepsilon_0 (\mathbf{E} \times \mathbf{B})$。当电磁波被完全吸收时，单位面积上受到的辐射压为 $P_{rad} = \frac{I}{c}$；当被完全反射时，辐射压加倍，$P_{rad} = \frac{2I}{c}$。1901年，俄国物理学家列别杰夫首次在实验室中直接测量到光压，验证了麦克斯韦的理论预言。太阳在距离1天文单位处的辐照度约为1361 W/m²（太阳常数），由此产生的辐射压约为 $4.5 \times 10^{-6}$ Pa，这正是彗星彗尾背离太阳的物理原因之一，也是当代"太阳帆"航天器设计的物理基础。

### 直流电路中的坡印廷矢量应用

在一段通有电流 $I$、两端电压为 $V$ 的直导线中，导线表面的电场 $\mathbf{E}$ 沿轴向，磁场 $\mathbf{B}$ 沿切向环绕导线。坡印廷矢量 $\mathbf{S} = \frac{1}{\mu_0}(\mathbf{E} \times \mathbf{B})$ 指向导线内部，表明能量从周围电磁场流入导线，转化为焦耳热。对导线侧面积分，能量流入速率恰好等于 $IV$（即欧姆损耗功率），完美验证了能量守恒。

## 实际应用

**激光强度的计算**：工业切割用的CO₂激光器，光束直径约2 mm，功率为1 kW时，平均强度可达 $I = P/A \approx 3.2 \times 10^7$ W/m²，对应电场振幅 $E_0 = \sqrt{2I/(\varepsilon_0 c)} \approx 4.9 \times 10^6$ V/m，接近空气击穿场强，这说明为何高功率激光束必须在真空或惰性气体中传播。

**太阳帆推进**：利用辐射压 $P = I/c$，面积为 $800\ \text{m}^2$、质量为 $4.5\ \text{kg}$ 的太阳帆飞船在地球轨道附近可获得约 $3.6 \times 10^{-3}$ N 的推力，对应加速度约 $8 \times 10^{-4}$ m/s²。2010年日本IKAROS探测器成功验证了太阳帆技术，在飞往金星途中利用辐射压实现了姿态控制。

**波导中的功率传输**：在矩形微波波导中，利用坡印廷矢量对横截面积分可以计算传输功率，这是微波工程中设计波导尺寸和评估功率容量的标准方法。

## 常见误区

**误区一：电流沿导线内部传输电能**。直觉上认为电能由电流携带在导线内部流动，但坡印廷矢量的计算明确表明，能量流动方向是从导线外部的电磁场指向导线内部，而非沿导线轴向传播。导线内的电子只是引导能量流动的机制，而非能量的载体。

**误区二：平均坡印廷矢量与瞬时坡印廷矢量的混淆**。对于正弦电磁波，瞬时功率密度 $S(t) = S_0\cos^2(\omega t - kz)$ 随时间高频振荡，时间平均值为 $\langle S \rangle = S_0/2$。在计算辐照度或辐射压时必须使用时间平均值，直接使用峰值幅度会导致结果偏大一倍。

**误区三：辐射压仅对完全吸收体成立**。实际上，公式 $P = I/c$ 仅适用于完全吸收（黑体）表面；对完全反射面，辐射压是 $2I/c$；对部分反射率为 $r$ 的表面，公式为 $P = (1+r)I/c$。忽视反射率的差异会在光学捕获（光镊）和辐射压推进计算中引入显著误差。

## 知识关联

坡印廷矢量直接从麦克斯韦方程组推导而来：将法拉第感应定律和安培-麦克斯韦定律与场量作点积，经过矢量恒等式 $\mathbf{E} \cdot (\nabla \times \mathbf{B}) - \mathbf{B} \cdot (\nabla \times \mathbf{E}) = \nabla \cdot (\mathbf{E} \times \mathbf{B})$ 的变换，即可直接得到坡印廷定理。因此，牢固掌握麦克斯韦方程组的旋度方程（特别是 $\nabla \times \mathbf{E} = -\partial\mathbf{B}/\partial t$ 和 $\nabla \times \mathbf{B} = \mu_0\mathbf{J} + \mu_0\varepsilon_0 \partial\mathbf{E}/\partial t$）是理解坡印廷定理推导过程的前提。

电磁能量密度公式 $u_E = \frac{1}{2}\varepsilon_0 E^2$ 与电容器储能 $U = \frac{1}{2}CV^2$ 相通，后者可视为前者对匀强电场空间的体积积分；同样，$u_B = \frac{1}{2\mu_0}B^2$ 与电感储能 $U = \frac{1}{2}LI^2$ 相互印证。坡印廷矢量还是理解辐射场（天线辐射、加速电荷辐射）和
