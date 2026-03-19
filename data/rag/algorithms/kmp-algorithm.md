---
concept: kmp-algorithm
subdomain: algorithms
difficulty: 7
prereqs: [string-matching]
---

# KMP算法

## 核心概念

KMP（Knuth-Morris-Pratt）算法是一种高效的字符串匹配算法。当匹配失败时，它利用已匹配部分的信息避免重复比较，将时间复杂度从暴力的O(mn)降低到O(m+n)。

## 核心思想：失败函数（Failure Function）

也称为部分匹配表（Partial Match Table）或前缀函数（Prefix Function）。

对于模式串P，fail[i]表示P[0..i]的最长公共前后缀长度。

**示例**: 模式串 `ABCABD`
```
索引:  0 1 2 3 4 5
字符:  A B C A B D
fail: 0 0 0 1 2 0
```
- fail[3]=1: "ABCA" 的最长公共前后缀是 "A"，长度1
- fail[4]=2: "ABCAB" 的最长公共前后缀是 "AB"，长度2

## 算法流程

```python
# Python: 构建失败函数
def build_failure(pattern):
    m = len(pattern)
    fail = [0] * m
    j = 0  # 前缀指针
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j - 1]  # 回退
        if pattern[i] == pattern[j]:
            j += 1
        fail[i] = j
    return fail

# Python: KMP搜索
def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    fail = build_failure(pattern)
    j = 0  # 模式串指针
    results = []
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = fail[j - 1]  # 利用失败函数回退
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            results.append(i - m + 1)  # 匹配位置
            j = fail[j - 1]  # 继续寻找下一个匹配
    return results
```

⚠️ 注意：此为Python实现。C++/Java的字符串索引和循环语法有所不同，但算法逻辑完全一致。

## 为什么KMP是O(m+n)

- 构建失败函数：O(m)
- 搜索过程中，文本指针i只增不减，共走n步
- 模式指针j的回退总次数不超过前进总次数
- 整体: O(m + n)

## 复杂度对比

| 算法 | 最坏时间 | 空间 |
|------|---------|------|
| 暴力匹配 | O(mn) | O(1) |
| KMP | O(m+n) | O(m) |
| Rabin-Karp | O(m+n)平均 | O(1) |
| Boyer-Moore | O(mn)最坏, O(n/m)最好 | O(k) |

## 典型应用

1. **文本搜索**: 在长文本中查找关键词
2. **重复子串**: 利用失败函数判断周期性
3. **最短循环节**: 如果n%(n-fail[n-1])==0，则循环节长度为n-fail[n-1]

## 与字符串匹配的关系

KMP是字符串匹配（String Matching）问题的经典解法。理解暴力匹配的局限性（重复比较），才能理解KMP通过失败函数跳过无效比较的精妙之处。
