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

生成模式（Spawn Mode）是Unreal Engine Niagara粒子系统中控制粒子"何时"与"以何种方式"被创建进入模拟世界的机制集合。不同于粒子在存活期间的行为控制，生成模式专门决定粒子的诞生时机、数量和触发条件，是粒子效果从无到有的第一道关卡。

Niagara系统在UE4.20版本中正式取代Cascade成为主推粒子编辑器，生成模式作为其Emitter模块体系的首要环节，被设计为可堆叠的模块化结构——开发者可以在同一个Emitter上同时叠加多个不同的生成模式模块，例如同时使用Spawn Rate持续生成背景烟雾，再叠加一个Spawn Burst Instantaneous制造爆发瞬间的火花。

理解生成模式的核心价值在于：错误的生成策略会直接导致性能浪费或视觉缺陷。使用过高的Spawn Rate会在一秒内生成数千个粒子拖垮GPU，而错误地用持续Rate代替Burst则会让爆炸效果看起来像是缓慢冒烟，而非瞬间爆发。

---

## 核心原理

### Spawn Rate：基于时间的持续生成

Spawn Rate模块以"每秒粒子数"（Particles Per Second，PPS）为单位持续匀速创建粒子。其内部计算逻辑使用**累积小数帧**机制：每一帧实际生成数 = `Rate × DeltaTime + 上一帧余量`，整数部分立即生成，小数部分留存到下一帧累积。这意味着即便帧率波动，30 PPS的设置在1秒内依然精确生成30个粒子，而不会因帧率不稳定产生数量漂移。

Spawn Rate支持绑定Niagara参数，例如将Rate绑定到`User.SpawnIntensity`浮点参数，可在蓝图中用`Set Niagara Variable (Float)`实时调整生成速率，制作如营火风力变化时火焰粒子随风速变稠变稀的动态效果。

### Spawn Burst Instantaneous：瞬时爆发

Burst模式在指定时间点**一次性**生成固定数量的粒子，核心参数为`SpawnCount`（生成数量）和`SpawnTime`（触发时刻，单位为秒，相对于Emitter激活后的本地时间）。一个典型子弹击中地面的烟尘效果会设置`SpawnTime = 0.0`、`SpawnCount = 80`，确保效果激活的第0帧立刻产生80颗尘粒，形成瞬间迸射感。

Burst支持设置`SpawnCount Min/Max`随机范围，例如设置Min=60、Max=100，系统每次激活时随机选取区间内整数，避免多次触发完全相同的粒子数量带来的重复感。可以在单个Emitter中添加多条Burst条目，例如时刻0.0生成主爆发，时刻0.15再追加一次余震效果。

### 事件触发生成（Event Handler Spawn）

Niagara的事件系统允许一个Emitter的粒子**死亡、碰撞或自定义事件**触发另一个Emitter生成新粒子。具体实现路径为：在发送方Emitter的Particle Update阶段添加`Generate Death Event`模块，在接收方Emitter中添加`Event Handler`并设置`Spawn Per Event`数量。

例如制作烟花效果：主Emitter的每颗烟花粒子死亡时，通过Death Event通知子Emitter在该空间位置生成8～12颗子弹粒子。事件传递的Payload数据（如位置`Position`、速度`Velocity`）可以直接注入子粒子的初始属性，使子粒子继承父粒子的动量方向，物理感更真实。

### Spawn Per Frame：帧锁定生成

与Rate不同，`Spawn Per Frame`模块每帧固定生成N个粒子，**不考虑DeltaTime**。这意味着帧率为60fps时每秒生成60×N个粒子，帧率降为30fps时每秒只生成30×N个。此模式极少用于常规特效，主要用于需要"每帧必有粒子更新"的特殊场景，如GPU粒子驱动的流体模拟或需要严格每帧输出数据点的技术性应用。

---

## 实际应用

**持续环境特效**：营地篝火的火星效果使用Spawn Rate设置为`15～25 PPS`，配合User参数绑定风力值，风大时PPS自动提升至40，视觉上模拟风吹火旺的状态。

**武器开枪闪光**：枪口火焰Emitter采用单条`Spawn Burst Instantaneous`，SpawnTime=0、SpawnCount=30，Emitter的Loop Behavior设置为`One Shot`，每次开枪事件通过蓝图调用`Activate(Reset)`重新触发，保证每次射击产生一次性的爆发闪光，而非持续燃烧。

**粒子链式反应**：爆炸碎片粒子落地碰撞时，通过`Generate Collision Event`触发地面粒子Emitter，在碰撞点生成3颗石块碎屑粒子，Payload中传递碰撞法线`CollisionNormal`，使碎屑沿反射方向弹开，整个效果无需蓝图介入，纯在Niagara系统内完成链式生成。

---

## 常见误区

**误区一：认为Burst等同于"Rate极大值"**
部分初学者用极高的Spawn Rate（如10000 PPS）并让Emitter只存活0.01秒来模拟Burst效果。这种方式无法保证粒子集中在同一帧生成，因为Rate的累积帧机制会将粒子分散到多帧，导致爆发感消失；同时Emitter生命周期管理的开销远高于直接使用一条Burst条目。

**误区二：Event Handler Spawn不设置生成上限导致雪崩**
当事件触发的子粒子本身也携带Death Event时，若未在Event Handler中勾选`Max Spawns Per Frame`限制，父粒子死亡→子粒子生成→子粒子死亡→孙粒子生成的链式反应会在数帧内使粒子数量指数级暴涨，直接卡死编辑器。正确做法是为链式Event的最末级Emitter禁用Death Event输出，或设置每帧最大生成数为固定上限（如16）。

**误区三：混淆Spawn Rate的全局时间与Emitter本地时间**
Burst的`SpawnTime`参数使用的是**Emitter激活后的本地经过时间**，而非游戏世界的全局时间。若Emitter设置了`Pre-Warm`预热秒数（例如2秒），则SpawnTime=0的Burst实际上在系统对玩家可见之前已经触发完毕，玩家只会看到已经扩散的粒子而看不到爆发瞬间，这是制作循环特效预热时必须注意的时间偏移问题。

---

## 知识关联

生成模式的参数（如SpawnCount、Rate值）本质上都是Niagara参数体系中的`Module Input`，在学习过**参数与属性**之后，你已经具备将这些数值绑定到User Parameter或System Parameter的基础，可以直接在蓝图中动态控制生成逻辑。

生成模式决定了粒子"出生"的条件，而粒子出生后立刻进入**粒子生命周期**的管理——包括Particle Spawn阶段的初始属性设置、Particle Update阶段的每帧行为更新以及粒子死亡时的回收逻辑。生成模式中Burst的`SpawnCount`直接决定了同一时刻有多少粒子进入生命周期管线，数量过大会造成同帧初始化压力，这是后续学习性能优化时需要回溯的关键节点。