---
id: "se-extract-class"
concept: "提取类"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["类"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 提取类

## 概述

提取类（Extract Class）是一种重构手法，专门用于解决"上帝类"（God Class）问题——即一个类承担了过多职责，导致代码膨胀、难以维护。其核心操作是：将原类中某一组紧密相关的字段和方法，迁移到一个新创建的独立类中，并在原类中保留对新类的引用。这一手法由 Martin Fowler 在1999年出版的《重构：改善既有代码的设计》一书中正式命名和系统化描述，编号为第149页的重构条目。

上帝类是一种典型的代码异味，常见症状是一个类拥有超过20个字段或30个方法，且这些成员并非都围绕同一个业务概念聚焦。提取类的目标是恢复单一职责原则（SRP），使每个类只代表一个清晰的业务概念。例如，一个 `Person` 类同时持有个人信息和联系电话的格式化逻辑，就应将电话相关字段和方法提取为独立的 `TelephoneNumber` 类——这正是 Fowler 书中使用的经典示范案例。

提取类之所以重要，在于它直接降低了类的圈复杂度（Cyclomatic Complexity），使单元测试的覆盖范围更小、更精准。一个经过提取类重构的系统，其类的平均方法数往往从15+降至5-8个，代码可读性和可测试性显著提升。

## 核心原理

### 识别需要提取的职责群

执行提取类之前，必须找出"职责群"——即字段和方法之间的内聚关系。判断标准是：如果类中某个子集的字段和方法彼此频繁交互，而与类中其他成员交互较少，就构成一个独立的职责群，适合被提取为新类。

具体信号包括：字段名称带有共同前缀（如 `phonePrimary`、`phoneSecondary`、`phoneAreaCode`），或一组方法只操作类中的某几个特定字段而不碰其余字段。当你发现某几个字段被删除后，类仍然"逻辑完整"，那些被删的字段就是提取候选。

### 提取的标准步骤

Fowler 描述的提取类操作分为六步：
1. **决定如何分割**：确定新类名称和要迁移的字段、方法清单；
2. **创建新类**：建立空的目标类；
3. **建立引用关系**：在原类中实例化新类，保存为字段（通常是 `private final`）；
4. **逐一迁移字段**：使用"移动字段"（Move Field）手法，每次迁移后运行测试；
5. **逐一迁移方法**：使用"移动方法"（Move Method）手法，每次迁移后运行测试；
6. **审查接口**：检查是否可以将新类对外暴露，或保持为原类的私有实现。

迁移顺序至关重要：应先迁移字段，再迁移方法，因为方法依赖字段，若方法先移动会产生临时编译错误。

### 新类的引用模式

提取后，原类对新类的引用有两种典型模式：

**聚合模式（Association）**：原类持有新类的对象引用，新类可以独立存在于原类之外。例如 `Order` 类提取出 `ShippingAddress` 类后，`ShippingAddress` 对象可以被多个 `Order` 共享。

**组合模式（Composition）**：新类的生命周期完全依附于原类，不对外暴露。例如 `BankAccount` 提取出 `InterestCalculator` 类，后者仅作为前者的内部计算助手，不向外部直接提供访问。

选择哪种模式取决于新类是否拥有独立的业务语义。若新类仅是原类的实现细节，使用组合并将新类设为包级私有（package-private）；若新类代表独立的领域概念，使用聚合并提供公共 API。

## 实际应用

**案例1：用户类拆分**

一个电商系统中的 `User` 类拥有字段：`id`、`username`、`passwordHash`、`email`、`street`、`city`、`province`、`postalCode`，以及方法 `formatAddress()`、`validateAddress()`、`hashPassword()`。识别出 `street`、`city`、`province`、`postalCode`、`formatAddress()`、`validateAddress()` 构成一个职责群，应提取为 `Address` 类。提取后，`User` 类通过 `private Address shippingAddress` 字段引用 `Address` 对象，原有的地址相关测试只需针对 `Address` 类编写，用例数量减少约40%。

**案例2：发票类拆分**

财务系统中 `Invoice` 类同时处理发票元数据和税金计算逻辑（含多档税率公式 `tax = amount × rate × (1 - discount)`）。将税金计算相关的三个方法和两个税率字段提取为 `TaxCalculator` 类后，当税率规则变更时，只需修改 `TaxCalculator` 一个类，而不会影响发票打印、归档等其他逻辑。

## 常见误区

**误区1：提取粒度过细，产生"贫血类"**

有些开发者机械执行提取类，将只有1-2个字段和1个方法的微小职责群也单独提取成类，导致项目中出现大量只有 getter/setter 的贫血数据类。这与提取类的初衷相悖——新类应承担真正的行为逻辑，而非仅作数据容器。判断标准是：新类至少应包含2个以上非 getter/setter 方法，否则提取意义不大。

**误区2：混淆"提取类"与"提取子类"（Extract Subclass）**

提取类创建的是**独立平级的新类**，通过组合关系与原类协作；而提取子类创建的是原类的**子类**，通过继承关系扩展行为。当分离的是不同的行为变体（如 `FullTimeEmployee` vs `PartTimeEmployee`）时应用提取子类；当分离的是不同的数据和职责群时才使用提取类。两者不可混用，否则会引入不必要的继承层次。

**误区3：提取后忘记检查原类对新类的暴露程度**

许多人完成字段和方法迁移后就认为重构结束，却忽略了一个问题：原类是否通过公共方法向外界暴露了新类的引用。若外部代码可以直接拿到新类对象并修改其状态，封装就被破坏了。正确做法是审查原类的公共接口，决定是返回新类对象本身（适合聚合场景），还是只暴露委托方法（适合组合场景）。

## 知识关联

**前置概念**：提取类针对的是"上帝类"这一代码异味，因此理解代码异味的识别方法是执行提取类的前提。具体而言，"过大的类"（Large Class）异味的两个量化指标——超过200行的类体和超过20个实例变量——是触发提取类的直接信号。

**配套手法**：提取类通常需要与"移动字段"（Move Field）和"移动方法"（Move Method）组合使用，这两个手法是提取类内部步骤的具体实现。此外，提取类完成后往往需要"内联类"（Inline Class）的逆向验证——如果提取出的新类最终只有一两个方法且被单一调用，则说明提取过度，应通过内联类撤销操作。

**设计原则层面**：提取类是单一职责原则（SRP）在重构实践中最直接的体现，每一次成功的提取类操作都使系统的类层次更接近领域驱动设计（DDD）中的值对象（Value Object）或聚合（Aggregate）建模目标。
