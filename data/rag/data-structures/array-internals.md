---
id: "array-internals"
concept: "数组内部原理"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 3
is_milestone: false
tags: ["线性"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 数组内部原理

## 概述

数组（Array）是一种将相同类型的元素存储在**连续内存地址**中的线性数据结构。其本质特征是：第 `i` 个元素的内存地址可由公式 `address(i) = base_address + i × element_size` 精确计算，其中 `base_address` 为数组首元素地址，`element_size` 为单个元素占用的字节数。正是这个公式赋予了数组 O(1) 的随机访问能力。

数组的概念可以追溯到 1950 年代的 FORTRAN 语言——人类历史上第一门高级编程语言。FORTRAN 于 1957 年发布时就将数组作为核心数据类型，并规定数组元素必须在内存中连续排列。这一设计决策影响了此后几乎所有编程语言对数组的实现方式。

在 AI 工程领域，理解数组内部原理极为关键：NumPy 的 `ndarray`、PyTorch 的 `Tensor`，其底层均依赖连续内存布局实现向量化计算（SIMD 指令）。若数组内存不连续，GPU 无法高效地批量加载数据，训练速度会下降数倍乃至数十倍。

---

## 核心原理

### 连续内存分配与地址计算

数组在创建时，操作系统会一次性分配 `n × element_size` 字节的连续内存块。以一个存储 `int32`（4 字节）的数组 `[10, 20, 30, 40]` 为例，若首地址为 `0x1000`，则：

- `arr[0]` 位于 `0x1000`
- `arr[1]` 位于 `0x1004`
- `arr[2]` 位于 `0x1008`
- `arr[3]` 位于 `0x100C`

CPU 访问 `arr[2]` 时，不需要遍历前两个元素，直接计算 `0x1000 + 2×4 = 0x1008` 后取址，这就是 O(1) 随机访问的根本来源。

### 多维数组的行主序与列主序

二维数组在内存中仍是一维线性排列，关键在于元素的排列顺序。**行主序（Row-major）**——C、Python（NumPy 默认）采用——将同一行的元素相邻存储；**列主序（Column-major）**——Fortran、MATLAB 采用——将同一列的元素相邻存储。

对于 3×3 矩阵，行主序下元素 `M[i][j]` 的地址偏移为 `(i×3 + j) × element_size`；列主序下则为 `(j×3 + i) × element_size`。在 AI 训练中，若矩阵乘法的访问模式与存储顺序不一致，会导致大量 **Cache Miss**，实测可使矩阵乘法速度降低 3～10 倍。NumPy 提供 `np.ascontiguousarray()` 函数可将数组强制转为行主序连续内存。

### 动态数组的扩容机制

Python 的 `list` 和 C++ 的 `std::vector` 均是动态数组，底层通过**预分配+倍增扩容**实现。以 CPython 实现为例，当 `list` 需要扩容时，新容量约为当前容量的 **1.125 倍**（实际公式为 `new_size = old_size + (old_size >> 3) + 6`）。这与 Java `ArrayList` 的 1.5 倍扩容策略不同，也与 C++ `std::vector` 的 2 倍扩容不同。

扩容时，系统会申请新的连续内存块，将旧数据全部复制过去，再释放旧内存——这是 `list.append()` 均摊时间复杂度为 O(1) 而最坏情况为 O(n) 的根本原因。频繁扩容会导致内存碎片化，在处理超大规模数据集时应预先使用 `list = [None] * n` 或 NumPy 预分配数组。

### 缓存局部性（Cache Locality）

现代 CPU 的 L1 缓存通常为 32～64 KB，缓存行（Cache Line）大小通常为 64 字节。当访问 `arr[0]` 时，CPU 不止加载一个元素，而是将包含 `arr[0]` 的整个 64 字节缓存行（即 16 个 `int32` 元素）一并载入缓存。顺序遍历数组时，后续访问 `arr[1]` 到 `arr[15]` 直接命中缓存（Cache Hit），速度比随机访问链表节点快约 **100 倍**。这是数组在顺序遍历场景下远优于链表的底层物理原因。

---

## 实际应用

**NumPy 数组的内存视图（View）与副本（Copy）**：`arr[::2]` 产生的是原数组的视图，不占用新内存，仅改变步幅（stride）元数据；而 `arr[[0, 2, 4]]` 的花式索引必须创建副本，因为不规则索引无法用连续步幅描述。在 AI 数据预处理中，错误地修改视图会意外改变原始数据集，而无谓的副本操作则浪费 GPU 显存。

**Tensor 的 `contiguous()` 问题**：PyTorch 中对 Tensor 进行 `transpose()` 操作后，其内存布局变为非连续（strides 不再单调），此时若直接调用 `view()` 会抛出 `RuntimeError`。解决方法是先调用 `.contiguous()` 重新整理内存为连续布局，再调用 `view()`。这一现象的根源正是数组多维索引与内存地址映射之间的关系。

**前缀和数组的预分配**：计算前缀和时，需要创建长度为 `n+1` 的数组并初始化。提前用 `prefix = [0] * (n + 1)` 分配连续内存，比循环 `append` 快，因为避免了多次扩容拷贝操作。

---

## 常见误区

**误区一：Python `list` 直接存储元素本身**。实际上，CPython 的 `list` 存储的是指向 Python 对象的**指针数组**（每个指针 8 字节，在 64 位系统上）。因此 `list[i]` 的访问需要两次内存跳转：先通过 `base + i×8` 找到指针，再解引用指针找到对象。这使得 Python `list` 的缓存命中率远低于 NumPy `ndarray`（后者直接存储原始数值），这也是 NumPy 向量运算比纯 Python 循环快 10～100 倍的内存层面原因。

**误区二：数组越界只在运行时才能发现**。在 C/C++ 中，越界访问不会引发强制错误，而是**直接读写相邻内存区域**，可能静默破坏其他变量的值，这是缓冲区溢出漏洞（Buffer Overflow）的根本成因。Python 和 Java 通过在运行时检查索引边界牺牲了少量性能来避免此类问题。AI 框架在 CUDA 内核中若发生数组越界，可能导致 GPU 显存静默损坏，调试极为困难。

**误区三：`del arr[i]` 的时间复杂度是 O(1)**。由于数组要维持连续内存，删除第 `i` 个元素后，必须将 `i+1` 到 `n-1` 的所有元素向前移动一位，实际复杂度为 O(n)。只有删除最后一个元素（`del arr[-1]`）才是 O(1)。

---

## 知识关联

学习数组内部原理需要先掌握**数组/列表**的基本使用（如增删改查的 API），才能在此基础上理解为何不同操作的时间复杂度存在差异。内存地址计算公式 `base + i × size` 是理解所有后续内容的关键基础。

数组内部原理直接支撑**前缀和**技术的学习：前缀和数组 `prefix[i] = prefix[i-1] + arr[i-1]` 之所以能在 O(1) 内完成区间求和查询，正是依赖数组的随机访问特性（O(1) 寻址）。若底层换成链表，构建前缀和的时间不变，但查询任意 `prefix[i]` 需要 O(n) 遍历，前缀和技术将失去意义。此外，理解行主序/列主序与 Cache Locality 为后续学习**矩阵运算优化**和**稀疏矩阵**存储格式（CSR/CSC）打下直接基础。