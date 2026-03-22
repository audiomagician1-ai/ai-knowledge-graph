---
id: "recursion"
concept: "递归"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["算法思维"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Introduction to Algorithms"
    authors: ["Thomas H. Cormen", "Charles E. Leiserson", "Ronald L. Rivest", "Clifford Stein"]
    year: 2022
    isbn: "978-0262046305"
  - type: "textbook"
    title: "Structure and Interpretation of Computer Programs"
    authors: ["Harold Abelson", "Gerald Jay Sussman"]
    year: 1996
    isbn: "978-0262510875"
  - type: "textbook"
    title: "The Art of Computer Programming, Vol. 1"
    author: "Donald E. Knuth"
    year: 1997
    isbn: "978-0201896831"
scorer_version: "scorer-v2.0"
---
# 递归

## 概述

递归（Recursion）是一种函数直接或间接调用自身的编程技术。Donald Knuth 在《The Art of Computer Programming》（1997）中将递归定义为"用问题的较小实例来定义问题本身的方法"。它不仅是一种编程技巧，更是一种思维方式——将复杂问题分解为结构相同但规模更小的子问题。

递归的数学基础是**数学归纳法**（Mathematical Induction）：如果命题对 n=0 成立（基础情况），且"对 n=k 成立"能推出"对 n=k+1 成立"（归纳步骤），则命题对所有自然数成立。递归程序的结构与此完全对应。

## 递归的两个必要条件

每个正确的递归函数必须满足：

### 1. 基础情况（Base Case）

递归终止的条件——没有它，递归将无限进行直到栈溢出：

```python
def factorial(n):
    if n <= 1:        # 基础情况：0! = 1! = 1
        return 1
    return n * factorial(n - 1)  # 递归步骤
```

### 2. 递归步骤（Recursive Step）

将问题规模缩小，使其趋向基础情况：

```python
def fibonacci(n):
    if n <= 1:           # 基础情况
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # 每次 n 至少减 1
```

**关键验证**：递归步骤必须使参数向基础情况收敛。如果 `factorial(-1)` 被调用，n 永远不会到达 `n <= 1`→ 无限递归→栈溢出。防御性编程中应检查输入合法性。

## 递归的执行机制：调用栈

理解递归必须理解调用栈（Call Stack）：

```
factorial(4) 的执行过程：

调用栈增长（入栈）：           返回值计算（出栈）：
┌─────────────────┐           
│ factorial(1) → 1 │  ← 基础情况命中
├─────────────────┤           
│ factorial(2) = 2×factorial(1) │  → 2×1 = 2
├─────────────────┤           
│ factorial(3) = 3×factorial(2) │  → 3×2 = 6
├─────────────────┤           
│ factorial(4) = 4×factorial(3) │  → 4×6 = 24
└─────────────────┘           

每次调用分配一个栈帧（Stack Frame）：
- 局部变量 n 的值
- 返回地址
- 每帧约 64-256 字节（取决于语言/架构）
```

**栈溢出风险**：Python 默认递归深度限制 1000 层（`sys.getrecursionlimit()`）。C/C++ 默认线程栈大小 1-8MB，约支持 10,000-50,000 层递归。超过限制 → `StackOverflowError` / `RecursionError`。

## 经典递归模式

### 线性递归（Linear Recursion）

每次调用产生恰好一次递归调用：

```python
# 数组求和 — O(n) 时间, O(n) 栈空间
def sum_array(arr, i=0):
    if i == len(arr):
        return 0
    return arr[i] + sum_array(arr, i + 1)
```

### 二叉递归（Binary Recursion）

每次调用产生两次递归调用——形成二叉树结构：

```python
# Fibonacci — 朴素实现 O(2^n) 时间！
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# fib(5) 的调用树：
#           fib(5)
#          /      \
#      fib(4)    fib(3)
#      /    \    /    \
#   fib(3) fib(2) fib(2) fib(1)
#   ...    ...    ...
# 总调用次数：15 次（大量重复计算）
```

### 多路递归（Multiple Recursion）

每次调用产生 k 次递归——常见于树/图遍历：

```python
# 文件系统遍历
def list_files(directory):
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            list_files(path)    # 每个子目录一次递归
        else:
            print(path)
```

### 相互递归（Mutual Recursion）

两个函数互相调用：

```python
def is_even(n):
    if n == 0: return True
    return is_odd(n - 1)

def is_odd(n):
    if n == 0: return False
    return is_even(n - 1)
```

## 递归 vs 迭代

CLRS（Cormen et al., 2022）指出：**任何递归都可以用迭代+显式栈实现**。选择取决于问题特性：

| 维度 | 递归 | 迭代 |
|------|------|------|
| 代码清晰度 | 天然匹配树/分治问题 | 更适合线性遍历 |
| 空间复杂度 | O(n) 栈空间（隐式） | O(1)（显式循环） |
| 性能开销 | 函数调用开销 ~5-20ns/次 | 无调用开销 |
| 栈溢出风险 | 深度递归有风险 | 无此问题 |
| 调试难度 | 栈追踪长但结构清晰 | 需手动跟踪状态 |

```python
# 阶乘的迭代版本 — O(1) 空间
def factorial_iter(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

**经验法则**：如果递归深度可能超过 ~1000，转换为迭代。如果问题本身是树/图结构，递归更自然。

## 递归优化技术

### 1. 尾递归优化（Tail Call Optimization, TCO）

如果递归调用是函数的**最后一个操作**，编译器可以复用当前栈帧：

```python
# 非尾递归：return n * factorial(n-1)  ← 乘法在递归之后
# 尾递归版本：
def factorial_tail(n, acc=1):
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)  # 递归是最后操作
```

支持 TCO 的语言：Scheme（标准要求）、Haskell、Scala、部分 C/C++ 编译器（`-O2`）。
**不支持 TCO**：Python（Guido 明确拒绝）、Java、JavaScript（ES6 标准规定但仅 Safari 实现）。

### 2. 记忆化（Memoization）

缓存已计算结果，消除重复子问题：

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# fib(50) — 朴素递归需要 2^50 ≈ 10^15 次调用
# 记忆化后仅需 50 次调用，O(n) 时间 + O(n) 空间
```

