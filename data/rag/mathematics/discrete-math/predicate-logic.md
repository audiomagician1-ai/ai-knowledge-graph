---
id: "predicate-logic"
concept: "谓词逻辑"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
updated_at: "2026-03-26"
---
# 谓词逻辑

## 概述

谓词逻辑（Predicate Logic），又称一阶逻辑（First-Order Logic，FOL），是命题逻辑的扩展系统，它引入了量词和谓词，使得逻辑语言能够表达个体对象的性质及对象之间的关系。命题逻辑只能将"苏格拉底是人"这类陈述视为不可分割的原子命题，而谓词逻辑能将其分析为谓词 $H(x)$（"$x$ 是人"）作用于个体常量 $\text{socrates}$ 上，写作 $H(\text{socrates})$。

谓词逻辑的现代形式化由戈特洛布·弗雷格（Gottlob Frege）于1879年在其著作《概念文字》（*Begriffsschrift*）中首次系统提出，这标志着现代数理逻辑的诞生。弗雷格引入了全称量词和存在量词的符号系统，使数学证明能够被完全形式化。

谓词逻辑之所以重要，在于它能够表达"所有"和"存在"这类量化陈述，这是数学定理表达的基础。例如，"每个正整数都有一个后继"无法在命题逻辑中表达，但在谓词逻辑中可以精确写作 $\forall x \in \mathbb{Z}^+, \exists y \in \mathbb{Z}^+(y = x + 1)$。

---

## 核心原理

### 谓词与个体域

谓词（Predicate）是一个函数，它接受一个或多个个体作为参数，返回真值 $\top$ 或 $\bot$。接受 $n$ 个参数的谓词称为 $n$ 元谓词。例如：

- 一元谓词：$\text{Prime}(x)$ 表示"$x$ 是质数"，$\text{Prime}(7) = \top$，$\text{Prime}(4) = \bot$
- 二元谓词：$\text{Greater}(x, y)$ 表示"$x > y$"，$\text{Greater}(5, 3) = \top$

个体域（Domain of Discourse），也称论域，是所有个体变量取值的集合。同一个谓词公式在不同个体域下可以有不同的真值。例如，$\forall x\, \text{Prime}(x)$ 在论域为 $\{2, 3, 5\}$ 时为真，在论域为 $\{1, 2, 3\}$ 时为假。

### 量词：全称量词与存在量词

谓词逻辑有两个基本量词：

- **全称量词** $\forall$（Universal Quantifier）：$\forall x\, P(x)$ 表示论域中所有个体 $x$ 都满足谓词 $P$。其真值定义为：若论域中每一个体代入 $P$ 均得 $\top$，则整体为 $\top$。
- **存在量词** $\exists$（Existential Quantifier）：$\exists x\, P(x)$ 表示论域中至少存在一个个体 $x$ 满足 $P$。

两者通过德摩根定律相互转化：
$$\neg \forall x\, P(x) \equiv \exists x\, \neg P(x)$$
$$\neg \exists x\, P(x) \equiv \forall x\, \neg P(x)$$

量词的**辖域**（Scope）是指量词作用的范围，即紧跟量词的那个子公式。在 $\forall x\,(P(x) \to Q(x)) \land R(x)$ 中，$\forall x$ 的辖域是 $P(x) \to Q(x)$，而 $R(x)$ 中的 $x$ 不在辖域内。

### 自由变量与约束变量

变量在谓词公式中有两种出现方式：

- **约束变量**（Bound Variable）：出现在某个量词的辖域内，且该变量被此量词绑定。在 $\forall x\, P(x)$ 中，$x$ 是约束变量，可以被任意其他变量名替换而不改变公式语义，即 $\forall x\, P(x) \equiv \forall y\, P(y)$（$\alpha$-等价）。
- **自由变量**（Free Variable）：未被任何量词绑定的变量。在 $P(x, y) \land \forall x\, Q(x)$ 中，第一个 $x$ 和 $y$ 均为自由变量，而 $\forall x$ 辖域内的 $x$ 是约束变量。

包含自由变量的公式称为**开公式**（Open Formula），它本身无法判断真假，必须代入具体值才能求值。不含自由变量的公式称为**闭公式**或**语句**（Sentence），其真值由论域唯一确定。

