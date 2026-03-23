---
id: "se-code-smells"
concept: "代码异味"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["识别"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 代码异味

## 概述

代码异味（Code Smell）是指源代码中存在的、可能暗示更深层设计问题的表面特征。这个术语由 Kent Beck 最先提出，后由 Martin Fowler 在1999年出版的《重构：改善既有代码的设计》一书中系统整理，原书共列举了22种经典代码异味。代码异味本身不一定是缺陷——程序仍然可以正常运行——但它是代码需要重构的信号，就像食物变质前散发的气味一样，提醒开发者问题正在积累。

代码异味的重要性在于它提供了一套具体可操作的诊断语言。在没有这套分类体系之前，开发者只能凭感觉说"这段代码写得不好"，却无法精确指出问题所在。22种异味的分类让团队能够用统一的术语沟通，例如"这里有一个长方法（Long Method）"或"这两个类之间存在依恋情结（Feature Envy）"，从而把模糊的主观判断转化为可讨论、可解决的工程问题。

## 核心原理

### 22种异味的六大分类

Martin Fowler 的22种代码异味可按问题性质归为六大类：

**膨胀类（Bloaters）**：代码随时间增长而变得臃肿，包括长方法（Long Method）、巨型类（Large Class）、基本类型偏执（Primitive Obsession）、过长参数列（Long Parameter List）和数据泥团（Data Clumps）。一般认为，超过10行的方法就应警惕是否存在长方法问题，而超过200-300行的类则通常被认为是巨型类。

**面向对象滥用类（OO Abusers）**：错误地应用面向对象原则，包括switch语句（Switch Statements）、临时字段（Temporary Field）、被拒绝的遗赠（Refused Bequest）和平行继承体系（Parallel Inheritance Hierarchies）。其中"被拒绝的遗赠"专指子类继承了父类的方法和数据，却只使用其中一小部分，暗示继承关系建立有误。

**变更阻碍类（Change Preventers）**：使代码难以修改，包括发散式变化（Divergent Change）、霰弹式修改（Shotgun Surgery）和平行继承体系。发散式变化是指一个类因不同原因频繁修改，违反了单一职责原则；霰弹式修改则相反，指一个变更需要散弹式地修改多个不同的类。

**可有可无类（Dispensables）**：不必要存在的代码，包括注释（Comments，当注释是用来解释烂代码时）、重复代码（Duplicate Code）、惰性类（Lazy Class）、纯数据类（Data Class）和夸夸其谈的未来性（Speculative Generality）。其中重复代码是最常见也危害最大的异味，"Rule of Three"原则规定当同一段逻辑出现第三次时，必须提取重构。

**耦合类（Couplers）**：类之间过度耦合，包括依恋情结（Feature Envy）、不适当的亲密关系（Inappropriate Intimacy）、消息链（Message Chains）和中间人（Middle Man）。Feature Envy 专指一个方法对另一个类的数据或方法的兴趣远超对自身所属类的兴趣，其判断标准是：如果一个方法中超过半数的操作都在访问别的类，就应将其迁移过去。

### 代码异味的量化识别

部分代码异味可通过静态分析工具量化检测。以下是几个具体阈值参考：
- **圈复杂度（Cyclomatic Complexity）> 10**：提示存在过复杂的条件逻辑，是Switch Statements或长方法的信号
- **方法参数数量 > 4**：通常被视为过长参数列的警告线
- **类的耦合度（Coupling Between Objects, CBO）> 7**：暗示不适当的亲密关系
- **缺乏内聚性（LCOM，Lack of Cohesion of Methods）值过高**：巨型类的量化指标

工具如 SonarQube、PMD、Checkstyle 均基于上述类似阈值自动检测代码异味。

### 异味与重构手法的对应关系

每种代码异味都对应一种或多种具体的重构手法。这种对应关系构成了整个重构体系的诊断-治疗逻辑：
- 长方法 → 提取方法（Extract Method）
- 巨型类 → 提取类（Extract Class）
- 过长参数列 → 引入参数对象（Introduce Parameter Object）
- Feature Envy → 搬移方法（Move Method）
- 重复代码 → 提取方法或提取父类（Extract Superclass）

## 实际应用

**电商系统中的 Feature Envy**：假设 `OrderProcessor` 类中有一个方法 `calculateDiscount()`，其内部90%的代码都在读取 `Customer` 对象的会员等级、历史订单量和积分字段，却只有一行是操作 `Order` 本身。这正是典型的 Feature Envy——该方法应当被搬移到 `Customer` 类中。

**配置类中的数据泥团**：如果代码中经常有三个字段 `host`、`port`、`protocol` 同时出现在方法参数列或成员变量中，这三者就构成"数据泥团"，应当封装为一个 `ConnectionConfig` 对象。判断方法是：删掉其中一个字段，剩下的字段是否还有意义？若不然，它们就属于数据泥团。

**注释作为异味的特殊性**：注释本身不是坏事，但当注释的作用是解释一段复杂逻辑"为什么这样写"或"这段代码在做什么"时，这段注释往往暗示应该用提取方法并赋予一个清晰方法名来代替它，正如 Fowler 所说："当你感觉需要写注释时，先尝试重构，让代码自己说话。"

## 常见误区

**误区一：代码异味等于Bug，必须立刻修复。** 代码异味是设计层面的警示，不是功能性错误。一段含有"长方法"异味的代码完全可以正确运行多年。是否重构需要结合业务优先级判断，对于即将废弃的模块，忍受异味往往比重构更经济。盲目将所有异味当作紧急Bug处理，反而会造成返工和引入新缺陷。

**误区二：消除所有注释就是消除注释异味。** 注释异味特指"用来解释烂代码的注释"，即那些描述"做什么"和"怎么做"的注释。记录"为什么"的注释（如解释业务规则背景、记录已知限制或说明算法来源）不属于异味，删除它们反而会损失关键上下文信息。

**误区三：短小的类/方法一定没有异味。** 惰性类（Lazy Class）和中间人（Middle Man）恰恰是因为类太小、做的事情太少而构成异味。一个只有一个方法、仅仅委托调用另一个类的"包装类"，就是典型的中间人异味，应当考虑内联它（Inline Class）。

## 知识关联

学习代码异味需要先掌握重构概述中的基本理念——即在不改变外部行为的前提下改善代码结构，因为识别异味的目的始终是指导重构操作，脱离重构谈异味没有实践意义。

代码异味是后续具体重构手法的学习入口：识别出"长方法"后，自然引出**提取方法**（Extract Method）的操作步骤；识别出"巨型类"后，引出**提取类**（Extract Class）的拆分策略；识别出变量和方法命名晦涩这一异味（隐含于多种异味类型中），则引出**重命名重构**的实践。代码异味体系本质上是一张从"问题现象"指向"解决手法"的导航地图，22种异味对应 Fowler 书中80余种重构手法，二者共同构成重构实践的完整框架。
