---
id: "anim-montage"
concept: "动画蒙太奇"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 3
is_milestone: false
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 动画蒙太奇

## 概述

动画蒙太奇（Animation Montage）是 Unreal Engine 中一种特殊的动画资产，其核心功能是让程序员和设计师通过 C++ 或蓝图脚本在**运行时**动态触发、控制和打断动画播放。与普通 AnimSequence 不同，Montage 并不依赖状态机的状态转换逻辑，而是通过 `PlayMontage` 节点或 `Montage_Play()` 函数直接调用，使其成为一次性动作（如攻击、翻滚、换弹夹）的首选载体。

动画蒙太奇最早出现于 UE4 时代，其设计灵感来源于电影剪辑中的"蒙太奇"概念——将多个片段拼接组合成完整叙事。在引擎实现层面，Montage 文件（`.uasset`）内部维护一个 **Slot Track** 列表和一个 **Section** 链表，Anim Graph 中需要放置对应的 Montage Slot 节点才能让 Montage 的输出姿势混入最终骨骼姿势。

Montage 在游戏开发中的重要性体现在以下两点：第一，它将"何时播放动画"的决策权从动画状态机转移到游戏逻辑层，极大降低了状态机的复杂度；第二，它天然支持 **Anim Notify** 和 **Notify State**，可以在动画的精确帧位置触发游戏事件（如开启碰撞盒、播放特效），这是 UE 战斗系统实现的基础机制之一。

---

## 核心原理

### Slot 与 Slot Group 的工作机制

Montage 中每一段动画片段都必须归属于某个 **Slot**，默认 Slot 名称为 `DefaultSlot`，所属的 Slot Group 为 `DefaultGroup`。Anim Graph 里的 `Slot` 节点充当"插槽"，当有 Montage 激活时，该节点输出 Montage 的混合姿势；当 Montage 未激活时，节点直接透传上游姿势（Pass-Through）。同一个 Slot Group 内同一时刻只能有一个 Montage 完全占用该 Group，第二个 Montage 播放时会触发前一个的 Blend Out。

混合遮罩（Blend Mask）正是在此层面发挥作用：通过为 Slot 节点配置混合遮罩，可以让 Montage 仅驱动上半身骨骼，而下半身继续执行状态机的移动动画，实现"边跑边射击"的分层效果。

### Section 与跳转逻辑

Montage 内部可以定义多个 **Section**，每个 Section 有独立名称（如 `Start`、`Loop`、`End`）并标记在时间轴上的起始时间点。蓝图中可通过 `Montage_JumpToSection()` 或设置 Section 之间的跳转关系实现循环结构：将 `Loop` Section 的下一个 Section 设置为自身，即可形成无限循环直至主动调用 `Montage_JumpToSection("End")` 为止。此机制常用于蓄力攻击、持续施法等需要"保持状态直到玩家释放按键"的场景。

### Blend In / Blend Out 与播放速率

Montage 在编辑器内可直接配置 **Blend In 时长**（默认 0.25 秒）和 **Blend Out 时长**（默认 0.25 秒），这两个值控制 Montage 权重从 0 到 1（Blend In）以及从 1 到 0（Blend Out）的过渡时间。`PlayMontage` 节点还暴露了 `InPlayRate` 参数，设置为 `2.0` 则动画以两倍速播放，常用于不同角色体型下统一攻击节奏的适配。

Montage 播放结束后，蓝图节点会回调 `OnCompleted`、`OnBlendOut`、`OnInterrupted` 三条执行引脚，开发者可在 `OnBlendOut` 引脚处理"动画即将结束"的状态重置，而 `OnInterrupted` 则响应被其他 Montage 打断的情形。

### Anim Notify 的精确帧触发

