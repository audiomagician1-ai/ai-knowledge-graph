---
id: "modular-arithmetic"
concept: "模运算"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 5
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 34.1
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.367
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 模运算

## 概述

模运算（Modular Arithmetic）是研究整数在除以某个固定正整数后所得余数的运算体系。对于整数 $a$ 和正整数 $n$，$a \mod n$ 定义为 $a$ 除以 $n$ 的余数，记作 $r$，满足 $a = qn + r$，其中 $0 \leq r < n$，$q$ 为整数商。例如 $17 \mod 5 = 2$，因为 $17 = 3 \times 5 + 2$。

模运算的正式数学框架由高斯（Carl Friedrich Gauss）在1801年的著作《算术研究》（*Disquisitiones Arithmeticae*）中系统建立。高斯引入了同余符号 $a \equiv b \pmod{n}$，意指 $n \mid (a - b)$，即 $n$ 整除 $a - b$。这套符号使得数论研究从繁琐的余数计算中解放出来，转变为优雅的等价关系处理。

模运算在现代密码学、计算机科学和组合数学中具有不可替代的地位。RSA加密算法的核心操作是在模 $n = p \times q$（$p$、$q$ 为大素数）下的幂运算；哈希表的地址计算通常使用 $\text{key} \mod m$；计算机内32位整数的溢出行为本质上就是模 $2^{32}$ 的运算。

---

## 核心原理

### 同余关系的性质

同余 $a \equiv b \pmod{n}$ 是整数集上的一种等价关系，满足自反性（$a \equiv a$）、对称性和传递性。更重要的是，同余关系与加减乘运算兼容：

- 若 $a \equiv b \pmod{n}$ 且 $c \equiv d \pmod{n}$，则：
  - $a + c \equiv b + d \pmod{n}$
  - $a - c \equiv b - d \pmod{n}$
  - $a \times c \equiv b \times d \pmod{n}$

上述性质使得在进行大数运算时，可以在每一步之后取模，而不必等到最终结果再取模，极大降低计算复杂度。例如，计算 $7^{100} \mod 13$ 时，利用快速幂（反复平方）配合逐步取模，只需约 $\log_2 100 \approx 7$ 次乘法。

**注意**：同余与除法的兼容性受限制。由 $ac \equiv bc \pmod{n}$ 不能直接得出 $a \equiv b \pmod{n}$，只能得出 $a \equiv b \pmod{n / \gcd(c, n)}$。

### 模加法与模乘法的代数结构

整数模 $n$ 的余数类集合记为 $\mathbb{Z}_n = \{0, 1, 2, \ldots, n-1\}$。

**模加法**：$\mathbb{Z}_n$ 在加法下构成循环群，单位元为 $0$，每个元素 $a$ 的逆元为 $n - a$（当 $a \neq 0$ 时）。例如在 $\mathbb{Z}_7$ 中，$3$ 的加法逆元为 $4$，因为 $3 + 4 \equiv 0 \pmod{7}$。

**模乘法**：$\mathbb{Z}_n$ 在乘法下不总是构成群，因为并非所有元素都有乘法逆元。元素 $a$ 在模 $n$ 下有乘法逆元，当且仅当 $\gcd(a, n) = 1$。所有与 $n$ 互质的余数类组成集合 $\mathbb{Z}_n^*$，该集合在乘法下构成群，其阶（元素个数）恰好等于欧拉函数 $\varphi(n)$。

### 欧拉函数与欧拉定理

**欧拉函数** $\varphi(n)$ 定义为 $1$ 到 $n$ 中与 $n$ 互质的正整数个数。其计算公式为：

$$\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)$$

其中乘积遍历 $n$ 的所有不同素因子 $p$。具体地：
- $\varphi(1) = 1$
- $\varphi(p) = p - 1$（$p$ 为素数）
- $\varphi(p^k) = p^{k-1}(p-1)$
- $\varphi(12) = \varphi(4) \times \varphi(3) = 2 \times 2 = 4$，对应 $\{1, 5, 7, 11\}$ 四个与12互质的数

