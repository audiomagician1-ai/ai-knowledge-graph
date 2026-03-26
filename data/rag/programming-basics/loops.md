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
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
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

循环是编程语言中用于**重复执行一段代码块**的控制结构，允许程序在满足特定条件时自动执行相同或相似的操作，而无需手动复制粘贴代码。Python 中最常用的两种循环是 `for` 循环和 `while` 循环，它们在语义上有本质区别：`for` 循环用于**已知迭代次数或可枚举序列**的场景，而 `while` 循环用于**条件驱动的重复执行**场景。

`for` 循环的语法起源可追溯至 FORTRAN（1957年）中的 `DO` 循环，后在 C 语言中演化为经典的三段式 `for(init; condition; increment)` 结构。Python 则进一步将其设计为基于**迭代协议（Iterator Protocol）**的遍历机制，任何实现了 `__iter__()` 和 `__next__()` 方法的对象都可作为 `for` 循环的遍历目标，这使得 Python 的 `for` 循环在 AI 工程中处理数据集、批次（batch）时极为灵活。

在 AI 工程中，循环几乎无处不在：模型训练的每个 epoch 是一次大循环，每个 mini-batch 的前向传播与反向传播是内层循环，特征工程中对百万行数据的预处理依赖循环遍历。正确理解和使用循环，直接影响训练脚本的效率与可读性。

---

## 核心原理

### for 循环的迭代机制

Python 的 `for` 循环执行流程如下：

```python
for item in iterable:
    # 循环体
```

每次迭代时，Python 内部调用 `next(iter(iterable))` 获取下一个元素，直到抛出 `StopIteration` 异常为止。`range(start, stop, step)` 是 AI 工程中最常用的 `for` 循环伴侣，`range(0, 100, 2)` 会生成 0、2、4……98 共 50 个偶数，且不会在内存中预先生成整个列表，而是**惰性求值（lazy evaluation）**，节省内存开销。

在遍历列表同时需要索引时，`enumerate()` 比手动维护计数器更安全：

```python
for epoch, loss in enumerate(loss_history):
    print(f"Epoch {epoch}: loss = {loss:.4f}")
```

### while 循环的条件控制

`while` 循环的核心结构为：

```
while <布尔表达式>:
    <循环体>
```

其执行逻辑是：每次进入循环体之前都重新计算布尔表达式，若为 `True` 则继续，为 `False` 则退出。AI 工程中，**早停（Early Stopping）**策略天然适合用 `while` 循环表达：

```python
patience = 0
while patience < 5 and epoch < max_epochs:
    train_one_epoch()
    if val_loss > best_loss:
        patience += 1
    else:
        best_loss = val_loss
        patience = 0
    epoch += 1
```

这段逻辑用 `for` 循环虽然可以实现，但 `while` 循环更准确地表达了"满足条件就继续"的语义。

### break、continue 与 else 子句

`break` 立即终止整个循环，`continue` 跳过当前迭代直接进入下一次。Python 循环还有一个独特的 `else` 子句，它在循环**正常结束（未被 break 打断）时执行**：

```python
for sample in dataset:
    if is_corrupted(sample):
        print("发现损坏样本，停止加载")
        break
else:
    print("数据集加载完毕，无损坏样本")
```

许多其他语言没有这一结构。在 AI 数据加载和验证流程中，这种模式可以清晰地区分"提前终止"与"正常完成"两种状态，避免使用额外的标志变量（flag variable）。

### 嵌套循环与时间代价

嵌套循环指循环体内包含另一个循环，其执行次数为各层循环次数的乘积。两层 `for` 循环各执行 n 次，总执行次数为 n²。在 AI 工程中，手写矩阵乘法的崓套三重循环时间复杂度为 O(n³)，而 NumPy 的向量化操作通过底层 C/Fortran 实现，可将相同计算提速 **100 倍以上**，这是为何 AI 工程师需要用向量化替代显式嵌套循环的根本原因。

---

## 实际应用

**场景一：训练数据批次迭代**

```python
for epoch in range(num_epochs):          # 外层：epoch 循环
    for batch_X, batch_y in dataloader:  # 内层：batch 循环
        optimizer.zero_grad()
        predictions = model(batch_X)
        loss = criterion(predictions, batch_y)
        loss.backward()
        optimizer.step()
```

`DataLoader` 本身实现了迭代协议，因此可以直接用 `for` 循环遍历，每次自动返回一个 mini-batch。

**场景二：超参数搜索**

```python
learning_rates = [1e-4, 1e-3, 1e-2]
best_acc = 0
for lr in learning_rates:
    model = train_model(lr=lr)
    acc = evaluate(model)
    if acc > best_acc:
        best_acc = acc
        best_lr = lr
```

**场景三：收敛等待**

```python
delta = float('inf')
while delta > 1e-6:
    old_params = model.get_params()
    model.update()
    delta = np.linalg.norm(model.get_params() - old_params)
```

此处用 `while` 循环等待参数变化量 delta 降至 10⁻⁶ 以下，比 `for` 循环固定迭代次数更贴近"收敛"的数学含义。

---

## 常见误区

**误区一：认为 for 和 while 可以完全互换**

`for` 循环可以用 `while` 改写，但反之不总成立。`while` 循环的退出条件可以依赖循环体内的**动态计算结果**（如上例中的 delta），而 `for` 循环的迭代次数在循环开始时必须可枚举。强行用 `for range(9999999)` 模拟"直到收敛"的逻辑，既不清晰又可能提前终止。

**误区二：在循环内部修改正在遍历的列表**

```python
data = [1, -2, 3, -4, 5]
for x in data:
    if x < 0:
        data.remove(x)   # ❌ 危险！会跳过元素
```

Python 的 `for` 循环使用内部索引推进，删除元素会导致索引错位，产生遗漏。正确做法是遍历副本 `for x in data[:]` 或使用列表推导式 `data = [x for x in data if x >= 0]`。

**误区三：忽视 while 循环的无限循环风险**

`while True:` 是合法的无限循环，必须依赖 `break` 退出。AI 训练脚本中若忘记更新循环条件变量（如 epoch 未自增），程序会陷入无限循环并耗尽计算资源。**每个 while 循环都必须明确标识出改变其终止条件的语句**，并在代码审查时验证该语句在所有代码路径下都会被执行。

---

## 知识关联

**前置概念：条件判断（if/else）**

`while` 循环的终止条件本质上是一个布尔表达式，与 `if` 语句中的条件判断语法完全相同。`break` 和 `continue` 通常与 `if` 嵌套使用，例如 `if loss > threshold: break`，因此理解 `if/else` 的真值运算是编写正确循环终止条件的前提。

**后续概念：函数与递归**

函数将循环体封装为可复用单元（如 `train_one_epoch()`），递归则是函数调用自身来替代显式循环的另一种重复执行模式。理解 `for/while` 循环的"状态推进"逻辑，有助于理解递归调用栈如何模拟同样的状态变化过程。

**后续概念：时间复杂度（Big-O）**

单层 `for` 循环执行 n 次对应 O(n)，双层嵌套对应 O(n²)。Big-O 分析的核心就是**数循环层数与循环范围**，掌握循环结构是分析算法复杂度的直接起点。

**后续概念：并发编程基础**

当单个 `for` 循环处理百万样本速度不足时，可将循环体并行化——Python 的 `multiprocessing.Pool.map()` 本质上是将 `for` 循环的每次迭代分发到不同进程执行。理解循环的串行执行模型，才能准确判断哪些循环可以安全并行化，哪些存在数据依赖而不能。