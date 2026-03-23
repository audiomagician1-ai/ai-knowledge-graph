---
id: "congruences"
concept: "同余理论"
domain: "mathematics"
subdomain: "number-theory"
subdomain_name: "数论"
difficulty: 5
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 32.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.344
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 同余理论

## 概述

同余（Congruence）是由德国数学家高斯（Carl Friedrich Gauss）在1801年出版的《算术研究》（*Disquisitiones Arithmeticae*）中系统化引入的概念。其核心定义为：若整数 $a$ 与 $b$ 除以正整数 $m$ 余数相同，则称 $a$ 与 $b$ 模 $m$ 同余，记作 $a \equiv b \pmod{m}$。等价地，$a \equiv b \pmod{m}$ 当且仅当 $m \mid (a - b)$，即 $m$ 整除 $a - b$。

高斯引入同余符号"$\equiv$"之前，数学家已在零散地处理被除数余数相关问题，但缺乏统一语言。高斯将其形式化为代数结构，使数论从碎片化的技巧集合升级为严格的理论体系。同余关系具有**等价关系**的三条性质：自反性（$a \equiv a$）、对称性（$a \equiv b \Rightarrow b \equiv a$）、传递性（$a \equiv b, b \equiv c \Rightarrow a \equiv c$），这使得整数集可以按模 $m$ 被划分为 $m$ 个不相交的**剩余类**（residue classes）。

同余理论之所以重要，在于它将无限整数集上的问题转化为有限集合上的运算，是密码学（如RSA算法依赖模幂运算）、计算机科学（哈希函数、循环校验码CRC）以及竞赛数学的基础工具。

---

## 核心原理

### 基本运算规则

设 $a \equiv b \pmod{m}$，$c \equiv d \pmod{m}$，则同余关系在四则运算下具有如下封闭性：

- **加法**：$a + c \equiv b + d \pmod{m}$
- **减法**：$a - c \equiv b - d \pmod{m}$
- **乘法**：$ac \equiv bd \pmod{m}$
- **幂运算**：$a^n \equiv b^n \pmod{m}$（$n$ 为正整数）

特别注意，**除法不能随意约分**。例如 $6 \equiv 10 \pmod{4}$，两边除以2得 $3 \equiv 5 \pmod{4}$，而 $3 \not\equiv 5 \pmod{4}$，这是错误的。合法的约简规则为：若 $ac \equiv bc \pmod{m}$，且 $\gcd(c, m) = d$，则 $a \equiv b \pmod{m/d}$。当 $\gcd(c, m) = 1$ 时，才可直接消去 $c$。

### 完全剩余系与简化剩余系

模 $m$ 的**完全剩余系**（Complete Residue System）是从每个剩余类中各取一个代表元构成的集合，最常用的是 $\{0, 1, 2, \ldots, m-1\}$，共 $m$ 个元素。

模 $m$ 的**简化剩余系**（Reduced Residue System，又称缩系）只保留与 $m$ 互素的那些剩余类的代表元，元素个数为欧拉函数 $\varphi(m)$。例如模12的简化剩余系为 $\{1, 5, 7, 11\}$，共 $\varphi(12) = 4$ 个元素。欧拉定理 $a^{\varphi(m)} \equiv 1 \pmod{m}$（$\gcd(a,m)=1$）正是简化剩余系在乘法下构成**群**这一性质的直接推论。

### 线性同余方程

形如 $ax \equiv b \pmod{m}$ 的方程称为线性同余方程。其有解的充要条件是 $\gcd(a, m) \mid b$。当有解时，解的个数恰好为 $d = \gcd(a, m)$ 个（在模 $m$ 意义下），且这 $d$ 个解在模 $m/d$ 下彼此等价，即解集形如 $x \equiv x_0 \pmod{m/d}$。

求解方法依赖**扩展欧几里得算法**：先求出满足 $as + mt = \gcd(a,m)$ 的整数 $s, t$，再令 $x_0 = s \cdot (b/d)$，即得特解。例如求解 $3x \equiv 6 \pmod{9}$：$\gcd(3,9)=3$ 且 $3 \mid 6$，故有3个解，分别为 $x \equiv 2, 5, 8 \pmod{9}$。

### 威尔逊定理

