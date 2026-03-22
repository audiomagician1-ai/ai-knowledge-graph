---
id: "sentence-structure"
concept: "句子结构"
domain: "writing"
subdomain: "writing-fundamentals"
subdomain_name: "写作基础"
difficulty: 1
is_milestone: false
tags: ["结构", "句法"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Williams & Bizup, Style: Lessons in Clarity and Grace, 13th ed."
  - type: "textbook"
    name: "Kolln & Gray, Rhetorical Grammar, 8th ed."
scorer_version: "scorer-v2.0"
---
# 句子结构

## 定义与核心概念

句子结构（Sentence Structure）是词语按照语法规则组织成有意义表达单元的方式。Kolln & Gray 在《Rhetorical Grammar》（8th ed.）中将句子定义为包含**主语**和**谓语**、表达完整思想的语法单位。

句子结构的核心矛盾：语法正确性（Grammaticality）与修辞有效性（Rhetorical Effectiveness）并不等同。一个语法完美的句子可能晦涩难懂，而一个"违规"的句子片段可能极具表现力。

## 四种基本句型

| 句型 | 结构 | 功能 | 示例 |
|------|------|------|------|
| **简单句** | 1个独立子句 | 清晰直接 | The experiment failed. |
| **并列句** | 2+独立子句 (连词连接) | 并列等重信息 | The experiment failed, but the data was valuable. |
| **复杂句** | 1个独立 + 1+从属子句 | 表达主次关系 | Although the experiment failed, the data proved valuable. |
| **并列复杂句** | 2+独立 + 1+从属子句 | 表达复杂关系 | Although the experiment failed, the data proved valuable, and the team redesigned the protocol. |

### 从属子句的三种类型

| 类型 | 引导词 | 功能 | 示例 |
|------|--------|------|------|
| 名词性从句 | that, what, whether | 充当主/宾语 | **What he said** surprised us. |
| 形容词性从句 | who, which, that | 修饰名词 | The book **that you recommended** is excellent. |
| 副词性从句 | because, although, when, if | 修饰动词/句 | **Because it rained**, we stayed inside. |

## 信息分布原则

### 已知-新信息原则（Given-New Contract）

Williams（*Style*, 13th ed.）的核心教学：将**旧信息**放在句首，**新信息**放在句尾——句尾是英语句子的"压力位"（Stress Position）。

```
✗ A remarkable innovation in AI was announced by Google yesterday.
  (新信息"remarkable innovation"在句首，旧信息"Google"在句尾)

✓ Google yesterday announced a remarkable innovation in AI.
  (旧信息"Google"在句首，新信息"remarkable innovation"在句尾)
```

### 句子重心（End Focus）

句尾放置最重要的新信息：

```
✗ Einstein published his theory of relativity, which transformed physics, in 1905.
✓ In 1905, Einstein published his theory of relativity, which transformed physics.
```

### 主语-动词距离

读者处理句子时，需要将主语保持在工作记忆中直到遇到动词。主语和动词之间的距离不宜超过 **7-10 个单词**（Miller 的工作记忆容量，约 7±2 个组块）。

```
✗ The proposal that the committee reviewing the budget submitted to the board in 
  the third quarter of the fiscal year was rejected.
  （主语"proposal"到动词"was rejected"间隔 20+ 词）

✓ The committee's budget proposal was rejected by the board in Q3.
  （主语"proposal"到动词"was rejected"间隔 0 词）
```

## 句子长度与节奏

### 经验数据

| 写作类型 | 平均句长(词) | 建议范围 | 数据来源 |
|---------|-----------|---------|---------|
| 学术论文 | 22-28 | 15-35 | APA样本分析 |
| 新闻报道 | 16-20 | 10-25 | AP Stylebook |
| 技术文档 | 15-20 | 10-25 | Microsoft Style Guide |
| 小说 | 12-18 | 高度变化 | 文学风格分析 |

### 长短交替创造节奏

```
海明威式节奏（主要短句 + 偶尔长句）：
"He was an old man. He fished alone in a skiff in the Gulf Stream, 
and he had gone eighty-four days now without taking a fish."
（4词 → 22词 → 对比节奏）

Faulkner式节奏（长句为主，内嵌多层结构）：
适用于意识流、复杂思维表达
```

## 常见句子问题诊断

### 1. 名词化堆积（Nominalization）

```
✗ The implementation of the optimization of the algorithm
  resulted in the improvement of performance.
  （4个名词化：implementation, optimization, improvement, performance-as-subject）

✓ Optimizing the algorithm improved its performance.
  （动词还原：implement→直接动作, optimization→optimizing, improvement→improved）
```

Williams 的规则：如果一个名词可以还原为动词而使句子更清晰 → 还原。

### 2. 被动语态的适当使用

被动语态不是错误，而是工具：

| 场景 | 推荐语态 | 理由 |
|------|---------|------|
| 行为者重要 | 主动 | "Researchers discovered..." |
| 行为者不重要/未知 | 被动 | "The compound was synthesized..." |
| 维持主位连贯 | 被动 | 保持句间话题一致 |
| 科学方法描述 | 被动 | 学科惯例（但趋势在变） |

### 3. 悬垂修饰语（Dangling Modifier）

```
✗ Walking through the park, the trees were beautiful.
  （"walking"的逻辑主语是人，语法主语却是"trees"）

✓ Walking through the park, I found the trees beautiful.
  （主语"I"与分词一致）
```

### 4. 平行结构（Parallelism）

```
✗ The system must be fast, reliable, and have good scalability.
  （adj, adj, verb phrase — 不平行）

✓ The system must be fast, reliable, and scalable.
  （adj, adj, adj — 平行）

✓ The system must run fast, respond reliably, and scale efficiently.
  （verb+adv × 3 — 平行）
```

## 参考文献

- Williams, J.M. & Bizup, J. (2017). *Style: Lessons in Clarity and Grace*, 13th ed. Pearson. ISBN 978-0134080413
- Kolln, M. & Gray, L. (2017). *Rhetorical Grammar: Grammatical Choices, Rhetorical Effects*, 8th ed. Pearson. ISBN 978-0134080413
- Pinker, S. (2014). *The Sense of Style*. Viking. ISBN 978-0670025855

## 教学路径

**前置知识**：基本语法概念（主谓宾、词性）
**学习建议**：先能识别和写出四种基本句型（各写 5 个），再练习"已知-新信息"排列。日常练习：对自己写的每个段落，检查(1)主语-动词距离，(2)名词化是否可还原，(3)句末是否放了最重要的信息。
**进阶方向**：修辞句式（排比、对偶、设问）、跨语言句法对比（英-中主题突出 vs 主语突出）。
