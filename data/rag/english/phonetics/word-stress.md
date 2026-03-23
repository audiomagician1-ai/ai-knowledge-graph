---
id: "word-stress"
concept: "单词重音"
domain: "english"
subdomain: "phonetics"
subdomain_name: "语音"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 单词重音

## 概述

单词重音（Word Stress）是指在多音节英语单词中，某一特定音节以更大的气流、更高的音调、更长的时值和更强的肌肉张力发音的语音现象。与汉语的声调系统不同，英语重音是以**音节为单位**的相对突显，而非整个词的音高走势。英语重音的标注约定可追溯至19世纪末的比较语言学传统，现代标注体系由国际语音学协会（IPA）于1888年建立，其中重音符号"ˈ"（主重音）和"ˌ"（次重音）置于重读音节**之前**，例如 /ˈpɪktʃər/（picture）和 /ˌɪntəˈnæʃənl/（international）。

英语单词重音之所以在语音习得中占据特殊地位，是因为它直接影响元音质量：非重读音节的元音往往弱化为央元音/ə/（schwa），例如单词 "photograph" /ˈfəʊtəɡrɑːf/ 中第二、三音节均弱化，而 "photography" /fəˈtɒɡrəfi/ 中重音转移后第一音节亦发生弱化。据 [Roach, 2009] 在 *English Phonetics and Phonology* 中的统计，英语中约有95%的双音节名词和形容词重音落在第一音节，这一规律对初学者识别陌生词汇的发音有重要指导意义。

## 核心原理

### 重音判断的音节强弱规则

重音的分配与音节的"重量"（syllable weight）密切相关。语言学上将只含短元音且无尾辅音的音节称为"轻音节"（light syllable），含长元音、双元音或以辅音收尾的音节称为"重音节"（heavy syllable）。英语重音偏向于落在重音节上的倾向被称为**重音敏感性**（stress-sensitivity）。以三音节词为例：

- "ba·NA·na" /bəˈnɑːnə/：第二音节含长元音 /ɑː/，为重音节，故主重音落于第二音节。
- "CHA·rac·ter" /ˈkærəktər/：第一音节含短元音但处于词首封闭音节，依据英语词汇重音偏好规则，重音落于第一音节。

[Giegerich, 1992] 在 *English Phonology: An Introduction* 中系统论证了英语重音分配受到**词汇阶层**（lexical stratum）影响：源自拉丁语/法语的词汇（如 -tion, -ic, -ity 后缀词）遵循后缀主导的重音规则，而源自日耳曼语的本族词汇（如 "kingdom", "handsome"）则普遍保持第一音节重读。

### 后缀决定型重音规则

英语派生词的重音位置常由后缀决定，可归纳为以下三类：

**①重音前移型后缀**（stress-attracting suffixes）：后缀直接吸引主重音至其前一音节。

| 后缀 | 示例 | 重音位置 |
|------|------|----------|
| -tion / -sion | pho·TO·gra·phy → pho·to·GRA·phic | 倒数第二音节 |
| -ic / -ical | e·CO·no·my → e·co·NO·mic | 倒数第二音节 |
| -ity | pos·SI·bi·li·ty | 倒数第三音节 |

**②重音固定型后缀**（stress-neutral suffixes）：不改变词根的重音位置，如 -ness, -ful, -less, -ment（"hap·py" → "HAP·pi·ness"）。

**③后缀本身承担重音**（stress-bearing suffixes）：如 -eer（en·gi·NEER）、-esque（pic·tu·RESQUE）、-ette（cig·a·RETTE）。

### 名词与动词的重音对立

英语中约有130对同形异音的名/动词对（noun-verb minimal pairs），其重音分布规律为：**双音节名词倾向于第一音节重读，同形动词则倾向于第二音节重读**。这一规律可用简化公式表示：

$$\text{名词}: \acute{\sigma}\sigma \quad \text{动词}: \sigma\acute{\sigma}$$

典型例证包括：

- "REcord"（名词，记录）vs. "reCORD"（动词，录制）
- "CONtent"（名词，内容）vs. "conTENT"（动词，使满足）
- "PERmit"（名词，许可证）vs. "perMIT"（动词，允许）
- "OBject"（名词，物体）vs. "obJECT"（动词，反对）

该规律亦适用于部分名词/形容词对，如 "PREsent"（名词/形容词）vs. "preSENT"（动词）。

## 实际应用

### 词典标注与发音学习

