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
quality_tier: "B"
quality_score: 49.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
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

建造者模式（Builder Pattern）是一种创建型设计模式，专门用于解决**复杂对象需要多个步骤分阶段构建**的问题。它将一个复杂对象的构建过程与其表示分离，使得同样的构建过程可以创建出不同的表示形式。与工厂模式直接返回一个完整产品不同，建造者模式通过一系列有序的方法调用逐步组装对象，每个方法负责设置对象的一个特定部分。

建造者模式最早由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式收录，书中使用"RTF文档阅读器将RTF格式转换为多种目标格式（ASCII、TeX、文本小部件）"作为经典示例。该模式的核心价值在于：当一个对象的构造参数超过4到5个，且其中多个参数是可选的时，链式建造者能有效替代"重叠构造器"（Telescoping Constructor）反模式，消除因参数顺序混淆导致的静默错误。

## 核心原理

### 四个角色的职责划分

建造者模式由四个明确角色组成：

- **Product（产品）**：最终被构建的复杂对象，例如一辆汽车，包含引擎、座椅、GPS等多个零部件。
- **Builder（抽象建造者）**：定义构建各个零部件的抽象接口，例如 `buildEngine()`、`buildSeats()`、`buildGPS()`。
- **ConcreteBuilder（具体建造者）**：实现 Builder 接口，为每个零部件提供具体的构建逻辑，并持有正在构建中的 Product 实例。不同的 ConcreteBuilder 可以组装出"豪华型汽车"或"经济型汽车"。
- **Director（指挥者）**：持有 Builder 的引用，定义构建步骤的调用顺序。Director 不关心零部件的具体实现，只知道"先装引擎，再装座椅"这样的组装流程。

### Director 的核心作用

Director 是建造者模式区别于简单链式调用的关键。一个典型的 Director 实现如下（伪代码）：

```
class CarDirector {
    private Builder builder;
    
    void constructSportsCar(Builder builder) {
        builder.buildEngine("V8");
        builder.buildSeats(2);
        builder.buildGPS(true);
    }
    
    void constructSUV(Builder builder) {
        builder.buildEngine("V6");
        builder.buildSeats(7);
        builder.buildGPS(false);
    }
}
```

Director 将"构建一辆跑车需要哪些步骤以及步骤顺序"这一知识封装起来，客户端代码只需告诉 Director 使用哪个 Builder，而不必了解具体的构建顺序。当产品的构建流程发生变化时，只需修改 Director，而所有 ConcreteBuilder 无需改动。

### 与链式建造者（Fluent Builder）的关系

现代Java和C#开发中常见的链式建造者（如 `new Person.Builder("John").age(30).phone("555").build()`）是建造者模式的简化变体，通常省略了 Director 角色，适用于对象构建顺序无强制约束的场景。每个 setter 方法返回 `this`（即 Builder 自身），最后通过 `build()` 方法校验并返回最终对象。Joshua Bloch 在《Effective Java》第2条中将此变体作为替代多参数构造器的首选方案推荐。完整的 GoF 建造者模式（含 Director）则适用于构建步骤顺序固定且不可随意调换的场景。

## 实际应用

**SQL查询构建器**：许多ORM框架（如MyBatis、Hibernate）使用建造者模式构建SQL语句。`QueryBuilder` 提供 `select()`、`from()`、`where()`、`orderBy()` 等方法，最后调用 `build()` 生成合法的SQL字符串。这里的"合法顺序"（SELECT必须在WHERE之前）可以由 Director 或 `build()` 方法内部强制执行。

**Android中的AlertDialog**：Android SDK 的 `AlertDialog.Builder` 是教科书级别的链式建造者应用。开发者依次调用 `.setTitle()`、`.setMessage()`、`.setPositiveButton()`，最后调用 `.create()` 或 `.show()` 完成对话框的构建，避免了直接操作 AlertDialog 的多个可选字段。

**游戏角色生成**：角色扮演游戏中，`CharacterBuilder` 可分步设置种族、职业、外貌、装备等属性，而 Director 可预设"精灵法师模板"和"人类战士模板"两种构建流程，复用同一套 Builder 接口生成不同配置的角色。

## 常见误区

**误区一：认为建造者模式等同于链式调用**。许多开发者将 `StringBuilder` 的链式 `append()` 调用视为建造者模式的典型案例，但 `StringBuilder` 并没有分离构建步骤与最终产品表示，也没有可替换的 ConcreteBuilder，本质上只是一个可变对象的方法链，不满足建造者模式中"同一构建过程产生不同表示"的核心意图。

**误区二：认为建造者模式可以完全替代工厂模式**。工厂模式适用于创建类型不确定但结构相对简单的对象（通常一步完成），建造者模式适用于结构固定但内部配置复杂的对象（需要多步完成）。如果一个对象的所有"可选部分"都真正可选且无顺序依赖，直接使用带默认值的构造器或简单工厂即可，强行引入建造者模式会增加 Builder 和 ConcreteBuilder 至少两个额外类的维护成本。

**误区三：Director 必须存在**。GoF 原著中 Director 是可选角色。当客户端代码本身就能确定构建顺序时，可以直接操作 Builder 而不引入 Director。Director 的必要性仅在于：需要在多处复用同一套构建步骤序列时，才值得将该序列封装进 Director。

## 知识关联

**与工厂模式的衔接**：工厂模式（包括工厂方法和抽象工厂）解决的是"创建哪个类的实例"的问题，决策点在对象类型上；建造者模式解决的是"如何一步步组装一个已知类型的复杂对象"的问题，决策点在组装过程上。两者可以组合使用：Director 内部可以调用工厂方法来创建各个零部件，再将零部件组装进 Product。

**对象构建复杂度的演进路径**：当一个类的构造参数从2个增长到3个时，可以使用普通构造器；增长到5个以上且有可选参数时，应考虑链式建造者；当构建步骤本身有强制顺序且存在多种构建方案需要复用时，才引入完整的带 Director 的建造者模式。理解这一演进路径有助于在实际项目中判断引入建造者模式的时机，避免过度设计。