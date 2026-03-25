---
id: "quadratic-residues"
concept: "二次剩余"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 二次剩余

## 概述

二次剩余是数论中的核心概念，研究整数 $a$ 在模奇素数 $p$ 意义下是否能表示为某个整数的平方。具体地，设 $p$ 是奇素数，$a$ 是不被 $p$ 整除的整数，若存在整数 $x$ 使得 $x^2 \equiv a \pmod{p}$，则称 $a$ 是模 $p$ 的**二次剩余**；否则称 $a$ 为**二次非剩余**。

二次剩余的系统研究始于欧拉，他在18世纪中叶首先观察到"二次互反律"的模式，但未能给出完整证明。高斯（Carl Friedrich Gauss）于1796年，年仅19岁时，给出了二次互反律的第一个严格证明，并在其1801年出版的《算术研究》（*Disquisitiones Arithmeticae*）中收录了多达8种不同的证明。高斯将二次互反律称为"数论中的宝石"（*theorema aureum*），足见其重要性。

二次剩余理论直接决定了整数能否分解为两个平方数之和等经典问题的答案，并在现代密码学（如Rabin密码体制）与伪随机数生成中有重要应用。

## 核心原理

### Legendre 符号的定义与计算

Legendre 符号 $\left(\frac{a}{p}\right)$ 由法国数学家阿德里安-马里·勒让德于1798年引入，其定义如下：

$$\left(\frac{a}{p}\right) = \begin{cases} 0 & \text{若 } p \mid a \\ 1 & \text{若 } a \text{ 是模 } p \text{ 的二次剩余} \\ -1 & \text{若 } a \text{ 是模 } p \text{ 的二次非剩余} \end{cases}$$

其中 $p$ 为奇素数。计算 Legendre 符号最重要的工具是**欧拉判别准则**：

$$\left(\frac{a}{p}\right) \equiv a^{\frac{p-1}{2}} \pmod{p}$$

这意味着对奇素数 $p = 7$，验证 $a = 2$：$2^3 = 8 \equiv 1 \pmod{7}$，故 $\left(\frac{2}{7}\right) = 1$，即 $2$ 是模 $7$ 的二次剩余（验证：$3^2 = 9 \equiv 2 \pmod 7$）。

Legendre 符号满足完全积性：$\left(\frac{ab}{p}\right) = \left(\frac{a}{p}\right)\left(\frac{b}{p}\right)$，且模奇素数 $p$ 恰好有 $\frac{p-1}{2}$ 个二次剩余和 $\frac{p-1}{2}$ 个二次非剩余（均在模 $p$ 的缩剩余系中统计）。

### 二次互反律

二次互反律是关于两个不同奇素数 $p, q$ 之间 Legendre 符号关系的深刻定理：

$$\left(\frac{p}{q}\right)\left(\frac{q}{p}\right) = (-1)^{\frac{p-1}{2} \cdot \frac{q-1}{2}}$$

右端的指数 $\frac{p-1}{2} \cdot \frac{q-1}{2}$ 为奇数当且仅当 $p \equiv q \equiv 3 \pmod{4}$。换言之：
- 若 $p$ 与 $q$ 中至少有一个模 $4$ 余 $1$，则 $\left(\frac{p}{q}\right) = \left(\frac{q}{p}\right)$；
- 若 $p \equiv q \equiv 3 \pmod{4}$，则 $\left(\frac{p}{q}\right) = -\left(\frac{q}{p}\right)$。

**示例**：计算 $\left(\frac{71}{73}\right)$。由于 $71 \equiv 3 \pmod{4}$，$73 \equiv 1 \pmod{4}$，故 $\left(\frac{71}{73}\right) = \left(\frac{73}{71}\right) = \left(\frac{2}{71}\right)$。再利用 $-1$ 和 $2$ 的特殊公式：$\left(\frac{2}{p}\right) = (-1)^{\frac{p^2-1}{8}}$，代入 $p=71$：$\frac{71^2-1}{8} = \frac{5040}{8} = 630$，为偶数，故 $\left(\frac{2}{71}\right) = 1$，即 $71$ 是模 $73$ 的二次剩余。

