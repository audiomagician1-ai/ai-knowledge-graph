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
quality_tier: "B"
quality_score: 48.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
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

重构模式（Refactoring to Patterns）是由 Joshua Kerievsky 在 2004 年出版的同名著作《Refactoring to Patterns》中系统化提出的一套重构手法集合。其核心思想是：代码的演进应当从"过度简单"向"设计模式"方向渐进靠拢，而非一开始就强行套用模式。Kerievsky 将 Martin Fowler 的重构技法与 GoF（Gang of Four）的 23 种设计模式结合，形成了以模式为终态的定向重构路径。

该手法体系解决了两类对立的工程问题：一是"过度设计"——开发者在没有实际需求时预先引入复杂模式；二是"设计不足"——代码随功能堆砌而退化为难以扩展的大泥球。Kerievsky 提出"演进式设计"（Evolutionary Design）哲学，认为模式应当在代码"疼痛"时才被引入，这种疼痛通常以代码坏味道（Code Smell）的形式显现，如条件逻辑爆炸、重复类族或膨胀类。

重构模式之所以区别于普通重构，在于它具有明确的设计意图终态。普通重构手法如"提取方法"（Extract Method）仅改善局部结构，而重构模式手法如"以策略取代条件逻辑"（Replace Conditional Logic with Strategy）会将代码推向特定的 GoF 模式结构，每一步均可独立执行且不破坏现有行为。

## 核心原理

### 以创建模式消除重复构造逻辑

Kerievsky 书中第一类重构手法针对对象创建的混乱。典型手法"以工厂方法引入创建"（Introduce Creation Method）将散落在各处的 `new` 调用和初始化逻辑收敛到静态工厂方法中，终态是 Factory Method 或 Abstract Factory 模式。具体操作步骤为：首先识别所有构造相似对象的客户代码，其次提取一个意图明确的创建方法（如 `createGuest()` 而非 `new User(false, null, 0)`），再逐步将构造器设为私有。此手法专门对付"构造器参数超过 3 个且含有布尔标志位"这一具体坏味道。

### 以行为模式消除条件逻辑

书中最重要的手法之一是"以策略取代条件逻辑"（Replace Conditional Logic with Strategy），对应 GoF Strategy 模式。当一个方法内部出现多个 `if-else` 或 `switch` 分支，且每个分支代表一种算法变体时，手法步骤如下：第一步，将每个分支体用"提取方法"隔离；第二步，将这些方法移入独立类形成具体策略类；第三步，定义共同接口；第四步，在原类中注入策略对象替换条件判断。完成后原始条件逻辑从 O(n) 分支规模降至单一多态调用。

类似地，"以状态取代状态改变条件语句"（Replace State-Altering Conditionals with State）专门处理随状态变化而改变行为的条件块，终态为 GoF State 模式。两者区别在于：Strategy 的变体由调用者注入，State 的变体由对象自身在运行时切换。

### 以结构模式消除膨胀类

"以装饰器引入"（Move Embellishment to Decorator）是 Kerievsky 为处理"膨胀类"坏味道设计的手法。当一个核心类因为需要支持多种可选行为而膨胀时，手法将可选行为提取到 Decorator 包装类中。判断时机的量化标准是：若一个类中超过 30% 的方法仅在特定配置下被调用，便是引入 Decorator 的信号。操作时须先确保核心类与装饰器共享同一接口，再将可选逻辑迁移至装饰器并委托调用核心实现。

"以组合模式统一简单与复杂对象"（Replace One/Many Distinctions with Composite）则针对代码中频繁出现的"单个对象 vs. 集合对象"二元判断，终态为 GoF Composite 模式，使客户代码无需区分树节点与叶节点。

### 以模板方法消除继承层次中的重复

"以模板方法形成统一"（Form Template Method）解决的问题是：两个子类含有步骤顺序相同但细节不同的方法。手法要求先在两个方法中逐步"提取相似步骤"并比对差异，将不变步骤上移到父类、将变化步骤声明为抽象方法，终态为 GoF Template Method 模式。Kerievsky 给出的判断标准是：若两个方法可以通过"重命名后对比"而仅剩 1-3 处差异，则适合此手法。

## 实际应用

**电商订单折扣计算重构**：一个 `calculateDiscount()` 方法含有针对会员等级（普通、银牌、金牌、企业）的四路 `if-else`，每季度新增一个等级就需修改此方法，违反开闭原则。按"以策略取代条件逻辑"手法：将四路分支提取为 `RegularDiscount`、`SilverDiscount`、`GoldDiscount`、`CorporateDiscount` 四个实现 `DiscountStrategy` 接口的类，原方法变为 `strategy.calculate(order)`。新增等级只需新增类，不触碰原有逻辑。

**日志系统功能叠加重构**：一个 `Logger` 类因需支持"带时间戳"、"带线程名"、"加密输出"等可选功能而膨胀到 800 行。按"移入装饰器"手法，将每种可选功能封装为 `TimestampDecorator`、`ThreadNameDecorator`、`EncryptionDecorator`，均实现 `Logger` 接口并持有 `Logger` 引用。原类缩减至不足 100 行，功能组合由装饰器链式嵌套完成。

## 常见误区

**误区一：将重构模式等同于"直接应用设计模式"**。重构模式是渐进式手法序列，每一步都保证测试通过，而直接应用模式是一次性重写。Kerievsky 明确要求每个手法拆分为可独立提交的小步骤，其中间状态也必须编译通过且测试绿灯。跳步操作会引入回归风险，丧失重构的安全保障。

**误区二：认为所有坏味道都应推向模式**。Kerievsky 在书中明确区分了"模式是解法之一"与"模式是唯一解法"。例如，简单的 3 路条件逻辑用多态处理可能反而增加类数量，此时普通的"提取方法"就已足够。书中给出的经验阈值是：条件分支超过 4 个且预期会持续增长时，才值得引入 Strategy；否则过早引入模式本身就是一种设计坏味道，Kerievsky 称之为"模式过敏"（Pattern-itis）。

**误区三：混淆"重构到模式"与"从模式开始"**。"重构到模式"的前提是代码已经可以工作，重构动作在现有代码基础上演进。若在功能尚未实现时就规划 Strategy 或 Decorator 的完整骨架，则属于 YAGNI 原则的违背，与 Kerievsky 的演进式设计理念直接矛盾。

## 知识关联

重构模式以代码坏味道识别为触发条件，学习者需要熟悉 Martin Fowler《重构》第二版中列出的 24 种坏味道，尤其是"发散式变化"和"霰弹式修改"这两种直接驱动模式引入的坏味道。GoF 23 种设计模式的结构知识是手法终态的参照系，特别是 Strategy、State、Decorator、Composite、Template Method、Factory Method 六种模式在 Kerievsky 书中出现频次最高。

向上延伸，重构模式的思维方式为**架构级重构**奠定基础：当单一类或方法层面的模式引入积累到模块边界时，就会触发更大范围的层次调整，如将一组 Strategy 类演进为独立插件子系统，或将 Composite 结构演进为树形领域模型的独立有界上下文。Kerievsky 书中的手法本质上是局部决策，而架构级重构将这些局部决策在系统拓扑层面上进行协调与整合。