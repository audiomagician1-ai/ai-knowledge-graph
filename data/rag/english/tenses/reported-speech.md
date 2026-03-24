---
id: "reported-speech"
concept: "间接引语"
domain: "english"
subdomain: "tenses"
subdomain_name: "时态系统"
difficulty: 5
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 间接引语

## 概述

间接引语（Indirect Speech / Reported Speech）是指用自己的话转述他人所说内容的语法形式，与直接引语（使用引号原文呈现）相对。直接引语如 "I am tired," she said，转为间接引语后变为 She said (that) she was tired。这一转换不是简单的"翻译"，而是涉及时态、人称代词、时间状语等多个层面的系统性变化。

间接引语作为英语语法体系中的正式规则，最早在拉丁语语法著作中被系统描述，英语继承了这一传统。现代英语中，间接引语的时态后退规则（backshift）在书面语和正式口语中严格执行，但在非正式口语中有时允许保留原时态——这一区别在教学中经常被忽视，导致学习者要么过度后退，要么完全不后退。

时态后退规则之所以重要，是因为它反映了英语对"报告时间"与"原话时间"关系的语法编码方式：当主句动词（reporting verb）使用过去时时，从句中的时态必须相应往过去方向移动一格，以维持时间逻辑的一致性。这是英语区别于汉语的显著特征之一——汉语转述一般不改变时态。

## 核心原理

### 时态后退的基本规则

间接引语的时态后退遵循固定的对应关系，可总结为以下表格：

| 直接引语时态 | 间接引语时态 |
|---|---|
| 一般现在时（am/is/are） | 一般过去时（was/were） |
| 现在进行时（is doing） | 过去进行时（was doing） |
| 一般过去时（did） | 过去完成时（had done） |
| 现在完成时（has done） | 过去完成时（had done） |
| 将来时（will do） | 过去将来时（would do） |
| 过去进行时（was doing） | 过去完成进行时（had been doing） |

例如，直接引语 "I have finished the report" 转换后变为 He said he had finished the report，现在完成时 has finished 后退为过去完成时 had finished。

### 主句动词时态决定是否后退

时态后退的触发条件是**主句动词使用过去时**。若主句动词为现在时或将来时，从句时态不需要后退。比较以下两句：

- She **says** she **is** hungry.（主句为一般现在时，从句时态不变）
- She **said** she **was** hungry.（主句为一般过去时，从句时态后退）

这一规则意味着，当我们使用 says / tells / announces 等现在时报告动词时，间接引语中的时态可以完全保留原话的时态形式。许多教材忽略了这一区分，导致学生误以为"间接引语必须后退"是无条件的绝对规则。

### 过去完成时作为时态后退的终点

过去完成时（had + 过去分词）在时态后退中扮演特殊角色：它是后退链条的**终点**。当直接引语中已经使用了一般过去时或现在完成时，转换为间接引语后均统一变为过去完成时。这就是为什么学习本概念的先修知识是过去完成时——若不理解 had done 的构成与含义，就无法正确完成这一步转换。

例如："We **visited** Paris last year" → She said they **had visited** Paris the year before.

此处有两个变化同时发生：visited 后退为 had visited，而时间状语 last year 也同步变为 the year before（详见时间状语转换规则）。

### 时间状语与地点词的同步转换

时态后退往往伴随以下时间/地点词的变换：

| 直接引语 | 间接引语 |
|---|---|
| now | then |
| today | that day |
| yesterday | the day before / the previous day |
| tomorrow | the next day / the following day |
| last week | the week before |
| here | there |
| this | that |

例如，直接引语 "I will call you **tomorrow**" 转换后为 He said he would call me **the next day**。遗漏这些词的转换是高频错误来源。

## 实际应用

### 新闻报道中的间接引语

新闻英语是间接引语使用频率最高的文体之一。BBC新闻报道中常见句式如：

> The Prime Minister **said** the government **would** introduce new legislation in January. He added that the policy **had been** carefully considered.

此处 would introduce 是 will introduce 的后退形式，had been considered 是 has been considered 的后退形式，两者均遵循标准后退规则。

### 考试场景中的间接引语转换题

英语四六级及雅思写作中，间接引语转换是常见考点。以下为典型转换练习：

**直接引语：** "I can't attend the meeting because I am preparing for the exam," Tom said.

**间接引语：** Tom said (that) he **couldn't** attend the meeting because he **was** preparing for the exam.

注意：情态动词 can 后退为 could，am preparing 后退为 was preparing，人称代词 I 改为 he。

### 一般疑问句的间接引语转换

疑问句转换为间接引语时，不再使用助动词倒装，改用陈述语序，并以 whether 或 if 引导：

- 直接引语："**Are** you coming?" → 间接引语：He asked **whether/if** I **was** coming.
- 特殊疑问句："**Where** do you live?" → He asked **where** I **lived**.

这里的关键变化：疑问词序（do you live）恢复为陈述语序（I lived），且时态同步后退。

## 常见误区

**误区一：认为过去式后退后仍是过去式**

许多学习者将 "She said she went there" 和 "She said she had gone there" 视为等效表达。严格语法规范下，直接引语若为一般过去时（went），间接引语应后退为过去完成时（had gone）。但在非正式口语和美式英语中，保留一般过去时是被接受的。区分"规范用法"和"可接受用法"有助于理解为何不同教材给出不同答案。

**误区二：所有间接引语都必须后退时态**

当直接引语表达的是**客观事实或普遍真理**时，时态可以不后退。例如："Water boils at 100 degrees Celsius," the teacher said → The teacher said water **boils** at 100 degrees Celsius（不是 boiled）。物理常数不会因为"转述"而改变，因此使用一般现在时是正确的。

**误区三：人称代词转换规则混淆**

直接引语中的第一人称（I/we）和第二人称（you）在间接引语中需要根据语境转换，不存在固定公式。"I like you," John said to Mary → John told Mary that **he** liked **her**。此处 I→he 是因为 John 是第三人称，you→her 是因为听话人 Mary 是第三人称。如果语境不明，人称转换可能产生歧义，这正是书面语法题中常见的陷阱。

## 知识关联

学习间接引语需要熟练掌握**过去完成时**（had + p.p.），因为大量直接引语中的一般过去时和现在完成时在转换后都汇聚到过去完成时这一形式。如果对 had been、had seen、had finished 的构成尚不熟悉，时态后退的操作将频繁出错。

本概念向上延伸的是**间接引语进阶**，涵盖情态动词在间接引语中的后退规则（must→had to，need not→didn't need to），以及祈使句（命令/请求）转为间接引语的特殊句型——此时不再使用 say/tell，而使用 ask sb. to do / order sb. to do / advise sb. to do 等结构，时态后退逻辑也与陈述句不同，是该系统中难度最高的部分。
