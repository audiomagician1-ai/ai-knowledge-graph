---
id: "anim-notify-event"
concept: "动画通知"
domain: "animation"
subdomain: "animation-blueprint"
subdomain_name: "动画蓝图"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 动画通知

## 概述

动画通知（Animation Notify，简称 AnimNotify）是虚幻引擎动画系统中的一种机制，允许开发者在动画序列的**特定帧**上挂载事件，当动画播放至该帧时自动触发游戏逻辑。与依赖 Tick 轮询或计时器的事件触发方式不同，动画通知直接绑定在动画数据上，实现帧精确（Frame-Accurate）的事件分发，误差不超过一帧的播放间隔。

动画通知最早随虚幻引擎 4 的动画蓝图系统一同引入，其设计灵感来自传统 3D 动画软件中的"标记轨道"（Marker Track）概念。在 UE5 中，AnimNotify 体系进一步扩展，支持在 Sequencer 和 Montage 中复用相同的通知定义，无需为不同上下文重复编写触发代码。

动画通知的核心价值在于将"**何时触发**"的信息封装在动画资产本身，而非散落在游戏代码中。例如，一段攻击动画的出手帧、一段跑步动画的左右脚落地帧、一段开门动画的接触帧，这些时机都可以直接在 `.uasset` 层面标注，使动画师与程序员的工作流解耦。

---

## 核心原理

### AnimNotify 与 AnimNotifyState 的区别

虚幻引擎提供两种通知类型：

- **AnimNotify**：瞬时事件，仅在挂载帧触发一次 `Notify()` 回调。适合音效播放、粒子生成、足迹贴花等单次响应需求。
- **AnimNotifyState**：持续区间事件，具有 `NotifyBegin()`、`NotifyTick()` 和 `NotifyEnd()` 三个回调。开发者需在通知轨道上同时拖拽出一段区间，引擎会在该区间每帧调用 `NotifyTick(float DeltaTime)`。适合格斗游戏的攻击判定窗口（Hit Window）或角色无敌帧的管理。

两者在 C++ 层分别继承 `UAnimNotify` 和 `UAnimNotifyState`，需重写对应虚函数。

### 帧精确触发的实现机制

动画通知的触发由 `UAnimSequenceBase::GetAnimNotifies()` 在每次动画更新时检索。引擎计算当前 `CurrentTime` 与上一帧 `PreviousTime` 之间的区间，遍历序列上所有通知，判断其挂载时间是否落入 `[PreviousTime, CurrentTime]` 区间内。因此，即使动画播放速率（`PlayRate`）被修改，通知依然会在对应的**归一化时间位置**精确触发，而非依赖实际经过的秒数。

归一化触发公式为：

```
TriggerTime = NotifyTime / SequenceLength
```

其中 `NotifyTime` 为通知在序列中的绝对秒数，`SequenceLength` 为动画总时长（秒）。当动画以 `PlayRate = 2.0` 播放时，触发位置不变，但触发所对应的真实时间缩短为原来的一半。

### 通知的挂载与数据结构

在动画编辑器的"通知轨道（Notify Track）"面板中，右键单击时间轴即可添加通知。每条通知记录存储为 `FAnimNotifyEvent` 结构体，关键字段包括：

| 字段 | 含义 |
|---|---|
| `TriggerTime` | 触发时刻（秒） |
| `Duration` | 持续时长（仅 NotifyState 有效） |
| `Notify` | 指向 `UAnimNotify` 实例的指针 |
| `TrackIndex` | 所在通知轨道编号 |

一个动画序列可以拥有**多条通知轨道**，不同轨道上的通知彼此独立，便于分类管理（如将音效通知与游戏逻辑通知分轨存放）。

### 蓝图中的接收与响应

