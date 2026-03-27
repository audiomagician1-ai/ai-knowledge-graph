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
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 力场与运动

## 概述

在 Niagara 粒子系统中，力场（Force Field）模块是通过每帧对粒子速度向量施加加速度来改变粒子轨迹的机制。与直接设置粒子位置不同，力场遵循牛顿第二定律 **F = ma**，在粒子的整个生命周期内以累积方式影响运动状态，使粒子表现出物理上真实的惯性感。Niagara 将力场功能拆分为独立模块，分别处理重力（Gravity）、风力（Wind/Drag）、点吸引/排斥（Point Attraction/Repulsion）等不同类型的力，可在同一粒子发射器上叠加多个力场模块。

Niagara 力场系统于 UE4.20 随 Niagara 正式引入，取代了 Cascade 中硬编码的 Attractor 和 Wind Directional Source。这一改变的意义在于：开发者可以用蓝图或 HLSL 自定义力的计算逻辑，而不再受限于引擎预设的固定参数集。在 UE5 中，力场模块还能与 Niagara 的 GPU 模拟路径结合，在单帧内处理数十万个粒子的力计算，这是 Cascade 无法实现的规模。

力场模块的作用范围覆盖粒子的"更新（Update）"阶段，即粒子生成后每帧执行的逻辑。了解力场如何与粒子生命周期的 Spawn 和 Update 阶段协作，是正确配置运动行为的前提。

## 核心原理

### 重力模块（Apply Force: Gravity）

Niagara 内置的 **Apply Force** 模块通过向粒子的 `Physics.Force` 属性累加向量来实现重力效果。默认重力向量为 `(0, 0, -980)`，单位是厘米/秒²，对应现实中 9.8 m/s² 的地球重力。该值可通过模块参数或绑定 Niagara 系统变量 `Engine.Owner.ActorWorldSpaceScale` 动态缩放，以匹配场景的物理比例。重要的是，重力不会直接修改粒子速度，而是写入 Force 缓冲区，在 "Solve Forces and Velocity" 模块中统一积分：新速度 = 旧速度 + (Force / Mass) × DeltaTime。

### 风力与阻力模块（Drag / Wind）

**Drag** 模块实现空气阻力，其核心公式为：`DragForce = -DragCoefficient × Velocity`，即阻力方向始终与当前速度相反，大小与速度成正比。DragCoefficient 典型取值范围为 0.1 至 5.0，值越大粒子越快减速至静止。**Wind** 模块则在 Drag 的基础上引入一个目标速度偏移：`Force = DragCoefficient × (WindVelocity - ParticleVelocity)`，当粒子速度低于风速时加速，高于风速时减速，最终所有粒子都趋向随风飘动的稳态。这两个模块配合使用时，应将 Wind 放在 Drag 之前，否则阻力计算会基于未受风影响的旧速度，导致粒子在高风速下出现抖动。

### 点吸引与排斥模块（Point Attraction Force）

**Point Attraction Force** 模块根据粒子与一个世界空间目标点之间的距离计算向心力或离心力，其强度公式为：

```
Force = Strength × normalize(TargetPos - ParticlePos) × (1 / distance²)
```

`Strength` 为正值时表示吸引，为负值时表示排斥。`FalloffExponent` 参数控制距离衰减的指数，默认值 2.0 对应平方反比定律（类似万有引力），将其改为 1.0 则变为线性衰减，常用于漩涡特效。该模块还包含 `KillRadius` 参数：当粒子距目标点小于此半径时可选择杀死粒子，常用于模拟被黑洞吸收或进入传送门的视觉效果。

### 力的积分与执行顺序

Niagara Update 阶段中，**Solve Forces and Velocity** 模块必须位于所有力模块之后、位置更新之前。若模块堆栈顺序错误（例如将 Gravity 放在 Solve Forces and Velocity 之后），该帧的力将被忽略，表现为粒子无重力。执行顺序是：各力模块累加到 `Physics.Force` → Solve Forces and Velocity 将 Force 积分为速度变化 → `Particle.Velocity` 更新粒子位置。

## 实际应用

**火焰特效**：将重力设为 `(0, 0, 980)`（向上负重力）使火焰粒子上浮，同时添加 Wind 模块设定水平扰动向量 `(15, 0, 0)`，配合 DragCoefficient = 1.5，使火焰呈现随气流摇曳并逐渐减速消散的自然感。

**龙卷风/漩涡特效**：在场景中放置一个 Niagara 系统并绑定一个目标 Actor，使用 Point Attraction Force 将 TargetPos 绑定到 Actor 位置，Strength 设为 500，FalloffExponent 设为 1.0。同时叠加一个 Curl Noise Force 模块增加旋转分量，使粒子绕轴螺旋上升而非直线冲向中心。

**爆炸碎片飞散**：在 Spawn 阶段赋予粒子随机初速度（200\~800 cm/s），Update 阶段加入重力 `(0,0,-980)` 和 DragCoefficient = 0.3 的 Drag 模块，使碎片先高速飞出、受空气阻力减速，再被重力拉弧线落地，完整复现抛体运动轨迹。

## 常见误区

**误区一：直接修改 Particle.Velocity 等同于施加力**
许多初学者在 Update 阶段用 "Set Particle Velocity" 节点实现重力效果，直接每帧叠加速度偏移。这样做绕过了 Solve Forces and Velocity 的积分机制，导致碰撞检测模块（依赖 Physics.Force 数据）无法获得正确的力信息，从而在后续添加碰撞反弹时出现能量计算错误。正确做法是始终通过 Apply Force 系列模块写入 Physics.Force。

**误区二：GPU 模拟下所有力场模块均可使用**
Niagara 的 GPU 模拟路径不支持需要读取场景数据的力场模块，例如依赖物理场景查询的 **Collision Query Force** 和读取 Skeletal Mesh 骨骼位置的 **Skeletal Mesh Location Force**。在 GPU 模拟中使用这些模块会导致编译警告并静默回退到 CPU，造成性能预估与实际结果不符。GPU 模拟仅支持纯数学计算的力模块，如 Gravity、Drag 和 Point Attraction。

**误区三：多力场叠加时忽略量级差异**
将重力（980 cm/s²）与自定义力（如 Curl Noise Force 默认强度 1.0）叠加时，由于量级相差近千倍，噪波力对运动几乎无可见影响。应将 Curl Noise Strength 调整到 200\~500 范围才能与重力抗衡，产生肉眼可见的扰动效果。

## 知识关联

力场模块的计算发生在粒子生命周期的 Update 阶段，因此必须先掌握**粒子生命周期**（Spawn / Update / Event）的执行时序，才能理解为何力场设置在 Spawn 阶段无效。力场对速度的累积修改为**碰撞检测**模块提供了运动方向和速度大小数据——碰撞模块通过追踪粒子在当前速度方向上的射线来预判碰撞点，若力场数据缺失则碰撞响应方向会出错。在掌握基础力场之后，**重力模拟**进一步扩展到使用 Physics Field（物理场）Actor 在世界空间中定义非均匀重力区域，以及与 Chaos 物理系统的数据交换，是对本节平场景重力概念的空间化延伸。