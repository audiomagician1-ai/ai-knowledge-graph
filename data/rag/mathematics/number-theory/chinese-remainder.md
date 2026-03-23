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
quality_tier: "pending-rescore"
quality_score: 39.4
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 中国剩余定理

## 概述

中国剩余定理（Chinese Remainder Theorem，简称CRT）是数论中用于求解一次同余方程组的核心定理，描述了在模数两两互质的条件下，方程组解的存在性与唯一性。具体地，给定两两互质的正整数 $m_1, m_2, \ldots, m_k$，以及任意整数 $a_1, a_2, \ldots, a_k$，方程组 $x \equiv a_i \pmod{m_i}$（$i=1,2,\ldots,k$）在模 $M = m_1 m_2 \cdots m_k$ 意义下有唯一解。

该定理最早出现于中国南北朝时期数学家孙子（约公元3–5世纪）的著作《孙子算经》中，其中"物不知数"问题是原始形式：一数除以3余2、除以5余3、除以7余2，问该数为何。答案为23。南宋数学家秦九韶于1247年在《数书九章》中给出了系统的算法"大衍求一术"，是世界上最早的完整构造性证明。西方数学家高斯（Gauss）在1801年《算术研究》中独立重新发现并推广了这一定理。

中国剩余定理在密码学（尤其是RSA加速计算）、计算机科学（大整数并行运算）以及竞赛数论中均有直接应用。它将一个模大数的问题分解为多个模小数的独立子问题，极大地降低计算复杂度。

## 核心原理

### 定理的精确表述

设 $m_1, m_2, \ldots, m_k$ 是两两互质的正整数，令 $M = \prod_{i=1}^{k} m_i$。对每个 $i$，令 $M_i = M / m_i$（即除去 $m_i$ 的其余模数之积）。由于 $\gcd(M_i, m_i) = 1$，存在 $M_i$ 在模 $m_i$ 意义下的逆元 $t_i$，满足 $M_i t_i \equiv 1 \pmod{m_i}$。则方程组的解为：

$$x \equiv \sum_{i=1}^{k} a_i M_i t_i \pmod{M}$$

这个表达式给出了模 $M$ 意义下的唯一解。注意此公式依赖两两互质条件——若该条件不满足，解可能不存在，或存在但不唯一。

### 构造解的步骤

以"物不知数"为例，说明逐步构造：$m_1=3, m_2=5, m_3=7$，$M=105$。
- $M_1 = 35$，求 $35 t_1 \equiv 1 \pmod{3}$，即 $2t_1 \equiv 1 \pmod{3}$，得 $t_1 = 2$；
- $M_2 = 21$，求 $21 t_2 \equiv 1 \pmod{5}$，即 $t_2 \equiv 1 \pmod{5}$，得 $t_2 = 1$；
- $M_3 = 15$，求 $15 t_3 \equiv 1 \pmod{7}$，即 $t_3 \equiv 1 \pmod{7}$，得 $t_3 = 1$；
- $x \equiv 2 \cdot 35 \cdot 2 + 3 \cdot 21 \cdot 1 + 2 \cdot 15 \cdot 1 = 140 + 63 + 30 = 233 \equiv 23 \pmod{105}$。

验证：$23 = 3\times7+2$，$23=5\times4+3$，$23=7\times3+2$，完全符合。

### 互质条件不满足时的处理

当模数不两两互质时，方程组不一定有解。以 $x \equiv 1 \pmod{4}$ 与 $x \equiv 3 \pmod{6}$ 为例：由第一式 $x=4k+1$（奇数），由第二式 $x=6j+3$（奇数但模4余3），矛盾，故无解。一般判定准则为：$x \equiv a_1 \pmod{m_1}$ 与 $x \equiv a_2 \pmod{m_2}$ 有公共解当且仅当 $\gcd(m_1,m_2) \mid (a_2-a_1)$，若有解则解模 $\text{lcm}(m_1,m_2)$ 唯一。这一推广允许将任意同余方程组逐对合并，但不再套用上述直接公式。

## 实际应用

**RSA解密加速**：在RSA中，私钥解密需计算 $m = c^d \bmod n$，其中 $n=pq$。利用CRT，可先分别计算 $m_p = c^{d_p} \bmod p$ 和 $m_q = c^{d_q} \bmod q$（其中 $d_p = d \bmod (p-1)$，$d_q = d \bmod (q-1)$），再用CRT合并。由于操作在 $p$ 和 $q$（约为 $n$ 的一半长度）上进行，计算量约为直接计算的 **1/4**，这是RSA实现中的标准优化手段。

**大整数并行运算**：选取多个两两互质的模数（如 $m_1=2^{16}+1, m_2=2^{17}+1, \ldots$），将大整数映射到各模下的小余数，在各模下独立运算后再用CRT重构结果，这是"残数系统"（Residue Number System, RNS）的工作原理，广泛用于数字信号处理芯片的并行乘法。

**竞赛问题**：在整除与周期问题中，CRT常用于判断同时满足多个周期条件的最小正整数。如求最小正整数同时满足被7除余1、被11除余2、被13除余3，可直接套用公式，$M=1001$，解为 $x \equiv ?\pmod{1001}$（竞赛中常见题型）。

## 常见误区

**误区一：认为CRT对任意模数均成立**。许多初学者省略"两两互质"的验证步骤，直接套用公式 $x = \sum a_i M_i t_i$。实际上，若 $\gcd(m_i, m_j) > 1$，$M_i$ 在模 $m_i$ 下的逆元不再有意义（因为 $\gcd(M_i, m_i)$ 可能不为1），公式完全失效，得出的"解"根本不满足方程组。

**误区二：将解域写错**。CRT保证解在 $[0, M)$ 中唯一，但许多人将解误写为 $[0, m_i)$ 中的某个值。正确表述是：解在模 $M=m_1m_2\cdots m_k$ 意义下唯一，而非模某个单独的 $m_i$。在"物不知数"例题中，答案是模105唯一，即 $\{23, 128, 233, \ldots\}$ 均为整数解，但最小正整数解是23。

**误区三：混淆 $t_i$ 的求法**。逆元 $t_i$ 满足 $M_i t_i \equiv 1 \pmod{m_i}$，而非 $m_i t_i \equiv 1 \pmod{M_i}$。这两个方程完全不同：前者是在模 $m_i$ 下求 $M_i$ 的逆，后者方向相反且在 $m_i$ 与 $M_i$ 互质时才有意义，混淆后将得出错误的 $t_i$，导致最终解不满足某些分方程。

## 知识关联

**前置概念**：CRT的每一步都依赖同余理论的基础结论——特别是模逆元的存在条件（$\gcd(a,m)=1$ 时 $a$ 在模 $m$ 下存在逆元）以及扩展欧几里得算法（用于实际计算 $t_i$）。若不熟悉贝祖等式 $aM_i + bm_i = 1$ 的解法，则无法完成逆元计算步骤。此外，理解整除性和最大公约数的性质是判断方程组是否有解的必要工具。

**延伸方向**：CRT是抽象代数中环同构定理的具体实例——当 $m_1,\ldots,m_k$ 两两互质时，有环同构 $\mathbb{Z}/M\mathbb{Z} \cong \mathbb{Z}/m_1\mathbb{Z} \times \cdots \times \mathbb{Z}/m_k\mathbb{Z}$，这是数论与代数结构相互渗透的典型范例。在多项式环中也有类似的"多项式中国剩余定理"，用于快速插值算法（如快速傅里叶变换的某些变体）。
