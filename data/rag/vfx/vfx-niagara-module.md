---
id: "vfx-niagara-module"
concept: "Module脚本"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Module脚本

## 概述

Module脚本（模块脚本）是Niagara系统中用于定义单一粒子行为逻辑的最小可复用单元。每个Module脚本本质上是一段HLSL代码的可视化封装，通过Niagara的节点图（Node Graph）编辑器呈现，负责读取粒子属性、执行计算、再将结果写回属性。一个典型的Module脚本只做一件事——比如"施加重力"或"按速度旋转粒子"——这种单一职责设计使其可以在不同Emitter之间自由拖拽复用。

Module脚本的概念随UE4.26版本中Niagara正式脱离实验性阶段而成熟定型。在此之前，Cascade特效系统的行为逻辑是硬编码在C++模块里的，美术人员无法自行扩展。Niagara将这部分逻辑暴露为可视化脚本，Module脚本正是这次开放的核心产物，它让TA（技术美术）无需修改引擎源码即可创建全新的粒子行为。

Module脚本的重要性体现在Niagara执行栈（Execution Stack）的组织方式上。Emitter的每个执行阶段（Emitter Spawn、Emitter Update、Particle Spawn、Particle Update）都由一组有序的Module脚本构成，引擎按照栈中从上到下的顺序逐一调用这些脚本。因此，Module脚本的编写质量和执行顺序直接决定粒子系统最终的视觉表现与性能开销。

---

## 核心原理

### Module脚本的文件结构与执行上下文

每个Module脚本保存为`.uasset`格式，内部包含两部分：一是**输入映射（Input Map）**，声明该模块对外暴露的参数接口；二是**节点图**，定义实际的运算逻辑。节点图的入口固定为`Map Get`节点，出口固定为`Map Set`节点——`Map Get`从当前粒子的数据集（Parameter Store）读取数值，`Map Set`将计算结果写回。这种读-计算-写的结构保证了每个模块的副作用是明确且可追踪的。

Module脚本有四种执行上下文（Execution Context），对应Niagara的四个执行阶段：
- **System Spawn / System Update**：每个System实例只执行一次或每帧执行一次，适合写全局参数
- **Emitter Spawn / Emitter Update**：每个Emitter实例级别的逻辑
- **Particle Spawn**：粒子诞生时执行一次，适合初始化位置、颜色、大小
- **Particle Update**：每帧对所有存活粒子执行，适合持续性行为如阻力、颜色渐变

一个Module脚本在创建时必须指定其允许被放置的上下文，若尝试将`Particle Spawn`阶段的模块拖入`Emitter Update`栈，编辑器会报出上下文不匹配错误。

### 模块的输入参数与Namespace规则

Module脚本通过**Namespace（命名空间）**区分数据的归属与生命周期。常见的命名空间包括：

| 命名空间 | 含义 | 示例 |
|---|---|---|
| `Particles.` | 单个粒子的属性 | `Particles.Position`、`Particles.Velocity` |
| `Emitter.` | 当前Emitter级别数据 | `Emitter.Age`、`Emitter.SpawnRate` |
| `System.` | System级别全局数据 | `System.ElapsedTime` |
| `Module.` | 模块私有输入参数 | `Module.GravityStrength` |

`Module.`命名空间下的变量会自动在Emitter编辑器的该模块条目中显示为可调节的输入槽，这是Module脚本向外暴露用户接口的标准方式。例如，一个自定义重力模块会声明`Module.GravityScale`（float类型，默认值980.0，单位cm/s²），用户无需打开脚本内部即可直接修改此值。

### 节点图中的关键运算节点

在Module脚本的节点图内，除了基本的数学运算节点（Add、Multiply、Lerp等），有几类节点是Niagara特有的：

