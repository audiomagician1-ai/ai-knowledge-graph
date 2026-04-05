---
id: "se-dp-builder"
concept: "建造者模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["创建型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 建造者模式

## 概述

建造者模式（Builder Pattern）是一种创建型设计模式，专门用于解决构造参数过多、对象创建步骤复杂的问题。它将一个复杂对象的**构建过程**与其**表示形式**分离，使得同一套构建流程可以生产出不同的最终对象。与工厂模式的"一步到位"不同，建造者模式强调"分步构建"——对象的创建被拆分为多个独立的步骤，每个步骤对应一个具体的构建方法。

建造者模式由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式命名，书中以文本转换器（RTF读取器转换为多种格式）作为典型案例。在 Java 生态中，`StringBuilder` 类是最广为人知的建造者模式应用，它通过链式调用 `append()` 方法逐步拼接字符串，最后调用 `toString()` 获取结果。

这一模式在构造函数参数超过4个时体现出最大价值。当一个对象拥有10个可选配置项时，使用构造函数重载会产生"伸缩构造函数"反模式（Telescoping Constructor Anti-pattern），代码可读性极差。建造者模式通过将每个参数封装为独立的 `setX()` 构建方法，并最终通过 `build()` 触发对象实例化，彻底解决了这一问题。

---

## 核心原理

### 四个核心角色

建造者模式由四个角色构成，缺少任何一个结构都会不完整：

- **Product（产品）**：最终要构建的复杂对象，例如一辆汽车或一份完整的 SQL 查询语句。
- **Builder（抽象建造者）**：声明构建各个部件的抽象接口，如 `buildEngine()`、`buildWheels()`、`buildSeats()`。
- **ConcreteBuilder（具体建造者）**：实现 Builder 接口，负责具体部件的创建与组装，同时持有一个 Product 实例。
- **Director（指挥者）**：持有一个 Builder 引用，定义构建步骤的调用顺序，但不关心具体产品的内部构造。

Director 是建造者模式区别于其他创建型模式的关键所在。它封装了"如何组合步骤"的业务逻辑，客户端只需告知 Director 使用哪个 ConcreteBuilder，Director 便会按照固定流程完成构建。

### Director 与 Builder 的职责分界

Director 中的典型代码结构如下：

```java
public class CarDirector {
    private CarBuilder builder;
    public CarDirector(CarBuilder builder) {
        this.builder = builder;
    }
    public void constructSportsCar() {
        builder.buildEngine("V8");
        builder.buildWheels(4);
        builder.buildSeats(2);
    }
    public void constructSUV() {
        builder.buildEngine("V6");
        builder.buildWheels(4);
        builder.buildSeats(7);
    }
}
```

Director 中定义了 `constructSportsCar()` 和 `constructSUV()` 两种不同的构建流程。替换不同的 ConcreteBuilder 实例（如 `ElectricCarBuilder` vs `GasolineCarBuilder`），Director 可在完全不修改自身代码的情况下输出截然不同的产品。这体现了**开闭原则**：对扩展开放，对修改关闭。

### 流式建造者（Fluent Builder）的变体

现代框架中更常见的是省略 Director 的流式建造者变体，通过方法链实现同样效果：

```java
Pizza pizza = new Pizza.Builder()
    .size(12)
    .crust("thin")
    .topping("cheese")
    .topping("mushroom")
    .build();
```

每个构建方法返回 `this`（当前 Builder 实例），最终 `build()` 方法执行必要的参数校验后返回不可变的 Product 对象。Joshua Bloch 在《Effective Java》第2版（2008年）的第2条中将此变体作为处理多参数构造器的首选方案明确推荐。这种变体中 Builder 本身承担了 Director 的职责，适合构建逻辑相对简单、不需要多套构建方案的场景。

---

## 实际应用

**Lombok 的 `@Builder` 注解**：在 Java 项目中，`@Builder` 注解会自动为类生成静态内部 Builder 类，无需手写任何建造者代码。标注 `@Builder` 后，编译器生成的代码完整实现了流式建造者变体，包括所有字段的链式 setter 和最终的 `build()` 方法。

**SQL 查询构建器**：MyBatis、JOOQ 等 ORM 框架使用建造者模式构建动态 SQL。例如 JOOQ 的链式 API：`dsl.select(field).from(table).where(condition).orderBy(field).limit(10)` 将 SQL 的每个子句映射为独立的构建步骤，最终生成合法的 SQL 字符串，避免了字符串拼接的安全隐患（如 SQL 注入）。

**Android AlertDialog**：Android SDK 的 `AlertDialog.Builder` 是教科书级别的建造者模式应用。`setTitle()`、`setMessage()`、`setPositiveButton()` 等方法各自设置对话框的独立部分，全部完成后调用 `create()` 或 `show()` 生成最终的 AlertDialog 对象，且生成后对象不可再被修改，保证了不可变性。

**Protobuf 生成代码**：Google Protocol Buffers 自动生成的 Java 代码中，每个消息类型都附带一个 Builder，通过 `toBuilder()` 可从现有对象创建 Builder，实现对现有对象的"修改性复制"，这解决了不可变对象难以局部更新的难题。

---

## 常见误区

**误区一：认为建造者模式等于"有 Builder 内部类的类"**

很多开发者将流式 Builder 等同于建造者模式的完整形式，忽略了 Director 角色的存在。实际上，当同一个 Builder 需要支持多种固定构建流程时（例如"豪华套餐"和"基础套餐"），Director 是消除重复构建代码的正确方式，而不是在业务层代码中重复编写相同的 Builder 调用序列。

**误区二：将建造者模式与工厂模式混淆使用**

工厂模式适合"根据类型参数返回不同子类实例"的场景，创建逻辑是单步的、类型驱动的。建造者模式适合"同一类型的对象需要通过多个步骤逐步配置"的场景，创建逻辑是多步的、结构驱动的。若某对象只有2-3个必填参数且无可选配置，引入 Builder 是过度设计。

**误区三：`build()` 方法前不做参数校验**

建造者模式的 `build()` 方法是执行参数一致性校验的最佳时机。例如，构建 HTTP 请求时，若 `method` 为 `POST` 但 `body` 为空，应在 `build()` 中抛出 `IllegalStateException`，而不是等到实际发送请求时才报错。跳过此步骤会导致创建出内部状态不合法的 Product 对象，破坏建造者模式保证对象合法性的核心价值。

---

## 知识关联

**前置知识——工厂模式**：工厂模式解决"创建哪个类"的问题，建造者模式解决"如何一步步创建同一个类"的问题。掌握工厂方法模式后，可以理解建造者模式中 `ConcreteBuilder` 本质上是对产品组件创建逻辑的集中封装，而 Director 提供了比工厂更细粒度的流程控制能力。

**设计原则关联**：建造者模式直接体现了**单一职责原则**（Director 只管流程，Builder 只管构造，Product 只管表示）和**开闭原则**（新增产品类型只需添加新的 ConcreteBuilder，无需修改 Director 或已有 Builder）。同时，不可变 Product 的设计思想与**防御性编程**理念一致，确保构建完成的对象在多线程环境下天然线程安全。