---
id: "observer-pattern"
concept: "观察者模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["设计模式"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
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

# 观察者模式

## 概述

观察者模式（Observer Pattern）是一种行为型设计模式，定义了对象间的一对多依赖关系：当一个被观察对象（Subject/Observable）的状态发生变化时，所有依赖它的观察者对象（Observer）都会自动收到通知并更新。这种关系的核心是**松耦合**——Subject只知道观察者实现了特定接口，而不需要了解其具体类型。

该模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类和命名，编号为行为模式第5项。它的思想来源于Smalltalk语言中的MVC架构，其中Model与View之间的通知机制正是观察者模式的早期实践。在事件驱动系统和响应式编程兴起之前，观察者模式是实现"数据变化自动传播"的主流手段。

在AI工程场景中，观察者模式具有具体的工程价值：训练过程监控（TensorBoard的回调机制）、模型推理日志收集、多个下游服务订阅同一特征流，这些都依赖观察者模式的通知机制。理解它不仅是OOP基础，更是理解React的`useEffect`依赖数组、Redux store订阅、以及RxJS响应式流的前提。

---

## 核心原理

### 标准接口定义

观察者模式由两个关键接口构成：

```python
# Subject 接口
class Observable:
    def attach(self, observer: 'Observer') -> None: ...
    def detach(self, observer: 'Observer') -> None: ...
    def notify(self) -> None: ...

# Observer 接口
class Observer:
    def update(self, subject: 'Observable') -> None: ...
```

`attach`和`detach`负责管理观察者列表，`notify`在状态变更时遍历列表并调用每个观察者的`update`方法。这三个方法是GoF定义的最小接口集合，任何扩展（如传递具体变更数据）都是在此基础上的变体。

### 推模型与拉模型的区别

观察者模式有两种数据传递策略，工程上的选择直接影响耦合度：

- **推模型（Push）**：Subject在调用`update`时主动将变更数据作为参数传入。例如`observer.update(new_value=0.92)`。优点是Observer无需持有Subject引用，缺点是Subject必须预知Observer需要哪些数据，易导致接口膨胀。

- **拉模型（Pull）**：Subject只传递自身引用`observer.update(self)`，Observer主动调用`subject.get_state()`获取所需数据。GoF原书推荐拉模型，因为它将"需要什么数据"的决策权交给Observer，Subject变更接口时各Observer可独立适配。

在AI训练监控中，推模型适合传递单一指标（如当前epoch的loss值），拉模型适合Observer需要从训练对象中读取多个属性（loss、accuracy、学习率）的场景。

### 具体实现与内存管理

一个常见的工程陷阱是**强引用导致的内存泄漏**。Subject持有所有Observer的强引用，若Observer对象应被销毁但未调用`detach`，Subject的列表会持续持有该引用，阻止垃圾回收。Python中的解决方案是使用`weakref.WeakSet`存储观察者列表：

```python
import weakref

class ConcreteSubject:
    def __init__(self):
        self._observers = weakref.WeakSet()
        self._state = None

    def attach(self, observer):
        self._observers.add(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)
```

使用`WeakSet`后，当Observer对象不再被其他地方引用时，它会自动从集合中消失，无需手动调用`detach`。

---

## 实际应用

### Keras回调机制

TensorFlow/Keras中的`ModelCheckpoint`、`EarlyStopping`、`TensorBoard`均是观察者模式的直接实现。`Model`对象是Subject，各种`Callback`是Observer。训练循环在`on_epoch_end`时刻调用`callback_list.on_epoch_end(epoch, logs)`，即执行`notify`。`logs`字典（包含`loss`、`val_accuracy`等）采用推模型传递数据。你可以在不修改`Model`源码的前提下，通过继承`keras.callbacks.Callback`并重写`on_epoch_end`添加任意监控逻辑。

### React状态订阅

React的`useState`与Redux的`store.subscribe()`体现了不同粒度的观察者机制。Redux的`store.subscribe(listener)`直接暴露Subject接口，`listener`是Observer，每次dispatch触发state变更时所有listener被调用——这是严格的观察者模式。React的`useEffect(() => { ... }, [dep])`中的依赖数组则是声明式观察者注册：框架在内部追踪`dep`的变化，自动决定何时重新执行effect回调，本质上是框架代管了`attach/detach`生命周期。

### 特征流多播

在实时推理系统中，一个特征提取服务（Subject）的输出需要同时送往风控模型、推荐模型、日志系统三个消费者（Observer）。观察者模式允许特征服务在不修改自身代码的情况下，动态增减下游订阅者，实现系统的横向扩展。

---

## 常见误区

**误区一：认为观察者模式与发布-订阅模式完全相同。**  
两者的根本区别在于是否存在**消息中间层（Broker/EventBus）**。纯观察者模式中Subject直接持有Observer引用并调用其方法，Subject与Observer之间存在直接依赖。发布-订阅模式引入了事件总线，发布者和订阅者互不知晓对方的存在，通过字符串事件名（如`"model.trained"`）解耦。Kafka、Redis Pub/Sub是发布-订阅；Python内置的`__setattr__`触发回调是观察者模式。混淆二者会导致在需要跨进程解耦时错误地选用直接观察者，或在简单场景中引入不必要的事件总线开销。

**误区二：在`notify`中直接修改观察者列表。**  
若某个Observer在其`update`方法中调用`subject.detach(self)`，而`notify`正在遍历同一列表，Python的列表在迭代时被修改会抛出`RuntimeError`，或在某些实现中产生跳过通知的静默错误。正确做法是在`notify`中先复制一份列表快照：`for observer in list(self._observers): observer.update(self)`，确保迭代目标在遍历期间不变。

**误区三：将观察者模式用于高频同步通知场景而不设置节流。**  
若Subject状态每秒变更1000次（如实时传感器数据），每次变更都同步调用所有Observer的`update`，会导致主线程阻塞。正确做法是在Subject内部引入节流（throttle）或批量通知策略，或将`notify`改为异步发送（Python中使用`asyncio`事件循环），而不是让每个Observer自己处理防抖。

---

## 知识关联

**与设计模式概述的关系**：设计模式概述中介绍的"针对接口编程而非实现"原则在观察者模式中体现得最为具体——Subject持有的是`Observer`接口类型而非任何具体Observer类，这使得`ConcreteObserverA`和`ConcreteObserverB`可以互换挂载，运行时多态在此处有明确的工程用途。GoF的23种模式中，观察者与策略模式同属行为型，但策略解决"算法替换"，观察者解决"状态传播"，两者的职责边界在AI系统中经常需要明确区分。

**与React状态管理的关系**：React的单向数据流中，`useState`的setter函数触发组件重渲染，本质上是React框架内部的观察者通知。理解了观察者模式的`attach/notify/update`三步骤，就能准确解释为什么`useEffect`的依赖数组遗漏某个变量会导致stale closure问题——Observer注册时捕获的是旧引用，而Subject已经更新了状态，二者不同步。Redux的`connect()`高阶组件则在组件挂载时执行`store.subscribe()`、卸载时执行`unsubscribe()`，完整实现了观察者生命周期管理。