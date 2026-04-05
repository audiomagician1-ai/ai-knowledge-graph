---
id: "fermats-little-theorem"
concept: "费马小定理"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 6
is_milestone: false
tags: ["定理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 费马小定理

## 概述

费马小定理（Fermat's Little Theorem）是数论中关于素数与幂次同余的基本定理：若 $p$ 是素数，且整数 $a$ 满足 $\gcd(a, p) = 1$（即 $p \nmid a$），则 $a^{p-1} \equiv 1 \pmod{p}$。等价地，对任意整数 $a$，均有 $a^p \equiv a \pmod{p}$。这两种表述形式在不同场合各有用途，后者无需要求 $p \nmid a$，适用范围稍广。

该定理由法国数学家皮埃尔·德·费马（Pierre de Fermat）于1640年在写给友人弗雷尼克尔的信中首次陈述，但费马本人并未给出证明。第一个完整的书面证明由莱布尼茨（Leibniz）在其未发表的手稿中给出，欧拉（Euler）于1736年发表了第一个公开证明，并将其推广为后来的欧拉定理。历史上这一定理几乎与费马大定理同名，但两者内容截然不同，"小"字正是为了与费马大定理加以区别。

费马小定理在现代密码学、素性检验和模幂运算中具有直接应用价值。RSA 加密算法的正确性证明就依赖此定理（通过其推广形式欧拉定理）；Miller-Rabin 素性检验算法也以费马小定理的逆否命题为出发点设计。

## 核心原理

### 定理的精确表述与条件

定理核心公式为：

$$a^{p-1} \equiv 1 \pmod{p}, \quad \text{其中 } p \text{ 为素数，} \gcd(a,p)=1$$

条件 $\gcd(a,p)=1$ 不可省略。若 $p \mid a$，则 $a \equiv 0 \pmod{p}$，从而 $a^{p-1} \equiv 0 \not\equiv 1 \pmod{p}$，定理失效。等价形式 $a^p \equiv a \pmod{p}$ 对所有整数 $a$ 成立，是因为当 $p \mid a$ 时两边均为 $0$，当 $p \nmid a$ 时在原式两边同乘 $a$ 即可得到。

### 证明思路：完全剩余系方法

最经典的证明利用模 $p$ 的非零剩余类的乘法封闭性。考虑集合 $S = \{1, 2, 3, \ldots, p-1\}$，共 $p-1$ 个元素。对 $\gcd(a,p)=1$，将 $S$ 中每个元素乘以 $a$，得到集合 $S' = \{a, 2a, 3a, \ldots, (p-1)a\}$。

可以证明 $S'$ 中各元素模 $p$ 后仍是 $1$ 到 $p-1$ 的一个排列：若 $ia \equiv ja \pmod{p}$ 且 $1 \le i,j \le p-1$，由 $\gcd(a,p)=1$ 可消去 $a$ 得 $i \equiv j \pmod{p}$，故 $i=j$。因此：

$$\prod_{k=1}^{p-1}(ka) \equiv \prod_{k=1}^{p-1} k \pmod{p}$$

$$a^{p-1} \cdot (p-1)! \equiv (p-1)! \pmod{p}$$

由于 $\gcd((p-1)!, p) = 1$（$p$ 为素数），两边消去 $(p-1)!$，即得 $a^{p-1} \equiv 1 \pmod{p}$。

### 逆元计算的应用

费马小定理提供了在模素数意义下求乘法逆元的直接公式。若 $p$ 为素数且 $p \nmid a$，则：

$$a^{-1} \equiv a^{p-2} \pmod{p}$$

这是因为 $a \cdot a^{p-2} = a^{p-1} \equiv 1 \pmod{p}$。例如，求 $3^{-1} \pmod{7}$：由费马小定理，$3^{-1} \equiv 3^{5} = 243 \equiv 243 - 34 \times 7 = 243 - 238 = 5 \pmod{7}$，即 $3 \times 5 = 15 \equiv 1 \pmod{7}$，验证正确。

## 实际应用

**快速模幂降幂**：计算 $2^{100} \pmod{101}$ 时，注意 $101$ 为素数，由费马小定理 $2^{100} \equiv 1 \pmod{101}$，无需任何实际乘法运算，直接得出结果为 $1$。若指数不恰好是 $p-1$，则利用 $a^{k(p-1)+r} \equiv a^r \pmod{p}$ 将指数化简。

**费马素性检验**：给定待检验整数 $n$，随机选取 $a$（$1 < a < n$），若 $a^{n-1} \not\equiv 1 \pmod{n}$，则 $n$ 必为合数（费马小定理逆否命题）。例如检验 $n=341$：取 $a=2$，$2^{340} \equiv 1 \pmod{341}$，但 $341 = 11 \times 31$ 实为合数，这类能"骗过"所有 $\gcd(a,n)=1$ 的 $a$ 的合数称为 **Carmichael 数**，最小的 Carmichael 数为 $561 = 3 \times 11 \times 17$。

**组合数模素数计算**：利用 $\binom{p}{k} \equiv 0 \pmod{p}$（$1 \le k \le p-1$，$p$ 为素数）可推导 $(1+x)^p \equiv 1 + x^p \pmod{p}$，这一结论本身是费马小定理的另一等价形式（对 $x=a-1$ 应用）。

## 常见误区

**误区一：将费马小定理的逆命题当作素性判定依据**。$a^{p-1} \equiv 1 \pmod{p}$ 对所有 $\gcd(a,p)=1$ 成立是 $p$ 为素数的**必要条件**，而非充分条件。若仅对单个 $a$ 值验证，极可能被 Carmichael 数欺骗——$561$ 对所有与其互质的 $a$ 均满足 $a^{560} \equiv 1 \pmod{561}$，但 $561$ 不是素数。

**误区二：当底数 $a$ 是 $p$ 的倍数时套用 $a^{p-1} \equiv 1$ 的形式**。例如认为 $7^{6} \equiv 1 \pmod{7}$ 成立，这是错的，因为 $7 \equiv 0 \pmod{7}$，故 $7^6 \equiv 0 \pmod{7}$。正确应使用等价形式 $a^p \equiv a \pmod{p}$，此时 $7^7 \equiv 7 \pmod{7}$ 才是正确表述（两边均为 $0$）。

**误区三：误将费马小定理直接用于合数模**。费马小定理要求模数 $p$ 严格为**素数**。对合数模 $n$，应使用欧拉定理：$a^{\varphi(n)} \equiv 1 \pmod{n}$（在 $\gcd(a,n)=1$ 时）。例如模 $15$ 时，$\varphi(15)=8$，不能随意使用 $14$ 作指数进行化简。

## 知识关联

**前置概念——同余理论**：费马小定理的证明全程依赖同余的基本运算法则，特别是乘法的消去律（即当 $\gcd(c,p)=1$ 时，$ac \equiv bc \pmod{p}$ 可推出 $a \equiv b \pmod{p}$）。理解模 $p$ 剩余类关于乘法构成群（阶为 $p-1$）的结构，是理解证明本质的基础。

**后续概念——欧拉定理**：欧拉将费马小定理推广至任意正整数模：若 $\gcd(a,n)=1$，则 $a^{\varphi(n)} \equiv 1 \pmod{n}$，其中 $\varphi(n)$ 为欧拉函数。当 $n=p$ 为素数时，$\varphi(p)=p-1$，恰好退化为费马小定理。欧拉定理是 RSA 算法解密正确性的直接数学依据，而费马小定理可视为欧拉定理在素数情形下的特例与历史先驱。