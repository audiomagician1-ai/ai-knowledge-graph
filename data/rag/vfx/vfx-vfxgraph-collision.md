---
id: "vfx-vfxgraph-collision"
concept: "碰撞与交互"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.5
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

# 碰撞与交互

## 概述

在 Unity VFX Graph 中，碰撞与交互系统允许粒子对场景几何体或深度缓冲图像做出物理响应，而不仅仅是在空间中自由飘散。VFX Graph 提供两种截然不同的碰撞实现路径：基于 **Collider** 的精确几何碰撞，以及基于 **Depth Buffer** 的屏幕空间近似碰撞，两者适用于不同的性能预算和视觉需求。

深度缓冲碰撞（Depth Buffer Collision）最早随 Unity 2019.3 的 VFX Graph 正式版本引入，其设计目标是在 GPU 上以极低的 CPU 开销实现数万粒子的实时碰撞检测，避免了传统物理引擎中 CPU 与 GPU 之间昂贵的数据往返（readback）。这一机制对粒子数量超过 10,000 的特效场景尤其重要——使用传统 PhysX 碰撞在此规模下往往导致帧率骤降。

碰撞系统与 VFX Graph 的**事件（Event）机制**深度整合：粒子发生碰撞时可以触发子事件，驱动二级粒子系统（如火花碰撞地面后产生烟雾），这种事件链条完全在 GPU 侧执行，是 VFX Graph 区别于 Shuriken 粒子系统的核心能力之一。

---

## 核心原理

### Collider 几何碰撞

VFX Graph 的 **Collide with Sphere / Box / Plane** 节点系列允许粒子与简单几何体进行精确碰撞。每个碰撞 Block 接受一个 `Radius Scale` 参数，用于缩放粒子自身的碰撞半径（默认为粒子 `Size` 的 0.5 倍）。碰撞响应由以下两个关键参数决定：

- **Elasticity（弹性系数）**：取值范围 0~1，0 表示完全非弹性碰撞（粒子沿法线方向速度归零），1 表示完全弹性反弹，反射公式为 `v' = v - 2(v·n)n`，其中 `n` 为碰撞面法线。
- **Friction（摩擦系数）**：取值范围 0~1，作用于粒子切线方向速度分量，模拟表面摩擦减速。

几何碰撞的优势是精确可预测，但每增加一个 Collider 节点都会在 GPU Compute Shader 中引入额外的循环迭代，多 Collider 场景建议控制在 4 个以内。

### 深度缓冲碰撞（Depth Buffer Collision）

**Depth Buffer Collision** Block 从摄像机的深度缓冲中采样，将粒子的世界坐标反投影到屏幕空间，比较粒子深度与场景深度来判断穿透。若粒子深度大于（即"在场景表面之后"）采样深度值，则视为发生碰撞，并将粒子位置修正回表面。

该方法存在一个固有限制：**屏幕空间盲区**——当碰撞表面位于摄像机背面、被其他物体遮挡，或超出相机视锥体时，碰撞检测完全失效。因此深度缓冲碰撞适合地面灰尘、屏幕前景火花等始终在相机前方的特效，而不适合全方向爆炸碎片。

深度缓冲碰撞还需要在 **HDRP 或 URP** 的 Camera 组件上启用 `Depth Texture` 输出（`DepthTextureMode.Depth`），否则节点将无法获取深度数据，粒子表现为穿透所有表面。

### 碰撞事件与事件触发

VFX Graph 碰撞 Block 内置 **On Death** 和 **On Collide** 两个输出事件槽。勾选 `Kill on Collide` 后，粒子碰撞即死亡并触发 `On Death` 事件；不勾选时触发 `On Collide` 事件，粒子继续存活并反弹。

事件触发通过 **GPUEvent** 节点连接到子 Context（Initialize 上游），实现粒子的"繁殖"行为。例如雨滴撞击地面 → `On Collide` → 触发 `Spawn（Burst，count=3）` → 初始化水花子粒子，整个链条无需任何 C# 脚本介入。事件携带 `EventAttribute`，可将父粒子的位置、速度、颜色等属性传递给子粒子，继承参数通过 **Inherit Source Attribute** Block 接收。

---

## 实际应用

**雨水溅射特效**：主粒子系统模拟雨滴下落，为其 Update Context 添加 `Depth Buffer Collision` Block，设置 `Elasticity = 0.1`（接近非弹性）、`Friction = 0.8`。在 `On Collide` 事件输出端连接 Burst Spawn，子粒子继承父粒子碰撞位置（`Inherit Source Position`）并以径向速度初始化，形成溅射水花。整个场景可稳定运行 50,000 粒子而不产生 CPU 瓶颈。

**弹跳火花特效**：焊接或爆炸场景中的金属火花需要多次弹跳。使用 `Collide with Plane` 节点模拟地面，设置 `Elasticity = 0.6`、`Friction = 0.3`，配合 `Set Velocity from Bounce` 的速度衰减曲线，每次碰撞后粒子速度乘以系数 0.7，实现自然衰减的多次弹跳，而非无限循环。

**粒子与动态物体交互**：将 `Collide with Sphere` 的球体中心绑定到角色骨骼的 `Transform` 属性（通过 Exposed Property），可实现角色行走时拨开周围雪花或尘埃粒子的动态效果，碰撞响应延迟在单帧 Compute Shader 内完成，视觉上无明显滞后。

---

## 常见误区

**误区一：认为深度缓冲碰撞在所有视角下等效于几何碰撞**。实际上，当摄像机俯视角超过约 75° 时，垂直薄壁（如栅栏、楼梯台阶侧面）的深度信息严重失真，粒子会穿透这些表面。此场景应改用 `Collide with Plane` 几何碰撞补充。

**误区二：On Collide 事件会无限触发导致粒子爆炸式增长**。单个粒子在一帧内可能多次满足碰撞条件（尤其在低帧率下），若子 Spawn 不设置 `Count` 上限或父粒子不设置 `Cooldown` 间隔，GPU 缓冲区会在数秒内被撑满。正确做法是在碰撞后立即通过 `Set Alive（false）` 杀死父粒子，或为子系统的 Capacity 设置明确上限。

**误区三：将碰撞节点放在 Initialize Context 中**。碰撞检测必须位于 **Update Context**，因为只有每帧更新时才能对比粒子当前位置与几何体/深度缓冲。放在 Initialize 中节点不报错但完全不产生任何碰撞响应，是初学者最常遇到的无声失效问题。

---

## 知识关联

**前置概念——力与运动**：碰撞响应的速度反射计算建立在粒子已具备速度向量的基础上，`Elasticity` 系数直接作用于由 `Add Velocity` 或重力积累的 `velocity` 属性。没有运动状态的粒子（速度为零）发生碰撞后不产生任何可见的弹跳效果。

**后续概念——输出模式**：碰撞事件触发的子粒子系统通常需要不同于父粒子的渲染输出（如水花用 `Output Particle Mesh`，烟雾用 `Output Particle Quad`），理解碰撞事件链条后自然延伸到如何为子 Context 配置独立的输出渲染管线。

**后续概念——碰撞物理**：本文介绍的是 VFX Graph 内置的简化碰撞模型。`碰撞物理` 章节进一步探讨碰撞系数的物理含义、法线采样精度与 `Radius Scale` 对穿透率的影响，以及如何通过自定义 HLSL Block 实现 VFX Graph 原生节点不支持的摩擦锥（friction cone）计算。