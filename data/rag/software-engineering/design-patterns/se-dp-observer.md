---
id: "se-dp-observer"
concept: "观察者模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: true
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.5
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 观察者模式

## 概述

观察者模式（Observer Pattern）是一种行为型设计模式，定义了对象之间的**一对多依赖关系**：当一个对象（被观察者/Subject）的状态发生改变时，所有依赖它的对象（观察者/Observer）都会自动收到通知并更新。这种机制使得被观察者无需知道有多少观察者存在，也无需关心观察者的具体类型。

观察者模式最早被系统化记录于1994年GoF（Gang of Four）出版的《设计模式：可复用面向对象软件的基础》一书中，编号为第5个行为型模式。它的思想源于MVC（Model-View-Controller）架构中Model通知View更新的机制，该机制在1980年代的Smalltalk语言环境中已被广泛实践。

观察者模式直接解决了软件中的**事件驱动解耦**问题：如果不使用此模式，数据源每次状态变化时必须手动调用每个依赖方的更新方法，导致数据源与展示层、业务逻辑层之间产生强耦合。以股票行情系统为例，行情数据源不应该知道到底有哪些图表、报警模块、交易策略在监听它——观察者模式正是为此而生。

---

## 核心原理

### 参与角色与接口结构

观察者模式包含四个核心角色：

- **Subject（抽象被观察者）**：持有观察者列表，提供 `attach(Observer)`、`detach(Observer)`、`notify()` 三个方法
- **ConcreteSubject（具体被观察者）**：存储实际状态（如 `temperature`），在状态变化时调用 `notify()`
- **Observer（抽象观察者）**：声明 `update()` 接口，所有具体观察者必须实现此方法
- **ConcreteObserver（具体观察者）**：实现 `update()` 方法，从 Subject 中拉取或直接接收最新状态

```java
// 推模型示例：Subject主动将数据推送给Observer
public interface Observer {
    void update(float temperature, float humidity);
}
```

### 推模型 vs. 拉模型

观察者模式在通知数据传递上存在两种变体，是理解此模式的关键区分点：

- **推模型（Push）**：Subject 调用 `notify()` 时，直接将变化的数据作为参数传入 `update(data)`。优点是Observer无需持有Subject引用；缺点是Subject必须预判Observer需要哪些数据，若Observer种类增多，方法签名难以维护。
- **拉模型（Pull）**：Subject 调用 `update(this)` 将自身引用传给Observer，由Observer主动调用 `subject.getState()` 拉取所需数据。Java内置的 `java.util.Observable` 类（已在Java 9标记为deprecated）采用的正是拉模型，Observer通过 `Observable` 对象引用按需读取。

### 注册与注销机制

Subject 内部维护一个 `List<Observer>` 容器。`attach()` 将观察者加入列表，`detach()` 将其移除，`notify()` 遍历列表依次调用每个 Observer 的 `update()` 方法。这个遍历顺序通常与注册顺序一致，但**不应依赖通知顺序**来设计业务逻辑，因为不同语言/框架的实现可能不保证顺序。

需要注意的是，若在 `notify()` 遍历过程中某个 Observer 触发了 `detach()` 操作，可能导致 `ConcurrentModificationException`（Java）等并发修改异常，实际实现时需对观察者列表进行防御性拷贝再遍历。

---

## 实际应用

### GUI事件系统

Java Swing 的按钮点击机制是教科书级的观察者模式应用：`JButton` 是 Subject，`ActionListener` 是 Observer 接口，`addActionListener()` 即 `attach()`。每次用户点击按钮，Swing内部调用所有已注册 `ActionListener` 的 `actionPerformed()` 方法，按钮本身完全不关心有多少监听器存在。

### 发布-订阅框架

现代消息队列（如 Redis Pub/Sub、Kafka）将观察者模式扩展为**异步跨进程**版本，称为发布-订阅（Pub/Sub）模式。与经典观察者模式不同的是，Pub/Sub 引入了**消息代理（Broker）**作为中间层，发布者和订阅者彼此完全不知道对方的存在。Kafka 的 Topic 相当于 Subject，Consumer Group 相当于 ConcreteObserver，但二者通过 Broker 解耦，不存在直接引用关系。

### 前端响应式框架

Vue.js 的响应式系统（Vue 3中基于 `Proxy` 实现）本质上是观察者模式：数据对象是 Subject，模板渲染函数和 `computed` 属性是 Observer。当 `data.count` 被修改时，Vue 的依赖追踪系统（Dep类）自动通知所有订阅了 `count` 的 Watcher 执行重新渲染，开发者无需手动调用任何刷新方法。

---

## 常见误区

### 误区一：混淆观察者模式与发布-订阅模式

很多开发者认为这两者完全等价，但存在关键差异：**经典观察者模式中，Subject 持有 Observer 的直接引用**，是同步调用；而发布-订阅模式引入了事件总线（Event Bus）或消息代理作为中间层，发布者与订阅者之间无直接依赖，且通常是异步通信。JavaScript 中常见的 `EventEmitter` 更接近发布-订阅，而非纯粹的GoF观察者模式。

### 误区二：忘记调用 detach() 导致内存泄漏

Subject 的 Observer 列表持有 Observer 的强引用，若 Observer 对象已不再使用但未调用 `detach()`，GC 无法回收该对象，造成内存泄漏。这在 Android 开发中尤为常见：Activity 向某个全局 Subject（如事件总线）注册监听后，若在 `onDestroy()` 中忘记反注册，已销毁的 Activity 实例将永久驻留内存。解决方案包括使用弱引用（`WeakReference<Observer>`）存储观察者列表，或在生命周期结束时强制反注册。

### 误区三：在 update() 中再次触发状态变化

若 ConcreteObserver 的 `update()` 方法内部修改了 Subject 的状态，会导致 Subject 再次调用 `notify()`，进而触发新一轮 `update()`，形成**无限递归调用栈溢出**。GoF 原书特别指出 Subject 可维护一个 `boolean changed` 标志位来防止重复通知，但更稳健的方式是在设计上规定 `update()` 方法不得反向修改被观察的 Subject。

---

## 知识关联

**前置概念**：学习观察者模式需要熟悉《设计模式概述》中的接口与多态概念，因为Observer接口的多态调用是整个模式运作的基础——`notify()` 遍历列表调用 `update()` 时，依赖的正是运行时多态来分派到不同的ConcreteObserver实现。

**后续扩展——中介者模式**：当系统中存在多个 Subject 和多个 Observer 需要相互通知时，直接使用观察者模式会导致复杂的多对多引用网络。中介者模式（Mediator）通过引入一个中央协调对象，将这张网络扁平化为星型结构，可视为观察者模式在复杂多方通信场景下的升级方案。

**后续扩展——游戏中的观察者模式**：游戏开发中的成就系统、AI感知系统等场景对观察者模式提出了性能约束：当帧率要求达到60FPS时，同步遍历数百个Observer的通知开销不可忽视。游戏专用变体会引入事件队列（Event Queue）将通知延迟到帧末批量处理，这是经典观察者模式在实时系统中的关键改造点。
