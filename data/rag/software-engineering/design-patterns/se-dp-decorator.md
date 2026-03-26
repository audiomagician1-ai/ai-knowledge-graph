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

装饰器模式（Decorator Pattern）是一种结构型设计模式，其核心思想是在不修改原始类代码的前提下，通过将对象包裹在装饰器对象中来动态地为其添加新行为。与直接修改类或使用继承相比，装饰器模式允许在运行时（而非编译时）灵活组合功能，且每个装饰器只负责一项附加职责。

该模式由"四人帮"（Gang of Four，GoF）在1994年出版的《设计模式：可复用面向对象软件的基础》一书中正式归纳。GoF 将其列为23种经典模式之一，并特别指出它是"继承"这一静态扩展机制的动态替代方案。在 Java 标准库中，`java.io.InputStream` 的整个体系（如 `BufferedInputStream` 包裹 `FileInputStream`）就是装饰器模式最广为人知的工业级实现案例。

装饰器模式解决了"类爆炸"问题：假设一个咖啡类需要支持加牛奶、加糖、加奶泡三种可选配料，若用继承实现所有组合需要 2³ = 8 个子类；而用装饰器只需要3个装饰器类加1个基类，总共4个类即可覆盖全部8种组合，且支持重复叠加（如加双份糖）。

---

## 核心原理

### 基本结构与四个角色

装饰器模式由四个角色构成：

- **Component（抽象组件）**：定义被装饰对象和装饰器共同遵守的接口，如 `Beverage` 接口中声明 `getCost()` 和 `getDescription()`。
- **ConcreteComponent（具体组件）**：实现 Component 的原始对象，如 `Espresso`，是被包裹的核心对象。
- **Decorator（抽象装饰器）**：持有一个 Component 类型的引用，并实现相同的 Component 接口。这一层是模式的关键——装饰器"是一个"组件，同时"拥有一个"组件，即同时满足 IS-A 和 HAS-A 关系。
- **ConcreteDecorator（具体装饰器）**：在调用被包裹对象方法的基础上添加额外行为，如 `MilkDecorator` 在 `getCost()` 中返回 `wrappedBeverage.getCost() + 0.25`。

### 包裹调用链与透明性原则

装饰器的工作机制是递归的"包裹调用链"。以 `MilkDecorator(SugarDecorator(Espresso))` 为例，调用最外层的 `getCost()` 时，执行顺序为：

```
MilkDecorator.getCost()
  → SugarDecorator.getCost()
    → Espresso.getCost()  // 返回 1.00
  → +0.10（糖的费用）    // 返回 1.10
→ +0.25（牛奶的费用）    // 返回 1.35
```

透明性原则要求客户端代码无需知道自己持有的是原始对象还是装饰后的对象——两者均实现相同接口，这使得装饰器可以在不影响调用方的情况下无限嵌套。

### 与继承的本质差异

继承在编译时固化行为扩展，且子类数量随功能组合呈指数增长。装饰器通过对象组合在运行时动态附加职责，遵循"组合优于继承"原则（Favor Composition over Inheritance，GoF 书中明确提出的设计准则之一）。具体来说：继承的扩展关系在代码编译后即不可更改；而装饰器的包裹关系可以在程序运行期间根据条件动态构建，例如根据用户的实时选择决定是否添加某项装饰。

---

## 实际应用

**Java I/O 流体系**：`new BufferedInputStream(new GZIPInputStream(new FileInputStream("data.bin")))` 这一行代码同时为文件流附加了 GZIP 解压和缓冲读取两种能力，每个包裹类只实现单一职责，完整体现了装饰器模式的工业级用法。

**Python 函数装饰器**：Python 语言内置的 `@` 语法糖是装饰器模式的语言级实现。`@lru_cache` 为函数动态附加了缓存记忆化能力，`@login_required`（Django 框架）为视图函数附加了登录验证逻辑，两者均不修改原函数的任何代码。

**前端 UI 组件扩展**：在 React 生态中，高阶组件（Higher-Order Component，HOC）本质上是装饰器模式。`withRouter(MyComponent)` 将路由能力注入到 `MyComponent`，返回的新组件与原组件具有相同的 props 接口，保持了透明性原则。

**咖啡馆订单系统**：星巴克的定制饮品（如"拿铁加燕麦奶加两份香草糖浆"）在《Head First 设计模式》一书中被用作装饰器模式的教学标准案例，完整演示了装饰器如何支持同一类型装饰器的重复叠加。

---

## 常见误区

**误区一：认为装饰器模式就是继承的另一种写法**
装饰器与继承在本质上不同：继承创建的是一个新类型，在编译时绑定行为；装饰器在运行时通过对象组合添加行为，不创建新类型，被装饰对象的实际类型不发生改变。如果你用继承实现"咖啡加牛奶"，`MilkCoffee` 是 `Coffee` 的子类；而用装饰器，`MilkDecorator` 包裹的仍然是一个 `Beverage` 实例，其类型在运行时是 `MilkDecorator`，不是 `Espresso` 的子类。

**误区二：把装饰器模式和责任链模式混淆**
装饰器模式中，每一层装饰器**必须**调用被包裹对象的同名方法（即 `super` 调用或委托调用），调用链不会中断；而责任链模式中，链上的处理者可以选择**不向下传递**请求，直接处理后终止链条。装饰器是**增强**行为，责任链是**分发**行为，两者的中断语义完全相反。

**误区三：过度使用导致调试困难**
当装饰器嵌套层数超过3至4层时，调试堆栈会变得极难阅读，`toString()` 打印出的对象信息也形如 `A(B(C(D(...))))`，难以直观理解当前对象的完整状态。针对这一问题，应在装饰器的 `getDescription()` 等方法中显式拼接每一层的描述信息，而非依赖默认的对象标识符。

---

## 知识关联

**前置概念**：装饰器模式不依赖复杂的前置知识，但需要熟悉面向对象编程中接口（Interface）和组合（Composition）的基本概念——具体而言，需理解"一个类可以同时持有某接口的引用并实现该接口"这一代码结构为何合法且有意义。

**后续概念——代理模式**：代理模式（Proxy Pattern）与装饰器模式在代码结构上几乎完全相同，均持有同接口的被包裹对象引用。两者的本质区别在于**意图**：装饰器的目的是**添加新功能**（如增加缓存、添加日志）；代理的目的是**控制访问**（如权限验证、延迟初始化、远程访问）。学习代理模式时，最有效的方式是对比同一段结构相似的代码，分析其意图差异，从而体会设计模式中"意图比结构更重要"的核心思想。