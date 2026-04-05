---
id: "loops"
concept: "循环(for/while)"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["控制流"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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



# 循环（for/while）

## 概述

循环是编程语言中用于**重复执行一段代码块**的控制结构，分为计数驱动的 `for` 循环和条件驱动的 `while` 循环两大类。Python 的 `for` 循环本质上是一个迭代器协议的消费者——它依次调用可迭代对象的 `__next__()` 方法，直到捕获 `StopIteration` 异常为止，这与 C 语言中 `for(int i=0; i<n; i++)` 的纯计数语义有本质区别。

`while` 循环的历史可追溯到 1957 年 FORTRAN 语言的 `DO` 语句，但现代 `while` 的布尔条件语义由 Algol 60 在 1960 年正式确立。`for` 循环遍历集合的风格则随着 1970 年代 CLU 语言引入迭代器概念而逐渐成型。理解这两种循环的起源，有助于解释为何 Python 的 `for` 专门为遍历设计，而 `while` 专门为"不确定次数"的重复设计。

在 AI 工程中，循环是数据预处理、模型训练、批量推理的基础骨架。一个典型的神经网络训练循环（epoch 循环嵌套 batch 循环）决定了整个梯度下降过程的执行结构，循环写法的效率差异可以使训练时间相差数倍。

---

## 核心原理

### for 循环：迭代器协议驱动

Python 的 `for item in iterable` 在底层等价于：

```python
_iter = iter(iterable)      # 调用 iterable.__iter__()
while True:
    try:
        item = next(_iter)  # 调用 _iter.__next__()
        # 执行循环体
    except StopIteration:
        break
```

这意味着任何实现了 `__iter__` 和 `__next__` 的对象（包括列表、NumPy 数组、PyTorch `DataLoader`）都可以直接用 `for` 遍历。`range(n)` 是一个惰性对象，不会提前分配 `n` 个整数的内存，`range(10**9)` 的内存占用仅为 48 字节（在 CPython 3.10 中），这对大规模数据索引遍历至关重要。

### while 循环：条件求值与死循环风险

`while condition:` 在每次进入循环体**之前**重新求值 `condition`。其执行流程为：求值 → 若为 `False` 则退出 → 执行循环体 → 返回求值步骤。正是因为条件在循环体执行前判断，`while True:` 配合内部 `break` 是构建"读取-处理-直到终止信号"模式的惯用写法，例如实时推理服务中持续读取请求队列：

```python
while True:
    batch = queue.get(timeout=1.0)
    if batch is None:       # 毒丸信号（Poison Pill）
        break
    model.predict(batch)
```

死循环的最常见原因是循环变量在循环体内**未被修改**，或修改逻辑存在边界错误（off-by-one），调试时应优先检查循环变量的每次迭代变化。

### break、continue 与 else 子句

`break` 使 `for`/`while` **立即退出**整个循环，跳过 `else` 块；`continue` 跳过本次迭代剩余代码，直接进入下一次条件判断或迭代。Python 独有的循环 `else` 子句仅在循环**未被 `break` 中断**时执行，常用于"搜索失败"的判断：

```python
for candidate in model_list:
    if candidate.accuracy > 0.95:
        best = candidate
        break
else:
    raise ValueError("没有满足精度要求的模型")
```

此模式避免了额外的 `found` 布尔标志变量，代码更简洁。

### 嵌套循环的时间代价

两层 `for` 循环遍历 `n×m` 个元素，执行次数为 `n × m` 次。在 AI 数据处理中，对 10,000 条样本做成对距离计算若使用嵌套循环，执行次数为 10,000² = 1 亿次；替换为 NumPy 的向量化操作后，底层 C 实现的常数系数使速度提升通常在 **100 倍以上**。因此，在 AI 工程中看到嵌套 `for` 循环处理矩阵运算时，应首先考虑向量化替代。

---

## 实际应用

**训练 epoch 循环**：标准 PyTorch 训练使用双重 `for` 循环——外层 `for epoch in range(num_epochs)` 控制完整数据集遍历次数，内层 `for batch in dataloader` 按批次取数据。`num_epochs` 典型值为 10～100，`dataloader` 的 `batch_size` 典型值为 32 或 64。

**数据清洗中的 while 循环**：当处理流式日志数据（如持续写入的推理日志文件）时，`while not file.closed` 配合 `readline()` 是逐行读取的标准模式，因为文件总行数在处理开始时未知，`while` 的不定次数特性正好匹配此场景。

**列表推导式作为 for 循环的替代**：`[tokenize(text) for text in corpus]` 是 `for` 循环的语法糖，在 CPython 中执行速度比等效的 `for` 循环快约 **10%～35%**，因为它在字节码层面减少了 `STORE_NAME` 和 `LOAD_NAME` 操作。但当循环体包含副作用（如写入数据库）时，不应使用列表推导式替代，可读性和语义清晰度优先。

---

## 常见误区

**误区一：认为 for 和 while 可以完全互相替代**。技术上 `for` 循环确实可以用 `while` 加手动迭代器管理来模拟，但 Python 的 `for` 直接对接迭代器协议，能正确处理生成器、惰性序列等 `while` 手动模拟容易出错的对象。反方向替代更危险：将 `while i < len(data)` 改写为 `for i in range(len(data))` 时，若循环体内修改了 `data` 的长度，`for` 版本会在循环开始时固定 `range` 的上界，而 `while` 版本会动态感知长度变化，两者行为不同。

**误区二：在 Python 中用 for 循环做数值计算是"正常操作"**。对 NumPy 数组逐元素用 `for` 循环处理，比调用 `np.vectorize` 或直接写向量化表达式慢 **10～100 倍**，因为每次循环都有 Python 解释器的对象装箱（boxing）开销。在 AI 工程中，凡是对数组或张量的逐元素操作，均应优先考虑 `numpy`/`torch` 的广播机制，`for` 循环应仅用于无法向量化的逻辑（如样本间有依赖关系的序列处理）。

**误区三：`break` 只能跳出最内层循环**。这是正确的，但很多初学者在嵌套循环中误以为一个 `break` 能跳出所有层。Python 没有像 Java 的带标签 `break`（`break label`）语法，跳出多层嵌套需要借助函数封装（将嵌套循环放入函数，用 `return` 替代 `break`）或设置外层标志变量，或使用异常机制——在 AI 工程代码中，函数封装是最推荐的方式。

---

## 知识关联

循环依赖**条件判断（if/else）** 作为前置知识：`for`/`while` 内部通常包含 `if` 来处理特殊情况（如跳过空样本、检测收敛条件），`while` 的终止条件本身就是一个布尔表达式，与 `if` 共享相同的真值求值规则。

掌握循环后，**函数**的学习将把循环体封装为可复用单元，避免代码重复；**递归**是循环的函数式替代，理解循环的迭代语义有助于将递归调用栈与等效的 `while` 循环相互转化。**时间复杂度（Big-O）** 的分析直接依赖循环层数：单层循环通常对应 O(n)，双层嵌套循环对应 O(n²)，这是分析算法效率的基础量化方式。在 AI 工程的高级阶段，**并发编程**会将单线程的顺序循环转变为多线程或异步并发执行，理解循环的执行顺序是理解并发竞争条件的前提。