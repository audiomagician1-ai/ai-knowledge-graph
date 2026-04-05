---
id: "arithmetic-functions"
concept: "算术函数"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 算术函数

## 概述

算术函数（Arithmetic Function）是定义在正整数集合上、取值为复数的函数，即 $f: \mathbb{Z}^+ \to \mathbb{C}$。它们是研究正整数乘法结构的核心工具，与素数分布、因子性质密切相关。常见的算术函数包括欧拉函数 $\varphi(n)$、Möbius函数 $\mu(n)$、因子和函数 $\sigma(n)$ 以及因子个数函数 $\tau(n)$，每一个都编码了正整数不同维度的乘法信息。

算术函数的系统研究可追溯至18世纪，欧拉在1763年前后引入了 $\varphi(n)$ 来描述模 $n$ 的既约剩余系。Möbius函数由奥古斯特·费迪南德·Möbius于1832年引入，其反演公式成为解析数论的基本工具之一。19世纪末，狄利克雷级数 $\sum_{n=1}^{\infty} f(n)/n^s$ 将算术函数与复分析联系起来，使黎曼猜想等深层问题得以表述。

算术函数之所以重要，在于它们揭示了正整数的"乘法骨架"。通过积性（multiplicativity）概念，复杂的求和问题可以分解为素数幂处的局部计算，大幅简化数论分析。Möbius反演公式更是提供了一种系统地"去除"因子和条件的逆变换机制，在组合数论和解析数论中频繁出现。

## 核心原理

### 积性函数与完全积性函数

若函数 $f$ 满足：对所有互素正整数 $m, n$（即 $\gcd(m,n)=1$），有 $f(mn) = f(m)f(n)$，则称 $f$ 为**积性函数**。若对所有正整数 $m, n$ 均满足此等式（无需互素条件），则称为**完全积性函数**。

积性函数由其在素数幂 $p^k$ 处的值完全决定。若 $n = p_1^{a_1} p_2^{a_2} \cdots p_r^{a_r}$，则 $f(n) = f(p_1^{a_1}) \cdot f(p_2^{a_2}) \cdots f(p_r^{a_r})$。欧拉函数 $\varphi$、Möbius函数 $\mu$、因子和 $\sigma_k$、因子个数 $\tau$ 均为积性函数；而恒等函数 $\text{id}(n) = n$ 和常数函数 $\mathbf{1}(n) = 1$ 是完全积性函数。

### 四个经典算术函数

**欧拉函数** $\varphi(n)$ 定义为 $1$ 到 $n$ 中与 $n$ 互素的整数个数。其计算公式为：
$$\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)$$
例如 $\varphi(12) = 12 \cdot \frac{1}{2} \cdot \frac{2}{3} = 4$，对应 $\{1, 5, 7, 11\}$。在素数幂处，$\varphi(p^k) = p^k - p^{k-1}$。

**Möbius函数** $\mu(n)$ 定义为：
$$\mu(n) = \begin{cases} 1 & \text{若 } n = 1 \\ (-1)^k & \text{若 } n \text{ 是 } k \text{ 个不同素数之积} \\ 0 & \text{若 } n \text{ 有平方因子} \end{cases}$$
例如 $\mu(6) = \mu(2 \cdot 3) = (-1)^2 = 1$，$\mu(4) = 0$，$\mu(30) = \mu(2 \cdot 3 \cdot 5) = -1$。关键性质：$\sum_{d \mid n} \mu(d) = [n=1]$，即仅当 $n=1$ 时等于1，否则为0。

**因子和函数** $\sigma_k(n) = \sum_{d \mid n} d^k$，常用的是 $\sigma_1(n)$（因子之和）和 $\sigma_0(n) = \tau(n)$（因子个数）。对素数幂：$\sigma_1(p^a) = \frac{p^{a+1}-1}{p-1}$。完全数满足 $\sigma_1(n) = 2n$，最小完全数是 $6$，因为 $\sigma_1(6) = 1+2+3+6 = 12 = 2 \times 6$。

### Möbius反演公式

