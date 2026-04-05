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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 间接引语

## 概述

间接引语（Reported Speech）是指用自己的话转述他人所说内容的语法结构，区别于用引号直接照搬原话的直接引语（Direct Speech）。将直接引语转换为间接引语时，最核心的操作是**时态后退**（Backshift），即原句中的时态需向过去方向移动一级。例如，直接引语中的一般现在时（She said, "I am tired."）转为间接引语后变为一般过去时（She said that she was tired.）。

这一语法规则源于英语的**时态一致原则**（Sequence of Tenses），在16世纪的英语文法书中已有系统描述。其核心逻辑是：当说话动词（reporting verb）使用过去时时，从句内容被视为发生在过去的认知，因此从句时态需相应后退，以反映时间上的距离感。在新闻报道、学术引用和日常对话中，间接引语的准确使用直接影响信息传达的准确性与正式程度。

间接引语并非仅是时态变化，还涉及人称代词、时间状语词和地点副词的同步替换，但时态后退是其中规则最复杂、最容易出错的部分，也是英语学习者在写作和考试中失分的高频点。

---

## 核心原理

### 时态后退的完整对应表

直接引语转间接引语时，时态按以下规律后退一级：

| 直接引语时态 | 间接引语时态 |
|---|---|
| 一般现在时（am/is/are） | 一般过去时（was/were） |
| 现在进行时（is doing） | 过去进行时（was doing） |
| 一般过去时（did） | 过去完成时（had done） |
| 现在完成时（has done） | 过去完成时（had done） |
| 将来时（will do） | 过去将来时（would do） |
| 过去完成时（had done） | 过去完成时（had done，不再后退） |

特别注意：**过去完成时是时态后退的终点**，已经无法再向过去移动，因此直接引语中的过去完成时在间接引语中保持不变。例如：He said, "I had finished the report." → He said that he had finished the report.

### 说话动词的核心作用

时态后退仅在说话动词（如 said、told、asked、replied、explained）使用**过去时**时才强制触发。若说话动词为一般现在时，则从句时态无需后退：

- She **says** (that) she **is** tired. （说话动词现在时，从句保持原时态）
- She **said** (that) she **was** tired. （说话动词过去时，从句时态后退）

此外，不同说话动词对应不同的句型结构：**tell 必须接宾语**（She told me that...），而 say 不能直接接人称宾语（❌ She said me that...）。ask 用于转述疑问句，后接 if/whether 或疑问词引导的从句。

### 时间与地点状语的替换规则

时态后退之外，间接引语还要求特定副词随语境改变：

- now → then
- today → that day
- yesterday → the day before / the previous day
- tomorrow → the next day / the following day
- here → there
- this → that / these → those

例如：He said, "I will call you **tomorrow**." → He said that he would call me **the next day**.

遗漏这些状语的替换是间接引语书写中极常见的错误，即便时态后退正确，状语不改也会导致语义混乱。

### 不需要时态后退的特殊情形

以下三种情形中，时态后退**不适用或不强制**：

1. **客观真理和永恒事实**：直接引语描述的是不变的科学事实，转述时可保留现在时。例如：The teacher said that the earth **moves** around the sun.（保留 moves 而非改为 moved）
2. **说话时间与转述时间极近**：若引语刚刚发生，转述者可以不后退时态，但这在正式书面语中较少见。
3. **条件句中的虚拟语气**：if 引导的虚拟条件句（如 If I were you...）转述后通常结构不变，不再后退。

---

## 实际应用

**新闻报道场景**：英文新闻中，记者转述采访内容时大量使用间接引语。例如，一名官员在发布会上说 "We will increase the budget by 10% next year."，记者报道时写作：The official said that they would increase the budget by 10% **the following year**. 注意 will 后退为 would，next year 替换为 the following year。

**考试写作场景**：英语四六级和雅思写作中，转述他人观点时间接引语使用错误会直接扣分。常见题目要求："Some people argue that technology isolates us."——转述时不可写 "Some people argued that technology isolated us."（因为这是普遍观点而非特定时刻的言论，说话动词宜用现在时 argue，从句时态无需后退）。

**日常对话**：朋友传话场景中，"Tom said he would be late."（Tom 原话是 "I will be late."）是间接引语时态后退的典型口语用例，将来时 will 后退为 would。

---

## 常见误区

**误区一：过去时再后退为"更远的过去时"**
许多学习者误以为直接引语中的一般过去时（did）在间接引语中需要变为"过去的过去的过去时"，实际上过去完成时（had done）就是其后退目标，也是后退的终点。部分学生会将 had done 再次错误地写成 had been done 等形式，这是混淆了被动语态与时态后退概念导致的错误。

**误区二：客观事实也必须后退**
"The teacher said the earth was flat."（错误）与"The teacher said the earth is round."（正确）的区别在于：后者是公认的科学事实，转述时保留一般现在时 is 反而更准确。但这条规则不适用于个人观点或描述过去状态的陈述，不可滥用。

**误区三：say 和 tell 可以互换**
"She said me that she was tired."是典型错误——say 后不能直接接人称宾语。正确写法是 "She told me that she was tired." 或 "She said (to me) that she was tired."。这是间接引语中动词搭配的固定规则，与时态无关但同样影响句子正确性。

---

## 知识关联

间接引语的时态后退规则以**过去完成时（had done）**的理解为前提——学习者必须先掌握过去完成时的构成与含义，才能理解为何一般过去时后退后变为 had done，以及为何过去完成时在间接引语中不再继续后退。若对过去完成时的时间逻辑（"过去的过去"）不清晰，间接引语的时态后退表将无法正确运用。

进一步学习**间接引语进阶**时，将涉及疑问句转为间接引语的语序变化（疑问句语序→陈述句语序）、祈使句转间接引语（使用 tell/ask sb. to do 结构），以及感叹句的转述规则。这些内容共同构成英语转述语法的完整体系，而时态后退是贯穿所有类型间接引语的基础规则，不掌握本节内容将直接导致进阶练习中的大量语法错误。