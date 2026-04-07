---
id: "euler-theorem"
concept: "欧拉定理"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 7
is_milestone: false
tags: ["定理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 77.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.944
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 欧拉定理

## 概述

欧拉定理是数论中关于模运算的一个基本结论：若整数 $a$ 与正整数 $n$ 互质（即 $\gcd(a, n) = 1$），则 $a^{\varphi(n)} \equiv 1 \pmod{n}$，其中 $\varphi(n)$ 是欧拉函数（也称欧拉totient函数），表示 $1$ 到 $n$ 中与 $n$ 互质的正整数个数。这一定理由瑞士数学家莱昂哈德·欧拉（Leonhard Euler）于1763年正式证明，发表于他的论文集中。

欧拉定理之所以重要，在于它将"幂次模运算"与"乘法群的阶"紧密连接。$a^{\varphi(n)} \equiv 1 \pmod{n}$ 这一等式揭示了整数 $a$ 在模 $n$ 乘法群 $(\mathbb{Z}/n\mathbb{Z})^*$ 中的周期行为：$a$ 的模 $n$ 幂次必在不超过 $\varphi(n)$ 步内回到 $1$。这不仅是纯理论的结果，更是现代 RSA 加密算法能够正确解密的数学基石。

欧拉定理是费马小定理的直接推广。费马小定理仅适用于 $n$ 为素数的情形，此时 $\varphi(p) = p - 1$，定理退化为 $a^{p-1} \equiv 1 \pmod{p}$。欧拉定理将这一结论扩展至任意与 $n$ 互质的 $a$，无论 $n$ 是合数还是素数。

---

## 核心原理

### 欧拉函数 $\varphi(n)$ 的计算

欧拉函数 $\varphi(n)$ 的计算依赖 $n$ 的质因数分解。若 $n = p_1^{k_1} p_2^{k_2} \cdots p_r^{k_r}$，则：

$$\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)$$

例如，$n = 12 = 2^2 \times 3$，则 $\varphi(12) = 12 \times (1 - \frac{1}{2}) \times (1 - \frac{1}{3}) = 4$。与 $12$ 互质的数为 $1, 5, 7, 11$，恰好 4 个。对于素数 $p$，$\varphi(p) = p - 1$；对于素数幂 $p^k$，$\varphi(p^k) = p^{k-1}(p-1)$。欧拉函数还是**积性函数**：若 $\gcd(m, n) = 1$，则 $\varphi(mn) = \varphi(m)\varphi(n)$。

### 定理的证明思路：构造完全余数系

欧拉定理的标准证明基于模 $n$ 的**简化剩余系**（缩系）。设 $\{r_1, r_2, \ldots, r_{\varphi(n)}\}$ 是模 $n$ 的缩系，即所有与 $n$ 互质的余数类的代表元。由于 $\gcd(a, n) = 1$，集合 $\{ar_1, ar_2, \ldots, ar_{\varphi(n)}\}$ 模 $n$ 后仍是缩系的一个排列（两个不同元素 $ar_i \equiv ar_j \pmod{n}$ 将推出 $r_i \equiv r_j$，矛盾）。因此：

$$\prod_{i=1}^{\varphi(n)} (ar_i) \equiv \prod_{i=1}^{\varphi(n)} r_i \pmod{n}$$

左边等于 $a^{\varphi(n)} \prod r_i$，右边等于 $\prod r_i$。由于 $\prod r_i$ 与 $n$ 互质，可以消去，得 $a^{\varphi(n)} \equiv 1 \pmod{n}$。

### 元素的阶与欧拉定理的关系

在群论语言下，$a$ 模 $n$ 的**阶**（order）定义为使 $a^d \equiv 1 \pmod{n}$ 成立的最小正整数 $d$，记作 $\text{ord}_n(a)$。欧拉定理保证这样的 $d$ 存在且 $d \mid \varphi(n)$。例如，取 $n = 7$，$a = 3$：$3^1=3,\ 3^2=2,\ 3^3=6,\ 3^4=4,\ 3^5=5,\ 3^6 \equiv 1 \pmod{7}$，故 $\text{ord}_7(3) = 6 = \varphi(7)$，说明 3 是模 7 的**原根**。但对 $a=2$：$2^3 = 8 \equiv 1 \pmod 7$，故 $\text{ord}_7(2) = 3$，它是 $\varphi(7) = 6$ 的因子，不等于 $\varphi(n)$，说明欧拉定理给出的是幂次周期的**上界**，不一定是最小周期。

