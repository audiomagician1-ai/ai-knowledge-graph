---
id: "cohesion-coherence"
concept: "衔接与连贯"
domain: "english"
subdomain: "reading"
subdomain_name: "阅读理解"
difficulty: 5
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.5
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.379
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 衔接与连贯

## 概述

衔接（Cohesion）与连贯（Coherence）是英语篇章分析中两个互补的维度。衔接指句子之间通过显性语言手段（如代词、连接词、词汇重复）建立的形式上的联系；连贯则指读者在理解篇章时感知到的语义逻辑的统一性。Halliday 与 Hasan 在其1976年的经典著作《英语中的衔接》（*Cohesion in English*）中首次系统提出了这一理论框架，将衔接手段分为五大类：指代（Reference）、替代（Substitution）、省略（Ellipsis）、连接（Conjunction）、词汇衔接（Lexical Cohesion）。

在阅读理解题目中，考查衔接与连贯的题型主要包括：代词指代判断（"the pronoun 'it' in line 3 refers to..."）、逻辑连接词填空、句子插入位置判断等。对这两个概念的掌握直接影响考生能否准确理解长难句中跨句的语义关系，尤其是在SAT、GRE、托福等标准化考试的阅读与写作部分。

## 核心原理

### 代词指代（Pronominal Reference）

代词指代是衔接中最高频的考点。英语中人称代词（he/she/it/they）、指示代词（this/that/these/those）和关系代词（which/who/that）通过"回指"（Anaphora）将后文锚定到前文已出现的名词短语。解题时需定位代词出现的位置，向前追溯最近的名词性先行词，并用回代法验证——即把找到的先行词替换代词放入原句，看语义是否通顺。

例如在句子 *"Scientists discovered a new enzyme. It breaks down plastic at room temperature."* 中，`It` 回指 `a new enzyme`，而非 `Scientists`，因为主语位置的 `Scientists` 是有生命的人，与 `breaks down plastic` 的语义搭配不符。注意：当段落中存在多个候选先行词时，语义相容性优先于位置邻近原则。

### 连接词的逻辑关系（Conjunctive Cohesion）

连接词按逻辑关系可分为四大类：
- **加合（Additive）**：furthermore, moreover, in addition — 表示信息叠加
- **转折（Adversative）**：however, nevertheless, yet — 表示语义对立
- **因果（Causal）**：therefore, consequently, hence — 表示推理结论
- **时序（Temporal）**：subsequently, meanwhile, thereafter — 表示时间顺序

在句子插入题中，判断插入位置的关键是识别空格前后的逻辑关系。若前句陈述一个现象，后句用 `This suggests that...` 开头，则插入句必须提供可供 `This` 回指的具体事实。转折词 `however` 出现时，前后两句的命题内容必须形成可识别的语义对立，否则该位置不成立。

### 词汇衔接（Lexical Cohesion）

词汇衔接通过两种机制实现：**复现（Reiteration）** 和 **同现（Collocation）**。

复现包含四个层次：
1. 原词重复（repetition）：同一词形反复出现
2. 同义词替换（synonym）：如 `scientist` → `researcher`
3. 上义词替换（superordinate）：如 `rose` → `flower`
4. 概括词（general word）：如 `thing`, `matter`, `fact`

同现指在同一语义场中频繁共现的词汇群，例如描述经济衰退的文本中，`recession`、`unemployment`、`deflation`、`fiscal`会形成语义网络，帮助读者识别篇章的主题域。在阅读理解中，识别词汇衔接链（lexical chain）有助于快速定位段落主旨，因为词汇复现密度最高的语义场往往对应文章的核心论点。

## 实际应用

**场景一：代词指代判断题**
题目给出段落：*"The committee rejected the proposal because they believed it was too costly."* 问 `it` 指代什么。答案为 `the proposal`（不是 `the committee`，因为 `costly` 描述方案而非委员会）。

**场景二：六选五句子插入题（SAT Writing）**
原段落末句为：*"Early vaccines required refrigeration, limiting their use in remote areas."* 备选插入句为：*"However, newer formulations remain stable at 40°C for up to six months."* 插入合理，因为 `However` 正确标注了"旧疫苗需冷藏"与"新配方耐热"之间的转折对立关系，且 `newer formulations` 与 `Early vaccines` 形成时间上的对比词汇衔接。

**场景三：词汇衔接识别主旨**
一段文字反复出现 `carbon emissions`、`atmospheric concentration`、`fossil fuels`、`greenhouse effect`，即使没有显性主题句，读者也能通过这条词汇衔接链判断段落主题为气候变化的成因，而非气候变化的解决方案。

## 常见误区

**误区一：代词指代只取最近的名词**
许多学生默认代词指代位置上最近的名词，但英语的指代遵循"语义最优先"原则。在 *"The bacteria infected the host cells; then they multiplied rapidly."* 中，`they` 指 `bacteria` 而非 `host cells`，因为细菌具有自主增殖的语义属性，而宿主细胞在此语境中是被动受体。单纯依据位置邻近会选出错误答案。

**误区二：连接词决定衔接，没有连接词就没有连贯**
衔接（显性手段）与连贯（语义逻辑）可以分离。学术文章中大量存在"零连接"（zero conjunction）段落，即相邻句子之间没有任何连接词，但读者依然通过词汇衔接和背景知识感知到连贯性。反之，连接词使用错误（如将因果关系误标为转折）会破坏连贯，即使句子在语法上完全正确。

**误区三：上义词替换必然是衔接手段**
只有当上义词在具体语境中指代已知个体时，才构成衔接。*"A robin flew past. The bird landed on the fence."* 中，`The bird` 是衔接手段。但 *"Birds migrate seasonally. Robins are a typical example."* 中，`Robins` 并非 `Birds` 的回指，而是例证关系，属于篇章结构手段而非词汇衔接。

## 知识关联

学习衔接与连贯需要以**篇章结构**知识为基础：理解段落的论点—支撑—例证三层结构，才能判断某个连接词是否在正确的逻辑位置出现。例如，`for instance` 只能出现在从一般陈述过渡到具体案例的位置，若前句已经是具体数据，再用 `for instance` 引出另一数据则破坏连贯。

向前延伸，掌握衔接与连贯后可直接进入**学术文章阅读**的训练。学术语篇大量使用名词化（nominalization）构成词汇衔接链，如将动词 `argue` 转化为名词 `the argument`，再被 `this claim` 替代，形成跨段落的指代链；若无法追踪这类抽象名词的指代关系，将无法理解学术文章的论证走向。同时，衔接手段的显性分析也为**连贯与过渡**的写作训练提供了可操作的检查框架——学生可以通过统计自己作文中的词汇衔接链密度和连接词分布，诊断段落连贯性问题。