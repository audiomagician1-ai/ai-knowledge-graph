---
id: "primes"
concept: "素数"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 3
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 32.6
generation_method: "llm-rewrite-v2"
unique_content_ratio: 0.367
last_scored: "2026-03-22"
sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Prime number"
    url: "https://en.wikipedia.org/wiki/Prime_number"
  - type: "textbook-reference"
    ref: "Hardy & Wright. An Introduction to the Theory of Numbers, 6th ed."
scorer_version: "scorer-v2.0"
---
# 素数

## 概述

素数（Prime Number）是大于1的自然数中，除了1和自身外没有其他正因数的数。前几个素数为：2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...。特别地，**2是唯一的偶素数**。

素数的研究始于古希腊。欧几里得在《几何原本》第九卷命题20中证明了**素数有无穷多个**——这是数学史上最优美的证明之一。假设素数有限，设为 $p_1, p_2, \ldots, p_n$，考虑 $N = p_1 p_2 \cdots p_n + 1$，则 $N$ 不能被任何 $p_i$ 整除（余数为1），因此 $N$ 要么自身是素数，要么有一个不在列表中的素因子，矛盾。

素数是**算术基本定理**（Fundamental Theorem of Arithmetic）的核心：任何大于1的自然数都可以唯一分解为素数的乘积（不计顺序）。例如 $360 = 2^3 \times 3^2 \times 5$。

## 核心原理

### 素数判定

**试除法**：判定 $n$ 是否为素数，只需检查从2到 $\lfloor\sqrt{n}\rfloor$ 的所有整数是否整除 $n$。原理：若 $n = ab$ 且 $a \leq b$，则 $a \leq \sqrt{n}$。

**埃拉托斯特尼筛法**（Sieve of Eratosthenes，约公元前230年）：列出2到 $N$ 的所有整数，从2开始逐步划去每个素数的倍数，剩余的即为素数。找到 $N$ 以内的所有素数，时间复杂度为 $O(N \log \log N)$。

**Miller-Rabin检验**：现代概率性素性测试，对于大数（数百位）效率远高于试除法。2002年，Agrawal-Kayal-Saxena（AKS）算法证明素性测试可以在多项式时间内确定性完成。

### 素数分布

**素数定理**（Prime Number Theorem, 1896年Hadamard和de la Vallée-Poussin独立证明）：不超过 $x$ 的素数个数 $\pi(x)$ 近似为：

$$\pi(x) \sim \frac{x}{\ln x}$$

更精确地，$\pi(x) \sim \text{Li}(x) = \int_2^x \frac{dt}{\ln t}$。例如，$\pi(10^9) = 50,847,534$，而 $10^9 / \ln(10^9) \approx 48,254,942$（误差约5%）。

### 特殊素数

- **孪生素数**：相差2的素数对，如 $(11, 13)$、$(29, 31)$、$(71, 73)$。孪生素数猜想（是否有无穷多对）至今未解决。2013年张益唐证明存在无穷多个间距不超过7000万的素数对，陶哲轩等人将此上界缩小至246。
- **梅森素数**：形如 $2^p - 1$ 的素数（$p$ 本身也必须是素数）。截至2024年12月，已知最大素数为第52个梅森素数 $2^{136,279,841} - 1$（41,024,320位数），由GIMPS项目发现。
- **费马素数**：形如 $2^{2^n} + 1$ 的素数。已知仅5个：$3, 5, 17, 257, 65537$（$n = 0,1,2,3,4$）。

## 实际应用

1. **RSA密码系统**：选两个大素数（通常各1024位），其乘积作为公钥的一部分。破解RSA需要分解这个乘积，而当前最好的算法对2048位整数需要的计算量远超现有算力。

2. **哈希表设计**：使用素数作为哈希表大小可以减少碰撞概率。因为当模数为素数时，乘法散列的分布更均匀。

3. **数字水印与校验**：循环冗余校验（CRC）使用不可约多项式（多项式环中的"素数"）检测数据传输错误。

## 常见误区

1. **"1是素数"**：历史上确有数学家将1视为素数，但现代定义明确排除1。原因在于保证算术基本定理中分解的**唯一性**——若1是素数，则 $6 = 2 \times 3 = 1 \times 2 \times 3 = 1^2 \times 2 \times 3$ 等无穷种分解方式。

2. **"存在生成所有素数的公式"**：不存在简单的代数公式能生成所有素数。$n^2 - n + 41$ 对 $n = 1, 2, \ldots, 40$ 都给出素数（欧拉发现），但 $n = 41$ 时结果为 $41^2$（非素数）。

3. **"素数越来越稀疏，最终会消失"**：虽然素数密度趋于0（$\pi(x)/x \to 0$），但素数个数是无穷的。素数的绝对数量在任何范围内都在增长。

## 知识关联

**先修概念**：自然数、整除性、因数与倍数、最大公约数。

**后续发展**：素数直接连接同余理论与模运算、密码学基础（RSA、椭圆曲线）。在解析数论中，素数分布与黎曼ζ函数 $\zeta(s) = \sum_{n=1}^{\infty} n^{-s}$ 深度关联——黎曼猜想（1859年提出，至今未证明，千禧年奖金100万美元）正是关于ζ函数非平凡零点与素数分布的精确关系。

## 参考来源

- [Prime number - Wikipedia](https://en.wikipedia.org/wiki/Prime_number)
- Hardy, G.H. & Wright, E.M. *An Introduction to the Theory of Numbers*, 6th ed.
- GIMPS (Great Internet Mersenne Prime Search), https://www.mersenne.org
