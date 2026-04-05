---
id: "vfx-niagara-force"
concept: "力场与运动"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 力场与运动

## 概述

在 Unreal Engine 的 Niagara 粒子系统中，力场（Force Field）模块是通过对粒子施加持续或瞬时加速度来改变运动轨迹的专用模块集合。与初速度（Initial Velocity）的一次性赋值不同，力场模块注册在发射器的 **Particle Update** 阶段，每帧执行一次速度积分，使粒子在其存活周期（Particle.NormalizedAge 从 0 到 1）的每一帧都受到持续影响，从而产生弯曲轨迹、旋涡聚集或向外爆散等复杂动态效果。

Niagara 的力场系统建立在牛顿第二定律 $F = ma$ 的基础上，其中粒子质量（`Particle.Mass`）可在模块参数中单独配置，默认值为 **1.0**，这使加速度在数值上直接等于施加的力向量。力场模块最早在 Niagara 的前身 Cascade 系统中以孤立的 "Acceleration Life" 和 "Constant Acceleration" 形式存在，二者不可堆叠。Niagara 在 **UE 4.20 版本（2018年7月）** 正式引入模块化力场架构，允许在同一发射器的 Particle Update 阶段叠加任意数量的力场模块，每个模块独立计算贡献量，所有模块输出的加速度向量逐帧累加，最终合力决定粒子的帧位移。这种可堆叠设计使同时模拟烟雾受重力拉扯、被横向风吹动、同时受涡流扰动成为可能。

本节内容主要参考《Real-Time Rendering》第4版（Akenine-Möller et al., 2018）第13章中粒子系统的速度积分方法，以及 Epic Games 官方 Niagara 技术文档（Epic Games, 2023）。

---

## 核心原理

### 速度积分模型

Niagara 力场模块统一采用**显式欧拉积分（Explicit Euler Integration）**更新粒子速度与位置。每帧执行顺序如下：

$$
\vec{v}_{t+\Delta t} = \vec{v}_t + \vec{a}_{total} \cdot \Delta t
$$

$$
\vec{x}_{t+\Delta t} = \vec{x}_t + \vec{v}_{t+\Delta t} \cdot \Delta t
$$

其中 $\vec{a}_{total}$ 是当前帧所有力场模块贡献加速度的向量和，$\Delta t$ 为帧间时间（`Engine.DeltaTime`，60fps 时约为 0.0167s）。显式欧拉法在 $\Delta t$ 较大（帧率低于 20fps）时会产生数值不稳定，表现为粒子抖动或爆炸性飘飞——这正是 Niagara 力场在极低帧率下出现异常的根本原因。

### 重力模块（Apply Force: Gravity）

Niagara 内置重力模块（`Apply Force: Gravity`）本质上是一个方向固定的恒定加速度施加器。默认参数为 **Z 轴 −980 cm/s²**，对应现实标准重力加速度 9.80665 m/s²（Niagara 以厘米为内部单位）。每帧执行时，模块将重力向量乘以 `Engine.DeltaTime` 后累加到 `Particle.Velocity`。

重力模块的 **"Scale by Mass"** 选项开启后，实际加速度变为：

$$
\vec{a}_{gravity} = \frac{\vec{g}}{m_{particle}}
$$

其中 $m_{particle}$ 取自 `Particle.Mass` 属性。这意味着质量为 **2.0** 的岩石碎片粒子其重力加速度为 490 cm/s²（下落更慢），而质量为 **0.5** 的烟尘粒子其重力加速度为 1960 cm/s²（下落更快），从而在同一发射器内实现粒子分层沉降效果。

> **案例**：在制作爆炸碎片效果时，将碎石粒子 `Particle.Mass` 设为 3.0，火星粒子 `Particle.Mass` 设为 0.2，同一重力模块即可产生碎石低抛弧线、火星高飞弧线同框的视觉分层，无需分开发射器。

### 风力与空气阻力模块（Wind Force / Drag）

风力模块（`Apply Wind Force`）通过设定世界空间目标速度向量（`Wind Velocity`，默认值为 `(100, 0, 0)` cm/s），将粒子当前速度逐帧拉向该目标，而非瞬间叠加速度。施加到粒子的逐帧加速度为：

$$
\vec{a}_{wind} = (\vec{v}_{wind} - \vec{v}_{particle}) \times k_{accel}
$$

其中 $k_{accel}$ 为"Wind Acceleration Rate"参数（单位 s⁻¹，典型值 **2.0～10.0**）。$k_{accel} = 5.0$ 时，粒子在约 **0.2 秒**内速度接近风速的 63%（一阶时间常数特性）。

空气阻力模块（`Apply Drag`）与风力协同工作，阻力向量计算公式为：

$$
\vec{a}_{drag} = -k_{drag} \cdot |\vec{v}_{particle}| \cdot \vec{v}_{particle}
$$

$k_{drag}$ 典型范围为 **0.01～5.0**。当 $k_{drag} = 0.1$ 时，初速为 500 cm/s 的粒子在 0.5 秒内减速至约 250 cm/s（适合烟雾缓慢漂散）；当 $k_{drag} = 3.0$ 时，同条件粒子在不足 0.05 秒内近乎静止（适合模拟水中气泡的极高阻尼）。

### 吸引与排斥力模块（Point Attraction / Repulsion Force）

吸引力模块（`Apply Point Attraction Force`）在世界空间中设置引力中心坐标，对所有粒子施加指向该坐标的加速度，大小遵循**距离平方反比衰减**：

