---
id: "four-operations"
concept: "四则运算"
domain: "mathematics"
subdomain: "arithmetic"
subdomain_name: "算术"
difficulty: 1
is_milestone: false
tags: ["基础", "运算"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Knuth, The Art of Computer Programming, Vol. 2: Seminumerical Algorithms"
  - type: "research"
    name: "Karatsuba & Ofman (1962) Multiplication of Many-Digital Numbers by Automatic Computers"
scorer_version: "scorer-v2.0"
---
# 四则运算

## 定义与核心概念

四则运算是数学中四种基本算术操作的统称：**加法（Addition）、减法（Subtraction）、乘法（Multiplication）和除法（Division）**。它们构成了从小学算术到高等数学的计算基础，也是所有计算机算术运算的底层原语。

在 Peano 公理体系中，加法是唯一通过**后继函数**原始定义的运算，其余三种运算均可由加法派生：
- 减法 = 加法的逆运算
- 乘法 = 重复加法
- 除法 = 乘法的逆运算

## 运算的形式化定义

### 自然数上的递归定义

```
加法（Peano公理）：
  a + 0 = a                    （零元素）
  a + S(b) = S(a + b)          （递推，S为后继函数）

乘法：
  a × 0 = 0
  a × S(b) = a × b + a

幂运算（由乘法派生）：
  a⁰ = 1
  a^S(b) = a^b × a
```

### 运算律总结

| 性质 | 加法 | 乘法 | 减法 | 除法 |
|------|------|------|------|------|
| 交换律 | a+b = b+a ✓ | a×b = b×a ✓ | ✗ | ✗ |
| 结合律 | (a+b)+c = a+(b+c) ✓ | (a×b)×c = a×(b×c) ✓ | ✗ | ✗ |
| 单位元 | 0 | 1 | — | — |
| 逆元素 | -a (整数域) | 1/a (有理数域, a≠0) | — | — |
| 分配律 | — | a×(b+c) = a×b+a×c ✓ | — | (a+b)÷c = a÷c+b÷c ✓ (右分配) |

**关键洞察**：加法和乘法各自形成**交换幺半群**；在整数域上，加法形成**阿贝尔群**；在有理数域（除0外），乘法也形成阿贝尔群。这两个群通过分配律连接，构成**域**（Field）结构。

## 运算优先级

标准优先级规则（PEMDAS/BODMAS）：

```
括号 > 指数 > 乘除（同级，从左到右） > 加减（同级，从左到右）

示例：2 + 3 × 4² ÷ 2 - 1
     = 2 + 3 × 16 ÷ 2 - 1    （先指数）
     = 2 + 48 ÷ 2 - 1         （从左到右：乘）
     = 2 + 24 - 1              （除）
     = 25                       （加减）
```

**历史注记**：运算优先级并非"自然法则"，而是约定俗成。Cajori（1928, *A History of Mathematical Notations*）记录了18-19世纪优先级规则的逐步标准化过程。

## 算法复杂度

不同算法在 n 位数运算上的时间复杂度：

| 运算 | 朴素算法 | 最佳已知算法 | 备注 |
|------|---------|------------|------|
| 加法 | O(n) | O(n) | 已最优 |
| 减法 | O(n) | O(n) | 已最优 |
| 乘法 | O(n²) | O(n·log n)（Harvey & van der Hoeven, 2021） | Karatsuba: O(n^1.585) |
| 除法 | O(n²) | O(M(n))，M为乘法复杂度 | Newton迭代求逆 |

### Karatsuba 乘法（1962）

第一个打破 O(n²) 壁垒的乘法算法（Karatsuba & Ofman, 1962）：

```
将 n 位数 x, y 各分为高低两半：
x = x₁·B^m + x₀,  y = y₁·B^m + y₀  (B=基数, m=n/2)

朴素：x·y = x₁y₁·B^2m + (x₁y₀+x₀y₁)·B^m + x₀y₀  → 4次乘法

Karatsuba 技巧：
z₂ = x₁·y₁
z₀ = x₀·y₀
z₁ = (x₁+x₀)·(y₁+y₀) - z₂ - z₀  → 只需3次乘法！

x·y = z₂·B^2m + z₁·B^m + z₀

复杂度：T(n) = 3T(n/2) + O(n) → O(n^log₂3) ≈ O(n^1.585)
```

## 计算机中的实现

### 整数运算

| 表示 | 位宽 | 范围 | 溢出行为 |
|------|------|------|---------|
| unsigned int | 32 | 0 ~ 4,294,967,295 | 回绕（模 2³²） |
| signed int (补码) | 32 | -2,147,483,648 ~ 2,147,483,647 | 未定义（C标准） |
| int64 | 64 | ±9.2×10¹⁸ | 回绕 |

### 浮点运算（IEEE 754）

```
float32: 1位符号 + 8位指数 + 23位尾数
精度：约7位十进制有效数字
最大值：≈ 3.4 × 10³⁸

关键陷阱：
0.1 + 0.2 = 0.30000000000000004  (float64)
原因：0.1 的二进制表示是无限循环小数 0.0001100110011...
```

**Kahan 求和算法**（补偿求和）解决浮点加法的累积误差：
```python
def kahan_sum(values):
    s = 0.0
    c = 0.0  # 补偿值
    for x in values:
        y = x - c
        t = s + y
        c = (t - s) - y  # 丢失的低位
        s = t
    return s
```

## 除法的特殊性

除法是四则运算中唯一**不封闭**的运算（自然数除法结果可能不是自然数），也是唯一涉及**不可执行情况**（除以零）的运算。

不同数学系统对除以零的处理：
| 系统 | 1/0 的结果 | 理由 |
|------|-----------|------|
| 实数域 | 未定义 | 不存在满足 0×x=1 的 x |
| IEEE 754 | +∞ 或 -∞ | 实用约定（极限意义下） |
| 0/0 | NaN (Not a Number) | 不定式 |
| 射影几何 | ∞（有意义） | 扩展实数线 |

## 参考文献

- Knuth, D.E. (1997). *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 3rd ed. Addison-Wesley. ISBN 978-0201896848
- Karatsuba, A. & Ofman, Y. (1962). "Multiplication of Many-Digital Numbers by Automatic Computers," *Doklady Akademii Nauk SSSR*, 145(2), 293-294.
- Harvey, D. & van der Hoeven, J. (2021). "Integer multiplication in time O(n log n)," *Annals of Mathematics*, 193(2). [doi: 10.4007/annals.2021.193.2.4]

## 教学路径

**前置知识**：自然数概念、计数能力
**学习建议**：先通过实物操作建立加减法直觉，再理解乘法作为"重复加法"的本质。除法应分两阶段教学：先等分（12÷3="分成3份"），再包含（12÷3="每3个一组"）。运算律的记忆应结合代数结构理解而非死记硬背。
**进阶方向**：模运算与同余、计算机算术（补码、浮点）、快速乘法算法（FFT-based）。
