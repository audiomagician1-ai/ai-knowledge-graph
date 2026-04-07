---
id: "se-replace-conditional"
concept: "替换条件逻辑"
domain: "software-engineering"
subdomain: "refactoring"
subdomain_name: "重构"
difficulty: 2
is_milestone: false
tags: ["控制流"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 替换条件逻辑

## 概述

替换条件逻辑（Replace Conditional with Polymorphism）是重构领域中一种将冗长的 `switch/case` 语句或 `if-else` 链转换为面向对象多态调用的手法。其核心思想是：将"根据类型判断执行什么"的判断逻辑，分散到各个子类或策略对象中，让每个类"自己知道自己该做什么"，从而消除集中式的类型枚举代码。

这一手法由 Martin Fowler 在 1999 年出版的《重构：改善既有代码的设计》（*Refactoring: Improving the Design of Existing Code*）中系统化整理，编号为第 327 页的核心重构手法之一。Fowler 明确指出，`switch` 语句是"坏味道"的典型代表，尤其当同一组条件在代码库中重复出现两次以上时，就是应用此手法的强烈信号。

该手法直接解决了"散弹式修改"（Shotgun Surgery）问题——每当增加一种新类型时，必须找遍所有 `switch` 分支逐一添加 `case`，极易遗漏。改用多态后，新增类型只需新建一个子类并覆写对应方法，修改范围严格限定在单一文件内。

## 核心原理

### 识别适用场景

并非所有条件逻辑都应被多态替换。Fowler 给出了明确的判断标准：当你发现条件表达式的每个分支都在做**相同名称但不同实现**的操作，且条件变量本质上代表一种"类型"或"角色"时，才是典型的适用场景。例如，以下代码按 `bird.type` 决定 `getSpeed()` 的计算方式：

```java
// 替换前：典型的 switch 坏味道
double getSpeed() {
    switch (bird.type) {
        case "EUROPEAN":   return baseSpeed();
        case "AFRICAN":    return baseSpeed() - loadFactor() * bird.numberOfCoconuts;
        case "NORWEGIAN_BLUE": return (bird.isNailed) ? 0 : baseSpeed(bird.voltage);
        default: throw new RuntimeException("Unknown type: " + bird.type);
    }
}
```

该 `switch` 中，每个分支都在回答同一个问题（"速度是多少"），但答案因类型不同而异，正是多态替换的目标对象。

### 三步重构手法

替换条件逻辑的标准步骤如下：

**第一步：建立超类/接口**。提取一个包含条件逻辑所在方法的抽象基类（或接口），声明 `getSpeed()` 为抽象方法或提供默认实现。

**第二步：为每个分支建立子类**。针对 `switch` 的每个 `case`，创建对应的子类（`EuropeanSwallow`、`AfricanSwallow`、`NorwegianBlueParrot`），并在各子类中覆写 `getSpeed()` 方法，将原分支的计算逻辑迁入。

**第三步：引入工厂方法，删除 `switch`**。原始的类型创建逻辑集中到一个工厂方法中（通常仍保留一个 `switch`，但仅负责对象构建，不再承载业务计算），最终删除原始的条件分支。

重构后的代码结构中，调用方只需调用 `bird.getSpeed()`，完全不感知具体类型——这正是开闭原则（Open/Closed Principle）的体现：对扩展开放，对修改关闭。

### 变体：使用策略模式替代继承

当被替换的条件逻辑所在类**无法被继承**（如是第三方库类、或需要在运行时切换类型），可改用策略模式（Strategy Pattern）。将各分支逻辑封装为独立的策略类，通过组合而非继承实现多态。例如 Java 中将策略存入 `Map<String, BirdStrategy>`，以类型字符串为键查找对应策略执行，完全绕过 `switch`：

```java
Map<String, BirdStrategy> strategies = Map.of(
    "EUROPEAN",       new EuropeanStrategy(),
    "AFRICAN",        new AfricanStrategy(),
    "NORWEGIAN_BLUE", new NorwegianBlueStrategy()
);
// 调用时：strategies.get(bird.type).getSpeed(bird)
```

这一变体在 JavaScript、Python 等语言中因一等函数支持，常直接以函数字典（function map）实现，无需专门定义策略类。

## 实际应用

**电商订单折扣计算**：系统需要根据用户类型（普通用户、VIP、企业客户）计算不同折扣率，原始实现往往是一条 `if-else` 链，散布在多个服务类中。应用替换条件逻辑后，建立 `Customer` 抽象类及三个子类，各自覆写 `getDiscount()` 方法，新增"超级VIP"级别只需新建子类，全部已有服务代码无需改动。

**游戏角色行为**：角色扮演游戏中，战士、法师、弓手的攻击方式截然不同，若以 `switch (role)` 实现，每次新增职业都必须修改战斗系统核心类。重构为多态后，新职业的加入对战斗引擎完全透明，测试范围也缩小为仅对新类编写单元测试。

**编译器 AST 节点处理**：编译器对不同语法节点（加法节点、变量节点、函数调用节点）进行求值时，若用 `instanceof` 链判断，每次添加新节点类型都需修改求值逻辑。改为在每个节点类上定义 `evaluate()` 虚方法，是该手法在编译器工程中的经典应用。

## 常见误区

**误区一：认为所有条件都应被多态替换**。Fowler 本人明确提醒，对于"每个分支在做完全不同事情"的条件（例如权限判断中的 `if (isAdmin)`），并不适合多态替换——因为这里条件变量并非类型区分，强行引入子类反而增加了不必要的类层次。只有当条件的各分支在语义上回答同一问题时，多态替换才有价值。

**误区二：工厂方法中的 `switch` 也被视为坏味道**。很多初学者在完成替换后，看到工厂方法中仍存在 `switch (type)` 便感到困惑。实际上这是正常且合理的——工厂方法中的 `switch` 专职负责"根据类型创建对象"，职责单一，不会因业务逻辑变化而膨胀，与散布在业务方法中的 `switch` 性质完全不同。

**误区三：多态替换必然导致类数量爆炸难以维护**。当类型枚举只有 2-3 个值且变化极低频时，引入继承层次的复杂度可能确实超过直接写 `if-else` 的成本。重构时机的判断标准是：同一条件在代码库中出现 **3 次以上**，且有增加新类型的预期，此时多态替换的收益才明显超过成本。

## 知识关联

替换条件逻辑的前置知识是面向对象的继承与方法覆写机制，以及基本的"坏味道"识别能力（尤其是识别重复的 `switch` 语句）。掌握这一手法是理解**开闭原则**在代码层面如何落地的最直观路径——每一次成功的多态替换，都是一次开闭原则的具体实践。

在重构技术体系中，该手法常与**提炼方法**（Extract Method）和**引入参数对象**配合使用：在执行多态替换之前，通常需要先用提炼方法将 `switch` 的各分支逻辑整理干净，再进行类层次的构建。理解该手法之后，自然引出了**策略模式**、**访问者模式**（Visitor Pattern）等设计模式的动机——它们本质上都是将条件分发逻辑通过结构化手段消除的系统化方案。