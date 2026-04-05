---
id: "se-dp-state"
concept: "状态模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 状态模式

## 概述

状态模式（State Pattern）是一种行为型设计模式，它将对象在不同状态下的行为封装成独立的状态类，使对象可以在运行时根据内部状态切换行为，表现得好像改变了自身的类一样。其本质是用面向对象的方式实现**有限状态机（FSM, Finite State Machine）**：将状态机中的每个状态映射为一个具体类，将状态转移逻辑分散到各状态类内部，而非集中在一个充斥 `if-else` 的上下文类中。

状态模式由 GoF（Gang of Four）在 1994 年出版的《设计模式：可复用面向对象软件的基础》中正式命名，编号为行为型模式的第八个。其理论根源可追溯至 1943 年麦卡洛克与皮茨提出的有限自动机模型。状态模式将"状态决定行为"这一直觉转化为可扩展的类结构，彻底消除因状态增多而指数膨胀的条件分支代码。

状态模式在嵌入式控制、游戏角色 AI、网络协议栈、UI 组件生命周期管理中被广泛使用。以 TCP 连接为典型例子：`CLOSED`、`LISTEN`、`ESTABLISHED`、`TIME_WAIT` 等状态在状态模式下分别成为独立类，每个类各自实现 `open()`、`close()`、`acknowledge()` 等方法，上下文对象 `TCPConnection` 只持有当前状态对象的引用，无需关心具体行为如何实现。

---

## 核心原理

### 角色结构与 UML 关系

状态模式包含三个参与者：

- **Context（上下文）**：持有一个 `State` 接口类型的成员变量 `currentState`，将所有与状态相关的请求委托给该对象处理。
- **State（抽象状态接口）**：声明所有具体状态必须实现的方法集合，例如 `handle(context)`。
- **ConcreteState（具体状态类）**：实现 `State` 接口，在 `handle()` 中编写本状态下的具体行为，并可调用 `context.setState(nextState)` 触发状态转移。

上下文与状态之间是**聚合关系**，不是继承关系。状态转移的触发权可以交给 Context，也可以交给 ConcreteState，GoF 明确指出后者更灵活但会引入各状态类之间的依赖。

### 状态转移的实现方式

具体状态类负责驱动转移时，每个 `ConcreteState` 需要知道其他状态类的存在。以自动售货机为例，`HasCoinState`（已投币状态）的 `pressButton()` 方法会创建 `DispensingState` 对象并调用 `context.setState(new DispensingState())`；而 `SoldOutState`（售罄状态）的 `pressButton()` 方法则只打印提示并不改变状态。这种设计使每个状态类仅关注"本状态能做什么、转移到哪里"，单一职责十分清晰。

状态对象可以**共享**（Flyweight 风格）或**按需创建**。若状态对象无实例变量（纯行为），则可使用单例或静态实例共享，降低 GC 压力；若状态需要携带数据（如剩余重试次数），则每次进入状态时创建新实例。

### 与策略模式的结构差异

状态模式与策略模式（Strategy Pattern）的 UML 图几乎相同，二者都通过委托实现行为替换，但语义截然不同：

| 维度 | 状态模式 | 策略模式 |
|------|----------|----------|
| 切换发起者 | 通常由状态类自身或Context根据事件自动切换 | 由客户端代码显式替换算法 |
| 状态类间关系 | 各状态类可能互相引用以完成转移 | 各策略类完全独立，互不感知 |
| 生命周期语义 | 表达"对象所处阶段" | 表达"算法的可替换实现" |

理解这一差异能避免在代码评审中将二者混淆命名。

---

## 实际应用

### 电商订单状态机

一个典型的电商订单拥有状态：`待付款 → 已付款 → 已发货 → 已完成`，以及异常路径 `已取消`。使用状态模式时，`Order` 类作为 Context，持有 `OrderState currentState`。`PendingPaymentState` 的 `pay()` 方法将状态切换为 `PaidState` 并触发库存扣减；`PaidState` 的 `pay()` 方法则抛出 `IllegalStateException`，因为该操作在当前状态无意义。相比之下，若用 `switch(status)` 实现，每新增一个状态就需要在所有方法的 switch 块中添加分支，违反开闭原则。

### 游戏角色 AI 行为切换

Unity 游戏中敌人 AI 常用状态模式：`IdleState`（巡逻）、`ChaseState`（追击）、`AttackState`（攻击）、`FleeState`（逃跑）四个状态类各自实现 `Update(EnemyContext ctx)` 方法。`ChaseState.Update()` 检测到与玩家距离 < 2f 时调用 `ctx.setState(new AttackState())`，检测到血量 < 20% 时调用 `ctx.setState(new FleeState())`。这套结构可直接对接行为树或 Animator，是游戏 AI 开发的标准实践。

### Java 线程状态

Java 的 `Thread` 类底层正是状态机思想：`NEW → RUNNABLE → BLOCKED / WAITING / TIMED_WAITING → TERMINATED`，共 6 种状态定义在 `Thread.State` 枚举中。JVM 内部为不同状态下的调度行为维护了不同的处理逻辑，与状态模式的思想高度吻合。

---

## 常见误区

### 误区一：状态越多越应该用状态模式

状态模式并非状态数量的门槛问题，而是**行为差异化**的问题。若一个对象有 10 个状态，但每个状态下的方法行为完全相同，只是数据不同，那么用枚举 + 数据表驱动更简洁。只有当不同状态下同一方法的实现逻辑差异显著（例如 `SoldOutState.pressButton()` 与 `HasCoinState.pressButton()` 的代码完全不同）时，状态模式才能显著减少条件判断。一般经验是：**同一事件在超过 3 个状态下有不同处理逻辑**时引入状态模式才合算。

### 误区二：状态类之间不应该互相知道

有开发者认为状态类应当完全解耦，实际上 GoF 原文明确指出具体状态类"可以了解其他具体状态类，以便决定下一个状态"。刻意隔离状态类会导致将所有转移逻辑移回 Context，使 Context 重新膨胀为包含大量条件判断的上帝类，违背引入状态模式的初衷。正确做法是允许状态类之间存在依赖，但通过工厂方法或依赖注入管理状态实例的创建，以控制耦合强度。

### 误区三：状态模式等同于有限状态机框架

状态模式是 FSM 的一种面向对象**实现手段**，但完整的 FSM 框架（如 Spring Statemachine、XState）还包含：转移条件守卫（Guard）、进入/退出动作（Entry/Exit Action）、层次化状态（Hierarchical State）、历史状态（History State）等特性。状态模式本身并不内置这些机制，若需要历史状态回退或并发状态，需在模式基础上额外设计，或直接使用专用 FSM 库。

---

## 知识关联

**前置概念**——学习状态模式前，**策略模式**提供了"通过委托替换行为"的基础结构；**命令模式**提供了"将操作封装为对象"的思路，二者合用可将状态转移动作本身包装为命令对象，支持撤销/重做功能（如文本编辑器的 Undo 栈配合状态机）。

**后续概念**——掌握基础状态模式后，**状态模式（游戏）**方向会引入层次状态机（HSM）和并发状态机，处理角色同时具有"移动状态"和"武器状态"的复合场景；**模板方法模式**与状态模式结合时，可在抽象状态基类中定义 `enter()`、`execute()`、`exit()` 三步模板，统一每个具体状态的生命周期钩子，这是游戏引擎和工作流引擎中的常见设计。