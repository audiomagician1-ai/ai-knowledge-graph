---
id: "authors-purpose"
concept: "作者目的"
domain: "english"
subdomain: "reading"
subdomain_name: "阅读理解"
difficulty: 4
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-03-30
---

# 作者目的

## 概述

作者目的（Author's Purpose）是英语阅读理解中的一类核心题型，要求读者判断作者撰写某段文字或整篇文章的根本意图，以及作者对所讨论话题持有的态度立场。这类题目不同于字面理解，它要求读者超越表层文字，分析作者为何写作、为何选择特定措辞、以及希望读者产生何种反应。

历史上，作者目的分析框架最早在20世纪60年代的英语教育研究中被系统化，美国学者将其归纳为经典的"PIE"模型——**P**ersuade（说服）、**I**nform（告知）、**E**ntertain（娱乐）。这三类目的覆盖了绝大多数英语阅读材料的写作动机，至今仍是英语阅读教学中判断作者目的的基础框架。

在高考、托福、GRE等标准化考试中，作者目的题通常以"The main purpose of the passage is to..."或"The author writes this paragraph in order to..."的形式出现，占阅读理解总分的10%–20%。这类题目得分率普遍低于细节题，原因在于学生往往误将文章的主题内容当作写作目的，而忽略了作者的写作动机与态度层面的信息。

---

## 核心原理

### PIE框架的具体区分

**Persuade（说服）** 型文章的语言特征最为鲜明：作者会大量使用情感性词汇（如"urgent"、"critical"、"must"），以及一边倒的论证结构——只呈现支持自身立场的证据，刻意弱化或反驳对立观点。例如一篇关于禁止塑料袋的评论文章，若作者仅列举塑料袋的危害而不讨论其便利性，则目的指向说服。

**Inform（告知）** 型文章追求客观中立，作者使用被动语态、数据引用、专家引述来呈现事实。典型特征是段落以"Research shows..."或"According to..."开头，不含情感判断词汇。科普文章、新闻报道、百科条目通常属于此类。

**Entertain（娱乐）** 型文章以叙事性语言、幽默手法、生动描写为主。作者目的是让读者产生愉悦感或情感共鸣，而非传递特定知识或改变读者行为。短篇故事、旅游游记、幽默专栏均属此类。

部分学者将PIE扩展为PIEED，增加了**Explain（解释）**与**Describe（描述）**两类，用于区分机制解析型文章（如"How does the heart work?"）与场景描写型文章。

### 作者态度的识别方法

作者态度（Author's Attitude/Tone）是目的判断的重要辅助维度，常见态度词汇包含：
- **正面态度**：admiring, supportive, optimistic, enthusiastic
- **负面态度**：critical, skeptical, cynical, dismissive
- **中立态度**：objective, impartial, detached, neutral

识别态度的关键技术是**情感词汇密度分析**：统计文章中正面情感词与负面情感词的比例，并注意反语（irony）的使用——当作者表面赞扬实则批评时，字面词汇方向与真实态度相反。例如，"What a brilliant solution that turned out to be"若出现在描述一项失败政策的段落中，则为反语。

### 段落级别与全文级别的目的区分

同一篇文章中，全文目的与局部段落目的可能不同。例如，一篇整体目的为**说服**读者支持环保政策的文章，其中某一段落可能临时转换为**告知**功能（提供污染数据作为论据支撑）。考试中，若题目问"The author mentions the statistic in paragraph 3 in order to..."，则需判断该**段落局部功能**，而非全文目的。这种全文-局部目的的两层结构是作者目的题的高难度变体，在GRE阅读中尤为常见。

---

## 实际应用

**场景一：高考英语阅读C、D篇**

高考阅读中，作者目的题通常出现在说明文或议论文的末尾。例如，若一篇文章描述了青少年过度使用社交媒体的现象，并在结尾段落呼吁家长与学校采取干预措施，则正确答案应选"to persuade readers to take action"，而非"to describe how teenagers use social media"（描述功能仅是手段，不是最终目的）。

**场景二：托福阅读中的修辞目的题（Rhetorical Purpose）**

托福阅读第3–5题常为"Why does the author mention X in paragraph 2?"此类题要求判断某一例子或数据被引入的修辞功能，选项通常为：to illustrate（举例说明）、to contrast（对比）、to support（支持论点）、to challenge（质疑假设）。答对此类题的关键是先定位该段落的**核心论点**，再判断被提问的内容是如何服务于该论点的。

**场景三：GRE短文章目的判断**

GRE中，作者目的题的干扰项极具迷惑性，常以"to compare X and Y"代替"to argue that X is superior to Y"。区分两者的技巧在于：若文章比较了X与Y但明确偏向一方，则目的是"argue"而非"compare"。

---

## 常见误区

**误区一：将文章主题等同于写作目的**

最高频的错误是用"to discuss/introduce/describe X"来回答目的题。一篇讨论气候变化的文章，其主题是气候变化，但写作目的可能是"to persuade governments to adopt carbon taxes"。主题回答了"写了什么"，目的回答了"为什么写"，二者不可混淆。

**误区二：忽视反语和修辞手法导致态度判断错误**

学生在判断作者态度时，常对含有反语的句子做出字面判断。若作者写"Clearly, ignoring scientific evidence is a wonderful strategy for success"，字面为正面，实际为强烈批评。识别反语的方法是检查上下文语境——若周围段落均表达负面评价，则该句很可能使用了反语。

**误区三：混淆主要目的与次要目的**

一篇文章可能同时具有"告知"和"说服"两种功能，但题目要求判断**主要**目的。区分的方法是：查看文章结构中哪一功能占用了更多篇幅，以及文章**开头与结尾**的语气——开头引入和结尾总结最能体现作者的根本意图。若结尾段发出行动号召（call to action），则主要目的为说服，不论文章中间提供了多少客观信息。

---

## 知识关联

作者目的的判断建立在**推断**能力的基础之上：读者必须先能从字里行间推断隐含信息，才能进一步判断这些信息背后的写作动机。若推断能力不足，面对含蓄表达的说服型文章，学生只能停留在"此文在描述现象"的表层理解，而无法识别作者的真实意图。

掌握作者目的之后，学生将进入**语气与情感**的深度学习。语气（Tone）是作者目的在文字层面的具体体现——作者选择讽刺性语气（satirical tone）是实现批评目的的手段，选择激励性语气（inspirational tone）是实现说服目的的工具。作者目的是宏观的"为何写"，语气与情感是微观的"如何写"，两个概念在阅读分析中构成目的-手段关系，共同服务于对文本意图的完整解读。