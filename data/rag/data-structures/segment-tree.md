---
id: "segment-tree"
concept: "线段树"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 8
is_milestone: false
tags: ["高级数据结构"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 71.3
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 线段树

## 核心概念

线段树（Segment Tree）是一种二叉树数据结构，用于高效处理区间查询和区间更新。它将数组划分为若干段，每个节点存储一个区间的聚合信息（如和、最大值、最小值）。

## 结构特征

- 叶节点对应原数组的每个元素
- 内部节点存储子节点的聚合值
- 树高 O(log n)
- 空间 O(4n)（数组实现，4倍原数组大小）

## 基本操作

### 构建 O(n)
```python
# Python: 线段树（区间和）
class SegTree:
    def __init__(self, nums):
        self.n = len(nums)
        self.tree = [0] * (4 * self.n)
        self._build(nums, 1, 0, self.n - 1)
    
    def _build(self, nums, node, start, end):
        if start == end:
            self.tree[node] = nums[start]
            return
        mid = (start + end) // 2
        self._build(nums, 2 * node, start, mid)
        self._build(nums, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
```

### 单点更新 O(log n)
```python
    def update(self, idx, val, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if idx <= mid:
            self.update(idx, val, 2*node, start, mid)
        else:
            self.update(idx, val, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]
```

### 区间查询 O(log n)
```python
    def query(self, l, r, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l:
            return 0  # 不相交
        if l <= start and end <= r:
            return self.tree[node]  # 完全包含
        mid = (start + end) // 2
        return self.query(l, r, 2*node, start, mid) + \
               self.query(l, r, 2*node+1, mid+1, end)
```

⚠️ 注意：此为Python实现。C++/Java实现类似但需注意数组大小分配和递归栈深度。

## 懒惰传播（Lazy Propagation）

区间更新优化——不立即更新所有叶节点，而是标记延迟：
- 区间更新 O(log n)（不使用懒惰传播则为O(n)）
- 查询时下推延迟标记

## 复杂度对比

| 操作 | 朴素数组 | 前缀和 | 线段树 |
|------|---------|--------|--------|
| 单点更新 | O(1) | O(n) | O(log n) |
| 区间查询 | O(n) | O(1) | O(log n) |
| 区间更新 | O(n) | O(n) | O(log n) |

## 典型应用

- **区间和/最值查询**: 动态数组上的高效查询
- **区间染色**: 计算不同颜色的区间数
- **逆序对计数**: 离散化后用线段树统计

## 与二叉树的关系

线段树是二叉树的一种特殊应用。理解二叉树的递归结构和遍历是学习线段树的基础。
