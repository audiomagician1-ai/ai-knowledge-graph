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

姿势缓存（Pose Caching）是 Unreal Engine 动画蓝图中的一种优化机制，通过 **Save Cached Pose** 和 **Use Cached Pose** 这两个节点，将某条动画图计算链的输出结果暂存为具名快照，供同一动画蓝图内其他位置多次读取，而无需重新执行该链上的所有节点运算。

这一机制随 UE4 动画蓝图系统的成熟而被正式引入，其设计动机来自真实项目中的性能瓶颈观察：一个典型的第三人称角色动画图通常包含 Locomotion、上半身叠加、IK 修正等多条并行逻辑，若这些分支都独立驱动同一套基础运动状态机，每帧的骨骼变换矩阵计算量将随分支数量线性增长。姿势缓存打断了这种重复计算链，使相同计算只执行一次。

在拥有超过 50 根骨骼的角色上，每次完整的动画图遍历都需要对每根骨骼完成局部空间到组件空间的矩阵运算。若 Final Animation Pose 节点的三条输入分支都引用同一套运动状态机而不使用缓存，等价于该状态机每帧被计算三次。姿势缓存将这一代价压缩为一次，节省的 CPU 时间在大规模 NPC 场景中尤为显著。

---

## 核心原理

### Save Cached Pose 节点的工作机制

**Save Cached Pose** 节点在动画图中充当一个"命名存储点"。用户为其指定一个字符串标识符（如 `LocomotionCache`），节点在每帧动画更新阶段（Update Phase）将上游链传入的 `FPoseContext` 结构体完整复制到蓝图内部的缓存槽中。`FPoseContext` 包含骨骼变换数组、曲线权重表及属性数据，因此缓存的是一帧完整的姿势快照，而非仅仅是某个状态机的状态索引。

Save Cached Pose 节点本身**不改变**姿势数据，它仅是一个透传加复制的操作：上游数据原样流向下游，同时被写入缓存槽。这意味着该节点可以串联在任意动画链的中途，不会打断主数据流。

### Use Cached Pose 节点的读取方式

**Use Cached Pose** 节点通过同名标识符（必须与对应 Save 节点的名称完全匹配，区分大小写）读取缓存槽，并将其作为一个姿势输出引脚供下游节点使用。无论在蓝图图表中创建多少个引用同名缓存的 Use Cached Pose 节点，底层只访问同一份数据副本，不触发任何重新计算。

同一帧内，Save Cached Pose 节点的执行顺序必须早于所有引用它的 Use Cached Pose 节点。动画蓝图的图表求值遵循从 Final Animation Pose 节点反向遍历依赖图的方式，若 Use 节点在图拓扑上处于 Save 节点之前被遍历，将读取上一帧的缓存数据，产生单帧延迟的视觉抖动。正确的布局方式是确保 Save Cached Pose 节点连接到最终输出路径的主干上，Use 节点则用于侧路分支。

### 缓存的作用域与生命周期

每个姿势缓存的作用域严格限定在**同一动画蓝图实例**内，无法跨蓝图读取。缓存槽的生命周期与动画蓝图实例绑定：实例被销毁时缓存同步释放，实例在非激活状态（角色不在视锥或被 LOD 冻结）时缓存不更新，恢复激活后第一帧读取的是停止更新前的最后一份快照。

缓存命名冲突（同一蓝图中两个 Save 节点使用相同名称）会导致后执行的写入覆盖前者的数据，Unreal Engine 编辑器不会对此报错，需要开发者手动保证名称唯一性。

---

## 实际应用

### 基础运动姿势的共享

最常见的用法是将角色的 Locomotion 状态机输出保存为 `BasePose` 缓存，然后在以下三处同时引用：
1. **LayeredBlendPerBone** 节点的 Base Pose 输入（叠加上半身武器动作）
2. **Two Bone IK** 节点链的输入（脚部 IK 贴地修正）
3. **AnimDynamics** 节点的输入（布料或毛发二次运动）

若不使用缓存，Locomotion 状态机将被求值三次，每次为完整的 100+ 骨骼角色执行全套混合树运算。使用 `BasePose` 缓存后，该状态机只计算一次，另外两处消耗降为接近零的内存读取。

### 多线程友好的图表分割

UE5 的动画蓝图支持多线程更新（`bUseMultiThreadedAnimationUpdate = true`）。姿势缓存将复杂动画图分割为若干依赖段，调度器可以将不依赖同一缓存的段分配到不同工作线程并行执行，而依赖同一缓存的段则在 Save 节点完成后顺序读取，兼顾了并行性与数据一致性。

### 动画蓝图调试中的分段测量

在 Unreal Engine 的 **Animation Insights** 工具中，每个 Save Cached Pose 节点的名称会作为独立条目出现在动画线程的 Timing 面板中，显示其上游链的实际耗时（单位：微秒）。利用这一特性，开发者可以在复杂蓝图中精确定位高耗时节点段，而无需逐节点断点调试。

---

## 常见误区

### 误区一：认为缓存等同于跨帧复用

姿势缓存每帧都会被 Save 节点重新写入，它解决的是**同一帧内**多个分支重复计算的问题，而非将某一帧的结果延用到后续帧。若要实现跨帧的姿势保留（如惯性化混合），需要使用 `Inertialization` 节点或手动管理 `FPoseSnapshot`，这与姿势缓存是完全不同的机制。

### 误区二：Use Cached Pose 可以放置在任意位置

部分开发者认为只要创建了 Save 节点，对应的 Use 节点放在图表任何位置都能正确工作。实际上，若 Use 节点在图求值顺序上处于 Save 节点之前（例如 Use 节点连接到了主干而 Save 节点位于侧分支），将持续读取上一帧的数据，表现为动画有一帧的滞后或在快速状态切换时产生可见的姿势跳变。

### 误区三：缓存节点数量越多性能越好

每个 Save Cached Pose 节点的执行本身涉及一次 `FPoseContext` 的内存深拷贝，对于 200 根骨骼的角色，这次拷贝约需复制 200 个 `FTransform`（每个 48 字节，共约 9.6 KB）。如果某条动画链只被引用一次，增加缓存节点反而引入了不必要的内存拷贝开销。姿势缓存的净收益仅在**同一缓存被两个或两个以上 Use 节点引用时**才为正值。

---

## 知识关联

**前置概念——动画图（AnimGraph）：** 理解姿势缓存必须先掌握动画图的节点求值顺序：AnimGraph 从 Final Animation Pose 反向遍历依赖关系图，每个节点在被"拉取"时才执行计算。正是这种拉取式求值模型导致了多分支重复计算的问题，姿势缓存通过引入命名存储点将拉取式转换为局部推送式，从而打破重复计算链。

**后续概念——动画蓝图优化：** 姿势缓存是动画蓝图优化体系中最基础的图表级手段。在此基础上，进一步的优化手段包括：使用 **Animation Budget Allocator** 按距离动态降低更新频率、将无交互逻辑迁移到 **LinkedAnimGraph** 以复用共享实例、以及在 UE5 中使用 **Property Access** 减少蓝图函数调用开销。这些手段共同构成了从单角色到百人 NPC 场景的完整优化路径，而姿势缓存是其中唯一直接作用于单帧骨骼计算次数的节点级工具。