若两个算术函数 $f$ 与 $g$ 满足：
$$g(n) = \sum_{d \mid n} f(d)$$
则有**Möbius反演公式**：
$$f(n) = \sum_{d \mid n} \mu(d) \cdot g\!\left(\frac{n}{d}\right)$$

这等价于在狄利克雷卷积意义下，$f = \mu * g$，即 $\mu$ 是常数函数 $\mathbf{1}$ 的狄利克雷逆元。应用示例：由 $n = \sum_{d \mid n} \varphi(d)$ 反演得 $\varphi(n) = \sum_{d \mid n} \mu(d) \cdot \frac{n}{d}$，这是欧拉函数的另一表达形式。

### 狄利克雷卷积

两个算术函数 $f$ 与 $g$ 的**狄利克雷卷积**定义为：
$$(f * g)(n) = \sum_{d \mid n} f(d) \cdot g\!\left(\frac{n}{d}\right)$$

狄利克雷卷积构成交换环，满足结合律和交换律。乘法单位元是 $\varepsilon(n) = [n=1]$（即 $n=1$ 时为1，否则为0）。积性函数在狄利克雷卷积下封闭——两个积性函数的卷积仍是积性函数，这保证了 $\sigma_k = \mathbf{1} * \text{id}_k$、$\tau = \mathbf{1} * \mathbf{1}$ 等分解的有效性。

## 实际应用

**密码学中的欧拉函数**：RSA算法的正确性依赖欧拉定理 $a^{\varphi(n)} \equiv 1 \pmod{n}$（$\gcd(a,n)=1$）。选取 $n=pq$（两个大素数之积），则 $\varphi(n) = (p-1)(q-1)$，公钥指数 $e$ 与私钥指数 $d$ 满足 $ed \equiv 1 \pmod{\varphi(n)}$。

**计数问题中的Möbius反演**：设 $f(n)$ 为长度为 $n$、最小周期恰好为 $n$ 的二元项链数，$g(n) = 2^n$ 为长度为 $n$ 的所有项链数。由 $g(n) = \sum_{d \mid n} f(d)$，反演得 $f(n) = \sum_{d \mid n} \mu(d) \cdot 2^{n/d}$。例如 $f(6) = \mu(1) \cdot 64 + \mu(2) \cdot 8 + \mu(3) \cdot 4 + \mu(6) \cdot 2 = 64 - 8 - 4 + 2 = 54$。

**素数计数的筛法**：Möbius函数是埃拉托色尼筛法的代数抽象。线性筛算法利用积性函数在素数幂处的递推关系，在 $O(n)$ 时间内同时计算 $\varphi(n)$、$\mu(n)$、$\tau(n)$ 等多个算术函数的前 $n$ 项值。

## 常见误区

**误区1：认为所有算术函数都是积性的。** Ω函数（计重复素因子个数，$\Omega(12)=3$）满足 $\Omega(mn) = \Omega(m) + \Omega(n)$，是完全加性函数而非积性函数。$f(n) = n+1$ 连加性都不满足：$f(2) \cdot f(3) = 3 \times 4 = 12 \neq f(6) = 7$。积性的充要条件是 $f(1)=1$（非零函数）且对互素对满足乘法性，缺一不可。

**误区2：Möbius反演只能用于整除偏序。** 经典形式是对因子格的反演，但Möbius函数可推广到任意局部有限偏序集（Rota 1964年的工作）。在子集格上，广义Möbius函数给出容斥原理；在整除格上，才是本文所述的数论Möbius函数。二者形式相同，但定义域不同，不能混淆。

**误区3：$\varphi(mn) = \varphi(m)\varphi(n)$ 无条件成立。** 这只在 $\gcd(m,n)=1$ 时成立。一般情况下，$\varphi(mn) = \varphi(m)\varphi(n) \cdot \frac{d}{\varphi(d)}$，其中 $d = \gcd(m,n)$。例如 $\varphi(4) = 2$，$\varphi(2) = 1$，但 $\varphi(4) \neq \varphi(2)^2 = 1$，因为 $\gcd(2,2) = 2 \neq 1$。

## 知识关联

**与欧拉定理的关联