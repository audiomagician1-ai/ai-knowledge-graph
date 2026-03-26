---
id: "montage-system"
concept: "Montage系统"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.6
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

# Montage系统

## 概述

Animation Montage（动画蒙太奇）是Unreal Engine中用于在蓝图或C++代码中直接播放和控制动画的特殊资产类型。与普通动画序列不同，Montage不直接挂载在动画状态机中，而是通过`PlayMontage`节点或`Montage_Play`函数在运行时动态调用，使程序员和设计师能够在逻辑层面精确触发特定动画片段，例如攻击、拾取道具或翻越障碍。

Montage系统最早在UE3时代以AnimMontage形式引入，目的是解决游戏玩法动画（Gameplay Animation）无法灵活与游戏逻辑交互的问题。在UE5中，Montage与Motion Warping、Full Body IK等新系统深度整合，成为近战战斗、技能系统和过场动画的标准实现方案。

Montage之所以重要，在于它将动画资产与游戏逻辑解耦：攻击动画的伤害检测时机、音效触发点、特效激活帧都可以在Montage内部精确定义，而不需要修改动画蓝图的状态机拓扑结构。一个典型的格斗游戏角色可能拥有超过50个独立Montage文件，每个对应一种技能或交互动作。

---

## 核心原理

### Montage Slot（插槽机制）

Montage必须指定至少一个**Slot（插槽）**才能播放，Slot名称默认为`DefaultSlot`。在动画蓝图的AnimGraph中，需要插入`Slot`节点并填写对应名称，Montage播放时会将动画数据"注入"到该插槽位置，覆盖或混合正在运行的状态机输出。Slot支持分组（Slot Group），同一组内同时只能有一个Slot处于活跃状态，这防止了同组多个Montage并发播放时产生冲突。UE5内置的`FullBody`和`UpperBody`插槽组分别对应全身动画与上半身叠加动画的典型用例。

### Section（分段）系统

每个Montage可以划分为若干命名的**Section**，这是Montage区别于普通动画序列的核心结构。在Montage编辑器的时间轴顶部点击添加Section后，可以通过蓝图函数`Montage_JumpToSection(SectionName, Montage)`在运行时跳转到指定段落。Section还支持循环跳转：将Section A的"下一Section"指向自身可实现循环待机动画，等待条件满足后再调用`Montage_JumpToSection`切换到Section B（如收刀动画）。Section的起止时间以秒为单位记录在Montage资产的`CompositeSections`数组中。

### Blend In / Blend Out参数

Montage播放时通过`BlendIn`和`BlendOut`曲线控制与当前姿势的过渡。默认`BlendIn`时长为0.25秒，`BlendOut`时长为0.25秒，均使用`EaseInOut`曲线类型。可在Montage资产的Asset Details面板中单独调整每个Montage的融合参数，也可在`PlayMontage`节点的`InTimeToStartMontageAt`参数中指定从哪一帧开始播放，从而跳过前摇动画。播放速率通过`InPlayRate`参数控制，设置为2.0时动画以两倍速播放但BlendIn/BlendOut时长不变。

---

## 实际应用

**近战攻击连击系统**：设计师将普攻分为三个Section：`Attack1`、`Attack2`、`Attack3`，每段Section末尾设置一个短暂的"连击窗口"。玩家在窗口期内按键时，蓝图检测到输入后调用`Montage_JumpToSection("Attack2")`，否则Montage在当前Section结束后自然BlendOut。这种结构使连击手感可以完全通过Montage编辑器调整，无需修改任何蓝图逻辑。

**技能系统中的Root Motion**：在Montage的Asset Details中启用`Enable Root Motion`后，角色的位移由动画曲线驱动而非CharacterMovement组件。冲刺攻击技能的位移数据直接烘焙在动画中，避免了位移量硬编码在蓝图里导致与动画不同步的问题。UE5的Motion Warping插件可以在Montage播放期间实时修改Root Motion的目标位置，实现锁定敌人位置的近战攻击对齐。

**武器切换与上半身动画叠加**：为上半身Slot创建换弹Montage，动画蓝图的AnimGraph同时运行下半身移动状态机和上半身`UpperBody` Slot节点，二者通过`Layered Blend Per Bone`节点以`spine_01`骨骼为分割点叠加，实现角色奔跑换弹的同步表现。

---

## 常见误区

**误区一：认为Montage可以脱离动画蓝图独立播放**

新手常常只在资产中创建Montage并调用`PlayMontage`，但发现角色没有任何动作变化。根本原因是动画蓝图的AnimGraph中没有插入对应名称的`Slot`节点。Montage的数据必须经由Slot节点"流入"动画图表才能生效，缺少Slot节点等同于信号有发送者但没有接收者。

**误区二：混淆Section跳转与从头播放的区别**

`Montage_JumpToSection`在Montage已经播放时才有效，它不会重新触发BlendIn过渡，而是直接跳至目标Section的起始帧。如果在Montage未播放时调用此函数，什么也不会发生。需要重置到初始状态时应先调用`Montage_Stop`再重新`PlayMontage`，而不是跳转到第一个Section，后者会跳过BlendIn导致动画切换生硬。

**误区三：在同一Slot中叠放过多Montage导致姿势冲突**

同一个Slot Group在同一时刻只能有一个活跃Montage。当新的Montage开始播放时，旧的Montage会立即被中断并触发其`OnMontageEnded`事件，`bInterrupted`参数值为`true`。若业务逻辑依赖`OnMontageEnded`来释放技能锁定状态，必须区分"自然结束"（`bInterrupted = false`）和"被打断结束"两种情况，否则会出现角色技能状态机卡死的问题。

---

## 知识关联

**前置知识**：理解Montage系统需要熟悉**动画蓝图**中AnimGraph的节点流结构，特别是Pose如何从状态机传递到Output Pose节点的路径，因为Slot节点正是插入在这条路径上的一个"拦截点"。不了解AnimGraph拓扑结构的开发者无法判断Slot节点应该放置在哪个混合层级。

**后续概念**：掌握Montage的Section结构后，自然延伸到**动画通知（Animation Notify）**系统。Notify本身可以放置在普通动画序列中，但在Montage中使用时有额外的`Notify State`能力，允许在某个Section的时间范围内持续触发逻辑，例如在攻击Section的第15帧到第22帧之间开启武器碰撞检测盒，第23帧自动关闭，这是近战伤害系统的标准实现模式。