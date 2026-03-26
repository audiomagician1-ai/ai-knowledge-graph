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

# 包围盒优化

## 概述

包围盒优化（Bounds Optimization）是指通过精确设置粒子系统的 `Bounds`（边界框）参数，让引擎的可见性裁剪系统（Frustum Culling）能够正确判断粒子特效是否处于摄像机视野内，从而跳过不可见特效的渲染计算。粒子系统的包围盒是一个轴对齐包围盒（AABB，Axis-Aligned Bounding Box），它以特效的锚点为中心，用长宽高三个数值描述粒子可能到达的最大空间范围。

Unity 引擎默认对粒子系统使用自动包围盒计算，但该自动模式仅根据当前帧的实际粒子位置动态更新，这会导致每帧产生额外的 CPU 计算开销。更严重的是，当粒子系统使用了世界空间模拟（Simulation Space 设为 World）且粒子向远处飘散时，包围盒会持续扩张，触发大量本不必要的 `OnBecameVisible` / `OnBecameInvisible` 回调，干扰裁剪逻辑。

从性能视角看，若包围盒设置过大，摄像机视锥与 AABB 的相交测试会始终返回"可见"，导致该特效永远不会被裁剪，GPU 持续承受无效的绘制调用（Draw Call）。若包围盒设置过小，粒子飞出包围盒后引擎误判特效不可见，产生画面突然消失的视觉错误。因此，准确的包围盒设置是特效性能和画面正确性的双重保障。

---

## 核心原理

### AABB 与视锥裁剪的数学关系

Unity 的视锥裁剪通过检测 AABB 的 8 个顶点是否至少有 1 个位于摄像机视锥体的 6 个裁剪平面内侧来判断可见性。AABB 由中心点 `Center(cx, cy, cz)` 和半尺寸 `Extents(ex, ey, ez)` 定义，其体积为 `V = 8 × ex × ey × ez`。若 Extents 在每个轴上都扩大 1 个单位，体积会以立方关系膨胀，裁剪测试永远通过的概率随之增大。正确做法是将 Extents 设置为粒子在特效生命周期内能到达的最远距离，例如一个向上喷射的火焰特效，粒子最大飞行高度为 3 米、水平扩散半径为 1 米，则应设置 `Extents = (1, 3, 1)`，而非默认的 `(1, 1, 1)` 或无限大的自动模式。

### Custom Bounds 的设置方法

在 Unity Inspector 中，展开粒子系统的 **Renderer** 模块，将 `Bounds Mode` 从 `Auto` 切换为 `Custom`，然后手动填写 `Center Offset` 和 `Size`（即 2 × Extents）。切换为 Custom 模式后，引擎每帧不再重新计算包围盒，消除了动态更新带来的 CPU 开销。对于使用 Local 模拟空间的特效，包围盒随粒子系统对象移动而移动，无需额外处理；对于 World 模拟空间，中心点应始终保持在发射器位置附近，Extents 需覆盖粒子全程轨迹。

### 包围盒与 GPU Instancing 的联动

当同一粒子系统在场景中存在多个实例并启用了 GPU Instancing 时，引擎会使用各实例各自的 AABB 分别做裁剪测试。若某实例的 AABB 过大导致与视锥相交，该实例的所有粒子都会进入渲染管线，无法被实例级裁剪优化掉。因此在批量实例化特效的场景（例如同时存在 50 个爆炸粒子实例）中，精确的 Custom Bounds 能让视野外的实例以整批为单位被裁剪，将 GPU 的粒子处理量从 O(N×粒子数) 降低到 O(可见实例数×粒子数)。

### 通过 CPU Profiler 测量包围盒效益

使用 Unity CPU Profiler 抓取帧数据时，在 `Rendering` 层级下查找 `Camera.Render > CullAllVisibleObjects` 条目，其耗时反映了所有 AABB 裁剪测试的总开销。若该条目中 `ParticleSystem.Update` 子项占比过高，通常意味着大量粒子系统仍在使用 Auto 模式进行动态包围盒计算。将高频特效切换为 Custom Bounds 后，该子项耗时通常可降低 20%–40%（具体数值取决于场景中粒子系统的数量）。

