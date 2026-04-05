---
id: "combinatorial-identities"
concept: "组合恒等式"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 组合恒等式

## 概述

组合恒等式是关于二项式系数 $\binom{n}{k}$ 的等式，揭示了不同计数方式之间的内在一致性。这类恒等式并非偶然的数字巧合，而是从不同角度对同一集合进行计数时必然产生的等价关系。历史上，帕斯卡（Pascal）在17世纪系统整理了与二项式系数相关的恒等式，但许多结果实际上可追溯至中国的杨辉三角（13世纪）和阿拉伯数学家的著作（11世纪）。

学习组合恒等式的核心价值在于"双重计数"（Double Counting）思想的训练：对同一量建立两种表达式，令其相等即得恒等式。与代数恒等式不同，组合恒等式往往同时具有代数证明（代入展开）和组合论证（构造双射或分类讨论）两种完全不同风格的证明路径，这种双重性使其成为离散数学中最富启发性的内容之一。

## 核心原理

### Vandermonde 恒等式

Vandermonde 恒等式由法国数学家 Alexandre-Théophile Vandermonde 在1772年发表，其形式为：

$$\binom{m+n}{r} = \sum_{k=0}^{r} \binom{m}{k}\binom{n}{r-k}$$

其中 $m, n, r$ 为非负整数，$r \leq m+n$。组合解释：从 $m$ 个男生和 $n$ 个女生中选 $r$ 人，右侧按女生人数 $k$ 分类求和，左侧直接计数，两者必然相等。

当 $m = n = r$ 时，得到特殊情形 $\binom{2n}{n} = \sum_{k=0}^{n}\binom{n}{k}^2$，即中心二项式系数等于第 $n$ 行系数的平方和。例如 $n=3$ 时：$\binom{6}{3} = 20 = 1^2 + 9 + 9 + 1 = \binom{3}{0}^2 + \binom{3}{1}^2 + \binom{3}{2}^2 + \binom{3}{3}^2$。

### Hockey Stick 恒等式

Hockey Stick 恒等式（曲棍球棒恒等式）得名于其在帕斯卡三角中的几何形状——沿对角线连续求和后指向角落，形如曲棍球棒：

$$\sum_{i=r}^{n} \binom{i}{r} = \binom{n+1}{r+1}$$

例如取 $r=2, n=5$：$\binom{2}{2}+\binom{3}{2}+\binom{4}{2}+\binom{5}{2} = 1+3+6+10 = 20 = \binom{6}{3}$，验证成立。

组合论证：右侧 $\binom{n+1}{r+1}$ 表示从 $\{1,2,\ldots,n+1\}$ 中选 $r+1$ 个元素的方案数。设所选最大元素为 $i+1$（$i$ 从 $r$ 到 $n$），则其余 $r$ 个元素必须从 $\{1,\ldots,i\}$ 中选取，共 $\binom{i}{r}$ 种，对 $i$ 求和即得左侧。

### 帕斯卡恒等式与上指标求和

帕斯卡恒等式 $\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$ 是最基础的组合恒等式，直接对应帕斯卡三角的构造规则。其组合解释：从 $n$ 个元素中选 $k$ 个，固定第 $n$ 个元素，按其是否入选分类。

上指标求和恒等式（Parallel Summation）为：

$$\sum_{k=0}^{n} \binom{k+r}{k} = \binom{n+r+1}{n}$$

这是 Hockey Stick 的等价形式，通过替换变量 $k \to i - r$ 可以相互转化，但在计算递推数列的封闭形式时常以此形式出现。

### 二项式定理推论恒等式

将二项式定理 $(1+x)^n = \sum_{k=0}^{n}\binom{n}{k}x^k$ 在特殊点取值，可得一批恒等式：

- 令 $x=1$：$\sum_{k=0}^{n}\binom{n}{k} = 2^n$（子集总数为 $2^n$）
- 令 $x=-1$：$\sum_{k=0}^{n}(-1)^k\binom{n}{k} = 0$（奇偶子集数相等）
- 对 $x$ 求导后令 $x=1$：$\sum_{k=0}^{n}k\binom{n}{k} = n \cdot 2^{n-1}$（所有子集元素总数）

