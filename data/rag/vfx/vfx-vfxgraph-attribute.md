---
id: "vfx-vfxgraph-attribute"
concept: "属性系统"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 属性系统

## 概述

属性系统（Attribute System）是 Unity VFX Graph 中用于描述每个粒子状态的数据结构体系。每一个粒子在其生命周期内都携带一组属性，包括内置属性（Built-in Attributes）如 `position`、`velocity`、`color`、`size`、`age`、`lifetime` 等，以及用户自定义的自定义属性（Custom Attributes）。这些属性本质上是 GPU 端的结构化缓冲区字段，VFX Graph 的所有模块（Initialize、Update、Output）都通过读写这些属性来实现粒子行为。

属性系统的设计源于 Unity 在 2018 年推出 VFX Graph 时对 GPU 粒子计算管线的重新架构。传统 CPU 粒子系统（如 Shuriken）将粒子数据存储在主内存中，而 VFX Graph 的属性直接存储在 GPU 显存的 StructuredBuffer 中，单帧可处理百万级粒子而无需 CPU-GPU 数据回传。属性系统的意义在于：它定义了"粒子知道自己什么"，而 Block 和 Operator 定义了"粒子用这些信息做什么"，二者协作构成了整个特效的计算逻辑。

## 核心原理

### 内置属性与数据类型

VFX Graph 提供约 20 个内置属性，每个属性都有固定类型。`position` 和 `velocity` 为 `Vector3`，`color` 为 `Vector4`（含 alpha），`size` 为 `float`，`alive` 为 `bool`，`age` 和 `lifetime` 均为 `float`（单位：秒）。在 HLSL 层面，这些属性被编译为一个名为 `VFXAttributes` 的结构体，在 Compute Shader 中以 `attributeBuffer` 的形式存储，每个粒子占用一个连续的内存槽位（Slot）。`age` 属性每帧自动递增 `deltaTime`，当 `age >= lifetime` 时 `alive` 被置为 `false`，粒子被标记为死亡——这一机制完全由 VFX Graph 内部的 Update Context 自动处理，无需手动编写逻辑。

### 属性的读写阶段与作用域

VFX Graph 将属性操作划分为三个 Context 阶段，每个阶段的读写权限不同：

- **Initialize Context**：仅在粒子出生时执行一次，可读写所有属性。常用于设置初始 `position`、`velocity`、`lifetime`。
- **Update Context**：每帧对所有存活粒子执行，可读写除 `particleId` 之外的大多数属性。力、碰撞、噪声等逻辑均在此阶段修改属性。
- **Output Context**：仅用于渲染，只能**读取**属性，不可写入。这一限制防止了渲染阶段对粒子状态的意外修改。

在节点图中，属性通过 **Get Attribute** 和 **Set Attribute** 节点访问。Get 节点输出该属性当前值，Set 节点将计算结果写回缓冲区。同一帧内对同一属性的多次 Set 操作会按 Block 的上下顺序依次覆盖，最终值由最后一个 Set 决定。

### 自定义属性（Custom Attributes）

当内置属性不足以描述特效需求时，可通过 VFX Graph 的 **Blackboard** 面板创建自定义属性。支持的类型包括 `float`、`Vector2`、`Vector3`、`Vector4`、`int`、`uint`、`bool` 和 `Matrix4x4`。自定义属性与内置属性共同存储在同一个 attributeBuffer 中，因此增加自定义属性会直接增大每个粒子的内存占用。例如，为 10 万个粒子添加一个 `Vector3` 类型的自定义属性，额外显存消耗为 `100000 × 12 bytes = 1.2 MB`。自定义属性的典型用途是存储粒子的"出生位置"（spawn position）供后续 Update 阶段引用，实现粒子始终围绕出生点运动的效果。

### 属性继承与 Spawn Context 传递

Spawn Context 可以通过 **SpawnEvent Attribute** 机制向 Initialize Context 传递数据。在 Spawn Context 中使用 `Set SpawnEvent Attribute` 节点将值附加到生成事件上，Initialize Context 使用 `Get Attribute: sourceIndex` 和对应的 Get 节点接收这些值。这使得不同 Spawner 产生的粒子可以携带差异化的初始属性，例如从多个不同颜色的发射源生成的粒子在出生时即持有各自的颜色信息。

## 实际应用

**轨迹残影效果**：在 Initialize Context 中使用 `Set Attribute: position`（source: `Transform`）将粒子出生位置记录到自定义属性 `spawnPos`（Vector3 类型）。在 Update Context 中，每帧将 `position` 与 `spawnPos` 做插值（`Lerp`），实现粒子向出生点回弹的拖尾感。

**基于年龄的颜色变化**：使用 `age / lifetime` 计算归一化年龄（值域 0~1），将其输入 `Sample Gradient` Operator，输出结果通过 `Set Attribute: color` 写入。粒子从出生（蓝色）到死亡（红色）自动插值，整个逻辑仅需 3 个节点，无需脚本。

**与 C# 脚本交互**：通过 `VisualEffect.SetVector3("属性名", value)` 在 CPU 端写入 Exposed Property（暴露属性），这类属性属于 Graph-level 的全局参数而非粒子级属性，二者需要明确区分。粒子级属性只存在于 GPU 缓冲区，C# 无法直接逐粒子读写。

## 常见误区

**误区一：混淆 Exposed Property 与粒子属性**。Exposed Property 是整个 VFX Graph 的全局参数，在 Inspector 面板可见，类似 Shader 的 Property；而粒子属性是每个粒子独立持有的数据。两者都出现在 Blackboard 中，但粒子属性图标为菱形，Exposed Property 图标为圆形，初学者常因界面相似而混淆，导致误以为可以通过 `VisualEffect.SetFloat` 修改单个粒子的 `size`。

**误区二：认为 Output Context 可以写入属性**。部分开发者尝试在 Output Context 中通过 Set Attribute 修改 `color` 或 `size` 以实现渲染时的变化，但 VFX Graph 不允许在 Output 阶段写回 attributeBuffer。正确做法是将颜色/大小计算逻辑移至 Update Context，或使用 Output 阶段专有的 **Composition** 模式（如 `Multiply`、`Over`）对属性进行非破坏性的渲染覆盖。

**误区三：无限增加自定义属性不影响性能**。由于所有自定义属性均存储在 GPU 显存的连续缓冲区中，粒子容量（Capacity）在创建时固定分配。若 Capacity 设为 1,000,000 且添加了 3 个 Vector3 自定义属性，仅这部分额外显存即达 `1,000,000 × 3 × 12 = 36 MB`，在移动端或显存有限的平台上会造成严重压力。

## 知识关联

属性系统依赖**生成系统**（Spawn Context）作为数据入口——正是 Spawn Context 触发 Initialize Context 执行，粒子属性才得以完成首次赋值。没有生成系统产生的粒子实例，属性系统的字段虽然存在于 Buffer 定义中，但不会有任何有效数据被写入。

属性系统是**力与运动**模块的直接操作对象。VFX Graph 中所有力（Gravity、Drag、Turbulence 等）的本质都是在 Update Context 中读取 `velocity` 属性、施加加速度、再将新的 `velocity` 写回——即对粒子属性的连续帧修改。理解属性的读写机制和阶段限制，是正确实现力与运动效果、避免属性覆盖冲突的前提条件。