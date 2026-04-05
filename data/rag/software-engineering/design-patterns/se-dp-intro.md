---
id: "se-dp-intro"
concept: "设计模式概述"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 1
is_milestone: true
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "reference"
    title: "Design Patterns: Elements of Reusable Object-Oriented Software"
    author: "Gamma, Helm, Johnson, Vlissides (GoF)"
    year: 1994
    isbn: "978-0201633610"
  - type: "reference"
    title: "Head First Design Patterns"
    author: "Eric Freeman, Elisabeth Robson"
    year: 2004
    isbn: "978-0596007126"
  - type: "reference"
    title: "Refactoring: Improving the Design of Existing Code"
    author: "Martin Fowler"
    year: 1999
    isbn: "978-0201485677"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 设计模式概述

## 概述

设计模式（Design Pattern）是软件工程中针对反复出现的设计问题所总结出的**可复用解决方案模板**。它不是可以直接运行的代码，而是描述在特定上下文中如何解决某类设计问题的结构性方案。设计模式的价值在于将专家级的设计经验提炼为标准词汇，使开发者能够高效沟通并规避已知的设计陷阱。

1994年，Erich Gamma、Richard Helm、Ralph Johnson、John Vlissides四人（合称"四人帮"，Gang of Four，简称GoF）出版了《Design Patterns: Elements of Reusable Object-Oriented Software》，系统整理了**23种经典设计模式**。这一著作奠定了面向对象设计模式的学科基础，书中的模式至今仍是行业标准参考。值得注意的是，设计模式的思想源头可追溯到建筑师Christopher Alexander在1977年提出的"模式语言"概念，GoF将其引入了软件领域。

在工程实践中，设计模式解决的是**接口设计、对象职责划分与系统扩展性**三类核心问题。一个未经模式思考的系统往往在需求变更时暴露出类爆炸、强耦合或修改涟漪效应等问题，而正确应用设计模式可将这些风险控制在可预见范围内。

---

## 核心原理

### GoF 23种模式的三大分类

GoF将23种模式按**意图**分为三类，而非按语法特征分类：

| 类别 | 模式数量 | 解决问题 | 典型代表 |
|------|---------|---------|---------|
| **创建型**（Creational） | 5种 | 控制对象的创建方式与时机 | 单例、工厂方法、抽象工厂 |
| **结构型**（Structural） | 7种 | 组织类与对象的组合关系 | 适配器、装饰器、代理 |
| **行为型**（Behavioral） | 11种 | 定义对象间的通信与职责分配 | 观察者、策略、命令 |

创建型模式将"如何创建对象"的逻辑从使用逻辑中分离；结构型模式通过组合而非继承来扩展功能；行为型模式专注于算法封装与对象协作协议。

### 模式的四要素描述法

GoF规定每个模式必须包含四个描述要素：**模式名称（Pattern Name）、问题（Problem）、解决方案（Solution）、效果（Consequences）**。这套四要素描述法是设计模式区别于普通编程技巧的重要标志——它强制要求说明模式的适用条件和权衡取舍，而不仅是提供代码结构。例如，单例模式的"效果"部分必须明确指出它会引入全局状态，导致单元测试困难。

### 模式选择的适用场景判断

选择设计模式的核心依据是**变化点定位**，即识别系统中哪些维度会发生变化：
- 若**创建逻辑复杂或需要延迟**，选创建型模式（如工厂模式处理多类型对象实例化）
- 若**接口不兼容或需要透明扩展**，选结构型模式（如适配器处理第三方库接口差异）
- 若**算法或行为需要运行时切换**，选行为型模式（如策略模式替换条件分支链）

这一判断框架与SOLID原则直接对应：开闭原则（OCP）要求对扩展开放，这正是行为型模式中策略、模板方法等模式的设计动机。

---

## 实际应用

**Java标准库中的模式实例**是理解设计模式真实用途的最佳案例。`java.util.Calendar.getInstance()` 使用了工厂方法模式；`java.io.InputStream` 的各种包装类（如`BufferedInputStream`）是装饰器模式的教科书实现；`java.util.Observer`接口（Java 9前）直接对应观察者模式。

**Spring框架中的模式应用**更加密集：IoC容器本质上是工厂模式与依赖注入的结合，`ApplicationContext` 使用了单例作用域管理Bean；Spring AOP使用了代理模式动态织入横切逻辑；`JdbcTemplate` 使用模板方法模式固定数据库操作流程，留出具体SQL供子类定义。

在**微服务架构**中，断路器（Circuit Breaker）可视为状态模式的工程应用——系统在"关闭/开启/半开"三种状态间转换，每种状态对应不同的请求处理行为，这与GoF状态模式的结构完全吻合。

---

## 常见误区

**误区一：将设计模式视为必须强制套用的规范**
设计模式是"在复杂度达到阈值时"的解决方案，而非默认编码规范。对一个只有两种支付方式的简单系统强行引入策略模式，反而增加了不必要的类数量和间接层。GoF原书明确指出："如果问题不存在，就不要应用模式。"过度设计（Over-engineering）与不用模式同样有害。

**误区二：混淆模式分类导致选型错误**
常见错误是将工厂方法模式（属于创建型）与模板方法模式（属于行为型）混淆，两者都使用"父类定义框架，子类实现细节"的结构，但工厂方法的意图是**延迟对象创建**，模板方法的意图是**固定算法骨架**。混淆分类会导致用错模式、解决不了真实问题。

**误区三：忽视反模式（Anti-Pattern）的识别价值**
反模式与设计模式同等重要。1998年，AntiPatterns一书记录了软件开发中常见的失败模式，如"大泥球"（Big Ball of Mud，缺乏清晰架构的系统）、"神类"（God Class，一个类承担过多职责）和"黄金锤"（Golden Hammer，用同一种熟悉的技术解决所有问题）。识别反模式是应用设计模式的前置能力，因为反模式正是设计模式试图预防的问题形态。

---

## 知识关联

**前置概念：SOLID原则**为设计模式提供了判断依据。单一职责原则（SRP）解释了为何命令模式要将请求封装为对象；依赖倒置原则（DIP）是工厂模式和策略模式能够实现的数学基础——依赖抽象而非具体实现，才使替换成为可能。不理解SOLID，就无法判断某个模式是否解决了真实问题还是制造了复杂度。

**后续概念展开路径**：三类23种模式形成学习树状结构。**单例模式**是最简单的创建型模式，用于理解"控制实例化"思想，但也因引入全局状态而频繁成为反模式案例，是学习创建型模式的争议性起点；**工厂模式**（包含简单工厂、工厂方法、抽象工厂三个变体）是创建型模式中应用最广泛的一族，直接体现DIP原则的落地；**观察者模式**则打开行为型模式的学习通道，其发布-订阅变体是现代事件驱动架构和响应式编程（RxJava、Reactor）的直接理论来源。