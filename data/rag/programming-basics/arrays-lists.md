---
id: "arrays-lists"
concept: "数组/列表"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["数据类型"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 数组/列表

## 概述

数组（Array）和列表（List）是用于存储**有序元素集合**的数据结构，其核心特征是通过整数索引（从 0 开始）访问任意位置的元素。与单个变量只能存储一个值不同，一个列表可以在同一个变量名下管理数百万个元素，并保持它们的排列顺序。

Python 的 `list` 是 AI 工程中最常用的数据容器，其前身可追溯到 1960 年代 FORTRAN 和 C 语言中的静态数组。Python 列表在此基础上进化为**动态数组**，允许在运行时随意增删元素，而 C 语言原生数组一旦声明大小便无法更改。理解这一历史演变有助于解释为何 Python 列表在灵活性上优于传统数组，但在内存效率上弱于 NumPy 的 `ndarray`。

在 AI 工程中，列表是数据预处理管道的基础载体。一批训练样本的文件路径、一段文本分词后的 token 序列、一个神经网络各层的维度配置（如 `[128, 64, 32, 10]`）——这些都依赖列表来表达有序、可迭代的信息集合。

---

## 核心原理

### 索引与切片机制

Python 列表使用**零基索引**（zero-based indexing），即第一个元素的索引为 `0`，最后一个元素的索引为 `len(list) - 1`。同时支持**负索引**，`-1` 表示最后一个元素，`-2` 表示倒数第二个，依此类推。

切片语法 `list[start:stop:step]` 可以提取子列表。例如 `tokens[2:8:2]` 从索引 2 开始，到索引 7 结束，每隔一个取一个元素。`stop` 位置的元素**不包含在结果中**，这是初学者最容易忽略的规则。切片操作返回原列表的**浅拷贝**（shallow copy），修改切片不会影响原列表中的不可变元素，但若列表元素本身是可变对象（如另一个列表），则共享引用。

### 动态数组的内存增长策略

Python `list` 底层是一块连续内存区域，当元素数量超过当前分配容量时，Python 解释器会申请一块**约 1.125 倍**当前容量的新内存，将所有元素复制过去，再释放旧内存。这一策略称为**过度分配（over-allocation）**，使得 `append()` 操作的均摊时间复杂度为 O(1)，但 `insert(0, x)` 在列表头部插入元素需要移动所有现有元素，时间复杂度为 O(n)。

可用 `sys.getsizeof()` 验证这一机制：一个空列表占 56 字节，添加第一个元素后跳至 88 字节，因为 Python 预先分配了 4 个元素的空间。

### 列表推导式（List Comprehension）

列表推导式是 Python 创建列表最简洁的方式，语法为：

```python
new_list = [expression for item in iterable if condition]
```

例如，从原始数值列表中提取所有大于 0.5 的置信度分数并平方：

```python
high_conf = [score**2 for score in predictions if score > 0.5]
```

与等价的 `for` 循环相比，列表推导式在 CPython 中执行速度通常快 **10%–35%**，因为它在底层使用专门的字节码指令 `LIST_APPEND`，减少了属性查找开销。

### 常用操作的时间复杂度

| 操作 | 时间复杂度 |
|------|-----------|
| `list[i]` 随机访问 | O(1) |
| `list.append(x)` | O(1) 均摊 |
| `list.insert(i, x)` | O(n) |
| `x in list` 成员检测 | O(n) |
| `list.sort()` | O(n log n) |

---

## 实际应用

**场景一：构建 mini-batch 索引**  
训练神经网络时，通常用列表存储数据集的样本索引，再随机打乱后按 batch_size 切片：

```python
indices = list(range(10000))        # [0, 1, 2, ..., 9999]
random.shuffle(indices)
batch = indices[0:32]               # 第一个 batch 的 32 个样本索引
```

**场景二：逐步收集损失值**  
训练循环中用 `append()` 动态记录每个 epoch 的损失，训练结束后统一绘图：

```python
loss_history = []
for epoch in range(100):
    loss = train_one_epoch(model)
    loss_history.append(loss)       # O(1) 均摊操作
```

**场景三：NLP 文本分词结果**  
将句子分词后的 token 列表传入词嵌入层，其中列表的**顺序**直接决定了序列模型（如 LSTM、Transformer）对上下文的理解：

```python
tokens = ["the", "cat", "sat", "on", "the", "mat"]
token_ids = [vocab[t] for t in tokens]   # [3, 142, 87, 12, 3, 201]
```

---

## 常见误区

**误区一：混淆浅拷贝与深拷贝导致数据污染**  
执行 `b = a` 时，`b` 和 `a` 指向**同一个列表对象**，修改 `b[0]` 会同时改变 `a[0]`。即使使用 `b = a[:]` 或 `b = list(a)` 进行浅拷贝，若列表元素是嵌套列表，内层列表仍共享引用。在 AI 工程的数据增强管道中，若不加注意，同一批样本会被多次修改叠加。正确做法是 `import copy; b = copy.deepcopy(a)`。

**误区二：将列表用于大规模数值计算**  
Python 列表中每个元素是独立的 Python 对象，存储 100 万个 `float` 约占 **8 MB**（每个对象 24 字节 + 指针 8 字节），而 NumPy `ndarray` 同等数据仅占约 **7.6 MB** 且支持向量化运算，速度快 10–100 倍。对于矩阵运算、批量激活值计算等场景，应始终优先使用 `numpy.array`，而非 Python 原生列表。

**误区三：认为 `in` 操作符在列表中是快速查找**  
`x in list` 需要从头到尾逐个比较，时间复杂度为 O(n)。当需要频繁检查某个词是否在词汇表中时，若词汇表是列表，查询 5 万个词每次都要线性扫描。正确做法是将词汇表转为 `set` 或 `dict`，使查找降至 O(1)。

---

## 知识关联

**与变量与数据类型的关系**：列表本身是一种数据类型，其元素可以是之前学过的任意基础类型（`int`、`float`、`str`、`bool`），也可以是列表本身（嵌套列表），从而构成二维矩阵的朴素表示形式。

**通向字典/映射**：当需要通过"名字"而非"位置"来访问数据时（例如用 `"learning_rate"` 直接获取值），列表的整数索引就显得笨拙，这直接催生了字典结构的需求。

**通向数组内部原理**：本文提到的动态扩容策略和内存连续性，正是「数组内部原理」的核心议题，届时将深入分析 CPython 的 `listobject.c` 源码中 `list_resize()` 函数的具体实现。

**通向栈与队列**：Python 列表通过 `append()` + `pop()` 可直接模拟栈（LIFO），通过 `collections.deque` 可高效实现队列（FIFO）——理解列表操作的时间复杂度差异，是选择正确队列实现方式的前提。