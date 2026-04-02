---
id: "vfx-vfxgraph-block"
concept: "Block与节点"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---



# Block与节点

## 概述

VFX Graph 的视觉编程系统由三种不同类型的节点构成：**Block（块）**、**Operator（运算符节点）** 和 **属性节点（Property Node）**。这三者共同构成粒子系统逻辑的完整表达，但各自承担截然不同的职责。Block 是只能存在于 Context 内部的执行单元，Operator 是可以独立浮动于图中的计算节点，属性节点则是将 VFX Asset 的暴露参数接入图中的入口。

Block 的概念源自 Unity 将 Shader Graph 的节点化思想延伸至粒子系统领域，于 Unity 2018.3 进入实验性阶段，2019.3 正式推出 VFX Graph 1.0。Block 之所以与普通节点分离，是因为粒子系统的执行逻辑本质上是**顺序化的管线**——每个 Block 按从上到下的顺序依次作用于粒子属性，这与 Shader Graph 中节点的数据流方向有根本不同。

理解这三类节点的区别，直接影响能否在 VFX Graph 中正确搭建粒子逻辑。若将 Operator 与 Block 混淆，会导致图中出现孤立计算节点却无法影响粒子行为的典型错误；若不理解属性节点的绑定机制，则无法从 C# 脚本动态控制粒子效果。

---

## 核心原理

### Block：Context 内的执行指令

Block 是 VFX Graph 中**唯一能够写入粒子属性**的节点类型。每个 Block 必须挂载在某个 Context（如 Initialize、Update、Output）之内，不能独立存在于图的空白区域。Block 的输入端口（左侧）接收数值或向量，**不输出数据给其他节点**——它的"输出"是直接修改对应 Context 所管理的粒子属性。

Block 的执行顺序严格遵循垂直排列顺序，靠上的 Block 先执行。例如在 Update Context 中，若先放置 `Set Velocity` Block 再放置 `Turbulence` Block，则湍流效果会叠加在已设置的速度之上；反之则顺序相反，结果不同。Block 可通过右键菜单在 Context 内部拖拽重排。

每种 Context 仅支持特定类别的 Block。Initialize Context 只接受初始化类 Block（如 `Set Position Shape`、`Set Lifetime Random`），Output Context 只接受输出类 Block（如 `Set Size over Life`、`Orient`）。若尝试将 Output 专属 Block 拖入 Update Context，VFX Graph 会拒绝放置并显示红色禁止标志。

### Operator：浮动的数学运算单元

Operator 是 VFX Graph 中的纯计算节点，可以放置在图的任意空白区域，**既有输入端口也有输出端口**，专门用于生成和变换数据流。常见的 Operator 包括 `Add`、`Multiply`、`Sample Texture2D`、`Noise`、`Get Attribute` 等。

Operator 本身**不直接影响任何粒子**，必须将其输出端口连接到某个 Block 的输入端口，才能将计算结果注入粒子系统。一个典型链路是：`Time` Operator → `Multiply` Operator → `Sine` Operator → `Set Position` Block 的 Position 输入，由此实现粒子位置随时间做正弦波动。

`Get Attribute` 是一类特殊 Operator，用于读取当前粒子的属性值（如当前速度、当前位置），其输出可以再连接到其他 Operator 进行计算后送回 Block。这使得粒子属性的自我引用成为可能，例如实现速度衰减公式 `newVelocity = oldVelocity × 0.98`。

### 属性节点：外部参数的接入口

属性节点（Property Node，也称 Blackboard 参数节点）对应 VFX Graph 左侧 **Blackboard** 面板中定义的暴露参数。将 Blackboard 中的参数拖拽到图中，即生成对应的属性节点，其输出端口类型与参数类型一致（Float、Vector3、Texture2D 等）。

在 C# 脚本中，通过 `visualEffect.SetFloat("参数名", value)` 即可在运行时修改该属性节点的值，进而影响所有连接该节点的 Block。属性节点的典型应用是将粒子颜色的 HDR 强度暴露给脚本，由游戏逻辑驱动粒子效果的强弱变化。属性节点不支持直接在图中手动输入覆盖值，其数值来源必须是 Blackboard 定义。

---

## 实际应用

**粒子随血量变化变红**：在 Blackboard 中创建一个名为 `HealthRatio` 的 Float 参数（范围 0–1）。在图中拖入该属性节点，通过 `Lerp` Operator 将其在红色（1,0,0）和白色（1,1,1）之间插值，输出连接到 Output Context 中的 `Set Color` Block。在 C# 中每帧调用 `vfx.SetFloat("HealthRatio", currentHP / maxHP)`，即可实现粒子颜色随生命值动态变化。

**分层噪声驱动运动**：在 Update Context 中放置 `Turbulence` Block，将其 Intensity 输入连接到一个 `Multiply` Operator，该 Operator 的两个输入分别来自 `Noise` Operator（频率 2.5）和一个 `Get Attribute: Age/Lifetime` Operator。这样粒子越接近生命末尾，湍流强度越大，产生消散效果。整个链路中 Block 仅有一个，其余均为 Operator。

---

## 常见误区

**误区一：认为 Operator 的输出可以直接作用于粒子**。初学者常将 `Noise` Operator 的输出接到空白处就以为粒子会抖动。实际上，任何 Operator 的效果都必须通过连接到某个 Block 的输入端口才能落地。孤立的 Operator 在图中只是"悬空计算"，Unity 甚至会在编译时以灰色标注未使用的 Operator 节点。

**误区二：将属性节点与 Operator 内联常量等同**。Block 的输入端口在未连接时可以直接填写常量数值（内联值），这与拖入属性节点后连接完全不同——内联常量无法被 C# 脚本修改，而属性节点可以。若项目需要运行时调参，必须使用 Blackboard 属性节点，而非依赖内联常量。

**误区三：认为 Block 执行顺序不重要**。在同一 Context 中，同类操作的 Block 顺序会影响最终结果。例如先执行 `Conform to Sphere`（将粒子推离球面）再执行 `Set Velocity from Direction & Speed`，与相反顺序相比，粒子的运动轨迹会有明显差异，因为后执行的 Block 会覆盖前一个 Block 对同一属性的写入。

---

## 知识关联

Block 的"只能存在于 Context 内部"这一约束，直接来源于 **Context 系统**的设计——每种 Context 代表粒子生命周期的一个阶段（Initialize、Update、Output），Block 是向该阶段注入具体行为的最小单元。没有对 Context 阶段语义的理解，就无法判断某个 Block 应该归属于哪个 Context。

掌握三类节点后，下一步是学习 **生成系统（Spawn System）**。Spawn System 本身也是一类 Context（Spawn Context），其内部同样使用 Block 来定义粒子生成的节奏——例如 `Constant Spawn Rate` Block（设置每秒生成数量）和 `Periodic Burst` Block（定时爆发生成）。Spawn Context 的 Block 作用对象不是粒子属性，而是生成事件流，这是对 Block 机制的进一步扩展应用。