---
id: "parts-of-speech"
concept: "词性概述"
domain: "english"
subdomain: "basic-grammar"
subdomain_name: "基础语法"
difficulty: 1
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 89.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Huddleston, Rodney & Pullum, Geoffrey. The Cambridge Grammar of the English Language, Cambridge UP, 2002"
  - type: "textbook"
    ref: "Murphy, Raymond. English Grammar in Use, 5th Ed., Cambridge UP, 2019"
  - type: "corpus"
    ref: "British National Corpus (BNC): Word class frequency statistics"
scorer_version: "scorer-v2.0"
---
# 词性概述

## 概述

词性（Parts of Speech）是根据单词在句子中的**语法功能和形态特征**进行的分类。英语传统上分为**八大词性**，但现代语言学（Huddleston & Pullum, 2002）倾向于更精细的分类。理解词性是掌握英语语法的第一步——句子结构的规则本质上就是"什么词性可以出现在什么位置"。

British National Corpus 的统计数据揭示了一个有趣的事实：英语中使用频率最高的 100 个词几乎全部是**功能词**（冠词、代词、介词、连词），而非内容词（名词、动词、形容词）。"the" 一个词就占了所有英语文本的约 **7%**。

## 核心知识点

### 1. 八大词性速览

| 词性 | 功能 | 示例 | BNC 中占比 |
|------|------|------|-----------|
| **名词**（Noun） | 表示人、事物、概念 | dog, happiness, London | ~30% |
| **动词**（Verb） | 表示动作或状态 | run, is, think | ~15% |
| **形容词**（Adjective） | 修饰名词 | big, beautiful, fast | ~7% |
| **副词**（Adverb） | 修饰动词/形容词/其他副词 | quickly, very, often | ~5% |
| **代词**（Pronoun） | 替代名词 | he, they, it, this | ~10% |
| **介词**（Preposition） | 表示关系（空间/时间/逻辑） | in, on, at, with, for | ~13% |
| **连词**（Conjunction） | 连接词、短语或从句 | and, but, because, if | ~7% |
| **感叹词**（Interjection） | 表达情感 | oh, wow, oops | < 0.5% |

**冠词**（a, an, the）在传统分类中归入形容词，现代语法学将其独立为**限定词**（Determiner）。

### 2. 开放词类 vs 封闭词类

**开放词类**（Open Class）：名词、动词、形容词、副词。新词不断加入（如 "google" 成为动词, "selfie" 成为名词）。

**封闭词类**（Closed Class）：代词、介词、连词、冠词。几乎不会新增成员。"the" 在 500 年前和今天的用法几乎一样。

这一区分对语言学习的意义：**封闭词类必须逐一记忆**（因为数量有限且不可推导），**开放词类可以通过规则和词根推导**。

### 3. 词性转换（Conversion）

英语的一大特征是同一个词可以充当不同词性（无需形态变化）：

- "water" → 名词（水）/ 动词（浇水）："Please **water** the plants."
- "fast" → 形容词（快速的）/ 副词（快速地）："He runs **fast**."
- "run" → 动词（跑）/ 名词（一次跑步）："He went for a **run**."
- "empty" → 形容词（空的）/ 动词（清空）："Please **empty** the bin."

**判断词性的方法**：不看单词本身，看它在句子中的**位置和功能**。

### 4. 词性识别测试

**名词测试**：可以加 the/a/an 吗？可以变复数吗？
- "the **happiness**" (OK) → 名词
- "the **happy**" (不自然) → 不是名词

**动词测试**：可以加时态标记吗？（-ed, -ing, will）
- "She **walked**" (OK) → 动词
- "She **happied**" (不可能) → 不是动词

**形容词测试**：可以放在名词前或 be 动词后吗？可以用 very 修饰吗？
- "a **big** dog" / "The dog is **big**" / "**very** big" → 形容词

**副词测试**：可以修饰动词吗？可以回答 how/when/where？
- "She runs **quickly**" (how?) → 副词

### 5. 句法功能映射

| 句法位置 | 典型词性 | 示例 |
|---------|---------|------|
| 主语 | 名词/代词 | **Dogs** bark. / **They** left. |
| 谓语 | 动词 | She **runs**. |
| 宾语 | 名词/代词 | I see **him**. |
| 定语（修饰名词） | 形容词 | A **red** car. |
| 状语（修饰动词） | 副词 | She sings **beautifully**. |
| 补语 | 名词/形容词 | She is a **teacher**. / She is **tall**. |

## 关键原理分析

### 词性与句子构造

英语句子的核心公式是 **S + V + (O/C)**（主语 + 动词 + 宾语/补语）。词性决定了什么可以填入这些槽位。理解词性不是为了"贴标签"，而是为了理解句子为什么是这样组织的——为什么 "Happy she" 不是合法句子但 "She is happy" 是。

### 语料库频率与学习优先级

基于 BNC 频率数据，学习优先级应该是：高频功能词（介词、代词、连词）> 高频内容词（常用动词和名词）> 低频内容词。掌握最常用的 2000 个词就能覆盖日常英语的 **85-90%**。

## 实践练习

**练习 1**：标注以下句子中每个词的词性："The quick brown fox jumps over the lazy dog."

**练习 2**：找出 "run" 在以下三句中的不同词性：(a) "I run every morning." (b) "It was a good run." (c) "Run the program."

## 常见误区

1. **"一个词只有一个词性"**：英语中大量词是多词性的。"light" 可以是名词、动词、形容词
2. **死记词性表而不看语境**：词性由句中位置决定，脱离句子谈词性无意义
3. **中文思维干扰**：中文词性转换更自由且无形态变化，导致英语中该加词尾时忘加（如形容词变副词加 -ly）