---

## 实际应用

**场景一：技能命中特效（Local 空间）**
角色释放一个持续时间 1.5 秒的命中光效，粒子向四周爆散，最大扩散半径约 2 米，无垂直位移。设置 `Center Offset = (0, 0, 0)`，`Size = (4, 0.5, 4)`（保留 0.5 米的垂直厚度防止裁剪误判）。由于是 Local 空间，包围盒随角色移动，裁剪结果始终正确。

**场景二：环境烟雾特效（World 空间）**
地图中固定位置的烟囱烟雾，粒子使用 World 空间模拟，向上漂移最高 8 米，水平受风力影响偏移约 3 米。设置 `Center Offset = (1.5, 4, 0)`（沿漂移方向偏移中心），`Size = (6, 8, 6)`。若不偏移中心而只扩大 Size，会导致包围盒向烟囱另一侧也延伸 4 米，浪费裁剪精度。

**场景三：UI 粒子特效**
附着在 UI Canvas 上的粒子特效，由于 Canvas 始终处于摄像机视野内，包围盒裁剪本不会触发。此时优化重点转为将 `Size` 设为最小可用值（如 `(0.1, 0.1, 0.1)`），避免引擎为过大的 AABB 分配不必要的空间数据，减少内存对齐开销。

---

## 常见误区

**误区一：认为 Auto 模式"足够智能"不需要手动设置**
Auto 模式在粒子系统有子发射器（Sub-Emitter）或使用曲线速度模块时，计算结果往往严重低估实际范围——因为 Unity 的自动计算仅采样当前帧已存在的粒子位置，而新生成的子粒子在下一帧才纳入计算，导致 AABB 在特效爆发期持续震荡，每帧触发可见性状态切换，反而比稳定的 Custom Bounds 产生更多回调开销。

**误区二：把包围盒设置为整个场景大小以"一劳永逸"**
将 `Size` 设为 `(1000, 1000, 1000)` 的粒子系统，其 AABB 与任何正常摄像机视锥都会相交，视锥裁剪对该特效完全失效。在移动平台上，一个永不被裁剪的粒子系统每帧会强制占用约 0.02–0.05 ms 的 GPU 时间（取决于粒子数量），若场景中存在 30 个这样的特效，累计可造成约 1.5 ms 的不可裁剪 GPU 开销。

**误区三：Local 空间和 World 空间使用相同的 Bounds 配置策略**
Local 空间的包围盒以对象本地坐标系为准，跟随对象移动旋转；World 空间的包围盒固定在世界坐标，对象移动后包围盒不跟随。对 World 空间特效使用 Local 策略配置 Bounds 时，粒子系统对象一旦移动，包围盒就会脱离实际粒子区域，引发错误裁剪。必须根据模拟空间分别计算 `Center Offset`。

---

## 知识关联

**前置概念：CPU Profiler**
包围盒优化效果的量化依赖 CPU Profiler 的帧分析数据。具体来说，需要在 Profiler 的 `Rendering > CullAllVisibleObjects` 和 `VFX.Update` 中对比 Auto 与 Custom 模式的耗时差异，才能确认手动 Bounds 是否真正减少了裁剪计算量，而不是靠主观感受判断。

**后续概念：特效池化**
包围盒优化解决的是"运行中的特效是否被正确裁剪"的问题，而特效池化解决的是"如何复用特效对象避免频繁的 Instantiate/Destroy"。两者配合使用时，池化对象在回收入池后应通过 `ParticleSystem.Stop()` 停止粒子发射，此时其包围盒的精确性直接影响停止状态的特效是否仍会参与裁剪计算——精确的 Custom Bounds 能让已停止的特效在进入摄像机视锥外后立即被跳过，为池化机制的整体性能提供额外保障。