---
id: "se-refactor-patterns"
concept: "重构模式"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 3
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 重构模式

## 概述

重构模式（Refactoring to Patterns）是由Joshua Kerievsky于2004年在其同名著作《Refactoring to Patterns》中系统化提出的一套重构手法。它将Martin Fowler的基础重构技巧与GoF（Gang of Four）的23种设计模式结合起来，核心思想是：代码中已经存在的坏味道（bad smells）往往可以通过引入恰当的设计模式来消除，同时避免过度设计。

Kerievsky明确区分了两个方向：**向模式重构**（Refactoring to Patterns）和**远离模式重构**（Refactoring Away from Patterns）。前者是在代码复杂度已经需要模式支撑时引入模式，后者是在模式被过度使用导致不必要复杂性时将其移除。这与"一开始就套用模式"的错误做法形成对比——模式应当是重构的结果，而非设计的起点。

这套手法之所以重要，在于它解决了实际遗留代码中最常见的困境：代码的条件逻辑爆炸、对象创建耦合过深、算法变体难以扩展。Kerievsky整理了27种具体的重构到模式手法，每种手法都有明确的动机、力量权衡（forces）和机制步骤，使开发者能在已有代码库中逐步演进出设计模式，而不是推倒重写。

---

## 核心原理

### 用策略模式替换条件逻辑

当一个方法中出现多个`if-else`或`switch`分支，每个分支实现同一操作的不同变体时，Kerievsky提出"用策略模式替换条件逻辑"（Replace Conditional Logic with Strategy）手法。具体步骤是：先识别出各分支中变化的部分，将其抽取为独立的策略类，再让原方法通过组合调用策略对象完成计算。

例如，一个`Loan`类中根据贷款类型（`TERM_LOAN`、`REVOLVER`、`ADVISED_LINE`）用三段`if`逻辑计算资本金，重构后每种类型对应一个`CapitalStrategy`子类，`Loan`对象持有策略引用。这使得新增贷款类型时只需添加新策略类，原有代码无需修改，满足开闭原则。

### 用工厂方法替换构造函数

Kerievsky提出"用创建方法替换构造函数"（Replace Constructors with Creation Methods）和"将创建迁移至工厂"（Move Creation Knowledge to Factory）两个相关手法。当客户端代码直接调用`new`创建对象，且参数组合复杂易出错时，引入工厂方法让意图更加明显。

具体触发条件是：类有多个构造函数重载，调用者难以区分`new Loan(amount, duration, riskRating)`与`new Loan(amount, duration, expiryDate, riskRating)`的语义差异。重构后改为`Loan.createTermLoan(amount, duration, riskRating)`和`Loan.createRevolverLoan(...)`，工厂方法名称本身就是文档，消除了"神秘构造函数"的坏味道。

### 用组合模式统一叶节点与组合节点

"用组合模式替换隐式树"（Replace Implicit Tree with Composite）手法针对的是用字符串拼接或手动管理层级关系来构建树形结构的代码。Kerievsky的判断标准是：若构建逻辑中充斥`indent`、`depth`参数或手动追踪父子关系，则应引入`Component`接口，让`Leaf`和`Composite`统一实现`build()`或`accept()`方法。

这一手法的关键公式是：**客户端代码复杂度∝树层级数**，引入组合模式后，客户端复杂度降为O(1)——无论树有多少层，客户端只需调用根节点的统一方法，递归由组合节点内部处理。

### 用装饰者模式替换特殊情形

"用装饰者模式统一接口"（Unify Interfaces with Adapter）以及相关的装饰者引入手法，针对在原有类上打补丁式地添加功能（如为`PasswordSender`添加加密、日志功能时直接修改原类）的情况。Kerievsky建议在不修改原类的前提下，让装饰者包裹原对象并扩展行为，使得功能叠加呈线性可组合，而非指数级的子类爆炸（避免出现`EncryptedLoggingPasswordSender`这类组合命名的子类）。

---

## 实际应用

**案例：重构XML构建器**
Kerievsky书中展示了一个构建HTML标签的类，原始代码用`String`手动拼接`<ul>`、`<li>`，通过向组合模式重构后，`TagNode`成为组合节点，`StringNode`成为叶节点，客户端只需调用`root.toXml()`，消除了原先120行拼接逻辑中近40处字符串连接操作。

**案例：贷款风险计算器**
Kerievsky以银行贷款系统为主线贯穿全书。`Loan`类原本有超过5个构造函数重载和3段条件分支计算资本金，经过"替换构造函数为工厂方法"和"替换条件逻辑为策略"两步重构后，代码行数从约200行降至每个策略类平均30行，且每类贷款的计算逻辑可独立测试。

**案例：远离单例模式**
Kerievsky明确列出"内联单例"（Inline Singleton）手法：当`Registry`或`ServiceLocator`被实现为单例，但实际上只在测试中造成状态污染而无真实并发需求时，应将其改为普通对象通过依赖注入传递，消除隐式全局状态。

---

## 常见误区

**误区一：认为重构模式等于"先写模式后重构"**
许多开发者误解为在新功能开发时直接套用策略模式、工厂模式，再说是"用了重构模式"。Kerievsky的原则恰恰相反：只有当代码已经出现明确的坏味道（如条件逻辑重复、子类爆炸），并且复杂度已经证明模式有收益时，才执行向模式重构。过早引入模式是过度设计，书中称之为"模式病"（Patternitis）。

**误区二：认为所有重构方向都是"引入更多模式"**
Kerievsky的27种手法中，专门有一类是"远离模式"的手法，如"内联单例"、"以数据类替代类型码的简化版"等。有些代码库中存在不必要的`AbstractFactory`，导致只有一个具体工厂却有四层抽象，此时正确做法是移除模式而非增加模式。判断依据是：若模式引入的间接层没有对应的变化需求作为支撑，就应当移除。

**误区三：忽视重构手法的前置条件（forces）**
Kerievsky为每种手法列出了"力量权衡"（forces），例如"替换条件逻辑为策略"的前提是策略对象之间**无需共享状态**，若各分支逻辑需要访问大量`Loan`的私有字段，策略类会因数据传递而变得更复杂，此时手法的收益为负。忽视forces直接套用手法，是导致重构后代码反而更难维护的主要原因。

---

## 知识关联

**与基础重构的关系**：重构模式以Martin Fowler《Refactoring》（1999年第一版）中的基础手法为操作单元，每次"向策略模式重构"内部实际执行了提炼方法（Extract Method）、引入参数对象（Introduce Parameter Object）、替换类型码为子类（Replace Type Code with Subclasses）等多个Fowler级手法的组合序列。没有基础重构手法，重构模式的步骤无法原子化执行。

**与架构级重构的衔接**：重构模式作用于单个类或紧密相关的几个类之间，属于设计级别的演进。当多次应用重构模式后，子系统边界变得清晰，职责划分明确，这为架构级重构（如识别限界上下文、分离模块、提取微服务）提供了稳定的内部结构基础。若在架构拆分前没有完成设计级重构，跨服务的职责混乱会直接被复制到新的服务边界中，造成分布式单体。