**欧拉定理**：若 $\gcd(a, n) = 1$，则 $a^{\varphi(n)} \equiv 1 \pmod{n}$。

**费马小定理**是欧拉定理在 $n = p$（素数）时的特例：$a^{p-1} \equiv 1 \pmod{p}$（$p \nmid a$）。利用费马小定理，$a$ 在模素数 $p$ 下的乘法逆元为 $a^{p-2} \mod p$，避免了辗转相除法的繁琐。

### 中国剩余定理

当模数两两互质时，联立同余方程组有唯一解。具体地，设 $n_1, n_2, \ldots, n_k$ 两两互质，则方程组：

$$x \equiv a_i \pmod{n_i}, \quad i = 1, 2, \ldots, k$$

在模 $N = n_1 n_2 \cdots n_k$ 意义下有唯一解。解的构造使用 $N_i = N / n_i$ 及其模 $n_i$ 的逆元 $M_i$（满足 $N_i M_i \equiv 1 \pmod{n_i}$），得 $x \equiv \sum_{i=1}^k a_i N_i M_i \pmod{N}$。

---

## 实际应用

**RSA密码算法**：选取两个大素数 $p = 61$、$q = 53$（简化示例），令 $n = pq = 3233$，$\varphi(n) = 60 \times 52 = 3120$。选公钥指数 $e = 17$（与3120互质），用扩展欧几里得算法求私钥 $d$ 满足 $17d \equiv 1 \pmod{3120}$，得 $d = 2753$。加密时计算 $c = m^{17} \mod 3233$，解密时计算 $m = c^{2753} \mod 3233$，正确性依赖欧拉定理 $m^{\varphi(n)} \equiv 1 \pmod{n}$。

**循环冗余校验（CRC）**：数据帧的校验码通过将数据多项式对生成多项式取模得到，本质是 $\mathbb{Z}_2[x]$ 上的多项式模运算，与整数模运算同构。

**约瑟夫问题**：$n$ 人围坐成圈，每隔 $k$ 人淘汰一人，最终存活位置的递推公式 $J(n, k) = (J(n-1, k) + k) \mod n$ 中，模运算保证了圆圈的"环绕"性质，使线性的下标递推等价于循环选取。

**日历计算**：蔡勒公式（Zeller's Formula）利用模7计算任意日期的星期几，例如 2000年1月1日为星期六，可验证 $h = (1 + \lfloor 13 \times 14/5 \rfloor + 0 + 0 + 0 - 2) \mod 7 = 6$。

---

## 常见误区

**误区一：模运算对负数的处理与编程语言一致**

数学定义要求余数 $r$ 满足 $0 \leq r < n$，因此 $-7 \mod 3 = 2$（因为 $-7 = (-3) \times 3 + 2$）。但C/C++、Java中 `-7 % 3` 的结果为 `-1`（向零取整的余数）。在密码学和数论编程中若不注意此差异，会导致错误结果。Python的 `%` 运算符遵从数学定义，`-7 % 3` 返回 `2`。

**误区二：同余关系两边可以任意"除"**

由 $6 \equiv 2 \pmod{4}$ 两边除以2，得 $3 \equiv 1 \pmod{4}$，但 $3 \not\equiv 1 \pmod{4}$，这是错误的！正确结论是 $3 \equiv 1 \pmod{4/\gcd(2,4)} = \pmod{2}$，即 $3 \equiv 1 \pmod{2}$，这才成立。只有当除数与模数互质时，消去才是安全的。

**误区三：欧拉定理适用于所有整数**

$a^{\varphi(n)} \equiv 1 \pmod{n}$ 的前提是 $\gcd(a, n) = 1$。若 $\gcd(a, n) > 1$，结论不成立。例如 $\gcd(4, 6) = 2 \neq 1$，而 $4^{\varphi(6)} = 4^2 = 16 \equiv 4 \pmod{6} \neq 1$。在使用费马小定理求逆元时，必须先确认 $p \nmid a$。

---

## 知识关联

**与前置概念的衔接**：模运算依赖**整除与因数分解**的基础——$a \mod n$ 的定义直接来源于带余除法；欧拉函数 $\varp
