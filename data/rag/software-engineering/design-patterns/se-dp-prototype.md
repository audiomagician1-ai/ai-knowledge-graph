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
quality_tier: "S"
quality_score: 82.9
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


# 原型模式

## 概述

原型模式（Prototype Pattern）是一种创建型设计模式，其核心机制是通过**克隆已有对象**来创建新对象，而非调用构造函数重新初始化。这意味着新对象的创建成本由"构造"转变为"复制"，在对象初始化代价高昂时具有显著优势。GoF（Gang of Four）在1994年出版的《设计模式》一书中正式定义了原型模式，将其归类为创建型模式之一。

原型模式的标准接口极为精简：只需在基类或接口上声明一个 `clone()` 方法，每个具体类负责实现自身的克隆逻辑。客户端代码无需知道被克隆对象的具体类型，只需持有原型接口的引用即可生成副本。这与工厂模式的差异在于：工厂模式依赖外部逻辑决定实例化哪个类，而原型模式把"如何复制自己"的知识封装在对象内部。

原型模式在以下场景中不可替代：当系统需要创建的对象类型在运行时才能确定、对象初始化需要访问数据库或网络（克隆可绕过这一开销）、或者需要保存对象在某一时刻的完整状态快照时。

---

## 核心原理

### 浅拷贝（Shallow Copy）

浅拷贝只复制对象的**基本类型字段的值**，对于引用类型字段，仅复制引用地址，不复制引用所指向的对象本身。在 Java 中，`Object.clone()` 默认执行的就是浅拷贝。

```java
class Address {
    String city;
}
class Person implements Cloneable {
    String name;
    Address address; // 引用类型
    
    @Override
    public Person clone() throws CloneNotSupportedException {
        return (Person) super.clone(); // 浅拷贝：address 指向同一对象
    }
}
```

浅拷贝的危险在于：若原型和克隆体共享同一个 `Address` 对象，修改克隆体的 `address.city` 会同时影响原型，产生意外的"幽灵修改"。

### 深拷贝（Deep Copy）

深拷贝递归复制对象图中的**所有节点**，克隆体与原型完全独立，互不影响。实现深拷贝有三种常见方式：

1. **逐层手动克隆**：在 `clone()` 方法中对每个引用字段也调用 `clone()`，适合对象层次较浅的情况。
2. **序列化反序列化**：将对象序列化为字节流再反序列化，可自动处理任意深度的对象图，但要求所有字段实现 `Serializable`，且性能开销约为手动克隆的 5–10 倍。
3. **拷贝构造函数**：`new Person(existingPerson)`，在 C++ 社区更为常见，逻辑清晰但需手动维护。

判断应用场景时，规则很简单：如果被复制的对象中任何引用字段指向的对象**在克隆体生命周期内可能被修改**，就必须使用深拷贝。

### 原型注册表（Prototype Registry）

当系统中存在多种可克隆的原型时，通常引入一个**原型注册表**来统一管理。注册表本质上是一个 `Map<String, Prototype>`，客户端通过字符串键来检索并克隆所需原型：

```java
class PrototypeRegistry {
    private Map<String, Shape> registry = new HashMap<>();
    
    public void register(String key, Shape prototype) {
        registry.put(key, prototype);
    }
    
    public Shape getClone(String key) {
        return registry.get(key).clone(); // 每次调用返回全新副本
    }
}
```

注册表在程序启动时预先填充"昂贵对象"（如经过复杂计算初始化的地图图块、预加载完毕的角色模型），后续所有相同对象均从注册表克隆，避免重复初始化。这是原型模式性能价值的集中体现。

---

## 实际应用

**文档编辑器中的图形元素**：Microsoft Word 或 Keynote 的"复制粘贴"功能本质上就是原型模式。用户粘贴一个包含自定义字体、颜色、阴影效果的文本框时，系统克隆该文本框对象而非重新弹出配置对话框。

**游戏中的敌人生成**：策略游戏中同类敌人单位数量可达数百个，若每次 `new Soldier()` 都要重新加载贴图、解析属性表，帧率会严重下降。标准做法是为每种敌人类型创建一个"模板实例"存入注册表，战斗中所有同类单位均从该模板深拷贝生成。

**Spring 框架的 Prototype Scope**：Spring Bean 的 `scope="prototype"` 配置项直接得名于原型模式。每次从 ApplicationContext 请求该 Bean 时，容器返回的是一个全新实例（相当于调用 `clone()`），而非单例模式下的共享实例。

---

## 常见误区

**误区一：以为 Java 的 `Cloneable` 接口提供了克隆实现**
`Cloneable` 在 Java 中是一个**标记接口**，本身不包含任何方法。它只是告知 JVM 允许调用 `Object.clone()`；真正的克隆逻辑仍需开发者在子类中重写 `clone()` 方法。遗忘这一点会导致运行时抛出 `CloneNotSupportedException`，即使类已经实现了 `Cloneable`。

**误区二：浅拷贝对不可变对象足够安全，深拷贝总是必要的**
这个判断方向反了。对于 `String`、`Integer` 等不可变对象，浅拷贝是**完全安全且正确**的，因为其内容无法被修改，共享引用不会引发问题。盲目对所有字段深拷贝不仅浪费资源，还可能破坏对象的共享语义（例如共享同一个枚举常量是刻意设计）。

**误区三：原型模式与工厂模式可以随意互换**
两者解决的问题不同。工厂模式擅长根据参数决定实例化**哪个类**，但每次都从零开始构建对象；原型模式擅长快速复制一个**已配置完毕的具体实例**，保留其运行时状态。当需要"带状态的副本"而非"全新对象"时，工厂模式无法替代原型模式。

---

## 知识关联

**前置概念——工厂模式**：工厂模式解决了"谁负责创建对象"的问题，将实例化逻辑从客户端剥离。原型模式在此基础上进一步回答"当构造成本过高时如何创建对象"——以注册表取代工厂方法，以 `clone()` 取代 `new`。理解工厂模式中"将创建逻辑封装"的思路，有助于理解原型注册表为何也要统一管理克隆入口。

**后续概念——原型模式（游戏）**：游戏开发场景会将原型模式推向极限复杂度。游戏对象（GameObject）往往包含物理组件、渲染组件、AI行为树等深度嵌套的子系统，深拷贝策略的选择直接影响帧率；同时，游戏中的"预制体"（Prefab，如 Unity 引擎的核心概念）正是原型注册表的工程化实现，是学习原型模式在真实系统中规模化应用的最佳案例。