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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 策略模式

## 概述

策略模式（Strategy Pattern）是一种行为型设计模式，其核心思想是将一族可互换的算法分别封装到独立的类中，使得算法可以独立于使用它的客户端而变化。GoF（Gang of Four）在1994年出版的《Design Patterns》中将其定义为："定义一系列算法，把每一个算法封装起来，并且使它们可以相互替换。"与观察者模式关注对象间通知机制不同，策略模式专注于将"做什么"与"怎么做"分离。

策略模式的本质是面向接口编程而非面向实现编程。一个 `Context`（上下文）对象持有对某个 `Strategy`（策略接口）的引用，在运行时可以将该引用指向不同的 `ConcreteStrategy`（具体策略）实例，从而切换算法行为，而 `Context` 自身的代码无需修改。这直接体现了开闭原则：对扩展开放，对修改关闭。

策略模式在排序、支付方式切换、文件压缩算法选择等场景中极为常见。一个没有策略模式的系统往往依赖大量 `if-else` 或 `switch-case` 来分支不同算法，每次新增算法都需要修改已有代码，引入回归风险。策略模式将这些分支替换为多态调用，把复杂度从条件判断转移到类的组织结构中。

---

## 核心原理

### 三角色结构

策略模式由三个核心角色构成：

- **Strategy（策略接口）**：声明所有具体策略必须实现的方法签名，例如 `execute(int[] data): int[]`。
- **ConcreteStrategy（具体策略）**：实现 `Strategy` 接口的具体算法类，如 `BubbleSortStrategy`、`QuickSortStrategy`、`MergeSortStrategy`，每个类只负责一种排序算法。
- **Context（上下文）**：持有一个 `Strategy` 类型的成员变量，通过构造函数注入或 `setStrategy()` 方法在运行时替换策略，然后通过 `context.executeStrategy()` 委托给当前策略执行。

`Context` 与具体策略之间是**组合关系而非继承关系**，这是策略模式区别于模板方法模式的根本差异。

### 运行时切换机制

策略的切换发生在运行时，不需要重新编译。以Java为例：

```java
Context ctx = new Context(new QuickSortStrategy());
ctx.executeStrategy(data);           // 使用快速排序

ctx.setStrategy(new MergeSortStrategy());
ctx.executeStrategy(data);           // 切换为归并排序，零改动Context
```

`setStrategy()` 方法接收 `Strategy` 接口类型的参数，而非任何具体类。这意味着新增第N种策略只需新建一个实现类，`Context` 代码保持不变，符合依赖倒置原则（DIP）。

### 消除条件分支

假设一个电商系统支持三种促销计算：满减、折扣、返现。不使用策略模式时，代码为：

```java
if (type == "discount") { price *= 0.9; }
else if (type == "full_minus") { price -= 50; }
else if (type == "cashback") { cashback += 20; }
```

每增加一种促销，上述代码块就必须被修改。使用策略模式后，每种促销封装为独立的 `PromotionStrategy` 实现类，`Context` 只调用 `strategy.calculate(price)`，新增促销类型时零修改已有代码。这种转变将 O(n) 的条件判断复杂度分散到 n 个独立的、可单独测试的类中。

---

## 实际应用

**Java标准库中的策略模式**：`java.util.Comparator` 接口是策略模式最典型的标准库实现。`Collections.sort(list, comparator)` 中，`comparator` 即为策略对象，传入不同的 `Comparator` 实现（如按姓名排序、按年龄排序）即可在运行时切换排序规则，`Collections.sort` 方法本身（Context）不做任何修改。

**支付系统**：电商平台的结算模块通常将支付方式抽象为 `PaymentStrategy`，包含 `pay(int amount)` 方法。`WeChatPayStrategy`、`AlipayStrategy`、`CreditCardStrategy` 分别实现该接口。用户在购物车页面选择支付方式时，系统将对应策略注入 `PaymentContext`，调用统一入口完成支付，新接入银联只需新增 `UnionPayStrategy` 类即可。

**游戏AI行为**：在游戏开发中，NPC的移动算法（`PathfindingStrategy`）可在运行时根据地形切换：开阔地使用 `AStarStrategy`，迷宫中使用 `BFSStrategy`，追逐玩家时使用 `DirectChaseStrategy`。Unity和Unreal的行为树插件底层均采用了策略模式变体来处理行为节点的替换。

**文件压缩工具**：压缩软件将 `CompressionStrategy` 定义为接口，包含 `compress(byte[] data): byte[]`，由 `ZipStrategy`、`GzipStrategy`、`LzmaStrategy` 实现。用户界面根据用户选择动态设置策略，`Compressor`（Context）无需关心底层算法细节。

---

## 常见误区

**误区1：策略模式与简单工厂模式是同一回事**
简单工厂负责"创建哪个对象"，其返回值通常直接被使用一次；策略模式的 `Context` 持有策略对象的引用，强调在整个生命周期内可以**多次切换**同一个 Context 的算法。两者常配合使用——工厂负责根据条件创建具体策略对象，策略模式负责将其注入并使用，但本质职责不同，混淆会导致 Context 承担了本不属于它的对象创建责任。

**误区2：所有 if-else 都应替换为策略模式**
策略模式引入了至少3个新类（接口 + 若干实现），如果算法分支只有2种且极少变化，直接用 `if-else` 反而更清晰、维护成本更低。策略模式适用的判断标准是：**算法族有3种以上、且未来有扩展预期、且客户端需要在运行时切换**。盲目应用导致类爆炸（Class Explosion）是过度设计的典型症状。

**误区3：策略模式的 Context 应该知道所有具体策略**
正确的策略模式中，`Context` 只依赖 `Strategy` 接口，完全不知道任何 `ConcreteStrategy` 的存在。一旦 `Context` 内部出现 `instanceof BubbleSortStrategy` 或 `if (strategy is QuickSort)` 的判断，说明设计已退化，违反了依赖倒置原则，此时策略模式形同虚设。

---

## 知识关联

**与观察者模式的关系**：观察者模式中，`Observer` 接口定义了 `update()` 回调，多个观察者实现同一接口，这与策略模式的 `ConcreteStrategy` 实现 `Strategy` 接口在结构上高度相似。区别在于语义：观察者模式用于"当事件发生时通知多个监听者"（1对N），策略模式用于"在同一时刻只有一个算法处于活跃状态"（1对1的可替换关系）。理解了观察者的接口多态机制，策略模式的接口设计水到渠成。

**与状态模式的区别**：状态模式与策略模式在类图上几乎相同，但状态模式中的 `ConcreteState` 类可以**主动触发** `Context` 的状态转换（即具体状态知道下一个状态是什么），而策略模式中具体策略类对 `Context` 一无所知，切换权完全在客户端或 `Context` 自身。

**与模板方法模式的对比**：模板方法模式用继承实现算法骨架的固定与步骤的扩展，编译时确定；策略模式用组合在运行时替换整个算法，更灵活但类数量更多。两者都解决算法变化问题，选择依据是"变化点在算法的局部步骤还是整个算法"。

**向命令模式的延伸**：命令模式可视为策略模式的扩展——`Command` 接口同样封装了一个"行为"，但额外支持撤销（`undo()`）、排队执行和日志记录等功能，将"行为对象化"的思路推向更复杂的场景。