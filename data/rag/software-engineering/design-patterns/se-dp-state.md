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
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 状态模式

## 概述

状态模式（State Pattern）是一种行为型设计模式，允许对象在其内部状态改变时改变它的行为，使对象看起来像是修改了它所属的类。其本质是将有限状态机（Finite State Machine，FSM）的思想翻译成面向对象语言，把每一个具体状态封装成独立的类，而不是用大量的 `if-else` 或 `switch-case` 语句来区分状态分支。

状态模式由 Gang of Four（GoF）在 1994 年出版的《设计模式：可复用面向对象软件的基础》中正式定义。其灵感直接来源于自动机理论中的有限状态机模型：系统在任意时刻只处于有限个状态之一，当特定事件发生时，系统根据当前状态转移到另一个状态，并执行对应的动作。

状态模式解决的核心痛点是"状态爆炸"问题。当一个类的行为依赖于超过 3 个以上的内部状态时，用条件分支维护代码会导致方法体急剧膨胀、状态转移逻辑散落各处且极难测试。状态模式通过将每种状态的行为集中到一个类中，使新增状态只需新增一个类，而无需修改现有代码。

---

## 核心原理

### 参与者结构

状态模式包含三类参与者：

- **Context（上下文）**：持有一个指向当前 `State` 对象的引用，并将所有与状态相关的请求委托给该对象处理。Context 是客户端唯一直接交互的类。
- **State（抽象状态接口）**：声明所有具体状态必须实现的方法，通常与 Context 提供给外部的操作一一对应。
- **ConcreteState（具体状态类）**：实现 State 接口，在方法中编写该状态下的具体行为，并在适当时机通过 `context.setState(new OtherState())` 触发状态转移。

### 状态转移的两种策略

状态转移逻辑可以放在两个地方：

1. **ConcreteState 内部主动转移**：每个具体状态类在执行完动作后，自行决定下一个状态并调用 `context.setState()`。这种方式使状态类之间产生耦合，但状态转移规则清晰内聚。
2. **Context 统一管理转移**：Context 在调用委托方法后，根据返回值或预设规则切换状态。这种方式减少状态类之间的相互依赖，但转移逻辑集中在 Context 中可能变得复杂。

实际工程中，第 1 种策略更常见于状态数量多、转移规则复杂的场景；第 2 种适用于 Context 需要严格控制转移条件的场景。

### 与策略模式的结构差异

状态模式与策略模式（Strategy Pattern）的类图几乎相同——都是 Context 持有一个接口引用并动态替换具体实现。但两者存在本质区别：

- **策略模式**中，具体策略之间互不知晓，策略的切换由客户端主动完成，Context 本身没有"当前状态"的语义。
- **状态模式**中，具体状态类通常相互知晓（或至少知道 Context），状态切换由状态自身或 Context 根据业务规则自动触发，客户端无需感知。

用一个公式描述状态转移：若当前状态为 $S_i$，触发事件为 $e$，则下一状态 $S_j = \delta(S_i, e)$，其中 $\delta$ 是转移函数。状态模式将 $\delta$ 的每一行（即每个 $S_i$ 对应的所有事件处理）内聚到 `ConcreteState_i` 类中。

---

## 实际应用

### 自动售货机

自动售货机是状态模式的经典教学案例，其状态机包含 4 个状态：`NoQuarterState`（未投币）、`HasQuarterState`（已投币）、`SoldState`（正在出货）、`SoldOutState`（售罄）。

当用户投入硬币时，`NoQuarterState.insertQuarter()` 方法执行，并将 Context 切换到 `HasQuarterState`；若在 `SoldOutState` 下投币，则直接打印"已售罄，退还硬币"并保持当前状态不变。每种状态对同一操作（如 `insertQuarter`、`turnCrank`、`dispense`）给出完全不同的响应，若用条件分支实现，一个拥有 4 个状态和 4 个操作的机器将产生最多 16 个条件分支，维护成本极高。

### TCP 连接管理

TCP 协议的连接生命周期可用状态模式实现：`TCPClosed`、`TCPListen`、`TCPEstablished` 等状态分别实现 `open()`、`close()`、`acknowledge()` 方法。`TCPEstablished` 状态下调用 `close()` 会触发四次挥手并转移到 `TCPClosed`；而在 `TCPClosed` 状态下调用 `close()` 则是无操作或抛出异常。这与 Linux 内核网络栈中 TCP 状态机的实际实现逻辑高度一致。

### 游戏角色状态

RPG 游戏中角色的 `Standing`（站立）、`Running`（奔跑）、`Jumping`（跳跃）、`Ducking`（蹲下）状态各自实现 `handleInput(input)` 和 `update()` 方法。`JumpingState` 在 `update()` 中检测角色是否落地，若落地则自动切换回 `StandingState`，而无需外部代码轮询状态条件。

---

## 常见误区

### 误区一：状态数量少时也应使用状态模式

状态模式引入了多个新类，增加了代码文件数量和类间依赖。当一个对象只有 2 个状态（如开/关），且未来几乎不会扩展时，简单的布尔字段加条件判断的成本远低于状态模式。GoF 建议在状态数量≥3 且状态行为差异明显时才考虑引入该模式。

### 误区二：Context 不应该暴露 setState 方法

很多初学者将 `setState()` 设为 `private`，导致 ConcreteState 无法触发状态转移。正确做法是将 `setState()` 设为包级别访问（Java 中的 package-private）或通过友元类（C++ 中的 `friend`）限制访问范围，使具体状态类可调用但外部客户端不可直接操控。

### 误区三：状态对象必须是无状态的

实际上，具体状态类可以持有自己的数据字段。例如 `JumpingState` 可以持有 `jumpStartY` 字段记录起跳高度，用于计算落地时机。但需注意，若 Context 的多个实例共享同一个状态对象（享元优化），则状态类必须是无状态的，否则会引发并发或数据混乱问题。

---

## 知识关联

**前置概念——策略模式**：学习状态模式之前理解策略模式，有助于快速掌握"将行为封装进对象并动态替换"这一手法。两者在结构上相同，但状态模式额外引入了状态转移逻辑和 Context 自动切换机制，这是策略模式中不存在的概念。

**后续概念——状态模式在游戏中的应用**：游戏开发场景会将状态模式进一步扩展为**分层状态机**（Hierarchical State Machine）和**并发状态机**。例如角色可同时处于"装备状态"和"移动状态"两个独立状态维度，每个维度各自维护一套 State 对象，这是对基础状态模式的直接延伸。

**横向关联——备忘录模式**：若需要记录状态转移历史并支持"撤销"操作，可将备忘录模式（Memento Pattern）与状态模式结合使用，将每次状态切换前的 Context 快照存入历史栈，实现可回溯的状态机。
