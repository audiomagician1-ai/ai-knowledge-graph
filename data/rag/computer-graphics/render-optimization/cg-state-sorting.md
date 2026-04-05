---
id: "cg-state-sorting"
concept: "状态排序"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 状态排序

## 概述

状态排序（State Sorting）是渲染优化中的一种技术，通过在提交绘制命令之前，按照材质、着色器、纹理或深度等属性对渲染对象进行分组和排序，从而最大限度地减少GPU渲染管线中的状态切换（State Change）次数。每次切换着色器程序、绑定新纹理或修改混合模式，驱动层都必须重新验证管线状态并向GPU发送配置命令，这一过程的开销可高达数十微秒，在场景中存在数千个渲染对象时会严重影响帧率。

状态排序的概念在早期固定管线时代（DirectX 7 之前）就已存在，但在可编程着色器普及后（DirectX 9 / OpenGL 2.0 时期，约2002年前后）变得尤为重要——因为着色器程序的切换代价远大于固定管线中修改渲染参数的代价。现代引擎如 Unreal Engine 和 Unity 均在其渲染器的"批处理排序阶段"内置了状态排序逻辑。

状态排序之所以重要，在于它直接决定了 CPU 向 GPU 提交命令的效率：在同一帧中将使用相同着色器的对象连续绘制，GPU 无需重新绑定程序对象，驱动的状态验证开销可降低 30%–70%，具体数值因平台和驱动实现而异。

## 核心原理

### 状态切换的代价分级

GPU 驱动层的状态切换代价并不均等，业界通常将其分为以下由高到低的代价等级：

1. **渲染目标切换（Render Target）**：代价最高，需要刷新 tile cache（在移动 GPU 上）或触发 resolve 操作。
2. **着色器程序切换（Shader Program / PSO）**：需要驱动重新编译或查找管线状态对象（Pipeline State Object），在 Vulkan/Metal/DX12 中通过预编译 PSO 可降低此代价，但切换本身仍存在绑定成本。
3. **纹理绑定切换（Texture Binding）**：代价中等，需要更新描述符集或纹理采样器。
4. **常量缓冲区更新（Uniform / Constant Buffer）**：代价相对较低，但频率过高同样影响性能。

状态排序的核心目标是减少等级越高的切换次数，即优先保证着色器程序的连续性，其次是纹理，再次是常量参数。

### 排序键（Sort Key）设计

实际引擎中，状态排序依赖一个64位（或更宽）的排序键，将多种状态信息编码为整数，然后对所有渲染对象按该键排序（通常使用基数排序 Radix Sort，时间复杂度 O(n)）。一种典型的排序键位域布局如下：

```
[63:60] 渲染层级 (Layer/Pass, 4 bits)
[59:44] 着色器/材质 ID (16 bits)
[43:32] 纹理集 ID (12 bits)
[31:16] 深度值 (16 bits，不透明物体前到后，透明物体后到前)
[15:0]  其他状态标志
```

这种设计允许渲染器在 O(n log n) 甚至 O(n) 的时间内完成排序，Frostbite 引擎的技术文档（2010年 GDC 演讲"Sorting your way to success"）中详细描述了类似的排序键方案。

### 不透明与透明物体的排序方向相反

状态排序对不透明（Opaque）和透明（Transparent）物体采用截然相反的深度策略：

- **不透明物体**：按**由近到远**（Front-to-Back）排序。GPU 的 Early-Z 测试会剔除被遮挡片元，越近的物体越先绘制，可大幅减少 Overdraw。常见场景中，良好的 Front-to-Back 排序可将 Overdraw 从 5× 降至 1.5× 以下。
- **透明物体**：必须按**由远到近**（Back-to-Front）排序，即画家算法（Painter's Algorithm），否则混合结果出现视觉错误。透明物体无法从 Early-Z 中获益，因此其状态排序优先级通常低于深度排序。

### 材质分组与 Batch 合并

在完成排序之后，若相邻的多个对象共享相同的材质与变换矩阵结构，可进一步合并为一个 Instanced Draw Call（实例化绘制），从单次 Draw Call 绘制数百个相同物体。状态排序正是 GPU Instancing 能够生效的前提条件——只有排序后相同材质的对象相邻，引擎才能检测到可合并的实例并生成 `DrawIndexedInstanced` 调用。

## 实际应用

**Unity 的 SRP Batcher**：Unity 的可编程渲染管线（URP/HDRP）中，SRP Batcher 按着色器变体（Shader Variant）对对象排序，将使用相同变体的对象归为一组，每组只绑定一次着色器，仅更新每个对象的 Per-Object Constant Buffer（每对象常量缓冲区）。官方数据显示该技术可将 CPU 渲染线程耗时降低约 1.2×–4× 倍，具体取决于场景中材质多样性。

**移动端 Tile-Based 架构的特殊考量**：在 Mali、Adreno 等移动 GPU 上，渲染目标切换会触发 Tile Memory 的 flush 和 load/store，代价极高（可占帧时间 5%–15%）。状态排序中应将所有写入同一渲染目标的对象集中提交，避免在同一帧中反复切换 FBO（Frame Buffer Object）。

**粒子系统的半透明排序**：粒子系统通常含有数千个透明四边形，若不排序直接提交，混合结果错误且 Overdraw 极高。Unreal Engine 的 Niagara 粒子系统在 CPU 端每帧对粒子执行 Back-to-Front 排序，对于10,000个粒子的排序耗时约为 0.3–0.8ms（视 CPU 和 SIMD 优化程度而定）。

## 常见误区

**误区一：认为状态排序只影响透明物体**
许多初学者因"画家算法"的概念印象，误以为状态排序只对透明渲染有意义。实际上，对不透明物体按材质分组排序对减少着色器切换次数的收益同样显著，甚至更大——因为不透明物体通常数量更多，且可以从 Early-Z 裁剪中额外获益。

**误区二：认为排序的 CPU 开销会抵消其收益**
对 10,000 个对象执行基数排序的 CPU 耗时通常在 0.1–0.5ms 以内，而一次着色器状态切换的驱动开销约为 5–50μs。若排序能消除 100 次以上的着色器切换，其 CPU 收益即可覆盖排序本身的开销。在 GPU 受限（GPU-bound）场景中，减少状态切换带来的 GPU 端节省还未计入此比较。

**误区三：深度排序与状态排序必须二选一**
部分开发者认为材质排序（按 Shader 分组）与深度排序（Front-to-Back）存在根本冲突，必须取舍。实际上，通过排序键的位域优先级设计，可以在"同一材质内部按深度排序"——即先按材质 ID 作为主键，再按深度作为次键，两种优化可以同时获得，只是各自收益有所折中。

## 知识关联

状态排序建立在 **Draw Call 优化**的基础之上：Draw Call 优化解决的是"如何减少绘制命令数量"，而状态排序解决的是"如何排列这些命令以最小化每次命令之间的驱动开销"。两者是互补关系——批处理合并减少 Draw Call 总数，状态排序降低剩余 Draw Call 的提交代价。

状态排序所产生的"相同材质对象相邻"这一条件，同时也是 **GPU Instancing**（实例化渲染）和 **Dynamic Batching**（动态合批）能够自动触发的前提。在 Unity 和 Unreal 等引擎中，状态排序阶段完成后，合批检测逻辑才能遍历排序后的队列并识别可合并对象，因此状态排序在渲染管线的排序阶段处于批处理的上游位置。