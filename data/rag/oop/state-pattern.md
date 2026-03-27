---
id: "state-pattern"
concept: "状态模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["state", "fsm", "design-pattern"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 状态模式

## 概述

状态模式（State Pattern）是GoF（Gang of Four）在1994年《设计模式：可复用面向对象软件的基础》中定义的行为型设计模式，其核心意图是：**允许对象在其内部状态发生改变时改变自身的行为，使对象看起来像是修改了它所属的类**。从结构上看，状态模式将有限状态机（Finite State Machine, FSM）的概念翻译成面向对象语言中的类与对象关系。

该模式诞生于解决"巨型条件分支"问题的需求。当一个对象（如AI角色、网络连接、订单流程）需要根据不同状态执行截然不同的行为时，朴素写法会在方法体内堆积大量 `if-else` 或 `switch-case` 语句。随着状态数量增长，这类代码的圈复杂度呈平方级增长，维护成本极高。状态模式通过将每个状态封装为独立类来解决这一问题。

在AI工程领域，状态模式广泛用于NPC行为树的底层状态机实现、对话系统的会话状态管理，以及强化学习环境中的环境状态建模。与策略模式相比，状态模式中的状态对象**主动驱动状态转移**，而策略模式的策略对象不知道彼此存在。

---

## 核心原理

### 三角色结构

状态模式由三个核心角色构成：

- **Context（上下文）**：持有当前状态对象的引用，对外暴露业务方法，并提供 `setState(State s)` 切换状态的接口。Context本身不包含状态相关的条件逻辑。
- **State（抽象状态）**：声明所有具体状态共同实现的接口方法，如 `handle(Context ctx)`。
- **ConcreteState（具体状态）**：每个子类封装一种状态下的完整行为，并在适当时机调用 `ctx.setState(new OtherState())` 触发转移。

最小实现仅需这三类，但状态机中的**转移逻辑既可放在ConcreteState内部，也可放在Context中**，这一设计决策影响状态的耦合度。

### 状态转移的两种实现方式

**方式一：状态自管理转移（State-driven）**
每个ConcreteState在 `handle()` 中根据输入判断是否切换：
```python
class IdleState:
    def handle(self, ctx, event):
        if event == "ENEMY_DETECTED":
            ctx.set_state(ChaseState())  # 主动触发转移
        else:
            ctx.agent.stay_idle()
```
这种方式使每个状态类内聚，但状态间存在互相引用，适合状态数量≤10的场景。

**方式二：转移表驱动（Table-driven）**
Context维护一张字典 `{(当前状态, 事件): 目标状态}`，状态类本身只负责行为，不负责转移。这在AI工程的配置化场景中更常用，可在运行时热修改转移规则。

### 与策略模式的结构差异

状态模式和策略模式的UML类图几乎相同，均有Context持有一个可替换的接口引用。关键区别在于**语义与主动权**：策略模式由外部客户端选择并注入策略，Context不知道策略切换时机；状态模式中，Context或State对象自身知道何时发生状态转移，且转移通常由**触发事件**（如输入、时间、条件检测）驱动，而非客户端调用。换句话说，状态模式实现的是FSM中 `δ(q, σ) = q'`（当前状态 `q`，输入符号 `σ`，产生新状态 `q'`）这一转移函数。

---

## 实际应用

### AI对话系统中的会话状态机

在任务型对话系统中，一次会话经历 `Greeting → SlotFilling → Confirmation → Execution → Farewell` 五个状态。使用状态模式，每个状态类封装该轮次的意图识别逻辑、槽位填充校验和提示语生成。当所有必填槽位填满时，`SlotFillingState` 调用 `ctx.set_state(ConfirmationState())`，此后用户输入由 `ConfirmationState` 完全接管，无需任何全局条件判断。这比在单一 `Chatbot.respond()` 方法中维护十几个布尔标志要清晰得多。

### 游戏NPC的行为状态机

Unity游戏开发中，NPC敌人通常有 `Patrol → Alert → Chase → Attack → Dead` 状态链。用状态模式实现时，`ChaseState.update()` 每帧检测距离：距离 < 2.0m 则切换到 `AttackState`，距离 > 15.0m 则返回 `PatrolState`，HP归零则切换 `DeadState`。每个状态的 `enter()` 和 `exit()` 方法分别处理动画过渡，使动画逻辑与行为逻辑各自内聚。

### 网络连接对象

TCP连接对象的状态模式实现是教科书级案例：`CLOSED → LISTEN → SYN_SENT → ESTABLISHED → FIN_WAIT_1 → TIME_WAIT → CLOSED`。每个状态类处理相应控制报文（SYN、ACK、FIN）的响应，`ESTABLISHED` 状态处理数据收发，其他状态则拒绝数据传输请求并返回相应错误码，无需在 `Connection.send()` 中写 `if self.state == "ESTABLISHED": ...`。

---

## 常见误区

### 误区一：把状态模式当策略模式用，忘记状态转移

初学者常将所有状态封装为类，却让客户端代码手动调用 `ctx.setState(new XXXState())`，等同于把状态模式退化成了策略模式。状态模式的精髓在于**状态转移逻辑内嵌**：系统根据事件自动驱动状态迁移，外部调用者只需调用 `ctx.handle(event)`，不关心当前状态是什么。如果调用方需要判断当前状态才能决定下一步操作，说明封装不彻底。

### 误区二：为两个状态创建状态模式

状态模式的引入成本包括：至少3个新类（抽象State + N个ConcreteState）、Context中的状态引用管理，以及状态对象的生命周期设计（单例复用 vs. 每次new）。对于只有2个互斥状态（如开/关）且转移条件简单的对象，一个布尔字段配合简单条件判断可读性反而更高。状态模式适合**状态数量≥3且每个状态行为差异显著**的场景。

### 误区三：状态对象持有大量Context数据

具体状态类为实现行为，有时会直接持有Context的大量业务字段引用，甚至修改Context私有属性。正确做法是Context仅向State暴露必要的接口（如 `ctx.get_input()`、`ctx.set_state()`、`ctx.get_agent()`），State通过这些接口操作Context，保持双向依赖的边界清晰。否则State类与Context高度耦合，违背了封装状态的初衷。

---

## 知识关联

**前置基础——设计模式概述**：理解GoF模式的三大分类（创建型、结构型、行为型）有助于定位状态模式属于行为型，关注的是对象间的职责分配与通信协议，而非对象的创建或组合方式。

**前置基础——策略模式**：策略模式与状态模式共享"将行为封装为对象"的技术手段，但策略模式中各策略相互独立、无状态转移，是理解状态模式中"状态自驱转移"特性的对比参照。掌握策略模式后，学习状态模式的关键跨越就是理解 `setState()` 被谁调用、在何时调用。

**延伸方向——有限状态机框架**：工业级AI行为系统（如行为树 Behavior Tree）在底层往往结合了状态模式与组合模式。Unity的Animator状态机、游戏AI框架Godot的AnimationStateMachine，以及Python库 `transitions`（支持HSM层次状态机）都是状态模式在FSM框架层面的扩展实现，适合在掌握基础状态模式之后深入研究。