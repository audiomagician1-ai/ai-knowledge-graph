---
id: "set-theory"
concept: "集合论"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 4
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 集合论

## 概述

集合论是研究由元素构成的无序整体（称为"集合"）的数学分支，核心对象是满足"要么属于、要么不属于"二值关系的元素与集合之间的隶属关系，记作 $a \in A$（a属于集合A）或 $a \notin A$（a不属于集合A）。集合用花括号表示，如 $A = \{1, 2, 3\}$，或用描述法表示，如 $B = \{x \mid x \text{ 是偶数}\}$。集合中的元素具有无序性和互异性，即 $\{1,2\} = \{2,1\}$，且同一元素不重复出现。

现代集合论由德国数学家格奥尔格·康托尔（Georg Cantor）于1874年至1884年间建立。康托尔在1874年发表的论文中首次证明了实数集与自然数集不等势（不可数与可数的区别），引入了无限集合的基数概念。后来，为了解决朴素集合论中罗素悖论（"所有不包含自身的集合构成的集合"导致矛盾）等问题，数学家采用ZFC公理系统（策梅洛-弗兰克尔加选择公理，1908年至1922年间完善）为集合论提供了严格基础。

在离散数学中，集合论为关系、函数、图论等所有后续主题提供形式化语言。计算机科学中的数据库查询（SQL的并、交、差操作直接对应集合运算）、程序语言的类型系统、以及算法中的集合数据结构（如Python的`set`），均建立在集合论概念之上。

## 核心原理

### 集合运算

四种基本集合运算定义如下，设全集为 $U$，集合 $A$、$B \subseteq U$：

- **并集**：$A \cup B = \{x \mid x \in A \text{ 或 } x \in B\}$，包含至少属于其中一个集合的所有元素。
- **交集**：$A \cap B = \{x \mid x \in A \text{ 且 } x \in B\}$，仅包含同时属于两个集合的元素。
- **差集**：$A - B = \{x \mid x \in A \text{ 且 } x \notin B\}$，从A中去除属于B的元素。
- **补集**：$\bar{A} = U - A = \{x \mid x \in U \text{ 且 } x \notin A\}$，全集中不属于A的元素。

集合运算满足德摩根定律：$\overline{A \cup B} = \bar{A} \cap \bar{B}$，$\overline{A \cap B} = \bar{A} \cup \bar{B}$。这与布尔代数中的逻辑运算形式完全对应，是命题逻辑与集合论之间的桥梁。

### 子集与幂集

若集合A中的每个元素都属于集合B，则称A是B的子集，记作 $A \subseteq B$。若 $A \subseteq B$ 且 $A \neq B$，则A是B的**真子集**，记作 $A \subsetneq B$。空集 $\emptyset$ 是任何集合的子集（含零个元素的集合），这是一个重要且常被忽视的规定。

集合A的**幂集**（Power Set）是A的所有子集构成的集合，记作 $\mathcal{P}(A)$ 或 $2^A$。关键公式：若 $|A| = n$（A有n个元素），则 $|\mathcal{P}(A)| = 2^n$。

例如，$A = \{a, b, c\}$，则：
$$\mathcal{P}(A) = \{\emptyset, \{a\}, \{b\}, \{c\}, \{a,b\}, \{a,c\}, \{b,c\}, \{a,b,c\}\}$$
共 $2^3 = 8$ 个元素。幂集的每个元素本身是一个集合，这一层次嵌套性质是后续定义关系（关系是笛卡尔积的子集）的基础。

### 笛卡尔积

集合A与集合B的**笛卡尔积**（Cartesian Product）定义为：
$$A \times B = \{(a, b) \mid a \in A \text{ 且 } b \in B\}$$
其中 $(a, b)$ 是**有序对**，$(a,b) \neq (b,a)$（除非 $a = b$）。若 $|A| = m$，$|B| = n$，则 $|A \times B| = mn$。

例如，$A = \{1, 2\}$，$B = \{x, y\}$，则：
$$A \times B = \{(1,x),(1,y),(2,x),(2,y)\}$$

