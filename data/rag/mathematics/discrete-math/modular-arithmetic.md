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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 模运算

## 概述

模运算（Modular Arithmetic）是整数运算的一种，定义为：整数 $a$ 除以正整数 $m$ 所得的余数，记作 $a \bmod m$。形式化定义为：$a \bmod m = a - m\lfloor a/m \rfloor$，其中 $\lfloor \cdot \rfloor$ 表示向下取整。例如 $17 \bmod 5 = 2$，$-7 \bmod 3 = 2$（注意负数取模结果为非负数）。

模运算的历史可追溯至中国古代的"同余"概念，《孙子算经》（约公元3世纪）中的"物不知数"问题（中国剩余定理）正是模运算的经典应用。18世纪末，高斯在《算术研究》（Disquisitiones Arithmeticae，1801年）中系统化引入同余符号 $a \equiv b \pmod{m}$，将模运算建立在严谨的数论框架之上。

模运算在现代计算机科学中无处不在：哈希表的桶编号用 $h(k) \bmod N$ 计算，RSA加密的核心是在模 $n = pq$ 下的幂运算，循环队列的下标更新用 $(i+1) \bmod N$ 实现。掌握模运算是进入密码学、组合数学和算法设计的必要前提。

---

## 核心原理

### 同余关系

若 $m \mid (a - b)$（即 $m$ 整除 $a-b$），则称 $a$ 与 $b$ 模 $m$ 同余，记作 $a \equiv b \pmod{m}$。同余关系是一种**等价关系**，满足：
- **自反性**：$a \equiv a \pmod{m}$
- **对称性**：$a \equiv b \Rightarrow b \equiv a \pmod{m}$
- **传递性**：$a \equiv b, b \equiv c \Rightarrow a \equiv c \pmod{m}$

模 $m$ 将整数集合 $\mathbb{Z}$ 划分为 $m$ 个**剩余类**（余数分别为 $0, 1, \ldots, m-1$），这 $m$ 个剩余类构成集合 $\mathbb{Z}/m\mathbb{Z}$（也写作 $\mathbb{Z}_m$）。

### 模加法与模乘法

模运算对加法和乘法均封闭，且以下性质成立：

$$
(a + b) \bmod m = ((a \bmod m) + (b \bmod m)) \bmod m
$$

$$
(a \times b) \bmod m = ((a \bmod m) \times (b \bmod m)) \bmod m
$$

利用这一性质，计算 $2^{100} \bmod 13$ 时无需算出天文数字，只需逐步取模：$2^1=2, 2^2=4, 2^3=8, 2^6=64\equiv 12\equiv -1, 2^{12}\equiv 1 \pmod{13}$，因此 $2^{100}=2^{12\times8+4}\equiv 1^8\times 16\equiv 3 \pmod{13}$。这一技巧称为**快速幂取模**，时间复杂度为 $O(\log k)$（$k$ 为指数）。

**模加法逆元**：在 $\mathbb{Z}_m$ 中，$a$ 的加法逆元为 $m - a$，始终存在。**模乘法逆元**：$a$ 模 $m$ 的乘法逆元 $a^{-1}$ 满足 $a \cdot a^{-1} \equiv 1 \pmod{m}$，其存在当且仅当 $\gcd(a, m) = 1$，可用扩展欧几里得算法求出。

### 欧拉函数与欧拉定理

欧拉函数 $\varphi(n)$ 定义为 $1$ 到 $n$ 中与 $n$ 互质的正整数个数。对 $n$ 做质因数分解 $n = p_1^{k_1} p_2^{k_2} \cdots p_r^{k_r}$，则：

$$
\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)
$$

例如 $\varphi(12) = 12 \times (1 - \frac{1}{2}) \times (1 - \frac{1}{3}) = 4$（对应 $1, 5, 7, 11$）。

**欧拉定理**：若 $\gcd(a, m) = 1$，则：

$$
a^{\varphi(m)} \equiv 1 \pmod{m}
$$

当 $m = p$（素数）时，$\varphi(p) = p - 1$，欧拉定理退化为**费马小定理**：$a^{p-1} \equiv 1 \pmod{p}$。这两个定理是RSA算法正确性证明的数学基石。

