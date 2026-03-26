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
quality_tier: "B"
quality_score: 46.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.519
last_scored: "2026-03-22"
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

组合模式（Composite Pattern）是一种结构型设计模式，它将对象组织成树形结构，使客户端能够以完全相同的方式处理单个对象（叶节点）和对象集合（组合节点）。这个"统一处理"的思想是组合模式最本质的特征：调用者无需判断当前操作的是一片叶子还是整棵子树，对外接口完全一致。

组合模式由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式命名，书中将其归类为结构型模式第7号。其灵感来源于图形编辑器的实际需求——绘图软件中，"圆形"是一个单独图元，而"由若干图元组成的图形组"也需要支持移动、缩放、渲染等相同操作，这促使作者将二者抽象为统一接口。

组合模式的价值在于消除客户端代码中大量的 `instanceof` 判断和条件分支。若没有组合模式，遍历文件系统时就必须写"如果是文件则读取，如果是文件夹则递归"的分叉逻辑；引入组合模式后，文件和文件夹都实现同一个 `Component` 接口，遍历代码只需调用 `component.getSize()` 即可，树的深度无论多深，调用方式永不改变。

---

## 核心原理

### 三个角色的定义

组合模式由三个固定角色构成：

- **Component（抽象构件）**：定义叶节点和组合节点共有的接口，通常包含 `operation()`、`add(Component c)`、`remove(Component c)`、`getChild(int i)` 等方法。
- **Leaf（叶节点）**：树的末端节点，不包含子节点。它实现 `operation()` 的具体逻辑，但对 `add/remove/getChild` 这类管理子节点的方法通常抛出 `UnsupportedOperationException`。
- **Composite（组合节点）**：包含子节点列表（`List<Component> children`），其 `operation()` 的实现是遍历所有子节点并递归调用各子节点的 `operation()`，自身不做具体业务计算。

### 透明模式与安全模式的取舍

组合模式存在两种实现变体，在接口设计上有根本区别：

- **透明模式**：将 `add/remove/getChild` 方法定义在 `Component` 接口中。优点是客户端完全不需要区分叶节点和组合节点（透明性最强）；缺点是叶节点被迫实现无意义的管理方法。
- **安全模式**：`Component` 接口只定义 `operation()`，管理方法仅在 `Composite` 类中定义。优点是叶节点接口干净；缺点是调用管理方法前必须做类型转换 `(Composite) component`，破坏了部分透明性。

GoF 原书推荐透明模式，但 Java 标准库（如 `javax.swing.JComponent`）更倾向安全模式。选择哪种变体取决于是否希望牺牲类型安全换取调用便利。

### 递归结构与终止条件

组合节点的 `operation()` 天然形成递归调用链。以计算目录大小为例，其逻辑可以表示为：

```
getSize(node) =
    若 node 是 Leaf：返回 node.fileSize
    若 node 是 Composite：返回 Σ getSize(child) for child in children
```

递归的自然终止条件是到达叶节点。若树中存在环形引用（某个子节点的子节点又指向祖先节点），递归将无限循环，因此组合模式要求树结构严格无环（DAG 也需要额外处理）。

---

## 实际应用

**文件系统**是组合模式最经典的应用场景。Linux 文件系统中，`File` 是叶节点，`Directory` 是组合节点，`ls -lR`（递归列出目录）正是对根节点调用一次 `list()` 触发全树递归遍历的典型案例。

**GUI 组件树**大量使用组合模式。Java Swing 中，`JButton` 是叶节点，`JPanel` 是组合节点，二者都继承自 `java.awt.Component`，调用 `panel.paint(g)` 时，`JPanel` 的 `paint()` 方法会自动递归调用其所有子组件的 `paint()`——这段逻辑在 JDK 源码 `java.awt.Container#paint()` 中可直接查看。

**组织架构树**也是典型场景：公司中"员工"是叶节点，"部门"是组合节点，计算某部门总薪资时，只需对该部门节点调用 `getSalary()`，它会自动将所有子部门和直属员工的薪资递归累加，HR 系统无需关心层级深度。

**XML/HTML 的 DOM 树**解析同样依赖组合模式：`TextNode` 是叶节点，`Element` 是组合节点，`document.getElementById("root").innerHTML` 的赋值操作会递归影响该元素下的所有子节点。

---

## 常见误区

**误区一：叶节点也必须实现 add/remove 方法，认为这是设计缺陷。**  
这只在透明模式下发生，且这是有意为之的权衡。叶节点的 `add()` 可以直接抛出 `UnsupportedOperationException` 并附带明确错误信息，这并不违反里氏替换原则（LSP）的精神——调用方在透明模式下本不应调用叶节点的管理方法，若调用则视为编程错误。解决方案是改用安全模式，而非认为整个模式有缺陷。

**误区二：只要是树形结构，都必须用组合模式。**  
组合模式的关键前提是"叶节点和组合节点需要被统一对待"。如果业务逻辑中叶节点和组合节点的操作完全不同（比如叶节点需要详细渲染参数，组合节点仅做布局计算），强行抽象为同一接口反而会导致接口臃肿。判断是否适用组合模式，核心问题是："客户端是否真的需要无差别地调用叶节点和组合节点？"

**误区三：组合模式等同于递归算法。**  
组合模式是一种对象结构的组织方式，递归只是遍历这种结构时自然产生的调用方式。完全可以用栈（Stack）将递归改写为迭代方式遍历组合树，组合模式的结构本身不变。此外，组合节点的 `operation()` 也不一定非得遍历所有子节点——例如"短路求值"逻辑中，找到第一个满足条件的子节点后即可停止遍历。

---

## 知识关联

**前置基础**：组合模式不依赖其他设计模式的知识，但需要熟悉面向对象中的接口/抽象类概念，以及多态调用机制——`Component` 引用指向 `Leaf` 或 `Composite` 实例时，运行时能正确分派到对应子类的 `operation()` 方法，这是组合模式得以运作的底层基础。

**后续扩展：迭代器模式**。组合树构建完成后，常见需求是"遍历树中所有节点"。将迭代器模式应用于组合树，可以为客户端提供 `iterator()` 方法，返回一个能够按前序、后序或层序遍历整棵树的迭代器对象，从而将"如何遍历"的逻辑与"如何使用遍历结果"的逻辑彻底分离。GoF 书中专门讨论了"组合迭代器"的实现——其核心是维护一个节点栈，每次调用 `next()` 时弹出当前节点并将其子节点压入栈中。

**横向关联**：装饰器模式（Decorator）与组合模式同样使用了递归对象结构，但装饰器的目的是为单个对象动态附加职责，而组合模式的目的是表达部分-整体的层级关系；前者是链状结构，后者是树状结构，两者经常在 GUI 框架中同时出现。