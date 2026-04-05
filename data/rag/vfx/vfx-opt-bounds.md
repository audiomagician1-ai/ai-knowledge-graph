---
id: "vfx-opt-bounds"
concept: "包围盒优化"
domain: "vfx"
subdomain: "vfx-optimization"
subdomain_name: "特效优化"
difficulty: 2
is_milestone: false
tags: ["基础"]

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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 包围盒优化

## 概述

包围盒优化是针对粒子系统的 Bounds（包围盒）进行精确设置，从而避免 GPU 在视锥体剔除（Frustum Culling）阶段错误地渲染或错误地剔除粒子系统的一种性能优化手段。Unity 中每个粒子系统都有一个轴对齐包围盒（AABB，Axis-Aligned Bounding Box），引擎依据该 AABB 是否与摄像机视锥体相交来决定是否提交该粒子系统的渲染调用（Draw Call）。

包围盒的概念在实时图形渲染中由来已久，最早广泛应用于 20 世纪 90 年代的游戏引擎中，用于加速场景树（Scene Tree）的剔除计算。对于粒子系统而言，由于粒子是动态生成并实时更新位置的，引擎默认会每帧重新计算其 AABB，这一操作在粒子数量庞大时会产生显著的 CPU 开销。通过手动预设一个足够准确的固定 Bounds，可以完全跳过这一逐帧计算过程。

包围盒设置过大或过小都会引发问题：过大的 Bounds 会导致粒子系统在摄像机已无法看到任何粒子时依然提交 Draw Call，浪费渲染资源；过小的 Bounds 会导致部分粒子仍在视口内时系统就被过早剔除，产生粒子突然消失的视觉穿帮。因此，准确设置 Bounds 是该优化的关键所在。

---

## 核心原理

### AABB 与视锥体剔除的工作机制

Unity 的 Particle System 在 Inspector 面板中提供 `Bounds` 字段，对应 `ParticleSystem.bounds` 属性，其数据类型为 `Bounds`（包含 `center` 和 `size` 两个 `Vector3` 参数）。引擎每帧在 Culling 阶段将该 AABB 与当前摄像机的六个视锥面做相交测试，测试算法复杂度为 O(1)，相比逐粒子位置更新的 O(n) 开销极低。当 `Custom Bounds` 未启用时，Unity 默认开启 `Automatic`模式，每帧遍历所有存活粒子坐标来重建 AABB，当粒子数达到 500 以上时，这一步骤在 CPU Profile 中可见的耗时通常超过 0.1ms。

### 手动设置 Bounds 的参数计算方法

要准确确定自定义 Bounds 的 `size`，需要综合考虑三个因素：粒子的最大存活距离、粒子的最大缩放值（`Start Size` 的最大值）以及粒子是否受重力或外力影响后的最终偏移量。以一个从原点向上喷射、初速度最大为 5 单位/秒、存活时间最长为 2 秒的火焰特效为例，粒子在 Y 轴方向最大位移约为 10 单位，加上最大粒子尺寸 0.5 单位，Y 轴方向 `size` 应至少设为 11 单位。`center` 则应设置为粒子运动路径的几何中心，本例中 `center.y` 应设为 5.5。

### Custom Bounds 的启用方式与注意事项

在 Particle System 的 `Renderer` 模块中，将 `Bounds` 模式从 `Automatic` 切换为 `Custom Bounds` 后，粒子系统不再执行逐帧 AABB 重算。需要特别注意的是，Custom Bounds 的坐标系为**粒子系统组件所在 GameObject 的本地空间（Local Space）**，因此当粒子系统的 `Simulation Space` 设置为 `World` 时，若父节点 GameObject 发生了非均匀缩放（Non-Uniform Scale），Bounds 的实际世界空间范围会随之变形，需要在设计时额外留余量。此外，`Use Custom Bounds` 选项在 Unity 2019.3 版本后才正式稳定提供 API 支持（`ParticleSystemRenderer.bounds`）。

