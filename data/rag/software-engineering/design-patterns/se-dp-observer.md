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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 观察者模式

## 概述

观察者模式（Observer Pattern）是一种行为型设计模式，定义了对象之间的**一对多依赖关系**：当一个对象（Subject，主题/被观察者）的状态发生变化时，所有依赖它的对象（Observer，观察者）都会自动收到通知并执行各自的更新逻辑。这种机制使主题与观察者之间实现了松耦合——主题不需要知道观察者的具体类型，只需持有一个观察者接口的引用列表。

该模式最早由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归纳，编号为第293页的经典模式之一。其灵感来源于MVC（Model-View-Controller）架构中Model与View之间的通知机制：当数据模型变更时，多个视图需要同步刷新，正是观察者模式解决了这一场景中的耦合问题。

观察者模式的核心价值在于**事件驱动解耦**：发布者（Subject）完全不依赖订阅者（Observer）的实现细节，新增或移除观察者无需修改主题代码，符合开闭原则。这使得它成为GUI事件系统、消息队列、实时数据推送等场景的首选结构。

---

## 核心原理

### 角色组成与接口定义

观察者模式包含4个角色：

- **Subject（抽象主题）**：持有观察者列表，提供 `attach(Observer)`、`detach(Observer)`、`notify()` 三个方法。
- **ConcreteSubject（具体主题）**：存储实际状态，在状态改变时调用 `notify()`。
- **Observer（抽象观察者）**：声明 `update()` 接口，所有具体观察者必须实现此方法。
- **ConcreteObserver（具体观察者）**：实现 `update()`，从主题中拉取或接收新状态。

以Java伪代码表达核心调用链：

```java
interface Observer { void update(String state); }

class ConcreteSubject {
    private List<Observer> observers = new ArrayList<>();
    private String state;

    public void attach(Observer o) { observers.add(o); }
    public void setState(String s) {
        this.state = s;
        notify(); // 状态变更 → 触发通知
    }
    private void notify() {
        for (Observer o : observers) o.update(state);
    }
}
```

### 推模型与拉模型的区别

观察者模式有两种数据传递方式，选择不同会影响耦合程度：

- **推模型（Push）**：`notify()` 调用时将变更数据作为参数直接传入 `update(data)`。观察者无需持有主题引用，但若不同观察者需要不同数据，会导致 `update` 签名臃肿。
- **拉模型（Pull）**：`update()` 只传递主题引用 `update(Subject s)`，观察者主动调用 `s.getState()` 获取所需数据。耦合略高，但观察者可按需取用。

Java标准库中已废弃的 `java.util.Observable` 类采用的是推拉混合模式，`notifyObservers(Object arg)` 中 `arg` 可为null（拉）或具体数据（推）。

### 通知顺序与一致性问题

`notify()` 默认按 `attach()` 注册顺序依次调用各观察者的 `update()`，这意味着：若观察者A的 `update()` 内部再次修改了主题状态，会在观察者B收到第一次通知之前触发第二次 `notify()`，造成**级联通知（Cascading Update）**问题。GoF书中明确指出这是观察者模式已知的缺陷，建议在 `ConcreteSubject` 中设置"正在通知"标志位来防止重入。

---

## 实际应用

**前端事件系统**：浏览器DOM事件本质上是观察者模式。`element.addEventListener('click', handler)` 等价于 `attach(observer)`，`element.removeEventListener` 等价于 `detach`。一个按钮（Subject）可以注册多个点击处理函数（ConcreteObserver），互不干扰。

**电子表格联动**：Excel中当单元格A1的数值变更时，所有引用了A1的公式单元格（如B1=A1*2，C1=SUM(A1:A5)）自动重新计算。每个公式单元格是观察者，A1是被观察的Subject，这是观察者模式在数据流中最直观的体现。

**Vue.js响应式系统**：Vue 2.x使用 `Object.defineProperty` 劫持数据属性的setter，在setter内部调用 `dep.notify()`（dep即依赖收集器，充当Subject），通知所有订阅该属性的Watcher（充当Observer）触发重新渲染。Vue 3.x改用 `Proxy` 实现相同结构，核心仍是观察者模式。

**股票行情推送**：服务器端维护一个股票价格Subject，当某只股票报价更新时，同时通知移动端App、网页图表、风控系统等多个观察者，各自执行不同的业务逻辑（显示、报警、记录），主题无需关心下游有几个消费者。

---

## 常见误区

**误区一：将观察者模式与发布-订阅模式视为完全相同**

观察者模式中，Subject直接持有Observer的引用列表，两者存在直接依赖；而发布-订阅（Pub/Sub）模式在二者之间引入了**消息代理（Event Bus / Message Broker）**，发布者与订阅者互不知晓对方的存在。Redis的Pub/Sub、RabbitMQ属于发布-订阅，而非严格意义上的观察者模式。两者都实现了解耦，但解耦的程度和适用规模不同。

**误区二：认为移除观察者是可选操作**

在长生命周期对象中，若Subject生命周期长于Observer（如全局事件总线 vs 页面组件），忘记调用 `detach()` 会导致Observer无法被垃圾回收，形成**内存泄漏**。Android开发中 `BroadcastReceiver` 未在 `onDestroy()` 中 `unregisterReceiver` 是此类泄漏的典型案例。`detach()` 不是辅助功能，而是观察者模式资源管理的必要环节。

**误区三：Subject通知越及时越好**

频繁的细粒度通知会引发性能问题。若一次业务操作涉及Subject的10次属性变更，每次变更都触发 `notify()` 会导致观察者执行10次完整更新。正确做法是引入**批量通知机制**：暂停通知 → 批量修改状态 → 恢复并触发一次 `notify()`，Vue的异步更新队列（nextTick机制）正是为此设计。

---

## 知识关联

**与组合模式的关系**：组合模式解决"对象树的统一操作"问题，当树中某节点状态需要向父节点或兄弟节点传播时，常与观察者模式配合——父节点作为Observer监听子节点Subject的变化，实现树形结构中的事件冒泡。

**通往中介者模式**：当系统中观察者之间产生相互依赖（A观察B、B观察C、C又观察A），形成复杂网状通知链时，观察者模式的维护成本急剧上升。此时引入中介者模式，将所有通信逻辑集中到中介者对象，是对过度使用观察者模式的重构方向。

**通往策略模式**：观察者模式解决"谁被通知"的问题，策略模式解决"如何处理通知"的问题。在实际系统中，ConcreteObserver的 `update()` 内部处理逻辑常被进一步抽取为策略，使同一类观察者可以在运行时切换响应行为，两种模式形成自然的组合使用场景。