---
id: "world-origin-shifting"
concept: "世界原点偏移"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 3
is_milestone: false
tags: ["大世界"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 世界原点偏移

## 概述

世界原点偏移（World Origin Shifting，也称 Floating Origin）是一种专门针对超大开放世界游戏中浮点精度退化问题的场景管理技术。其核心操作是：当玩家摄像机（或角色）距离世界坐标系原点（0, 0, 0）超过某个阈值距离时，将整个场景中所有物体的坐标整体平移，使摄像机重新回到靠近原点的位置，而玩家感知不到任何变化。

这一技术的需求源于 IEEE 754 单精度浮点数的精度限制。32位浮点数在表示距离原点约 10,000 米（10km）的坐标时，精度已退化到约 1mm 量级；到 100,000 米时精度仅剩约 1cm；而在星球或星系尺度（数百万至数十亿米）下，精度退化严重到物体会出现肉眼可见的抖动和错位，这种现象通常被称为"大世界抖动"（Large World Jitter）。《无人深空》《精英危险》《KSP》等太空游戏以及《荒野大镖客》《GTA》系列等大地图游戏都曾面对或使用了这一技术。

世界原点偏移方案允许游戏的逻辑地图坐标（往往以双精度 double 存储）可以无限扩展，而渲染坐标始终保持在浮点精度最高的原点附近，两套坐标系之间的差值即为当前的"原点偏移量"（Origin Offset Vector）。

## 核心原理

### 浮点精度退化的数学本质

IEEE 754 单精度浮点数的有效尾数为 23 位，可表示的相对精度约为 2⁻²³ ≈ 1.19×10⁻⁷。因此在坐标值为 X 处，相邻两个可表示浮点数之间的间距（机器精度）约为 `ε = X × 1.19×10⁻⁷`。在 X = 10,000m 时 ε ≈ 0.0012m（约 1.2mm）；在 X = 1,000,000m（1000km）时 ε ≈ 0.119m（约 12cm）。顶点着色器和物理引擎大量使用 float32 运算，当坐标绝对值过大时，这些运算的舍入误差会逐帧累积成视觉抖动。

### 偏移触发与坐标变换

实现世界原点偏移需要维护一个全局向量 `WorldOffset`（建议以 `double` 或 `int64` 厘米精度存储）。当摄像机的逻辑坐标满足 `|LogicPos| > Threshold`（常见阈值为 2,000m 至 10,000m，具体取决于引擎精度要求）时触发偏移。偏移步骤如下：

1. 计算偏移量 `Δ = LogicPos_camera`（即把摄像机移回原点所需的位移）
2. 对场景中**所有**实体执行 `RenderPos -= Δ`
3. 累加全局偏移 `WorldOffset += Δ`
4. 摄像机渲染坐标归零（或归至近原点位置）

任意实体的逻辑世界坐标可随时通过 `LogicPos = RenderPos + WorldOffset` 还原，用于游戏逻辑、存档、网络同步等需要精确坐标的系统。

### 各子系统的同步处理

世界原点偏移最棘手的工程挑战在于**所有持有世界坐标的系统都必须同步响应**偏移事件，否则会出现坐标系不一致导致的碰撞错位、粒子系统位置漂移、AI 导航网格偏差等问题。需要处理的系统通常包括：

- **物理引擎**：PhysX、Bullet 等物理引擎内部也使用 float32，必须在偏移时同步移动所有刚体、碰撞体的物理坐标；Unreal Engine 5 在其 `UWorld::SetNewWorldOrigin()` 函数中向所有 `IWorldPartitionStreamingSourceProvider` 广播偏移事件。
- **粒子与特效**：每个活跃粒子的位置需要平移，或改为以相对坐标存储。
- **流式加载（World Streaming）**：配合世界组合（World Composition）或 World Partition 使用时，偏移会改变各 Level Tile 的加载判定中心，需要用逻辑坐标而非渲染坐标进行距离计算。
- **网络同步**：多人游戏中每个客户端的 `WorldOffset` 可能不同，服务器和客户端之间传输坐标必须使用逻辑坐标（double 精度），客户端收到后减去本地 `WorldOffset` 再写入渲染坐标。

## 实际应用

**Unreal Engine 的内置支持**：UE4 及 UE5 内置了 `Enable World Origin Rebasing` 选项（位于 World Settings），默认触发阈值为距原点 2,097,152cm（约 20km）。启用后引擎在 `Tick` 阶段自动检测摄像机距离并调用 `UWorld::RequestNewWorldOrigin()`，开发者可重写 `AWorldSettings::OnWorldOriginLocationChanged()` 来处理自定义子系统的同步。

**KSP2（坎巴拉太空计划2）**的实现案例：游戏中行星间距离可达数亿米，开发团队使用双精度逻辑坐标系（称为"Scaled Space"与"Local Space"两套坐标系切换），在飞船距离行星表面 100km 以内时切换到以飞船为原点的局部空间，并将星球整体平移至该原点附近渲染，这是世界原点偏移思路的变体应用。

**自定义引擎中的整数坐标方案**：部分工作室（如开发《我的世界》的 Mojang）选择以整数方块坐标（int32 块坐标 + float 块内偏移）代替纯浮点世界坐标，本质上是把世界原点偏移的精度保障硬编码进坐标表示结构中，避免了动态偏移的系统同步开销。

## 常见误区

**误区一：只移动摄像机，不移动场景**

初学者常误认为只需将摄像机的渲染矩阵做一个大数值的平移变换即可解决抖动问题。实际上，顶点着色器收到的顶点坐标本身就已经是精度退化的浮点值，GPU 在 VS 阶段做矩阵乘法之前精度损失就已发生。正确做法是在 CPU 侧将所有物体的坐标平移到原点附近，再上传给 GPU，而不是在 GPU 侧用一个大数值的视图矩阵来"修正"。

**误区二：偏移一次即可永久解决**

世界原点偏移不是一次性操作，而是一个持续触发的循环机制。玩家在超大世界中不断移动，坐标会再次偏离原点，因此引擎必须周期性地检测并多次执行偏移。若设置的触发阈值过大（如 50km），则在触发之前的区间内精度问题依然存在，阈值应根据游戏所需最小精度反推：`Threshold ≤ MinPrecision / 1.19×10⁻⁷`。

**误区三：偏移量用 float 存储即可**

`WorldOffset` 本身如果用 float32 存储，在累加多次偏移后同样会有精度损失，导致逻辑坐标反推不准确。`WorldOffset` 必须使用 double（64位）或整数（如微米/厘米级 int64）存储，才能保证逻辑坐标的精度在整个游戏会话期间不退化。

## 知识关联

世界原点偏移建立在**世界组合（World Composition）**的基础上：世界组合将地图拆分为多个 Level Tile 并以流式方式加载卸载，但这些 Tile 的加载判定距离和坐标依然是浮点数，在超大地图时仍会遇到精度问题。世界原点偏移为世界组合提供了运行时的坐标精度保障，两者在 Unreal Engine 的大地图管线中通常配合使用——World Composition/World Partition 负责管理哪些区块被加载，世界原点偏移负责保证已加载区块的渲染精度。

在技术演进方向上，部分引擎（如 Unity DOTS 和 Unreal 5 的 Large World Coordinates）已在引擎层面将渲染管线的关键路径升级为 double 精度，使世界原点偏移的触发阈值可以推迟到约 10¹⁵ 米量级，覆盖了绝大多数游戏场景的需求，但在移动端和主机平台上 double 精度的 GPU 性能开销仍是权衡因素，使世界原点偏移技术在相当长时间内仍具有重要的工程实践价值。