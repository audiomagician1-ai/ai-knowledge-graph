---
id: "se-null-object"
concept: "Null对象模式"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.519
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Null对象模式

## 概述

Null对象模式（Null Object Pattern）是一种行为型设计模式，通过引入一个实现了目标接口但所有方法均为"什么都不做"或返回安全默认值的特殊对象，来消除代码中散布各处的 `if (obj != null)` 检查。它的核心思想是：与其让调用方每次使用对象前都判断是否为null，不如提供一个永远合法、永远可调用的"空"实现。

该模式由 Bobby Woolf 于1996年在《Pattern Languages of Program Design 3》一书中正式命名和描述。在此之前，许多程序员已经在实践中无意识地使用这个技巧，但缺乏统一的名称和规范化表述。Martin Fowler 在其重构著作中将"引入Null对象"（Introduce Null Object）列为独立的重构手法，认为它能显著减少条件判断噪音，让主流程代码更清晰地表达业务意图。

该模式之所以重要，是因为null引用本身被Hoare爵士在2009年称为"价值十亿美元的错误"（The Billion Dollar Mistake）——其在运行时造成的 `NullPointerException` 或 `NullReferenceException` 是工业界最常见的崩溃原因之一。Null对象模式从设计层面绕开这个陷阱，将"没有对象"这一语义转化为一个合法的多态实现。

---

## 核心原理

### 结构组成

Null对象模式的结构包含三个角色：
- **抽象类/接口（AbstractObject）**：声明客户端需要的操作，例如 `Logger` 接口定义 `log(String message)` 方法。
- **真实实现（RealObject）**：提供真正的业务行为，例如 `ConsoleLogger` 将消息输出到控制台。
- **Null对象（NullObject）**：同样实现该接口，但所有方法体为空或返回零值/空集合，例如 `NullLogger` 的 `log` 方法体内什么都不做。

客户端持有的变量类型是 `AbstractObject`，无论其实际指向 `RealObject` 还是 `NullObject`，调用方式完全相同，无需任何分支判断。

### 方法体的设计原则

Null对象中各方法的返回值必须是"语义安全"的，而非随意填写：
- 返回 `void` 的方法：方法体留空。
- 返回数值的方法：通常返回 `0` 或 `1`（视业务含义而定，如计数器返回0，乘法因子返回1）。
- 返回布尔值的方法：通常返回 `false`，但"isNull()"方法应返回 `true`。
- 返回集合的方法：返回空集合 `Collections.emptyList()`，而非 `null`（否则重蹈覆辙）。
- 返回对象的方法：若返回类型自身也适用Null对象模式，则返回其对应的Null对象。

### 与多态的关系

Null对象模式本质上是多态（Polymorphism）的一种应用——将"空"行为封装为一个合法子类型，让类型系统替代程序员完成"是否为空"的决策。以下 Java 代码展示了对比：

```java
// 重构前：每次使用都需要null检查
if (logger != null) {
    logger.log("操作完成");
}

// 重构后：logger要么是ConsoleLogger，要么是NullLogger
logger.log("操作完成"); // 直接调用，无需判断
```

当 `logger` 被赋值为 `new NullLogger()` 时，调用 `log()` 安全执行且无副作用，代码行数从2行降为1行，且消除了一个可能因疏忽遗漏检查而导致的隐患。

---

## 实际应用

**日志系统的可选注入**：许多框架允许用户不配置日志组件。若系统默认将 `logger` 字段初始化为 `NullLogger` 实例而非 `null`，则业务代码中所有 `logger.log(...)` 调用无需防御性判断，用户配置了真实Logger时正常输出，未配置时静默跳过。

**游戏开发中的空角色**：在角色扮演游戏中，某个槽位（如副手武器槽）可能为空。传统做法需要在每帧更新、渲染、碰撞检测时都判断该槽位是否有武器。引入 `EmptyWeapon` 作为Null对象后，其 `attack()` 方法返回0伤害，`render()` 方法不绘制任何内容，主游戏循环无需特殊处理空槽位。

**数据库查询结果**：当查询"用户的当前订阅计划"可能返回无结果时，可返回 `FreeTrialPlan`（一个Null对象），其 `getMaxStorage()` 返回0，`isPremium()` 返回 `false`，调用方可以直接使用查询结果而无需先判断是否为 `null`。

---

## 常见误区

**误区一：Null对象等同于把null检查搬进Null对象内部**
有些开发者实现Null对象时，在其方法内部仍然写了逻辑判断或异常处理，这偏离了该模式的本意。Null对象的方法应当是无条件的静默执行——方法体要么为空，要么直接返回固定的安全默认值，不包含任何 `if` 分支。

**误区二：所有返回值一律返回null**
在Null对象的方法中，若返回类型是一个对象，错误的实现会直接 `return null`，这会让调用方的下一步操作重新面临 `NullPointerException`，完全违背了引入该模式的目的。正确做法是返回该类型对应的Null对象实例，或者返回空集合、零值等语义明确的安全值。

**误区三：Null对象可以替代所有null的使用场景**
该模式适用于"不存在该对象时应静默跳过操作"的场景，但不适用于"必须知道对象是否存在并做出不同决策"的场景。例如，若业务逻辑需要区分"用户有地址"与"用户没有地址"来分别执行不同操作，此时强行使用Null对象会隐藏这一关键区别，导致业务逻辑出错。Java 8 的 `Optional<T>` 和 Kotlin 的可空类型（`T?`）是此类场景更合适的工具。

---

## 知识关联

**与策略模式（Strategy Pattern）的关系**：Null对象模式在结构上是策略模式的特例——Null对象就是一个"什么都不做"的策略实现。理解策略模式中接口与实现类的分离方式，有助于正确定义Null对象所实现的接口边界。

**与工厂方法的配合**：通常建议通过工厂方法或依赖注入容器来决定返回真实对象还是Null对象，而不是在业务代码中直接 `new NullXxx()`，这样可以集中管理"空"语义的分配逻辑。

**与 Optional 的比较**：`Optional<T>`（Java 8 引入）和 Null对象模式都致力于消除裸露的 `null`，但方向相反：`Optional` 强制调用方在使用前显式处理"可能为空"的情况（通过 `.orElse()`、`.map()` 等），而Null对象模式则让调用方完全感知不到"空"的存在。两者适用场景不同，并非谁取代谁的关系。