---
id: "ai-behavior-tree"
concept: "行为树"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 3
is_milestone: false
tags: ["AI"]

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



# 行为树

## 概述

行为树（Behavior Tree，简称BT）是一种用于描述AI代理决策逻辑的树形数据结构，起源于2000年代初期的游戏AI研究，在《光环2》（2004）的开发过程中得到早期工程实践，后被Unreal Engine 4将其内置为官方AI编程框架并大幅推广。与有限状态机（FSM）相比，行为树通过层级化的节点组合，使NPC行为既能灵活扩展，又能避免"状态爆炸"问题——当角色需要50种以上行为时，FSM的状态转换连线会急剧失控，而行为树可通过增加分支节点无缝扩展。

行为树的执行依赖于"Tick"机制：游戏引擎每帧（或按指定间隔）从根节点开始遍历整棵树，每个节点执行后必须返回三种状态之一：**Success（成功）**、**Failure（失败）** 或 **Running（运行中）**。正是这套返回值体系驱动了整棵树的控制流，使得复杂行为能够通过简单节点的组合来实现。在Unreal Engine中，行为树必须配合Blackboard（黑板）组件使用，Blackboard充当AI的"工作记忆"，存储键值对数据供所有节点读写。

## 核心原理

### 四类基础节点类型

行为树节点分为四大类，各司其职：

**控制节点（Composite）** 负责决定子节点的执行顺序与逻辑。最常用的两种是Selector和Sequence：
- **Sequence（顺序节点）**：从左到右依次执行子节点，遇到第一个返回Failure的子节点立即停止并返回Failure；只有所有子节点均返回Success，自身才返回Success。可理解为逻辑"与"（AND）。
- **Selector（选择节点）**：从左到右执行子节点，遇到第一个返回Success的子节点立即停止并返回Success；只有所有子节点均返回Failure，自身才返回Failure。可理解为逻辑"或"（OR）。

**叶节点（Leaf / Task）** 是实际执行动作的终端节点，例如`MoveTo`、`PlayAnimation`、`Attack`等。叶节点不包含子节点，直接与游戏逻辑交互。

**装饰器（Decorator）** 包裹单个子节点，对其返回值或执行条件进行修改，下节详述。

**服务节点（Service）** 附加于控制节点上，在所在子树激活期间按固定间隔执行，用于维护Blackboard数据，下节详述。

### Decorator（装饰器）的工作机制

Decorator是行为树中一种"拦截器"角色的节点，它附加在某个节点的顶端，对被装饰节点的执行资格或返回结果施加影响。常见的内置Decorator包括：

- **Blackboard条件装饰器**：检查Blackboard上的某个键是否满足条件（如`TargetActor != null`），不满足则直接返回Failure，阻止子节点执行。
- **Loop装饰器**：将子节点的执行重复指定次数（可设置为无限循环），无论子节点返回何值都继续循环直到达到次数上限。
- **Invert（取反）装饰器**：将子节点返回的Success翻转为Failure，或将Failure翻转为Success，常用于构造"当某条件不成立时执行"的逻辑。
- **Cooldown装饰器**：为子节点添加冷却时间（单位为秒），冷却期间子节点强制返回Failure。

Decorator还具有**Observer Abort（观察者中止）** 属性，可设置为`None`、`Self`、`Lower Priority`或`Both`。当设置为`Lower Priority`时，一旦该Decorator的条件在当前帧重新变为满足，行为树会中止优先级更低的正在运行分支，立即跳回该节点重新执行——这是实现"发现敌人立即打断游荡行为"等响应式逻辑的关键机制。

### Service（服务节点）的工作机制

Service附加于Composite节点（Sequence或Selector）而非Task节点，当所在子树处于激活状态时，Service按其`Interval`（间隔，默认0.5秒）加上`Random Deviation`（随机偏差）周期性执行，而不是每帧执行。这一设计是出于性能考量：感知范围查询、距离计算等操作无需每帧刷新，0.5秒的间隔已足够流畅。

典型用途是在Service的`ReceiveTick`函数中更新Blackboard的值，例如："每0.5秒查询一次周围50米内的敌方单位，将距离最近的一个写入Blackboard的`ClosestEnemy`键"。Task节点随后直接读取`ClosestEnemy`键做出决策，从而实现感知层与决策层的解耦。

Service与Decorator的根本区别在于：Decorator决定**是否执行**某节点，Service决定**执行期间持续维护**哪些数据。

## 实际应用

**巡逻-追击-攻击三段式AI**是行为树最经典的应用案例。根节点下挂一个Selector，其三个子分支按优先级从高到低排列：
1. 最左分支：Sequence节点 + "HasTarget" Blackboard Decorator → `MoveTo(Target)` → `MeleeAttack`
2. 中间分支：Sequence节点 + "HeardNoise" Blackboard Decorator → `MoveTo(NoiseLocation)` → `Investigate`
3. 最右分支：`PatrolAlongSpline`（无条件兜底）

当Decorator的Observer Abort设为`Lower Priority`时，NPC一旦发现目标（Blackboard上`HasTarget`变为True），正在执行的巡逻Task会立即被中止，控制流跳至攻击分支。

在Unreal Engine 5的行为树编辑器中，一个典型的Service节点代码结构为：覆写`ReceiveTick(DeltaSeconds)`函数，调用`GetPerceptionComponent()->GetPerceivedActors()`，过滤后将结果写入Blackboard，整个过程不超过10行蓝图节点。

## 常见误区

**误区一：将所有逻辑塞进Task节点**。初学者常将条件判断直接写在Task的`ReceiveExecute`里，让Task自己决定返回Success还是Failure，导致Task臃肿且无法复用。正确做法是将条件检查抽离到Decorator，Task只负责执行单一动作并汇报结果，Decorator负责门控。

**误区二：将Service当作每帧执行的Update使用**。由于Service有Interval间隔，若将需要逐帧精确响应的逻辑（如实时瞄准计算）放入Service，会因时间延迟产生明显卡顿感。帧级别更新应当放在Actor的`Tick`事件或专用的AIController的`Tick`中，行为树Service仅适合低频的状态刷新。

**误区三：忽视Decorator的Observer Abort设置**。不设置Observer Abort的行为树会导致AI对环境变化的响应严重滞后——NPC发现目标后必须等当前Task执行完毕才能切换到追击逻辑。将关键感知Decorator的Observer Abort设为`Lower Priority`，是确保AI"反应灵敏"的必要配置，而非可选项。

## 知识关联

行为树在Unreal Engine中以Blueprint系统为直接入口：Decorator、Service、Task三类节点均可通过创建继承自`BTDecorator`、`BTService`、`BTTaskNode`的Blueprint类来自定义实现，Blueprint的变量系统和事件图表构成了这三类节点逻辑的编写环境。Blackboard的键类型（Object、Vector、Bool、Float等）与Blueprint的变量类型直接对应，理解Blueprint引用类型与值类型的区别，有助于正确选择Blackboard键类型——将Actor引用存为Object键，将位置存为Vector键。

行为树进一步衔接Unreal Engine的Environment Query System（EQS，环境查询系统）：EQS可作为Task节点的执行内容，在运行时生成地图上的候选点并评分，将最优结果写回Blackboard供后续节点使用，从而实现"找掩体"、"选择迂回路径"等空间感知行为。