这三个结论在 $n=4$ 时分别给出 $16$、$0$、$32$，可直接验证。

## 实际应用

**计算路径数**：在 $m \times n$ 网格中从左下角走到右上角的最短路径数为 $\binom{m+n}{m}$。利用 Vandermonde 恒等式，可以计算途经某个中间格点的路径数：经过格点 $(a,b)$ 的路径数为 $\binom{a+b}{a} \cdot \binom{(m-a)+(n-b)}{m-a}$，这正是 Vandermonde 卷积的直接应用。

**概率论中的超几何分布**：超几何分布的归一化条件正是 Vandermonde 恒等式的直接应用。设总体 $N$ 人中有 $K$ 名特征者，抽取 $n$ 人，其概率质量函数中对所有 $k$ 求和时利用 $\sum_{k}\binom{K}{k}\binom{N-K}{n-k} = \binom{N}{n}$ 保证概率之和为1。

**递推关系的封闭解**：求 $S(n) = \sum_{k=1}^{n} k^2$ 的封闭形式时，利用 $k^2 = 2\binom{k}{2} + \binom{k}{1}$，再用 Hockey Stick 恒等式分别求和：$S(n) = 2\binom{n+1}{3} + \binom{n+1}{2} = \frac{n(n+1)(2n+1)}{6}$，这是将多项式分解为下降阶乘幂的标准技巧。

## 常见误区

**误区一：将 Vandermonde 恒等式误用于连续变量**。该恒等式要求 $m, n, r$ 为非负整数，且对 $k$ 的求和上限是 $r$ 而非 $\min(m,r)$。实际上当 $k > m$ 时 $\binom{m}{k} = 0$，所以写到 $r$ 或 $\min(m,r)$ 结果相同，但若粗心将上限写成 $m$ 或 $n$，在 $r < m$ 的情形下会引起混淆。

**误区二：认为 Hockey Stick 只有一个方向**。标准形式沿右对角线求和，但存在对称的左对角线版本：$\sum_{i=0}^{r}\binom{n+i}{i} = \binom{n+r+1}{r}$，即上指标求和恒等式。两种形式通过 $\binom{n}{k}=\binom{n}{n-k}$ 对称性相互转化，但初学者常忘记左方向版本的存在，在解题时无从下手。

**误区三：混淆代数证明与组合证明的适用场景**。代数证明（如用生成函数或直接展开）虽然严格，但对整数参数的限制不够敏感；组合证明天然只对非负整数成立，且能揭示"为什么"而非仅仅"是否"成立。考试中若题目要求"给出组合解释"，单纯的代数验证即使结果正确也不能得分。

## 知识关联

组合恒等式的学习直接建立在**二项式系数**的定义 $\binom{n}{k} = \frac{n!}{k!(n-k)!}$ 和**帕斯卡三角**的构造之上，需要熟练运用组合数的对称性 $\binom{n}{k}=\binom{n}{n-k}$ 以及边界条件 $\binom{n}{0}=\binom{n}{n}=1$。

在更高层次，这些恒等式是**生成函数**方法的基础——Vandermonde 恒等式本质上对应两个生成函数 $(1+x)^m$ 与 $(1+x)^n$ 相乘得 $(1+x)^{m+n}$ 后比较 $x^r$ 系数，这一思路直接引导学习者进入正式的幂级数运算框架。Hockey Stick 恒等式在**差分运算**和**有限微积分**中也有自然的对应，为后续研究离散积分（逆差分）奠定直觉基础。此外，带符号的组合恒等式如 $\sum_{k=0}^{r}(-1)^k\binom{r}{k}\binom{n-k}{m} = \binom{n-r}{m-r}$ 是**容斥原理**高阶应用的典型形式，是学习 Möbius 反演之前的必要铺垫。