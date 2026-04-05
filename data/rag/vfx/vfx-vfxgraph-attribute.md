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
quality_tier: "A"
quality_score: 76.3
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



# 属性系统

## 概述

属性系统（Attribute System）是 Unity VFX Graph 中用于描述和驱动每个粒子状态的数据机制。每个粒子在生命周期内携带一组独立的属性值，例如 `position`、`velocity`、`color`、`size` 和 `lifetime`，这些值在粒子诞生时初始化，并在每帧的 Update 阶段被读取或修改，最终传递给输出阶段完成渲染。属性本质上是存储在 GPU 显存粒子缓冲区（Particle Buffer）中的逐粒子数据，VFX Graph 的所有计算都围绕这些属性展开。

属性系统随 VFX Graph 于 Unity 2018.3 正式引入，取代了旧版 Shuriken 粒子系统的 CPU 端属性模型。旧模型中属性修改发生在主线程，每帧面临大量数据拷贝开销；新属性系统将数据完全保留在 GPU 端，避免了 CPU-GPU 之间的往返传输，使百万级粒子的属性并行更新成为可能。

理解属性系统的意义在于：VFX Graph 的节点本质上是读写属性的操作符。无论是 Set Velocity、Set Color 还是 Turbulence，它们的功能都归结为读取某些属性并将计算结果写回另一些属性。掌握属性的类型、作用域和数据流向，才能准确预判节点组合的行为，并有效调试粒子运动或渲染异常。

---

## 核心原理

### 内置属性与自定义属性

VFX Graph 提供了一套内置属性集合，这些属性名称固定且具有特殊含义。最常用的内置属性包括：

- `position`（Vector3）：粒子在世界或局部空间的坐标
- `velocity`（Vector3）：每帧位移驱动量
- `age` / `lifetime`（float）：粒子当前年龄与总寿命，比值 `age/lifetime` 即归一化生命进度
- `size`（float）或 `size3`（Vector3）：粒子的缩放尺寸
- `color`（Vector4，RGBA）：粒子颜色与透明度

除内置属性外，用户可在 Graph 的 Blackboard 面板中创建自定义属性（Custom Attribute）。自定义属性支持 float、Vector2、Vector3、Vector4、int、uint、bool 共 7 种数据类型，命名遵循 HLSL 标识符规则（不可使用空格或连字符）。自定义属性一经创建即占用粒子缓冲区中固定的每粒子内存槽位。

### 作用域：粒子属性 vs. 系统属性

属性系统区分两种作用域。**粒子属性（Particle Attribute）** 是逐粒子存储的值，每个粒子独立持有一份，数量等于粒子池（Particle Capacity）上限，因此 Capacity 设置为 100 万时，一个 Vector3 粒子属性将占用约 12 MB 显存。**系统属性（System / Exposed Property）** 则是整个 VFX Graph 实例共享的单一值，存储在常量缓冲区（CBuffer）中，可通过 C# 脚本以 `vfxComponent.SetFloat("MyParam", value)` 实时修改，常用于传递风向、颜色主题等全局参数。

两种作用域的根本区别在于读写时机：粒子属性在 Initialize、Update、Output 三个 Context 中以计算着色器（Compute Shader）分派方式并行读写；系统属性在 CPU 端设置后通过 CBuffer 注入，所有粒子共享同一值。

### 数据流：Initialize → Update → Output

属性的生命周期严格遵循三阶段数据流。在 **Initialize Context** 中，属性被首次赋值——例如 Set Position (Sphere) 节点将 `position` 写入随机球面坐标。Initialize 只在粒子诞生时执行一次，适合设置初始状态。在 **Update Context** 中，属性以每帧为单位被反复读写——例如 Add Velocity 节点每帧将重力向量加到 `velocity` 上，再由引擎内置的 Integrate 操作用 `velocity × deltaTime` 更新 `position`。在 **Output Context** 中，属性被读取用于渲染决策，但通常不写回粒子缓冲区——例如将 `age/lifetime` 映射到一条渐变曲线来采样最终 `color`。

如果在 Update 中写入某个属性，但在同一 Update 块中后续节点又读取同一属性，VFX Graph 会按节点的垂直排列顺序确定执行先后，因此节点的上下位置直接影响读到的是旧值还是新值。

---

## 实际应用

**场景一：基于寿命的颜色渐变**
在 Output Particle Quad Context 中，添加 `Set Color over Life` 节点，该节点内部计算 `age / lifetime` 得到 0–1 的进度值，再通过 Gradient 类型的系统属性采样颜色，最终写入渲染用的 `color` 属性。这一做法将颜色控制完全交给 GPU，无需任何 CPU 干预，万级粒子的颜色插值开销可忽略不计。

**场景二：C# 驱动动态参数**
在 Blackboard 中创建一个 Exposed 的 Vector3 属性 `WindDirection`，在 Update 中用 `Force from Field` 节点读取该属性施加力。在 C# 脚本中每帧调用 `vfxAsset.SetVector3("WindDirection", windVector)`，实现风向随游戏逻辑实时变化的火焰或烟雾效果，而不需要重新编译 VFX Graph。

**场景三：自定义属性传递碰撞状态**
创建一个 uint 类型自定义属性 `bounceCount`，在 Update 的碰撞事件块中每次检测到碰撞时执行 `bounceCount += 1`。Output 阶段根据 `bounceCount` 的值用 Branch 节点选择不同贴图，从而实现反弹次数越多粒子颜色越暗的视觉反馈。

---

## 常见误区

**误区一：认为 Initialize 中的属性赋值在后续帧会保留**
Initialize Context 仅在粒子诞生的第一帧执行。如果希望某个值在粒子整个生命内持续生效（例如一个随机的初始旋转速度），必须在 Initialize 中将其写入一个自定义粒子属性，然后在 Update 中读取该属性使用。直接在 Update 中用 Random 节点生成值则会导致每帧重新随机，产生抖动而非持续旋转。

**误区二：将 Exposed Property 与 Particle Attribute 混用**
Exposed Property 是全局单值，所有粒子读到相同结果；Particle Attribute 是逐粒子值，每个粒子独立。若希望每个粒子有不同的初始颜色，必须使用 Particle Attribute 而非 Exposed Property——将全局颜色参数误用为逐粒子颜色，会让所有粒子同时变色，而非各自独立渐变。

**误区三：忽视自定义属性对 Particle Capacity 的显存影响**
每增加一个 Vector3 自定义属性，在 Capacity 为 100 万的系统中将额外消耗约 12 MB 显存（100万 × 12 字节）。过度添加不必要的自定义属性，尤其是 Vector4 类型，会快速耗尽 GPU 资源。应当在设计阶段评估是否可以复用内置属性（例如用 `color.a` 存储辅助标志位）来减少自定义属性数量。

---

## 知识关联

**前置概念——生成系统**：生成系统（Spawn System）决定了何时创建粒子以及初始属性值从何而来。Spawn Rate、Burst 等参数控制粒子进入 Initialize Context 的时机，而 Initialize Context 正是属性系统数据流的起点。不理解生成系统，就无法知道属性被赋初值的触发条件。

**后续概念——力与运动**：力与运动（Force & Motion）系统的核心是在 Update Context 中读取 `velocity` 和 `position` 这两个内置粒子属性，并按物理规则修改它们。例如 Gravity 节点将 `(0, -9.8, 0) × deltaTime` 累加到 `velocity`，Linear Drag 节点以系数乘以 `velocity` 实现阻尼——这些操作都是属性系统读写机制的直接应用。掌握属性的数据流后，力学节点的行为便可从数学层面完整推导。