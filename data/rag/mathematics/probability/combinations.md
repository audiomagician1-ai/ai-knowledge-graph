---
id: "combinations"
concept: "组合"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 1
is_milestone: false
tags: ["计数", "组合数学"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Graham, Knuth & Patashnik, Concrete Mathematics, 2nd ed."
  - type: "textbook"
    name: "Brualdi, Introductory Combinatorics, 5th ed."
scorer_version: "scorer-v2.0"
---
# 组合

## 定义与核心概念

组合（Combination）是从 n 个不同元素中选取 k 个元素的**无序**选择方案数。与排列不同，组合不考虑元素的排列顺序——选 {A,B,C} 和 {C,A,B} 视为同一种组合。

二项式系数（Binomial Coefficient）的标准记号和公式：

```
C(n,k) = (n choose k) = n! / (k!(n-k)!)

等价递推定义（Pascal恒等式）：
C(n,k) = C(n-1,k-1) + C(n-1,k)
边界条件：C(n,0) = C(n,n) = 1
```

Graham, Knuth & Patashnik 在《Concrete Mathematics》中强调，二项式系数"可能是数学中出现频率最高的组合对象"（2nd ed., p.153）。

## 基本公式的推导

### 从排列到组合

从 n 中选 k 个的排列数 = P(n,k) = n!/(n-k)!

每种组合对应 k! 种排列（k 个元素的全排列），因此：

```
C(n,k) = P(n,k) / k! = n! / (k!(n-k)!)

数值示例：从5人中选3人
P(5,3) = 5×4×3 = 60（排列数）
C(5,3) = 60 / 3! = 60 / 6 = 10（组合数）
```

### Pascal三角与递推

```
         C(0,0)
        C(1,0) C(1,1)
      C(2,0) C(2,1) C(2,2)
    C(3,0) C(3,1) C(3,2) C(3,3)
  C(4,0) C(4,1) C(4,2) C(4,3) C(4,4)

数值：
       1
      1  1
     1  2  1
    1  3  3  1
   1  4  6  4  1
  1  5 10 10  5  1
```

Pascal 恒等式的组合解释：n 中选 k，对某个特定元素 x：
- 要么选了 x → 从剩余 n-1 中再选 k-1：C(n-1,k-1)
- 要么没选 x → 从剩余 n-1 中选 k：C(n-1,k)

## 关键恒等式

| 恒等式 | 公式 | 组合解释 |
|--------|------|---------|
| 对称性 | C(n,k) = C(n,n-k) | 选k个 = 排除n-k个 |
| Vandermonde | C(m+n,r) = Σ C(m,k)·C(n,r-k) | 从两组分别选 |
| 行和 | Σ C(n,k) = 2ⁿ | n元素子集总数 |
| 交错和 | Σ(-1)ᵏC(n,k) = 0 | 奇偶子集数相等 |
| 上指标求和 | Σ C(i,k) [i=k..n] = C(n+1,k+1) | Hockey stick恒等式 |
| 倍增 | C(2n,n) = Σ C(n,k)² | Catalan数的基础 |

## 二项式定理

组合最重要的代数应用：

```
(x + y)ⁿ = Σ C(n,k) · xᵏ · yⁿ⁻ᵏ  [k=0..n]

示例：(a+b)⁴ = a⁴ + 4a³b + 6a²b² + 4ab³ + b⁴
系数恰好是 Pascal 第4行：1, 4, 6, 4, 1
```

**推广**：Newton 广义二项式定理（1665）将指数推广到非整数/负数：
```
(1+x)^α = Σ C(α,k) · xᵏ  [k=0..∞]，|x|<1

其中 C(α,k) = α(α-1)(α-2)...(α-k+1) / k!
```

## 组合模型的分类

| 模型 | 有序? | 可重复? | 公式 | 示例 |
|------|------|--------|------|------|
| 排列 | 是 | 否 | P(n,k)=n!/(n-k)! | 赛跑名次 |
| 组合 | 否 | 否 | C(n,k) | 选委员会 |
| 可重排列 | 是 | 是 | nᵏ | 密码组合 |
| 可重组合 | 否 | 是 | C(n+k-1,k) | 糖果分配 |

### 可重组合（Stars and Bars）

从 n 种中选 k 个（可重复），等价于将 k 个星星用 n-1 个隔板分为 n 组：

```
C(n+k-1, k) = C(n+k-1, n-1)

示例：从3种水果中选5个
C(3+5-1, 5) = C(7,5) = 21 种方案
```

## 计算技巧

### 大数组合的对数计算

直接计算 C(100,50) 会溢出（≈ 10²⁹），使用对数：
```
log C(n,k) = Σ log(i) [i=1..n] - Σ log(i) [i=1..k] - Σ log(i) [i=1..n-k]
           = log(n!) - log(k!) - log((n-k)!)

Stirling近似：log(n!) ≈ n·log(n) - n + 0.5·log(2πn)
```

### 递推计算（避免溢出）

```python
# Python: 逐步乘除避免中间值爆炸
def comb(n, k):
    if k > n - k:
        k = n - k  # C(n,k) = C(n,n-k)，取较小的k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

# comb(100, 50) = 100891344545564193334812497256
```

## 应用实例

### 概率计算：扑克牌型

```
52张牌选5张总方案数：C(52,5) = 2,598,960

皇家同花顺：4种（每种花色1种）
概率 = 4 / 2,598,960 = 1/649,740 ≈ 0.000154%

同花（5张同花色，不含顺子和同花顺）：
C(4,1)·C(13,5) - 40 = 4·1287 - 40 = 5,108
概率 = 5,108 / 2,598,960 ≈ 0.197%
```

### 算法：子集枚举

```python
# 位掩码枚举所有 C(n,k) 个k元子集
def k_subsets(n, k):
    if k == 0:
        yield []
        return
    for i in range(k-1, n):
        for subset in k_subsets(i, k-1):
            yield subset + [i]
```

## 参考文献

- Graham, R.L., Knuth, D.E. & Patashnik, O. (1994). *Concrete Mathematics*, 2nd ed. Addison-Wesley. ISBN 978-0201558029
- Brualdi, R.A. (2009). *Introductory Combinatorics*, 5th ed. Pearson. ISBN 978-0136020400
- Stanley, R.P. (2011). *Enumerative Combinatorics*, Vol. 1, 2nd ed. Cambridge University Press.

## 教学路径

**前置知识**：阶乘、基本排列概念
**学习建议**：先通过小例子（从5选3的10种方案手动列举）建立直觉，再掌握 C(n,k)公式。Pascal三角是理解递推关系的最佳工具。之后学习二项式定理并练习展开 (a+b)ⁿ。
**进阶方向**：生成函数方法、容斥原理、Catalan数与组合恒等式的证明技巧。
