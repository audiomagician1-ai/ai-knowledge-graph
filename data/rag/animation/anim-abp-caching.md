---
id: "anim-abp-caching"
concept: "姿势缓存"
domain: "animation"
subdomain: "animation-blueprint"
subdomain_name: "动画蓝图"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
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


# 姿势缓存

## 概述

姿势缓存（Pose Caching）是虚幻引擎动画蓝图中的一种计算优化机制，通过 **Save Cached Pose** 节点将某个动画姿势的求值结果存储到命名缓存槽中，再由 **Use Cached Pose** 节点在同一帧内的任意位置反复读取，从而避免对同一动画图分支进行多次冗余求值。这一机制在 UE4 引入动画蓝图架构时同步提供，是动画图执行流中少数能够横向"分叉共享"计算结果的手段之一。

在没有姿势缓存的情况下，若两个混合节点（如 Blend 或 Layered Blend per Bone）都需要使用同一个"基础运动"动画图分支的输出，引擎会对该分支求值两次，每次求值都要完整执行其中所有 AnimNode 的 `Update` 和 `Evaluate` 阶段。对于包含 IK、物理模拟或多层状态机的复杂分支，重复求值会造成显著的 CPU 开销。姿势缓存通过一次存储、多次读取，将该分支的计算代价降低为单次。

## 核心原理

### Save Cached Pose 与 Use Cached Pose 的执行时序

动画蓝图的求值遵循从输出端向输入端反向遍历的拓扑顺序。**Save Cached Pose** 节点在第一次被遍历到时执行完整的子图求值，并将结果姿势（一组骨骼变换数据）写入以节点名称标识的缓存槽。在同一帧内，后续所有引用该缓存名称的 **Use Cached Pose** 节点直接从缓存槽读取数据，不再重新触发子图求值。缓存槽的生命周期仅限于单帧；下一帧开始时缓存标记重置，Save Cached Pose 重新执行子图。

### 缓存槽的命名与作用域

每个 Save Cached Pose 节点在创建时必须指定一个唯一的字符串名称（如 `LocomotionCache`）。同一动画蓝图实例内，相同名称的 Use Cached Pose 节点共享同一缓存槽；不同动画蓝图实例之间缓存槽完全隔离，不存在跨实例读取的情况。若在同一蓝图中定义两个同名的 Save Cached Pose 节点，编译器会报错，因为这将产生写入冲突。

### 姿势数据的存储结构

缓存槽存储的是一帧内所有受控骨骼的局部空间变换，数据格式为 `FCompactPose`，其中包含位移（Translation）、旋转（Rotation，四元数）和缩放（Scale）三个分量。对于一个拥有 100 根骨骼的角色骨架，缓存一次姿势需要存储 100 × (3 + 4 + 3) = 1000 个浮点数，内存开销约为 4 KB。这意味着姿势缓存是以空间换时间的典型策略：每增加一个命名缓存槽，就额外占用与骨骼数量正相关的内存。

### 与动画图求值的关系

在动画蓝图的 AnimGraph 中，姿势缓存不能跨越线程边界使用——Save 与所有对应的 Use 节点必须位于同一 AnimGraph（主图或同一个子动画蓝图实例）中。若将 Save Cached Pose 放置在 AnimGraph 之外（例如 EventGraph），编译器同样会报错，因为 EventGraph 不参与姿势求值流水线。

## 实际应用

**全身运动 + 上半身叠加的共享基础姿势**：角色的下半身行走状态机输出一个完整姿势，同时需要作为全身混合和上半身叠加的基础输入。将该状态机连接到一个名为 `BaseLocomotion` 的 Save Cached Pose 节点，下游的 Layered Blend per Bone 和 Blend Poses by Bool 各接一个 `Use Cached Pose（BaseLocomotion）`。这样状态机只求值一次，两个混合节点均能获得完整的行走姿势数据。

**ALS（高级运动系统）中的多层缓存链**：开源插件 Advanced Locomotion System V4 大量使用姿势缓存，在其 AnimGraph 中定义了 `N_BasePose`、`N_OverlayPose` 等多个独立缓存槽，形成缓存→混合→再缓存的多级链式结构，使整个蓝图在保持高度模块化的同时，将重复计算降到最低。

**布娃娃过渡阶段**：在角色死亡时，引擎需要同时将物理模拟姿势与动画姿势混合（`Simulate Physics` 混合节点）。将物理前的动画姿势缓存一帧，供过渡混合的两个输入端复用，可避免在过渡权重从 0 渐变到 1 的过程中重复执行死亡动画的完整求值。

## 常见误区

**误区一：认为 Use Cached Pose 可以读取上一帧的数据**
Use Cached Pose 读取的是**同一帧**内 Save Cached Pose 写入的结果，而非上一帧的快照。缓存槽在每帧求值开始时即被标记为"待刷新"状态，Save 节点在本帧第一次被访问时执行子图并写入，随后同帧的所有 Use 节点读取本帧数据。若需要访问历史帧姿势，需使用 `Bone Driven Controller` 或自行在 C++ 中维护帧间缓冲。

**误区二：在状态机内部使用 Save Cached Pose 来共享状态间的姿势**
Save Cached Pose 节点不能放置在状态机的 State 内部图中；它只能存在于 AnimGraph 的顶层图或子图层（Sub-Anim Instance）中。试图在 State 图内放置 Save 节点，引擎会在编译阶段报告"Cached pose node cannot be used inside a state machine"类错误。状态机内的姿势共享应通过状态机本身的输出端和外部混合节点实现。

**误区三：姿势缓存可以替代 LOD 动画优化**
姿势缓存仅消除同一帧内的重复求值，对单次求值本身的开销没有任何影响。若动画图分支包含代价高昂的 FABRIK IK 节点（每次求值耗时可达 0.1 ms 以上），缓存能避免该节点被调用两次，但不能降低它被调用一次的成本。减少单次求值开销需要结合动画 LOD（在 `SkeletalMeshComponent` 中设置 `AnimUpdateRateParams`）或将 IK 计算移至较低频率的任务线程来实现。

## 知识关联

姿势缓存建立在对**动画图（AnimGraph）**求值顺序的理解之上：只有明确动画蓝图以输出端为根、向输入端深度优先遍历的求值方式，才能正确预判 Save 节点何时触发、Use 节点何时命中缓存。若对 AnimGraph 的拓扑遍历顺序不熟悉，容易误以为两个 Use 节点会各自独立执行子图。

在掌握姿势缓存之后，**动画蓝图优化**这一进阶主题会系统介绍与之配合的其他技术：多线程动画求值（`Multi-Threaded Animation Update`）、动画 LOD 分级、以及将部分动画逻辑下放到 `Worker Thread` 的方式。姿势缓存是动画蓝图优化工具箱中最轻量级且零侵入的手段，通常是优化工作的第一步排查项——在 Unreal Insights 的动画 CPU 追踪中，若同一节点名称出现两次求值记录，即表明存在可用姿势缓存消除的重复计算。