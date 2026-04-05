---
id: "se-dp-iterator"
concept: "迭代器模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 迭代器模式

## 概述

迭代器模式（Iterator Pattern）是一种行为型设计模式，它提供一种方法**顺序访问聚合对象中的各个元素，而又不暴露该对象的内部表示**。换言之，迭代器将"如何遍历集合"的逻辑从集合本身中剥离出来，封装在独立的迭代器对象中。

该模式最早由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式命名，书中给出的意图定义为："提供一种方法顺序访问一个聚合对象中的各个元素，且不需要暴露该对象的内部表示。"Java 从1.2版本起引入 `java.util.Iterator` 接口，Python 则通过实现 `__iter__` 和 `__next__` 两个双下划线方法使迭代器成为语言的内置机制。

迭代器模式之所以重要，在于它解决了一个具体的矛盾：当一个聚合对象（如链表、树、哈希表）对外提供遍历功能时，如果直接暴露内部数据结构，就会导致客户端与存储实现紧耦合。一旦内部存储从数组改为链表，所有遍历代码都需要修改。迭代器通过统一的 `hasNext()` / `next()` 接口屏蔽这一差异。

---

## 核心原理

### 四个核心角色

迭代器模式由四个角色构成，缺一不可：

- **Iterator（迭代器接口）**：声明 `hasNext(): boolean` 和 `next(): Element` 两个方法，部分实现还包含 `remove()` 方法。
- **ConcreteIterator（具体迭代器）**：实现迭代器接口，持有对聚合对象的引用，并维护当前遍历位置（通常是一个整数索引 `cursor`）。
- **Aggregate（聚合接口）**：声明 `createIterator(): Iterator` 工厂方法，负责生产对应的迭代器对象。
- **ConcreteAggregate（具体聚合）**：实现聚合接口，在 `createIterator()` 中返回 `new ConcreteIterator(this)`，将自身传入。

### 状态维护与遍历逻辑

具体迭代器必须独立维护遍历状态，这是迭代器模式区别于简单索引循环的关键。以数组聚合为例：

```
ConcreteIterator {
    private items[]       // 指向聚合对象的数组
    private cursor = 0    // 当前位置，初始为 0

    hasNext() → cursor < items.length
    next()    → return items[cursor++]
}
```

正因为状态保存在迭代器自身，同一聚合对象可以**同时存在多个独立的迭代器**，各自维护不同的 `cursor`，互不干扰。这是迭代器模式的核心优势之一，在多线程只读遍历场景下尤为重要。

### 外部迭代器 vs 内部迭代器

迭代器模式存在两种变体：

- **外部迭代器（External Iterator）**：客户端主动调用 `next()` 推进遍历，控制权在客户端。Java 的 `Iterator` 接口即为外部迭代器，灵活性更高，可在遍历中途中断或跳过元素。
- **内部迭代器（Internal Iterator）**：客户端将操作以回调函数形式传入迭代器，迭代器自行驱动遍历。Ruby 的 `each` 方法、JavaScript 的 `Array.forEach` 均属此类，代码更简洁，但无法在中途中断（除非抛出异常）。

GoF 书中将外部迭代器称为"主动迭代器"，内部迭代器称为"被动迭代器"。

---

## 实际应用

### Java 集合框架中的迭代器

Java 的 `ArrayList`、`LinkedList`、`HashSet` 均实现了 `Iterable<E>` 接口，该接口只有一个方法 `iterator()`，返回 `Iterator<E>` 对象。Java 5 引入的增强 for 循环（`for-each`）本质上是编译器将其展开为 `Iterator` 调用的语法糖：

```java
for (String s : list) { ... }
// 等价于：
Iterator<String> it = list.iterator();
while (it.hasNext()) { String s = it.next(); ... }
```

`ArrayList` 的内部类 `Itr` 持有一个 `int cursor` 和 `int expectedModCount`，后者用于检测并发修改——如果在遍历期间修改了集合大小，`next()` 会抛出 `ConcurrentModificationException`，这是迭代器模式在安全性上的具体实现细节。

### 文件系统树遍历

对目录树进行深度优先遍历时，可以将目录对象（实现自组合模式的 Composite 节点）包装为迭代器。迭代器内部维护一个显式栈（`Deque<File>`），`next()` 每次从栈顶弹出一个节点，若该节点为目录则将其子节点压栈。这使得调用者无需了解目录树的递归结构，只需循环调用 `hasNext()` / `next()` 即可完成全树遍历。

---

## 常见误区

### 误区一：迭代器模式只适用于线性结构

许多初学者认为迭代器只能用于数组或链表。实际上，迭代器模式同样适用于树（前序、中序、后序迭代器各不同）、图（BFS 迭代器使用队列，DFS 迭代器使用栈）和数据库结果集（`ResultSet` 本质上是数据库查询结果的迭代器）。不同的遍历策略可以实现为同一聚合对象的不同具体迭代器，彼此独立。

### 误区二：迭代器等同于 for 循环的封装

for 循环是语言语法，它将遍历逻辑硬编码在使用处，无法被传递、组合或替换。迭代器是**对象**，可以作为参数传入方法、存储在字段中、在多个地方共享同一遍历状态，也可以被装饰器包装（例如"过滤迭代器"在 `next()` 中跳过不满足条件的元素）。两者在封装粒度上有本质区别。

### 误区三：必须在迭代器中实现 remove() 方法

GoF 的原始定义中并不要求迭代器支持元素修改。Java 的 `Iterator` 接口中 `remove()` 是可选的，默认实现抛出 `UnsupportedOperationException`。只读迭代器（如只实现 `hasNext()` 和 `next()`）在绝大多数场景下已经足够，强行添加修改能力反而增加并发安全的复杂度。

---

## 知识关联

迭代器模式与**组合模式**有天然的协作关系：组合模式定义了树形对象结构（如文件系统、UI 控件树），但并未规定如何遍历这棵树；为组合模式的根节点提供一个迭代器，恰好填补了这一空缺，使客户端可以用统一接口遍历整个复合结构，无需手写递归。

**模板方法模式**中，父类定义算法骨架，子类填充具体步骤。迭代器模式的内部迭代器变体与此相似：聚合类提供遍历骨架（驱动循环），而每次迭代执行的操作由外部传入的回调决定。理解模板方法有助于区分"谁控制遍历节奏"这一核心问题。

在进阶学习**中介者模式**时，可以将两者对比：迭代器解耦的是"集合"与"遍历逻辑"，中介者解耦的是"多个对象之间的通信逻辑"。两者都是将某种交互行为从参与对象中抽离，但作用层面不同——迭代器针对单个聚合的内部访问，中介者针对多个对象之间的协作网络。