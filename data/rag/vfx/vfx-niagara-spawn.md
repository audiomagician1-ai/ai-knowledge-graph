---
id: "vfx-niagara-spawn"
concept: "生成模式"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 生成模式

## 概述

生成模式（Spawn Mode）是Niagara系统中控制粒子**何时、以何种速率**产生的核心机制。它决定了粒子系统在时间轴上的粒子数量分布方式，直接影响特效的视觉密度和爆发节奏。Niagara中的生成模式通过专用的**发射器生成（Emitter Spawn）**和**粒子生成（Particle Spawn）**两个执行阶段来实现，这两个阶段在每帧运行的顺序上是固定且不可互换的。

生成模式的概念在Unreal Engine 4时代就已在Cascade粒子系统中存在，但Niagara于UE 4.20版本引入后，将生成策略拆分为独立模块，允许多个生成模块同时叠加运行，赋予美术更高的组合自由度。例如，你可以同时启用一个持续速率模块和一个爆发模块，两者的输出粒子数会相加，而不会互相覆盖。

理解生成模式对于控制特效性能至关重要：粒子数量直接影响GPU和CPU的计算开销。一个每秒生成500个粒子的持续速率设置，与一次性爆发500个粒子的Burst设置，在瞬时性能峰值和平均开销上有本质区别，选错生成模式会导致帧率尖刺或特效失去冲击力。

---

## 核心原理

### Spawn Rate：持续速率生成

Spawn Rate模块以**每秒粒子数（Particles Per Second，PPS）**为单位持续生成粒子。其内部逻辑基于**时间累积（Time Accumulator）**机制：每帧将`DeltaTime × SpawnRate`的结果累积到一个浮点数中，当累积值超过1.0时，实际生成对应数量的整数粒子，并保留小数部分供下一帧继续累积。

$$N_{spawn} = \lfloor Accumulator + \Delta t \times R \rfloor$$

其中 $R$ 为设定的SpawnRate值，$\Delta t$ 为帧间隔时间，$Accumulator$ 为上一帧的残余小数。这意味着在低帧率情况下（如15fps），Spawn Rate为100时每帧约生成6~7个粒子，仍能保持总体数量的稳定性，而不是在低帧率下粒子数量成比例减少。

### Burst：爆发式生成

Burst模块在**指定时间点**一次性释放固定数量的粒子，常用于爆炸、碰撞火花、技能释放瞬间等需要强烈冲击感的场景。在Niagara的Burst设置中，每个Burst条目包含三个参数：

- **Time**：触发时刻（相对于发射器激活后的秒数，如`0.0`表示立即触发）
- **Count**：生成粒子数量（整数）
- **Count Low**：若大于0，则实际数量在`Count Low`到`Count`之间随机取整数，用于制造自然变化感

多个Burst条目可以在同一发射器中共存，例如在0.0秒生成50个粒子，在0.5秒再生成30个粒子，模拟爆炸后的二次迸发效果。Burst与SpawnRate叠加时，同一帧内两者的粒子都会进入同一粒子生成阶段执行初始化。

### 事件触发生成（Event Handler Spawn）

事件触发生成依赖Niagara的**事件系统**，允许一个发射器（或其他系统）产生的事件驱动另一个发射器生成粒子。常见事件类型包括：

- **Collision Event**：粒子碰撞到物体表面时触发，常用于弹孔飞溅特效
- **Death Event**：粒子生命周期结束时触发，常用于粒子消失时产生碎片或烟雾
- **Location Event**：粒子携带位置信息，驱动子发射器在该位置生成新粒子

事件触发生成的特点是**每个事件对应一批粒子生成**，生成数量通过`Spawn Per Event`参数控制。若一帧内发生了10次碰撞事件，`Spawn Per Event`设为3，则该帧总共生成30个子粒子。事件数据（如碰撞法线、位置）可直接通过`EventPayload`传递给新生成的粒子，无需额外的参数绑定。

### 脚本化生成（Spawn Script）

Niagara还支持通过自定义HLSL或可视化脚本节点实现完全程序化的生成逻辑。在`Particle Spawn`阶段插入自定义模块，可以根据游戏逻辑参数（如角色速度、与玩家的距离）动态调整每帧生成数量，实现普通Spawn Rate无法覆盖的动态密度效果。

---

## 实际应用

**火焰特效**通常组合使用Spawn Rate与随机化参数：设置SpawnRate为80~120（使用`Uniform Ranged Float`绑定到该参数），配合生命周期1.5~2.5秒，维持火焰的密度感与自然波动。

**爆炸特效**的标准做法是关闭Spawn Rate（设为0），仅使用单个Burst条目在`Time=0.0`时释放150~300个粒子，确保爆炸的瞬时冲击感。爆炸烟雾的二级发射器则通过**Death Event**在主发射器粒子消亡时生成，避免烟雾与火焰同时爆发导致视觉混乱。

**拖尾特效**（如刀光）常将SpawnRate设置为极高值（500~1000），并将发射器的`Loop Duration`设为0.1~0.2秒，配合武器挥动动画的时间窗口，在短暂时间内密集生成粒子构成连续轨迹。

---

## 常见误区

**误区一：认为Burst的Time参数是游戏世界时间**
Burst的`Time`参数是相对于**发射器自身激活后的本地时间**，而非游戏全局时间轴。如果发射器被延迟激活（通过`Emitter Delay`设置了0.5秒延迟），Burst的`Time=0.0`仍然指发射器开始运行后的第0秒，而非系统整体启动后的第0秒。混淆这两个时间坐标系会导致Burst粒子不在预期时刻出现。

**误区二：Spawn Rate越高粒子越多越好**
高Spawn Rate配合长生命周期会导致活跃粒子数（Active Particle Count）持续累积。以SpawnRate=200、生命周期=5秒为例，稳定状态下活跃粒子数高达1000个。Niagara在GPU模拟模式下，超过`Max GPU Particle Count`（默认通常为1,048,576）会直接丢弃粒子；在CPU模式下则会触发内存分配压力。美术应始终在发射器的`Fixed Bounds`和`Max Particle Count`中设定合理上限。

**误区三：事件触发生成可以跨Niagara系统使用**
事件触发生成（Event Handler）只能在**同一个Niagara系统内的发射器之间**传递。跨系统的事件通信需要通过蓝图或`User Parameter`传递外部信号，无法直接在两个独立的`NiagaraSystem`资产之间使用内置事件机制。

---

## 知识关联

生成模式依赖**参数与属性**中介绍的`Float参数`、`User Parameter`绑定机制——SpawnRate和BurstCount都可以绑定到用户参数，由蓝图在运行时动态修改，例如根据技能等级调整爆发粒子数量。

生成模式结束后，每个被创建的粒子立即进入**粒子生命周期**阶段，执行初始位置、速度、颜色等属性的初始化逻辑。生成模式决定了**粒子的产生时机和数量**，而粒子生命周期决定了**每个粒子从诞生到消亡的完整行为序列**，二者共同构成Niagara发射器运作的完整时间线。