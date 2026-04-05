---
id: "predicate-logic"
concept: "谓词逻辑"
domain: "philosophy"
subdomain: "logic-reasoning"
subdomain_name: "逻辑与推理"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 92.6
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

# 谓词逻辑

## 概述

谓词逻辑（Predicate Logic），又称一阶逻辑（First-Order Logic，FOL），是在命题逻辑基础上引入量词、个体变元和谓词符号的逻辑系统。命题逻辑只能处理"苏格拉底是人"这类原子陈述的真假，却无法分析其内部结构；而谓词逻辑通过将陈述分解为谓词与个体，能够表达"所有人都会死"与"苏格拉底是人"之间的推导关系，从而使三段论论证得以形式化。

谓词逻辑的现代形式由德国数学家弗雷格（Gottlob Frege）在1879年出版的《概念文字》（*Begriffsschrift*）中首次系统建立。弗雷格引入了全称量词和函数-论元结构，彻底取代了亚里士多德沿用两千年的主谓分析框架。罗素和怀特海在1910年出版的《数学原理》进一步将一阶逻辑发展为数学基础的形式语言。

谓词逻辑的表达力远超命题逻辑：它能够刻画无限个体域上的普遍规律，而命题逻辑只能处理有限个独立命题。这一表达力使它成为现代数学证明、数据库查询语言（SQL的语义基础）以及人工智能知识表示的核心形式工具。

## 核心原理

### 语法构成：谓词、个体与量词

谓词逻辑的基本词汇包括四类符号：**个体常元**（如 $a, b, c$，指特定对象）、**个体变元**（如 $x, y, z$，范围在论域中变化）、**谓词符号**（如 $P, Q$，表示性质或关系）以及**函数符号**。一个 $n$ 元谓词接受 $n$ 个个体论元，例如 $\text{Loves}(x, y)$ 表示"$x$ 爱 $y$"，是二元谓词。

原子公式形如 $P(t_1, t_2, \ldots, t_n)$，其中 $t_i$ 是项（个体常元、变元或函数表达式）。复合公式则通过命题联结词（$\neg, \wedge, \vee, \rightarrow$）和两个量词构造：
- **全称量词** $\forall x\, \varphi(x)$：论域中所有个体 $x$ 满足 $\varphi$
- **存在量词** $\exists x\, \varphi(x)$：论域中至少存在一个 $x$ 满足 $\varphi$

两个量词通过否定可以互相定义：$\forall x\, \varphi(x) \equiv \neg\exists x\, \neg\varphi(x)$，这一等价关系称为**量词对偶性**。

### 语义：模型与满足关系

谓词逻辑的语义建立在**模型**（或解释）上，一个模型 $\mathcal{M} = \langle D, I \rangle$ 由非空论域 $D$ 和解释函数 $I$ 组成。$I$ 将常元映射到 $D$ 中的具体元素，将 $n$ 元谓词映射到 $D^n$ 的子集。例如，若 $D = \{\text{苏格拉底, 柏拉图}\}$，$I(\text{Human}) = \{\text{苏格拉底, 柏拉图}\}$，则 $\forall x\, \text{Human}(x)$ 在此模型下为真。

全称语句 $\forall x\, \varphi(x)$ 的真值判定需要遍历论域中**每一个**个体，因此当论域为无限集时（如自然数域），其真值验证在计算上不可穷举，这直接关联到一阶逻辑的**不可判定性**——丘奇（Alonzo Church）和图灵于1936年独立证明，一阶逻辑的有效性问题（即判断某公式是否在所有模型下为真）是不可判定的。

### 自由变元、约束变元与辖域

