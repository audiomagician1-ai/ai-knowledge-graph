---
id: "fenwick-tree"
concept: "树状数组"
domain: "ai-engineering"
subdomain: "data-structures"
subdomain_name: "数据结构"
difficulty: 7
is_milestone: false
tags: ["高级数据结构"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 66.5
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 树状数组（Fenwick Tree）

## 核心概念

树状数组（Binary Indexed Tree / Fenwick Tree）是一种支持单点更新和前缀和查询的数据结构，两种操作均为O(log n)。它比线段树更简洁，常数因子更小。

## 核心思想

利用二进制表示将数组划分为不同长度的段：
- tree[i] 存储从 i-lowbit(i)+1 到 i 的区间和
- lowbit(i) = i & (-i)，即i的最低有效位

## 基本操作

```python
# Python: 树状数组
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)  # 1-indexed
    
    def update(self, i, delta):
        """单点增加：a[i] += delta"""
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # 加上lowbit
    
    def prefix_sum(self, i):
        """前缀和：a[1] + a[2] + ... + a[i]"""
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)  # 减去lowbit
        return s
    
    def range_sum(self, l, r):
        """区间和：a[l] + ... + a[r]"""
        return self.prefix_sum(r) - self.prefix_sum(l - 1)
```

⚠️ 注意：此为Python实现。树状数组使用1-indexed（从1开始），这在所有语言中都一样。

## lowbit的含义

`lowbit(i) = i & (-i)` 返回i的最低位的1所代表的值：
```
i = 12 = 1100₂  →  lowbit = 100₂ = 4
i =  6 = 0110₂  →  lowbit = 010₂ = 2
i =  7 = 0111₂  →  lowbit = 001₂ = 1
```

- 更新时: 向上走(i += lowbit)，沿着父节点路径
- 查询时: 向下走(i -= lowbit)，收集不重叠区间的和

## 与线段树的对比

| 特征 | 树状数组 | 线段树 |
|------|---------|--------|
| 空间 | O(n) | O(4n) |
| 常数因子 | 小 | 大 |
| 实现复杂度 | 简单 | 复杂 |
| 区间更新 | 需要技巧 | 原生支持(懒传播) |
| 区间最值 | 不支持 | 支持 |
| 离线查询 | 不适合 | 可持久化 |

## 典型应用

1. **动态前缀和**: 需要频繁更新和查询的场景
2. **逆序对计数**: 离散化后用树状数组统计
3. **区间更新+单点查询**: 用差分数组+树状数组

## 与二叉树和前缀和的关系

树状数组的结构灵感来自二叉树，但存储方式更紧凑。它是前缀和的动态版本——当数组需要频繁修改时，静态前缀和需要O(n)重建，树状数组只需O(log n)更新。
