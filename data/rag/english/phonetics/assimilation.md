---
id: "assimilation"
concept: "语音同化"
domain: "english"
subdomain: "phonetics"
subdomain_name: "语音"
difficulty: 5
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 语音同化

## 概述

语音同化（Assimilation）是指在连续语流中，相邻音素由于发音器官的惰性或协调性，互相影响而导致某个音素的发音特征向另一个音素靠拢甚至完全改变的现象。这种现象普遍存在于自然英语口语中，是母语者在正常语速下产生的自然生理结果，而非口音错误或发音懒散的表现。

语音同化现象在英语历史中早已有记录，许多现代英语词汇的拼写与发音差异本身就是历史同化过程固化的产物。例如古英语单词 *handbōc* 演变为现代英语 *handbook*，其中 /d/ 在 /b/ 前的弱化消失便是历史同化的痕迹。国际音标学会（IPA）在19世纪末系统化描述了同化现象，并将其分类纳入语音学分析框架。

同化现象对英语学习者至关重要，原因在于：不了解同化规则的学习者在听力中往往无法识别已发生音变的词语，在口语中则因逐词发音而听起来生硬机械。例如，当母语者说 "that person" 时，/t/ 受后续 /p/ 影响往往变为双唇音 [p]，整体听起来像 "thap person"，不熟悉此规则的学习者可能完全无法反应出这是 "that"。

---

## 核心原理

### 同化的方向：前向、后向与互向

语音同化按影响方向分为三类：

- **后向同化（Regressive Assimilation）**：后面的音影响前面的音，是英语中最常见的类型。例如 "in possible" → /ɪm ˈpɒsəbl/，/n/ 受双唇音 /p/ 影响，提前准备双唇闭合，变为双唇鼻音 /m/。
- **前向同化（Progressive Assimilation）**：前面的音影响后面的音。英语中典型案例是复数词尾 **-s** 的发音：/s/ 在清辅音后保持清辅音（cats /s/），在浊辅音或元音后变为浊辅音 /z/（dogs /z/）。
- **互向同化（Coalescent Assimilation）**：两个相邻音融合为一个全新的音。最典型的例子是 /t/ + /j/ → /tʃ/，如 "don't you" 在口语中变为 /doʊntʃu/；以及 /d/ + /j/ → /dʒ/，如 "did you" 变为 /dɪdʒu/。

### 发音部位同化（Place Assimilation）

发音部位同化是英语口语中频率最高的同化类型，指音素在**发音部位（place of articulation）**上向相邻音靠拢。核心规律如下：

- 齿槽音 /n, t, d/ 在双唇音 /p, b, m/ 前，转变为双唇音 /m, p, b/：
  - "ten minutes" → /tem ˈmɪnɪts/
  - "good morning" → /ɡʊb ˈmɔːnɪŋ/（/d/ → /b/）
- 齿槽音在软腭音 /k, ɡ/ 前，转变为软腭音 /ŋ, k, ɡ/：
  - "that car" → /ðæk kɑː/
  - "ten girls" → /teŋ ɡɜːlz/

### 发音方式同化：清浊同化

英语中浊辅音在清辅音前（或反之）会发生清浊同化。过去式词尾 **-ed** 的发音规则即为前向清浊同化的系统体现：
- /t/ 出现在清辅音后：walked /wɔːkt/、kissed /kɪst/
- /d/ 出现在浊辅音或元音后：played /pleɪd/、moved /muːvd/

此规则并非随机变化，而是英语构词形态学与语音同化共同作用的结果，适用于英语中绝大多数规则动词。

### 鼻音同化与 /n/ → /ŋ/ 变体

在非正式口语语速下，/n/ 在软腭音前系统性地变为 /ŋ/，这一现象甚至在单词内部也可观察到：
- "congress" 标准音为 /ˈkɒŋɡrəs/，其中 /n/ 已完全同化为 /ŋ/
- "income" 口语中常读作 /ˈɪŋkʌm/

---

## 实际应用

### 听力识别训练

在BBC新闻广播中，主持人说 "that person should" 时，/t/ + /p/ 的组合极可能产生 /p/ 同化，整句听来更像 "thap person should"。训练自己识别这类"缺失的齿槽音"是提升听力的关键步骤。剑桥英语听力教材（如 *English Pronunciation in Use* by Mark Hancock）专门将同化列为B2至C1阶段的重点训练内容。

### 口语流利度提升

在演讲或雅思口语考试中，考生若能在以下常见词组中主动使用同化，将显著提升语音自然度：
- "Would you like…" → /wʊdʒə laɪk/（/d/+/j/ 互向同化为 /dʒ/）
- "I'm not going to" → /aɪm nɒ ɡənə/（/t/ 在软腭音前弱化并同化）
- "sandwich" 的标准英音本身已是 /ˈsæmwɪtʃ/，/n/ 被 /w/ 影响同化为 /m/

### 词汇层面的固化同化

部分词汇的拼写已记录了历史同化的结果，例如：
- "impossible"（im- 而非 in-）：/n/ 在 /p/ 前完全同化为 /m/
- "immobile"、"irregular"：前缀 in- 在不同辅音前产生不同同化形式

---

## 常见误区

### 误区一：同化是懒惰发音，不应模仿

许多学习者认为同化是不标准的口语习惯，在考试或正式场合应避免。这是错误的。语言学研究（如 Gimson's Pronunciation of English，第8版）明确指出，同化是英语语音系统的内在属性，受过良好教育的母语者在自然语速下同样会大量使用。刻意避免同化反而会导致发音过于僵硬，影响流利度评分。

### 误区二：/t/+/j/ 和 /d/+/j/ 的互向同化在任何语速下都发生

实际上，互向同化（coalescent assimilation）具有语速敏感性。在慢速或强调语境中，"did you" 可以清晰地保留 /d/ 和 /j/ 分别发音；只有在正常或较快的连读语速下，融合为 /dʒ/ 才是自然的。将所有语速一律同化处理，反而会造成语义模糊或显得过于随意。

### 误区三：同化规则等同于省音规则

语音同化（Assimilation）与省音（Elision）是不同的音变过程：省音是某个音素**完全消失**（如 "next day" 中 /t/ 脱落），而同化是某个音素**改变特征但仍然存在**（如 /n/ → /m/）。将两者混淆会导致学习者在描述和练习音变时方向错误。

---

## 知识关联

语音同化建立在**弱化与省音**（Weakening & Elision）的基础之上。省音处理的是连读中音素消失的情形，而同化则进一步解释了音素不消失时如何发生质变。两者共同构成英语连读语音变化的完整图景：省音减少音段数量，同化改变音段特征。

学习者在掌握同化规律后，应将其与**连读（Liaison）**和**节奏单元（Tone Unit）**的知识结合使用，才能真正理解自然英语口语中音节边界模糊、词义依赖语境的深层原因。对于希望进一步深入的学习者，Daniel Jones 的《英语发音词典》（English Pronouncing Dictionary）和 Peter Roach 的 *English Phonetics and Phonology* 均提供了详细的同化音标注记体系，可作为进阶参考。
