---
id: "physics-interpolation"
concept: "物理插值"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["同步"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 物理插值

## 概述

物理插值（Physics Interpolation）是游戏引擎中协调物理模拟更新频率与渲染帧率之间差异的技术。物理引擎通常以固定时间步长（Fixed Timestep）运行，例如每秒60次（16.67ms/步）或50次（20ms/步），而渲染帧率可能是任意值，如144Hz的显示器会以约6.94ms输出一帧。插值技术负责在两个已知的物理状态之间计算出对应当前渲染时刻的平滑中间状态，从而避免画面因物理步长与渲染步长不同步而产生的抖动和卡顿。

这一技术的必要性源于固定时间步长本身的设计哲学。Glenn Fiedler在2004年的经典文章《Fix Your Timestep!》中系统阐述了为何物理模拟必须使用固定步长——可变步长会导致碰撞检测不稳定、约束求解结果不可复现。但固定步长带来的副作用是，渲染线程无法恰好在每个物理步结束时输出画面，如果直接使用最近一次物理状态渲染，画面更新会呈现出不均匀的"跳帧感"，即使物理本身是正确的。

物理插值解决的是**视觉表现与物理正确性之间的矛盾**，它不改变任何物理计算结果，只影响渲染用的位置和旋转数据。这使开发者可以在保持物理模拟确定性的同时，让玩家看到丝滑的运动曲线。

## 核心原理

### 固定时间步长的累积器模式

物理引擎主循环使用"累积器（Accumulator）"模式：每帧将真实经过的时间（deltaTime）累积到一个变量中，当累积量超过固定步长（如`fixedDeltaTime = 0.02s`）时，执行一次或多次物理步，并将剩余时间留给下一帧。每次物理步结束后，引擎会保存当前步的状态（`stateNew`）并将上一步的状态存入`stateOld`。

```
accumulator += deltaTime
while accumulator >= fixedDeltaTime:
    stateOld = stateNew
    PhysicsStep(fixedDeltaTime)
    accumulator -= fixedDeltaTime
alpha = accumulator / fixedDeltaTime
renderState = Lerp(stateOld, stateNew, alpha)
```

变量`alpha`的范围是\[0, 1\]，代表当前渲染时刻处于上一物理步与下一物理步之间的相对位置。

### 线性插值与球面线性插值

对于物体的**位置**，使用线性插值（Lerp）即可获得良好效果：

$$\vec{p}_{render} = \vec{p}_{old} + \alpha \cdot (\vec{p}_{new} - \vec{p}_{old})$$

对于物体的**旋转**，由于旋转以四元数（Quaternion）表示，直接线性插值会导致角速度不均匀，因此必须使用球面线性插值（Slerp）：

$$q_{render} = \text{Slerp}(q_{old},\ q_{new},\ \alpha)$$

Slerp沿四元数单位超球面的大圆弧进行插值，保证旋转角速度恒定，适合快速旋转的物体（如车轮、陀螺）。

### 外推（Extrapolation）与插值的区别

物理插值是在`stateOld`和`stateNew`之间做**后验插值**——两个端点都是已经计算完成的真实物理状态。与之相对的是**外推（Extrapolation）**，即基于当前状态和速度预测未来位置：`p_render = p_new + velocity * accumulator`。外推延迟更低，但当物体发生碰撞或突然改变速度时会出现明显的"弹回"（snapback）伪影，因此大多数引擎默认使用插值而非外推。Unity的物理系统（PhysX集成）在Rigidbody组件上提供了`Interpolate`（后验插值）和`Extrapolate`（外推）两种模式供开发者显式选择。

## 实际应用

**Unity引擎**中，每个`Rigidbody`组件有`interpolation`属性，默认值为`None`（不插值，直接使用最新物理状态）。将其设为`Interpolate`后，Unity在`FixedUpdate`结束时缓存前一帧位置，在`Update`渲染时按`alpha`混合输出给`Transform`。对于玩家角色控制器这类需要精确视觉反馈的对象，启用插值是标准做法；而静态场景中大量不移动的物体则无需开启，以节省计算开销。

**Godot 4**引擎在3D物理节点（`RigidBody3D`）上同样提供`physics_interpolation_mode`属性，并且引擎全局设置中可通过`ProjectSettings.physics/common/physics_interpolation`一键为所有物理节点启用插值，大幅降低了配置成本。

在赛车游戏中，车轮的视觉Mesh通常是独立节点，其旋转通过物理插值平滑，否则在高帧率显示器上，车轮每物理步跳转一次角度会产生明显的旋转卡顿，即使物理步长达到120Hz也无法完全消除视觉问题。

## 常见误区

**误区一：认为提高固定物理频率可以替代插值。**
将`fixedDeltaTime`从0.02s提升到0.005s（200Hz物理频率）确实减少了步长间隔，但不能从根本上解决问题。在144Hz屏幕上，相邻两帧间隔约6.94ms，仍然与5ms的物理步不对齐，仍会出现周期性的帧率不均匀。更高的物理频率还会成倍增加CPU计算开销。插值的代价几乎为零（仅一次Lerp/Slerp），是正确的解决路径。

**误区二：对所有物体都启用插值，包括触发器和传感器。**
插值仅影响渲染位置（`Transform`），不影响物理碰撞体的实际位置。如果一个触发器的`Rigidbody`开启了插值，其`Transform`（视觉位置）与碰撞体（逻辑位置）会相差最多一个物理步的位移，导致视觉上"碰到了"但实际没有触发，或反之。因此触发器、伤害判定区域等以逻辑为准的对象不应开启插值。

**误区三：插值会引入一帧延迟。**
物理插值确实使渲染状态比最新物理状态落后最多一个`fixedDeltaTime`（如20ms），这在理论上是延迟。但对玩家的体感而言，20ms的渲染延迟远小于人眼对运动不连续性的感知阈值（约50ms），实践中玩家感受到的是"更流畅"而非"更延迟"。

## 知识关联

物理插值建立在**物理场景管理**提供的对象状态存储能力之上——正是场景管理负责维护每个物理体的`stateOld`和`stateNew`双缓冲，插值才有数据可读。理解固定时间步长（Fixed Timestep）的累积器循环是正确实现插值的前提，因为`alpha`的计算直接依赖累积器的剩余量。

在多线程物理引擎（如PhysX的异步模式）中，插值还承担了跨线程安全读取物理状态的职责——渲染线程读取的插值状态是已完成写入的历史数据，避免了与物理线程的数据竞争，是并发架构中额外的工程价值。