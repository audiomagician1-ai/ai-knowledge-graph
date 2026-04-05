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
quality_tier: "A"
quality_score: 79.6
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


# 访问者模式

## 概述

访问者模式（Visitor Pattern）是一种行为型设计模式，其核心思想是将**数据结构**与**作用于该结构上的操作**彻底分离。当你需要对一个由多种类型节点组成的对象结构执行许多不同且不相关的操作时，访问者模式允许你在不修改这些节点类的前提下，通过新增访问者类来扩展操作。

访问者模式由Erich Gamma等四人（GoF）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归纳，属于"四人帮"总结的23种经典模式之一。该模式的提出背景是编译器开发领域——抽象语法树（AST）由几十种不同节点类型（如赋值节点、函数调用节点、变量节点等）组成，而编译器需要对同一棵树执行类型检查、代码生成、常量折叠等十几种不同的遍历操作，如果每种操作都要修改所有节点类，维护成本极高。

访问者模式真正解决的工程问题是**开闭原则的非对称性**：当对象结构（Element类体系）稳定、而操作（Visitor类体系）频繁变化时，该模式允许无限扩展操作而不触碰任何已有Element代码。反之，若频繁新增Element类型，则访问者模式的维护成本极高，因为每个已有Visitor都需要新增对应的`visit`方法。

---

## 核心原理

### 双分派机制

访问者模式最关键的技术基础是**双分派（Double Dispatch）**。普通方法调用是单分派——运行时仅根据接收方对象的实际类型决定调用哪个方法。而访问者模式通过两次分派，使最终执行的操作同时依赖**访问者的类型**和**被访问元素的类型**。

第一次分派：客户端调用 `element.accept(visitor)`，根据`element`的实际类型（如`ConcreteElementA`）确定调用哪个`accept`方法。

第二次分派：在`ConcreteElementA.accept()`内部调用 `visitor.visitConcreteElementA(this)`，根据`visitor`的实际类型（如`ConcreteVisitor1`）确定调用哪个`visit`重载方法。

两次分派的最终结果是：`ConcreteVisitor1` 与 `ConcreteElementA` 的组合确定了具体行为，即一张 `访问者类型 × 元素类型` 的操作矩阵在运行时被精确索引。

### 参与者与结构

访问者模式包含五类参与者：

- **Visitor**（抽象访问者）：为每种ConcreteElement声明一个`visit`方法，如 `visitElementA(ElementA e)` 和 `visitElementB(ElementB e)`。
- **ConcreteVisitor**（具体访问者）：实现全部`visit`方法，每个ConcreteVisitor代表一种独立操作（如序列化、打印、统计）。
- **Element**（抽象元素）：声明`accept(Visitor v)`方法。
- **ConcreteElement**（具体元素）：实现`accept`，内部固定写 `v.visitConcreteElement(this)`。
- **ObjectStructure**（对象结构）：持有Element集合，提供遍历入口，通常是组合模式构成的树或列表。

以Java伪代码表示`accept`的标准实现：

```java
class ConcreteElementA implements Element {
    public void accept(Visitor v) {
        v.visitConcreteElementA(this); // 第二次分派在此发生
    }
}
```

### 操作扩展而不修改数据结构

若需要新增一种对AST的"代码美化"操作，只需新建 `PrettyPrintVisitor` 类并实现所有节点类型对应的`visit`方法即可，`AssignmentNode`、`CallNode`等任何已有节点类**零改动**。这与直接在节点类中添加`prettyPrint()`方法的做法截然相反——后者会造成每次新增操作都需修改数十个节点类，违反开闭原则。

---

## 实际应用

**编译器/解释器的AST处理**是访问者模式最经典的工业级应用。Java编译器工具链中的`javax.lang.model`以及LLVM的Pass框架均采用访问者模式对语法/IR节点进行多遍处理。每个编译器Pass（类型推断、死代码消除、内联优化）都是一个独立的Visitor，互不干扰。

**文档对象模型导出**同样常见：一个由`Paragraph`、`Table`、`Image`、`Heading`等节点组成的文档树，可以定义`HtmlExportVisitor`、`PdfExportVisitor`、`WordCountVisitor`三个访问者，分别输出HTML、PDF和字数统计，而文档节点类本身无需感知导出格式。

**静态代码分析工具**（如Checkstyle、PMD）将每条检查规则实现为独立的Visitor，扫描同一棵Java AST。新增检查规则只需新增一个Visitor类，不影响已有规则的运行。

---

## 常见误区

**误区一：认为`accept`方法可以用instanceof替代双分派**。部分开发者会在单一方法中用`if (element instanceof ConcreteElementA)`来分支处理，这确实能实现功能，但它是单分派模拟，当新增Element类型时编译器不会强制要求更新分支逻辑，容易遗漏，而双分派方案中新增`ConcreteElementB`后若忘记在Visitor接口添加`visitConcreteElementB`，所有ConcreteVisitor的编译会立即报错，提供了编译期安全保障。

**误区二：认为访问者模式适用于元素类型经常变动的场景**。访问者模式的代价是：每次新增一种Element类型，就必须修改**所有已有的Visitor接口和全部ConcreteVisitor实现**。若一个系统有10个ConcreteVisitor，新增1种Element类型意味着至少10处改动。因此该模式只适合**Element类型稳定、操作类型多变**的场景，频繁新增节点类型的系统应考虑使用策略模式或直接在元素类中定义操作。

**误区三：混淆访问者模式与迭代器模式的职责**。迭代器模式只解决"如何遍历集合中的每个元素"，它不关心对元素执行什么操作。访问者模式则假定遍历已由ObjectStructure或组合结构负责，它解决的是"对遍历到的每个元素，如何根据元素类型和访问者类型执行不同操作"。两者经常配合使用，但职责不重叠。

---

## 知识关联

访问者模式与**组合模式**天然配对：组合模式构建树形Element结构，访问者模式在该树上执行多态操作，AST就是这种配合的典型体现。

**双分派**是理解访问者模式绕不开的前置概念：在只支持单分派的语言（如Java、C#）中，访问者模式通过`accept`+`visit`的两步调用手动实现了双分派；而在原生支持多分派的语言（如Julia、Common Lisp的CLOS）中，访问者模式可以被多方法机制直接替代，无需`accept`样板代码。

访问者模式与**策略模式**的核心区别在于：策略模式用一个算法替换另一个算法，针对单一操作；访问者模式处理的是跨越多种类型的操作矩阵，一个Visitor封装的是对整个类型体系的一套完整操作。在扩展维度上，策略模式扩展算法实现，访问者模式扩展操作种类。