---
id: "se-dp-template"
concept: "模板方法模式"
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

# 模板方法模式

## 概述

模板方法模式（Template Method Pattern）是一种行为型设计模式，它在父类中定义一个算法的骨架（即固定步骤序列），并将某些步骤的具体实现延迟到子类中完成。父类中这个定义骨架的方法称为**模板方法**，它通常被声明为 `final`，防止子类修改整体算法流程，而骨架中的可变步骤则声明为抽象方法或钩子方法（hook method）供子类覆写。

该模式最早由 Gang of Four（GoF）在1994年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中正式收录，归类为行为型模式。其核心思想体现了面向对象设计的"好莱坞原则"（Hollywood Principle）：**Don't call us, we'll call you**——父类掌控流程，子类只提供具体行为，而不自行决定何时被调用。

模板方法模式直接解决代码重复问题。当多个子类拥有相同的算法流程但某几个步骤实现不同时，如果不使用该模式，每个子类都要重写整段流程，造成大量重复代码。模板方法将不变的部分集中在父类，变化的部分下沉到子类，符合"开闭原则"——对扩展开放（新增子类即可扩展），对修改关闭（无需改动父类骨架）。

---

## 核心原理

### 模板方法的组成要素

一个标准的模板方法模式包含以下三类方法：

1. **模板方法（Template Method）**：定义算法骨架，调用其他方法的固定序列，通常声明为 `final` 防止子类覆写。
2. **抽象方法（Abstract Method）**：骨架中必须由子类实现的步骤，父类不提供默认实现。
3. **钩子方法（Hook Method）**：父类提供空实现或默认实现的可选步骤，子类可选择性覆写。钩子方法赋予子类"影响"流程而非"控制"流程的能力。

以Java伪代码为例：

```java
abstract class DataProcessor {
    // 模板方法，final 禁止覆写
    public final void process() {
        readData();       // 抽象方法：必须覆写
        processData();    // 抽象方法：必须覆写
        if (needsOutput()) { // 钩子方法控制可选步骤
            writeOutput();
        }
    }
    abstract void readData();
    abstract void processData();
    void writeOutput() {} // 钩子：默认空实现
    boolean needsOutput() { return true; } // 钩子：默认返回 true
}
```

### 与继承的关系

模板方法模式**依赖继承**实现行为复用，这与策略模式依赖组合（将算法封装为独立对象）形成直接对比。模板方法的整个骨架固化在编译时，子类数量即扩展点数量，每个新变体需要新建一个子类。这意味着当变体数量极多时，类层次结构会膨胀，而策略模式可以通过运行时传入不同策略对象规避此问题。

### 不变部分与可变部分的识别

设计模板方法的关键在于正确区分**不变步骤**和**可变步骤**。以泡茶与泡咖啡为例（GoF原书的经典示例）：

- **不变步骤**：烧水 → 浸泡/冲泡 → 倒入杯中 → 加调料
- **可变步骤**：`brew()`（泡茶用茶叶，泡咖啡用咖啡粉）、`addCondiments()`（茶加柠檬，咖啡加糖奶）

父类 `CaffeineBeverage` 将这四步写入 `final void prepareRecipe()` 模板方法，子类 `Tea` 和 `Coffee` 分别实现 `brew()` 和 `addCondiments()`，约50%的代码得以在父类中共享。

---

## 实际应用

### Java标准库中的应用

Java标准库大量使用模板方法模式。`java.util.AbstractList` 中，`indexOf()` 和 `contains()` 等具体方法基于 `get(int index)` 和 `size()` 构建，后两者是抽象方法，由 `ArrayList`、`LinkedList` 等具体子类实现。`java.io.InputStream` 的 `read(byte[], int, int)` 方法是模板方法，它在内部多次调用抽象的单字节 `read()` 方法。

### Junit 测试框架

JUnit 3.x 中，`TestCase` 类的 `runTest()` 方法是模板方法，框架固定调用 `setUp()` → 测试方法 → `tearDown()` 的顺序。开发者只需在子类中覆写 `setUp()` 和 `tearDown()` 来准备和清理测试环境，无需关心调用顺序，这正是模板方法"好莱坞原则"的体现。

### Android Activity 生命周期

Android 的 `Activity` 类定义了 `onCreate()` → `onStart()` → `onResume()` → `onPause()` → `onStop()` → `onDestroy()` 的回调序列，框架（父类）控制整个生命周期流程，开发者（子类）覆写其中需要定制的钩子方法。Activity 的整个生命周期管理就是一个大型模板方法的应用实例。

---

## 常见误区

### 误区一：把所有步骤都声明为抽象方法

初学者常将骨架中的每一步都设为抽象方法，强迫每个子类实现所有步骤，即使大多数子类的实现完全相同。正确做法是：只有真正需要变化的步骤才设为抽象方法，可选变化的步骤设为钩子方法（提供默认实现），不变的步骤直接在父类中实现，不对外开放。

### 误区二：忽略 `final` 修饰模板方法

如果不将模板方法声明为 `final`，子类可以覆写整个骨架方法，完全绕开父类定义的流程，使模板方法模式失去意义。部分开发者认为 `final` 限制了灵活性，但这恰恰是该模式的**设计意图**——流程控制权必须保留在父类，子类只能填充步骤而非重写流程。

### 误区三：混淆模板方法模式与策略模式的适用场景

两者都解决"算法变体"问题，但适用条件不同。当算法步骤序列固定、只有少数步骤实现不同、且子类数量可控时，用模板方法（继承，静态绑定）。当需要运行时切换整个算法、或变体数量很多时，用策略模式（组合，动态绑定）。将两者混用——例如在模板方法的某个步骤中注入策略对象——是合法且常见的组合方式，但不能将二者等同。

---

## 知识关联

**与策略模式的对比**：策略模式和模板方法模式都是行为型模式，都用于封装算法变体。策略模式通过接口组合在运行时替换完整算法，而模板方法通过继承在编译时固定算法骨架。理解了策略模式的组合思想，再学习模板方法的继承思想，能清晰感受到"组合优于继承"原则的适用边界。

**与状态模式的联系**：状态模式中，状态对象的 `handle()` 方法序列有时也遵循固定流程，可以在状态类的基类中用模板方法定义状态处理骨架，让具体状态子类只实现差异化行为。两者在类结构上有相似之处（都利用多态），但状态模式聚焦于对象行为随状态改变，模板方法聚焦于固定流程内的步骤替换。

**通往迭代器模式**：学习迭代器模式时，会遇到 `java.util.AbstractIterator` 等抽象迭代器类，它们往往用模板方法固定 `hasNext()`/`next()` 的调用协议，子类只实现底层数据访问。掌握模板方法模式后，理解这类抽象迭代器的设计意图会更加直接。