---
id: "vfx-niagara-event"
concept: "事件系统"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 事件系统

## 概述

Niagara事件系统是虚幻引擎Niagara粒子框架中专门用于粒子间通信的机制，允许一个粒子发出事件（Event）后，同一Niagara系统内的其他发射器（Emitter）通过事件处理器（Event Handler）接收并响应，从而实现级联触发效果。这种生产者-消费者模式打破了传统粒子系统中各发射器相互孤立的限制，让粒子行为可以相互感知、相互驱动。

事件系统在虚幻引擎4.20版本随Niagara正式引入，取代了Cascade中依赖蓝图触发器或参数集合才能实现的跨发射器通信方式。在Cascade时代，制作一个子弹击中地面后溅起碎石的效果，需要在蓝图中手动触发第二个粒子系统组件；而在Niagara事件系统中，整个过程可以在单一Niagara系统资产（`.ns`文件）内部自动完成。

事件系统对于制作多阶段特效至关重要——例如爆炸粒子碰撞地面后触发烟雾扩散、火焰粒子死亡时生成余烬、雨滴落地产生涟漪——这些效果都需要事件系统在粒子生命周期特定节点精确传递位置、速度、法线等载荷数据。

## 核心原理

### 事件的类型与数据载荷

Niagara内置三种原生事件类型，分别对应粒子生命周期的关键节点：

- **生成事件（Spawn Event）**：粒子被创建时发出，携带初始位置和速度。
- **死亡事件（Death Event）**：粒子生命结束时发出，常用于粒子消逝后在原位置生成新效果。
- **碰撞事件（Collision Event）**：粒子触发碰撞检测后发出，载荷中包含碰撞位置（`CollisionPosition`）、碰撞法线（`CollisionNormal`）和物理材质（`PhysicalMaterial`）三个关键字段，这是与碰撞检测模块直接对接的数据接口。

除原生类型外，开发者还可以在"粒子更新（Particle Update）"阶段使用**Generate Persistent Curve Event**模块创建自定义事件，向载荷中写入任意粒子属性（如颜色、自定义浮点数）。

### 事件的生产与消费流程

事件系统的工作流分为两个独立配置步骤，必须在同一Niagara系统内的不同发射器上分别设置：

1. **生产侧**：在发起发射器（Producer Emitter）的相应阶段（如"粒子碰撞"）添加`Generate Collision Event`模块，系统会将该发射器命名为事件源，并自动为此事件分配一个**事件名称（Event Name）**字符串，默认为`CollisionEvent`。

2. **消费侧**：在接收发射器（Consumer Emitter）的发射器属性面板中找到**Event Handler**区，点击"+"添加处理器，选择**事件源发射器**和对应的**事件名称**，再选择响应类型：`SpawnOnEvent`（收到事件时生成新粒子）或`UpdateOnEvent`（对现有粒子执行更新）。

两侧通过**事件名称字符串精确匹配**，拼写错误会导致事件静默失败而不报错，这是调试时最常见的陷阱。

### 事件数据的读取方式

消费侧发射器通过**Event Handler**上下文中的专用模块读取载荷。以碰撞事件为例，在事件处理的"Particle Spawn"阶段，使用`Receive Collision Event`模块可直接将`CollisionPosition`绑定到新粒子的`Position`属性，实现在碰撞点精确生成粒子。该模块还暴露`CollisionNormal`，可直接用于控制新粒子的初始速度方向，使溅射粒子沿碰撞面法线方向弹出，无需额外的向量计算。

事件载荷的数据类型是固定结构体，不能在运行时动态扩展字段；若需要传递额外信息（如当前粒子的颜色），必须在创建自定义事件时预先声明。

## 实际应用

**雨滴涟漪效果**：创建名为`Rain`的发射器，启用GPU碰撞检测并添加`Generate Collision Event`模块。再创建名为`Ripple`的发射器，在其Event Handler中指定源为`Rain`、事件名`CollisionEvent`，响应类型设为`SpawnOnEvent`，每次收到事件生成`Count = 1`个涟漪网格粒子，其Position直接绑定`CollisionPosition`。最终效果是每颗雨滴落点都会精确触发一圈涟漪，整个系统仅用1个`.ns`资产实现。

**子弹穿透级联碎片**：子弹发射器在死亡时发出Death Event，碎片发射器通过`SpawnOnEvent`在子弹消亡位置生成8到12颗碎石粒子，碎石粒子本身再通过第二层碰撞事件触发地面尘土发射器，形成三级级联链。注意三级链会在一帧内触发两次事件处理，帧率波动时需在`Event Handler`的**Max Events Per Frame**参数中设置上限（建议不超过64）以避免性能峰值。

## 常见误区

**误区一：认为事件是全局广播的**。事件系统的通信范围被严格限制在同一个Niagara系统实例（System Instance）内部。`Rain`系统的碰撞事件无法被另一个独立的`Ripple`系统接收，跨系统通信必须借助Niagara的用户参数（User Parameter）或蓝图接口实现。若在关卡中放置了两个相同的`Rain.ns`实例，它们各自的涟漪发射器只响应自身的雨滴，不会相互干扰。

**误区二：Death Event与粒子年龄归零等价**。部分开发者用`Particle Age >= Lifetime`条件来模拟死亡事件，但这无法捕捉被`Kill`模块强制终止的粒子。真正的Death Event由Niagara执行引擎在粒子实际从活跃列表移除时触发，包括被`Kill Particles`模块、碰撞杀死或年龄耗尽等所有终止路径，两者行为不等价。

**误区三：GPU发射器可以自由接收CPU发射器的事件**。Niagara事件系统对模拟类型有严格约束：CPU发射器可以同时充当生产者和消费者；GPU发射器只能消费来自**同为GPU模拟**的发射器事件，CPU→GPU的事件传递在Niagara中不被支持，会在编译时产生验证错误。

## 知识关联

事件系统的碰撞事件类型依赖**碰撞检测**模块提供触发源——只有在发射器中启用`Collision`模块并将`Collision Mode`设置为`GPU Collision`或`CPU Collision`之后，`Generate Collision Event`模块才有数据可发出。碰撞法线的精度直接决定了事件载荷中`CollisionNormal`字段的可靠性，进而影响消费侧粒子的运动方向计算。

学习事件系统之后，下一个关键概念是**数据接口（Data Interface）**。数据接口将事件系统的跨对象通信能力从发射器间扩展到外部场景数据（如样条曲线、骨骼位置、纹理采样），事件系统解决的是"粒子之间如何通信"，而数据接口解决的是"粒子与引擎其他系统如何通信"，两者共同构成Niagara系统与外部世界交换信息的完整通道。