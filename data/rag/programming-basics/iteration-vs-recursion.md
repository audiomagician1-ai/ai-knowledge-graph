# 迭代 vs 递归

## 概述

迭代（Iteration）与递归（Recursion）是解决重复性计算问题的两种根本不同的程序设计范式。迭代通过循环结构（`for`、`while`）在**同一栈帧**内反复执行代码块，每次循环更新状态变量直到满足终止条件；递归则通过函数自我调用，将大问题分解为同类型的子问题，每次调用都会在调用栈上压入一个新的栈帧，直到触达基础情形（base case）后逐层返回。

从历史脉络看，迭代对应冯·诺依曼（John von Neumann）架构中最自然的指令执行模型，是命令式编程的基石；递归则源自1930年代阿隆佐·邱奇（Alonzo Church）的 λ 演算（Lambda Calculus），是函数式编程的理论根基。1958年 John McCarthy 设计的 Lisp 语言将递归带入实际编程实践，成为 AI 领域早期符号推理算法的主流表达方式（McCarthy, 1960）。1977年 Aho、Hopcroft 和 Ullman 在《计算机算法的设计与分析》中系统阐述了递归与迭代的复杂度等价性，奠定了现代算法分析的框架（Aho et al., 1974）。

理解二者的差异在 AI 工程中尤为关键：神经网络训练中的反向传播（Backpropagation）本质上是跨层的链式递推，而批次梯度下降的 epoch 循环是典型迭代结构。决策树的构建天然适合递归分治，而向量化批量推理则依赖迭代展开。选错范式不仅影响代码可读性，更会导致 `RecursionError` 或不必要的内存开销，直接决定训练流水线能否在生产环境稳定运行。

---

## 核心原理

### 调用栈与空间复杂度的本质差异

迭代使用 $O(1)$ 的额外空间——循环变量固定占用固定大小的寄存器或栈空间，与问题规模 $n$ 无关。朴素递归的空间复杂度为 $O(d)$，其中 $d$ 是递归调用的最大深度，因为每次调用都要在栈上保存当前函数的局部变量、参数和返回地址，形成"活动记录（Activation Record）"的链式堆叠。

以斐波那契数列第 $n$ 项为具体对比：

$$F(n) = F(n-1) + F(n-2), \quad F(0) = 0,\ F(1) = 1$$

- **朴素递归**：直接按定义展开，时间复杂度 $O(2^n)$，栈深度 $O(n)$，因为存在大量重复子问题（$F(n-2)$ 被计算指数次）。
- **记忆化递归（Memoization）**：用哈希表缓存已计算结果，时间降至 $O(n)$，空间仍为 $O(n)$（递归栈 + 缓存表）。
- **迭代版本**：两个临时变量 `a, b` 交替赋值，时间 $O(n)$，空间 $O(1)$，是最优实现。

```python
# 迭代版斐波那契：O(1) 空间
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

Python 默认递归深度限制为 **1000**（通过 `sys.getrecursionlimit()` 可查，`sys.setrecursionlimit()` 可修改），超过即抛出 `RecursionError`。这意味着在处理深度超过1000的树结构或图的深度优先搜索时，直接递归实现会在运行时崩溃，必须改用显式栈迭代。

### 尾递归优化（TCO）与语言支持的分化

尾递归（Tail Recursion）是指递归调用是函数体中**最后一个操作**，其返回值直接作为当前函数的返回值，形如：

```python
def factorial_tail(n, acc=1):
    if n == 0:
        return acc
    return factorial_tail(n - 1, acc * n)  # 尾位置调用
```

此处 `acc`（累加器）将中间结果前向传递，消除了返回后还需计算的依赖。对支持尾调用消除（Tail Call Optimization, TCO）的编译器或解释器而言，可以**复用当前栈帧**而非新建，使尾递归的空间行为等同于迭代，复杂度从 $O(n)$ 降至 $O(1)$。

然而，**CPython 和标准 JVM 均刻意不实现 TCO**。Python 之父 Guido van Rossum 在2009年的博客"Tail Recursion Elimination"中明确说明：TCO 会破坏 Python 的栈帧追踪（traceback），使调试时的错误堆栈信息变得不可读，因此选择牺牲优化来保留可调试性。相比之下，Haskell 的 GHC 编译器、Scala（通过 `@tailrec` 注解）、以及 Scheme（R6RS 规范强制要求）原生支持 TCO。

这一语言差异对 AI 工程的 Python 生态具有直接影响：所有"看起来是尾递归"的 Python 代码在运行时仍会完整消耗栈空间，开发者**不能依赖 TCO 来优化深递归**，必须手动将其转换为带累加器的迭代循环。

### 递归的结构优势：分治与树形问题

递归在表达**分治（Divide and Conquer）**结构时具有压倒性的可读性优势。以归并排序为例，递归版本直接映射其数学定义：

$$\text{MergeSort}(A) = \text{Merge}\left(\text{MergeSort}(A[:\lfloor n/2 \rfloor]),\ \text{MergeSort}(A[\lfloor n/2 \rfloor:])\right)$$

相比之下，迭代版归并排序需要显式管理合并的"步长"（stride），代码量增加3倍且逻辑不直观。对于**二叉树的中序遍历**，递归版本仅需3行：

```python
def inorder(node):
    if not node: return []
    return inorder(node.left) + [node.val] + inorder(node.right)