在动画蓝图的 **AnimGraph** 或 **EventGraph** 中，可直接添加 `AnimNotify_[通知名]` 事件节点来响应通知。若通知定义为自定义 C++ 类，则在 `Notify()` 函数体内可直接通过 `MeshComp->GetAnimInstance()` 获取 AnimInstance 指针，调用角色逻辑。蓝图自定义通知（Blueprint Notify）则无需 C++ 代码，在动画编辑器中选择"新建通知"后，事件节点会自动出现在 AnimInstance 的事件图表中。

---

## 实际应用

**脚步音效同步**：在跑步动画中，左脚落地帧（约第 8 帧）和右脚落地帧（约第 22 帧）各挂载一个 `AnimNotify_Footstep`，通知触发时读取角色脚下的物理材质，播放对应的泥地、石板或金属音效。这是第三人称游戏中最常见的通知用例，完全消除了音效与动作不同步的问题。

**近战攻击判定窗口**：使用 `AnimNotifyState` 在攻击动画的第 12 帧到第 18 帧之间定义 `AttackWindow` 状态。`NotifyBegin()` 激活武器碰撞体，`NotifyEnd()` 关闭碰撞体，`NotifyTick()` 每帧记录武器扫掠轨迹用于连续碰撞检测（Sweep Trace）。这比在 `AnimBP Tick` 中用布尔变量控制碰撞更精确，且碰撞窗口数据直接可视化于动画时间轴上。

**技能系统集成**：与 GAS（Gameplay Ability System）配合时，可将 `AnimNotify_PlayMontageNotify` 与 `UAbilityTask_PlayMontageAndWaitForEvent` 结合，通知触发后向 Ability Task 发送游戏标签事件（Gameplay Tag Event），从而在帧精确的时机推进技能状态机，无需在 `AbilityTick` 中轮询动画进度。

---

## 常见误区

**误区一：认为通知触发时机等于帧率固定的某一帧**。实际上通知挂载的是**时间坐标（秒）**，而非帧编号。在 30fps 动画中标注为"第 10 帧"的通知，其 `TriggerTime` 为 `10/30 ≈ 0.333` 秒。若项目以 60fps 运行，该通知仍在 0.333 秒处触发，不会变成"第 20 帧"。混淆时间与帧编号会导致开发者误判通知位置。

**误区二：AnimNotifyState 的 `NotifyEnd` 一定会在 `NotifyBegin` 之后调用**。当动画被中断（如 Montage 被 `StopMontage()` 强制停止）时，引擎会在同一帧内依次调用尚未结束的所有 `NotifyState` 的 `NotifyEnd()`，但如果代码在 `NotifyBegin()` 中分配了资源，必须在 `NotifyEnd()` 中做好清理，否则中断场景下会出现攻击碰撞体永久激活的 Bug。

**误区三：蓝图通知与 C++ 通知性能相当**。蓝图通知每次触发需经过反射系统查找蓝图函数，在高频触发场景（如每帧多角色同时触发脚步通知）下，C++ 重写 `UAnimNotify::Notify()` 的开销明显低于纯蓝图通知。性能敏感的通知建议使用 C++ 实现并通过 `UFUNCTION(BlueprintCallable)` 暴露必要接口。

---

## 知识关联

动画通知依赖**动画图（AnimGraph）** 的状态机驱动动画播放——只有当某个动画序列处于活跃播放状态时，其上挂载的通知才会被评估和触发。理解状态机中的过渡规则有助于预判哪些通知可能因过渡中断而提前触发 `NotifyEnd`。

在掌握动画通知之后，学习**动画序列器（Sequencer）** 时会发现，Sequencer 的通知轨道与动画蓝图共用同一套 `UAnimNotify` 类定义，可直接复用已有通知资产。Sequencer 中的通知还额外支持绑定到特定 Actor 实例，使过场动画中的帧精确事件触发与游戏运行时逻辑无缝衔接。此外，动画通知与 **Animation Montage** 紧密配合：Montage 的分段（Section）跳转并不影响通知的时间轴评估，通知依然按绝对时间坐标触发，这一点在设计连招动画时尤为重要。
