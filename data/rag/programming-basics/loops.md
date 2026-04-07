# 循环（for/while）

## 概述

循环（Loop）是程序控制流中用于**重复执行指定代码块**的基础结构，其核心语义分为两类：以**计数/遍历**为驱动的 `for` 循环，以及以**布尔条件**为驱动的 `while` 循环。二者的分野并非语法糖层面的细节，而是反映了两种根本不同的重复执行哲学。

从历史沿革来看，循环的概念可追溯至 1957 年 IBM 发布的 FORTRAN I，其 `DO` 语句是现代 `for` 循环的直接祖先，语法为 `DO 10 I = 1, N`，规定变量 `I` 从 1 递增至 `N`，每次步长为 1（Backus et al., 1957）。条件循环的正式语义则由 Naur 等人主持设计的 **Algol 60** 在 1960 年确立，首次引入 `while <condition> do <statement>` 的严格布尔求值语义，奠定了此后六十余年所有主流语言的 `while` 循环规范（Naur, 1960）。基于迭代器对象的 `for` 遍历风格，则源于 1975 年麻省理工学院 Barbara Liskov 领导设计的 **CLU 语言**，CLU 首次将"迭代器"作为一等语言特性引入，Python 的 `for` 循环正是这一思想的直接继承者。

在 AI 工程实践中，循环是数据预处理流水线、模型训练 epoch/batch 双层嵌套、超参数网格搜索的基础骨架。以 PyTorch 训练循环为例，外层 `for epoch in range(num_epochs)` 控制全局数据扫描轮次，内层 `for batch in dataloader` 消费 `DataLoader` 产生的每个小批量数据——这两层循环的写法效率差异，可以使相同硬件上的训练时间相差 3 到 10 倍（取决于 I/O 是否成为瓶颈）。

---

## 核心原理

### for 循环：迭代器协议的消费者

Python 的 `for item in iterable:` 并不像 C 语言那样维护一个整数计数器，而是在底层完整执行**迭代器协议（Iterator Protocol）**，其等价展开如下：

```python
_iter = iter(iterable)       # 调用 iterable.__iter__()，获取迭代器对象
while True:
    try:
        item = next(_iter)   # 调用 _iter.__next__()，获取下一个元素
        # 执行用户定义的循环体
    except StopIteration:    # __next__() 抛出该异常时，循环终止
        break
```

这意味着，任何实现了 `__iter__` 和 `__next__` 双方法的对象均可被 `for` 循环直接消费，包括 Python 内置列表、字典、`range` 对象、NumPy 数组、PyTorch `DataLoader`，乃至自定义的数据流类。`range(n)` 是一个**惰性求值**对象——它不会预先分配 $n$ 个整数的内存，在 CPython 3.10 中，无论 $n$ 取何值，`sys.getsizeof(range(10**9))` 均返回 **48 字节**，仅存储 start、stop、step 三个整数字段。这一特性对需要遍历亿级索引的大规模数据集处理至关重要。

**迭代顺序的确定性**是另一个常被忽视的细节：Python 3.7+ 起，`dict` 的迭代顺序**严格保证为插入顺序**（CPython 3.6 已实现，3.7 起写入语言规范），因此 `for key in my_dict` 的遍历结果是可预期的，可安全用于有序特征工程流水线。

### while 循环：条件前置求值与不定次重复

`while condition:` 的语义是：在**每次进入循环体之前**重新对 `condition` 求值，若结果为 `False`（或任何假值），立即终止循环并跳转至循环后续代码。执行流程严格为：

$$\text{求值 condition} \to \begin{cases} \text{False：退出循环} \\ \text{True：执行循环体} \to \text{返回求值 condition} \end{cases}$$

这种"**先判断、后执行**"的语义（称为 entry-controlled loop）与 `do...while`（exit-controlled loop，Python 中无原生语法）的根本区别在于：`while` 循环在条件初始为假时，循环体执行次数为零；`do...while` 至少执行一次。

`while True: ... break` 是构建**"读取-处理-终止信号"**模式的惯用写法，常见于实时推理服务、消息队列消费者：

```python
while True:
    batch = request_queue.get(timeout=1.0)
    if batch is None:        # 毒丸信号（Poison Pill Pattern）
        break
    predictions = model.predict(batch)
    response_queue.put(predictions)
```

此处 `while True` 搭配内部 `break` 的写法，比 `while not shutdown_flag:` 更安全——因为 `shutdown_flag` 在多线程场景下存在竞态条件，而毒丸信号通过队列本身保证了顺序一致性。

### break、continue 与 else 子句

Python 循环独有的 `else` 子句是一个高度特异性的语义：**当循环因条件耗尽（`for` 遍历完毕或 `while` 条件变为 False）而正常终止时，执行 `else` 块；若因 `break` 退出，则跳过 `else` 块**。这一语义在搜索场景中极为实用：

```python
for prime_candidate in range(2, n):
    if n % prime_candidate == 0:
        print(f"{n} 不是质数，因子为 {prime_candidate}")
        break
else:
    print(f"{n} 是质数")   # 仅在未触发 break 时执行
```