英式词典（如《牛津高阶英汉双解词典》第10版）和美式词典（如 *Merriam-Webster's Collegiate Dictionary*）均采用IPA重音符号标注。学习者可通过以下方法训练：在听写时先判断音节数量，再依据后缀规则预测重音位置，最后核对词典标注。研究显示，使用重音感知训练（stress perception training）的学习者在6周内单词识别准确率可提升约23%（Juffs, 1990）。

### 语音合成与NLP中的重音模型

在自然语言处理（NLP）和文字转语音（TTS）系统中，单词重音预测是关键步骤。以Python为例，可调用CMU发音词典（CMUdict）获取重音信息：

```python
import nltk
nltk.download('cmudict')
from nltk.corpus import cmudict

d = cmudict.dict()

def get_stress(word):
    """返回单词每个音素的重音标记（0=无重音, 1=主重音, 2=次重音）"""
    if word.lower() in d:
        phonemes = d[word.lower()][0]
        return [(p, p[-1]) for p in phonemes if p[-1].isdigit()]
    return None

print(get_stress("photograph"))
# 输出: [('F', ''), ('OW1', '1'), ('T', ''), ('AH0', '0'), ('G', ''), ('R', ''), ('AE2', '2'), ('F', '')]
# OW1 = 主重音, AH0 = 无重音, AE2 = 次重音
```

CMUdict 用数字 0/1/2 附于元音音素之后标注重音等级，这种编码方式被现代语音引擎（如 Festival、Flite）广泛采用。

### 课堂教学中的重音节律训练

教师常用"重音节拍法"（stress-timed rhythm method）：用手拍打桌面标记主重音音节，配合橡皮筋拉伸模拟音节延长。以"international"为例，拍打节奏为：in·ter·**NA**·tion·al，学生能直观感受第三音节的突出程度。英语属于**重音计时语言**（stress-timed language），不同于音节计时语言（syllable-timed language，如法语、普通话），这意味着两个主重音之间的时长趋于相等，无论其间包含几个弱化音节。

## 常见误区

### 误区一：以为重音等于"读重一点"

许多学习者认为只需要加大音量即可体现重音，实际上英语重音是**四维综合**的：更高的基础音调（pitch）、更长的音节时值（duration）、更大的共鸣（sonority）以及更清晰的元音音色（vowel quality）。单纯提高音量而不改变音调和时值，在英语母语者听来仍属非重读音节，甚至造成语义混淆。例如，仅靠音量无法区分 "INsult"（名词）和 "inSULT"（动词）。

### 误区二：把汉语声调规则迁移至英语重音

以普通话为母语的学习者常将英语重读音节与普通话第一声（高平调）对应，导致重读音节全部上扬却无法区分主次重音。实际上，英语主重音的音调走势因**语调**（intonation）而变化：在陈述句末尾，重读音节通常下降；在疑问句末尾则上升。重音本身是**词汇固有属性**（lexically specified），不因句子类型而改变落点，只是叠加在不同语调曲线之上。

### 误区三：认为所有双音节词重音都在第一音节

虽然95%的双音节**名词**重音在第一音节，但双音节**动词**约有60-65%的重音在第二音节（如 "begin", "decide", "forget", "allow"）。此外，借自法语的词汇（如 "café", "ballet", "fiancée"）保留了原语言末音节重读的特征；以 be-, re-, de-, pre- 开头的非重读前缀词（如 "beHAVE", "reTURN"）也普遍第二音节重读。将"双音节词一律第一音节重读"奉为通则，会导致大量常见动词和借词发音错误。

## 思考题

1. 单词 "protest" 在句子 "The workers held a **pro**test"（名词）和 "The workers **pro**tested against the decision"（动词）中重音位置是否相同？请用IPA符号分别标出两个词的重音，并解释为什么动词形式加了 -ed 后缀仍保持与名词不同的重音。

2. 以下三个词 "PHOtograph"、"phoTOgraphy"、"photoGRAPHic" 构成一个重音位移链。请分析各词所使用的后缀（-y 和 -ic），说明它们分别属于哪类重音控制型后缀，并据此预测 "photograph·er" 的重音位置，核对词典后反思规则的预测准确性。

3. 英语属于重音计时语言，而重音计时性要求弱读音节压缩。请录制自己朗读句子 "The **CAT** sat on the **MAT**" 和 "The **CAT** was sitting on the **MAT**" 的音频，测量两句中第一个重读音节（CAT）到第二个重读音节（MAT）之间的时长，验证重音计时假说是否在你的发音中成立。
