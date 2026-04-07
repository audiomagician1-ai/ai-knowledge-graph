---
id: "state-machine-anim"
concept: "动画状态机"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["状态"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 动画状态机

## 概述

动画状态机（Animation State Machine）是游戏引擎动画系统中用于管理角色动画切换逻辑的有限状态自动机模型。它将角色所有可能的动画状态（如站立、奔跑、跳跃、死亡）建模为节点，将状态之间的切换规则建模为带条件的有向边，使动画系统能够根据游戏逻辑的变化自动选择并平滑过渡到正确的动画片段。

动画状态机的概念源于有限状态机（Finite State Machine，FSM）理论，最早被系统性地引入游戏动画领域是在2000年代初期，随着《光晕》等3A游戏对复杂角色动画的需求增长而普及。Unreal Engine 在 UE4（2012年）中将其作为动画蓝图（Animation Blueprint）的核心可视化工具推出，Unity 则于2012年在 Mecanim 系统中引入了 Animator Controller 实现同等功能，两者都将状态机从纯代码配置变为了可视化图形编辑界面。

动画状态机的重要性在于它将"播放哪个动画"这一决策逻辑从游戏代码中解耦出来，交由专门的状态机节点图管理。设计师无需修改 C++ 或脚本代码，只需在编辑器中连线即可调整角色动画行为，使动画师、设计师和程序员能够并行协作。

---

## 核心原理

### 状态（State）

状态是状态机中的基本单元，每个状态对应一个或一组动画片段的播放逻辑。在 Unreal Engine 的动画蓝图中，一个状态内部可以放置完整的动画图（Animation Graph）节点网络，例如混合空间（Blend Space）或单帧序列。进入某个状态时，引擎会从该状态内部的动画图输出最终姿势（Pose）。每个状态机有且仅有一个**默认状态（Default State / Entry State）**，动画蓝图初始化时自动进入该状态，通常设置为角色的 Idle（待机）动画。

### 转换（Transition）

转换是连接两个状态的有向边，决定了从状态 A 切换到状态 B 的时机和方式。每条转换有以下三个关键属性：
- **转换条件（Condition）**：一个布尔表达式，当其为真时允许触发转换。例如 `Speed > 150.0` 表示移动速度超过 150 cm/s 时从 Idle 切换到 Run。
- **混合时间（Blend Duration）**：过渡动画的持续时间，单位为秒，典型值在 0.1～0.3 秒之间，控制两个动画之间交叉淡入淡出（Cross-fade）的长度。
- **转换优先级**：当某状态同时满足多条转换条件时，按优先级从高到低选择。

在 Unity Mecanim 中，转换还有一个 **Has Exit Time** 选项，勾选后只有当前动画播放到指定的归一化时间点（如 0.9，即播放至 90% 位置）才允许触发转换，适用于攻击等必须完整播放的动作。

### 条件与参数（Condition & Parameter）

状态机的转换条件基于**动画参数（Animator Parameter）**进行判断。参数由游戏逻辑代码在每帧更新，状态机根据参数值评估所有出边的转换条件。参数类型包括：

| 类型 | 说明 | 典型用例 |
|------|------|----------|
| Float | 浮点数，支持 `>` `<` 比较 | 移动速度、混合权重 |
| Int | 整数，支持 `=` `≠` 比较 | 武器类型编号 |
| Bool | 布尔值，支持 `true/false` | 是否在地面上 |
| Trigger | 单次触发，消费后自动重置为 false | 跳跃、攻击事件 |

Trigger 类型与 Bool 类型的本质区别在于**自动消费机制**——Trigger 被任意一条转换消费后立即归零，避免了因 Bool 未手动重置而导致的意外循环触发问题。

### 分层状态机（Layered State Machine）

分层状态机（Layered Animation State Machine）允许多个状态机层叠运行，每层控制身体的不同部位或优先级不同的动画逻辑。在 Unreal Engine 中通过 **Animation Layers** 实现，在 Unity 中通过 **Animator Controller Layers** 实现。

每层有一个**混合权重（Weight）**参数（范围 0.0～1.0）和一个**混合模式（Blend Mode）**：
- **Override（覆盖模式）**：上层完全替换下层的输出姿势，权重为 1 时完全覆盖，常用于上半身独立播放射击动画。
- **Additive（叠加模式）**：将上层动画的增量叠加到下层姿势上，常用于呼吸起伏、受伤晃动等细节动画。

分层的典型场景是角色同时奔跑（下半身由基础层控制）并开枪（上半身由叠加层控制），两层状态机独立运转互不干扰。

---

## 实际应用

**角色移动动画管理**：一个标准第三人称角色的基础状态机通常包含 Idle、Walk、Run、Sprint 四个状态，以速度浮点参数为转换条件。Idle→Walk 的条件设为 `Speed > 10`，Walk→Run 设为 `Speed > 150`，Run→Sprint 设为 `Speed > 400`（数值单位为 Unreal 的 cm/s）。反向转换设置相同阈值或略低阈值（滞后处理）防止抖动。

**攻击连段逻辑**：格斗游戏中常见的三段连击可用状态机实现：Attack1 → Attack2 → Attack3 → Idle，每个 Attack 状态使用 Has Exit Time 确保动画播放到特定帧（例如归一化时间 0.6）才检测下一段输入，若未输入则自动回到 Idle，若检测到攻击 Trigger 则进入下一段。

**受伤与死亡处理**：死亡状态通常设置为**任意状态（Any State）**的转换目标。在 Unity 中，"Any State" 是一个特殊节点，它的转换条件一旦满足，无论当前处于哪个状态都会立刻切换到死亡状态，省去了从每个状态单独连线到 Death 的重复工作。

---

## 常见误区

**误区一：Bool 参数与 Trigger 参数混用导致动画卡死**
新手常用 Bool 参数替代 Trigger 来触发一次性动作（如跳跃）。由于 Bool 不会自动重置，如果代码中忘记在跳跃动作播完后将其设回 false，状态机会持续满足跳跃转换条件而无法切回 Idle，角色表现为永远循环播放跳跃动画开头。正确做法是跳跃、攻击等一次性触发动作一律使用 Trigger 类型参数。

**误区二：混合时间过长掩盖状态机逻辑错误**
将所有转换的 Blend Duration 设为较大值（如 0.5 秒）会让错误的状态切换被长时间交叉淡出掩盖，看起来"过渡流畅"，但实际上状态切换时序已经错误。调试时应临时将 Blend Duration 归零，使状态切换变为瞬切，便于准确观察状态机的跳转时机是否与预期一致。

**误区三：分层状态机权重设置混淆 Override 与 Additive**
将需要完全控制上半身的射击动画层设为 Additive 模式，会导致射击姿势叠加在下半身奔跑动作上产生形变，角色腰部出现扭曲。上半身独立控制必须使用 Override 模式，并通过骨骼遮罩（Avatar Mask）将该层的影响范围限制在脊椎以上的骨骼，避免干扰腿部动画。

---

## 知识关联

动画状态机构建在**动画蓝图（Animation Blueprint）**之上——动画蓝图提供了事件图（Event Graph）和动画图（Anim Graph）的整体框架，而状态机是动画图中的一类特殊节点，负责选择和混合哪段动画输出到最终姿势。学习动画状态机之前，需要掌握动画蓝图中参数的读取与更新机制，理解每帧 `BlueprintUpdateAnimation` 如何将游戏逻辑的速度、姿态数据写入状态机所依赖的参数。

在实际项目中，复杂角色（如具有多种武器、骑乘状态的 RPG 角色）往往会将状态机拆分为多个**子状态机（Sub-State Machine）**进行模块化管理。例如将所有近战攻击状态封装为一个名为 MeleeAttack 的子状态机节点，从外部看只是状态图中的一个普通节点，内部包含数十个攻击状态的完整转换逻辑，从而保持顶层状态机的清晰可读性。