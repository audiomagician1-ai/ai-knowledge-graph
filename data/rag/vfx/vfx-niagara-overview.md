---
id: "vfx-niagara-overview"
concept: "Niagara系统概述"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Niagara系统概述

## 概述

Niagara是虚幻引擎5（UE5）内置的可视化粒子特效系统，于UE4.20版本首次以实验性功能发布，并在UE5中成为官方推荐的默认粒子系统，完全取代了前代的Cascade系统。Niagara的核心设计目标是让技术美术师（Technical Artist）在不依赖程序员的情况下，通过可视化脚本节点自主定义粒子的行为逻辑，而不是像Cascade那样只能在预设模块范围内调整参数。

Niagara的名称来源于尼亚加拉瀑布，寓意粒子数据如同瀑布般流动处理。整个系统建立在数据驱动（Data-Driven）的设计哲学上：粒子的每一个属性——位置、速度、颜色、生命周期——都被视为可以被任意模块读取和写入的数据流。这与Cascade的封闭式模块堆栈形成根本区别，Cascade模块内部逻辑对用户不透明，而Niagara的每个模块本质上都是一段可见、可修改的HLSL代码或可视化脚本图。

Niagara之所以重要，在于它将GPU模拟粒子的上限从Cascade时代的数百万颗扩展到潜在的数亿颗，同时支持粒子与场景的深度交互，例如读取深度缓冲（Depth Buffer）进行碰撞检测，或采样场景中的向量场（Vector Field）影响粒子运动方向。

## 核心原理

### 三层层级架构：System / Emitter / Particle

Niagara采用严格的三层嵌套结构。最顶层是**Niagara System（NS）**，对应编辑器中`.ns`后缀的资产，代表一个完整的特效单元（如一场爆炸或一束火焰），可以包含多个Emitter。中间层是**Emitter**，负责定义单一类型粒子的生成规则，例如"每秒生成50个火星"和"每秒生成10块碎石"分别是同一个System内的两个Emitter。最底层是**Particle**，即每个独立粒子实例，其属性值在Emitter定义的逻辑下逐帧更新。这种分层使得同一个Emitter可以在多个System中复用，修改Emitter会同步影响所有引用它的System。

### 执行阶段（Execution Stage）

每个Emitter内部的逻辑按照固定的四个执行阶段顺序运行：**Emitter Spawn**（Emitter初始化，整个生命周期只执行一次）、**Emitter Update**（每帧执行，处理Emitter级别的持续逻辑）、**Particle Spawn**（每颗粒子诞生时执行一次，设置初始属性）、**Particle Update**（每帧对所有存活粒子执行，更新位置、颜色等动态属性）。这四个阶段的执行顺序不可颠倒，理解这一点是调试粒子行为异常的关键。例如，在Particle Update阶段无法访问Particle Spawn中才会计算的"初始随机种子"，必须将该值存储为粒子属性后才能跨阶段读取。

### 命名空间（Namespace）数据系统

Niagara通过命名空间区分不同作用域的数据。`Emitter.`前缀的变量在整个Emitter层级共享，所有粒子均可读取；`Particles.`前缀的变量是每个粒子独有的，如`Particles.Position`和`Particles.Velocity`；`Engine.`前缀的变量来自引擎系统，如`Engine.DeltaTime`表示当前帧的时间增量（以秒为单位）；`User.`前缀的变量是对外暴露的参数接口，可以在蓝图或C++中通过`UNiagaraComponent::SetVariableFloat()`等函数动态赋值。这套命名空间规则直接决定了数据能否在模块间正确传递，是新手最常出错的地方。

### CPU模拟与GPU模拟的选择

Niagara的每个Emitter可以独立选择在CPU或GPU上运行粒子逻辑。CPU模拟支持完整的Niagara功能，包括事件（Event）系统和粒子间通信，但性能上限约在数万颗粒子。GPU模拟将粒子逻辑完全卸载到显卡，可以轻松支持数十万甚至数百万颗粒子，但不支持部分需要随机访问的功能，如Event Handler。选择哪种模式取决于粒子数量和所需特性的权衡，并非GPU一定优于CPU。

## 实际应用

在游戏制作中，Niagara System作为独立资产放置在关卡中或附加到Actor上。例如，制作角色脚步扬尘效果时，美术师会创建一个包含"尘埃Emitter"和"小石粒Emitter"的NS文件，通过蓝图在角色落脚事件触发时调用`Activate()`函数播放该特效，同时通过`User.SurfaceColor`变量传入地表颜色，让尘埃颜色与地面贴图保持一致。

Niagara还被用于实现大规模环境特效，如UE5演示场景"Valley of the Ancient"中的沙尘暴效果，单帧内在GPU上同时模拟超过100万颗沙尘粒子，并通过读取场景风向向量场驱动粒子轨迹，这是Cascade系统在技术上无法实现的效果规模。

## 常见误区

**误区一：认为Niagara System等同于单个Emitter。** 初学者经常把NS文件当作单个粒子发射器使用，但NS是多个Emitter的容器，代表一个完整特效。将原本应该拆分为两个Emitter的粒子类型（如火焰主体与火焰飞溅）强行放在同一Emitter中调试，会导致逻辑复杂且难以复用。

**误区二：混淆Emitter Update和Particle Update的执行对象。** Emitter Update中的逻辑每帧只执行一次，作用于整个Emitter；Particle Update每帧对每一颗存活的粒子各执行一次。将只需计算一次的全局值（如当前时间的正弦波）放入Particle Update，会造成数倍于必要次数的重复计算，在粒子数量多时会显著影响性能。

**误区三：直接修改继承自父Emitter的模块参数。** Niagara支持Emitter继承，子Emitter会继承父Emitter的所有模块。若在子Emitter中直接覆盖父模块的某个参数值，在父Emitter更新后该覆盖有时会被重置，正确做法是通过子Emitter的`Override`功能显式标记需要覆盖的参数。

## 知识关联

学习Niagara系统概述后，下一步应深入研究**Emitter与System**的关系，包括如何创建Emitter资产、设置继承关系，以及System层级的Emitter排列顺序如何影响渲染结果。Niagara的命名空间规则与虚幻引擎的蓝图变量作用域规则是平行的概念，熟悉蓝图的学习者可以以此为类比快速理解数据流向。Niagara的模块本质是HLSL代码的可视化封装，后续学习自定义模块时需要具备基础的着色器编程知识。Cascade系统的使用经验对学习Niagara有参考价值，但Cascade的"模块堆栈"思维定式需要主动转换为Niagara的"数据流"思维，否则容易在设计粒子逻辑时走弯路。