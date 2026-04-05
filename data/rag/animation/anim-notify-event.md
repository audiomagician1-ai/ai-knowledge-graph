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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 动画通知

## 概述

动画通知（Animation Notify，简称 AnimNotify）是 Unreal Engine 动画系统中内嵌于动画序列时间轴上的事件标记机制。它允许开发者在动画的特定帧位置触发自定义逻辑，例如在角色脚步落地的精确帧播放脚步声、在挥拳动画到达最大力度帧时开启碰撞检测，或在技能释放瞬间生成粒子特效。与代码层面的定时器（Timer）相比，动画通知的触发时机与动画帧严格绑定，不受帧率波动影响。

动画通知的设计源于游戏开发中"动画驱动逻辑"的需求。早期引擎通过在更新循环中轮询动画播放进度来触发事件，精度低且耦合性强。Unreal Engine 将通知系统集成进动画序列资产本身，使美术人员可以直接在 Persona 编辑器的 Notifies 轨道上拖放事件标记，无需修改蓝图逻辑即可调整触发时机。

动画通知分为两种主要类型：单帧触发的 **AnimNotify** 和具有持续时间的 **AnimNotifyState**。AnimNotify 在时间轴上表现为一个点，仅在该帧被执行一次；AnimNotifyState 则在时间轴上占据一段区间，分别在进入（NotifyBegin）、持续（NotifyTick）和离开（NotifyEnd）三个阶段执行对应逻辑，适合处理需要开关控制的行为，如攻击判定窗口的开启与关闭。

---

## 核心原理

### AnimNotify 的帧精确触发机制

动画系统在每次更新时会计算当前动画的播放位置（以归一化的 0.0～1.0 表示，或以实际时间秒数表示），并扫描时间轴上所有通知标记的位置。若本次更新跨越了某个通知的时间戳，则立即触发该通知。这一扫描过程发生在动画图（Animation Graph）求值之后、最终姿势写入之前，确保通知触发与骨骼位置保持严格的单帧同步。

在 C++ 层面，自定义 AnimNotify 需继承 `UAnimNotify` 并重写 `Notify(USkeletalMeshComponent*, UAnimSequenceBase*)` 函数；自定义 AnimNotifyState 则继承 `UAnimNotifyState`，重写 `NotifyBegin`、`NotifyTick` 和 `NotifyEnd` 三个函数，其中 `NotifyTick` 接收 `float TotalDuration` 和 `float FrameDeltaTime` 参数，可用于按比例插值计算进度。

### AnimNotifyState 的时间区间管理

AnimNotifyState 的持续时间在 Persona 编辑器中以拖动右侧边缘的方式设置，内部以帧数或秒数记录。当动画被循环播放且通知区间跨越循环点时，引擎会在循环接缝处正确触发 NotifyEnd 和下一次循环的 NotifyBegin，而不会出现状态泄露（State Leak）。这对于循环攻击动画中的碰撞窗口管理尤为关键。

若动画蒙太奇（Anim Montage）的某段被跳段（Section Jump）打断，处于激活状态的 AnimNotifyState 同样会立即收到 NotifyEnd 回调，防止碰撞检测或特效在动画切换后残留。

### 通知组与同步（Notify Group）

Unreal Engine 提供了 **Notify Group** 功能，允许将多个动画资产中的同名通知标记绑定到同一同步组（Sync Group）。当两个动画在混合过渡期间同时处于激活状态时，引擎可以选择以"主导动画"的通知为准，抑制"跟随动画"的同名通知，避免脚步声重复播放。此功能通过在 Notify 属性面板中设置 `Notify Filter Type` 为 `AllAnimations` 或 `CurrentStateMachine` 来控制。

---

## 实际应用

**脚步声与地面材质检测**：在奔跑动画中，将 AnimNotify 放置于左右脚落地的精确帧（通常需要在 Persona 中逐帧检查骨骼位置确认）。通知触发后，蓝图执行 Line Trace 检测地面材质，根据返回的物理材质资产播放对应脚步音效（木板、石头、泥地），整个逻辑与帧完全对齐。

