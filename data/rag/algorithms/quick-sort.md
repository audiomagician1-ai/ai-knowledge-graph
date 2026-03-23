---
id: "quick-sort"
concept: "快速排序"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 5
is_milestone: false
tags: ["排序", "分治"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 快速排序

## 概述

快速排序（Quicksort）由英国计算机科学家 Tony Hoare 于1959年在苏联实习期间构思，并于1961年正式发表于《Communications of the ACM》。Hoare 当时面临的问题是如何在内存极为有限的计算机上高效地对俄语词汇表进行排序，这一实际需求直接催生了这一算法。快速排序的核心思想是**分区（Partition）**：选取一个基准元素（pivot），将数组重新排列使得所有小于基准的元素排在基准左侧，所有大于基准的元素排在右侧，然后递归地对两个子数组执行相同操作。

与归并排序不同，快速排序是一种**原地排序（in-place sort）**算法，不需要额外的 $O(n)$ 辅助内存来存储临时数组，其额外空间开销仅来自递归调用栈，平均为 $O(\log n)$。这一特性使得快速排序在实际工程中比归并排序更常用——C标准库的 `qsort()`、C++ STL的 `std::sort()`（混合算法，核心为快速排序）、Python的 Timsort（对短序列使用插入排序辅助）都以快速排序的思想为基础。Knuth 在《计算机程序设计艺术》第三卷第5.2.2节中将快速排序称为"已知最快的通用排序方法"[Knuth, 1998]。

## 核心原理

### 分区操作（Partition）

分区是快速排序的灵魂。经典的 Lomuto 分区方案选取数组末尾元素作为 pivot，维护一个指针 `i` 指向"小于pivot区域"的末尾，遍历数组时若当前元素小于 pivot 则将其与 `i+1` 位置元素交换。Hoare 的原始分区方案使用双指针从两端向中间扫描，平均交换次数约为 Lomuto 方案的1/3，性能更优但实现稍复杂。

```python
def lomuto_partition(arr, low, high):
    pivot = arr[high]      # 选取末尾元素为基准
    i = low - 1            # i 指向小于 pivot 区域的末尾
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1           # 返回 pivot 的最终位置

def quicksort(arr, low, high):
    if low < high:
        pi = lomuto_partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)
```

分区操作的时间复杂度严格为 $O(n)$，每次分区后 pivot 元素已经到达其最终位置，无需再移动。

### 时间与空间复杂度分析

快速排序的时间复杂度取决于每次分区的平衡程度。设 $T(n)$ 为排序 $n$ 个元素的时间：

- **最优情况**：每次 pivot 恰好将数组平分，递推关系为 $T(n) = 2T(n/2) + O(n)$，由主定理得 $T(n) = O(n \log n)$。
- **平均情况**：随机输入下，期望时间复杂度为 $O(n \log n)$，且常数因子约为 $1.39 n \log_2 n$，比归并排序的 $n \log_2 n$ 仅大39%，但由于缓存友好性，实际速度通常更快。
- **最坏情况**：输入数组已排序或逆序，且每次选取首/尾元素为 pivot，递推关系退化为 $T(n) = T(n-1) + O(n)$，即 $T(n) = O(n^2)$。

空间复杂度方面，递归深度在平均情况下为 $O(\log n)$，最坏情况下为 $O(n)$（退化为单侧递归）。使用**尾递归优化**或**迭代+显式栈**可将最坏空间复杂度控制在 $O(\log n)$。

### Pivot 选取策略与三路分区

Pivot 的选取策略对性能影响极大。Sedgewick 和 Wayne 在《算法（第4版）》中详细比较了三种策略[Sedgewick, 2011]：

1. **固定位置**（首/尾元素）：面对已排序输入时退化为 $O(n^2)$，实际工程中已基本弃用。
2. **随机选取**：以等概率从 $[low, high]$ 中随机选取 pivot，将最坏情况概率降至极低，期望复杂度严格为 $O(n \log n)$。
3. **三数取中（Median-of-Three）**：取首、中、尾三个元素的中位数作为 pivot，在实践中比随机选取更快约5%，被 C++ `std::sort` 采用。

针对含大量重复元素的数组，Dijkstra 提出的**三路分区（Dutch National Flag Problem）**将数组分为"小于pivot"、"等于pivot"、"大于pivot"三段，对所有等于 pivot 的元素**一次性处理完毕**，使得重复元素极多时复杂度从 $O(n^2)$ 降为 $O(n)$。Java 7 的 `Arrays.sort()` 对基本类型采用的 **Dual-Pivot Quicksort**（双基准快速排序）正是三路分区思想的工程扩展，在随机数组上比经典快速排序快10%~15%。

## 实际应用

**Linux内核排序**：Linux内核的 `lib/sort.c` 使用了基于堆排序和快速排序混合的算法，在序列长度超过阈值时触发快速排序逻辑，以保证内核调度队列等数据结构的高效维护。

**数据库查询优化**：PostgreSQL 在执行 `ORDER BY` 操作时，对超出内存缓冲区的大型结果集采用外部归并排序，但在内存中对单个排序批次（Sort Run）使用快速排序。根据 PostgreSQL 官方文档，其内部实现使用了带随机化 pivot 的内省排序（Introsort），即快速排序 + 堆排序的混合体，防止最坏情况退化。

**机器学习特征选择**：在计算特征重要性（如随机森林的基尼不纯度排序）时，需要对数千个特征的重要性得分进行排序。scikit-learn 的 `SelectKBest` 内部调用 NumPy 的 `np.partition()`（基于快速选择算法 Quickselect，快速排序的变体），在 $O(n)$ 期望时间内找出第 $k$ 大元素，无需对全部特征完整排序。

## 常见误区

**误区1：快速排序在所有情况下都是最快的排序算法。**  
这一观点忽略了最坏情况。当输入数组已经有序或近乎有序，且使用固定位置 pivot 时，快速排序退化为 $O(n^2)$。实际上，标准库实现（如 C++ `std::sort`）均采用内省排序（Introsort）：当递归深度超过 $2 \lfloor \log_2 n \rfloor$ 时，自动切换为堆排序以保证 $O(n \log n)$ 的最坏时间复杂度。

**误区2：快速排序是稳定排序（Stable Sort）。**  
标准的快速排序**不是稳定排序**。在 Lomuto 分区中，相等元素的相对顺序可能被交换操作打乱。例如对 `[(3,a), (1,b), (3,c)]` 按第一个字段排序，快速排序可能输出 `[(1,b), (3,c), (3,a)]` 而非 `[(1,b), (3,a), (3,c)]`。这是为何 Java 的 `Collections.sort()`（针对对象）使用稳定的 Timsort，而 `Arrays.sort()`（针对基本类型）使用不稳定的 Dual-Pivot Quicksort——因为基本类型无法区分相等元素的"身份"，稳定性无意义。

**误区3：随机化 pivot 使快速排序的最坏情况变为 $O(n \log n)$。**  
随机化仅能**降低**最坏情况的发生概率，而非消除最坏情况。对于任意固定的随机种子，理论上仍然存在使算法退化到 $O(n^2)$ 的输入序列。正确表述是：随机化快速排序对**任意固定输入**，其期望时间复杂度（对随机 pivot 选择取期望）为 $O(n \log n)$，但绝对最坏情况仍是 $O(n^2)$，只是概率极低（约为 $n!$ 分之一的量级）。

## 思考题

1. 对一个包含100万个元素、其中99%的元素值相同的数组，经典双指针快速排序和 Dijkstra 三路分区快速排序的实际运行时间会相差多少数量级？请通过复杂度分析推导，并说明三路分区如何将该场景的时间复杂度从 $O(n^2)$ 降为 $O(n)$。

2. C++ `std::sort` 使用内省排序（快速排序 + 堆排序 + 插入排序的混合）。请分析：为何对于长度小于16的子数组，切换为插入排序（而非继续递归快速排序）能提升实际性能？这与快速排序的递归开销和 CPU 缓存命中率有何关系？

3. 快速选择算法（Quickselect）是快速排序的变体，用于在 $O(n)$ 期望时间内找到数组中第 $k$ 小的元素。请描述其与快速排序的区别：分区后，Quickselect 如何决定只递归处理一侧而非两侧子数组？在最坏情况下，Quickselect 的时间复杂度是多少，又如何通过"中位数的中位数"（Median of Medians）算法保证严格 $O(n)$ 的最坏情况？
