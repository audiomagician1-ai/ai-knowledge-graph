---
id: "se-dp-visitor"
concept: "访问者模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 3
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.517
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 访问者模式

## 概述

访问者模式（Visitor Pattern）是一种行为型设计模式，允许在不修改已有数据结构类的前提下，向这些类添加新的操作。其核心思想是将数据结构与作用于数据结构上的操作分离，把操作逻辑封装在独立的"访问者"对象中，而非散落在各个数据节点类里。

访问者模式最早由 GoF（Gang of Four）在 1994 年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中正式收录。该书将其定义为："表示一个作用于某对象结构中各元素的操作，使你可以在不改变各元素的类的前提下定义作用于这些元素的新操作。"

访问者模式在编译器设计领域极为普遍——抽象语法树（AST）的节点类型相对固定（变量节点、表达式节点、语句节点等），但需要对 AST 施加多种操作（类型检查、代码生成、常量折叠、打印输出），若将每种操作都写进节点类，会导致节点类膨胀且违反单一职责原则。访问者模式将每种操作提取为一个独立的访问者类，使扩展新操作只需增加新类，无需触碰已有节点代码。

---

## 核心原理

### 双分派机制（Double Dispatch）

访问者模式的技术基础是**双分派**，这是区别于普通多态（单分派）的关键特征。

在单分派语言（如 Java、C++、Python）中，方法调用仅根据调用者的运行时类型决定具体执行哪个方法。若直接调用 `visitor.visit(element)`，编译器无法在运行时同时依据 `visitor` 的类型和 `element` 的类型分派到正确的重载版本。

双分派通过两步调用解决这一问题：

1. **第一次分派**：调用 `element.accept(visitor)`，根据 `element` 的实际类型（如 `NumberNode` 或 `AddNode`）调用对应的 `accept` 方法——这一步用单分派确定了元素类型。
2. **第二次分派**：在 `accept` 方法体内，调用 `visitor.visit(this)`，此时 `this` 的静态类型已知（就是该具体元素类），运行时再根据 `visitor` 的实际类型选择正确的 `visit` 重载版本——这一步确定了访问者类型。

```
element.accept(visitor)
  → ConcreteElement.accept(visitor)
      → visitor.visit(this)  // this 类型为 ConcreteElement
          → ConcreteVisitor.visit(ConcreteElement)
```

两次分派合力，实现了"同时依据两个对象的运行时类型做出决策"。

### 标准参与者结构

访问者模式包含以下 5 个角色：

- **Visitor（抽象访问者）**：为每个具体元素类型声明一个 `visit` 方法，如 `visitNumberNode(NumberNode n)` 和 `visitAddNode(AddNode n)`。
- **ConcreteVisitor（具体访问者）**：实现全部 `visit` 方法，每个具体访问者对应一种完整操作，如 `EvaluateVisitor`（求值）或 `PrintVisitor`（打印）。
- **Element（抽象元素）**：声明 `accept(Visitor v)` 接口。
- **ConcreteElement（具体元素）**：实现 `accept`，方法体只有一行 `v.visit(this)`。
- **ObjectStructure（对象结构）**：持有元素集合，负责遍历并让每个元素接受访问者。

### 开闭原则的非对称性

访问者模式对**操作扩展**满足开闭原则（对扩展开放，对修改关闭）：添加新的 `ConcreteVisitor` 完全不影响任何元素类。但对**元素类型扩展**则违反开闭原则：一旦新增一个 `ConcreteElement`，必须在抽象 `Visitor` 接口中添加对应的 `visit` 方法，进而修改所有已有的 `ConcreteVisitor` 实现类。这种非对称性决定了访问者模式适用的前提条件是**元素类层次稳定、操作种类频繁变化**。

---

## 实际应用

**Java 编译器 AST 处理**：LLVM 的 C++ 前端 Clang 使用 `RecursiveASTVisitor` 类，用户只需继承该类并重写感兴趣节点的 `VisitXxxDecl`/`VisitXxxStmt` 方法，即可在不修改 AST 节点定义的情况下实现代码分析、重构等操作。

**Java `javax.lang.model` API**：Java 注解处理器框架提供 `ElementVisitor<R, P>` 接口，其中 `R` 为返回类型，`P` 为附加参数类型，针对 `TypeElement`、`VariableElement`、`ExecutableElement` 等 8 种元素各有一个 `visit` 方法。注解处理工具通过实现该接口遍历程序元素，无需修改 JDK 内置的元素类。

**文档格式导出**：一个富文本文档的节点结构（段落、标题、表格、图片）相对稳定，但导出格式（HTML、Markdown、PDF、Word）会持续增加。使用访问者模式，每种导出格式对应一个访问者类，如 `HtmlExportVisitor` 和 `MarkdownExportVisitor`，增加新格式无需改动文档节点类。

---

## 常见误区

**误区一：认为 `accept` 方法可以简化或省略**。初学者有时试图在 `ObjectStructure` 中直接使用 `instanceof` 判断元素类型再调用对应 `visit` 方法，以为省去了 `accept`。这种做法破坏了双分派机制，将类型判断逻辑暴露在外部，且每次新增元素类型时都需修改遍历代码，反而丧失了访问者模式的全部设计收益。`accept` 方法虽然只有一行代码，但它是实现双分派不可缺少的一步。

**误区二：将访问者模式用于元素类型频繁变化的场景**。由于访问者模式的非对称开闭特性，当元素类数量不稳定（例如插件系统中数据节点类型由第三方扩展提供）时，强行使用访问者模式会导致每次新增元素类型都需要修改所有访问者实现，维护成本远高于直接在元素类中定义方法。正确判断标准是：若最近半年内元素类层次未曾修改，且操作种类已超过 3 种，才是引入访问者模式的合适时机。

**误区三：混淆访问者模式与迭代器模式**。迭代器模式只负责遍历集合，不携带针对元素的操作逻辑；访问者模式的核心价值在于将操作本身（求值、打印、类型检查）外置为独立对象，并通过双分派确保操作与元素类型的正确匹配。两者可以组合使用——`ObjectStructure` 内部可用迭代器遍历，但调用的是 `element.accept(visitor)` 而非普通的元素方法。

---

## 知识关联

访问者模式以**多态（Polymorphism）**为基础——没有方法重写和接口多态，`accept` 方法的第一次分派无从实现。同时，对函数重载（Overloading）的理解有助于解释为何单分派语言无法在一步调用中同时根据两个对象类型分派，从而说明为何需要双分派这一间接手段。

访问者模式与**组合模式（Composite Pattern）**高度配合：组合模式构建树形元素结构（如 AST、文件目录树、UI 组件树），而访问者模式则在该树上执行各种操作，`accept` 在父节点中递归调用子节点的 `accept`，自然实现树的深度优先遍历。

在函数式编程领域，访问者模式对应的概念是**代数数据类型（ADT）上的模式匹配**。Haskell 和 Scala 的 `case class` 加 `match` 表达式天然支持多类型分派，无需手动实现 `accept`，这从语言设计层面揭示了访问者模式本质上是对缺乏多分派能力的面向对象语言的一种补偿方案。