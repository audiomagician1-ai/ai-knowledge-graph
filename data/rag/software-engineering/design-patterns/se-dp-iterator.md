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

迭代器模式（Iterator Pattern）是一种行为型设计模式，它提供一种统一的方式来顺序访问聚合对象（如列表、树、图等集合结构）中的各个元素，而无需暴露该对象的内部表示。其核心思想是将"遍历逻辑"从聚合对象本身剥离出来，封装进一个独立的迭代器对象。

该模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式提出，是书中23种模式之一，归类于行为型模式。迭代器模式的原始动机来自于STL（Standard Template Library）的设计需求：在C++中，需要一种与容器类型无关的统一遍历接口，使得`std::list`、`std::vector`、`std::set`等不同容器都能通过相同的`begin()`/`end()`语义进行迭代。

迭代器模式的重要性在于它彻底解耦了"集合的存储结构"与"遍历算法"。同一个集合可以同时拥有多个独立的迭代器，每个迭代器维护自己的当前位置（游标），互不干扰。这使得对同一集合进行多路并发遍历成为可能，且不需要修改集合类本身的任何代码。

## 核心原理

### 四个基本参与角色

迭代器模式由四个角色构成：**Iterator（抽象迭代器）**、**ConcreteIterator（具体迭代器）**、**Aggregate（抽象聚合）**、**ConcreteAggregate（具体聚合）**。

- `Iterator` 接口定义 `hasNext(): boolean` 和 `next(): T` 两个核心方法（不同语言中命名略有差异，Java中是`hasNext()`/`next()`，Python中是`__next__()`配合`StopIteration`异常）。
- `ConcreteIterator` 持有对具体聚合对象的引用，并维护一个整数游标（cursor，初始值为0），`next()` 返回当前元素并将游标加1。
- `ConcreteAggregate` 实现 `createIterator()` 工厂方法，返回与自身绑定的具体迭代器实例。

### 内部迭代器 vs 外部迭代器

**外部迭代器**（External Iterator）将遍历的控制权交给客户端，客户端显式调用 `next()` 推进游标——Java的 `Iterator<T>` 接口和C++的迭代器均属此类。**内部迭代器**（Internal Iterator）则由迭代器本身驱动遍历，客户端只需提供一个操作（通常是回调函数或Lambda）——Ruby的 `Array#each`、Python的 `map()`/`filter()` 属此类。外部迭代器更灵活，可以暂停、恢复遍历，支持两个迭代器之间的同步比较；内部迭代器代码更简洁，但无法轻易中途中止（需要抛出异常来打破遍历）。

### 游标机制与快照迭代器

标准实现中，迭代器持有聚合对象的引用而非副本，游标指向实际数据。这意味着如果在遍历过程中修改集合（增删元素），游标可能失效——Java的 `ArrayList` 迭代器内置了 `modCount` 字段检测并发修改，一旦检测到会抛出 `ConcurrentModificationException`。**快照迭代器**（Snapshot Iterator）则在创建时对集合制作一份完整副本，游标遍历副本，牺牲内存换取安全性，适用于写多读多的并发场景。

### 与组合模式的结合：复合迭代器

当聚合对象本身是一棵树（即使用了组合模式构建的复合结构）时，需要**复合迭代器**（Composite Iterator）。其内部维护一个栈（Stack）而非单一整数游标，每次遇到叶子节点则返回元素，遇到容器节点则将其子迭代器压栈，从而实现深度优先遍历。这正是组合模式与迭代器模式最典型的配合场景：由组合模式负责构建层级结构，由迭代器模式负责展平（flatten）该结构以进行统一遍历。

## 实际应用

**Java集合框架**是迭代器模式最典型的工业级实现。`java.util.Iterator<E>` 接口定义了 `hasNext()`、`next()`、`remove()` 三个方法，`java.lang.Iterable<T>` 接口仅包含 `iterator()` 工厂方法。只要实现了 `Iterable`，该类的实例就可以直接用于Java 5引入的增强型for循环（`for-each` 语法糖），编译器会自动将其展开为迭代器调用。

**Python生成器**（Generator）是迭代器模式的语言级原生支持。使用 `yield` 关键字定义的函数会自动创建一个实现了 `__iter__()` 和 `__next__()` 协议的迭代器对象，遍历文件系统目录时常见如下模式：

```python
def walk_files(directory):
    for entry in os.scandir(directory):
        if entry.is_dir():
            yield from walk_files(entry.path)  # 递归委托，替代复合迭代器的栈
        else:
            yield entry.path
```

**数据库游标（Cursor）**是迭代器模式在持久化层的直接映射。SQL查询结果集不会一次性加载到内存，而是通过游标逐行提取（`fetchone()` / `fetchmany(n)`），迭代器的 `next()` 对应一次网络往返或磁盘读取，延迟求值（Lazy Evaluation）避免了对百万行结果集的全量内存占用。

## 常见误区

**误区一：认为迭代器只能进行单向顺序遍历。** 标准迭代器接口确实只定义正向遍历，但迭代器模式并不限制此点。`java.util.ListIterator<E>` 在 `Iterator<E>` 基础上额外提供了 `hasPrevious()`/`previous()` 支持双向遍历，还提供了 `nextIndex()`/`previousIndex()` 暴露当前游标位置。C++的随机访问迭代器（Random Access Iterator）甚至支持 `it += n` 操作，游标可以任意跳跃。

**误区二：迭代器与for循环等价，只是语法形式不同。** 实际上迭代器的价值在于统一了异构集合的遍历接口。一个接受 `Iterator<Shape>` 参数的方法，可以无差别地处理 `ArrayList<Shape>`、`LinkedList<Shape>`、自定义的树形结构，甚至远程分页数据源——这些集合的内部结构完全不同，但迭代器将差异封装，使调用方代码零修改。这是普通for循环（依赖索引和`size()`）无法做到的。

**误区三：认为迭代器模式引入了过多类，增加复杂度，应改用Lambda回调。** 对于简单的单次内部遍历，Lambda（内部迭代器）确实更简洁。但当需要"暂停遍历并保存进度"、"多个迭代器并行扫描同一集合"或"将遍历结果作为惰性流传递给多个下游处理器"时，持有游标状态的外部迭代器对象不可替代。Java 8的 `Stream` API底层依赖 `Spliterator`（可拆分迭代器）而非简单Lambda，正说明了这一点。

## 知识关联

迭代器模式以**组合模式**为重要前置知识：当被遍历的聚合对象是由组合模式构建的树形结构时，单纯的整数游标无法胜任，必须使用持有栈的复合迭代器来实现深度优先或广度优先遍历。两个模式合用时，组合模式的 `Component` 接口通常会增加一个 `createIterator()` 方法，让每种节点（叶子或容器）返回适合自身结构的迭代器。

在更广泛的设计模式体系中，迭代器模式与**工厂方法模式**存在结构性联系：聚合类的 `createIterator()` 本质上就是一个工厂方法，将具体迭代器类的实例化延迟到子类中决定。在现代编程语言设计中，迭代器协议已演化为响应式流（Reactive Streams）和异步迭代器（如JavaScript的 `AsyncIterator`、Python的 `async for`）的基础，这些扩展将迭代器的 `next()` 返回值从同步值改为 `Promise`/`Future`，使迭代器模式能够跨越I/O边界进行惰性数据流处理。