---

## 实际应用

**移动端爆炸特效的 Bounds 优化**：一个典型的手游爆炸特效通常包含 3 个子粒子系统（火焰、烟雾、火花），默认情况下每个子系统都独立执行 Automatic Bounds 计算。以 Snapdragon 865 设备为测试平台，将这 3 个子系统全部改用 Custom Bounds 后，在同屏 10 个爆炸特效同时播放的场景下，CPU 端粒子系统更新线程的耗时从 2.3ms 降低至 0.8ms，降幅约 65%。

**持续循环的环境粒子（如落叶、雪花）**：这类粒子通常覆盖固定范围区域，是 Custom Bounds 最适合的应用场景。以一个 20×20 单位的落雪区域为例，设置 `center = (0, 5, 0)`，`size = (22, 12, 22)` 即可精确覆盖所有粒子的运动范围，同时避免在摄像机离开区域后依然进行渲染。

**跟随角色移动的特效（如角色脚步尘土）**：此类特效的粒子系统挂载在角色骨骼上，随角色高速移动。由于粒子在 World Space 中快速扩散，若 Custom Bounds 设置过小，当角色快速跑动时会出现粒子被意外剔除的闪烁现象。正确做法是在 Local Space 模式下，将 `size` 适度放大 1.5 倍作为安全余量，以换取剔除精度略微降低但视觉稳定性完全保证的结果。

---

## 常见误区

**误区一：认为 Custom Bounds 越大越安全**
许多开发者为了"一劳永逸"将 Bounds `size` 设置为 `(100, 100, 100)` 这样的极大值。这会导致该粒子系统几乎永远不会被视锥体剔除，即使特效播放已经结束、所有粒子已消亡，其 Draw Call 依然每帧被提交，渲染线程中出现一批空的 Draw Call 占用 GPU 指令队列。正确做法是以粒子实际最大扩散范围为基准，加不超过粒子最大尺寸 2 倍的余量。

**误区二：混淆 Bounds 坐标系与粒子 Simulation Space**
当粒子系统的 `Simulation Space` 为 `World`，但粒子系统组件附加在一个会旋转的 GameObject 上时，部分开发者误以为 Custom Bounds 会跟随世界坐标轴保持固定。实际上 AABB 始终在 GameObject 的 Local Space 中定义，引擎在执行视锥体测试前会将其变换到世界空间。若 GameObject 发生了 90° 旋转，原本在 Y 轴细长的 Bounds 会变换为 X 轴细长，导致粒子意外被剔除。

**误区三：对子粒子系统（Sub-Emitter）忽略单独设置 Bounds**
Unity 中每个子粒子系统（Sub-Emitter）是独立的 ParticleSystem 组件，拥有独立的 Bounds。只对根粒子系统设置 Custom Bounds 而忽略 Sub-Emitter，会导致 Sub-Emitter 依然每帧执行 Automatic 计算，CPU Profile 中仍然可以观察到来自子系统的 `ParticleSystem.Update` 峰值。

---

## 知识关联

**前置知识——CPU Profile**：包围盒优化的必要性需要通过 CPU Profiler 来定量确认。在 Unity Profiler 的 CPU 时间轴中，`ParticleSystem.Update` 和 `ParticleSystem.BuildParticleSystemRenderer` 这两个标记会直接体现 Automatic Bounds 的逐帧计算开销。只有在 Profiler 中观察到这两项耗时异常后，才能有的放矢地对特定粒子系统实施 Custom Bounds 设置，而不是盲目地对所有特效批量修改。

**后续优化——特效池化**：包围盒优化解决的是"已激活的粒子系统是否应该被渲染"这一剔除层面的问题，而特效池化解决的是"粒子系统组件的反复创建与销毁"带来的内存分配开销问题。两者在优化链路上互补：先通过包围盒优化减少每帧渲染提交量，再通过特效池化减少 GC Alloc，共同构成粒子系统性能优化的完整方案。