`continue` 跳过当前迭代的剩余语句，直接进入下一次条件判断或 `__next__()` 调用。在数据清洗循环中，`continue` 常用于跳过空值行，避免深层嵌套 `if-else`，使代码可读性提高。

---

## 关键公式与复杂度分析

### 循环执行次数与复杂度

对于嵌套循环，总迭代次数决定算法的时间复杂度上界。设外层循环执行 $m$ 次，内层循环执行 $n$ 次，则总迭代次数为：

$$T = m \times n$$

对于 AI 训练中的三层嵌套（epoch × batch × 层内前向传播），设 epoch 数为 $E$，数据集大小为 $N$，批量大小为 $B$，则每轮训练的 batch 数为 $\lceil N/B \rceil$，总迭代次数为：

$$T_{\text{train}} = E \times \left\lceil \frac{N}{B} \right\rceil$$

**例如**：ImageNet 数据集（$N = 1,281,167$），批量大小 $B = 256$，训练 90 个 epoch（ResNet-50 标准配置），则：

$$T_{\text{train}} = 90 \times \left\lceil \frac{1{,}281{,}167}{256} \right\rceil = 90 \times 5005 = 450{,}450 \text{ 次 batch 迭代}$$

每次 batch 迭代约耗时 0.3 秒（单块 V100），总训练时间约 37.5 小时，与 He et al. (2016) 论文中报告的 ResNet-50 训练时间高度吻合。

### 循环不变量（Loop Invariant）

循环不变量是一个在循环每次迭代开始时均为真的断言，由 C.A.R. Hoare 在 1969 年提出，是形式化验证循环正确性的核心工具（Hoare, 1969）。对于一个求数组前 $k$ 项之和的 `for` 循环：

```python
total = 0
for i in range(k):
    total += arr[i]
```

其循环不变量为：**在第 $i$ 次迭代开始时，`total` 等于 `arr[0]` 到 `arr[i-1]` 的和**，即 $\text{total} = \sum_{j=0}^{i-1} \text{arr}[j]$。验证不变量在初始化、保持、终止三个阶段均成立，即可证明循环的正确性，这是调试复杂数据聚合循环的系统化方法。

---

## 实际应用

### 应用一：神经网络训练的双层循环结构

PyTorch 标准训练循环的骨架直接体现了 `for` 循环的嵌套语义：

```python
for epoch in range(num_epochs):                    # 外层：epoch 循环
    model.train()
    running_loss = 0.0
    for batch_idx, (inputs, labels) in enumerate(train_loader):   # 内层：batch 循环
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"Epoch {epoch+1}, Loss: {running_loss/len(train_loader):.4f}")
```

此处 `enumerate(train_loader)` 同时利用了 Python 的迭代器协议（`DataLoader` 实现了 `__iter__`）和 `enumerate` 包装器（返回 `(index, value)` 元组的迭代器），是 `for` 循环迭代器协议在工程中的典型应用。

### 应用二：while 循环驱动的早停机制

早停（Early Stopping）是防止过拟合的重要技术，其核心逻辑天然适合 `while` 循环而非 `for` 循环，因为训练轮次是**不确定的**：

```python
best_val_loss = float('inf')
patience_counter = 0
epoch = 0

while patience_counter < patience:               # 条件：未超出耐心值
    train_one_epoch(model, train_loader)
    val_loss = evaluate(model, val_loader)
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), 'best_model.pt')
    else:
        patience_counter += 1
    epoch += 1
```

这里选择 `while` 而非 `for` 并非偏好问题——`for epoch in range(max_epochs)` 无法在不引入额外 `break` 条件的情况下表达"直到验证损失不再改善"的语义，而 `while` 的条件直接编码了终止逻辑。

### 应用三：列表推导式与生成器表达式的循环等价形式

Python 列表推导式 `[f(x) for x in iterable if condition]` 在语义上与以下 `for` 循环完全等价：

```python
result = []
for x in iterable:
    if condition:
        result.append(f(x))
```

但推导式在 CPython 解释器中经过专门优化，避免了每次调用 `result.append` 的方法查找开销，在处理 10 万级元素时，推导式通常比等价 `for` 循环快 **15%–30%**。生成器表达式 `(f(x) for x in iterable)` 则进一步延迟求值，适用于无需全量结果在内存中存在的流式数据处理场景。

---

## 常见误区

### 误区一：在迭代时修改正在被遍历的列表

```python
# 危险写法：可能跳过元素
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)   # 修改了正在被遍历的列表！
# 结果：items = [1, 3, 5] 看似正确，但对 [1, 2, 2, 3] 则会遗漏第二个 2

# 正确写法：遍历副本，修改原列表
for item in items[:]:        # items[:] 创建浅拷贝
    if item % 2 == 0:
        items.remove(item)
```

根本原因是 `for` 循环内部维护的迭代器状态（当前索引位置）与列表长度的动态变化之间产生了不同步。

### 误区二：混淆 for 与 while 的适用场景

**次数已知/遍历集合 → `for`；终止条件依赖运行时状态 → `while`**。一个常见的反模式是用 `while` 模拟已知次数的迭代：

```python
# 反模式：手动维护计数器
i = 0
while i < len(data):
    process(data[i])
    i += 1

# 正确写法：直接使用 for 遍历
for item in data:
    process(item)