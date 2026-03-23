---
id: "binary-search"
concept: "二分查找"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 3
is_milestone: false
tags: ["搜索"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 二分查找

## 概述

二分查找（Binary Search）是一种专门针对**有序序列**的高效搜索算法，其核心机制是每次将搜索范围缩减为原来的一半，直至找到目标值或确定其不存在。该算法的思想最早可追溯至1946年，John Mauchly在宾夕法尼亚大学的讲稿中首次提及折半搜索的概念；而第一个被证明在所有情况下均正确的二分查找实现，直到1962年才由Bottenbruch给出 [Knuth, 1998]。值得注意的是，Knuth在《计算机程序设计艺术》第三卷（Sorting and Searching）中专门指出，二分查找虽然思路简单，但第一个无Bug的完整实现比算法思想的提出晚了整整16年，这一事实深刻揭示了边界条件处理的棘手性。

二分查找的时间复杂度为 $O(\log n)$，相比顺序查找的 $O(n)$ 有着质的提升。当数组长度 $n = 10^9$ 时，顺序查找最坏需要10亿次比较，而二分查找最多只需 $\lceil \log_2(10^9) \rceil = 30$ 次比较。这一特性使其在数据库索引、操作系统内核的页表查找以及机器学习中的超参数搜索等场景中被广泛采用。

---

## 核心原理

### 算法逻辑与不变量

二分查找的正确性依赖于维护一个**循环不变量**：目标值若存在，必然位于 `[left, right]` 区间内。每次迭代取中间索引 $mid = left + \lfloor(right - left) / 2\rfloor$（注意：直接写 $(left + right) / 2$ 在 `left` 和 `right` 都接近 `INT_MAX` 时会产生整数溢出，这是工程实践中的经典陷阱），将目标值与 `arr[mid]` 比较后，三路分支缩小范围。

标准的闭区间写法如下：

```python
def binary_search(arr: list, target: int) -> int:
    """
    在有序数组 arr 中查找 target，返回其索引；不存在则返回 -1。
    循环不变量：若 target 存在，则必在 arr[left..right] 中。
    """
    left, right = 0, len(arr) - 1

    while left <= right:          # 区间非空时继续搜索
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1        # 目标在右半部分，排除 mid
        else:
            right = mid - 1       # 目标在左半部分，排除 mid

    return -1                     # 区间为空，目标不存在
```

### 查找左边界与右边界

当数组中存在**重复元素**时，标准二分查找只能返回某一个匹配索引，无法定位第一个或最后一个出现位置。工程场景中更常用的是"查找左边界"（lower bound）和"查找右边界"（upper bound），C++ 标准库 `<algorithm>` 中的 `std::lower_bound` 和 `std::upper_bound` 正是基于此语义实现的 [ISO C++ Standard, 2020]。

以查找**左边界**为例（第一个 $\geq$ target 的位置）：

```python
def lower_bound(arr: list, target: int) -> int:
    """
    返回第一个 >= target 的元素的索引。
    若所有元素均 < target，返回 len(arr)。
    """
    left, right = 0, len(arr)    # 注意 right 初始化为 len(arr)，半开区间 [left, right)

    while left < right:           # 区间非空条件变为 left < right
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid           # 不排除 mid，收缩右边界

    return left
```

左右边界的差值即为目标值在有序数组中出现的次数：`upper_bound(arr, target) - lower_bound(arr, target)`。

### 复杂度分析与递归深度

设数组长度为 $n$，每次迭代将搜索区间减半，最坏情况下迭代次数满足：

$$T(n) = T\!\left(\frac{n}{2}\right) + O(1), \quad T(1) = O(1)$$

由主定理（Master Theorem，$a=1, b=2, f(n)=O(1)$）得 $T(n) = O(\log_2 n)$。空间复杂度在迭代实现下为 $O(1)$，递归实现下因调用栈深度为 $\lceil \log_2 n \rceil$ 层，空间复杂度为 $O(\log n)$。因此实际工程中几乎总是采用迭代写法。

---

## 实际应用

**1. 猜数字游戏与"答题器"系统**：二分查找的标准教学场景是1到100的猜数字，最优策略恒为猜50→25/75→……，最坏情况7次猜中（$\lceil \log_2 100 \rceil = 7$）。Leetcode第374题"猜数字大小"正是该思想的直接实现，其API `guess(num)` 返回 -1/0/1 完全对应二分的三路比较。

**2. Git 的 `git bisect` 命令**：Git 版本控制系统的 `git bisect` 功能使用二分查找在提交历史中定位引入Bug的具体 commit。假设项目有1024个提交，`git bisect` 最多只需10次手动测试即可精确定位，而逐一回溯则需要最多1024次。这是二分查找在DevOps工程实践中最直观的应用案例。

**3. 机器学习超参数调优**：在搜索学习率等连续超参数时，若损失函数在参数空间上具有单调性（例如正则化强度与验证误差的关系），可以用二分查找代替网格搜索。Scikit-learn 的部分模型（如 `LogisticRegression` 的 `liblinear` 求解器）内部对正则化参数的默认搜索范围 $[10^{-4}, 10^{4}]$ 采用对数等比序列，本质上是对数空间上的均匀采样，与二分思想一脉相承。

---

## 常见误区

**误区一：忽视"有序"前提，对无序数组直接调用二分查找**

二分查找的正确性完全依赖于序列的单调性。若数组无序，`arr[mid] < target` 并不能推断目标在右半段，算法将给出随机错误结论而非报错，排查极为困难。正确做法是先 $O(n \log n)$ 排序再二分，或改用哈希表 $O(1)$ 查找。

**误区二：将 `mid` 更新写成 `right = mid - 1` 与 `left = mid + 1` 时混淆区间定义**

闭区间 `[left, right]` 与半开区间 `[left, right)` 对应不同的循环条件和边界更新规则。闭区间时循环条件为 `left <= right`，右边界更新为 `right = mid - 1`；半开区间时条件为 `left < right`，右边界更新为 `right = mid`（不减1）。混用两套规则会导致死循环或漏查。Labuladong 在《我写了首诗，让你闭着眼睛也能写对二分查找》一文中将此归纳为"区间定义决定代码细节"，是目前中文社区最清晰的二分查找框架说明之一。

**误区三：认为二分查找只能用于静态查找，不适合动态数据**

二分查找本身确实要求有序数组，插入/删除需要 $O(n)$ 移位。但二分查找的思想可以直接扩展到**二叉搜索树（BST）**乃至**平衡BST（AVL树、红黑树）**，在动态数据集上将插入、删除、查找均保持在 $O(\log n)$。这正是本概念通向后续学习路径（二叉搜索树）的关键桥接点。

---

## 思考题

1. 给定一个旋转有序数组（如 `[4, 5, 6, 7, 0, 1, 2]`，原数组在某个未知位置被"旋转"），如何修改标准二分查找来仍然以 $O(\log n)$ 时间复杂度找到目标值？关键在于每次迭代如何判断左半段还是右半段"有序"？（对应 Leetcode 第33题）

2. 标准二分查找在长度为 $n=10$ 的数组中，最坏情况需要几次比较？最好情况呢？请画出"比较次数与目标位置"的对应关系，并解释为什么二分查找**不是**对所有输入等概率分布的最优搜索算法（提示：考虑插值查找 Interpolation Search）。

3. 在浮点数域上使用二分查找求 $\sqrt{2}$ 的近似值（精度 $\epsilon = 10^{-9}$）：初始区间设为 $[1, 2]$，需要迭代多少次才能达到精度要求？请写出终止条件，并讨论为什么此场景下不能用 `mid == target` 作为终止条件。