量词嵌套时须特别注意辖域的划分。在 $\forall x\, \exists y\, (x < y)$ 中，两个量词均绑定各自的变量；该公式在论域 $\mathbb{N}$（自然数）上为真，意为"每个自然数都有比它更大的自然数"。

### 前束范式（PNF）

谓词逻辑公式可以化为**前束范式**（Prenex Normal Form），其标准形式为：
$$Q_1 x_1\, Q_2 x_2\, \cdots\, Q_n x_n\, M(x_1, x_2, \ldots, x_n)$$
其中 $Q_i \in \{\forall, \exists\}$，$M$ 是不含量词的无量词矩阵（Matrix）。化为前束范式的步骤包括：消去蕴含符号、向内推入否定（使用德摩根定律）、变量换名（避免辖域冲突）、最后将所有量词前移。

---

## 实际应用

**数学定理的形式化表达**：费马小定理可以写作 $\forall p\, \forall a\, (\text{Prime}(p) \land \neg \text{Divides}(p, a) \to a^{p-1} \equiv 1 \pmod{p})$，这一表达借助了谓词逻辑的全称量词和多元谓词。

**数据库查询**：关系型数据库的查询语言 SQL 在语义上对应谓词逻辑。例如，查询"找出所有工资高于部门平均工资的员工"可对应谓词公式 $\exists\, \text{dept}\,(\text{Employee}(x, \text{dept}) \land \text{Salary}(x) > \text{AvgSalary}(\text{dept}))$。

**程序验证**：霍尔逻辑（Hoare Logic）使用谓词 $\{P\}\, C\, \{Q\}$ 表示：若前置条件谓词 $P$ 成立，执行程序 $C$ 后后置条件谓词 $Q$ 成立。这是软件形式验证的基础语言，其中 $P$ 和 $Q$ 均为谓词逻辑公式。

**自然语言处理**：句子"所有学生都提交了作业"被分析为 $\forall x\,(\text{Student}(x) \to \text{Submitted}(x))$，而"有学生没有提交作业"被分析为 $\exists x\,(\text{Student}(x) \land \neg \text{Submitted}(x))$，二者互为否定关系，恰好体现了量词德摩根定律。

---

## 常见误区

**误区一：混淆 $\forall x\,(P(x) \to Q(x))$ 与 $\forall x\,(P(x) \land Q(x))$**

这是谓词逻辑中最常见的错误。"所有猫都是动物"的正确翻译是 $\forall x\,(\text{Cat}(x) \to \text{Animal}(x))$，而非 $\forall x\,(\text{Cat}(x) \land \text{Animal}(x))$。后者断言论域中每个个体既是猫又是动物，这是一个远强于前者的命题。类似地，存在量词通常与合取配合：$\exists x\,(\text{Cat}(x) \land \text{Animal}(x))$（存在一个既是猫又是动物的个体）。

**误区二：量词顺序不可随意交换**

$\forall x\, \exists y\, P(x, y)$ 与 $\exists y\, \forall x\, P(x, y)$ 语义不同。前者表示"对每个 $x$，都存在（可能各不相同的）$y$"；后者表示"存在同一个 $y$，对所有 $x$ 成立"。以 $P(x,y)$ 为 $y > x$，在 $\mathbb{R}$ 上：前者为真（对每个实数可取更大值），后者为假（不存在一个最大实数）。一般有 $\exists y\, \forall x\, P(x,y) \Rightarrow \forall x\, \exists y\, P(x,y)$，但反向蕴含不成立。

**误区三：自由变量不影响公式语义的错误认识**

有些学生认为自由变量的名字无关紧要，可以随意替换。实际上，对约束变量（在辖域内）可以安全换名（$\alpha$-等价），但对自由变量换名则改变了公式的语义。在 $P(x) \land \forall y\, Q(x, y)$ 中，若将自由变量 $x$ 换为 $y$，得到 $P(y) \land \forall y\, Q(y, y)$，此时原本自由的 $x$ 被量词 $\forall y$ "意外捕获"，这一现象称为**变量捕获**（Variable Capture），会产生逻辑错误。

---
