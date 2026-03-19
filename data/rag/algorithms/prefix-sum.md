---
concept: prefix-sum
subdomain: algorithms
difficulty: 4
prereqs: [array-internals, time-complexity]
---

# 前缀和

## 核心概念

前缀和（Prefix Sum）是一种预处理技术，通过预先计算数组从头到每个位置的累积和，使得任意区间和查询可以在O(1)时间内完成。

## 基本原理

给定数组 `nums = [a₀, a₁, a₂, ..., aₙ₋₁]`

前缀和数组 `prefix[i] = nums[0] + nums[1] + ... + nums[i-1]`

区间和 `sum(l, r) = prefix[r+1] - prefix[l]`

```python
# Python 构建前缀和
def build_prefix_sum(nums):
    n = len(nums)
    prefix = [0] * (n + 1)  # prefix[0] = 0 作为哨兵
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]
    return prefix

# 查询区间 [l, r] 的和
def range_sum(prefix, l, r):
    return prefix[r + 1] - prefix[l]
```

⚠️ 注意：此为Python实现。在C++/Java中数组索引语法相同，但需注意数组越界检查。

## 复杂度分析

| 操作 | 暴力方法 | 前缀和方法 |
|------|---------|-----------|
| 预处理 | O(1) | O(n) |
| 单次区间和 | O(n) | O(1) |
| M次区间和 | O(M·n) | O(n + M) |

当查询次数M较大时，前缀和的优势非常明显。

## 二维前缀和

扩展到矩阵的子矩阵和查询：
```
prefix[i][j] = 从(0,0)到(i-1,j-1)的矩形区域和
```

构建利用容斥原理：
```
prefix[i][j] = prefix[i-1][j] + prefix[i][j-1] - prefix[i-1][j-1] + matrix[i-1][j-1]
```

## 差分数组（逆操作）

前缀和的逆运算——差分数组：
- `diff[i] = nums[i] - nums[i-1]`
- 对差分数组做前缀和可以还原原数组
- 用途：O(1)完成区间加减操作

## 典型应用

1. **子数组和等于K**: 前缀和+哈希表，O(n)
2. **区域和检索**: 二维前缀和预处理
3. **航班预订统计**: 差分数组+前缀和
4. **和为K的最长子数组**: 前缀和+哈希表

## 与数组和时间复杂度的关系

前缀和是数组操作的经典优化技巧。理解数组的连续存储特性和时间复杂度分析是使用前缀和的基础。
