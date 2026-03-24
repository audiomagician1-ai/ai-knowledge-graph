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
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 算术函数

## 概述

算术函数（Arithmetic Function）是指定义在正整数集合上的复值函数 $f: \mathbb{Z}^+ \to \mathbb{C}$。与一般实分析中的函数不同，算术函数的自变量仅取正整数，其理论价值在于揭示整数的乘法结构——尤其是素因子分解——如何决定函数的取值模式。算术函数的系统研究可追溯至高斯（1801年《算术研究》）和狄利克雷（1837年引入狄利克雷级数工具），Möbius本人在1832年发表的论文中引入了以其命名的函数及反演公式。

算术函数中最重要的一类称为**积性函数**（multiplicative function）：若对所有互素的正整数 $m, n$（即 $\gcd(m,n)=1$），均有 $f(mn) = f(m)f(n)$，则称 $f$ 为积性函数。若该等式对所有正整数 $m, n$（不要求互素）成立，则称为完全积性函数。积性这一性质使得对任意正整数 $n = p_1^{a_1} p_2^{a_2} \cdots p_k^{a_k}$ 的计算可分解为对各素数幂次的独立计算，极大简化了数论分析。

---

## 核心原理

### 欧拉函数 φ(n)

欧拉函数 $\varphi(n)$ 定义为 $1$ 到 $n$ 中与 $n$ 互素的正整数个数。对 $n = p_1^{a_1} \cdots p_k^{a_k}$，有公式：

$$\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)$$

例如 $\varphi(12) = 12 \cdot (1 - \frac{1}{2})(1 - \frac{1}{3}) = 4$，对应 $\{1, 5, 7, 11\}$ 这四个数。$\varphi(n)$ 是积性函数但非完全积性（$\varphi(4) = 2 \neq \varphi(2)^2 = 1$）。欧拉函数与欧拉定理直接衔接：若 $\gcd(a,n)=1$，则 $a^{\varphi(n)} \equiv 1 \pmod{n}$，这是RSA加密算法的数学基础。

### Möbius函数 μ(n)

Möbius函数 $\mu(n)$ 的定义如下：

$$\mu(n) = \begin{cases} 1 & \text{若 } n = 1 \\ (-1)^k & \text{若 } n \text{ 是 } k \text{ 个不同素数之积} \\ 0 & \text{若 } n \text{ 含平方因子} \end{cases}$$

例如 $\mu(1)=1$，$\mu(6)=\mu(2\cdot3)=1$，$\mu(30)=\mu(2\cdot3\cdot5)=-1$，$\mu(4)=0$（因为 $4=2^2$）。$\mu(n)$ 的关键性质是：

$$\sum_{d \mid n} \mu(d) = [n=1] = \varepsilon(n)$$

即该和式在 $n=1$ 时等于 $1$，在 $n>1$ 时等于 $0$。这一性质是Möbius反演成立的代数根源，$\mu$ 也是狄利克雷卷积意义下恒等函数 $\mathbf{1}$ 的逆元。

### 除数函数 σ(n)

除数函数 $\sigma_k(n)$ 定义为 $n$ 的所有正因子的 $k$ 次幂之和：

$$\sigma_k(n) = \sum_{d \mid n} d^k$$

最常用的两个特例是 $\sigma_0(n)$（因子个数，常记为 $\tau(n)$ 或 $d(n)$）和 $\sigma_1(n)$（因子之和，常简记为 $\sigma(n)$）。对 $n = 12$，$\sigma_0(12) = 6$（因子为 $1,2,3,4,6,12$），$\sigma_1(12) = 28$。对素数幂 $p^a$，有 $\sigma_1(p^a) = \frac{p^{a+1}-1}{p-1}$。完全数的定义正是 $\sigma_1(n) = 2n$（如 $n=6,28,496$），这是 $\sigma$ 函数最经典的应用场景。

### Möbius反演公式

Möbius反演公式是算术函数理论中最强大的工具。设 $f, g$ 均为算术函数，若：

$$g(n) = \sum_{d \mid n} f(d)$$

则：

