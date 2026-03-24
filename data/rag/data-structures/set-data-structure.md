---
id: "set-data-structure"
concept: "集合"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 3
is_milestone: false
tags: ["集合论"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 集合

## 概述

集合（Set）是一种存储**无序、不重复**元素的数据结构。与列表不同，集合中每个元素只能出现一次；与字典不同，集合只存储键而不存储值。Python 中原生支持集合类型，`set()` 构造函数或花括号 `{1, 2, 3}` 均可创建集合，但空集合必须使用 `set()` 而非 `{}`（后者创建的是空字典）。

集合的概念源自数学中的集合论，由德国数学家格奥尔格·康托尔（Georg Cantor）于19世纪70年代系统化建立。计算机科学将其实现为基于哈希表的数据结构——Python 的 `set` 底层与 `dict` 共享相同的哈希机制，这意味着集合中的元素必须是**可哈希的**（hashable），即元素必须是不可变类型，如整数、字符串、元组，而列表和字典不能作为集合元素。

在 AI 工程中，集合的最大价值在于**O(1) 平均时间复杂度的成员检测**。当需要判断一个样本 ID 是否已被处理、某个词汇是否在词表中、某条边是否已存在于图结构时，集合的查找效率远超列表的 O(n) 线性扫描。

---

## 核心原理

### 哈希表实现与时间复杂度

Python 的 `set` 底层是一张开放寻址哈希表。添加元素 `x` 时，Python 计算 `hash(x)`，将其映射到桶（bucket）位置；查找时同样先计算哈希值，直接定位桶，无需逐一比较。因此：

- **添加（add）**：平均 O(1)，最坏 O(n)（哈希碰撞导致大量探测）
- **成员检测（in）**：平均 O(1)
- **删除（remove/discard）**：平均 O(1)
- **遍历**：O(n)

哈希表的负载因子（load factor）超过约 2/3 时，Python 会自动扩容并重新哈希，这一操作的摊销代价保证了整体 O(1) 性能。

### 四种集合运算及其语法

集合论的四种基本运算在 Python 中都有对应的运算符和方法：

| 运算 | 运算符 | 方法 | 含义 |
|------|--------|------|------|
| 并集 | `A \| B` | `A.union(B)` | 属于 A 或属于 B 的所有元素 |
| 交集 | `A & B` | `A.intersection(B)` | 同时属于 A 和 B 的元素 |
| 差集 | `A - B` | `A.difference(B)` | 属于 A 但不属于 B 的元素 |
| 对称差 | `A ^ B` | `A.symmetric_difference(B)` | 属于 A 或 B 但不同时属于两者 |

对称差 `A ^ B` 等价于 `(A - B) | (B - A)`，在检测两个数据集之间的**新增或删除样本**时非常直观。

### frozenset 与可哈希性约束

Python 提供 `frozenset`——集合的不可变版本。`frozenset` 创建后无法添加或删除元素，但因为它是不可变的，所以它本身是可哈希的，可以作为另一个集合的元素或字典的键。例如，要表示"一组特征组合"作为字典的键时，必须使用 `frozenset({"age", "income"})` 而非普通 `set`。

---

## 实际应用

### 训练数据去重

在构建机器学习数据集时，重复样本会导致模型过拟合某些数据点。使用集合对样本 ID 或文本哈希值去重是最直接的方案：

```python
seen_hashes = set()
unique_samples = []
for sample in raw_data:
    h = hash(sample["text"])
    if h not in seen_hashes:
        seen_hashes.add(h)
        unique_samples.append(sample)
```

这比用列表维护已见元素，将去重操作从 O(n²) 降至 O(n)。

### 词表（Vocabulary）构建

NLP 任务中，词表本质上就是一个集合——收集所有训练文本出现过的唯一词元（token）。`vocab = set(token for doc in corpus for token in doc)` 一行代码即可完成，随后再将其转换为排序列表分配索引。词表查询（判断一个词是否为 OOV——Out of Vocabulary）使用集合的 `in` 操作，每次查询平均 O(1)。

### 图神经网络中的邻居去重

在构建图结构时，同一对节点可能在原始边列表中出现多次（无向图的正反向重复）。使用 `frozenset` 作为边的标识符可以优雅地消除重复边：

```python
edge_set = set()
for u, v in raw_edges:
    edge_set.add(frozenset((u, v)))
```

### 特征交叉验证

在检验两个模型使用的特征集合是否一致时，集合差集能直接找出差异：

```python
missing = model_A_features - model_B_features
extra   = model_B_features - model_A_features
```

---

## 常见误区

### 误区一：用集合存储顺序敏感的数据

集合是**无序的**，Python 3.7+ 的 `dict` 保留插入顺序，但 `set` 从不保证顺序。遍历集合 `{3, 1, 2}` 的输出顺序取决于哈希值，不一定是 `3, 1, 2`。如果业务逻辑需要按插入顺序维护唯一元素（例如保留首次出现的词），应使用 `dict.fromkeys(iterable)` 代替集合，利用字典的有序性实现有序去重。

### 误区二：混淆 remove 和 discard

`set.remove(x)` 在 `x` 不存在时抛出 `KeyError`；`set.discard(x)` 在元素不存在时静默忽略。在 AI 管道中批量清洗标签集时，若不确定某标签是否存在，应使用 `discard` 避免异常中断流程。

### 误区三：认为集合运算结果总是原集合类型

`set & frozenset` 的结果类型取决于**左操作数**：`set({1,2}) & frozenset({2,3})` 返回 `set`，而 `frozenset({1,2}) & set({2,3})` 返回 `frozenset`。在混合使用两种集合类型时，若后续需要将结果存入另一个集合或字典键，需注意显式转换类型。

---

## 知识关联

**与字典（dict）的关系**：集合可以理解为"只有键、没有值的字典"。两者底层均使用哈希表，对元素的可哈希性要求相同，时间复杂度特性一致。学习集合之前掌握字典的哈希机制，可以直接复用对碰撞处理、扩容策略的理解。集合的 `add/remove` 对应字典的 `__setitem__`/`__delitem__`，但集合没有键值对的概念。

**在 AI 工程中的定位**：集合是实现快速成员检测和集合代数运算的专用工具。在数据预处理阶段，集合用于去重和过滤；在特征工程阶段，集合代数用于特征对齐；在图算法阶段，集合维护已访问节点（如 BFS/DFS 的 `visited` 集合）。掌握集合后，可以将数据管道中大量 O(n) 的线性扫描替换为 O(1) 的哈希查找，这对处理百万级以上样本的 AI 工程任务有实质性的性能影响。
