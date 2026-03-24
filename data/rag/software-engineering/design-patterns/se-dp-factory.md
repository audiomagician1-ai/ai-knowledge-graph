---
id: "se-dp-factory"
concept: "工厂模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: true
tags: ["创建型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 工厂模式

## 概述

工厂模式是一类专门处理"对象创建"问题的创建型设计模式，其核心思想是将 `new` 关键字的直接调用从客户端代码中隐藏起来，交由专门的工厂类或方法负责。客户端只需说明想要什么产品，而不需要知道产品是如何被实例化的。这种"隐藏构造细节"的能力，使得更换产品实现时无需修改调用方代码。

工厂模式并非某一种单一模式，而是由三个层次递进的模式组成：简单工厂（Simple Factory）、工厂方法（Factory Method）和抽象工厂（Abstract Factory）。其中工厂方法模式由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式收录，而简单工厂严格来讲不在GoF的23种模式之列，属于一种编程惯用法。

工厂模式在日志框架、数据库连接池、UI组件库等场景中极为常见。例如 Java 的 `java.util.Calendar.getInstance()` 和 `java.sql.DriverManager.getConnection()` 都是工厂方法的实际案例。理解三种工厂变体之间的差异，是选择合适设计方案的关键判断能力。

## 核心原理

### 简单工厂（Simple Factory）

简单工厂使用一个静态方法（通常命名为 `create` 或 `getInstance`），通过 `if-else` 或 `switch` 分支，根据传入的类型参数决定实例化哪个具体类。其结构只有三个角色：**工厂类**、**抽象产品接口**、**具体产品类**。

```java
// 根据 type 字符串创建不同 Shape 对象
public static Shape createShape(String type) {
    if ("circle".equals(type)) return new Circle();
    else if ("rect".equals(type)) return new Rectangle();
    else throw new IllegalArgumentException("Unknown shape: " + type);
}
```

简单工厂的最大缺陷是违反了**开闭原则（OCP）**：每新增一种产品，就必须修改工厂类的 `switch/if` 分支，导致工厂类随产品种类增长而膨胀。

### 工厂方法（Factory Method）

工厂方法将"决定创建哪种产品"的职责从工厂类移到子类，父类只定义一个抽象的 `createProduct()` 方法，由每个子类覆写并返回自己负责的产品。其四个角色为：**抽象创建者**、**具体创建者**、**抽象产品**、**具体产品**。

```java
abstract class Dialog {
    abstract Button createButton();  // 工厂方法
    void render() { createButton().render(); }  // 使用工厂方法
}
class WindowsDialog extends Dialog {
    Button createButton() { return new WindowsButton(); }
}
class WebDialog extends Dialog {
    Button createButton() { return new HTMLButton(); }
}
```

新增产品时，只需新增一对"具体创建者 + 具体产品"，**不修改**已有代码，完全符合开闭原则。工厂方法的代价是类的数量随产品线性增长——每增加1个产品就需要至少增加1个工厂子类。

### 抽象工厂（Abstract Factory）

抽象工厂面向**产品族**（Product Family）而非单一产品。一个抽象工厂接口声明多个工厂方法，负责创建一整套相互配套的产品对象。例如一个 `GUIFactory` 接口同时声明 `createButton()`、`createCheckbox()`、`createScrollbar()` 三个方法，`WindowsFactory` 和 `MacFactory` 各自实现全套方法，保证同一工厂产出的组件风格一致。

| 维度 | 简单工厂 | 工厂方法 | 抽象工厂 |
|---|---|---|---|
| GoF收录 | 否 | 是 | 是 |
| 扩展方式 | 修改工厂类 | 新增子类 | 新增工厂实现 |
| 处理对象 | 单一产品 | 单一产品 | 产品族 |
| 典型场景 | 产品种类少且固定 | 产品种类会扩展 | 多套风格/平台切换 |

抽象工厂的代价是当需要向产品族中**新增一种产品类型**（如再加 `createMenu()`）时，必须修改抽象工厂接口及所有实现类，这是其主要缺陷。

## 实际应用

**跨数据库支持**：框架需同时支持 MySQL、PostgreSQL、SQLite 时，可用抽象工厂模式。`DatabaseFactory` 接口声明 `createConnection()`、`createQueryBuilder()`，`MySQLFactory` 与 `PostgresFactory` 各自实现，切换数据库只需替换工厂实例。

**日志组件**：SLF4J 采用工厂方法模式，`LoggerFactory.getLogger(Class)` 根据 classpath 上绑定的具体实现（Logback、Log4j2等）返回对应的 Logger 实例，调用方代码完全不感知底层实现。

**Android View 创建**：Android 的 `LayoutInflater` 使用工厂方法，将 XML 标签名映射为具体 View 子类的实例化，开发者可通过 `setFactory2()` 注入自定义工厂覆盖默认行为，实现换肤等功能。

## 常见误区

**误区一：认为简单工厂就是工厂方法**。两者有本质区别：简单工厂是一个单一类用 `if-else` 创建所有产品，新增产品必须修改这个类；工厂方法是通过继承将创建行为分散到子类，新增产品无需改动已有代码。混淆两者会导致错误评估代码的可扩展性。

**误区二：认为抽象工厂只是"工厂的工厂"**。这个描述在字面上勉强成立，但会误导对其适用场景的判断。抽象工厂的关键价值在于**保证产品族内部的一致性约束**——它不允许 `WindowsButton` 与 `MacCheckbox` 混搭出现，这种约束是工厂方法无法提供的。

**误区三：认为工厂模式总是比直接 `new` 更好**。当产品类型固定（如只有一种实现且未来不会扩展）、对象创建逻辑无需复用时，直接 `new` 反而更清晰。过度使用工厂模式会引入不必要的类数量膨胀，增加代码阅读成本。

## 知识关联

学习工厂模式之前，需要掌握**面向接口编程**和**多态**原理——工厂方法中 `createProduct()` 返回类型是抽象产品接口，而非具体类，正是多态机制使客户端代码得以解耦。此外，简单工厂对开闭原则的违反，是理解为何需要工厂方法的直接动因，两者对比学习效果最佳。

后续的**建造者模式**同样是创建型模式，但其关注点从"创建哪种对象"转移到"如何一步步构造一个复杂对象"——工厂模式通常一步返回完整产品，而建造者模式将构造过程拆分为多个 `setXxx()` 步骤，最后调用 `build()` 完成装配，适合参数超过4~5个的复杂对象。**原型模式**则是另一种创建策略，通过克隆已有实例而非调用构造函数来生成新对象，当对象创建成本极高（如深度网络模型初始化）时可替代工厂模式使用。
