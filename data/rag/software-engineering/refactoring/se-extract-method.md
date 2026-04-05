---
id: "se-extract-method"
concept: "提取方法"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: true
tags: ["方法"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 提取方法

## 概述

提取方法（Extract Method）是重构技术中最常用的手法之一，由Martin Fowler在1999年出版的《重构：改善既有代码的设计》中系统化整理并命名。其核心操作是：将一段独立完成特定任务的代码块，从原有方法中剪切出来，放入一个新的命名方法中，再以调用新方法的语句替换原有代码段。这一操作的结果是原方法变短、新方法获得一个能揭示意图的名称。

提取方法的直接动机来自于"长方法"这一代码异味。当一个方法超过10行时，就值得检视其内部是否存在可独立命名的逻辑段落；当方法超过30行时，几乎可以确定它承担了不止一个职责。提取方法通过拆分长方法来实现"单一职责原则"（SRP），使每个方法只回答一个问题或完成一件事，从而降低方法级别的认知复杂度。

## 核心原理

### 识别可提取代码块的标准

一段代码是否值得提取，判断的关键标准是"意图与实现的分离"：如果你需要为这段代码写一条注释才能让读者理解它在做什么，那它就是提取方法的候选目标。具体信号包括：连续的循环体、条件判断的整个分支、同一抽象层次上的重复代码片段，以及任何可以用一个动词短语完整描述的步骤（例如 `calculateTotalPrice()`、`validateUserInput()`）。

### 变量处理：局部变量与参数传递规则

提取方法的技术难点集中在局部变量的处理上，分为三种情形：

**第一种**：被提取代码块只读取某些局部变量，但不修改它们——这些变量直接作为新方法的**参数**传入，操作最简单。

**第二种**：被提取代码块修改了某个局部变量，且该变量在提取后的原方法中仍被使用——新方法需要**返回**该变量的值，并在调用处赋值。若同时需要修改多个变量，则应考虑是否应进一步提取为对象（此时提取类比提取方法更合适）。

**第三种**：被提取代码块修改了某个变量，但该变量在提取后不再被原方法使用——该变量可以成为新方法的局部变量，无需传参或返回，是最干净的情形。

Fowler建议：如果提取后需要返回两个以上的值，则应重新审视提取的边界是否合理，而不是强行使用元组或输出参数。

### 命名规则与抽象层次一致性

新方法的名称应描述"做什么"而非"怎么做"。例如，一段遍历订单列表并累加折扣价格的代码，应命名为 `calculateDiscountedTotal()` 而非 `loopOrdersAndSum()`。好的命名往往比代码本身更长，这是可以接受的。此外，提取后原方法体内所有语句应处于同一抽象层次：若原方法调用了 `renderHeader()`、`renderBody()`、`renderFooter()`，则不应在其中夹杂一行底层的字符串拼接逻辑，那行代码需要再次提取。

## 实际应用

**场景一：打印收据的长方法**

```java
// 重构前（30行混杂方法）
void printReceipt(Order order) {
    System.out.println("=== Receipt ===");
    double total = 0;
    for (Item item : order.getItems()) {
        total += item.getPrice() * item.getQuantity();
        System.out.println(item.getName() + ": " + item.getPrice());
    }
    if (order.hasMembership()) total *= 0.9;
    System.out.println("Total: " + total);
}

// 重构后：提取 printItemList() 和 calculateTotal()
void printReceipt(Order order) {
    printHeader();
    printItemList(order.getItems());
    System.out.println("Total: " + calculateTotal(order));
}
```

提取后，`printReceipt` 方法从混杂输出和计算逻辑，变为三行清晰表达收据结构的调用，读者无需阅读细节即可理解流程。

**场景二：IDE自动化提取**

IntelliJ IDEA、Eclipse等主流IDE均内置提取方法的快捷操作（IntelliJ为 `Ctrl+Alt+M`）。IDE会自动分析选中代码块的变量依赖关系，推断参数列表和返回值，大幅降低手动操作出错的风险。但IDE自动推断的方法名通常是 `extracted()`，开发者必须手动给出有意义的命名。

## 常见误区

**误区一：提取过细导致方法碎片化**

一些开发者将每1-2行代码都提取为独立方法，造成调用链过深，阅读时需要在多个方法间反复跳转，反而降低可读性。提取方法的粒度标准是"能否用一句话准确命名"，而非"行数最小化"。一个只有一行代码且名称与代码表意完全相同的方法（如 `getAge()` 内部只有 `return age;`）通常不需要进一步提取其他包装方法。

**误区二：提取方法等同于消除重复代码**

提取方法的首要目的是**提升可读性和揭示意图**，消除重复（DRY原则）是其附带效果而非主要目标。消除重复有专门的手法（如提取父类、模板方法模式），若将提取方法视为纯粹的去重工具，可能会为了复用而强行抽象出参数众多、职责模糊的公共方法，得不偿失。

**误区三：忽视提取后对原方法的影响**

提取方法后，原方法的可见性可能发生变化：如果被提取的方法只在一个类内部使用，应声明为 `private`；若原方法是 `synchronized` 方法，提取出的代码块中若包含共享状态访问，需要重新评估线程安全性，而不能假设提取操作是完全透明的。

## 知识关联

提取方法的前置知识是识别"代码异味"中的**长方法**和**注释驱动的代码段**——只有能够识别出哪些代码"值得一个名字"，才能正确划定提取边界。

提取方法之后自然引出**移动方法/字段**的需求：当提取出的新方法发现自己更多地依赖另一个类的数据时，就应将该方法移动到那个类中去。**内联重构**（Inline Method）是提取方法的逆操作，用于处理提取过度导致的碎片化问题，两者配合使用维持方法粒度的平衡。当提取方法的过程中发现需要同时提取多个相关方法和字段时，则升级为**提取类**操作，将相关职责整体迁移到新类中，形成完整的类级别单一职责。