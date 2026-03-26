---
id: "se-dp-prototype"
concept: "原型模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["创建型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.429
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 原型模式

## 概述

原型模式（Prototype Pattern）是一种创建型设计模式，其核心机制是**通过复制一个已存在的对象来创建新对象**，而非调用构造函数重新初始化。这个"已存在的对象"称为原型（prototype），新创建的对象是原型的克隆体。GoF（Gang of Four）在1994年出版的《Design Patterns》中将其正式列为23种经典设计模式之一，意图定义为："用原型实例指定创建对象的种类，并且通过拷贝这些原型创建新的对象。"

原型模式的价值在于**绕过构造函数的开销**。当创建一个对象需要大量计算、数据库查询或文件读取时，克隆一个已有对象的成本远低于重新构造。例如，一个从数据库加载了10,000行数据的报表对象，克隆它只需内存复制，而重新构造则需重新执行查询。与工厂模式不同，原型模式不依赖类层次结构来决定创建哪个子类，而是依赖对象自身的`clone()`方法。

## 核心原理

### 克隆接口与 `clone()` 方法

原型模式要求原型类实现一个克隆接口。在Java中，这是`java.lang.Cloneable`接口，配合`Object.clone()`方法；在C#中则是`ICloneable`接口，要求实现`Clone()`方法。Python中可通过`copy`模块的`copy()`和`deepcopy()`函数实现。最简化的结构如下：

```
Prototype接口
  + clone() → Prototype

ConcretePrototype实现Prototype
  - field: SomeType
  + clone() → ConcretePrototype  // 返回自身的副本
```

调用方（Client）持有一个原型对象引用，需要新对象时直接调用`prototype.clone()`，无需知道具体类名。

### 浅拷贝 vs 深拷贝

这是原型模式中**最关键的技术区分**，直接影响克隆对象是否安全独立。

**浅拷贝（Shallow Copy）**：复制对象的所有字段，但对于引用类型字段，只复制引用地址，不复制引用指向的对象本身。结果是原对象与克隆体**共享**同一块子对象内存。Java的`Object.clone()`默认执行浅拷贝。若原型有字段`List<String> tags`，浅拷贝后两个对象的`tags`指向同一个List实例，修改一个会影响另一个。

**深拷贝（Deep Copy）**：递归复制对象及其所有引用指向的子对象，克隆体与原型**完全独立**。实现深拷贝的常见方式有：
1. 手动递归调用每个子对象的`clone()`
2. 序列化再反序列化（Java中使用`ObjectOutputStream` + `ObjectInputStream`）
3. 使用专用库，如Java的`Apache Commons Lang`中的`SerializationUtils.clone()`

选择浅拷贝还是深拷贝，取决于业务需求：不可变对象（如`String`、`Integer`）共享是安全的，可变集合则通常需要深拷贝。

### 克隆注册表（Prototype Registry）

当系统中存在多种不同配置的原型时，可引入**克隆注册表**（也称原型管理器）统一管理。注册表本质是一个`Map<String, Prototype>`，以名称或枚举Key存储预配置好的原型实例。

```
PrototypeRegistry
  - registry: Map<String, Prototype>
  + register(key: String, prototype: Prototype)
  + clone(key: String) → Prototype   // 查找后调用clone()
```

客户端通过`registry.clone("circle_large")`即可获得对应类型的克隆体，无需知道`CirclePrototype`类的存在。注册表将**对象的配置**与**对象的创建**分离，是原型模式在复杂场景下的标准扩展形式。

## 实际应用

**文字处理软件的样式复制**：Microsoft Word中的"格式刷"功能，本质上是将一个段落样式对象（含字体、字号、颜色、段距等20余个属性）克隆后应用到目标段落，而非逐属性手动赋值。

**游戏地图编辑器中的对象放置**：地图编辑器中预设多个"模板敌人"存储在注册表里，设计师点击放置时，系统调用`registry.clone("goblin_elite")`得到独立实例并修改其位置坐标。这避免了每次放置都重新加载模型、贴图和AI配置。

**Java标准库中的实际案例**：`java.util.ArrayList`实现了`Cloneable`接口，其`clone()`方法执行的是浅拷贝——返回一个新的ArrayList，但其中的元素对象仍是原来的引用。这一行为在Java文档中有明确说明，是理解浅拷贝副作用的经典参考。

## 常见误区

**误区一：认为`clone()`一定等于深拷贝**。很多初学者以为调用`clone()`就能获得完全独立的副本。实际上Java的`Object.clone()`是逐字段浅拷贝，若对象包含`Date`、`List`等可变引用字段，修改克隆体的这些字段会同步影响原型。必须显式覆写`clone()`并手动深拷贝可变字段。

**误区二：原型模式与工厂模式是互斥替代关系**。工厂模式通过调用构造函数和`new`关键字创建对象，适合对象构造逻辑复杂但每次需要全新状态的场景；原型模式适合对象构造昂贵但新对象初始状态与某个已有对象相近的场景。两者解决的创建时机不同，实践中常在同一个工厂方法内部使用`prototype.clone()`来实现对象创建，二者可以协同。

**误区三：循环引用时深拷贝会无限递归**。若对象A引用对象B，B又引用A，朴素的递归深拷贝实现会导致栈溢出。正确做法是在深拷贝过程中维护一个`Map<Object, Object>`作为"已拷贝对象"缓存，检测到已拷贝过的对象直接返回缓存中的副本，打破循环。

## 知识关联

学习原型模式前，需掌握**工厂模式**中"将对象创建逻辑封装"的思想——原型模式是另一种封装方式，区别在于用已有实例替代类信息作为创建依据。理解构造函数与初始化过程的内存开销，也是判断原型模式是否适用的前提知识。

掌握本章内容后，自然延伸至**原型模式在游戏开发中的应用**：游戏实体（Entity）系统大量使用原型注册表管理数百种可实例化的游戏对象，且需要处理深拷贝中的组件系统、附加行为脚本等复杂嵌套结构，是本章浅拷贝/深拷贝和注册表概念在高复杂度场景下的直接延伸。