---
id: "se-dp-decorator"
concept: "装饰器模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["结构型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 装饰器模式

## 概述

装饰器模式（Decorator Pattern）是一种结构型设计模式，其核心思想是在不修改原有对象代码的前提下，通过将对象包裹在装饰器对象内部，动态地为其附加新的职责或行为。与子类化不同，装饰器模式允许在运行时按需叠加功能，而非在编译期通过继承固化类的能力。

该模式由 Gang of Four（GoF）于1994年在《设计模式：可复用面向对象软件的基础》一书中正式命名和记录。书中明确将其归类为结构型模式，并提出"组合优于继承"（Favor composition over inheritance）的设计原则——装饰器模式正是这一原则最典型的实现形式。

装饰器模式解决的是功能扩展的组合爆炸问题。假设一个咖啡系统中有3种基础咖啡和4种配料，若用继承实现所有组合，需要 3×(2⁴-1)+3 = 48 个子类；而使用装饰器模式，只需 3 个基础类和 4 个装饰器类，共 7 个类即可覆盖全部组合场景。

---

## 核心原理

### 结构组成

装饰器模式由四个角色构成：

- **Component（抽象组件）**：定义对象接口，是被装饰对象和装饰器的共同超类型，例如接口 `Beverage`。
- **ConcreteComponent（具体组件）**：实现 Component 的原始对象，即被包裹的核心对象，例如 `Espresso`。
- **Decorator（抽象装饰器）**：持有一个 Component 类型的引用，并实现同一接口，将方法调用委托给被包裹的对象。
- **ConcreteDecorator（具体装饰器）**：在委托调用前后添加新行为，例如 `MilkDecorator` 在 `cost()` 返回值上叠加牛奶的价格。

关键在于：装饰器与被装饰对象实现**同一接口**，因此对调用者透明，外部代码无需区分"原始对象"和"被装饰对象"。

### 核心公式与代码结构

装饰器的方法调用遵循链式委托模式，以计算价格为例：

```
total_cost = decorator_n.cost()
           = own_cost_n + decorator_(n-1).cost()
           = own_cost_n + own_cost_(n-1) + ... + concrete_component.cost()
```

在 Java 实现中，`InputStream` 体系是标准库里最经典的装饰器应用：`FileInputStream` 是 ConcreteComponent，`BufferedInputStream` 是 ConcreteDecorator，其构造函数接收一个 `InputStream` 并在 `read()` 调用外层增加缓冲逻辑。

```java
InputStream in = new BufferedInputStream(
                     new DataInputStream(
                         new FileInputStream("data.txt")));
```

每一层包裹都是一次装饰，职责通过嵌套叠加，而非通过多重继承混合。

### 装饰器 vs 继承的关键区别

继承在编译期确定类的全部行为，且每增加一种组合就需要一个新类。装饰器模式在运行时动态决定对象具备哪些职责——同一个 `Espresso` 对象，可以在程序运行中先被 `MilkDecorator` 包裹，再被 `SugarDecorator` 包裹，顺序不同结果相同（对于叠加型操作），或顺序有意义（对于有序操作如加密后压缩 vs 压缩后加密）。装饰器的层数原则上不受限制，而继承深度超过3层即被业界普遍认为是代码坏味道。

---

## 实际应用

**Java I/O 库**：`java.io` 包完整采用装饰器模式。`BufferedReader`、`InputStreamReader`、`PrintStream` 均是装饰器，可以任意嵌套在 `InputStream`/`Reader` 体系上，为基础流增加缓冲、字符编码转换、格式化输出等能力。

**Python 函数装饰器**：Python 的 `@decorator` 语法是语言层面对装饰器模式的原生支持。`@functools.lru_cache` 将任意函数包裹后添加缓存职责，`@app.route` 在 Flask 中将函数注册为路由处理器，原始函数本身不做任何修改。

**UI 组件扩展**：在前端框架中，高阶组件（Higher-Order Component，HOC）本质上是装饰器模式——`withAuth(MyComponent)` 返回一个新组件，在渲染 `MyComponent` 前检查用户权限，`MyComponent` 自身不包含任何认证逻辑。

**游戏角色装备系统**：角色基础攻击力为 10，装备"火焰剑"装饰器后攻击力变为 10+15=25，再装备"力量戒指"装饰器后变为 25×1.2=30，多个装备效果按装饰链顺序叠加计算。

---

## 常见误区

**误区一：认为装饰器模式只能叠加，不能修改原有行为**

装饰器不仅可以在原方法调用前后追加逻辑（前置/后置装饰），也可以**完全替换**被装饰对象的行为而不调用 `super` 或委托方法。例如，一个缓存装饰器在命中缓存时直接返回结果，根本不调用被包裹对象的 `query()` 方法。

**误区二：把装饰器模式与代理模式混淆**

两者结构高度相似，都持有被包裹对象的引用并实现同一接口。本质区别在于**意图**：装饰器模式的目的是为对象**动态添加职责**，装饰器通常由客户端代码显式创建和组合；代理模式的目的是**控制对对象的访问**（延迟加载、访问控制、远程代理），代理通常对客户端透明，客户端不感知代理的存在。

**误区三：层数越多越灵活，无限叠加无代价**

装饰器链过长会导致调试困难——当 `cost()` 返回错误值时，需要逐层检查每个装饰器。此外，每个装饰器都是一次对象创建，深度嵌套在内存分配和方法调用栈上均有开销。业界通常建议单条装饰链不超过5层，超过时应考虑是否需要重新设计职责划分。

---

## 知识关联

**前置基础**：理解装饰器模式需要熟悉面向对象的接口与多态机制——装饰器能够替代原始对象的根本原因，是它与被装饰对象实现了相同的接口，满足里氏替换原则（LSP）。"组合优于继承"作为其设计哲学，也需要对继承的局限性（脆弱基类问题、类爆炸）有具体认识。

**后续概念——代理模式**：学完装饰器模式后，代理模式（Proxy Pattern）是天然的对比学习对象。两者共享"包裹对象并实现同一接口"的结构骨架，但代理模式引入了访问控制、懒加载（Virtual Proxy）、远程调用（Remote Proxy）等代理特有的职责。对比装饰器与代理的异同，是掌握结构型模式分类逻辑的有效路径——前者扩展能力，后者控制访问。