---

## 实际应用

**计算大幂次模运算**：欧拉定理可大幅简化模幂运算。例如，计算 $3^{100} \pmod{13}$。由于 $\gcd(3, 13) = 1$ 且 $\varphi(13) = 12$，所以 $3^{12} \equiv 1 \pmod{13}$。将 $100 = 12 \times 8 + 4$ 代入，得 $3^{100} = (3^{12})^8 \cdot 3^4 \equiv 1^8 \cdot 81 \equiv 81 \pmod{13}$。而 $81 = 6 \times 13 + 3$，故 $3^{100} \equiv 3 \pmod{13}$。

**RSA 加密算法的解密正确性**：RSA 选取两个大素数 $p, q$，令 $n = pq$，则 $\varphi(n) = (p-1)(q-1)$。公钥 $e$ 和私钥 $d$ 满足 $ed \equiv 1 \pmod{\varphi(n)}$。加密为 $c \equiv m^e \pmod{n}$，解密为 $c^d \equiv m^{ed} \pmod{n}$。由于 $ed = 1 + k\varphi(n)$，欧拉定理保证 $m^{ed} = m \cdot (m^{\varphi(n)})^k \equiv m \cdot 1^k = m \pmod{n}$（当 $\gcd(m, n) = 1$ 时），从而解密正确还原明文 $m$。

**模逆元的存在性**：欧拉定理直接给出 $a^{-1} \equiv a^{\varphi(n)-1} \pmod{n}$，即 $a$ 模 $n$ 的乘法逆元为 $a^{\varphi(n)-1}$。例如，$5^{-1} \pmod{12}$：$\varphi(12)=4$，故 $5^{-1} \equiv 5^3 = 125 \equiv 5 \pmod{12}$（即 $5 \times 5 = 25 \equiv 1$，验证正确）。

---

## 常见误区

**误区一：忽略互质条件，误用欧拉定理**。欧拉定理要求 $\gcd(a, n) = 1$，若此条件不满足则定理完全失效。例如，$\gcd(6, 12) = 6 \neq 1$，此时 $6^{\varphi(12)} = 6^4 = 1296$，而 $1296 \div 12 = 108$，$1296 \equiv 0 \pmod{12}$，显然不等于 $1$。许多初学者在 $n$ 为合数时不验证互质条件便直接套用公式，导致错误。

**误区二：将 $\varphi(n)$ 误认为幂次的最小周期**。欧拉定理只保证 $a^{\varphi(n)} \equiv 1 \pmod{n}$，但 $a$ 的实际阶 $\text{ord}_n(a)$ 是 $\varphi(n)$ 的因子，可能远小于 $\varphi(n)$。例如 $a=2, n=15$：$\varphi(15) = 8$，但 $2^4 = 16 \equiv 1 \pmod{15}$，故 $\text{ord}_{15}(2) = 4$，仅为 $\varphi(15)$ 的一半。在需要最小周期的场合（如密码分析），必须单独计算 $\text{ord}_n(a)$，不能直接以 $\varphi(n)$ 代替。

**误区三：混淆欧拉定理与中国剩余定理的适用范围**。部分学生在处理模合数问题时，将欧拉定理的 $\varphi(n)$ 与中国剩余定理中的模数分解混用。欧拉定理直接给出整体模 $n$ 的幂次结论，而中国剩余定理是将模 $n$ 的方程组拆解到各素数幂因子上分别求解，二者逻辑目标不同，不可互换。

---

## 知识关联

**前置概念——费马小定理**：费马小定理（$a^{p-1} \equiv 1 \pmod p$，$p$ 为素数）是欧拉定理在 $n = p$ 时的特例。理解费马小定理的证明（同样基于缩系排列思想）可以直接迁