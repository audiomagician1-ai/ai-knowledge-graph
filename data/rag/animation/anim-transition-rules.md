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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 转换规则

## 概述

转换规则（Transition Rule）是状态机中决定何时从一个动画状态切换到另一个状态的判断逻辑。它本质上是一组条件表达式，当这些条件被满足时，状态机才会执行跳转。没有转换规则，状态机中的每个动画状态都会永远循环播放，无法响应任何游戏逻辑或玩家输入。

转换规则的概念源自有限状态自动机（Finite State Automaton）理论，在20世纪50年代由 Stephen Kleene 等计算机科学家形式化。游戏引擎将这一理论引入动画系统，以 Unity 的 Animator Controller 和 Unreal Engine 的 Animation Blueprint 为代表，均在2010年代将可视化转换规则编辑器作为标配功能。

转换规则的重要性体现在它将动画表现与游戏状态解耦：动画师只需定义每条规则的条件，程序员负责在代码中修改参数值，两者互不干扰。一个错误的转换规则会导致动画闪烁、卡帧或跳变，直接影响游戏的视觉流畅度，因此理解其三种核心触发方式至关重要。

## 核心原理

### 布尔条件触发

布尔型转换规则使用 true/false 参数作为判断依据。例如在 Unity 中，将一个名为 `isGrounded` 的 Bool 参数设置为转换条件，当 `isGrounded == true` 时，从"下落"状态切换到"落地"状态。布尔条件适合表达非此即彼的状态，如角色是否着地、是否持有武器、是否处于隐身状态。

布尔条件的陷阱在于它不会自动复位。若将 `isJumping` 设为 true 触发跳跃，但忘记在跳跃结束后将其置回 false，则状态机会在跳跃动画结束后立刻再次触发同一条规则，产生无限跳跃的 bug。这与下文的事件触发（Trigger）有本质区别。

### 参数比较触发

参数比较规则使用数值型参数（Int 或 Float）与一个阈值进行比较，支持以下六种运算符：`Greater`（>）、`Less`（<）、`Equals`（==）、`NotEqual`（!=）、`GreaterOrEqual`（>=）、`LessOrEqual`（<=）。

以移动速度控制动画为例，定义规则如下：

- `speed > 0.1` → 从"待机"切换到"行走"
- `speed > 5.5` → 从"行走"切换到"奔跑"
- `speed < 0.1` → 从"行走"切换到"待机"

阈值的设置需要留有余量（Hysteresis），即从"行走"切换到"奔跑"的阈值（5.5）应高于从"奔跑"退回"行走"的阈值（4.5），防止速度在临界值附近小幅波动时动画来回抖动。这种双阈值策略在游戏动画中称为**迟滞设计**。

Float 参数比较还涉及浮点精度问题：Unity 文档明确指出，使用 `Equals` 比较两个 Float 值时，实际执行的是"差值小于 0.00001"的近似判断，开发者应避免用 Float 做严格等值比较。

### 事件触发（Trigger）

Trigger 是一种特殊的布尔参数，其特征是**被消费后自动置回 false**。在 Unity 中，调用 `animator.SetTrigger("Attack")` 会将该 Trigger 置为 true，状态机检测到后立即执行对应转换，并将参数自动重置。这使得 Trigger 非常适合处理一次性动作，如攻击、翻滚、受击反应。

Trigger 的消费机制遵循先到先得原则：若同一帧内有多条规则都监听同一个 Trigger，只有优先级最高的那条转换会消费它，其余规则不会被触发。在 Unity 的 Animator Controller 中，转换优先级由列表顺序决定，排在上方的规则优先级更高。

### 多条件组合

单条转换规则可以包含多个条件，这些条件之间是**逻辑与（AND）**关系，即所有条件同时满足才触发转换。例如：

```
条件1: isGrounded == true
条件2: speed < 0.1
→ 同时满足 → 切换到"待机"状态
```

若需要逻辑或（OR）的效果，必须创建两条独立的转换规则，分别指向同一目标状态，各自携带不同的条件。

## 实际应用

以第三人称动作游戏中的角色动画状态机为例，"待机→行走→奔跑"这一常见链路使用 Float 参数 `MoveSpeed` 和阈值比较规则实现：待机到行走的阈值通常设为 0.1，行走到奔跑设为 5.0，各反向转换的阈值分别降低 0.5 作为迟滞缓冲。

在格斗游戏的连招系统中，Trigger 参数被大量使用。例如"普攻1→普攻2→普攻3"的连击窗口，每次按键调用 `SetTrigger("LightAttack")`，但只有在前一动画播放到特定帧（通常是 60%~80% 进度）时，对应的转换规则才被激活，超出窗口期则 Trigger 被清除不产生响应，这通过在转换规则中额外添加 `NormalizedTime > 0.6` 的 Float 条件来实现。

在 Unreal Engine 的 Animation Blueprint 中，转换规则以蓝图节点图的形式编辑，可以调用任意游戏逻辑函数，表达能力比 Unity 的参数比较更强，但也更容易因逻辑复杂而难以维护。

## 常见误区

**误区一：Trigger 和 Bool 可以互换使用**
许多初学者用 Bool 参数模拟攻击触发，手动 SetBool(true) 再 SetBool(false)，认为效果等同于 Trigger。实际上，若 SetBool(false) 在状态机更新之前执行，状态机在该帧根本检测不到 true 值，转换规则永远不会触发。Trigger 专门解决了这一问题，它的置位与消费由引擎在状态机更新周期内统一处理。

**误区二：转换规则条件满足后动画立刻切换**
转换规则有一个重要参数叫做**退出时间（Exit Time）**，默认值在 Unity 中为 0.75（即当前动画播放到75%时才检查条件）。开发者常常发现"明明条件满足了，动画却没有立刻切换"，原因往往是 Exit Time 未关闭。对于需要即时响应的转换（如受击），必须将 `Has Exit Time` 取消勾选，让转换规则在条件满足的第一帧就生效。

**误区三：转换规则的"条件满足"等于"转换完成"**
条件满足仅代表转换**开始**，过渡动画（Transition Duration）仍需经历一段混合时间（通常为 0.1~0.25 秒）。在此期间，状态机实际上处于两个状态的混合中，若在混合期间再次满足其他规则条件，可能产生意外的三状态混合，在人物运动动画中表现为短暂的"橡皮人"变形。

## 知识关联

转换规则建立在**状态转换**的基础上：状态转换定义了"从哪里到哪里"，转换规则则回答"什么时候走"。两者共同构成一条完整的有向边——没有规则的转换永远无法执行，没有目标状态的规则无意义存在。

参数类型（Bool、Float、Int、Trigger）是转换规则的数据载体，理解四种类型的差异直接决定能否正确选择规则形式。Float 的迟滞设计、Trigger 的自动消费机制，以及 Exit Time 与即时响应的权衡，是实际项目中设计角色动画状态机时最频繁需要决策的技术点。