在 Montage 时间轴上，Anim Notify 可以插入在任意时间点。以近战攻击为例，通常在挥击动作接触帧（如第 0.18 秒）放置一个自定义 Notify 来启用碰撞检测，在动作回收帧（如第 0.42 秒）放置另一个 Notify 关闭碰撞检测，整个伤害窗口精确控制在 240ms 内，完全由动画资产本身定义，无需游戏逻辑代码硬编码时间延迟。

---

## 实际应用

**近战连击系统**：将三段连击动画分别命名为 `Attack1`、`Attack2`、`Attack3` 三个 Section，在 `Attack1` 的打击帧放置一个 Notify，Notify 回调中检测玩家是否再次按下攻击键，若是则调用 `Montage_JumpToSection("Attack2")`，否则播放到末尾自然结束。此方案避免了状态机中需要维护大量连击状态转换的问题。

**换弹夹动画**：换弹夹是一次性完整动作，适合用 Montage 而非状态机管理。在 C++ 中调用 `PlayMontage` 并传入换弹 Montage 资产引用，在 Montage 中途的特定帧 Notify 处执行子弹数量更新逻辑，`OnCompleted` 回调后将角色状态标记为"可开火"。整个流程保证了子弹数更新与动画表现的严格同步。

**过场对话动画**：一段包含多个角色动作的过场，可将所有分段动画放入同一个 Montage 的不同 Section，由对话系统依次调用 `Montage_JumpToSection()` 驱动播放节奏，而不需要为每个动作创建独立的 Montage 资产。

---

## 常见误区

**误区一：直接使用 Play Animation 节点替代 Montage**  
`Play Animation` 节点也可以直接播放 AnimSequence，但它绕过了 Anim Graph 中的 Slot 系统，无法与状态机的其他姿势进行加权混合。结果是动画播放时会完全覆盖全身骨骼，导致下半身移动动画丢失，且无法响应 Blend Mask 的分层配置。

**误区二：忘记在 Anim Graph 中添加 Slot 节点**  
创建了 Montage 资产并在蓝图中调用 `PlayMontage` 后，如果 Anim Graph 中没有对应 Slot 名称的 `Slot` 节点，角色不会产生任何可见变化，但引擎也不会报错。这是初学者最常遇到的调试陷阱：Montage 播放回调正常触发，只是输出姿势没有路由到骨骼网格体。

**误区三：将 Blend Out 时长设为 0 以求"立即切换"**  
将 Blend Out 设为 `0.0` 秒确实会让 Montage 瞬间退出，但这会导致姿势在单帧内发生跳变（Pose Popping），在慢动作或帧率波动时产生明显的视觉抖动。正确做法是保留至少 `0.1` 秒的 Blend Out，并确保被混合回的状态机姿势在此刻与 Montage 末尾姿势相近。

---

## 知识关联

**前置概念——混合遮罩（Blend Mask）**：Montage 的分层播放完全依赖 Blend Mask 的骨骼权重配置。若未在 Slot 节点上指定 Blend Mask，则 Montage 会以全身权重 `1.0` 混入，覆盖所有骨骼。只有理解 Blend Mask 如何按骨骼名称分配 `0~1` 权重值，才能正确实现上半身/下半身分离的 Montage 效果。

**横向关联——AnimNotify 与游戏逻辑**：Montage 是 UE 中 AnimNotify 最主要的触发载体。与直接在 AnimSequence 上挂载 Notify 相比，Montage 中的 Notify 在 Section 跳转时可以被跳过或重复触发，开发者需要了解 Section 边界对 Notify 触发行为的影响，避免跳转逻辑导致的伤害判定重复触发问题。

**架构定位**：在 UE 动画系统的整体架构中，Montage 作为"脚本驱动层"存在，状态机负责持续性循环动画（走、跑、待机），而 Montage 负责响应性、一次性动作。两者通过 Anim Graph 中的 Slot 节点汇合，Slot 节点位于状态机输出之后、Final Animation Pose 之前，确保 Montage 姿势拥有最高的混合优先级。