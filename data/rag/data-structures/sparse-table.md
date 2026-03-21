---
id: "sparse-table"
concept: "稀疏表"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 7
is_milestone: false
tags: ["高级数据结构"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 73.6
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 稀疏表（Sparse Table）

## 核心概念

稀疏表（Sparse Table）是一种用于静态区间查询的数据结构。它在O(n log n)时间和空间内预处理后，可以在O(1)时间内回答区间最值查询（RMQ, Range Minimum/Maximum Query）。

## 核心思想

利用"倍增"思想：预计算所有长度为2的幂次的子区间的答案。

`table[i][j]` = 从索引i开始、长度为2^j的子区间的最小值

## 预处理

```python
# Python: Sparse Table 构建
import math

class SparseTable:
    def __init__(self, nums):
        n = len(nums)
        k = int(math.log2(n)) + 1 if n > 0 else 1
        # table[i][j] = min of nums[i..i+2^j-1]
        self.table = [[0] * k for _ in range(n)]
        self.log = [0] * (n + 1)
        
        # 预计算log值
        for i in range(2, n + 1):
            self.log[i] = self.log[i // 2] + 1
        
        # 基础情况：长度为1的区间
        for i in range(n):
            self.table[i][0] = nums[i]
        
        # DP填表：合并两个半区间
        for j in range(1, k):
            for i in range(n - (1 << j) + 1):
                self.table[i][j] = min(
                    self.table[i][j-1],
                    self.table[i + (1 << (j-1))][j-1]
                )
```

⚠️ 注意：此为Python实现。位运算`1 << j`在所有主流语言中语法一致。

## O(1) 查询

关键洞察：任何区间[l, r]可以被两个可能重叠的2的幂次长度区间覆盖。

对于求最小值，两个区间重叠不影响结果（min操作是幂等的）。

```python
    def query(self, l, r):
        """O(1) 区间最小值查询"""
        j = self.log[r - l + 1]
        return min(
            self.table[l][j],
            self.table[r - (1 << j) + 1][j]
        )
```

## 为什么只适用于幂等操作

O(1)查询依赖于两个重叠子区间合并后结果不变：
- ✅ min, max, gcd, or, and（幂等操作）
- ❌ sum, xor（非幂等操作，重叠区间会重复计算）

对于非幂等操作的区间查询，需要使用线段树。

## 复杂度

| 操作 | 时间 | 空间 |
|------|------|------|
| 预处理 | O(n log n) | O(n log n) |
| 查询 | O(1) | - |
| 更新 | 不支持 | - |

## 与其他区间查询的对比

| 结构 | 预处理 | 查询 | 更新 | 适用 |
|------|--------|------|------|------|
| 暴力 | O(1) | O(n) | O(1) | - |
| 稀疏表 | O(n log n) | O(1) | ❌ | 静态数组最值 |
| 线段树 | O(n) | O(log n) | O(log n) | 动态数组 |
| 树状数组 | O(n) | O(log n) | O(log n) | 动态前缀和 |

## 与动态规划的关系

稀疏表的预处理过程本质上是一个DP：每个大区间的答案由两个小区间的答案合并而得，状态转移方向是区间长度从小到大。
