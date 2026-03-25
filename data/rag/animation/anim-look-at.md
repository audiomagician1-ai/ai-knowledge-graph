---
id: "anim-look-at"
concept: "Look At"
domain: "animation"
subdomain: "ik-fk"
subdomain_name: "IK/FK"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Look At（视线跟随约束）

## 概述

Look At 是一种专为头部、眼球或摄像机追踪目标对象而设计的 IK 约束，它通过计算目标点与被控骨骼之间的方向向量，自动驱动骨骼旋转使其"注视"指定目标。与通用 IK 解算器不同，Look At 只处理旋转维度，不涉及位置的逆向求解，因此它本质上是一个单轴或双轴旋转约束，而非完整的多关节 IK 链。

这种约束最早在三维动画软件中以"Aim Constraint"（3ds Max）或"Look At Constraint"的形式出现于 1990 年代末，随后 Maya 将其命名为 Aim Constraint，Blender 则在骨骼约束系统中以 "Damped Track" 和 "Track To" 两种形态提供类似功能。游戏引擎 Unity 在 Animator 系统中通过 `LookAt` 权重参数直接暴露出来，开发者可以在 0 到 1 之间插值控制视线跟随的强度。

Look At 在角色动画中解决了一个极为具体的问题：手动 K 帧为角色的眼球制作追踪动画既繁琐又难以保持精准，而使用 Look At 约束后，动画师只需移动一个"眼神目标"控制器，两只眼球的旋转便会自动同步更新，将本来需要数十帧逐帧调整的工作压缩为对单一控制器的操作。

## 核心原理

### 方向向量计算

Look At 的数学核心是将被约束骨骼的局部轴对齐到目标方向向量。设被约束骨骼的世界空间位置为 **P**，目标点世界空间位置为 **T**，则目标方向向量为：

**D** = normalize(**T** − **P**)

约束系统随后计算从骨骼当前朝向到 **D** 所需的四元数旋转，并将该旋转应用于骨骼。由于只修改旋转而不修改位移，骨骼始终保持在骨架层级中的原始位置。

### 上方向向量（Up Vector）的作用

Look At 约束在确定主朝向后，还需要一个"上方向向量"（World Up 或 Scene Up）来消除绕目标轴滚动的自由度歧义。如果不指定 Up Vector，骨骼在目标移动到正上方或正下方时会出现万向锁现象（Gimbal Lock），导致旋转突变翻转 180°。在 Maya 的 Aim Constraint 中，Up Vector 对象通常是一个独立的定位器（Locator），绑定师会将它放置在角色头顶上方约 100 个单位处，确保任何合理的注视角度都不会与 Up Vector 共线。

### 权重混合与部分追踪

现代 Look At 实现支持 0–1 范围内的权重控制。当权重为 0.5 时，骨骼旋转结果是"无追踪状态"与"完全追踪状态"的球面线性插值（Slerp）。这在角色只需要用余光瞄向目标、而非转头直视时非常实用。Unity 的 `SetLookAtWeight(float weight, float bodyWeight, float headWeight, float eyesWeight, float clampWeight)` 函数提供了从身体到眼球的分层权重控制，允许眼球先追踪（眼球权重1.0），当偏转超过阈值后头部才跟随转动（头部权重0.6），模拟真实人类的注视反射。

### 角度限制与夹角约束

为防止眼球或头部旋转超出生理极限，Look At 通常配合角度限制（Clamp Angle）使用。人眼水平方向的舒适转动范围约为左右各 35°，极限约为 50°；头部水平转动舒适范围约为左右各 60°。超出这些范围的目标点，约束会自动将旋转值钳制在最大角度，骨骼不再继续跟随目标，视觉上表现为角色"目送"目标消失在视野边缘。

## 实际应用

**角色眼球绑定**：在标准的面部绑定流程中，动画师会在角色头部骨骼的子层级下创建两块眼球骨骼，并为每块眼球骨骼添加 Look At 约束，约束目标指向一个放置于角色正前方约 50–100 厘米处的"眼神控制器"。移动这一个控制器，两只眼球同时追踪，实现聚焦。若需制作斗鸡眼或各自独立的眼神，则为每只眼球设置单独的目标控制器。

**摄像机兴趣点追踪**：影视级动画中，摄像机骨骼常被添加 Look At 约束，将目标设置为角色胸口或头部的定位器，确保摄像机无论如何移动始终对焦于演员身体中心，常用于运动捕捉后期的摄像机修正。

**游戏 NPC 感知系统**：在 Unity 或 Unreal Engine 的 NPC 中，Look At 权重会根据 NPC 与玩家的距离动态调整：玩家进入 10 米范围内权重从 0 线性升至 1，NPC 开始注视玩家；玩家离开后权重以 0.5 秒的缓动时间降回 0，避免视线"弹回"造成的不自然感。

## 常见误区

**误区一：认为 Look At 会解算整条骨骼链**
Look At 只旋转被约束的单块骨骼（或头+颈的少数几块），它不会像全身 IK 解算器那样牵动脊椎、肩膀等上游骨骼。若需要角色整个上半身转向目标，必须对脊椎各段骨骼分别添加带不同权重的 Look At 约束，或改用支持全身 IK 的解算方案。

**误区二：忽略 Up Vector 导致翻转问题**
许多初学者在设置 Look At 时不指定 Up Vector，当目标移动到约束骨骼的正上方或正下方附近时，骨骼会发生 180° 的突变翻转。这不是软件 bug，而是方向向量与默认世界 Up 轴共线时旋转无法唯一确定的数学必然结果，解决方法唯有正确设置独立的 Up Vector 对象。

**误区三：将 Look At 与 Track To 混为一谈**
在 Blender 中，Track To 约束使骨骼的局部轴持续指向目标但允许任意滚动，而 Damped Track 会以最小旋转量对齐，这两者均不等同于带 Up Vector 的完整 Look At 实现。混用这两种约束进行眼球绑定，会在目标越过骨骼正上方时产生不同程度的滚动错误。

## 知识关联

Look At 建立在逆向动力学（IK）的基础概念之上——理解 IK 是"给定末端效应器目标，逆向求解关节角度"的机制，有助于理解 Look At 为何只处理旋转而非位置。与标准多关节 IK 链（如 FABRIK 或 CCD 解算器处理手臂、腿部）相比，Look At 是 IK 思想在单自由度目标上的简化应用，其计算量仅为通用 IK 解算器的极小子集。

在学习路径上，掌握 Look At 后可自然过渡到面部绑定的整体系统设计，包括理解如何将 Look At 约束与混合变形（Blend Shape）配合，使眼皮随眼球旋转角度自动下压（模拟眼睑追踪），以及如何在动作捕捉重定向流程中为不同比例的角色重新校准眼神目标控制器的位置。