- **`Simulation Stage Index`**：在GPU Simulation Stage（计算着色器阶段）中返回当前粒子的线程索引，用于实现粒子间交互（如流体模拟）
- **`Engine.DeltaTime`**：获取本帧的时间步长（秒），在`Particle Update`阶段实现帧率无关的物理积分时必须乘以此值；典型写法为 `NewVelocity = OldVelocity + Acceleration * Engine.DeltaTime`
- **`Transient`命名空间变量**：在单次模块调用内临时存在、不写入持久粒子数据集的中间变量，用于优化内存访问

---

## 实际应用

**自定义螺旋运动模块**：创建一个名为`SpiralMotion`的Particle Update模块，在节点图中读取`Particles.Age`（粒子存活时间），乘以`Module.AngularSpeed`（角速度，单位rad/s），通过`Sin`/`Cos`节点计算偏移量，加回`Particles.Position`。将该模块放置在`Particle Update`栈中`Solve Forces and Velocity`模块的之后，确保螺旋偏移叠加在物理速度积分之上。此模块可直接拖入任意其他Emitter复用，无需修改内部逻辑，只需在外部调整`Module.AngularSpeed`和`Module.Radius`两个输入槽。

**颜色随生命周期渐变模块**：在`Particle Update`阶段，读取`Particles.NormalizedAge`（范围0到1的归一化年龄，引擎内置属性），通过`Curve for Floats`节点采样一条自定义渐变曲线，输出至`Particles.Color`的RGB通道。这比直接使用内置`Color by Life`模块更灵活，因为可在曲线节点上叠加`Module.ColorMultiplier`参数，实现运行时动态调色。

**与Scratch Pad Module的区别**：Scratch Pad Module是临时写在Emitter资产内部、不可跨Emitter复用的一次性脚本，适合快速原型验证。一旦逻辑稳定，应将其"提升"（Promote to Asset）为独立的Module脚本`.uasset`，以便项目范围内共享。

---

## 常见误区

**误区一：认为Module脚本的执行顺序不重要**
Niagara执行栈是严格顺序执行的，靠后的模块能读到靠前模块的写入结果。若将`Apply Initial Forces`（施加初始力）放置在`Initialize Particle`（初始化质量）之前，前者读到的`Particles.Mass`将是未初始化的默认值0，导致力的计算结果为无穷大，粒子瞬间飞出视野。正确做法是严格遵守"初始化类模块 → 行为类模块 → 求解器模块"的排列顺序。

**误区二：在Particle Update阶段直接赋值位置而不乘DeltaTime**
新手常在`Particle Update`模块中写 `Particles.Position = Particles.Position + Velocity`，未乘`Engine.DeltaTime`。这导致粒子的移动距离随帧率线性变化：60fps时速度是30fps时的两倍。正确写法必须包含时间步长：`Particles.Position += Velocity * Engine.DeltaTime`，这是实现帧率无关运动的唯一正确方式。

**误区三：混淆Module输入参数与Particle属性的修改范围**
`Module.`命名空间的变量是该模块的**输入配置**，它对整个Emitter下所有粒子共享同一个值；而`Particles.`命名空间的变量则**每个粒子独立存储**。若希望每个粒子有不同的旋转速度，必须在`Particle Spawn`阶段将随机值写入一个自定义的`Particles.RandomAngularSpeed`属性，而非在`Module.AngularSpeed`上做随机——后者只会让所有粒子共享同一个随机结果。

---

## 知识关联

理解Module脚本需要先掌握**Emitter与System**的层级关系——System包含Emitter，Emitter的执行栈才是Module脚本的"容器"，不清楚Particle Spawn与Particle Update阶段的区别就无法正确放置模块。Module脚本的Namespace规则（`Particles.`、`Module.`、`Emitter.`）与下一个主题**参数与属性**直接衔接：参数与属性系统详细定义了每种命名空间变量的生命周期、数据类型（float、Vector3、Color等）以及如何在System蓝图中从外部绑定动态数值。Module脚本是编写单个行为逻辑的场所，而参数与属性系统则决定了这些逻辑能读写哪些数据、数据如何在模块间流动。