$$f(n) = \sum_{d \mid n} \mu(d) \cdot g\!\left(\frac{n}{d}\right)$$

用**狄利克雷卷积**（Dirichlet convolution）语言可以极简地表达：若 $g = f * \mathbf{1}$，则 $f = g * \mu$，因为 $\mathbf{1} * \mu = \varepsilon$（单位元）。一个典型应用：利用 $n = \sum_{d \mid n} \varphi(d)$（恒等式），用Möbius反演即可直接导出 $\varphi(n) = \sum_{d \mid n} \mu(d) \cdot \frac{n}{d} = n \sum_{d \mid n} \frac{\mu(d)}{d}$，无需从头推导欧拉函数公式。

---

## 实际应用

**容斥计数与素数筛法：** $\mu(n)$ 的符号恰好编码了容斥原理中的加减号——$k$ 个不同素数之积对应 $(-1)^k$。Legendre筛法利用 $\mu$ 对不超过 $N$ 的素数计数，其核心估计涉及 $\sum_{n \leq x} \mu(n) = O(\sqrt{x})$（假设黎曼猜想成立则可改进到 $O(x^{1/2+\varepsilon})$）。

**RSA与密码学：** $\varphi(n)$ 在RSA中扮演核心角色。给定 $n = pq$（$p, q$ 为大素数），$\varphi(n) = (p-1)(q-1)$。加密指数 $e$ 与解密指数 $d$ 满足 $ed \equiv 1 \pmod{\varphi(n)}$，即 $d = e^{-1} \bmod \varphi(n)$。

**Möbius反演在组合数学中的应用：** 在格（poset）理论中，Möbius反演被推广为Rota的偏序集Möbius反演（1964年），整除格上的特例即经典数论版本。例如计算"恰好有 $k$ 个不同素因子的整数个数"时可借助反演简化计数。

**狄利克雷级数：** 算术函数 $f$ 对应的狄利克雷级数 $\sum_{n=1}^{\infty} \frac{f(n)}{n^s}$ 将乘法结构转化为解析工具。例如，$\sigma_k(n)$ 对应的狄利克雷级数满足 $\sum \frac{\sigma_k(n)}{n^s} = \zeta(s)\zeta(s-k)$，其中 $\zeta$ 为黎曼zeta函数。

---

## 常见误区

**误区一：积性函数与完全积性函数的混淆。** 许多初学者认为"积性"意味着 $f(mn)=f(m)f(n)$ 对所有 $m,n$ 成立，但标准定义只要求 $\gcd(m,n)=1$。$\varphi(n)$ 和 $\sigma(n)$ 是积性但非完全积性的典型例子。完全积性函数实际上极少：常用的只有 $\mathbf{1}(n)=1$、恒等函数 $\text{id}(n)=n$ 和刘维尔函数 $\lambda(n)=(-1)^{\Omega(n)}$（$\Omega(n)$ 为计重数的素因子个数）。

**误区二：Möbius反演的方向混淆。** 正确方向是：已知"因子求和"得到 $g$，则用 $\mu$ 反演恢复 $f$。若错误地从 $f = g * \mu$ 出发误写为 $g = f * (-\mu)$，或混淆 $\mu(n/d)$ 与 $\mu(d)$ 的位置，将得到错误结论。建议始终用狄利克雷卷积符号 $*$ 验证，因为卷积满足交换律：$f * \mathbf{1} = \mathbf{1} * f$，逆运算是唯一的。

**误区三：认为 $\mu(n)=0$ 的频率极低。** 实际上，无平方因子数（$\mu(n) \neq 0$ 的整数）的密度为 $\frac{6}{\pi^2} \approx 0.608$，即约 $60.8\%$ 的正整数满足 $\mu(n) \neq 0$；反之，约 $39.2\%$ 的正整数含平方因子使得 $\mu(n)=0$。这一密度恰好等于 $\frac{1}{\zeta(2)}$，是 $\mu$ 函数与黎曼zeta函数深层联系的具体体现。

---

## 知识关联

**与欧拉定理的衔接：** $\varphi(n)$ 既是欧拉定理 $a^{\varphi(n)} \equiv 1 \pmod{n}$
