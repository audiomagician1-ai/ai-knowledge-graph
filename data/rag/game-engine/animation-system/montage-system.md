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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

Animation Montage（动画蒙太奇）是Unreal Engine中一种特殊的动画容器资产，允许开发者在蓝图或C++代码中直接调用、控制和混合动画片段，而无需在动画蓝图的状态机中预先建立所有过渡关系。Montage的核心价值在于将"触发式"动画逻辑（如攻击、翻滚、换弹）从状态机中解耦出来，通过`PlayMontage`节点或`Montage_Play()`函数即可在任意时机播放。

Montage系统最早随Unreal Engine 4引入，旨在解决复杂动作游戏中状态机节点爆炸的问题。在UE4/UE5中，一个Montage文件本质上是对一或多个AnimSequence的引用和调度编排，它并不复制原始动画数据，而是以Section和Slot为单位对动画片段进行非破坏性组织。

Montage之所以在战斗系统、交互动画和技能系统中被广泛采用，原因在于它提供了三个其他动画资产不具备的能力：跨动画蓝图的Slot插槽混合、Section之间的程序化跳转逻辑，以及与游戏逻辑深度集成的Notify事件。

---

## 核心原理

### Slot插槽机制

Montage通过**Slot（插槽）**将自身插入动画蓝图的混合管线。在动画蓝图的AnimGraph中，必须放置一个`Slot`节点（默认名为`DefaultSlot`），Montage只会在该Slot所属的层级上被混合，不会干扰与Slot无关的其他动画层（例如移动的下半身IK）。

一个Montage可以包含多个Slot轨道（如`UpperBody`、`FullBody`），每个Slot轨道独立占据动画蓝图中对应名字的Slot节点位置。这使得"上半身攻击+下半身跑步"的分层播放成为可能——攻击Montage使用`UpperBody` Slot，下半身的跑步状态机保持独立运行，两者在`LayeredBlendPerBone`节点处以脊椎骨为分割点进行混合。

### Section与跳转逻辑

**Section（片段）**是Montage内部的命名时间区段，每个Section对应时间轴上的一段动画。开发者可通过以下蓝图函数在运行时控制Section跳转：

- `Montage_JumpToSection(SectionName, Montage)`：立即跳到指定Section起始帧
- `Montage_SetNextSection(SectionNameToChange, NextSection, Montage)`：修改当前Section播放完毕后的跳转目标

利用`SetNextSection`可以实现**连击链（Combo Chain）**：默认情况下Section A播放完毕跳回到Idle Section结束Montage；当玩家在正确时机按下攻击键时，调用`SetNextSection("Attack1", "Attack2")`将跳转目标改为下一段攻击动画，从而形成流畅的连击序列，而不需要为每种连击路径单独建立状态机过渡。

### 混合时间与权重

Montage拥有独立的**Blend In**和**Blend Out**时间参数，默认Blend In为0.25秒，Blend Out为0.25秒。这两个值决定了Montage权重从0淡入到1、再从1淡出到0的曲线形状。`PlayMontage`节点还暴露了`PlayRate`（播放倍率）和`StartingPosition`（起始秒数）参数，可在调用时动态覆盖资产内的默认值。

权重计算公式为：当前帧Montage对原始姿势的覆盖比例 = `MontageWeight × SlotNodeWeight`，其中`SlotNodeWeight`由动画蓝图中Slot节点上游的姿势权重决定。若Slot节点的输入姿势权重为0.5（例如处于BlendPose节点中），最终Montage影响力最高只有50%。

---

## 实际应用

**换弹动画（Reload Animation）**是Montage最典型的使用场景。换弹Montage通常包含三个Section：`ReloadStart`（掏出弹夹）、`ReloadLoop`（循环填弹，用于霰弹枪逐发填装）和`ReloadEnd`（复位动作）。游戏逻辑调用`PlayMontage`并监听`OnMontageEnded`委托，在Montage结束后将弹药数量更新到UI，保证动画与数据同步。

**技能打断（Ability Interruption）**中，当角色受击需要打断当前技能时，调用`Montage_Stop(BlendOutTime, Montage)`，其中`BlendOutTime`设为0.1秒可实现近乎即时的停止同时保留短暂的混合过渡避免姿势跳变。UE5的GameplayAbility系统（GAS）中，`UGameplayAbility::EndAbility()`内部正是通过此函数结束关联的Montage任务。

**过场对话动画**场景下，一个Montage可以在同一时间轴上放置多个Slot轨道（`Body`、`Facial`、`HandGesture`），分别驱动躯干、面部和手势骨骼组，实现多层次的表情与动作同步，而无需将三条动画序列合并成一个资产。

---

## 常见误区

**误区一：认为Montage可以不依赖动画蓝图独立运行。**
Montage必须通过AnimInstance生效，播放Montage的Actor的SkeletalMesh上必须有一个运行中的AnimInstance，且该AnimInstance的AnimGraph中存在对应名称的Slot节点。如果AnimGraph中没有放置`DefaultSlot`节点，调用`PlayMontage`不会报错，但角色姿势完全不会改变——这是初学者最常遇到却难以排查的问题。

**误区二：将Section等同于独立的AnimSequence资产。**
Section只是Montage时间轴上的标记点，它没有自己的混合参数，也不能单独被其他系统引用。两个Section之间若引用了不同的AnimSequence，切换时的平滑性完全依赖`Montage_JumpToSection`本身触发的Blend In逻辑（约0.2秒默认值），而非两个AnimSequence之间的过渡设置。

**误区三：认为同一角色同时只能播放一个Montage。**
UE5的AnimInstance维护一个Montage实例列表，同一Slot上的多个Montage会按照激活顺序进行权重叠加，最新激活的Montage权重最高。不同Slot上的Montage完全互不干扰，可以真正并行播放。

---

## 知识关联

学习Montage系统需要先掌握**动画蓝图**中AnimGraph的基本结构，特别是Slot节点的放置位置和`LayeredBlendPerBone`的骨骼遮罩配置，否则无法理解Montage权重为何在某些情况下不生效。

Montage系统直接引出**动画通知（Animation Notify）**的高级用法：Montage时间轴上可以放置Notify Track，在特定帧触发`AnimNotify`事件或`AnimNotifyState`范围事件。例如在攻击Montage的第0.3秒放置`AN_EnableHitbox`通知，在第0.6秒放置`AN_DisableHitbox`通知，实现帧精确的碰撞盒开关，这是Montage与纯AnimSequence相比在战斗系统中的核心优势所在。

此外，UE5的**GameplayAbility系统（GAS）**中的`UAbilityTask_PlayMontageAndWait`任务节点是对Montage系统的封装，它将`OnCompleted`、`OnBlendOut`、`OnInterrupted`和`OnCancelled`四种结束原因分别暴露为输出引脚，这一设计完全基于Montage的`FOnMontageEnded`委托机制。