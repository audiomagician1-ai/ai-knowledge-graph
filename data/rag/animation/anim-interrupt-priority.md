---
id: "anim-interrupt-priority"
concept: "中断优先级"
domain: "animation"
subdomain: "state-machine"
subdomain_name: "状态机"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
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


# 中断优先级

## 概述

中断优先级（Interrupt Priority）是动画状态机中用于决定哪些动画转换可以打断当前正在播放动画的规则体系。当角色同时满足多个转换条件时，优先级数值较高的转换会强制结束当前动画并切换到目标状态，而低优先级转换则被忽略。例如，一个奔跑动画可以被"受伤"动画打断，但不能被"普通行走"动画打断，这种层级关系正是由中断优先级决定的。

在早期动画系统（如 Unity 4.x 之前的版本）中，动画控制器缺乏精细的中断优先级配置，开发者只能依靠脚本手动切换状态，导致动画衔接混乱。Unity 5.0 引入了 Transition Interruption Source（转换中断源）参数，正式将中断优先级作为状态机的内置功能，允许设计师在 Animator 编辑器中直接为每条转换箭头配置中断规则，而无需额外编写代码。

中断优先级的意义在于解决"动画竞争"问题：当玩家在攻击动画的后摇帧连按跳跃键时，系统必须判断当前攻击状态是否允许被跳跃打断。没有优先级规则，角色会出现动画卡顿、动作取消失效或动作无响应等体验问题。合理配置优先级可以精确控制哪些动作"可取消"、哪些动作"无敌帧"不可打断，这直接影响战斗手感和技能设计。

---

## 核心原理

### 转换优先级的排序依据

在 Unity Animator 中，同一状态的多条出发转换（Transition）按照在 Inspector 面板中的**列表顺序**决定优先级——列表中排名第 0 的转换优先级最高，依次向下递减。当多个转换条件在同一帧同时为真时，系统仅执行排序最靠前的那一条。因此，把"死亡"转换放在列表第 0 位、"攻击"放在第 1 位、"移动"放在最后，就能保证死亡动画永远优先于其他状态触发。

### Interruption Source 的四种模式

Unity 的每条 Transition 都有一个 **Interruption Source** 下拉菜单，提供以下四个选项，直接控制中断行为：

| 模式 | 含义 |
|---|---|
| **None** | 转换一旦开始，不允许任何其他转换打断它 |
| **Current State** | 只有"起始状态"自身的其他转换可以打断本次转换 |
| **Next State** | 只有"目标状态"的出发转换可以打断本次转换 |
| **Current State Then Next State** | 先检查起始状态，再检查目标状态的转换，依次判断 |

例如将"跑步 → 攻击"这条转换的 Interruption Source 设为 **Current State**，则当角色在转换过渡期间触发了"跑步"状态的"翻滚"条件，翻滚会立即打断这次向攻击状态的切换，实现"取消预输入"效果。

### Ordered Interruption 开关的作用

每条 Transition 还有一个布尔选项 **Ordered Interruption**（默认勾选）。当此项开启时，只有在当前转换列表中**排序更靠前**的转换才能打断当前过渡；关闭时，任何满足条件的转换都可以打断，不受列表顺序限制。这意味着如果关闭 Ordered Interruption，一条优先级很低的转换也可以在过渡中途强行插入，适用于需要"任意取消"的技能系统，但需谨慎使用，否则容易产生动画跳变。

### 优先级计算与 Any State 的交互

Any State 节点发出的转换默认具有**全局最高优先级**，在每一帧的转换评估中先于所有普通状态转换被检查。但 Any State 转换的 Interruption Source 固定为 None，即 Any State 的转换本身一旦启动无法被打断。这使得"任意状态 → 死亡"这类转换成为天然的最高优先级中断，不需要在每个状态中单独配置死亡转换。

---

## 实际应用

**格斗游戏的攻击取消系统**：将普通攻击三段连击的每一段动画转换的 Interruption Source 设置为 Current State，并在转换列表中把"重攻击"排在"轻攻击"之前。结果是：玩家在轻攻击过渡帧按下重攻击键，重攻击会打断轻攻击转换；但反过来，不能用轻攻击打断重攻击，实现了技能优先级的单向约束。

**受伤硬直的无敌判断**：对"普通攻击"状态的所有出发转换关闭 Ordered Interruption，同时将"受伤"的 Any State 转换设为最高优先。这样在攻击动画的前摇阶段可以被任意技能取消，但一旦进入受伤硬直状态，该状态自身的转换列表中没有其他出发项，实现"受伤帧不可取消"。

**载具上下车的防误操作**：将"上车"动画转换的 Interruption Source 设为 None，持续时间为 1.2 秒。在这 1.2 秒内玩家按下任何其他按键都无法打断上车动画，避免因手柄误触导致上车中途回到站立状态的体验问题。

---

## 常见误区

**误区一：转换列表顺序就等于动画播放顺序**
很多初学者认为列表排第 0 的转换会"先播放"，实际上列表顺序只决定**同帧多条件均为真时哪条优先执行**，与动画播放顺序无关。如果某帧只有一个条件为真，无论它排第几，都会正常触发。

**误区二：Interruption Source 设为 None 等于"动画不可跳过"**
None 模式只阻止**过渡期间**被其他转换打断，但目标状态播放结束后若有 Exit Time 转换，动画依然会正常退出。想实现"此动画播完才能离开"，需要同时关闭 Can Transition To Self 并将目标状态的所有出发转换都使用 Has Exit Time 且 Exit Time = 1.0，而非仅依赖 Interruption Source。

**误区三：Any State 优先级永远最高无需额外配置**
Any State 的转换确实全局最早被评估，但如果同一帧有两条 Any State 转换同时满足条件（例如"任意 → 死亡"和"任意 → 眩晕"同时触发），系统同样按照 Any State 节点发出转换的**列表顺序**决定哪条生效。忽略这一点会导致低优先级的眩晕意外覆盖死亡动画。

---

## 知识关联

中断优先级建立在 **Any State 转换**概念之上：Any State 是实现全局最高优先级中断的基础节点，掌握 Any State 的触发机制和 Can Transition To Self 参数后，才能正确理解为什么 Any State 的转换在中断优先级层级中独立于普通状态转换之外。

在实际项目中，中断优先级与**混合树（Blend Tree）**紧密配合：当一个状态本身是混合树时，该混合树内部的子状态不参与外层的中断优先级判断，整个混合树作为单一状态节点参与竞争。此外，**层（Layer）权重**与优先级是两套独立系统，上层 Layer 的动画可以覆盖下层，但这种覆盖不属于中断，不受 Interruption Source 规则约束。