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

Module脚本（模块脚本）是Niagara系统中用于定义粒子具体行为逻辑的可视化脚本单元。每个Module脚本本质上是一段封装好的HLSL逻辑，通过Niagara的节点图（Node Graph）方式呈现，可以被插入到Emitter的执行堆栈（Execution Stack）中的特定阶段，如Particle Spawn、Particle Update、Emitter Update等。Module脚本与Blueprint不同，它直接运行于GPU或CPU粒子模拟管线中，每帧对每个粒子独立执行一次。

Module脚本的概念随虚幻引擎4.20版本（2018年）Niagara正式作为Beta功能引入而出现，并在UE4.26之后随Niagara转为正式功能而趋于稳定。在此之前，Cascade系统中的粒子行为是通过固定模块（如Required、Spawn、Color over Life等预设模块）实现的，用户几乎无法编写自定义逻辑。Niagara的Module脚本彻底改变了这一局面，赋予美术师和技术美术师直接编写粒子逻辑的能力，而无需修改引擎C++源码。

Module脚本的重要性在于它是Niagara系统"可组合性"设计哲学的直接体现。一个Emitter的粒子行为完全由其堆栈中若干Module脚本叠加决定，例如将"Solve Forces and Velocity"模块与自定义的"Curl Noise Force"模块同时插入Update阶段，两者各自写入或读取粒子属性，最终合并成复杂的运动表现。

## 核心原理

### Module脚本的执行上下文

每个Module脚本在创建时必须指定其**执行上下文（Script Usage）**，共有以下几类：`Particle Spawn Script`、`Particle Update Script`、`Emitter Spawn Script`、`Emitter Update Script`、`System Spawn Script`、`System Update Script`，以及`Particle Event Handler Script`。上下文决定了该脚本在哪个阶段被调用，以及它能访问哪些命名空间下的变量。例如，一个标记为`Particle Update Script`的模块，只能在粒子存活的每一帧被执行，无法访问`Emitter.SpawnRate`这类Emitter级别的只写属性。

### 输入（Input）与Map Get/Set节点

Module脚本的数据流通过**Map Get**和**Map Set**节点实现。Map Get节点从当前粒子的属性映射表（Attribute Map）中读取数值，如`Particles.Position`（粒子位置，Vector3类型）或`Particles.Age`（粒子年龄，Float类型）；Map Set节点则将计算结果写回属性映射表。关键规则是：**一个Module脚本必须以Map Set节点结尾**，否则该脚本不会对粒子状态产生任何修改。此外，Module脚本的对外暴露参数通过**Input节点**定义，这些Input在Emitter堆栈中以可调节的参数形式显示，允许在不修改脚本内部逻辑的情况下调整行为，例如将"Force Strength"设为Float类型的Input，默认值设为`100.0`，技术美术师可在Emitter面板直接覆盖此值。

### 内置函数与HLSL转译

Niagara Module脚本的节点图最终会被引擎编译转译为HLSL代码。节点图中提供了大量内置函数节点，如`Normalize`、`Cross Product`、`Lerp`、`Random Range Float`等。其中`Seeded Random Range Float`节点尤为特殊，它接受一个`NiagaraRandInfo`结构体作为种子输入，保证在CPU和GPU两种模拟模式下随机数结果的确定性一致。若需要编写节点图无法表达的复杂逻辑，可以使用**Custom HLSL节点**，在节点内部直接书写HLSL片段，变量通过`{InputName}`语法与节点引脚绑定。例如：
```
Output = sin({Phase} * 6.28318) * {Amplitude};
```
这段代码实现了一个正弦波偏移，`6.28318`即`2π`的近似值，用于将归一化的Phase值（0~1）映射为完整的正弦周期。

### 模块的堆栈顺序与依赖关系

在Emitter的执行堆栈中，Module脚本按照从上至下的顺序依次执行，且前一个模块的Map Set结果可以被后续模块的Map Get读取。因此模块顺序直接影响结果：若"Apply Velocity"模块在"Drag Force"模块之前执行，则当帧的阻力计算将作用于未应用速度的旧值，反之亦然。Niagara提供了依赖（Dependency）标签系统，允许模块声明自身需要在某类模块之前（`Pre Dependency`）或之后（`Post Dependency`）执行，以此在多人协作或资产复用时自动保证顺序正确。

## 实际应用

**自定义吸引力模块**：在一个火焰Emitter中，需要让粒子在生命周期末尾（Age接近Lifetime）向中心点收拢。具体做法是创建一个`Particle Update Script`类型的Module脚本，使用Map Get读取`Particles.Position`和`Particles.Age`/`Particles.NormalizedAge`，用`Lerp`节点将粒子位置向目标点插值，插值权重由`NormalizedAge`的平方驱动（即越老的粒子越快收拢），最后Map Set写回`Particles.Position`。将此模块插入Emitter Update堆栈"Solve Forces"之后，可确保吸引力在物理解算完成后叠加。

**GPU与CPU双模式兼容**：当Emitter设置为`GPU Simulation`模式时，Module脚本中不能使用`Spawn Info`或某些CPU独有的函数节点（如`Get Actor from Tag`）。因此在编写通用模块时，需在节点图中使用`Script Condition`节点区分模拟模式，或在模块描述中明确标注`CPU Only`，防止被错误插入GPU模拟的Emitter中。

## 常见误区

**误区一：认为Module脚本与Blueprint功能等同**。许多初学者将Niagara Module脚本理解为粒子版的Blueprint，实际上两者机制完全不同。Blueprint是基于对象的事件驱动脚本，运行于游戏线程；Module脚本是数据并行的粒子运算脚本，在粒子模拟线程（甚至GPU线程）上对数千粒子并行执行，不能调用Actor方法、不能访问UObject，也不能包含分支循环等控制流（GPU模式下HLSL不支持动态循环）。

**误区二：以为修改Input默认值等于修改了所有Emitter**。Module脚本中定义的Input默认值仅是"提案值"，一旦某个Emitter在其堆栈中覆盖（Override）了该Input的值，脚本默认值便不再生效。因此当多个Emitter共享同一Module脚本资产，但表现不同时，首先应检查各Emitter堆栈中该模块的Input绑定值，而非去修改Module脚本本身——修改脚本的默认值只会影响尚未覆盖该参数的Emitter。

**误区三：Map Set节点可以写入任意自定义属性名**。向属性映射表写入一个新命名的属性时，必须先在Emitter的**Emitter Properties**或**Add Attribute**处声明该属性，否则该属性虽然在本模块内可写，但在后续模块或Renderer中将无法被正确读取，甚至在GPU模式下直接导致编译错误。`Particles.MyCustomFloat`这类自定义属性的类型和名称需要在Emitter级别统一注册。

## 知识关联

学习Module脚本需要先理解**Emitter与System**的层级关系，因为Module脚本总是被放置在某个Emitter的执行堆栈中，其执行上下文（Particle/Emitter/System级别）直接对应Emitter-System的三层架构。不清楚执行堆栈的层级，就无法判断一个Module脚本应该写成Particle Update类型还是Emitter Update类型。

Module脚本中的Input节点，以及Map Get/Set读写的`Particles.*`、`Emitter.*`、`System.*`命名空间变量，正是下一个核心主题**参数与属性**的具体内容。理解了Module脚本如何通过节点图读写这些属性后，再学习参数绑定、Dynamic Input、用户暴露参数等概念，就能完整掌握Niagara数据流的全貌——即数据从System参数流入Emitter参数，再通过Module脚本中的Map Get被每个粒子读取并计算，最终通过Map Set写回属性，供Renderer采样渲染。