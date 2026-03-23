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
quality_tier: "pending-rescore"
quality_score: 35.1
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.375
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 集合论

## 概述

集合论是研究"集合"这一数学对象及其运算规则的理论体系。一个**集合**是不同对象的无序聚合，其中每个对象称为**元素**。集合的根本特征有两点：其一是**确定性**，即任意给定一个对象，必能判断它是否属于该集合；其二是**互异性**，集合中不含重复元素。记号 $a \in A$ 表示元素 $a$ 属于集合 $A$，$a \notin A$ 表示不属于。

集合论由德国数学家格奥尔格·康托尔（Georg Cantor）在1874年至1884年间系统建立。康托尔最初用集合论研究无穷级数，并在1874年证明了实数集不可数——这是集合论最震撼的早期成果。然而朴素集合论在1901年遭遇罗素悖论（"所有不包含自身的集合"构成的集合会导致矛盾），迫使数学家建立更严格的公理化集合论（如ZFC公理系统）。

在离散数学中，集合论是描述关系、函数、图论、组合计数等几乎一切结构的基础语言。理解幂集的大小公式 $|2^A| = 2^{|A|}$ 和笛卡尔积的计数规则，直接支撑着后续对关系和函数的形式化定义。

---

## 核心原理

### 子集与集合相等

若集合 $A$ 的每个元素都属于集合 $B$，则称 $A$ 是 $B$ 的**子集**，记作 $A \subseteq B$。若 $A \subseteq B$ 且 $B \subseteq A$，则 $A = B$。若 $A \subseteq B$ 但 $A \neq B$，则称 $A$ 是 $B$ 的**真子集**，记作 $A \subsetneq B$。

注意空集 $\emptyset$ 是任何集合的子集，这由"空洞真"（vacuous truth）原则保证：因为不存在 $\emptyset$ 中的元素违反 $A \subseteq B$ 的条件，故命题为真。若集合 $A$ 有 $n$ 个元素，则 $A$ 共有 $2^n$ 个子集（含 $\emptyset$ 和 $A$ 本身）。例如 $A = \{1, 2, 3\}$ 有 $2^3 = 8$ 个子集。

### 集合的基本运算

给定全集 $U$ 以及集合 $A, B \subseteq U$，定义四种基本运算：

- **并集**：$A \cup B = \{x \mid x \in A \text{ 或 } x \in B\}$
- **交集**：$A \cap B = \{x \mid x \in A \text{ 且 } x \in B\}$
- **差集**：$A - B = \{x \mid x \in A \text{ 且 } x \notin B\}$（也记 $A \setminus B$）
- **补集**：$\complement_U A = \{x \mid x \in U \text{ 且 } x \notin A\}$

这四种运算满足一组重要的代数律。其中**德摩根定律**在离散数学中尤为常用：
$$\complement_U(A \cup B) = \complement_U A \cap \complement_U B$$
$$\complement_U(A \cap B) = \complement_U A \cup \complement_U B$$

此外，集合运算满足**分配律**：$A \cap (B \cup C) = (A \cap B) \cup (A \cap C)$，以及**吸收律**：$A \cup (A \cap B) = A$。这些定律在证明集合等式时可逐步替换使用。

### 幂集

集合 $A$ 的**幂集**（power set）是由 $A$ 的所有子集构成的集合，记作 $\mathcal{P}(A)$ 或 $2^A$。若 $|A| = n$（$|A|$ 表示 $A$ 的元素个数，称为**基数**），则：
$$|\mathcal{P}(A)| = 2^n$$

以 $A = \{a, b\}$ 为例，$\mathcal{P}(A) = \{\emptyset, \{a\}, \{b\}, \{a,b\}\}$，共 $2^2 = 4$ 个元素。特别地，$\mathcal{P}(\emptyset) = \{\emptyset\}$，其基数为 $2^0 = 1$，而非 $0$。幂集本身也是一个集合，因此可以对它继续取幂集，得到 $\mathcal{P}(\mathcal{P}(A))$，其元素个数为 $2^{2^n}$，增长极为迅速。

### 笛卡尔积

