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
quality_tier: "pending-rescore"
quality_score: 43.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 观察者模式

## 概述

观察者模式（Observer Pattern）是一种行为型设计模式，定义了对象间的一种**一对多依赖关系**：当一个对象（被观察者/Subject）的状态发生改变时，所有依赖它的对象（观察者/Observer）都会自动收到通知并更新。这种关系在代码层面通过维护一个观察者列表，配合 `subscribe()`、`unsubscribe()`、`notify()` 三个核心方法来实现。

该模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式定义，归入行为型模式类别，与策略模式、命令模式并列。其思想根源来自事件驱动编程——被观察者无需知道谁在监听它，只需在状态变化时广播通知，这种**松耦合**特性使它成为AI工程中模型训练状态监控、数据流处理等场景的重要工具。

在AI工程上下文中，观察者模式特别适合处理**异步、多输出**的场景：例如一个模型训练进程作为Subject，同时向日志记录器、早停控制器、TensorBoard可视化器三个Observer推送每个epoch的指标，三者互不干涉、可独立增减，这是轮询或直接调用所无法优雅实现的。

---

## 核心原理

### 参与角色与接口定义

观察者模式由四个角色构成：

- **Subject（被观察者接口）**：声明 `attach(observer)`、`detach(observer)`、`notify()` 方法
- **ConcreteSubject（具体被观察者）**：持有 `_observers: List[Observer]` 列表，保存真实状态，状态变化时调用 `notify()`
- **Observer（观察者接口）**：声明 `update(subject)` 方法，是所有具体观察者必须实现的契约
- **ConcreteObserver（具体观察者）**：实现 `update()` 方法，在被通知时执行自己的业务逻辑

Python示例骨架如下：

```python
from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self, subject: "Subject") -> None:
        pass

class Subject(ABC):
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
```

### 推模型（Push）与拉模型（Pull）

观察者模式存在两种通知策略，选择错误会直接影响系统性能：

- **推模型（Push Model）**：Subject 在调用 `notify()` 时将具体数据作为参数推送给 Observer，如 `observer.update(loss=0.23, epoch=5)`。优点是Observer无需反查Subject；缺点是Subject必须预知Observer需要哪些数据，耦合度相对较高。
- **拉模型（Pull Model）**：Subject 只通知Observer"我变了"，Observer主动调用 `subject.get_state()` 拉取感兴趣的数据。GoF原著更推荐拉模型，因为它将数据获取的主动权交给Observer，Subject无需假设下游需求。

在AI训练监控中，若TensorBoard观察者只关心loss，而早停观察者同时需要loss和validation accuracy，拉模型可避免Subject广播冗余数据。

### 线程安全与通知顺序

当Subject运行在多线程环境（如异步数据加载+主训练线程）时，`_observers` 列表的并发修改会引发竞争条件。标准做法是在 `attach/detach/notify` 方法中使用 `threading.Lock()`，或在通知前先复制一份观察者列表快照：

```python
def notify(self) -> None:
    observers_snapshot = self._observers[:]  # 快照，避免并发修改
    for observer in observers_snapshot:
        observer.update(self)
```

通知顺序依赖 `_observers` 列表的插入顺序，不应在业务逻辑中假设固定顺序——若早停Observer必须在日志Observer之前执行，应通过优先级队列或显式排序保证，而非依赖注册顺序。

---

## 实际应用

### AI模型训练监控

在PyTorch训练循环中，可将 `TrainingSession` 设计为Subject，在每个epoch结束后调用 `notify()`。三个具体Observer分别负责：**LossLogger**（写入CSV文件）、**EarlyStoppingObserver**（连续3个epoch验证集loss不降则终止）、**CheckpointSaver**（每5个epoch保存一次模型权重）。新增Slack通知Observer时，只需实现 `update()` 方法并调用 `session.attach(slack_observer)`，训练代码零修改。

### React状态管理中的观察者思想

React的 `useState` 钩子背后的Fiber架构实现了类似观察者模式的订阅机制：组件通过 `useSelector` 订阅Redux Store（Subject），当 dispatch 导致 Store 状态变化时，只有订阅了相关状态切片的组件（Observer）会重新渲染。Redux的 `store.subscribe(listener)` 和 `store.dispatch()` 正是 `attach()` 和 `notify()` 的直接映射。与经典GoF实现的区别在于，Redux Store通知时不传递具体变化内容，完全采用拉模型——组件自行通过 `getState()` 获取新状态。

### 事件总线（EventBus）模式

EventBus是观察者模式的一种变体，引入了**事件类型（topic）**维度。Subject不再直接维护Observer列表，而是通过一个中介字典 `{event_type: [observers]}` 管理订阅关系。AI推理服务中，模型加载完成、推理超时、显存不足等事件可分别注册不同的Observer，实现比单一Subject更细粒度的通知控制。

---

## 常见误区

### 误区一：观察者模式与发布-订阅模式等价

这是最普遍的混淆。**观察者模式**中，Subject直接持有Observer的引用，二者存在直接依赖——Subject知道Observer的存在。而**发布-订阅模式**（Pub/Sub）在二者之间插入了一个**消息代理（Message Broker）**，发布者和订阅者完全不知道对方的存在，通过topic解耦。Kafka、RabbitMQ实现的是Pub/Sub，Python标准库中没有内置发布-订阅中间件，而Django的 `signals` 框架则是在语言层面实现的Pub/Sub变体。在同一进程内的状态同步用观察者模式，跨服务、跨进程的事件传递用Pub/Sub。

### 误区二：Observer的 `update()` 方法应执行耗时操作

`notify()` 是同步遍历Observer列表并逐一调用 `update()` 的，若某个Observer的 `update()` 执行了模型推理或磁盘写入，会阻塞Subject的通知流程，导致后续Observer延迟接收通知。正确做法是在 `update()` 内仅记录状态变化，将耗时任务提交至线程池或消息队列异步执行。例如CheckpointSaver的 `update()` 应只设置一个 `self._should_save = True` 标志，由后台线程负责实际的 `torch.save()` 调用。

### 误区三：无限制地添加观察者不会有性能问题

`notify()` 的时间复杂度是 **O(n)**，n为观察者数量。在高频触发场景（如每个training step都notify，每秒可能触发数百次）下，若观察者累积过多且未及时 `detach`，会产生可观的性能开销。此外，若Observer持有Subject的反向引用而未正确调用 `detach()`，会形成循环引用导致Python垃圾回收器无法释放内存——这在长时间运行的训练任务中是真实存在的内存泄漏风险。

---

## 知识关联

**前置概念衔接**：从《设计模式概述》中学到的"面向接口编程"原则在此处得到具体体现——Observer接口（抽象类）是Subject与具体Observer之间的唯一契约，Subject代码中出现的类型始终是 `Observer` 抽象类而非任何具体实现。从**React状态管理**的学习中，你已经接触过 `store.subscribe()` 这一API，现在可以理解它本质上是Subject的 `attach()` 方法，`useSelector` 的依赖追踪是对拉模型的工程化实现。

**横向关联**：观察者模式与**中介者模式（Mediator）**形成对比——当多个Subject之间需要互相通知时，直接使用观察者模式会形成网状依赖，此时引入中介者将通信拓扑从网状简化为星状。在AI工程的模块协调场景（如数据预处理、特征工程、模型训练三个模块互相感知状态）中，两种模式的选择取决于耦合度与灵活性之间的权衡。
