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
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 内联重构

## 概述

内联重构（Inline Refactoring）是一种将过度抽象的间接层消除、把被引用的代码直接合并回调用处的重构手法。与"提取方法"相反，内联重构的方向是逆向的——它不是将代码段抽出成独立函数，而是将那些仅被调用一次、函数体本身比函数名更清晰、或者不必要的"传话筒"函数溶解回其调用者中。Martin Fowler 在《重构：改善既有代码的设计》（2018年第二版）中将 Inline Function、Inline Variable、Inline Class 归为同一类内联手法，统称为解除不必要的间接层。

内联重构的核心价值在于识别并修复"过度工程化"的问题。当代码中存在一个函数，其内部逻辑仅仅是将参数原封不动地转交给另一个函数，或者函数名与函数体的语义完全重合到无需进一步解释时，这个函数就是多余的间接层。例如，一个名为 `getRating()` 的方法，其函数体只有一行 `return moreThanFiveLateDeliveries() ? 2 : 1`，这种情况下直接内联可以减少跳转、降低阅读负担。

内联重构在以下两种典型场景中尤为重要：第一，在一段重构会话中，开发者需要先将分散的小函数内联合并，重新观察代码全貌，再重新切割成更合理的结构；第二，在发现某个间接层设计之初有其意义（如适配旧接口），但随着系统演进该意义已消失时，继续保留只会增加维护认知负荷。

## 核心原理

### 内联函数（Inline Function）

内联函数的操作步骤为：首先检查函数不是多态方法（即该函数没有被子类覆盖），然后找到所有调用该函数的地方，将调用语句替换为函数体的完整内容，最后删除原函数定义。以 JavaScript 为例：

```javascript
// 重构前
function reportLines(aCustomer) {
  return [getName(aCustomer), getCity(aCustomer)];
}
function getName(c) { return c.name; }

// 内联后
function reportLines(aCustomer) {
  return [aCustomer.name, aCustomer.city];
}
```

内联函数有一个关键前提条件：该函数的函数体必须能够在调用处安全替换，即不存在递归调用、不存在多处调用导致替换语义不一致等情况。如果一个函数被 15 处不同代码调用，每处上下文不同，贸然内联会引入重复代码，此时不应内联。

### 内联变量（Inline Variable）

当一个临时变量仅被赋值一次、且变量名并不比表达式本身更有说明性时，应使用内联变量消除该变量。公式上，将所有出现 `let x = expr; ... use(x)` 的模式替换为直接使用 `expr`。例如：

```javascript
// 重构前
const basePrice = order.basePrice;
return basePrice > 1000;

// 内联后
return order.basePrice > 1000;
```

这与提取变量（Extract Variable）形成严格的对称关系：提取变量将表达式命名以增加可读性，内联变量则在命名反而制造噪声时还原表达式。判断标准是：变量名是否提供了表达式本身不具备的语义信息。

### 内联类（Inline Class）

当一个类承担的职责已被其他类吸收，或者该类只剩下极少的功能（例如仅有两个字段和一个方法），应将其内联到另一个类中。Fowler 建议先使用"移动函数"和"移动字段"将该类的所有行为迁移到目标类，使源类变成空壳，再删除源类。这个手法常出现在将多个小类合并以准备后续按新维度重新划分职责的过程中。

## 实际应用

**场景一：委托函数过时**
某项目早期为兼容旧版 API，引入了一个 `ShippingCalculator` 类作为 `PricingEngine` 的委托层，仅将调用转发过去。半年后旧 API 下线，`ShippingCalculator` 变成纯粹的转发壳。此时对 `ShippingCalculator` 执行内联类操作，将其两个方法直接合并入 `PricingEngine`，删除委托类，消除了 30 行无意义的转发代码。

**场景二：重构前的准备步骤**
开发者需要重新设计一组功能函数的边界，但当前函数划分零碎且有多处交叉依赖。正确做法是先将相关函数全部内联到一个母函数中，形成一块完整可视的逻辑，再按新的职责边界重新提取方法。这个"先内联再提取"的往返操作是重构实践中的标准节奏。

**场景三：消除单行传话筒**
`isEligible()` 方法体只有 `return checkAge() && checkIncome()`，且 `isEligible` 这个名字并不比直接阅读条件表达式更清晰，调用点只有一处。将该调用点替换为 `checkAge() && checkIncome()` 并删除 `isEligible`，代码行数减少，逻辑更直观。

## 常见误区

**误区一：认为内联与提取方法是相互矛盾的**
许多初学者认为既然提取方法是好的实践，内联就是在"撤销好设计"。实际上两者服务于同一目标——代码清晰度，只是针对不同症状。提取方法解决"函数过长、逻辑混杂"，内联重构解决"函数过小、间接层多余"。Fowler 明确指出，内联是为了在重新提取前建立更好的起点，而非目的本身。

**误区二：凡是只有一行的函数都应该内联**
函数长度不是内联的判断依据。一个只有一行的函数，如果其函数名提供了比函数体更高层次的抽象（如 `isUserAuthenticated()` vs `user.token !== null && user.tokenExpiry > Date.now()`），则该函数有保留价值，不应内联。内联的判断依据是"函数名的语义价值是否超过函数体本身"，而非函数长短。

**误区三：内联多态方法**
对于在继承体系中被子类覆盖的方法，不能执行内联函数操作。如果将父类的虚方法内联到调用处，会破坏多态分发机制，使子类的覆盖实现永远不会被执行。在执行内联前，必须确认该函数在整个类层次结构中没有被覆盖，这是内联函数操作的硬性前提。

## 知识关联

内联重构与"提取方法"构成一对镜像操作，两者共同构成函数粒度调节的完整工具集。学习者在掌握提取方法之后学习内联重构，能够建立双向的重构直觉：知道何时应该把代码拆出去，也知道何时应该把代码收回来。

内联重构的决策直接依赖于对代码坏味道"Middle Man"（中间人）的识别——《重构》第三章中将"Middle Man"定义为一个类中超过一半的方法都在委托给其他类的状态，内联类正是消除 Middle Man 的标准手法。此外，内联变量与"提取变量"的取舍，与表达式的复杂度和命名的信息增益直接相关，这要求开发者对代码的可读性有准确的主观判断能力，而这种能力通常通过代码审查和结对编程实践来培养。