集合 $A$ 与集合 $B$ 的**笛卡尔积**定义为：
$$A \times B = \{(a, b) \mid a \in A,\ b \in B\}$$

其中 $(a, b)$ 是**有序对**，$(a,b) \neq (b,a)$（除非 $a = b$）。若 $|A| = m$，$|B| = n$，则 $|A \times B| = mn$。例如 $A = \{1,2\}$，$B = \{x, y, z\}$，则 $A \times B$ 有 $2 \times 3 = 6$ 个有序对。笛卡尔积不满足交换律（$A \times B \neq B \times A$，除非 $A = B$ 或其中一个为空集），也不满足结合律（$(A \times B) \times C \neq A \times (B \times C)$，因为元素结构不同）。

---

## 实际应用

**数据库关系模型**：关系型数据库中的"表"本质上是若干域（集合）的笛卡尔积的子集。例如，学生表由学号域 $\times$ 姓名域 $\times$ 年龄域的笛卡尔积中选取的有效元组组成，这正是"关系"一词的集合论来源。

**位向量表示集合**：若全集 $U = \{u_1, u_2, \ldots, u_n\}$，任意子集 $A \subseteq U$ 可以用长度为 $n$ 的二进制串表示：第 $i$ 位为1当且仅当 $u_i \in A$。在这种表示下，并集对应按位OR，交集对应按位AND，补集对应按位NOT，运算效率极高，被广泛用于算法竞赛的状态压缩动态规划中。

**程序语言的类型系统**：许多编程语言的类型理论直接使用集合论概念。例如，Python 的 `set` 类型支持 `|`（并集）、`&`（交集）、`-`（差集）操作，且 `issubset()` 方法直接对应 $\subseteq$ 的判断。

---

## 常见误区

**误区一：将 $\{a\}$ 与 $a$ 混同**
单元素集合 $\{a\}$ 与元素 $a$ 是不同的对象。$a \in \{a\}$ 为真，但 $\{a\} \in \{a\}$ 为假；$a \subseteq \{a\}$ 只有当 $a$ 本身也是集合时才有意义。在幂集运算中，$\mathcal{P}(\{a\}) = \{\emptyset, \{a\}\}$，注意其元素是 $\emptyset$ 和 $\{a\}$，而不是 $\emptyset$ 和 $a$。

**误区二：认为空集没有子集**
许多初学者误以为"空集里什么都没有，所以没有子集"。实际上 $\mathcal{P}(\emptyset) = \{\emptyset\}$，空集有且只有一个子集，即它自身。这与"空集是任意集合的子集"这一规则一致，因为空集是空集的子集（$\emptyset \subseteq \emptyset$）。

**误区三：笛卡尔积的顺序无关**
由于集合本身是无序的，学生常误以为 $A \times B = B \times A$。但笛卡尔积的元素是有序对，$(1, x) \neq (x, 1)$，因此当 $A \neq B$ 时，$A \times B \neq B \times A$。可以用韦恩图类比：$A \times B$ 和 $B \times A$ 在平面坐标中对应关于 $y=x$ 对称的两组点，形状相同但位置不同。

---

## 知识关联

**前置知识**：集合论直接建立在**数集分类**的认知基础上。自然数集 $\mathbb{N}$、整数集 $\mathbb{Z}$、有理数集 $\mathbb{Q}$、实数集 $\mathbb{R}$ 是集合论的具体实例，学生对这些数集的包含关系（$\mathbb{N} \subsetneq \mathbb{Z} \subsetneq \mathbb{Q} \subsetneq \mathbb{R}$）的直觉正好对应子集的概念。

**后续概念——关系**：**二元关系**被定义为笛卡尔积的子集：$R \subseteq A \times B$。没有笛卡尔积的定义，关系就无法形式化。等价关系、偏序关系等都用集合论语言描述其自反性、对称性、传递性。

**后续概念——函数（离散）**：函数是一种特殊的关系，即满足"每个 $a \in A$ 恰好对应一个 $b \in B$"的子集 $f \subseteq A \times B$。函数的定义域、值域、像都用集合运算来精确
