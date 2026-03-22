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
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
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
---
# 设计模式概述

## 概述

设计模式（Design Patterns）是软件设计中**反复出现的问题的经过验证的解决方案模板**。这个概念由建筑师 Christopher Alexander 在 1977 年首次提出（*A Pattern Language*），后被 Gamma、Helm、Johnson、Vlissides 四人（合称 Gang of Four / GoF）引入软件工程，在 1994 年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中系统化为 23 种经典模式。

设计模式不是可以直接复制粘贴的代码，而是**描述问题-上下文-解决方案三元组的抽象方案**。正如 GoF 书中所述："每个模式描述了一个在我们的环境中反复出现的问题，以及该问题的解决方案的核心"（GoF, 1994, p.2）。

## 核心知识点

### 1. GoF 的三大分类

GoF 将 23 种模式按**目的（intent）**分为三类：

| 分类 | 目的 | 模式数 | 代表模式 | 解决的典型问题 |
|------|------|--------|---------|--------------|
| **创建型（Creational）** | 控制对象创建过程 | 5 | Singleton, Factory Method, Abstract Factory, Builder, Prototype | "如何创建对象而不硬编码具体类？" |
| **结构型（Structural）** | 组合类和对象形成更大结构 | 7 | Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight | "如何让不兼容的接口协同工作？" |
| **行为型（Behavioral）** | 定义对象间的通信方式 | 11 | Observer, Strategy, Command, State, Iterator, Template Method... | "如何让对象协作而不产生紧耦合？" |

**选择依据**：先问"我遇到的是创建问题、结构问题还是通信问题？"，这一步就能把候选范围缩小到 5-11 个。

### 2. 模式的四要素

GoF 定义每个模式包含四部分（GoF, 1994, p.3）：

1. **模式名称（Pattern Name）**：用 1-2 个词描述问题、方案和效果。命名本身就是设计词汇的扩展——当团队说"这里用 Observer"，所有人立即理解意图。
2. **问题（Problem）**：在什么场景下使用该模式。包括具体的上下文条件和约束（如"需要通知多个对象但不想硬编码依赖关系"）。
3. **解决方案（Solution）**：描述元素之间的关系、职责和协作方式。注意是抽象描述，不是具体实现。
4. **效果（Consequences）**：使用该模式的**权衡**（trade-offs）。每个模式都有代价——Singleton 方便全局访问但引入隐式依赖和测试困难；Observer 解耦但调试链条变长。

### 3. 适用场景判断框架

不是所有代码复用都需要设计模式。Martin Fowler 在《Refactoring》中建议的判断流程：

```
问题反复出现？ ─No→ 直接写最简方案（YAGNI）
       │Yes
       ↓
现有代码有 code smell？ ─No→ 现状可能已经够好
       │Yes
       ↓
smell 是否对应已知模式的 Problem？ ─Yes→ 考虑应用该模式
       │No
       ↓
先 Refactor 到更清晰的结构，再评估
```

**常见 code smells 与对应模式**：
- **Switch/case 爆炸** → Strategy 或 State
- **构造函数参数过多** → Builder
- **子类泛滥** → Decorator 或 Composite
- **跨模块依赖** → Observer 或 Mediator
- **遗留系统接口不兼容** → Adapter 或 Facade

### 4. 反模式（Anti-Patterns）

反模式是"看起来像好主意但系统性地导致坏结果的常见做法"。与设计模式形成对照学习效果极佳：

| 反模式 | 症状 | 根因 | 修正方向 |
|--------|------|------|---------|
| **God Object** | 一个类 3000+ 行，什么都做 | 职责未分离 | 拆分为多个 SRP 类 |
| **Singleton 滥用** | 到处 `getInstance()`，测试无法 mock | 把全局状态当捷径 | 改用依赖注入 |
| **Lava Flow** | 无人敢删的"可能有用的"死代码 | 缺乏文档和测试覆盖 | 写测试 → 安全删除 |
| **Golden Hammer** | 所有问题都用同一个模式解决 | 只熟悉一种方案 | 扩展模式知识面 |
| **Copy-Paste Programming** | 相同逻辑出现在 5+ 个地方 | 懒于抽象 | Template Method 或 Strategy |

### 5. 模式之间的关系

GoF 模式不是孤立的。常见组合：

- **Abstract Factory** 内部常用 **Factory Method** 来创建具体产品
- **Composite** + **Iterator** = 遍历树状结构
- **Strategy** 和 **State** 结构相似，区别在于意图：Strategy 选择算法，State 响应状态变化
- **Observer** + **Mediator** = 复杂事件系统（Unity 的事件系统就是这种组合）
- **Decorator** 和 **Proxy** 都包装了原对象，但 Proxy 控制访问，Decorator 增加行为

理解这些关系比死记 23 个模式的 UML 图更重要。

## 实践建议

1. **先学 5 个高频模式**：Singleton、Observer、Strategy、Factory Method、Decorator——覆盖大多数实际场景。
2. **从重构中学习**：不要在新项目中提前"设计"模式。写完简单代码，发现 smell 后再引入模式。GoF 自己说过："设计模式不应该在设计初期就应用"。
3. **用你的语言实践**：每学一个模式，用当前项目的语言（C++/Python/C#/TypeScript）实现一个最小可运行示例。
4. **画 UML 序列图**：比类图更能揭示模式的运行时行为。Observer 的类图看起来简单，但序列图能暴露通知链的复杂度。

## 常见误区

1. **模式崇拜**：为了用模式而用模式。经典反面教材——`AbstractSingletonProxyFactoryBean`（Spring 框架曾真实存在的类名）。如果简单 `if/else` 就能解决，不需要 Strategy。
2. **等同于架构**：设计模式是**类/对象级别**的解决方案（GoF 明确说明），不是系统架构（MVC、微服务属于架构模式，层级不同）。
3. **忽略语言特性**：Python 的函数是一等公民，很多 Strategy/Command 模式可以直接用函数引用替代类继承。Go 没有类继承，模式实现方式完全不同。
4. **23 种模式就是全部**：GoF 的 23 种只是起点。后续有 Enterprise Patterns（Fowler）、Game Programming Patterns（Nystrom）、Concurrency Patterns 等大量扩展。
5. **只看结构不看意图**：Strategy 和 State 的 UML 类图几乎一样，但解决完全不同的问题。模式的本质是**意图**，不是结构。

## 知识衔接

### 先修知识
- **SOLID 原则** — 设计模式是 SOLID 原则的具体实现工具。不理解 OCP（开闭原则），就无法理解 Strategy 为什么要抽取接口。

### 后续学习
- **单例模式** — 最简单但最容易被滥用的创建型模式
- **工厂模式** — 创建型模式的核心，理解多态创建
- **观察者模式** — 行为型模式的代表，事件驱动架构的基础

## 延伸阅读

- Gamma, E. et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley. ISBN 978-0201633610
- Freeman, E. & Robson, E. (2004). *Head First Design Patterns*. O'Reilly. ISBN 978-0596007126
- Nystrom, R. (2014). *Game Programming Patterns*. Genever Benning. [免费在线阅读](https://gameprogrammingpatterns.com/)
- Fowler, M. (1999). *Refactoring: Improving the Design of Existing Code*. Addison-Wesley. ISBN 978-0201485677
- Refactoring.Guru: [Design Patterns 交互式目录](https://refactoring.guru/design-patterns)
