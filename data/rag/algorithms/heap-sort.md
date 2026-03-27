---
id: "heap-sort"
concept: "堆排序"
domain: "ai-engineering"
subdomain: "algorithms"
subdomain_name: "算法"
difficulty: 5
is_milestone: false
tags: ["排序"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 堆排序

## 概述

堆排序（Heap Sort）是一种基于完全二叉堆数据结构的比较排序算法，时间复杂度稳定为 O(n log n)，空间复杂度为 O(1)（原地排序）。它由 J.W.J. Williams 于 1964 年首次提出，同年 Robert Floyd 改进了建堆过程，将朴素建堆的 O(n log n) 优化为线性时间 O(n)，这一优化是堆排序在工程中可用的关键所在。

堆排序的独特价值在于：它是少数同时满足 O(n log n) 最坏时间复杂度和 O(1) 额外空间的排序算法之一。快速排序在最坏情况下退化为 O(n²)，归并排序需要 O(n) 的辅助空间，而堆排序规避了这两个缺陷。这一特性使它在内存受限的嵌入式系统和对最坏情况有严格要求的实时系统中具有独特优势。

在 AI 工程中，堆排序或其衍生的优先队列结构广泛用于 Top-K 问题求解、Dijkstra 最短路径更新、beam search 候选维护等场景。理解堆排序的运作机制，能帮助工程师在处理大规模推荐系统中的候选集合排序时做出更精准的算法选择。

## 核心原理

### 最大堆性质与数组表示

堆排序依赖最大堆（Max-Heap）的性质：对于数组中下标为 i 的节点，其左子节点下标为 `2i+1`，右子节点为 `2i+2`，父节点为 `⌊(i-1)/2⌋`。最大堆要求每个节点的值均大于等于其子节点的值，即 `A[parent(i)] ≥ A[i]`。这种用数组模拟完全二叉树的方式无需指针开销，是堆排序 O(1) 空间的根本来源。

### 下沉操作（Heapify）

`Heapify(A, i, n)` 是堆排序的基础操作：对下标 i 的节点，比较它与左右子节点的大小，若子节点更大则交换，然后递归处理被交换的子节点，直到满足堆性质或到达叶节点。单次 Heapify 的时间复杂度为 O(log n)，因为树高最多为 ⌊log₂n⌋。若从根节点到叶节点路径上的每一层都需要交换，则恰好执行 ⌊log₂n⌋ 次比较和交换操作。

### Floyd 线性建堆

朴素建堆方法从叶节点逐一插入并上浮，总代价为 O(n log n)。Floyd 的改进是**从最后一个非叶节点**（下标 `⌊n/2⌋ - 1`）开始，向下标 0 方向逐个执行 Heapify。其复杂度证明利用了各层节点数与对应 Heapify 代价的乘积求和：

$$\sum_{h=0}^{\lfloor \log n \rfloor} \frac{n}{2^{h+1}} \cdot O(h) = O\left(n \sum_{h=0}^{\infty} \frac{h}{2^h}\right) = O(n \cdot 2) = O(n)$$

这个 O(n) 建堆是堆排序总复杂度仍保持 O(n log n) 的前提，而非 O(n² log n)。

### 排序阶段

建堆完成后，执行 n-1 次如下操作：将堆顶（当前最大值 `A[0]`）与堆末元素 `A[heap_size-1]` 交换，将 heap_size 减 1（相当于将最大值"锁定"到已排序区域），然后对新堆顶执行 Heapify 恢复堆性质。每次操作代价 O(log n)，n-1 次共 O(n log n)。最终数组从小到大有序排列。

```python
def heap_sort(arr):
    n = len(arr)
    # Floyd 线性建堆：从最后一个非叶节点开始
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    # 逐步提取最大值
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)

def heapify(arr, n, i):
    largest = i
    left, right = 2 * i + 1, 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)
```

## 实际应用

**Top-K 问题优化**：在推荐系统中从百万候选中提取最高评分的 K 个物品，若使用完整堆排序需 O(n log n)，而维护一个大小为 K 的最小堆只需 O(n log K)。遍历时若新元素大于堆顶则替换并 Heapify，最终堆中即为 Top-K 结果。当 K=100，n=1,000,000 时，log K ≈ 7 而 log n ≈ 20，性能提升约 3 倍。

**操作系统进程调度**：Linux 内核的完全公平调度器（CFS）使用红黑树而非堆，但许多实时操作系统（如 VxWorks）的任务调度器直接基于最大堆实现优先级队列，任务插入和提取最高优先级任务均为 O(log n)，与堆排序的 Heapify 共享相同的下沉逻辑。

**外部排序辅助结构**：在处理超过内存容量的大文件排序时，堆排序用于生成初始归并段（runs）。使用大小为 M 的最大堆，每次将磁盘读入的元素与堆顶比较，若新元素大于等于最近输出的最小值则加入当前 run，否则放入下一 run，这种"置换选择"策略使平均 run 长度达到 2M，显著减少归并趟数。

## 常见误区

**误区一：堆排序比快速排序快**。虽然堆排序的最坏情况保证更强，但在实践中快速排序通常比堆排序快 2-5 倍。原因在于堆排序的内存访问模式极不友好：Heapify 过程中访问 `A[i]`、`A[2i+1]`、`A[2i+2]` 跳跃幅度大，在 n=10⁶ 的数组中，访问下标 500000 的节点后立即跳到 1000001，几乎必然触发 CPU 缓存缺失（cache miss），而快速排序的分区操作是顺序扫描，缓存命中率远高于堆排序。

**误区二：堆排序是稳定排序**。堆排序是**不稳定**排序。在排序阶段将堆顶与堆末交换时，相同值的两个元素可能改变相对顺序。例如对序列 `[3a, 1, 3b]` 建堆后，3a 和 3b 的最终位置取决于 Heapify 的比较路径，无法保证 3a 仍排在 3b 之前。需要稳定性时应选择归并排序或 Timsort（Python 的 `sorted()` 使用的算法）。

**误区三：O(n) 建堆使整体复杂度降为 O(n)**。建堆仅完成一次 O(n) 的操作，但随后的排序阶段需执行 n-1 次 Heapify，每次 O(log n)，总计 O(n log n)，这部分无法优化。建堆的 O(n) 优化将总常数系数降低了约 30%，但渐进复杂度类别不变，仍为 O(n log n)。

## 知识关联

**前置知识**：堆排序要求牢固掌握完全二叉堆的结构——特别是父子节点的数组下标关系（`left=2i+1`，`right=2i+2`）和堆的两种形态（最大堆用于升序排列，最小堆用于降序排列）。若对优先队列的 `push` 和 `pop` 操作的 O(log n) 来源不清晰，则难以理解为何排序阶段恰好是 O(n log n) 而非其他复杂度。

**延伸方向**：掌握堆排序后，可进一步研究其变体——**Smoothsort**（由 Edsger Dijkstra 于 1981 年提出）在接近有序的输入上可达 O(n)，利用 Leonardo 数定义的堆序列替代标准完全二叉堆。此外，堆排序与优先队列的结合是理解 Dijkstra 算法（O((V+E) log V)）、Prim 算法和 A* 搜索中开放列表维护机制的直接基础。