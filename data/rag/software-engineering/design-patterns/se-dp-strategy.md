---
id: "se-dp-strategy"
concept: "策略模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 策略模式

## 概述

策略模式（Strategy Pattern）是一种行为型设计模式，其核心思想是将一组可互换的算法分别封装成独立的类，使得这些算法可以在运行时根据需要自由切换，而调用方无需了解算法的具体实现细节。策略模式的正式定义来自1994年出版的《设计模式：可复用面向对象软件的基础》（即"GoF四人帮"著作），书中将其归类为行为型模式，并给出了Context（上下文）、Strategy（策略接口）、ConcreteStrategy（具体策略）三角结构。

策略模式起源于对"条件分支爆炸"问题的解决需求。当一个函数中出现大量`if-else`或`switch-case`来选择不同算法时，每次新增算法都必须修改原有代码，违反了开闭原则（对扩展开放、对修改关闭）。策略模式通过将每个分支提取为一个独立的ConcreteStrategy类，使新增算法只需新建一个类即可完成，无需触碰已有代码。

该模式在排序算法选择、支付方式切换、数据压缩格式选择等场景中极为常见。例如Java标准库中的`java.util.Comparator`接口就是策略模式的直接体现——`Collections.sort(list, comparator)`允许调用方在运行时传入不同的比较策略，而排序逻辑本身无需改动。

---

## 核心原理

### 三角色结构

策略模式由三个固定角色构成：

- **Context（上下文）**：持有一个Strategy接口的引用，负责将客户端的请求委托给当前持有的策略对象执行。Context本身不实现任何算法逻辑。
- **Strategy（策略接口）**：定义所有具体策略必须实现的公共方法，例如`execute(data)`。这是Context与具体算法之间的唯一契约。
- **ConcreteStrategy（具体策略）**：实现Strategy接口，每个类封装一种完整的算法实现，如`BubbleSortStrategy`、`QuickSortStrategy`、`MergeSortStrategy`。

Context类的关键代码结构如下：

```python
class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def set_strategy(self, strategy: Strategy):
        self._strategy = strategy   # 运行时切换入口

    def execute(self, data):
        return self._strategy.algorithm(data)
```

`set_strategy()`方法是运行时切换的核心入口，客户端可在任意时刻调用它替换当前策略，而Context的其他部分完全不受影响。

### 算法封装的边界

每个ConcreteStrategy只负责自己那一种算法的完整逻辑，不应与其他策略有任何耦合。策略对象通常是**无状态**的——即它不存储算法执行过程中的中间结果。这使得同一个策略实例可以被多个Context对象安全共享，从而降低内存开销。若算法确实需要参数，应通过`algorithm(data, params)`方法参数传入，而非存入策略对象的成员变量。

### 与多态的关系

策略模式本质上是对多态机制的一种**有意识的结构化使用**。其区别于普通继承多态的关键在于：策略对象是Context的**组合成员**，而非Context的父类。这体现了"优先使用组合而非继承"的设计原则。组合方式允许在运行时动态替换行为，而继承方式在编译期就已固化了行为。

---

## 实际应用

**电商支付系统**：一个订单结算模块需要支持微信支付、支付宝、银行卡三种方式。将`PaymentStrategy`定义为接口，`WeChatPayStrategy`、`AlipayStrategy`、`BankCardStrategy`各自实现。用户在结算页面选择支付方式时，Context的`set_strategy()`被调用切换策略，结算流程代码无需任何修改。

**游戏角色AI难度切换**：射击游戏中的敌方AI可设置为简单、普通、困难三档，分别对应`EasyAIStrategy`、`NormalAIStrategy`、`HardAIStrategy`。玩家在设置菜单中调整难度时，游戏上下文立即替换策略对象，AI行为在下一帧即刻生效，而游戏主循环代码保持不变。

**文件压缩工具**：支持ZIP、GZIP、BZIP2三种压缩算法的工具类，通过`CompressionStrategy`接口统一暴露`compress(file)`方法。用户根据文件类型或大小需求选择压缩策略，主程序逻辑只调用`context.execute(file)`，与具体压缩算法完全解耦。

**Java标准库实例**：`ThreadPoolExecutor`构造函数中的`RejectedExecutionHandler`参数接受`AbortPolicy`、`CallerRunsPolicy`、`DiscardPolicy`等策略，这是Java原生API中策略模式的教科书级案例，在JDK 1.5版本中正式引入。

---

## 常见误区

**误区一：策略模式与简单工厂的混淆**

初学者常将选择策略的逻辑（"根据条件决定用哪个策略"）也塞入Strategy接口或Context中，退化成了简单工厂模式。策略模式的正确用法是：**Context不负责创建策略对象**，策略的创建与注入由客户端或依赖注入容器完成。Context只负责"使用"传入的策略，而不做"决策"。

**误区二：策略数量少时滥用策略模式**

若一个算法只有2种变体，且在可预见的未来不会扩展，直接使用布尔参数或简单`if-else`反而更清晰。策略模式引入了至少3个类（接口+2个实现），在变体数量少且稳定的场景下增加了不必要的类爆炸（class explosion）。通常在算法变体≥3种，或者需要运行时切换时，才值得引入策略模式。

**误区三：忽略策略对象的无状态要求**

将算法执行过程中的临时数据（如排序的中间数组）存入策略对象的成员变量，会导致策略对象无法被多个Context安全共享，还可能引发并发问题。正确做法是将所有中间数据作为局部变量放在`algorithm()`方法栈帧内，或通过方法参数传递。

---

## 知识关联

**与状态模式的联系与区别**：状态模式（State Pattern）与策略模式结构几乎相同——同样是Context持有一个接口引用，同样支持运行时替换。关键差异在于**谁来触发切换**：策略模式中切换由**外部客户端**主动调用`set_strategy()`完成；状态模式中切换由**状态对象自身**或Context根据内部逻辑自动触发。理解这一差异是区分两种模式适用场景的核心。

**与模板方法模式的对比**：模板方法模式通过**继承**来变化算法的某个步骤，父类定义算法骨架，子类重写特定步骤。策略模式则通过**组合**来替换整个算法。前者适合"算法结构固定，局部步骤可变"的场景；后者适合"整个算法可以整体替换"的场景。

**对对象池模式的铺垫**：在高频切换策略的场景中（如每次请求都需要一个新的策略实例），频繁创建和销毁策略对象会产生GC压力。对象池模式（Object Pool）可以预先创建并缓存无状态的策略对象，供Context反复取用归还，从而与策略模式配合优化性能。