```

而等价的迭代版本需要维护一个显式栈并模拟"回溯"状态，代码约15行。这说明递归的价值不仅在于性能，更在于**算法意图与代码结构的一致性**。

---

## 关键方法与转换公式

### 递归转迭代：显式栈替换调用栈

任何递归算法都可以通过**显式栈模拟调用栈**机械转换为迭代，通用步骤如下：

1. 将初始参数封装为"帧对象"压入栈（`stack = deque([(initial_params, state)])`）
2. 进入 `while stack` 循环，弹出栈顶帧
3. 执行原递归函数体的非递归部分逻辑
4. 将子问题的参数帧压回栈，替代递归调用
5. 用显式变量或结果列表替代返回值的传递

例如，深度优先搜索（DFS）的递归版本：

```python
def dfs_recursive(graph, node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
```

转换为显式栈迭代版本：

```python
def dfs_iterative(graph, start):
    visited, stack = set(), [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph[node])
    return visited
```

迭代版本不受 Python 栈深度限制，可处理任意规模的图结构。

### 迭代转递归：寻找自相似子结构

将迭代转换为递归的关键是识别**循环不变量（Loop Invariant）**对应的自相似子问题。若迭代的核心是 `state = f(state, input[i])`，则等价递归形式为：

```python
def recursive(input, i, state):
    if i == len(input): return state
    return recursive(input, i + 1, f(state, input[i]))
```

这实质上是将迭代的"状态更新序列"重写为"尾递归的参数传递链"。动态规划（DP）中的许多状态转移方程天然对应此结构，例如背包问题的递推关系：

$$dp[i][w] = \max\left(dp[i-1][w],\ dp[i-1][w - w_i] + v_i\right)$$

既可以用二维数组迭代填表（标准 DP），也可以用带记忆化的递归自顶向下求解，二者在时间复杂度上等价，均为 $O(nW)$，但迭代版空间可优化至 $O(W)$（滚动数组），而递归版最少需要 $O(nW)$（记忆表）加上 $O(n)$ 的栈空间。

---

## 实际应用

### AI 工程中的典型场景划分

**适合迭代的场景：**

- **神经网络训练循环**：Mini-batch SGD 的 epoch 迭代、每个 batch 内的前向传播计算，均以迭代展开，依赖 NumPy/PyTorch 的向量化，若改为递归将破坏自动微分图的构建逻辑。
- **序列处理**：RNN 的时间步展开（unrolling）在推理时是显式迭代循环，在训练时通过 BPTT（Backpropagation Through Time）等价为递归链式求导。
- **大规模图遍历**：知识图谱（Knowledge Graph）中节点数达百万级时，必须用显式栈迭代 DFS/BFS，避免 Python 栈溢出。

**适合递归的场景：**

- **决策树/随机森林构建**：ID3、CART 算法的节点分裂过程天然是递归分治——在当前节点选择最优特征，对左右子树递归调用同一逻辑，深度通常不超过50层，递归栈安全。
- **Transformer 的递归解码**：自回归生成（Autoregressive Generation）在逻辑上是递归的——每次生成一个 token 后将其追加到输入再重新调用，虽然实现中通常用迭代展开，但其数学结构是递归的。
- **JSON/AST 解析**：解析嵌套结构（如 Python 抽象语法树 AST、配置文件 JSON）时，递归下降解析器（Recursive Descent Parser）的结构与语法的嵌套层次完全吻合，代码逻辑清晰。

### 案例：sklearn 决策树的递归构建

以 scikit-learn 的 `DecisionTreeClassifier` 为例，其核心构建函数 `_build_tree` 是递归调用：对当前数据子集计算信息增益（Information Gain）选择最优分裂特征，然后对左子集和右子集分别递归调用自身。sklearn 内部通过 `max_depth` 参数控制递归深度（默认 `None` 即不限制），当数据集特征较多且允许完全生长时，实际递归深度约为 $O(\log n)$（均衡树）到 $O(n)$（极端不均衡树），后者在大数据集上有栈溢出风险，这也是为何 sklearn 建议配合 `max_depth` 使用的工程原因。

---

## 常见误区

**误区1："递归一定比迭代慢"**

这一判断忽略了函数调用开销的相对量级。对于深度为 $O(\log n)$ 的分治递归（如归并排序、二叉搜索树查找），函数调用开销相对于 $O(n \log n)$ 的计算量可忽略不计。朴素递归之所以慢，是因为存在**重复子问题**（如无记忆化的斐波那契），而非递归调用本身的开销。引入记忆化后，递归版本与迭代版本的时间复杂度完全相同。

**误区2："尾递归在 Python 中等于迭代"**

如前所述，CPython 不实现 TCO，因此即使写出形式完美的尾递归，每次调用仍会压栈。`factorial_tail(10000)` 仍会在 Python 中触发 `RecursionError`，必须改为显式循环。

**误区3："递归只是迭代的语法糖"**

从计算能力上二者等价，但从**表达能力**上，递归可以自然表达图灵不可判定问题的结构（如停机问题的证明依赖递归定义），