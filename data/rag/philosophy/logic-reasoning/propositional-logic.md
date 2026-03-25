---
id: "propositional-logic"
concept: "命题逻辑"
domain: "philosophy"
subdomain: "logic-reasoning"
subdomain_name: "逻辑与推理"
difficulty: 3
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Hurley, Patrick J. A Concise Introduction to Logic, 13th Ed., Ch.6-7"
  - type: "textbook"
    ref: "Enderton, Herbert. A Mathematical Introduction to Logic, 2nd Ed., 2001"
  - type: "academic"
    ref: "Boole, George. An Investigation of the Laws of Thought, 1854"
scorer_version: "scorer-v2.0"
---
# 命题逻辑

## 概述

命题逻辑（Propositional Logic, 又称命题演算）是形式逻辑最基础的分支，研究**命题（Proposition）之间通过逻辑联结词组合后的真值关系**。一个命题是一个有确定真假值的陈述句——"地球是圆的"（真）、"2 + 2 = 5"（假）。

George Boole（1854）在《思维法则的探究》中首次将逻辑系统化为代数运算，创立了布尔代数——这一成果在 80 年后被 Claude Shannon 应用于电路设计，直接催生了数字计算机。命题逻辑是整个现代逻辑学、计算机科学（电路设计、编程语言、SAT 求解器）和 AI 推理的基石。

## 核心知识点

### 1. 逻辑联结词（Logical Connectives）

设 p, q 为命题：

| 联结词 | 符号 | 读法 | 真值条件 |
|--------|------|------|---------|
| **否定** | NOT p | "非 p" | p 为真时结果为假，反之亦然 |
| **合取** | p AND q | "p 且 q" | 两者都真时才真 |
| **析取** | p OR q | "p 或 q" | 至少一个为真则真（包容性） |
| **蕴含** | p -> q | "若 p 则 q" | 仅当 p 真 q 假时为假 |
| **双条件** | p <-> q | "p 当且仅当 q" | 两者真值相同时为真 |

**蕴含的反直觉性**：p -> q 在 p 为假时**永远为真**（"空真"）。"如果月亮是方的，那么 2+2=5" 在逻辑上为真。这是因为蕴含只承诺"在前件成立时后件也成立"——前件不成立时，承诺自动满足。

### 2. 真值表方法

真值表穷举所有可能的真值组合来判断复合命题的真假。

**示例**：验证 NOT (p AND q) 等价于 (NOT p) OR (NOT q)（德摩根定律）

| p | q | p AND q | NOT(p AND q) | NOT p | NOT q | (NOT p) OR (NOT q) |
|---|---|---------|--------------|-------|-------|-------------------|
| T | T | T | F | F | F | F |
| T | F | F | T | F | T | T |
| F | T | F | T | T | F | T |
| F | F | F | T | T | T | T |

第 4 列与第 7 列完全相同，证毕。

### 3. 重要逻辑等价与推理规则

**逻辑等价**：
- **德摩根定律**：NOT(p AND q) = (NOT p) OR (NOT q); NOT(p OR q) = (NOT p) AND (NOT q)
- **逆否命题**：p -> q 等价于 NOT q -> NOT p
- **双重否定**：NOT(NOT p) = p
- **分配律**：p AND (q OR r) = (p AND q) OR (p AND r)

**关键推理规则**：
- **肯定前件**（Modus Ponens）：p -> q, p，所以 q
- **否定后件**（Modus Tollens）：p -> q, NOT q，所以 NOT p
- **假言三段论**：p -> q, q -> r，所以 p -> r
- **析取三段论**：p OR q, NOT p，所以 q

### 4. 重言式、矛盾式与可满足式

- **重言式**（Tautology）：在所有真值赋值下都为真。例：p OR (NOT p)
- **矛盾式**（Contradiction）：在所有真值赋值下都为假。例：p AND (NOT p)
- **可满足式**（Satisfiable）：至少存在一种赋值使其为真

**SAT 问题**：判断一个命题公式是否可满足——这是计算机科学中第一个被证明为 NP-Complete 的问题（Cook-Levin 定理，1971）。现代 SAT 求解器可以处理数百万变量的实例，广泛用于芯片验证、AI 规划和密码分析。

## 关键原理分析

### 命题逻辑的完备性与局限

**完备性**：命题逻辑的推理系统是完备的——所有重言式都可以通过形式推导证明（反之亦然）。

**局限性**：命题逻辑无法表达变量和量词。"所有人都会死"和"苏格拉底是人"无法在命题逻辑中推出"苏格拉底会死"——这需要**谓词逻辑**（增加全称量词和存在量词）。

### 与编程的直接关联

编程中的 `if-else`、`&&`、`||`、`!` 就是命题逻辑联结词的直接实现。布尔表达式求值、短路求值（Short-Circuit Evaluation）、条件编译都是命题逻辑的应用。

## 实践练习

**练习 1**：用真值表验证：(p -> q) 等价于 (NOT p) OR q。

**练习 2**：将以下自然语言论证形式化为命题逻辑并验证有效性："如果下雨，地面就会湿。地面没有湿。所以没有下雨。"

## 常见误区

1. **混淆"或"的含义**：逻辑的 OR 是包容性的（两者可以同时为真），日常语言中"茶或咖啡？"通常是排斥性的
2. **否定蕴含的方向**：p -> q 的否定不是 NOT p -> NOT q（否命题），而是 p AND (NOT q)
3. **"蕴含 = 因果"**：逻辑蕴含只是真值关系，不要求 p 与 q 之间有因果联系