$$
\vec{a}_{attract} = k_{attr} \cdot \frac{\vec{d}}{max(|\vec{d}|^2,\ r_{min}^2)}
$$

其中 $\vec{d}$ 为粒子到引力中心的向量，$k_{attr}$ 为引力强度（默认 **100 cm/s²**），$r_{min}$ 为最小安全距离（默认 **5 cm**，防止除零导致加速度爆炸至无穷大）。

排斥力模块（`Apply Point Repulsion Force`）公式结构与吸引力相同，唯独加速度方向取反。两者组合使用时，可通过设置 $k_{attract}$ 与 $k_{repulse}$ 的比值模拟**Lennard-Jones 势**风格的粒子间距平衡——当粒子距引力中心约 $\sqrt{k_{repulse}/k_{attract}}$ cm 时，合力为零，粒子在该半径附近形成稳定环绕轨道，常用于制作魔法护盾或粒子聚集球效果。

---

## 关键公式与 HLSL 实现

Niagara 模块底层以 **HLSL（High-Level Shading Language）** 编写，可通过"Custom HLSL"节点实现自定义力场。以下为一个螺旋力场（Vortex Force）的核心实现片段：

```hlsl
// 螺旋力场：绕 Z 轴产生切向加速度
// 输入：Particle.Position, VortexCenter(float3), VortexStrength(float)
float3 delta = Particle_Position - VortexCenter;
float3 radial = float3(delta.x, delta.y, 0.0f);
float dist = max(length(radial), 5.0f);          // 最小距离 5 cm 防止奇点

// 切向方向：绕 Z 轴逆时针旋转 90°
float3 tangent = float3(-radial.y, radial.x, 0.0f) / dist;

// 加速度大小与距离成反比（角动量守恒近似）
float accelMag = VortexStrength / dist;
float3 vortexAccel = tangent * accelMag;

// 输出叠加到 Particle.Velocity
Particle_Velocity += vortexAccel * Engine_DeltaTime;
```

此螺旋力场中，当 `VortexStrength = 2000` 时，距涡心 **100 cm** 处的粒子切向加速度为 20 cm/s²，在约 **1.5 秒**内可形成可见的旋转轨迹，适用于龙卷风、水漩涡等特效。

---

## 实际应用

### 火焰与烟雾特效

制作火焰效果时，常将三个力场模块叠加：

1. **重力模块**：Z 轴设为 **+200 cm/s²**（正值，模拟热浮力，与现实重力方向相反）；
2. **风力模块**：`Wind Velocity = (30, 15, 0)` cm/s，`k_{accel} = 3.0`，模拟微弱侧风；
3. **噪波力场（Curl Noise Force）**：强度 **50 cm/s²**，频率 **0.02**，模拟湍流扰动，防止粒子轨迹过于规律。

三者叠加后，火焰粒子自然呈现向上飘动、轻微偏斜、带随机抖动的有机形态，比单一浮力模块的视觉质感提升显著。

### 弹孔与碎片效果

枪击弹孔产生的混凝土碎片特效，需要在粒子生成后 **0～0.3 秒**内快速减速（空气阻力），同时持续受重力影响落地。典型配置：`Particle.Mass = 1.5`，`k_{drag} = 1.2`，重力 Z = −980 cm/s²，初速度随机范围 300～800 cm/s 朝向法线半球方向。粒子平均在 **0.8～1.2 秒**内落地，与实际碎片飞溅时长吻合。

### 粒子吸附特效（技能读条）

MOBA 或 RPG 游戏中常见"技能蓄力"特效：能量粒子从四周向玩家手部汇聚。实现方式为在手部骨骼位置挂载一个吸引力模块，`k_{attr} = 50000`，`r_{min} = 20 cm`，粒子从半径 **200 cm** 处生成，在约 **0.6 秒**内被吸入中心，恰好匹配常见技能读条时长（0.5～1.0 秒）。

---

## 常见误区

**误区1：重力单位混淆**
许多开发者将重力强度误设为 **−9.8**（以米为单位），实际 Niagara 使用厘米，正确值为 **−980 cm/s²**。误设 −9.8 导致粒子在 3 秒内仅下落约 44 cm（几乎不动），而非正确的 44 米。

**误区2：力场叠加顺序影响结果**
Niagara 的 Particle Update 阶段按模块列表**从上到下顺序执行**，同帧内各力场加速度线性叠加，最终一次性更新速度。理论上顺序不影响同帧合力结果，但若某模块直接修改 `Particle.Velocity`（而非输出加速度增量），则顺序影响后续模块的输入值，需注意区分"Add Force"型与"Set Velocity"型模块。

**误区3：在 Particle Spawn 阶段添加持续力场**
力场模块若被错误放置在 **Particle Spawn** 阶段而非 **Particle Update** 阶段，则仅在粒子出生帧执行一次，等价于一次性速度冲量，而非持续作用力。表现为粒子忽略重力弯曲，径直飞出后保持匀速直线运动。

**误区4：$r_{min}$ 设为 0 导致数值爆炸**
吸引/排斥力模块的最小距离 `Min Distance` 若设为 0，当粒子恰好经过引力中心时，分母趋近零，加速度趋近无穷大，导致粒子在单帧内获得极大速度，瞬间飞出视野。始终保持 `r_{min} ≥ 1 cm`。

---

## 知识关联

### 与粒子生命周期的关系

力场模块的作用效果直接依赖粒子生命周期（Particle Lifetime）的长短。相同的重力加速度（−980 cm/s²）作用于生命周期 **0.5 秒**的粒子，最终下落距离约