### $-1$ 与 $2$ 的二次剩余判别

两个特殊的补充公式完善了二次互反律的应用：

$$\left(\frac{-1}{p}\right) = (-1)^{\frac{p-1}{2}} = \begin{cases} 1 & p \equiv 1 \pmod{4} \\ -1 & p \equiv 3 \pmod{4} \end{cases}$$

$$\left(\frac{2}{p}\right) = (-1)^{\frac{p^2-1}{8}} = \begin{cases} 1 & p \equiv \pm 1 \pmod{8} \\ -1 & p \equiv \pm 3 \pmod{8} \end{cases}$$

这两个公式的证明路径完全不同：前者直接由欧拉判别准则得到，后者的证明需要用到高斯引理（Gauss's Lemma），统计特定集合中大于 $\frac{p}{2}$ 的元素个数 $\mu$，结论为 $\left(\frac{a}{p}\right) = (-1)^\mu$。

## 实际应用

**判断方程是否有解**：判断 $x^2 \equiv 219 \pmod{383}$ 是否有解，其中 $383$ 是素数。将 $219 = 3 \times 73$ 分解，利用 Legendre 符号积性及二次互反律逐步化简，最终得到 $\left(\frac{219}{383}\right) = 1$，说明方程有解。

**两平方和表示**：费马定理指出奇素数 $p$ 可以表示为两个整数平方之和 $p = a^2 + b^2$ 当且仅当 $p \equiv 1 \pmod{4}$，本质等价于 $-1$ 是模 $p$ 的二次剩余，即 $\left(\frac{-1}{p}\right) = 1$。

**Rabin 密码体制**：其安全性基于计算模合数 $n = pq$ 的平方根与大数分解等价这一事实，而模素数的平方根存在性恰由二次剩余理论保证，求解时使用 Tonelli–Shanks 算法在 $O(\log^2 p)$ 次运算内完成。

## 常见误区

**误区一：将 Legendre 符号与 Jacobi 符号混淆**。Jacobi 符号 $\left(\frac{a}{n}\right)$ 是 Legendre 符号对奇合数 $n$ 的推广，但 Jacobi 符号等于 $1$ 并不意味着 $a$ 是模 $n$ 的二次剩余。例如 $\left(\frac{2}{15}\right) = \left(\frac{2}{3}\right)\left(\frac{2}{5}\right) = (-1)(−1) = 1$，但 $x^2 \equiv 2 \pmod{15}$ 无整数解。Jacobi 符号仅在模为素数时才与二次剩余的存在性等价。

**误区二：认为二次互反律对合数模也成立**。二次互反律的标准形式严格要求 $p, q$ 均为奇素数且 $p \neq q$。将其直接推广到合数模会得出错误结论，正确的推广工具是 Jacobi 符号的互反律，其形式相同但含义已弱化。

**误区三：误以为二次剩余计数公式 $\frac{p-1}{2}$ 对合数模成立**。模合数 $n$ 的二次剩余个数由 $n$ 的素因子结构决定，例如模 $2^k$（$k \geq 3$）的二次剩余个数为 $2^{k-3}$，与模奇素数的情形截然不同。

## 知识关联

**前置基础**：二次剩余建立在同余理论之上，特别依赖模 $p$ 的缩剩余系结构与原根的存在性——模奇素数 $p$ 存在原根 $g$，二次剩余恰好是 $g$ 的偶数次幂 $\{g^0, g^2, g^4, \ldots, g^{p-3}\}$，共 $\frac{p-1}{2}$ 个元素。此视角将二次剩余的判断化归为离散对数的奇偶性问题。

**向上延伸**：Legendre 符号可推广为 Jacobi 符号（模奇合数）乃至 Kronecker 符号（任意整数模），后者在代数数论中描述二次域 $\mathbb{Q}(\sqrt{d})$ 中素数的分解行为。二次互反律本身是更一般的**高次互反律**的起点，Artin 互反律将其纳入类域论的统一框架，是20世纪数论的重大成就。