量词 $\forall x$ 和 $\exists x$ 对其**辖域**（scope）内的变元 $x$ 进行约束。公式 $\exists x\, P(x) \wedge Q(x, y)$ 中，第一个 $x$ 是约束变元，$y$ 是自由变元。一个含有自由变元的公式称为**开公式**，其真假依赖于变元的赋值；不含自由变元的公式称为**闭公式**（语句），真假由模型单独决定。混淆约束与自由变元是初学者最常见的形式错误，例如错误地将 $\forall x\, (P(x) \rightarrow Q(x))$ 与 $\forall x\, P(x) \rightarrow Q(x)$（此处 $Q(x)$ 中 $x$ 自由）视为等价。

## 实际应用

**三段论的形式化**：亚里士多德的"所有人皆有死，苏格拉底是人，故苏格拉底有死"可精确表达为：
$$\forall x\, (\text{Human}(x) \rightarrow \text{Mortal}(x)),\quad \text{Human}(\text{Socrates}) \vDash \text{Mortal}(\text{Socrates})$$
这一推导通过**全称例化**（Universal Instantiation）规则一步完成：将 $x$ 替换为常元 $\text{Socrates}$。

**数据库查询**：SQL中 `SELECT * FROM Students WHERE GPA > 3.5` 的语义等价于谓词逻辑公式 $\exists x\, (\text{Student}(x) \wedge \text{GPA}(x) > 3.5)$。关系代数的完整语义可以用一阶逻辑精确刻画，这是关系数据库理论的形式基础。

**数学公理的表达**：皮亚诺算术公理中，加法的递归定义需要用 $\forall x\, (x + 0 = x)$ 和 $\forall x\, \forall y\, (x + S(y) = S(x + y))$ 两条一阶语句精确表述，其中 $S$ 是后继函数符号。

## 常见误区

**误区一：全称量词预设存在性**。在现代谓词逻辑中，$\forall x\, P(x)$ 并不预设满足 $P$ 的对象存在。$\forall x\, (\text{Dragon}(x) \rightarrow \text{FireBreathing}(x))$ 在不存在龙的论域中**自动为真**（空真值，vacuous truth），因为不存在使前件为真的个体。这与亚里士多德逻辑的传统假设不同，初学者常因此在直觉上感到违反常识。

**误区二：量词顺序可以交换**。$\forall x\, \exists y\, \text{Loves}(x, y)$（每个人都有人爱他）与 $\exists y\, \forall x\, \text{Loves}(x, y)$（存在一个人被所有人爱）在语义上截然不同。前者在通常的人际关系论域中可能为真，后者则强得多。量词顺序不满足交换律是谓词逻辑区别于命题逻辑的关键特征之一。

**误区三：谓词逻辑等同于命题逻辑加变量**。许多初学者认为谓词逻辑只是"命题逻辑的变量版本"。实际上，两者在表达力和计算复杂度上存在本质差异：命题逻辑的可满足性问题是NP完全的，而一阶逻辑的有效性问题是$\Pi_2^0$完全的（属于算术层级的第二层），在可判定性意义上不可比较。

## 知识关联

从命题逻辑到谓词逻辑的核心跨越在于引入了**量化**机制：命题逻辑的联结词在谓词逻辑中完整保留，但新增的量词使得表达力从有限命题组合扩展到无限个体域上的全称与存在断言。掌握命题逻辑中的真值表方法和合取范式等技术，有助于理解谓词逻辑中前束范式（Prenex Normal Form）的化简——即将所有量词移到公式最前端的标准形式。

谓词逻辑直接通向**模态逻辑**：在谓词逻辑的量词结构上添加模态算子（$\Box$ "必然"、$\Diamond$ "可能"），可以得到量化模态逻辑，用于形式化"在所有可能世界中，存在某个体满足……"这类哲学断言。**逻辑哲学**中的核心争论，如指称理论（罗素摹状词理论）、本体论承诺（奎因的"存在就是变元的值"命题），都以谓词逻辑的量词语义为分析工具。**集合论基础**方面，ZFC公理系统完全用一阶谓词逻辑写成，集合的属于关系 $\in$ 即为一个二元谓词，使谓词逻辑成为现代数学基础的形式语言。