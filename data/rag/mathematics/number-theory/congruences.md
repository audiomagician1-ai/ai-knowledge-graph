---
id: "congruences"
concept: "同余理论"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 5
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 32.0
generation_method: "llm-rewrite-v2"
unique_content_ratio: 0.344
last_scored: "2026-03-22"
sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Modular arithmetic"
    url: "https://en.wikipedia.org/wiki/Modular_arithmetic"
  - type: "textbook-reference"
    ref: "Hardy & Wright. An Introduction to the Theory of Numbers, 6th ed."
scorer_version: "scorer-v2.0"
---
# 同余理论

## 概述

同余（Congruence）是数论中描述整数除法余数关系的核心概念，由德国数学家卡尔·弗里德里希·高斯（Carl Friedrich Gauss）于1801年在其里程碑式著作《算术研究》（*Disquisitiones Arithmeticae*）中系统化提出。

**定义**：对于整数 $a$、$b$ 和正整数 $m$，若 $m$ 整除 $(a - b)$，则称 $a$ 与 $b$ 模 $m$ 同余，记作：

$$a \equiv b \pmod{m}$$

等价地，$a$ 和 $b$ 除以 $m$ 的余数相同。例如 $17 \equiv 2 \pmod{5}$，因为 $17 - 2 = 15$ 是5的倍数。

同余理论是现代密码学（RSA算法）、计算机科学（哈希函数）和代数数论的基石。

## 核心原理

### 同余的基本性质

同余关系是等价关系，满足三大性质：
- **自反性**：$a \equiv a \pmod{m}$
- **对称性**：若 $a \equiv b \pmod{m}$，则 $b \equiv a \pmod{m}$
- **传递性**：若 $a \equiv b$ 且 $b \equiv c \pmod{m}$，则 $a \equiv c \pmod{m}$

**运算兼容性**：若 $a \equiv b$ 且 $c \equiv d \pmod{m}$，则：
- $a + c \equiv b + d \pmod{m}$（加法）
- $a \cdot c \equiv b \cdot d \pmod{m}$（乘法）
- $a^n \equiv b^n \pmod{m}$（幂运算）

**注意**：除法不能直接运算。$a \cdot c \equiv b \cdot c \pmod{m}$ 仅当 $\gcd(c, m) = 1$ 时才能消去 $c$。

### 剩余类与模运算

模 $m$ 的全体整数被划分为 $m$ 个**剩余类**（residue classes）：$\{[0], [1], [2], \ldots, [m-1]\}$。这些剩余类构成**整数模 m 的环** $\mathbb{Z}/m\mathbb{Z}$（或简记 $\mathbb{Z}_m$）。

当 $m$ 为素数 $p$ 时，$\mathbb{Z}_p$ 不仅是环，还是**域**——每个非零元素都有乘法逆元。例如在 $\mathbb{Z}_7$ 中，$3 \times 5 = 15 \equiv 1 \pmod{7}$，所以 $3^{-1} \equiv 5 \pmod{7}$。

### 费马小定理与欧拉定理

**费马小定理**（Fermat's Little Theorem, 1640年）：若 $p$ 为素数且 $\gcd(a, p) = 1$，则 $a^{p-1} \equiv 1 \pmod{p}$。

例如：$2^{6} = 64 \equiv 1 \pmod{7}$。

**欧拉推广**：对任意正整数 $m$，若 $\gcd(a, m) = 1$，则 $a^{\varphi(m)} \equiv 1 \pmod{m}$，其中欧拉函数 $\varphi(m)$ 表示 $1$ 到 $m$ 中与 $m$ 互素的整数个数。当 $m = p$（素数）时 $\varphi(p) = p - 1$，退化为费马小定理。

### 中国剩余定理

**中国剩余定理**（Chinese Remainder Theorem，CRT）最早见于南宋数学家秦九韶1247年的《数书九章》中"物不知其数"问题：有物不知其数，三三数之剩二，五五数之剩三，七七数之剩二，问物几何？

形式化表述：若 $m_1, m_2, \ldots, m_k$ 两两互素，则同余方程组 $x \equiv a_i \pmod{m_i}$ 在模 $M = m_1 m_2 \cdots m_k$ 下有唯一解。

## 实际应用

1. **RSA加密算法**：公钥密码学的基础。选两个大素数 $p, q$，计算 $n = pq$。加密：$c \equiv m^e \pmod{n}$；解密利用 $m \equiv c^d \pmod{n}$，其中 $ed \equiv 1 \pmod{\varphi(n)}$。RSA的安全性依赖于大整数分解的计算困难性。

2. **哈希函数**：计算机中常用 $h(k) = k \bmod m$ 作为哈希函数，将键值映射到 $[0, m-1]$ 的桶中。

3. **ISBN校验码**：ISBN-13的校验位使用模10运算验证条码正确性。

## 常见误区

1. **"同余可以随意做除法"**：$6 \equiv 0 \pmod{6}$ 但不能两边除以2得出 $3 \equiv 0 \pmod{6}$（事实上 $3 \not\equiv 0 \pmod{6}$）。除法仅在除数与模数互素时有效。

2. **"模运算结果总是正数"**：数学定义中 $-1 \equiv 4 \pmod{5}$，但不同编程语言对负数取模的结果不同（Python返回非负值，C++可能返回负值）。

3. **"费马小定理对所有整数成立"**：条件 $\gcd(a, p) = 1$ 不可省略。$0^{p-1} = 0 \not\equiv 1 \pmod{p}$。

## 知识关联

**先修概念**：整除性、最大公约数（欧几里得算法）、素数基础。

**后续发展**：同余理论直接引向二次互反律（Gauss称之为"算术的宝石"）、椭圆曲线上的模运算（椭圆曲线密码学ECC的基础）、以及抽象代数中的群论和环论。

## 参考来源

- [Modular arithmetic - Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- Hardy, G.H. & Wright, E.M. *An Introduction to the Theory of Numbers*, 6th ed., Oxford University Press.
- Gauss, C.F. *Disquisitiones Arithmeticae* (1801).