威尔逊定理（Wilson's Theorem，1770年由Edward Waring发表）给出了素数的同余判别准则：$p$ 为素数当且仅当 $(p-1)! \equiv -1 \pmod{p}$。例如 $p=5$：$(5-1)! = 24 \equiv 4 \equiv -1 \pmod{5}$，验证成立。这是同余理论中少数给出素数精确判定的结论，但由于计算 $(p-1)!$ 的复杂度，它在实际素性检测中很少使用，更多是理论工具。

---

## 实际应用

**整除性判断规则**：日常使用的"被9整除当且仅当各位数字之和被9整除"，本质是 $10 \equiv 1 \pmod{9}$，从而 $\overline{a_n a_{n-1}\cdots a_0} = \sum a_i \cdot 10^i \equiv \sum a_i \cdot 1^i = \sum a_i \pmod{9}$。类似地，"被11整除的交替位数和判断法"利用的是 $10 \equiv -1 \pmod{11}$。

**日期星期计算**：蔡勒公式（Zeller's Formula）利用模7同余计算任意日期是星期几。例如确定某日距已知星期的天数差 $d$，则目标星期数 $\equiv$ 已知星期数 $+ d \pmod{7}$。计算2000年1月1日后的第1000天：$1000 = 142 \times 7 + 6$，即 $1000 \equiv 6 \pmod{7}$，在星期六基础上加6天得星期五。

**RSA密码体制**：RSA加密中，加密运算为 $c \equiv m^e \pmod{n}$，解密为 $m \equiv c^d \pmod{n}$，其中 $ed \equiv 1 \pmod{\varphi(n)}$。解密的正确性直接来自欧拉定理的同余推论。典型参数中 $n$ 为2048位整数，安全性依赖对大数做模幂运算的高效性与因式分解的计算困难性之间的不对称性。

---

## 常见误区

**误区一：同余两边可以直接做除法**  
这是最频繁出现的错误。$12 \equiv 6 \pmod{6}$ 成立，但两边除以6得 $2 \equiv 1 \pmod{6}$，这是**错误**的。必须先检查除数与模数的最大公因数：若 $d = \gcd(c, m) > 1$，则商的同余关系模数需改为 $m/d$，而非原来的 $m$。忘记调整模数是此类题目失分的主要原因。

**误区二：同余关系中的"相等"等同于数值相等**  
$7 \equiv -5 \pmod{12}$ 是正确的同余式，但 $7 \neq -5$。在计算过程中，学生往往混淆"模 $m$ 同余"与"数值相等"，特别是在多步推导中将 $a \equiv b \pmod{m}$ 替换为 $a = b$ 继续运算，导致后续结论错误。同余符号"$\equiv$"与等号"$=$"有本质区别：前者描述的是等价类关系，后者是数值关系。

**误区三：模数为合数时，欧拉定理的阶必为 $\varphi(m)$**  
欧拉定理保证 $a^{\varphi(m)} \equiv 1 \pmod{m}$，但这并不意味着 $\varphi(m)$ 是使等式成立的最小正整数（即 $a$ 的阶）。例如 $\varphi(12) = 4$，但 $5^2 = 25 \equiv 1 \pmod{12}$，$5$ 的阶为2而非4。$a$ 的阶必须是 $\varphi(m)$ 的因子，但可以更小。将 $\varphi(m)$ 误认为是所有元素的阶，会在求解离散对数或分析循环群结构时产生错误。

---

## 知识关联

**前置知识衔接**：同余理论的定义直接建立在**模运算**（取余运算 $a \bmod m$）的基础上，二者的区别在于：模运算给出一个具体数值，同余关系描述整数之间的等价关系。**素数**知识在同余理论中反复出现——模数为素数时，线性同余方程 $ax \equiv b \pmod{p}$（$p \nmid a$）恰好有唯一解，且 $\mathbb{Z}/p\mathbb{Z}$ 构成域，性质远比合数模更整齐。

**后续理论拓展**：**费马小定理**（$a^{p-1} \equiv 1 \pmod{p}$，$p$ 为素数）是欧拉定理在 $m = p$ 时的特例，是Miller-Rabin素性检测的核心。**中国剩余定理**（CRT）解决的是多个模数下的同余方程组，给出