### 3. 转换为动态规划

自底向上消除递归开销：

```python
def fib_dp(n):
    if n <= 1: return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr
# O(n) 时间, O(1) 空间 — 最优解
```

## 递归的复杂度分析：Master 定理

CLRS 中的 Master 定理处理形如 `T(n) = aT(n/b) + f(n)` 的递归式：

| 递推式 | 算法实例 | 时间复杂度 |
|--------|---------|-----------|
| T(n) = T(n-1) + O(1) | 阶乘、线性搜索 | O(n) |
| T(n) = T(n-1) + O(n) | 选择排序 | O(n²) |
| T(n) = 2T(n/2) + O(n) | 归并排序 | O(n log n) |
| T(n) = 2T(n/2) + O(1) | 二叉树遍历 | O(n) |
| T(n) = T(n/2) + O(1) | 二分查找 | O(log n) |
| T(n) = 2T(n-1) + O(1) | 汉诺塔、朴素 Fibonacci | O(2ⁿ) |

## 递归的经典应用

1. **分治算法**：归并排序、快速排序、Karatsuba 乘法
2. **树遍历**：前序/中序/后序遍历、DOM 树操作
3. **回溯搜索**：八皇后问题、数独求解器、排列组合生成
4. **分形绘制**：Koch 雪花、Sierpinski 三角形、Mandelbrot 集
5. **语法解析**：递归下降解析器（编译器前端）
6. **文件系统**：目录递归遍历、递归删除

## 常见误区

1. **忘记基础情况**：最常见的递归 bug——导致无限递归和栈溢出。调试方法：在递归函数入口打印参数值，观察是否收敛
2. **不必要的递归**：能用简单循环解决的问题（如数组求和、字符串反转）用递归只会增加栈开销。递归的价值在于处理 **递归结构的数据**（树、图、嵌套数据）
3. **朴素递归处理重叠子问题**：如直接递归计算 `fib(40)` 需要约 3.3 亿次调用（实测 ~40 秒），加上 `@lru_cache` 只需 40 次调用（<1ms）。识别重叠子问题 → 加记忆化或转 DP

## 知识衔接

### 先修知识
- **函数** — 递归的基础是函数能够调用自身，需要先理解函数定义、参数传递和返回值
- **循环(for/while)** — 理解迭代思维才能对比递归思维的优劣

### 后续学习
- **迭代vs递归** — 系统化比较两种范式的适用场景
- **二叉树** — 递归是树操作的天然语言
- **归并排序** — 分治递归的经典应用
- **快速排序** — 另一种分治策略，递归划分
- **分治法** — 递归思维的系统化方法论

## 参考文献

1. Cormen, T.H. et al. (2022). *Introduction to Algorithms* (4th ed.). MIT Press. ISBN 978-0262046305
2. Abelson, H. & Sussman, G.J. (1996). *Structure and Interpretation of Computer Programs* (2nd ed.). MIT Press. ISBN 978-0262510875
3. Knuth, D.E. (1997). *The Art of Computer Programming, Vol. 1* (3rd ed.). Addison-Wesley. ISBN 978-0201896831
4. Sedgewick, R. & Wayne, K. (2011). *Algorithms* (4th ed.). Addison-Wesley. ISBN 978-0321573513
