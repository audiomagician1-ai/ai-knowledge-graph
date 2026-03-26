---
id: "se-dp-adapter"
concept: "适配器模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["结构型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 适配器模式

## 概述

适配器模式（Adapter Pattern）是一种结构型设计模式，其核心目的是将一个类的接口转换为客户端期望的另一种接口形式，使得原本因接口不兼容而无法协作的类能够一起工作。这个模式的名字来源于现实生活中的电源适配器——你的笔记本电脑插头无法直接插入墙上不同规格的插座，但通过一个转接头（适配器），两者就能正常工作，而笔记本和插座本身都不需要修改。

适配器模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式归类，编号为结构型模式第一位。它在软件开发史上被广泛使用的典型场景是遗留系统集成（Legacy System Integration）——当一个运行了十年的老系统提供的接口格式与新系统不兼容时，开发团队不必重写旧代码，只需引入一个适配器类来"翻译"两套接口之间的差异。

适配器模式的重要性体现在它是"开闭原则"的忠实践行者：旧有代码对修改关闭，新功能通过适配器扩展而非入侵原始类。在Java标准库中，`InputStreamReader`就是一个典型的适配器，它将字节流（`InputStream`）适配为字符流（`Reader`），从JDK 1.1起就存在于核心库中。

---

## 核心原理

### 两种实现形式：类适配器与对象适配器

适配器模式有两种实现方式，差别在于复用旧接口的手段。

**类适配器**使用多重继承（在Java中用接口+继承实现）：适配器类同时继承被适配类（Adaptee）并实现目标接口（Target）。其结构公式为：

```
Adapter extends Adaptee implements Target
```

**对象适配器**使用组合：适配器类内部持有一个被适配类的实例，通过委托调用来完成接口转换。其结构为：

```
class Adapter implements Target {
    private Adaptee adaptee;  // 组合持有
    public void request() {
        adaptee.specificRequest();  // 委托调用
    }
}
```

对象适配器比类适配器更灵活，因为它可以在运行时替换持有的Adaptee实例，而不受编译期继承关系的约束。GoF原书推荐优先使用对象适配器，这一建议与"优先组合而非继承"原则一致。

### 三个参与角色

适配器模式中精确地存在三个角色：

1. **Target（目标接口）**：客户端所期待的接口，定义了客户端使用的方法签名，例如 `void charge(int voltage)`。
2. **Adaptee（被适配者）**：已有的、接口不兼容的类，例如老系统提供的 `void oldCharge(double power)` 方法。
3. **Adapter（适配器）**：桥接前两者的转换类，内部把 `charge(int voltage)` 的调用转换为 `oldCharge(double power)` 的调用，并处理单位换算等细节（如 `power = voltage * 0.9`）。

### 接口转换的三种类型

适配器实际执行的转换操作分为三类：
- **方法名映射**：客户端调用 `read()`，适配器内部调用 `getData()`。
- **参数转换**：客户端传入整型电压220，适配器换算为浮点功率198.0后传给旧接口。
- **协议适配**：例如将同步调用转换为异步回调形式，常见于网络库的封装。

---

## 实际应用

### 案例一：Java的`Arrays.asList()`与`List`接口

`Arrays.asList()` 返回的是 `java.util.Arrays$ArrayList`，它不支持 `add()` 和 `remove()` 操作，但它实现了 `List` 接口，使得数组可以被所有期望 `List` 的代码接受。这是一个将固定长度数组适配为可遍历List接口的典型应用，但需注意其局限性（不支持增删），这正是适配器"不改变被适配者，只转换接口"特性的真实体现。

### 案例二：遗留支付系统集成

假设公司已有一套老支付系统提供方法 `oldPay(String user, float yuan)`，新统一支付平台要求所有支付模块实现接口 `PayService.pay(PayRequest request)`。开发人员无权修改老系统代码（可能是第三方SDK）。此时创建 `LegacyPayAdapter implements PayService`，在 `pay()` 内部从 `PayRequest` 提取用户名和金额，调用 `oldPay()`，仅需约10行代码即可完成集成，新系统完全无感知旧接口的存在。

### 案例三：Android中的RecyclerView.Adapter

Android的 `RecyclerView` 使用了名为 `Adapter` 的组件，将应用的数据源（如 `List<User>`）适配为 `RecyclerView` 能理解的 `ViewHolder` 体系。开发者继承 `RecyclerView.Adapter<VH>` 并实现 `onBindViewHolder()` 和 `getItemCount()`，这两个方法正是将数据接口转换为视图接口的适配逻辑。

---

## 常见误区

### 误区一：适配器模式等同于代理模式

两者都在原有对象外包装一层，但目的截然不同。代理模式的Proxy与RealSubject实现**相同接口**，目的是控制访问（如权限检查、延迟加载）；而适配器的Adapter与Adaptee接口**不同**，目的是接口转换。简单判断标准：如果包装前后接口一致，是代理；如果接口不一致需要转换，是适配器。

### 误区二：适配器应该承担业务逻辑

适配器的职责仅限于接口格式转换，例如参数重组、方法名映射、单位换算等轻量操作。如果在适配器内部编写大量业务规则（如折扣计算、风控判断），则违反了单一职责原则。一个健康的适配器代码量通常不超过50行，超出这个规模应考虑是否混入了本不属于它的逻辑。

### 误区三：适配器模式可以解决所有遗留系统问题

适配器只能解决**接口不兼容**问题，无法解决语义不兼容问题。例如，旧系统的"用户ID"是自增整数，新系统的"用户ID"是UUID字符串——单纯的适配器做类型转换后，ID本身的业务含义已经错位，这类问题需要在适配器中引入映射表（ID Mapping），或通过更深层的数据迁移解决，而非单靠模式本身。

---

## 知识关联

适配器模式不依赖其他设计模式作为前提，是入门结构型模式的第一站，这也是它在本域难度评级仅为2/9的原因。

学习适配器模式后，自然过渡到**外观模式（Facade Pattern）**。两者都为复杂或不兼容的接口提供新的访问入口，但外观模式面对的是**多个子系统**的复杂性，它将一组接口统一简化为一个高层接口；而适配器模式面对的是**单个接口**的不兼容性，目标是"翻译"而非"简化"。理解这一区别后，外观模式的学习将非常顺畅：适配器是一对一的接口翻译，外观是多对一的接口整合。

在实际架构设计中，适配器模式常与**依赖倒置原则（DIP）**配合使用——高层模块依赖Target抽象接口，适配器负责将具体的Adaptee绑定到该接口，使得更换底层实现时只需替换一个适配器类，高层代码零修改。