### 模运算的整除判别

模运算可以简洁表达整除性：$3 \mid n$ 当且仅当 $n$ 的各位数字之和满足 $S(n) \equiv 0 \pmod{3}$（因为 $10 \equiv 1 \pmod{3}$）；$9 \mid n$ 同理；$11 \mid n$ 当且仅当奇偶位数字交错和 $\equiv 0 \pmod{11}$（因为 $10 \equiv -1 \pmod{11}$）。

---

## 实际应用

**哈希表设计**：哈希函数 $h(k) = k \bmod m$ 将任意整数键映射到 $[0, m-1]$，通常选 $m$ 为素数以减少冲突。若 $m = 2^k$，则 $k \bmod m$ 等价于取最低 $k$ 位二进制，CPU 可用位与操作 `k & (m-1)` 加速计算。

**RSA加密**：选两个大素数 $p, q$，令 $n = pq$，公钥指数 $e$ 满足 $\gcd(e, \varphi(n)) = 1$，私钥 $d = e^{-1} \bmod \varphi(n)$。加密：$c = m^e \bmod n$；解密：$m = c^d \bmod n$。正确性依赖欧拉定理保证 $m^{ed} \equiv m \pmod{n}$。

**日期星期计算**：基姆拉尔森公式通过模7运算直接计算任意日期是星期几，核心是 $w = (d + \lfloor 2.6m - 0.2 \rfloor + y + \lfloor y/4 \rfloor + \lfloor c/4 \rfloor - 2c) \bmod 7$，利用了 $7$ 天周期的模7同余结构。

**循环缓冲区**：嵌入式系统中的环形队列，读写指针更新均为 $(ptr + 1) \bmod N$，模 $N$ 运算天然实现了指针的循环回绕，无需条件分支判断。

---

## 常见误区

**误区一：负数取模结果可以为负**。数学定义要求 $a \bmod m \in \{0, 1, \ldots, m-1\}$，结果始终非负。但C/C++/Java中 `-7 % 3 = -1`（截断取模），而Python中 `-7 % 3 = 2`（地板除取模）。在算法竞赛和密码学中使用C++时，负数结果需手动加上 $m$：`((a % m) + m) % m`。

**误区二：模乘逆元总是存在**。$a$ 模 $m$ 的乘法逆元存在**当且仅当** $\gcd(a, m) = 1$。例如 $2$ 在模 $4$ 意义下没有乘法逆元（因为 $\gcd(2,4)=2\neq 1$），$\mathbb{Z}_4$ 中不存在 $x$ 使 $2x \equiv 1 \pmod 4$。这也是 RSA 要求 $n$ 为两个不同素数之积的原因——确保 $\gcd(e, \varphi(n))=1$ 从而逆元存在。

**误区三：欧拉定理要求 $m$ 为素数**。费马小定理要求 $m$ 为素数，但欧拉定理对任意正整数 $m$（只需 $\gcd(a,m)=1$）均成立。混淆两者会导致在合数模下错误地套用 $a^{m-1}\equiv 1$ 的公式，例如 $2^{11} = 2048 \equiv 8 \not\equiv 1 \pmod{12}$，因为 $12$ 不是素数，正确做法是用 $\varphi(12)=4$，验证 $\gcd(5,12)=1$ 时 $5^4=625\equiv 1\pmod{12}$。

---

## 知识关联

**依赖的前置知识**：模运算的整除判别直接建立在**整除与因数分解**的基础上——判断 $m \mid (a-b)$ 需要理解整除的定义；乘法逆元的求解依赖**最大公因数**的扩展欧几里得算法，算法输出满足 $ax + my = \gcd(a,m)$ 的整数对 $(x, y)$，当 $\gcd(a,m)=1$ 时 $x$ 即为逆元。

**通向后续主题**：$\mathbb{Z}_m$ 在模加法和模乘法下构成代数结构，是**群论初步**的最直观例子——$(\mathbb{Z}_m, +)$ 是一个 $m$ 阶循环群，而 $(\mathbb{Z}_m^*, \times)$（由与 