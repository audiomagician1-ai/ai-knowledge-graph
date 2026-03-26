---
id: "vfx-niagara-collision"
concept: "碰撞检测"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 碰撞检测

## 概述

碰撞检测（Collision Detection）是Niagara粒子系统中用于判断粒子是否与场景几何体发生接触的计算过程。在Unreal Engine 5的Niagara框架中，碰撞检测通过粒子位置与场景深度缓冲（Depth Buffer）或物理碰撞体（Physics Collider）的比对，实现粒子在撞击地面、墙壁或动态物体时产生真实的弹跳、滑动或消亡效果。

Niagara碰撞系统在UE4.26引入GPU碰撞方案之后得到显著扩展，允许数十万个粒子同时进行场景碰撞计算而不完全依赖CPU。这一能力使得火花飞溅、雨滴打地、沙尘爆炸等需要大量粒子与场景互动的效果得以实现。与旧版Cascade系统相比，Niagara的碰撞模块是以独立的模块（Module）形式插入粒子更新阶段（Particle Update Stage），具有更高的可定制性。

碰撞检测的重要性不仅在于视觉真实感，更在于它作为事件触发的前置条件——粒子碰撞到表面后可以产生Collision Event，进而驱动二次粒子发射、贴花生成或声音播放等后续逻辑。

## 核心原理

### 场景深度碰撞（Scene Depth Collision）

Niagara中最常用的碰撞方式是基于场景深度缓冲的GPU碰撞。其工作原理是：每帧将粒子的世界空间位置投影到屏幕空间，然后与GBuffer中的深度值（Depth Value）进行比较。若粒子的投影深度大于场景深度，说明粒子已"穿入"几何体，触发碰撞响应。

此方法的核心参数包括 **Radius Bias**（半径偏移，默认值约10单位，防止粒子穿透）和 **Depth Buffer Thickness**（深度缓冲厚度，控制薄表面双面碰撞检测范围）。其基本判断公式为：

> **碰撞条件**：`depth_particle > depth_scene + RadiusBias`

场景深度碰撞的局限性在于仅能检测相机可见区域内的几何体，粒子一旦离开屏幕便失去碰撞参考，适合特写特效而非全局模拟。

### 物理Actor碰撞（Physics Actor Collision）

CPU粒子可以使用Niagara的 **Collision Query** 模块，通过向物理世界发射射线（Line Trace）或形状扫描（Shape Sweep）来检测碰撞体。每个粒子每帧发出一条从上一帧位置到当前位置的射线，若命中UPhysicsBodyComponent或StaticMesh的碰撞通道，则记录碰撞法线（Hit Normal）和碰撞点位置（Hit Location）。

这种方式支持动态物体（如移动的车辆、角色布娃娃）的碰撞检测，且不受摄像机视野限制，但每个粒子每帧产生一次物理查询，对于超过1万个粒子的系统会造成显著的CPU性能开销。因此建议将射线长度（Trace Length）限制在粒子速度的1.2倍以内，避免不必要的长距离查询。

### 碰撞响应计算

粒子碰撞后的速度反射基于物理反弹公式：

> **V_reflect = V - 2 × (V · N) × N × Restitution**

其中 `V` 为碰撞前速度向量，`N` 为碰撞面法线，`Restitution`（弹性系数，范围0.0~1.0）决定能量保留比例。Niagara还提供 **Friction** 参数，用于在切线方向衰减速度，模拟粒子沿表面滑动的摩擦效果。当Restitution设为0时粒子完全贴合表面，适合模拟泥土或水滴；设为0.8以上则产生明显弹跳，适合金属火花。

## 实际应用

**雨滴打地效果**：将粒子系统的Collision模块设置为Scene Depth模式，Restitution设为0.05（近乎无弹跳），在碰撞事件触发后生成溅射贴花（Decal Spawner）和短暂的环形波纹粒子。深度碰撞的Radius Bias调整为5单位确保雨滴紧贴地面而不悬浮。

**金属火花碰撞**：使用GPU粒子配合Scene Depth Collision，Restitution设为0.6~0.75，同时开启 **Kill On Contact** 选项的反面——保留粒子并在碰撞后切换渲染材质（从发光橙色渐变为暗红色），模拟火花落地后逐渐熄灭的过程。

**爆炸碎片与动态物体交互**：当需要碎片粒子打中可破坏物体时，必须使用CPU模式的Physics Actor Collision，并将碰撞通道（Collision Channel）设置为 `ECC_Destructible`，确保射线查询只命中可破坏Actor而非地面静态网格，减少无效查询数量。

**雪地足迹积雪效果**：利用碰撞检测记录的Hit Location，结合Niagara的Persistent ID系统，将粒子碰撞点坐标写入Render Target纹理，驱动雪地材质的置换贴图，实现粒子与地形的持久性交互痕迹。

## 常见误区

**误区一：认为GPU碰撞（Scene Depth）可以检测所有场景几何体**。实际上Scene Depth碰撞只能检测当前帧GBuffer中渲染的表面，对于半透明材质（Translucent Material）的网格，由于它们不写入深度缓冲，粒子会直接穿透。需要对这类物体额外添加不可见的Opaque碰撞代理网格。

**误区二：Restitution越高模拟越真实**。高弹性系数（如0.95）在多次弹跳后粒子速度衰减极慢，配合重力模拟时粒子会出现无法静止的"永动"抖动问题（Jittering Artifact）。解决方法是当粒子速度低于阈值（建议50单位/秒）时强制将Restitution临时降为0，或直接销毁粒子。

**误区三：对数万GPU粒子同时开启物理Actor碰撞**。GPU粒子的物理射线查询需要回读GPU数据到CPU，这一过程在Niagara中会引发 **GPU Readback** 同步等待，导致主线程卡顿。GPU粒子必须使用Scene Depth碰撞；仅在CPU粒子数量可控（通常低于5000个）时才使用物理Actor碰撞。

## 知识关联

碰撞检测建立在**力场与运动**模块的基础之上：粒子必须先拥有速度向量（Velocity）和位置更新逻辑，碰撞检测才能计算出有意义的反射速度。若粒子在运动模块中使用了自定义积分器（Custom Integrator），需确保积分步长与碰撞检测的采样频率一致，否则高速粒子会出现穿透（Tunneling）问题。

碰撞检测完成后，自然衔接到**事件系统（Event System）**：Niagara的Collision Event Handler可以捕获每次碰撞并作为事件源，向其他发射器（Emitter）广播碰撞数据，如Hit Location和Hit Normal，用于二次特效生成。

在更进阶的**碰撞物理**学习中，将涉及连续碰撞检测（CCD，Continuous Collision Detection）防止穿透，以及基于位置的动力学（PBD）在Niagara Fluids中的碰撞约束求解，这些内容是本节反射向量计算的数学扩展。