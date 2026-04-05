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


# 适配器模式

## 概述

适配器模式（Adapter Pattern）是一种结构型设计模式，其核心功能是将一个类的接口转换成客户端期望的另一种接口形式，从而使原本因接口不兼容而无法协作的类能够一起工作。这个模式的名称来源于现实生活中的"电源适配器"——就像一个三脚插头转两孔插座的转换器，它本身不改变电力的传输，只是解决了接口形制不匹配的问题。

适配器模式由 GoF（Gang of Four）在 1994 年出版的《设计模式：可复用面向对象软件的基础》一书中正式记录，是书中收录的 23 种经典设计模式之一。它在企业软件开发中极为常见，尤其在需要集成遗留系统（Legacy System）或第三方库时，适配器模式几乎是不可回避的选择——因为你往往无法修改已有代码，只能在中间加一层"翻译层"。

## 核心原理

### 两种实现结构

适配器模式有两种经典实现方式：**类适配器**和**对象适配器**。

**类适配器**通过多重继承实现：`Adapter` 类同时继承 `Target`（目标接口）和 `Adaptee`（被适配者）。这种方式在 Java 中受限，因为 Java 不支持多继承，但在 C++ 中可以直接使用。类适配器的优点是可以重写 `Adaptee` 的行为，缺点是耦合度较高。

**对象适配器**通过组合实现：`Adapter` 类实现 `Target` 接口，并在内部持有一个 `Adaptee` 实例的引用，在实现目标方法时委托给该实例。这是更常用的方式，符合"优先使用组合而非继承"的设计原则。其结构可以表示为：

```
Client → Target(接口) ← Adapter → Adaptee(被适配类)
```

### 参与角色及职责

适配器模式包含三个固定角色：

- **Target（目标接口）**：客户端所期望调用的接口，例如定义了 `request()` 方法。
- **Adaptee（被适配者）**：已有的、功能符合需求但接口不匹配的类，例如只有 `specificRequest()` 方法。
- **Adapter（适配器）**：实现 `Target` 接口，并在 `request()` 内部调用 `Adaptee.specificRequest()`，完成接口转换。

以 Java 代码示意：
```java
class Adapter implements Target {
    private Adaptee adaptee = new Adaptee();
    
    @Override
    public void request() {
        adaptee.specificRequest(); // 接口转换发生在这里
    }
}
```

### 双向适配器

在某些复杂场景下，需要两个已有系统互相调用，可以构建**双向适配器**，让 `Adapter` 类同时实现两个系统的接口，双向翻译各自的调用。这在系统迁移阶段尤为实用——新旧系统并行运行时，通过双向适配器保持互通。

## 实际应用

**Java 标准库中的真实案例**：`java.io.InputStreamReader` 就是一个典型的适配器。它将 `InputStream`（字节流接口）适配为 `Reader`（字符流接口），使得原本处理字节的 `InputStream` 可以被期望字符流的代码使用，其构造函数 `InputStreamReader(InputStream in)` 正是接收被适配对象的入口。

**遗留系统集成**：假设公司有一个老系统提供 XML 格式的数据接口，而新购买的第三方分析库只接受 JSON 输入。由于两者都无法修改，可以编写一个 `XmlToJsonAdapter`，实现新库要求的 `JsonDataSource` 接口，内部调用老系统的 XML 接口并完成格式转换，这样新库无需感知老系统的存在。

**支付接口统一化**：电商平台需要同时支持支付宝、微信支付、银联三种支付方式，每家 SDK 的接口名称和参数各不相同。可以定义统一的 `PaymentGateway` 接口（含 `pay(amount, currency)` 方法），然后分别编写 `AlipayAdapter`、`WechatPayAdapter`、`UnionPayAdapter`，各自在内部调用对应 SDK 的真实方法，客户端只与 `PaymentGateway` 接口交互。

## 常见误区

**误区一：把适配器当成万能的"接口转换工具"从而滥用**。适配器模式的设计前提是"无法修改现有类"。如果被适配的类是你自己可以修改的代码，正确做法是直接重构该类的接口，而不是叠加一层适配器——后者会增加类的数量和调用链深度，造成不必要的复杂性。

**误区二：混淆适配器模式与装饰器模式**。两者都使用组合，但目的截然不同：适配器模式的目的是**改变接口**，让不兼容的接口变得兼容，通常 `Adapter` 和 `Adaptee` 实现的接口完全不同；装饰器模式的目的是**增强功能**，装饰器和被装饰对象实现**相同**接口，只是在调用前后加入额外逻辑。判断标准只有一个：是否发生了接口转换。

**误区三：认为适配器只能适配单个方法**。实际上，一个适配器可以将 `Adaptee` 的多个方法组合映射到 `Target` 的一个方法中，也可以将 `Target` 的一个方法拆分委托给 `Adaptee` 的多个方法。适配器的本质是接口协议的翻译，翻译的复杂程度不受限制。

## 知识关联

适配器模式不需要任何设计模式的先修知识，只需要理解基本的面向对象概念（接口、继承、组合）即可掌握，这也是它在 23 种模式中入门难度最低（本文标注难度 2/9）的原因。

学习完适配器模式后，自然衔接的下一个概念是**外观模式（Facade Pattern）**。两者都属于结构型模式，也都是在现有代码之上增加一层间接层，但区别明显：适配器解决的是接口**不兼容**问题（一对一转换），外观模式解决的是接口**过于复杂**问题（对多个子系统提供统一的简化入口）。可以这样记忆：适配器是"翻译官"，外观是"前台接待"。理解了这个区别，再看外观模式时会发现其设计意图更加清晰。