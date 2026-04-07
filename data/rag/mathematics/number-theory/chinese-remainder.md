---
id: "chinese-remainder"
concept: "中国剩余定理"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 中国剩余定理

## 概述

中国剩余定理（Chinese Remainder Theorem，CRT）是数论中求解一次同余方程组的基本定理，描述了在模数两两互质的条件下，方程组 $x \equiv a_i \pmod{m_i}$（$i = 1, 2, \ldots, k$）存在唯一模 $M = m_1 m_2 \cdots m_k$ 的解。该定理得名于中国古代数学著作《孙子算经》（约公元3至5世纪），书中记载了"今有物不知其数，三三数之剩二，五五数之剩三，七七数之剩二，问物几何"这一经典问题，答案为23。

该定理在西方由欧拉和高斯分别在18至19世纪进行了形式化表述，高斯在1801年出版的《算术研究》中给出了严格证明。中国剩余定理在现代密码学（如RSA加速计算）、计算机科学（大整数运算）和组合数学中均有直接应用，是连接初等数论与抽象代数的关键结论之一。

## 核心原理

### 定理的精确表述与存在性条件

设正整数 $m_1, m_2, \ldots, m_k$ **两两互质**，即对任意 $i \neq j$ 有 $\gcd(m_i, m_j) = 1$。令 $M = m_1 m_2 \cdots m_k$，$M_i = M / m_i$。则对任意整数 $a_1, a_2, \ldots, a_k$，方程组

$$x \equiv a_i \pmod{m_i}, \quad i = 1, 2, \ldots, k$$

在模 $M$ 意义下有唯一解。两两互质是充分且必要的基础条件——若某两个模数不互质，方程组可能无解或解不唯一。

### 构造解的公式

定理的证明是构造性的，给出了显式求解算法。由于 $\gcd(M_i, m_i) = 1$，存在 $M_i$ 关于模 $m_i$ 的逆元 $t_i$，即满足 $M_i t_i \equiv 1 \pmod{m_i}$。$t_i$ 可通过扩展欧几里得算法求得。于是，方程组的通解为：

$$x = \sum_{i=1}^{k} a_i M_i t_i \pmod{M}$$

验证正确性：对每个 $j$，当 $i \neq j$ 时 $m_j \mid M_i$，故第 $i$ 项在模 $m_j$ 下为零，仅剩第 $j$ 项 $a_j M_j t_j \equiv a_j \cdot 1 = a_j \pmod{m_j}$，满足所有方程。

### 验证孙子算经原题

以《孙子算经》原题为例：$m_1=3, m_2=5, m_3=7$，$a_1=2, a_2=3, a_3=2$，$M=105$。

- $M_1=35$，$35 t_1 \equiv 1 \pmod{3}$，即 $2t_1 \equiv 1 \pmod{3}$，解得 $t_1=2$
- $M_2=21$，$21 t_2 \equiv 1 \pmod{5}$，即 $t_2 \equiv 1 \pmod{5}$，解得 $t_2=1$
- $M_3=15$，$15 t_3 \equiv 1 \pmod{7}$，即 $t_3 \equiv 1 \pmod{7}$，解得 $t_3=1$

$$x = 2 \times 35 \times 2 + 3 \times 21 \times 1 + 2 \times 15 \times 1 = 140 + 63 + 30 = 233 \equiv 23 \pmod{105}$$

最小正整数解为23，与原题答案一致。

### 代数结构视角

中国剩余定理等价于环同构 $\mathbb{Z}/M\mathbb{Z} \cong \mathbb{Z}/m_1\mathbb{Z} \times \mathbb{Z}/m_2\mathbb{Z} \times \cdots \times \mathbb{Z}/m_k\mathbb{Z}$。当 $m_i$ 两两互质时，这一同构由映射 $x \mapsto (x \bmod m_1, x \bmod m_2, \ldots, x \bmod m_k)$ 给出，且该映射是双射。此观点将CRT从解方程组推广到模环的分解，是抽象代数中的核心同构定理之一。

## 实际应用

**RSA算法加速**：在RSA私钥解密中，已知素因子 $p$ 和 $q$（$n=pq$），可分别计算 $d_p = d \bmod (p-1)$，$d_q = d \bmod (q-1)$，再用CRT将两个模 $p$ 和模 $q$ 的结果合并，相比直接计算 $m^d \bmod n$ 快约4倍，这一优化称为RSA-CRT。

**计算机多精度运算**：选取多个不超过机器字长的小素数 $m_i$，将大整数运算拆分为多个小整数的并行运算，最后用CRT重建结果，可高效处理数百位乃至数千位整数的乘法，避免了大整数直接存储的溢出问题。

**竞赛题中的应用**：在数学竞赛中，CRT常用于确定满足多个余数条件的最小正整数。例如"某数除以4余1，除以5余2，除以7余4，求最小正整数解"：$M=140$，按公式计算得解为 $x \equiv 137 \pmod{140}$，即137。

## 常见误区

**误区一：模数不互质时直接套用公式**。学生常忽略两两互质的前提，对 $x \equiv 1 \pmod{6}$ 与 $x \equiv 3 \pmod{4}$ 直接使用CRT公式。但 $\gcd(6,4)=2 \neq 1$，此时定理不适用，需先检验相容条件（$a_1 \equiv a_2 \pmod{\gcd(m_1,m_2)}$，即 $1 \equiv 3 \pmod{2}$ 不成立），故该方程组无解。

**误区二：混淆唯一解的范围**。CRT保证解在模 $M$ 意义下唯一，而非在所有整数中唯一。对模 $M=105$ 的方程组，$x=23$ 和 $x=128$（$=23+105$）都是解，只是同余意义下的同一个解。学生常误将"唯一解"理解为"只有一个整数解"，从而漏写周期性。

**误区三：认为逆元可以任意取**。在计算 $M_i t_i \equiv 1 \pmod{m_i}$ 时，若取 $t_i$ 为负数（如 $t_i = -1$ 而非 $m_i - 1$），代入公式后得到负的中间值，求和后对 $M$ 取模仍然正确，但部分学生在不对 $M$ 取模的情况下直接报告负数为答案。扩展欧几里得算法的输出可能为负值，须调整为正余数。

## 知识关联

中国剩余定理以**同余理论**（模运算定义、同余类性质）和**扩展欧几里得算法**（求乘法逆元 $M_i t_i \equiv 1 \pmod{m_i}$）为直接前提，缺少逆元的计算方法将无法完成构造解的关键步骤。理解 $\gcd(M_i, m_i)=1$ 的推导须依赖最大公因数的基本性质。

在代数方向，CRT直接引出**环同构**的概念，是抽象代数中研究有限交换环分解的经典范例，为进一步学习**欧拉定理**、**费马小定理**的推广以及**整数分拆**提供了结构化工具。在密码学方向，CRT是理解RSA-CRT优化、Pohlig-Hellman离散对数算法以及格密码中相关约简的必要基础。