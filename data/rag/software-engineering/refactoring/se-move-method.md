---
id: "se-move-method"
concept: "移动方法/字段"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["方法"]

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
updated_at: 2026-03-26
---



# 移动方法/字段

## 概述

移动方法（Move Method）和移动字段（Move Field）是两种紧密相关的重构手法，专门用于修复代码中的**Feature Envy（依恋情结）**气味——即一个方法或字段过度使用另一个类的数据，而非其所在类的数据。Martin Fowler 在1999年出版的《重构：改善既有代码的设计》中将这两种手法列为最基础的重构操作，编号分别为 Move Method 和 Move Field。

这两种手法解决的根本问题是**职责错位**：当方法A定义在类X中，但它的函数体90%的时间都在调用类Y的 getter 方法时，这个方法本质上"属于"类Y。将方法移过去后，原来的跨类调用变成了对本类字段的直接访问，消除了不必要的耦合。移动字段的动机类似——字段应当住在使用它最频繁的那个类里。

这两种手法的重要性在于它们是降低类间耦合、提高内聚性最直接的工具。正确完成之后，每个类都只持有与自身职责相关的数据和行为，后续的其他重构（如提取类、内联类）才能有更好的施力点。

## 核心原理

### Feature Envy 的识别标准

判断是否需要移动方法，有一条具体的经验规则：如果一个方法内部对**外部类的调用次数多于对本类成员的调用次数**，则应考虑移动。例如下面这段 Java 代码：

```java
// 定义在 Order 类中，却大量使用 Customer 的数据
double getDiscountedPrice() {
    double base = customer.getMemberLevel() * customer.getBaseRate();
    double cap  = customer.getMaxDiscount();
    return Math.min(base, cap) * this.quantity;
}
```

这里方法访问了 `customer` 的3个成员，却只访问了 `Order` 自身的1个字段 `quantity`，符合移动到 `Customer` 类的条件。

### 移动方法的操作步骤

移动方法的规范流程共五步：
1. **检查源类中该方法的所有调用点**，确认是否有多态（子类覆盖），若有则不宜直接移动；
2. 在**目标类**中创建同名方法，将方法体复制过去，并调整对原类字段的引用（改为通过参数传入源对象，或在目标类中直接读取）；
3. 在**源类**中将原方法体替换为一行委托调用，如 `return targetObject.getDiscountedPrice(this);`；
4. 运行全部测试，确认行为不变；
5. 若源类中没有其他代码引用原方法，**删除委托方法**，并更新所有调用处直接指向目标类。

### 移动字段的操作步骤与注意事项

移动字段比移动方法更需谨慎，因为字段往往被多处直接读写。具体步骤：
1. 若字段可见性不是 `private`，先**封装成 getter/setter**（即先做"封装字段"重构）；
2. 在目标类中**新建同类型字段**并添加访问方法；
3. 修改源类的 getter/setter，改为**委托给目标类**的对应方法；
4. 逐步将源类中直接访问该字段的代码改为通过委托方法访问，每步之后运行测试；
5. 所有引用都改完后，**删除源类中的字段定义**和委托方法。

移动字段时必须注意：若字段被源类的构造函数赋值，还需同步修改构造函数或初始化逻辑，否则会产生空引用错误。

### 与提取方法的配合关系

移动方法经常在**提取方法**之后执行。一个大方法被提取为若干小方法后，往往能清晰看出某些小方法只依赖特定子对象的数据，此时再做移动方法才能精准发力。直接对未提取的大方法做移动，会把所有依赖一并拖入目标类，反而造成新的混乱。

## 实际应用

**电商系统中的运费计算**：假设 `ShoppingCart` 类中有一个方法 `calculateShipping()`，它完全依赖 `DeliveryAddress` 对象的省份、城市、是否偏远地区等字段来计算运费，而不使用购物车自身的任何数据。正确做法是将该方法移动到 `DeliveryAddress` 类，并在 `ShoppingCart` 中保留一行 `return address.calculateShipping()` 的委托。

**账单系统中的税率字段**：若 `Invoice`（发票）类持有 `taxRate` 字段，但实际上 `TaxRule` 类有七八个方法都在读取这个字段，而 `Invoice` 自身只在打印时用一次，则应将 `taxRate` 字段迁移到 `TaxRule` 类，让数据住在真正频繁使用它的地方。

**IDE 工具支持**：IntelliJ IDEA 通过快捷键 `F6` 直接触发 Move 重构对话框，Eclipse 则在右键菜单的 Refactor → Move 中提供相同功能，两者均会自动检测并更新所有引用，大幅降低手动操作出错的概率。

## 常见误区

**误区一：只移动方法，不同步检查相关字段**。移动方法后，如果被移入的方法现在直接访问目标类的多个字段，但还有一个辅助字段仍留在源类，就会造成新的 Feature Envy（方向反转）。正确做法是移动方法后立即用同样的 Feature Envy 准则重新评估相关字段。

**误区二：忽视继承层级，强行移动被子类覆盖的方法**。若源类的子类覆盖了即将移动的方法，贸然移动会破坏多态契约，导致运行时行为错误。遇到此情况应先通过"以多态取代条件表达式"或重新设计继承结构，再考虑是否移动。

**误区三：把"方法调用了另一个类的方法"等同于 Feature Envy**。如果方法调用的是工具类（如 `Math.sqrt()`、`Collections.sort()`）或设计上就是跨类协调的门面方法，则不构成 Feature Envy，不应移动。Feature Envy 特指方法对某个**具体领域对象**的数据过度依赖，而非泛指所有跨类调用。

## 知识关联

**前置知识——提取方法**：移动方法的对象必须是粒度合适的独立方法，而非混杂了多个职责的大块代码。在做移动之前，通常需要先用提取方法将代码切分清楚，确保被移动的方法只做一件事，才能判断它的数据依赖属于哪个类。

**延伸到类级别的重构**：熟练运用移动方法和移动字段之后，会自然遇到需要将多个相关方法和字段一起迁移的情况，这便引出了**提取类（Extract Class）**手法——当一批字段和方法构成独立的职责簇时，应将它们整体提取为新类，而非逐个移动。移动方法/字段可视为提取类的原子操作。

**度量指标**：成功执行移动方法/字段后，可用**传出耦合（Efferent Coupling, Ce）**指标衡量效果——源类的 Ce 值应当下降，目标类的方法内聚度（LCOM，缺乏内聚度量）应当提高，这两个指标的改善是重构正确完成的量化信号。