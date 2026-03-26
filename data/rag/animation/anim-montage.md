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

动画蒙太奇（Animation Montage）是 Unreal Engine 中一种特殊的动画资产，其核心特征是**可以通过蓝图或 C++ 代码在运行时动态播放、暂停、跳转和停止**，区别于普通 AnimSequence 只能在动画图表中静态引用。一个 Montage 文件内部包含多个**Slot（插槽）轨道**，每个 Slot 可容纳一段或多段动画片段（Section），Montage 调度器会在这些 Section 之间按照指定顺序或随机跳转逻辑串联播放。

蒙太奇的名称来源于电影剪辑术语，UE 在 UE3 时代（对应 Unreal Development Kit，约 2009 年发布）引入前身机制，在 UE4 正式定型为现有 Montage 资产格式，并延续至 UE5。其设计目标是解决"一次性触发型动画"（如攻击、翻滚、换弹）的控制问题——这类动画需要游戏逻辑按需调用，而非由状态机常驻管理。

Montage 之所以重要，在于它是 UE 动画系统中**唯一内建 Anim Notify 插入、Section 跳转和播放速率动态修改**的资产类型，且播放接口直接暴露在角色的 `UAnimInstance` 上，调用一行 `PlayMontage` 节点即可触发复杂的分层动画逻辑。

---

## 核心原理

### Slot 插槽与动画图表的结合

Montage 本身不独立渲染动画，它必须依赖动画蓝图（AnimBP）图表中插入的 **Slot 节点**才能生效。每个 Slot 节点携带一个命名标识（默认名称为 `DefaultSlot`，上半身常用 `UpperBody`），当 Montage 播放时，引擎将该 Montage 中对应 Slot 的动画数据"注入"到图表的该节点位置，与来自下方状态机的姿态进行混合叠加。这意味着如果动画蓝图中没有放置对应名称的 Slot 节点，调用 `PlayMontage` 将**静默失败**，角色不显示任何蒙太奇动作。

Slot 节点的权重由 Montage 的 `BlendIn` 和 `BlendOut` 曲线控制：默认 `BlendIn` 时长为 **0.25 秒**，`BlendOut` 为 **0.25 秒**，开发者可在 Montage 资产的 Blend Settings 面板中单独调整每个 Section 的混入混出曲线类型（Linear、Cubic 等）。

### Section 分段与跳转逻辑

一个 Montage 可以包含多个具名 Section，例如一套连击动画可划分为 `Combo1`、`Combo2`、`Combo3` 三段。在蓝图中调用 `MontageJumpToSection(SectionName)` 可在运行时任意跳转，而不需要为每段连击单独创建 Montage 资产。Section 之间默认顺序播放，但可在 Montage 编辑器的 **Section 关联面板**中设置"下一段"为自身，形成单段循环，或设为 `None` 让播放自然结束。

Section 的时间位置精度依赖 Montage 的采样帧率，建议与源 AnimSequence 帧率一致（通常为 **30fps** 或 **60fps**）以避免关键帧偏移导致的 Notify 时序错位。

### Anim Notify 与事件驱动

Montage 轨道上可插入 Anim Notify 和 Anim Notify State，二者在 Montage 时间轴上的位置以**秒**为单位标注。最常用的内置 Notify 是 `PlayMontageNotify` 与 `PlayMontageNotifyWindow`，它们会在 `OnMontageBlendingOut`、`OnMontageEnded` 等委托之外额外触发具名回调，供蓝图用 `EventMontageNotify` 节点侦听。这套机制让攻击判定窗口、脚步音效、粒子特效的触发时机精确绑定到动画帧，而非依赖 Tick 轮询。

---

## 实际应用

### 射击游戏换弹动画

FPS 游戏中换弹动作需要在动画播放至某帧时触发"弹夹替换"逻辑，同时上半身播放换弹、下半身继续移动循环。实现方案：创建一个 `UpperBody` Slot 的 Montage，在换弹动作的第 **18 帧**（以 30fps 计，即 0.6 秒处）插入 `PlayMontageNotify`，命名为 `ReloadComplete`；动画蓝图图表中 `UpperBody` Slot 节点位于移动状态机之上，通过混合遮罩（Blend Mask）限制权重只作用于脊柱以上骨骼。角色控制器调用 `PlayMontage` 后，侦听 `EventMontageNotify(ReloadComplete)` 事件来执行弹药数量更新逻辑。

### RPG 连击系统

格斗 RPG 中三段连击的 Montage 包含 `Attack1`、`Attack2`、`Attack3` 三个 Section。在 `Attack1` 的攻击窗口 Notify State 存续期间，若玩家再次按下攻击键，调用 `MontageJumpToSection("Attack2")`，否则 `Attack1` 结束后 Section 关联指向 `None` 自然停止。此方案相比使用三个独立 Montage 减少了资产数量，且可在一次 `OnMontageEnded` 委托中统一处理连击重置逻辑。

---

## 常见误区

### 误区一：以为 PlayMontage 可以不依赖动画蓝图直接驱动骨骼

许多初学者在角色蓝图中调用 `PlayMontage` 后发现角色纹丝不动，误以为函数调用有误。实际原因是动画蓝图图表中缺少对应命名的 Slot 节点。Montage 的数据必须经由 Slot 节点"注入"AnimBP 的姿态计算管线，二者缺一不可。调试手段是在输出日志搜索 `"Montage has no slot"` 警告信息。

### 误区二：将 Montage 用于持续循环动画

Montage 的 BlendOut 机制和 Slot 权重管理针对"一次性触发"场景设计，将跑步、待机等长期循环动画放入 Montage 并通过 Section 自循环来实现会引入额外的混合开销，且状态机无法感知其激活状态，导致过渡条件失效。持续循环动画应放在状态机的 State 节点中管理，Montage 仅用于需要外部脚本触发的动画事件。

### 误区三：认为 MontageJumpToSection 会从头播放目标 Section

`MontageJumpToSection` 是**立即跳转**，不会触发目标 Section 的 BlendIn，也不会重置 Section 内的 Notify 已触发状态（Notify 状态重置需要完整重放整个 Montage）。若需要从特定 Section 的第 0 帧干净地开始播放，正确做法是调用 `PlayMontage` 并在调用时传入 `StartingSection` 参数，而非在播放过程中用 Jump 命令。

---

## 知识关联

**前置概念——混合遮罩（Blend Mask）**：混合遮罩定义了骨骼层级中每根骨骼的权重系数（0.0 到 1.0），Montage 的 Slot 节点在与底层状态机姿态叠加时，正是读取这份权重表来决定哪些骨骼受 Montage 影响。若未正确配置混合遮罩，上下半身分离播放将无法实现，Montage 会覆盖全身姿态。理解混合遮罩中每根骨骼权重的具体数值（如将 `pelvis` 设为 0.0、`spine_01` 设为 1.0 的分界点设置）是正确使用多 Slot Montage 的前提。

**在系统中的位置**：动画蒙太奇处于 UE 动画管线的**脚本控制层**，位于 AnimBP 逻辑图（Event Graph 调用）与动画图表（Anim Graph 中的 Slot 节点）的交汇点。掌握 Montage 后，开发者可以将游戏逻辑（输入、AI 决策、技能系统）与动画表现解耦，通过统一的 `PlayMontage` / `OnMontageEnded` 接口实现事件驱动的动画控制架构，这是 UE 项目中绝大多数角色动作系统的标准实现模式。