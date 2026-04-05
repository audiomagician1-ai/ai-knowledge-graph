---
id: "se-inline-refactor"
concept: "内联重构"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["简化"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 内联重构

## 概述

内联重构（Inline Refactoring）是一类重构手法，其目的是消除不必要的间接层，将过度抽象的代码合并回调用点，使代码更加直接、清晰。与"提取方法"相反，内联重构执行的是逆向操作：当一个方法、变量或类的抽象层级不再带来可读性或可维护性收益时，将其内容直接展开到使用处并删除该中间层。

内联重构在 Martin Fowler 1999 年出版的《重构：改善既有代码的设计》（Refactoring: Improving the Design of Existing Code）中被系统化整理，其中"内联方法"（Inline Method）、"内联临时变量"（Inline Temp）和"内联类"（Inline Class）均被列为独立的重构手法。Fowler 的核心观点是：抽象本身有成本，当一个方法的函数体与其名称同样清晰时，这层命名抽象就成了多余的噪音。

内联重构在软件工程实践中的价值体现在两个方面：一是清除"方法体比方法名更能说明意图"的冗余包装；二是作为更大规模重构的中间步骤，例如在将策略模式简化为直接逻辑之前，需要先内联若干委托方法。

---

## 核心原理

### 内联方法（Inline Method）

内联方法适用于这样的情形：一个方法的全部实现只有 1-3 行，且其方法名并不比方法体更具表达力。操作步骤为：找到该方法的所有调用点，将方法体逐一替换到调用处，最后删除原方法定义。

典型案例如下：

```java
// 重构前
int getRating() {
    return moreThanFiveLateDeliveries() ? 2 : 1;
}
boolean moreThanFiveLateDeliveries() {
    return numberOfLateDeliveries > 5;
}

// 重构后（内联 moreThanFiveLateDeliveries）
int getRating() {
    return numberOfLateDeliveries > 5 ? 2 : 1;
}
```

`moreThanFiveLateDeliveries()` 被内联后，逻辑一目了然，减少了一次不必要的跳转。

### 内联临时变量（Inline Temp）

当一个临时变量仅被赋值一次，且其名称并不比右侧表达式更清晰时，应将该变量内联。公式可表示为：

> 若 `T = expr`，且 T 只在后续出现一次或其名称无额外语义，则以 `expr` 直接替换对 T 的引用。

例如：

```python
# 重构前
base_price = order.base_price()
return base_price > 1000

# 重构后
return order.base_price() > 1000
```

内联临时变量的常见触发点是它阻碍了进一步的"以查询取代临时变量"重构，此时先执行内联能打通后续步骤。

### 内联类（Inline Class）

内联类用于处理一个类几乎不做任何事情、职责已萎缩到只剩少量字段和方法的情形。Fowler 建议：将该类的全部功能移入另一个与其最紧密协作的类中，然后删除原类。这与"提取类"重构直接互为逆操作。判断标准是：该类不再有独立演化的理由，保留它只会增加阅读时的层级跳转次数。

---

## 实际应用

**场景一：重构遗留代码中的过度委托链**

在遗留系统中，常见如下形式的委托链：`A.getB().getC().getValue()`，其中 `getB()` 和 `getC()` 的存在只是历史架构的残留，并不体现真实的领域边界。内联这两层中间方法后，可直接访问 `A.value`，减少了调用栈深度和测试时的 Mock 层数。

**场景二：简化状态标志方法**

当一个布尔方法如 `isEligible()` 的内部实现仅为 `return age >= 18 && hasLicense`，且该方法只在一处被调用时，将其内联到调用点使条件判断一目了然，而不必跳转到方法定义处才能理解真正的判断标准。

**场景三：为替换条件逻辑做铺垫**

在用多态替换 `switch/if-else` 链之前，通常需要先内联散布在各分支中的单行辅助方法，确保每个分支的逻辑集中可见，然后才能识别出哪些行为可以提升到子类中。

---

## 常见误区

**误区一：将内联方法等同于"代码变差了"**

许多开发者受"单一职责"和"小函数"原则影响，认为内联必然降低代码质量。实际上，当方法名与方法体的语义完全重叠时，这层抽象是零收益的。内联后代码变短并不代表设计退步，判断标准是抽象是否在传递超出字面量的信息。

**误区二：对有多个调用点的方法也强行内联**

内联方法的前提条件是该方法没有多态行为（即不被子类重写），且调用点数量可控。若一个方法有 20 处调用点，内联后代码重复量激增，违背了 DRY（Don't Repeat Yourself）原则。Fowler 明确指出：若方法被子类重写，则不应执行内联方法重构。

**误区三：混淆内联临时变量与删除有意义的中间变量**

内联临时变量只针对"纯透明"的中间量，即该变量对读者理解没有额外帮助。若临时变量名如 `discountedPriceAfterTax` 包含了右侧表达式无法直接传达的业务语义，则不应内联，否则会损害可读性。

---

## 知识关联

**与提取方法的关系**：内联方法与提取方法（Extract Method）互为逆操作。在实际重构流程中，两者经常交替使用：先提取方法以隔离变化点，再在职责重组后内联多余的中间层。掌握何时提取、何时内联是判断抽象粒度的核心技能。

**与移动方法/字段的关系**：当需要将一个方法移动到更合适的类时，若原方法只是简单地转发调用（Forwarding Method），可先内联原方法再在目标类中重新提取，避免保留无实质逻辑的转发壳。

**通向替换条件逻辑**：内联重构是实施"以多态替换条件表达式"（Replace Conditional with Polymorphism）的常见前置步骤。在识别出可多态化的条件分支后，往往需要先将分散在辅助方法中的判断条件内联到主方法体，使分支结构整体可见，从而为提取子类行为创造条件。