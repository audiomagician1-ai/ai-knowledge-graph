---
id: "anim-transition-rules"
concept: "转换规则"
domain: "animation"
subdomain: "state-machine"
subdomain_name: "状态机"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 转换规则

## 概述

转换规则（Transition Condition）是状态机中用于决定何时从一个动画状态切换到另一个状态的逻辑判断条件。与简单的状态转换（Transition）仅描述"从A到B的路径"不同，转换规则专门定义"在什么情况下允许走这条路"，是让动画系统自动响应游戏逻辑变化的关键机制。

转换规则的概念随动画状态机在游戏引擎中的普及而成熟，Unity的Animator系统（2012年随Unity 4引入）将其封装为可视化的Condition列表，开发者可以在Inspector面板中直接配置参数名、比较运算符和阈值，无需手写代码即可定义复杂的切换逻辑。Unreal Engine的AnimGraph同样提供了蓝图节点形式的转换规则编辑器。

在实际项目中，一套角色动画系统可能包含数十条转换路径，每条路径附带独立的转换规则。正是这些规则让"奔跑→跳跃→落地→行走"等动画序列能在运行时根据玩家输入和物理状态自动衔接，而不需要程序员逐帧手动控制播放器。

## 核心原理

### 三种条件类型

转换规则由三种基础条件类型构成，可单独使用也可组合叠加：

**布尔条件（Bool Condition）**：检测一个布尔参数是否为 `true` 或 `false`。例如在Unity中，若在Animator Controller里声明了布尔参数 `isGrounded`，则可以设置规则"当 `isGrounded == true` 时，允许从 `Falling` 状态转换到 `Landing` 状态"。布尔条件适合描述非此即彼的状态，如角色是否着地、是否持有武器。

**参数比较条件（Parameter Comparison）**：对浮点数（Float）或整数（Int）参数执行数值比较。支持的运算符包括 `Greater`、`Less`、`Equals`、`NotEqual`。具体公式为：`Parameter [Operator] Threshold`，例如 `speed > 0.1` 表示速度参数超过0.1时才允许从 `Idle` 切换到 `Walk`。阈值（Threshold）由开发者在编辑器中手动填写，需要与游戏逻辑中实际写入参数的数值范围相匹配。

**触发器条件（Trigger Condition）**：触发器（Trigger）是一种特殊的布尔参数，它在被消费（即满足一次转换条件）后自动重置为 `false`。设置规则"当 `Attack` 触发器被激活时从 `Idle` 切换到 `Attack_Swing`"，只要代码调用一次 `animator.SetTrigger("Attack")`，状态机就执行一次切换，不会因为布尔值持续为 `true` 而反复触发。

### 多条件的AND逻辑

在同一条转换路径上可以添加多个条件，这些条件之间默认是**AND关系**，即全部满足才允许转换。例如：
- 条件1：`speed > 5.0`  
- 条件2：`isGrounded == true`  

只有当角色速度超过5且处于地面时，才从 `Walk` 切换到 `Run`。如果需要OR逻辑，则需要建立两条独立的转换路径，每条路径携带不同的单一条件，两条路径都指向同一目标状态。

### 条件与转换时机的关系

转换规则满足后，状态机并不一定立刻切换。Unity中每条转换还有 `Exit Time`（退出时间）、`Transition Duration`（过渡时长）、`Transition Offset`（目标状态起始偏移）等属性。当 `Has Exit Time` 勾选时，即使规则已满足，系统也会等到当前动画播放到指定归一化时间（如 `0.9` 表示播放至90%）后才执行切换。这意味着转换规则是"允许切换的门禁"，而Exit Time是"切换的实际时刻"，两者共同决定最终行为。若想实现即时响应（如格斗游戏中按键立即出招），应禁用 `Has Exit Time` 并单独依赖触发器条件。

## 实际应用

**角色移动动画**：在大多数第三人称游戏中，Animator会声明一个名为 `MoveSpeed` 的浮点参数。`Idle→Walk` 转换规则设为 `MoveSpeed > 0.1`，`Walk→Run` 设为 `MoveSpeed > 5.5`，`Run→Walk` 设为 `MoveSpeed < 5.0`（注意使用比切换到Run时更低的阈值，形成滞后区间防止状态抖动），`Walk→Idle` 设为 `MoveSpeed < 0.05`。这四条规则构成一个完整的移动状态环。

**受击与死亡**：受击动画通常用触发器 `TakeDamage` 触发，规则设为"接收到 `TakeDamage` 触发器且 `Health > 0`（Int参数大于0）"，而死亡动画规则设为"接收到 `TakeDamage` 触发器且 `Health <= 0`"。同一个触发器结合不同的参数比较，实现分支跳转。

**武器收放**：布尔参数 `isArmed` 控制 `Unarmed_Idle` 与 `Armed_Idle` 之间的互相转换：`isArmed == true` 时走拔刀路径，`isArmed == false` 时走收刀路径，两条路径各自携带独立的 `Has Exit Time` 配置以保证拔刀动画完整播放。

## 常见误区

**误区一：将触发器当布尔参数使用**  
初学者经常用 `SetBool("Attack", true)` 实现攻击触发，然后在攻击动画结束后手动调用 `SetBool("Attack", false)`。这种做法在网络同步或帧率波动时容易出现"重置时机晚于状态机下一帧检测"的问题，导致攻击动画被连续触发两次。正确做法是改用 `SetTrigger("Attack")`，触发器的自动消费机制保证每次输入只产生一次切换。

**误区二：忽略条件方向性导致状态震荡**  
将双向转换的阈值设为同一个值，例如 `Walk→Run` 条件为 `speed >= 5.0`，`Run→Walk` 条件为 `speed <= 5.0`，当speed恰好等于5.0时，两条转换规则同时满足，状态机在同一帧内可能反复横跳。解决方法是引入约0.2到0.5的滞后区间，如 `Walk→Run` 用 `speed > 5.5`，`Run→Walk` 用 `speed < 5.0`。

**误区三：过度依赖Exit Time代替条件规则**  
部分开发者为省事，将转换条件留空并完全依靠Exit Time在固定时间点自动跳转。这在动画时长固定的离线游戏中勉强可行，但一旦动画需要被打断（如攻击中受击），空条件+Exit Time的组合无法响应外部触发器，只能等待播放结束，造成明显的操作延迟感。

## 知识关联

转换规则建立在**状态转换**概念之上：状态转换定义了状态之间存在哪些连线，而转换规则是附着在这些连线上的过滤器，两者缺一不可地共同构成完整的状态机跳转语义。

在Animator参数系统中，Bool、Float、Int、Trigger四种参数类型分别对应转换规则的不同使用场景，深入使用转换规则必须熟悉这四种参数的声明、赋值方法及其在状态机编辑器中的绑定方式。

对于复杂角色系统，掌握转换规则后通常需要进一步学习**层（Layer）与遮罩（Avatar Mask）**机制，以解决"上半身播放攻击动画同时下半身继续播放移动动画"等多状态并行问题，而每个层都有独立的状态机和转换规则集合。
