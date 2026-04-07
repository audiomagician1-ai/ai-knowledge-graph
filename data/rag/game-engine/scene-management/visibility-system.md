---
id: "visibility-system"
concept: "可见性系统"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 3
is_milestone: false
tags: ["剔除"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 可见性系统

## 概述

可见性系统（Visibility System）是游戏引擎场景管理模块中用于**预判或实时计算哪些物体无需渲染**的一组技术集合，其核心目标是在发送 draw call 前尽可能剔除摄像机永远看不到的几何体，从而减少 GPU 负载。与视锥剔除只检查"物体是否在摄像机锥体范围内"不同，可见性系统进一步回答"即使在视锥内，该物体是否被其他不透明几何体遮挡"这一更难的问题。

可见性系统的理论基础可追溯至 1969 年 Schumacker 等人提出的优先级算法，但真正工程化落地是在 1990 年代 Quake 引擎（id Software，1996 年发布）将 **PVS（Potentially Visible Set，潜在可见集）** 写入关卡编译阶段，成为室内场景渲染加速的经典范例。此后 Portal 系统、Distance Culling 相继成为标准工具，并被 Unreal Engine、Unity、Godot 等主流引擎内置支持。

可见性系统的重要性在于：一个包含 10 万个三角形的室内场景，若不使用任何可见性判断，每帧全部提交的 draw call 可能超过数千次；引入 PVS 后，同一视角实际需渲染的房间往往不超过 3-5 个，draw call 可降低 80% 以上。这直接决定了能否在主机和移动端稳定维持 60 fps。

---

## 核心原理

### PVS（潜在可见集）

PVS 是一种**离线预计算**方案。关卡被划分为若干凸多边形单元（Cell），编译器对每一对 Cell 之间的可见性进行射线采样，结果压缩存储为位掩码（bitmask）。运行时引擎只需：
1. 查询摄像机当前所在 Cell 的索引；
2. 取出该 Cell 对应的 PVS 位数组；
3. 仅渲染位为 1 的 Cell 内的物体。

Quake 的原始 PVS 使用**行程编码（Run-Length Encoding）** 压缩位数组，一张 100 个 Cell 的地图的 PVS 数据通常只有几十 KB。PVS 的缺点是无法处理动态改变的遮挡关系（如可开关的门），也不适用于开放大世界——Cell 数量一旦超过数千个，预计算时间和内存开销将急剧上升。

### Portal 系统

Portal 系统将场景拆分为**房间（Room）和门洞（Portal）**两类元素。Portal 是连接相邻两个 Room 的凸多边形窗口。渲染时从摄像机所在 Room 出发，对视锥与每个可见 Portal 做裁剪（Clip）：

> 新视锥 = 原视锥 ∩ Portal 平面集合

递归执行此裁剪直到视锥退化为空或所有 Portal 均已遍历。这意味着 Portal 系统是**运行时动态**计算的，天然支持可开关门（把门关闭等同于移除该 Portal），且精度高于 PVS——只有真正能通过 Portal 链看到的 Room 才会被渲染。代价是递归深度过大（Portal 链超过 8-10 层）时 CPU 开销显著增加。Unreal Engine 3/4 的 Anti-Portal（遮挡体）正是 Portal 思想的逆向扩展：用凸包体标记"摄像机绝对无法穿透此区域看到背面的物体"。

### Distance Culling（距离剔除）

Distance Culling 按物体距摄像机的距离设置**剔除距离阈值**，超过阈值的物体直接跳过渲染。Unreal Engine 中通过 `Cull Distance Volume` 组件实现分级剔除：

```
剔除条件：Distance(Camera, Object) > CullDistance
```

其中 `CullDistance` 可按物体尺寸分层设置，例如直径小于 1 m 的道具在 50 m 外剔除，直径大于 10 m 的建筑在 300 m 外剔除。Distance Culling 计算成本极低（仅一次浮点比较），适合开放世界中大量植被、石块等细节物体的管理，但无法处理遮挡——即便物体在距离阈值内、被山体完全遮挡，它仍会被提交渲染。因此 Distance Culling 通常与 Hardware Occlusion Query 或软件光栅化遮挡（如 Unreal 的 Software Occlusion Culling）联合使用。

### Hardware Occlusion Query

GPU 提供 `glBeginQuery(GL_SAMPLES_PASSED)` / `glEndQuery` 等接口，允许引擎先用简化的包围盒对潜在被遮挡物体发起查询，若返回通过像素数为 0，则下一帧跳过该物体的完整绘制。此方法存在**1-2 帧的延迟**（GPU 异步返回结果），快速移动时可能出现短暂的"物体闪现"（Popping）伪影，需要结合 Temporal 缓存策略缓解。

---

## 实际应用

**室内射击游戏（如《反恐精英》地图）**：编译阶段生成 PVS，玩家在走廊中时，背后完整的房间及其中的所有 Prop 均不提交，将复杂关卡的平均渲染 Cell 数从全部 200+ 压缩到每帧约 8-15 个。

**开放世界 RPG（如《原神》移动端优化）**：Distance Culling 对草丛（每株草约 200 三角形）设置 30 m 剔除距离，并在 15 m 处切换为 Billboard（公告板），将草地 draw call 从数千减少到数百，使骁龙 870 设备维持 60 fps 成为可能。

**Portal 系统在 Valve Source 引擎**：《传送门》系列的传送门本身即是可见性 Portal——玩家通过传送门看到另一个房间时，Source 引擎执行两遍完整的 Portal 裁剪渲染，渲染嵌套视图最多递归 2 层以平衡效果与性能。

---

## 常见误区

**误区一：PVS 和视锥剔除做的是同一件事**
视锥剔除只判断物体是否在摄像机六个裁剪平面内，不考虑遮挡。PVS 判断的是"即使在视锥内，该 Cell 是否能被本 Cell 看到"——两者独立且应叠加使用。在 Quake 中，PVS 过滤先于视锥测试执行，这两道过滤的组合才构成完整的早期剔除流水线。

**误区二：Distance Culling 设置越激进渲染越快**
将所有物体的剔除距离统一设为极小值（如 20 m）会导致玩家移动时大量物体频繁进出剔除状态，产生明显的 Popping 闪烁，同时频繁的状态切换本身也引入 CPU 排程开销。正确做法是按物体包围球半径比例配置剔除距离：`CullDistance ≈ k × BoundingSphereRadius`，其中 k 通常取 50-100，保证物体在视觉上足够小时才消失。

**误区三：Portal 系统适合所有场景类型**
Portal 系统要求场景能被合理划分为凸多边形 Room，对于开放世界、地形起伏或大量异形连通区域，Portal 划分的工作量和运行时递归开销均不可接受。《荒野大镖客：救赎 2》等开放世界大作主要依赖 Distance Culling + GPU Occlusion Query，而非 Portal 系统。

---

## 知识关联

**前置概念——视锥剔除**：视锥剔除是可见性系统的第一道防线，在调用任何 PVS 或 Portal 查询之前，引擎先通过视锥的六平面测试丢弃明显在视野外的物体，这使得可见性系统的候选对象集合大幅缩小，降低后续查询开销。

**后续概念——场景优化综合**：掌握可见性系统后，场景优化综合会将其与 LOD（细节层次）、静态/动态批处理（Static/Dynamic Batching）、间接渲染（GPU Driven Rendering）等技术整合，形成完整的渲染裁剪-提交流水线。例如 Unreal Engine 5 的 Nanite 虚拟几何体在微三角形层面重新定义了可见性粒度，但其底层仍依赖 Hierarchical Z-Buffer（HZB）实现高效的遮挡剔除，是 Distance Culling 和 Hardware Occlusion Query 思想的延伸。