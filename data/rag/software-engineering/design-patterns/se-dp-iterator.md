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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 迭代器模式

## 概述

迭代器模式（Iterator Pattern）是一种行为型设计模式，它提供一种方法**顺序访问聚合对象中的各个元素，而又不暴露该对象的内部表示**。简单来说，迭代器将"遍历逻辑"从聚合对象中分离出来，封装成一个独立的迭代器对象，使客户端代码可以用统一的接口遍历列表、树、栈等不同的数据结构。

该模式最早由 Gang of Four（GoF）在 1994 年出版的《设计模式：可复用面向对象软件的基础》中正式命名和归类。其思想来源于 CLU 语言（1970 年代麻省理工学院开发）中的"generator"概念。GoF 将其归入行为型模式，因为迭代器的核心职责是定义对象之间的通信协议——客户端如何一步一步地"要求"集合提供下一个元素。

迭代器模式在现代语言中已成为标准基础设施：Java 的 `java.util.Iterator<E>` 接口、Python 的 `__iter__` / `__next__` 双协议、C++ 的 STL 迭代器体系，都是该模式的直接落地。理解迭代器模式能帮助开发者正确区分"遍历责任归属"——到底是集合自己管理遍历游标，还是外部迭代器持有游标——这直接影响多游标并发遍历是否可行。

---

## 核心原理

### 四个角色与结构

迭代器模式由四个角色构成：

| 角色 | 职责 |
|---|---|
| `Iterator`（抽象迭代器） | 声明 `hasNext()` 和 `next()` 方法 |
| `ConcreteIterator`（具体迭代器） | 持有对聚合对象的引用和当前游标位置 |
| `Aggregate`（抽象聚合） | 声明 `createIterator()` 工厂方法 |
| `ConcreteAggregate`（具体聚合） | 实现 `createIterator()`，返回对应的具体迭代器实例 |

核心接口通常只有两个必须实现的方法：`hasNext(): Boolean`（判断是否还有下一个元素）和 `next(): T`（返回当前元素并将游标前移一位）。某些实现还增加 `remove()` 支持在遍历时删除元素，但这是可选扩展。

### 游标与聚合的分离机制

迭代器的关键设计决策是**游标（cursor）存放在迭代器对象内部，而不是聚合对象内部**。这意味着可以同时创建多个迭代器实例，各自持有独立游标，互不干扰。例如对同一个 `ArrayList` 调用两次 `iterator()`，得到两个独立的 `Itr` 对象，两个游标可以分别处于不同位置。若游标存放于聚合内部（称为"内部迭代器"），则同一时刻只能有一个活跃的遍历位置。

### 外部迭代器 vs 内部迭代器

- **外部迭代器（External Iterator）**：客户端显式调用 `next()` 控制遍历节奏，Java 的 `Iterator` 接口属于此类。优点是客户端可以在任意时刻暂停、保存迭代状态。
- **内部迭代器（Internal Iterator）**：将遍历逻辑和处理逻辑打包成一个操作传入聚合，Ruby 的 `each` 方法、JavaScript 的 `Array.prototype.forEach` 属于此类。优点是代码简洁，但客户端无法中途暂停遍历（除非抛出异常）。

### 失效迭代器问题（Fail-Fast）

Java 的 `ArrayList` 内部维护一个 `modCount` 计数器，每次结构性修改（增删元素）都使其递增。迭代器在创建时记录 `expectedModCount = modCount`；每次调用 `next()` 时检查两者是否相等，不等则立即抛出 `ConcurrentModificationException`。这是"快速失败（fail-fast）"策略的具体实现，防止在遍历过程中集合被修改导致不可预期的行为。

---

## 实际应用

**场景一：遍历组合树结构**

组合模式（Composite Pattern）构建出树形结构（如文件系统目录树），但本身不定义遍历顺序。为组合树实现一个迭代器（例如深度优先的 `CompositeIterator`），可以让客户端用统一的 `while (it.hasNext()) { it.next(); }` 代码遍历整棵树，无需关心叶节点和容器节点的区别。迭代器内部使用 `java.util.Stack` 维护待访问节点队列，实现前序遍历。

**场景二：数据库结果集**

JDBC 的 `ResultSet` 本质是一个迭代器：`rs.next()` 将游标移到下一行并返回是否有数据，`rs.getString("column")` 读取当前行数据。这将数据库驱动的底层缓冲区管理完全隐藏，客户端只需调用统一接口处理查询结果。

**场景三：Python 生成器作为惰性迭代器**

Python 的 `yield` 关键字将普通函数变为生成器函数，返回一个同时实现 `__iter__` 和 `__next__` 的生成器对象。这是迭代器模式的惰性求值变体——只在调用 `next()` 时才计算下一个值，适合处理无限序列（如斐波那契数列）或超大文件逐行读取，无需将全部数据载入内存。

---

## 常见误区

**误区一：认为迭代器只能顺序遍历，不能随机访问**

标准的 GoF 迭代器接口确实只定义顺序访问，但这是最小接口设计，不是技术限制。Java 的 `ListIterator<E>` 在 `Iterator<E>` 基础上增加了 `hasPrevious()`、`previous()`、`nextIndex()`、`previousIndex()` 等方法，支持双向遍历和索引访问。因此迭代器模式支持哪些遍历方向取决于具体接口设计，而非模式本身的约束。

**误区二：以为迭代器模式与 for-each 语法无关**

Java 的增强 for 循环 `for (T item : collection)` 在编译期会被转换为显式的迭代器调用：先调用 `collection.iterator()` 获取迭代器，再在循环体中调用 `hasNext()` 和 `next()`。任何实现了 `java.lang.Iterable<T>` 接口（只需实现 `iterator()` 方法）的类都可以使用 for-each 语法。因此 for-each 是迭代器模式的语法糖，两者本质相同。

**误区三：认为每次遍历都必须新建迭代器对象，性能必然低下**

对于简单的数组遍历，每次创建迭代器对象确实带来额外的堆分配开销。但 JVM 的即时编译器（JIT）会对短生命周期的小对象进行**栈上分配（Stack Allocation）**优化，使迭代器对象根本不进入堆，从而消除 GC 压力。实际性能测试表明，在 HotSpot JVM 上，使用迭代器遍历 `ArrayList` 与直接下标访问的性能差距通常在 5% 以内。

---

## 知识关联

**前置概念——组合模式**：组合模式解决"树形结构的统一操作"问题，但没有规定如何遍历这棵树。迭代器模式恰好填补这个空白：为组合树提供一个封装了递归遍历逻辑的迭代器，使客户端不必自行编写递归代码。GoF 书中专门讨论了"迭代器 + 组合"的协作方式，两者是天然的配对模式。

**延伸方向——访问者模式（Visitor Pattern）**：迭代器负责"取出每一个元素"，访问者负责"对取出的元素做什么操作"。两者配合使用时，外层迭代器驱动遍历，内层访问者执行类型分发处理，实现遍历与操作的双重解耦。

**语言级支持**：理解迭代器模式是读懂 Java Streams API、Python itertools 模块、C++ STL 算法库（`std::for_each`、`std::find` 等均接受迭代器范围 `[first, last)`）的前提。这三套标准库都以迭代器作为算法与数据结构之间的统一抽象层。