笛卡尔积不满足交换律（$A \times B \neq B \times A$，除非 $A = B$ 或其中一个为空集），也不满足结合律。笛卡尔积可推广到n个集合：$A_1 \times A_2 \times \cdots \times A_n$，其元素为n元有序组 $(a_1, a_2, \ldots, a_n)$，这正是数据库"关系表"（每一行是n元组）的数学定义。

### 集合的基数与等势

集合元素的个数称为集合的**基数**，记作 $|A|$ 或 $\#A$。对于有限集，基数就是自然数。康托尔证明了 $|\mathbb{N}| = |\mathbb{Z}| = |\mathbb{Q}|$（均为可数无穷，基数记作 $\aleph_0$），但 $|\mathbb{R}| > |\mathbb{N}|$（不可数无穷）。在离散数学范围内，主要处理有限集合的计数，关键公式为**容斥原理**：
$$|A \cup B| = |A| + |B| - |A \cap B|$$
三个集合时：$|A \cup B \cup C| = |A|+|B|+|C|-|A\cap B|-|A\cap C|-|B\cap C|+|A\cap B\cap C|$

## 实际应用

**数据库查询**：SQL的 `UNION`（并集）、`INTERSECT`（交集）、`EXCEPT`（差集）操作直接实现集合运算。查询"选了课程A或课程B的学生"就是两个学生集合的并集操作。

**编程中的集合操作**：Python中 `A | B`（并）、`A & B`（交）、`A - B`（差）、`A ^ B`（对称差 $A \triangle B = (A-B)\cup(B-A)$）直接对应集合运算。判断 `A <= B` 检查A是否为B的子集。

**组合计数**：幂集大小 $2^n$ 解释了n个元素的所有选择方案数（每个元素选或不选，共 $2^n$ 种）。在密码学中，AES-128密钥空间大小为 $2^{128}$，正是128个二进制位的幂集大小。

**关系数据库设计**：表的每一行是笛卡尔积 $D_1 \times D_2 \times \cdots \times D_n$ 中的一个n元组，其中 $D_i$ 是第i列的值域集合。

## 常见误区

**误区一：将空集 $\emptyset$ 与 $\{\emptyset\}$ 混淆。** $\emptyset$ 是没有任何元素的集合，基数为0；而 $\{\emptyset\}$ 是包含空集这一元素的集合，基数为1。类比：空钱包不等于装有一个空钱包的钱包。因此 $\emptyset \in \{\emptyset\}$ 成立，但 $\emptyset = \{\emptyset\}$ 不成立。

**误区二：认为"子集"与"元素"概念等同。** $\{1\} \subseteq \{1,2,3\}$ 是正确的子集关系，而 $1 \in \{1,2,3\}$ 是元素属于关系，两者不可互换。常见错误是写出 $\{1\} \in \{1,2,3\}$（错误，因为 $\{1,2,3\}$ 的元素是数字1、2、3，不是集合 $\{1\}$）或 $1 \subseteq \{1,2,3\}$（错误，因为1是元素不是集合）。

**误区三：笛卡尔积中忽视有序性。** $(1,2) \neq (2,1)$，这与集合 $\{1,2\} = \{2,1\}$ 的无序性完全相反。学生常将笛卡尔积的元素当作普通集合处理，从而在定义二元关系时出错。当 $A = B$ 时，$A \times B$ 包含所有形如 $(a_1,a_2)$ 的对，其中顺序严格区分。

## 知识关联

**前置知识**：数集分类（自然数集 $\mathbb{N}$、整数集 $\mathbb{Z}$、实数集 $\mathbb{R}$ 等）直接提供了集合论中最常用的具体集合实例，使学生能将抽象集合运算应用于已知数域。

**后续概念——关系**：二元关系定义为笛卡尔积 $A \times B$ 的子集 $R \subseteq A \times B$。没有笛卡尔积和幂集的概念，无法严格定义"关系是什么"。

**后续概念——函数（离散）**：函数是特殊的二元关系，其中每个 $a \in A$ 恰好对应唯一的 $b \in B$。函数的定义域、值域、