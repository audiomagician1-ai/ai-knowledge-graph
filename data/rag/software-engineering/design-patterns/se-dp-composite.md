---
id: "se-dp-composite"
concept: "组合模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["结构型"]

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
updated_at: 2026-03-26
---


# 组合模式

## 概述

组合模式（Composite Pattern）是一种结构型设计模式，其核心思想是将对象组织成树形结构，并通过统一的接口同等对待单个对象（叶节点）和对象集合（容器节点）。这样，客户端代码无需区分自己操作的是一片叶子还是整棵子树——调用方式完全一致。

该模式由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式命名。GoF 的原始定义是："将对象组合成树形结构以表示'部分-整体'的层次结构，使得用户对单个对象和组合对象的使用具有一致性。"这一定义精准捕捉了该模式的两大要素：树形层次与接口统一。

组合模式在文件系统、GUI 控件树、公司组织架构等现实场景中频繁出现，因为这些领域天然存在"容器可以嵌套容器"的递归结构。如果不使用该模式，客户端代码将充满 `instanceof` 判断，维护成本极高。

---

## 核心原理

### 三个角色构成最小骨架

组合模式由三个必要角色构成：

- **Component（抽象组件）**：声明叶节点和容器节点共有的接口，通常包含 `operation()`、`add(Component)`、`remove(Component)`、`getChild(int)` 等方法。
- **Leaf（叶节点）**：树的末端，不含子节点，实现 `operation()` 的具体业务逻辑，通常对 `add/remove` 抛出异常或留空。
- **Composite（容器节点）**：持有一个 `List<Component>` 子节点集合，其 `operation()` 实现为遍历子节点并逐一调用其 `operation()`，从而实现递归传播。

### 递归遍历与透明性权衡

容器节点的 `operation()` 方法本质上是一次深度优先遍历。以计算文件系统总大小为例，`Folder.getSize()` 的实现如下：

```
int getSize() {
    return children.stream()
                   .mapToInt(Component::getSize)
                   .sum();
}
```

`File.getSize()` 直接返回自身字节数，而 `Folder.getSize()` 则递归调用每个子组件。这种设计让"计算整棵子树的大小"与"计算单个文件的大小"共用同一条调用路径。

模式存在**透明模式**与**安全模式**两种变体：透明模式把 `add/remove` 放在 Component 接口上，客户端完全不区分叶与容器，但叶节点需要处理无意义的 `add` 调用；安全模式把 `add/remove` 仅放在 Composite 上，接口更纯粹但客户端有时需要向下转型。GoF 原书推荐透明模式优先，以维持接口的一致性。

### 与简单树结构的本质区别

普通树节点的遍历由外部调用方控制（通常是迭代器或显式递归），而组合模式把遍历逻辑封装在 `Composite.operation()` 内部，由树自身驱动。这意味着向树中新增一种叶节点类型时，客户端代码**零改动**，符合开闭原则（Open/Closed Principle）。

---

## 实际应用

**文件系统**：Linux 的 `du -sh` 命令计算目录大小，正是组合模式的经典实现——目录（Composite）递归统计子目录和文件（Leaf）的块数。

**GUI 框架**：Java Swing 中，`JPanel` 可以包含 `JButton`、`JLabel`，也可以包含另一个 `JPanel`。`Container.paint()` 方法遍历所有子组件依次调用其 `paint()`，这是组合模式在生产框架中的直接体现。

**公司组织架构**：CEO 下辖多个部门经理（Composite），部门经理下辖普通员工（Leaf）。统计全公司薪资总额时，调用 `CEO.getSalary()` 即可自动汇总所有层级——不需要知道每一层的具体节点数量。

**XML/HTML 解析**：DOM 树中，`Element` 节点可以包含子 `Element` 或 `TextNode`（Leaf）。浏览器渲染引擎对整棵 DOM 树调用 `render()`，通过组合模式将渲染指令递归传递到每一个文本节点。

---

## 常见误区

**误区一：叶节点必须实现 `add/remove` 并抛出异常**
许多教程让 Leaf 的 `add()` 直接抛出 `UnsupportedOperationException`，但这会破坏里氏替换原则（LSP）——客户端拿到一个 Component 引用后，无法安全地调用 `add`，必须先做类型检查。正确的设计选择是根据场景在透明模式与安全模式之间有意识地取舍，而非简单地"叶节点抛异常"。

**误区二：只要是树结构就该用组合模式**
组合模式的适用条件是**叶节点与容器节点需要被客户端以相同方式对待**。如果客户端本来就需要区分叶与容器的行为（例如，对文件执行编辑、对目录执行权限继承），强行套用组合模式反而会掩盖必要的类型差异，导致逻辑混乱。

**误区三：组合模式自带遍历能力，不需要迭代器**
组合模式内置的递归遍历是**固定的深度优先、前序遍历**。若客户端需要按层级遍历（BFS）、后序遍历或跳过特定子树，仅靠组合模式本身无法支持。这正是为什么组合模式常与迭代器模式配合使用——迭代器负责提供可切换的遍历策略，而组合模式负责维持树形结构本身。

---

## 知识关联

组合模式不依赖任何复杂的前置设计模式，入门门槛低，只需理解面向对象的接口与多态机制即可上手。学习组合模式时，重点掌握的是**Component 接口如何同时被 Leaf 和 Composite 实现**，以及**Composite 如何通过持有 `List<Component>` 实现无限深度的嵌套**。

学完组合模式后，自然引出**迭代器模式**（Iterator Pattern）。组合模式构建了一棵对象树，但该如何以不同顺序遍历这棵树，是迭代器模式要解决的问题。GoF 书中明确指出，迭代器模式常被用来遍历组合结构。在 Java 的 `java.awt.Component` 体系中，`Component` 同时承担了组合模式的 Component 角色，而 `Swing` 框架在其上叠加了遍历子组件的迭代能力，两种模式协同工作的痕迹清晰可见。