**近战攻击碰撞窗口**：使用 AnimNotifyState 标记挥拳动画中拳头实际可造成伤害的时间段（例如挥拳动画总时长 0.6 秒中的第 0.15 秒至第 0.35 秒）。在 NotifyBegin 中调用 `SetCollisionEnabled(ECollisionEnabled::QueryOnly)`，在 NotifyEnd 中调用 `SetCollisionEnabled(ECollisionEnabled::NoCollision)`，精确控制碰撞盒的激活时段，避免攻击判定过早或过晚。

**武器拖尾特效**：在 AnimNotifyState 的 NotifyTick 中每帧记录武器骨骼的世界坐标，传入 Niagara 拖尾系统的 Ribbon 粒子，生成随攻击动作实时更新的残影效果。由于 NotifyTick 与动画帧完全同步，拖尾轨迹与武器实际运动路径严格匹配。

**IK 过渡控制**：在着陆动画的 AnimNotifyState 区间内，用 NotifyTick 传递的 `FrameDeltaTime / TotalDuration` 进度值插值脚部 IK 的影响权重，实现落地时 IK 从 0 平滑过渡到 1 的效果，比在动画蓝图中写独立插值逻辑更易与动画美术对齐。

---

## 常见误区

**误区一：认为 AnimNotify 的触发精度等同于游戏帧率**

AnimNotify 的触发精度实际上取决于动画序列本身的采样帧率（通常为 30fps 或 60fps），而非游戏的运行帧率。若游戏以 120fps 运行，动画系统每帧仍按动画资产的采样率推进，不会在两个动画帧之间插入额外的通知触发。同时，当游戏帧率极低（如单帧耗时超过动画时长）时，引擎仍会在同一帧内扫描并触发本应在多帧内依序触发的所有通知，保证通知不丢失。

**误区二：将 AnimNotifyState 的 NotifyTick 等同于 Tick 事件**

AnimNotifyState 的 NotifyTick 仅在动画实际播放期间且在 AnimNotifyState 覆盖的时间段内执行。当动画被暂停、权重降为 0 或蒙太奇被停止时，NotifyTick 不再调用，但对应的 NotifyEnd 仍会触发。因此不能用 NotifyTick 替代 Actor 的 Tick 来执行持续性游戏逻辑，它只适合与该动画状态强耦合的短时逻辑。

**误区三：在蓝图中用"动画播放完成"事件替代 AnimNotify**

`OnMontageEnded` 等蒙太奇完成回调的触发时机是动画蓝图求值结束后经过一定延迟才被分发的，无法精确定位到动画内部某帧。对于需要在动画第 N 帧触发的逻辑（如第 15 帧生成弹壳），必须使用 AnimNotify 而非播放完成事件，否则会产生视觉上可见的触发延迟。

---

## 知识关联

动画通知直接依赖**动画图（Animation Graph）**提供的姿势求值流程——通知扫描发生在动画图输出最终姿势之后，因此理解动画图的单帧求值顺序有助于判断通知触发与骨骼变换的先后关系。

在后续学习**动画序列器（Sequencer）**时会发现，Sequencer 提供了独立的事件轨道（Event Track）机制，与 AnimNotify 的应用场景有所重叠。AnimNotify 适用于游戏运行时的动态动画状态机，而 Sequencer 事件轨道更适合过场动画的固定时间轴触发。区分两者的核心在于触发场景是否需要与动画蓝图的状态机逻辑交互。

自定义 AnimNotify 类也是学习 Unreal Engine C++ 动画扩展的入门切入点——继承 `UAnimNotify` 并在构造函数中调用 `#if WITH_EDITOR` 宏设置编辑器显示颜色和名称，是标准的引擎扩展模式，可延伸到后续的自定义动画节点（Custom Animation Node）开发。