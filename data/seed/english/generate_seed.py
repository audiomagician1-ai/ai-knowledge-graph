#!/usr/bin/env python3
"""Generate English Knowledge Sphere seed graph.

~200 concepts, ~280 edges, 10 subdomains, ~20 milestones.
Covers phonetics through advanced writing/speaking for English learners.

Usage:
    python generate_seed.py          # writes seed_graph.json
    python generate_seed.py --verify # also runs integrity checks
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc).isoformat()

DOMAIN = {
    "id": "english",
    "name": "英语",
    "description": "从基础语法到高级表达的英语学习体系",
    "icon": "🟡",
    "color": "#eab308",
}

SUBDOMAINS = [
    {"id": "phonetics",         "name": "语音",       "order": 1},
    {"id": "basic-grammar",     "name": "基础语法",   "order": 2},
    {"id": "vocabulary",        "name": "核心词汇",   "order": 3},
    {"id": "tenses",            "name": "时态系统",   "order": 4},
    {"id": "sentence-patterns", "name": "句型结构",   "order": 5},
    {"id": "advanced-grammar",  "name": "高级语法",   "order": 6},
    {"id": "reading",           "name": "阅读理解",   "order": 7},
    {"id": "writing-en",        "name": "写作",       "order": 8},
    {"id": "speaking",          "name": "口语表达",   "order": 9},
    {"id": "idioms-culture",    "name": "习语与文化", "order": 10},
]

# fmt: off
CONCEPTS = [
    # ── phonetics (20 concepts) ──
    {"id": "vowel-sounds",          "name": "元音音素",         "desc": "英语12个单元音和8个双元音",                    "sub": "phonetics", "diff": 2, "type": "theory",   "tags": ["基础"], "ms": False},
    {"id": "consonant-sounds",      "name": "辅音音素",         "desc": "英语24个辅音音素的发音位置和方式",              "sub": "phonetics", "diff": 2, "type": "theory",   "tags": ["基础"], "ms": False},
    {"id": "ipa-basics",            "name": "国际音标基础",     "desc": "IPA符号系统与英语音素对应关系",                 "sub": "phonetics", "diff": 3, "type": "theory",   "tags": ["基础"], "ms": True},
    {"id": "syllable-structure",    "name": "音节结构",         "desc": "音节的构成:起首辅音、元音核心、尾辅音",         "sub": "phonetics", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "word-stress",           "name": "单词重音",         "desc": "英语单词的重音规则与标注",                      "sub": "phonetics", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "sentence-stress",       "name": "句子重音",         "desc": "内容词与功能词的重读/弱读规则",                 "sub": "phonetics", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "intonation-patterns",   "name": "语调模式",         "desc": "升调、降调、降升调的意义与使用",                "sub": "phonetics", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "linking-sounds",        "name": "连读",             "desc": "辅音与元音的连读、同辅音连读",                  "sub": "phonetics", "diff": 4, "type": "practice", "tags": ["进阶"], "ms": False},
    {"id": "reduction-elision",     "name": "弱化与省音",       "desc": "弱读形式、音素省略现象",                        "sub": "phonetics", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "minimal-pairs",         "name": "最小对立体",       "desc": "通过最小差异词对辨别音素",                      "sub": "phonetics", "diff": 3, "type": "practice", "tags": ["练习"], "ms": False},
    {"id": "phonics-rules",         "name": "自然拼读规则",     "desc": "字母与音素的对应关系规则",                      "sub": "phonetics", "diff": 2, "type": "theory",   "tags": ["基础"], "ms": False},
    {"id": "schwa-sound",           "name": "中央元音schwa",    "desc": "最常见英语元音/ə/的出现规律",                   "sub": "phonetics", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "consonant-clusters",    "name": "辅音丛",           "desc": "词首和词尾的辅音组合",                          "sub": "phonetics", "diff": 4, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "rhythm-timing",         "name": "节奏与语速",       "desc": "英语的重音等时性节奏特征",                      "sub": "phonetics", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "am-vs-br-pronunciation","name": "美音与英音差异",   "desc": "美式和英式英语的主要发音区别",                  "sub": "phonetics", "diff": 4, "type": "theory",   "tags": ["拓展"], "ms": False},
    {"id": "tongue-twisters",       "name": "绕口令练习",       "desc": "通过绕口令训练难发音组合",                      "sub": "phonetics", "diff": 3, "type": "practice", "tags": ["趣味"], "ms": False},
    {"id": "assimilation",          "name": "语音同化",         "desc": "相邻音素互相影响改变发音",                      "sub": "phonetics", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "thought-groups",        "name": "意群划分",         "desc": "句子按意义分组停顿的规律",                      "sub": "phonetics", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "pronunciation-practice","name": "发音综合练习",     "desc": "系统性发音训练方法与自我纠正",                  "sub": "phonetics", "diff": 4, "type": "practice", "tags": ["练习"], "ms": False},
    {"id": "phonemic-transcription","name": "音标转写",         "desc": "将单词转写为IPA音标的练习",                     "sub": "phonetics", "diff": 4, "type": "practice", "tags": ["练习"], "ms": False},

    # ── basic-grammar (22 concepts) ──
    {"id": "parts-of-speech",       "name": "词性概述",         "desc": "名词、动词、形容词等八大词性",                  "sub": "basic-grammar", "diff": 1, "type": "theory", "tags": ["基础"], "ms": True},
    {"id": "nouns",                 "name": "名词",             "desc": "可数/不可数名词、单复数变化",                   "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "pronouns",              "name": "代词",             "desc": "人称/物主/指示/反身代词",                       "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "articles",              "name": "冠词",             "desc": "a/an/the的使用规则与零冠词",                    "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "adjectives",            "name": "形容词",           "desc": "形容词的用法、比较级和最高级",                  "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "adverbs",               "name": "副词",             "desc": "副词的类型、位置与比较等级",                    "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "prepositions",          "name": "介词",             "desc": "时间/地点/方向介词与固定搭配",                  "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "conjunctions",          "name": "连词",             "desc": "并列连词和从属连词",                            "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "basic-sentence-order",  "name": "基本语序",         "desc": "SVO语序与句子基本结构",                         "sub": "basic-grammar", "diff": 1, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "be-verb",               "name": "be动词",           "desc": "am/is/are/was/were的用法",                      "sub": "basic-grammar", "diff": 1, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "have-do-auxiliary",     "name": "助动词have/do",    "desc": "have和do作为助动词的用法",                      "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "modal-verbs",           "name": "情态动词",         "desc": "can/could/may/might/must/should等",             "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": True},
    {"id": "questions",             "name": "疑问句",           "desc": "一般疑问句、特殊疑问句、选择疑问句",            "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "negation",              "name": "否定句",           "desc": "not的用法、双重否定、否定前缀",                 "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "imperative",            "name": "祈使句",           "desc": "命令、请求、建议的祈使表达",                    "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "exclamatory",           "name": "感叹句",           "desc": "what/how引导的感叹句结构",                      "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "there-be",              "name": "there be句型",     "desc": "存在句的结构与主谓一致",                        "sub": "basic-grammar", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "it-usage",              "name": "it的用法",         "desc": "形式主语it、强调句、天气/时间表达",             "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "possessives",           "name": "所有格",           "desc": "'s所有格、of所有格、双重所有格",                "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "quantifiers",           "name": "数量词",           "desc": "some/any/many/much/few/little等",               "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "determiners",           "name": "限定词",           "desc": "this/that/these/those/each/every等",            "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "subject-verb-agreement","name": "主谓一致",         "desc": "单数/复数主语与动词的一致规则",                 "sub": "basic-grammar", "diff": 3, "type": "theory", "tags": ["核心"], "ms": True},

    # ── vocabulary (18 concepts) ──
    {"id": "word-formation",        "name": "构词法",           "desc": "前缀、后缀、词根与合成词",                     "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "common-prefixes",       "name": "常见前缀",         "desc": "un-/re-/pre-/dis-/mis-等20个高频前缀",          "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "common-suffixes",       "name": "常见后缀",         "desc": "-tion/-ment/-ness/-able/-ful等20个高频后缀",    "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "latin-greek-roots",     "name": "拉丁与希腊词根",   "desc": "常见拉丁/希腊词根及其派生",                    "sub": "vocabulary", "diff": 4, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "synonyms-antonyms",     "name": "同义词与反义词",   "desc": "近义词辨析与反义词构成",                        "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "collocations",          "name": "搭配",             "desc": "常见动词+名词、形容词+名词搭配",               "sub": "vocabulary", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "phrasal-verbs",         "name": "短语动词",         "desc": "动词+介词/副词组合的含义变化",                  "sub": "vocabulary", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "context-clues",         "name": "上下文猜词",       "desc": "通过语境推断生词含义的技巧",                    "sub": "vocabulary", "diff": 3, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "word-families",         "name": "词族",             "desc": "同一词根派生出的词性变化家族",                  "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "academic-vocabulary",   "name": "学术词汇",         "desc": "AWL学术词汇表核心词",                           "sub": "vocabulary", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "false-friends",         "name": "假朋友",           "desc": "中英文中形似但义不同的词汇",                    "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["易错"], "ms": False},
    {"id": "register-formality",    "name": "语域与正式程度",   "desc": "正式/非正式/口语/书面语词汇选择",               "sub": "vocabulary", "diff": 4, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "vocabulary-strategies",  "name": "词汇记忆策略",     "desc": "间隔重复、联想、语境学习等方法",               "sub": "vocabulary", "diff": 2, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "confusing-words",       "name": "易混淆词",         "desc": "affect/effect, its/it's等常见混淆",             "sub": "vocabulary", "diff": 3, "type": "theory",   "tags": ["易错"], "ms": False},
    {"id": "business-vocabulary",   "name": "商务词汇",         "desc": "商务场景高频词汇与表达",                        "sub": "vocabulary", "diff": 5, "type": "theory",   "tags": ["专业"], "ms": False},
    {"id": "technical-vocabulary",  "name": "科技词汇",         "desc": "科学技术领域常见英语术语",                      "sub": "vocabulary", "diff": 5, "type": "theory",   "tags": ["专业"], "ms": False},
    {"id": "connotation-denotation","name": "内涵与外延",       "desc": "词汇的字面含义与感情色彩",                      "sub": "vocabulary", "diff": 4, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "word-usage-practice",   "name": "词汇运用练习",     "desc": "在写作和口语中准确运用新词",                    "sub": "vocabulary", "diff": 4, "type": "practice", "tags": ["练习"], "ms": False},

    # ── tenses (20 concepts) ──
    {"id": "simple-present",        "name": "一般现在时",       "desc": "习惯动作、客观事实的表达",                      "sub": "tenses", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "present-continuous",    "name": "现在进行时",       "desc": "be+V-ing表示正在进行的动作",                    "sub": "tenses", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "simple-past",           "name": "一般过去时",       "desc": "过去发生的动作或状态",                          "sub": "tenses", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "past-continuous",       "name": "过去进行时",       "desc": "过去某时刻正在进行的动作",                      "sub": "tenses", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "simple-future",         "name": "一般将来时",       "desc": "will/be going to表示将来",                      "sub": "tenses", "diff": 2, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "present-perfect",       "name": "现在完成时",       "desc": "have/has+过去分词，已完成或持续",               "sub": "tenses", "diff": 4, "type": "theory", "tags": ["里程碑"], "ms": True},
    {"id": "present-perfect-cont",  "name": "现在完成进行时",   "desc": "have been+V-ing强调持续过程",                   "sub": "tenses", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "past-perfect",          "name": "过去完成时",       "desc": "had+过去分词，过去的过去",                      "sub": "tenses", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "past-perfect-cont",     "name": "过去完成进行时",   "desc": "had been+V-ing过去持续动作",                    "sub": "tenses", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "future-continuous",     "name": "将来进行时",       "desc": "will be+V-ing将来某刻正在做",                   "sub": "tenses", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "future-perfect",        "name": "将来完成时",       "desc": "will have+过去分词，将来某点前完成",            "sub": "tenses", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "tense-timeline",        "name": "时态时间线",       "desc": "12种时态的时间线对比与总结",                    "sub": "tenses", "diff": 4, "type": "theory", "tags": ["里程碑"], "ms": True},
    {"id": "irregular-verbs",       "name": "不规则动词",       "desc": "常见不规则动词三种形式",                        "sub": "tenses", "diff": 3, "type": "theory", "tags": ["基础"], "ms": False},
    {"id": "passive-voice",         "name": "被动语态",         "desc": "be+过去分词的各时态被动形式",                   "sub": "tenses", "diff": 4, "type": "theory", "tags": ["核心"], "ms": True},
    {"id": "reported-speech",       "name": "间接引语",         "desc": "直接引语转间接引语的时态后退",                  "sub": "tenses", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "stative-verbs",         "name": "状态动词",         "desc": "不用于进行时的动词及例外",                      "sub": "tenses", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "tense-consistency",     "name": "时态一致性",       "desc": "叙述中保持时态一致的规则",                      "sub": "tenses", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "used-to-would",         "name": "used to与would",  "desc": "表示过去习惯的两种表达",                        "sub": "tenses", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "present-for-future",    "name": "现在时表将来",     "desc": "时间/条件从句中现在时代替将来时",               "sub": "tenses", "diff": 4, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "tense-review-exercise", "name": "时态综合练习",     "desc": "混合时态语境选择与翻译练习",                    "sub": "tenses", "diff": 4, "type": "practice","tags": ["练习"], "ms": False},

    # ── sentence-patterns (20 concepts) ──
    {"id": "five-basic-patterns",   "name": "五种基本句型",     "desc": "SV/SVO/SVC/SVOO/SVOC",                          "sub": "sentence-patterns", "diff": 2, "type": "theory", "tags": ["基础"], "ms": True},
    {"id": "compound-sentences",    "name": "并列句",           "desc": "and/but/or/so连接的并列结构",                   "sub": "sentence-patterns", "diff": 3, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "complex-sentences",     "name": "复合句",           "desc": "主句+从句的基本结构",                           "sub": "sentence-patterns", "diff": 4, "type": "theory", "tags": ["核心"], "ms": True},
    {"id": "noun-clauses",          "name": "名词性从句",       "desc": "主语从句、宾语从句、表语从句",                  "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "adjective-clauses",     "name": "定语从句",         "desc": "who/which/that/where/when引导的定语从句",       "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["里程碑"], "ms": True},
    {"id": "adverb-clauses",        "name": "状语从句",         "desc": "时间/原因/条件/让步/目的状语从句",              "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "relative-pronouns",     "name": "关系代词与关系副词","desc": "定语从句中who/whom/whose/which/that/where/when","sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "restrictive-vs-non",    "name": "限制性与非限制性",  "desc": "限制性和非限制性定语从句的区别",                "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "infinitive-phrases",    "name": "不定式短语",       "desc": "to+V作主语/宾语/定语/状语/补语",               "sub": "sentence-patterns", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "gerund-phrases",        "name": "动名词短语",       "desc": "V-ing作主语/宾语/介词宾语",                     "sub": "sentence-patterns", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "participle-phrases",    "name": "分词短语",         "desc": "现在分词和过去分词作定语/状语",                 "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "conditional-sentences", "name": "条件句",           "desc": "零/一/二/三类条件句与混合条件句",               "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["核心"], "ms": True},
    {"id": "wish-subjunctive",      "name": "虚拟语气",         "desc": "wish/if only/as if/suggest等虚拟用法",          "sub": "sentence-patterns", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "inversion",             "name": "倒装句",           "desc": "完全倒装与部分倒装的条件",                      "sub": "sentence-patterns", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "emphasis-cleft",        "name": "强调与分裂句",     "desc": "It is...that强调句型、do/does强调",             "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "parallel-structure",    "name": "平行结构",         "desc": "句子成分的对等与平衡",                          "sub": "sentence-patterns", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "sentence-combining",    "name": "句子合并",         "desc": "将简单句合并为复合句的技巧",                    "sub": "sentence-patterns", "diff": 4, "type": "practice","tags": ["练习"], "ms": False},
    {"id": "run-on-fragments",      "name": "句子错误",         "desc": "连写句、断句、悬垂修饰语等常见错误",            "sub": "sentence-patterns", "diff": 4, "type": "theory", "tags": ["易错"], "ms": False},
    {"id": "appositive-phrases",    "name": "同位语",           "desc": "同位语和同位语从句的用法",                      "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "ellipsis-substitution", "name": "省略与替代",       "desc": "so/not/do so/one等替代和省略",                  "sub": "sentence-patterns", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},

    # ── advanced-grammar (20 concepts) ──
    {"id": "advanced-modals",       "name": "情态动词进阶",     "desc": "推测/后悔/可能性的情态表达",                    "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "causative-verbs",       "name": "使役动词",         "desc": "make/have/let/get+宾语+补语",                   "sub": "advanced-grammar", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "subjunctive-mood",      "name": "虚拟语气详解",     "desc": "各种虚拟语气的形式与用法总结",                  "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["核心"], "ms": True},
    {"id": "discourse-markers",     "name": "话语标记词",       "desc": "however/moreover/nevertheless等逻辑连接",       "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "reported-speech-adv",   "name": "间接引语进阶",     "desc": "复杂报告句、引用动词选择",                      "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "articles-advanced",     "name": "冠词进阶",         "desc": "抽象名词、专有名词等特殊冠词用法",              "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "noun-modifiers",        "name": "名词修饰语",       "desc": "多个形容词排序规则与名词作修饰",               "sub": "advanced-grammar", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "adverb-placement",      "name": "副词位置",         "desc": "不同类型副词在句中的位置规则",                  "sub": "advanced-grammar", "diff": 4, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "dangling-modifiers",    "name": "悬垂修饰语",       "desc": "分词短语修饰对象不明确的纠错",                  "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["易错"], "ms": False},
    {"id": "hedging-language",      "name": "模糊表达",         "desc": "学术写作中的缓和表达策略",                      "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["学术"], "ms": False},
    {"id": "ellipsis-advanced",     "name": "高级省略",         "desc": "比较句、并列句中的高级省略规则",                "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "fronting-theme",        "name": "主位推进",         "desc": "信息结构中的主位与述位",                        "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "mixed-conditionals",    "name": "混合条件句",       "desc": "过去与现在交叉的条件虚拟",                      "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "nominal-relative",      "name": "名词性关系从句",   "desc": "what/whoever/whatever引导的从句",               "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "reduced-clauses",       "name": "从句简化",         "desc": "将从句简化为短语的方法",                        "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "concession-contrast",   "name": "让步与对比",       "desc": "although/despite/whereas/while等对比表达",      "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["核心"], "ms": False},
    {"id": "complex-prepositions",  "name": "复杂介词短语",     "desc": "in terms of/with regard to/by means of等",     "sub": "advanced-grammar", "diff": 5, "type": "theory", "tags": ["学术"], "ms": False},
    {"id": "aspect-nuances",        "name": "体态细微差别",     "desc": "进行体、完成体、惯常体的深层语义",              "sub": "advanced-grammar", "diff": 6, "type": "theory", "tags": ["进阶"], "ms": False},
    {"id": "grammar-in-context",    "name": "语境中的语法",     "desc": "语法规则在真实语篇中的灵活应用",                "sub": "advanced-grammar", "diff": 5, "type": "practice","tags": ["练习"], "ms": False},
    {"id": "error-analysis",        "name": "语法纠错",         "desc": "中国学习者常见语法错误分析",                    "sub": "advanced-grammar", "diff": 5, "type": "practice","tags": ["练习"], "ms": True},

    # ── reading (20 concepts) ──
    {"id": "skimming",              "name": "略读",             "desc": "快速浏览获取文章大意",                          "sub": "reading", "diff": 3, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "scanning",              "name": "查读",             "desc": "快速定位特定信息",                              "sub": "reading", "diff": 3, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "intensive-reading",     "name": "精读",             "desc": "逐句分析理解文章细节",                          "sub": "reading", "diff": 4, "type": "practice", "tags": ["策略"], "ms": True},
    {"id": "main-idea",             "name": "主旨大意",         "desc": "识别段落和文章的中心思想",                      "sub": "reading", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "supporting-details",    "name": "细节支撑",         "desc": "识别和理解支撑主旨的细节",                      "sub": "reading", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "inference",             "name": "推断",             "desc": "根据文本信息进行逻辑推理",                      "sub": "reading", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "text-structure",        "name": "篇章结构",         "desc": "因果/比较/问题解决/时间等组织结构",              "sub": "reading", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "cohesion-coherence",    "name": "衔接与连贯",       "desc": "代词指代、连接词、词汇衔接",                    "sub": "reading", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "authors-purpose",       "name": "作者目的",         "desc": "判断作者写作意图和态度",                        "sub": "reading", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "tone-mood",             "name": "语气与情感",       "desc": "识别文本的语气和情感基调",                      "sub": "reading", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "fact-vs-opinion",       "name": "事实与观点",       "desc": "区分客观事实与主观观点",                        "sub": "reading", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "critical-reading",      "name": "批判性阅读",       "desc": "评价论点、识别偏见与逻辑谬误",                  "sub": "reading", "diff": 6, "type": "theory",   "tags": ["进阶"], "ms": True},
    {"id": "narrative-reading",     "name": "叙事文阅读",       "desc": "小说/故事的叙事要素与文学手法",                 "sub": "reading", "diff": 4, "type": "theory",   "tags": ["文学"], "ms": False},
    {"id": "expository-reading",    "name": "说明文阅读",       "desc": "科普/百科类文章的阅读策略",                     "sub": "reading", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "argumentative-reading", "name": "议论文阅读",       "desc": "论点/论据/论证过程的分析",                      "sub": "reading", "diff": 5, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "news-media-reading",    "name": "新闻阅读",         "desc": "新闻报道结构与媒体素养",                        "sub": "reading", "diff": 4, "type": "theory",   "tags": ["应用"], "ms": False},
    {"id": "academic-reading",      "name": "学术文章阅读",     "desc": "论文结构、引用、摘要阅读策略",                  "sub": "reading", "diff": 6, "type": "theory",   "tags": ["学术"], "ms": False},
    {"id": "reading-speed",         "name": "阅读速度",         "desc": "提高阅读速度的训练方法",                        "sub": "reading", "diff": 3, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "summarizing",           "name": "概括总结",         "desc": "用自己的话概括文章要点",                        "sub": "reading", "diff": 4, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "graphic-information",   "name": "图表信息",         "desc": "读懂图表、数据、信息图",                        "sub": "reading", "diff": 4, "type": "practice", "tags": ["应用"], "ms": False},

    # ── writing-en (22 concepts) ──
    {"id": "sentence-writing",      "name": "句子写作",         "desc": "写出语法正确、表意清晰的句子",                  "sub": "writing-en", "diff": 2, "type": "practice", "tags": ["基础"], "ms": False},
    {"id": "paragraph-structure",   "name": "段落结构",         "desc": "主题句+支撑句+结尾句",                          "sub": "writing-en", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "topic-sentences",       "name": "主题句",           "desc": "写好段落的主题句",                              "sub": "writing-en", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "coherence-transitions", "name": "连贯与过渡",       "desc": "段落间的过渡词和逻辑连接",                      "sub": "writing-en", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "essay-structure",       "name": "文章结构",         "desc": "引言/正文/结论的三部分结构",                    "sub": "writing-en", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "narrative-writing",     "name": "记叙文写作",       "desc": "讲故事的技巧：人物/情节/冲突",                  "sub": "writing-en", "diff": 4, "type": "practice", "tags": ["文体"], "ms": False},
    {"id": "descriptive-writing",   "name": "描写文写作",       "desc": "五感描写、细节与意象",                          "sub": "writing-en", "diff": 4, "type": "practice", "tags": ["文体"], "ms": False},
    {"id": "expository-writing",    "name": "说明文写作",       "desc": "解释概念、过程或现象",                          "sub": "writing-en", "diff": 5, "type": "practice", "tags": ["文体"], "ms": False},
    {"id": "argumentative-writing", "name": "议论文写作",       "desc": "论点+论据+反驳+结论",                           "sub": "writing-en", "diff": 5, "type": "practice", "tags": ["文体"], "ms": True},
    {"id": "email-writing",         "name": "邮件写作",         "desc": "正式/非正式邮件格式与表达",                     "sub": "writing-en", "diff": 3, "type": "practice", "tags": ["应用"], "ms": False},
    {"id": "summary-writing",       "name": "摘要写作",         "desc": "浓缩原文要点的写作技巧",                        "sub": "writing-en", "diff": 4, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "paraphrasing",          "name": "改写",             "desc": "用不同方式表达相同含义",                        "sub": "writing-en", "diff": 4, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "punctuation",           "name": "标点符号",         "desc": "逗号/句号/分号/冒号/引号的规则",                "sub": "writing-en", "diff": 3, "type": "theory",   "tags": ["基础"], "ms": False},
    {"id": "sentence-variety",      "name": "句式多样性",       "desc": "长短句交替、句首变化",                          "sub": "writing-en", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "word-choice",           "name": "措辞",             "desc": "精确、具体、生动的词语选择",                    "sub": "writing-en", "diff": 4, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "editing-proofreading",  "name": "编辑与校对",       "desc": "修改草稿的系统方法",                            "sub": "writing-en", "diff": 3, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "academic-writing",      "name": "学术写作",         "desc": "学术论文结构、引用格式",                        "sub": "writing-en", "diff": 6, "type": "theory",   "tags": ["学术"], "ms": False},
    {"id": "citation-referencing",  "name": "引用与参考文献",   "desc": "APA/MLA格式引用规范",                           "sub": "writing-en", "diff": 6, "type": "theory",   "tags": ["学术"], "ms": False},
    {"id": "creative-writing",      "name": "创意写作",         "desc": "诗歌、短篇小说等文学创作",                      "sub": "writing-en", "diff": 5, "type": "practice", "tags": ["文学"], "ms": False},
    {"id": "report-writing",        "name": "报告写作",         "desc": "正式报告的结构与语言",                          "sub": "writing-en", "diff": 5, "type": "practice", "tags": ["应用"], "ms": False},
    {"id": "review-writing",        "name": "书评/影评",        "desc": "评论文的结构与批判技巧",                        "sub": "writing-en", "diff": 5, "type": "practice", "tags": ["应用"], "ms": False},
    {"id": "writing-process",       "name": "写作流程",         "desc": "构思/起草/修改/定稿的完整流程",                 "sub": "writing-en", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},

    # ── speaking (20 concepts) ──
    {"id": "self-introduction",     "name": "自我介绍",         "desc": "不同场合的自我介绍表达",                        "sub": "speaking", "diff": 2, "type": "practice", "tags": ["基础"], "ms": False},
    {"id": "daily-conversations",   "name": "日常对话",         "desc": "问候/感谢/道歉/请求等基本社交",                 "sub": "speaking", "diff": 2, "type": "practice", "tags": ["基础"], "ms": True},
    {"id": "asking-directions",     "name": "问路与指路",       "desc": "方向、位置描述与交通表达",                      "sub": "speaking", "diff": 2, "type": "practice", "tags": ["基础"], "ms": False},
    {"id": "expressing-opinions",   "name": "表达观点",         "desc": "同意/反对/中立的表达方式",                      "sub": "speaking", "diff": 3, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "describing-things",     "name": "描述事物",         "desc": "外观/功能/特征的口语描述",                      "sub": "speaking", "diff": 3, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "storytelling-oral",     "name": "口头叙事",         "desc": "讲述经历和故事的口语技巧",                      "sub": "speaking", "diff": 4, "type": "practice", "tags": ["核心"], "ms": False},
    {"id": "discussion-skills",     "name": "讨论技巧",         "desc": "小组讨论中的发言与回应",                        "sub": "speaking", "diff": 4, "type": "practice", "tags": ["核心"], "ms": True},
    {"id": "presentation-skills",   "name": "演示技巧",         "desc": "结构化演讲与幻灯片配合",                        "sub": "speaking", "diff": 5, "type": "practice", "tags": ["进阶"], "ms": True},
    {"id": "debate-skills",         "name": "辩论技巧",         "desc": "论证、反驳和总结的口语表达",                    "sub": "speaking", "diff": 6, "type": "practice", "tags": ["进阶"], "ms": False},
    {"id": "telephone-english",     "name": "电话英语",         "desc": "电话/视频通话的常用表达",                       "sub": "speaking", "diff": 3, "type": "practice", "tags": ["应用"], "ms": False},
    {"id": "interview-english",     "name": "面试英语",         "desc": "工作面试常见问答与技巧",                        "sub": "speaking", "diff": 5, "type": "practice", "tags": ["应用"], "ms": False},
    {"id": "fillers-hesitation",    "name": "填充语与犹豫",     "desc": "well/um/you know等自然使用",                    "sub": "speaking", "diff": 3, "type": "theory",   "tags": ["口语"], "ms": False},
    {"id": "turn-taking",           "name": "话轮转换",         "desc": "对话中的接话与插话技巧",                        "sub": "speaking", "diff": 4, "type": "theory",   "tags": ["口语"], "ms": False},
    {"id": "pragmatic-competence",  "name": "语用能力",         "desc": "言外之意、间接请求与礼貌策略",                  "sub": "speaking", "diff": 5, "type": "theory",   "tags": ["进阶"], "ms": False},
    {"id": "negotiation-english",   "name": "谈判英语",         "desc": "商务谈判中的策略性表达",                        "sub": "speaking", "diff": 6, "type": "practice", "tags": ["商务"], "ms": False},
    {"id": "fluency-strategies",    "name": "流利性策略",       "desc": "提高口语流利度的方法",                          "sub": "speaking", "diff": 4, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "accuracy-practice",     "name": "准确性练习",       "desc": "口语中避免常见语法错误",                        "sub": "speaking", "diff": 4, "type": "practice", "tags": ["练习"], "ms": False},
    {"id": "shadowing-technique",   "name": "影子跟读",         "desc": "跟随母语者同步朗读训练",                        "sub": "speaking", "diff": 3, "type": "practice", "tags": ["策略"], "ms": False},
    {"id": "small-talk",            "name": "闲聊",             "desc": "天气/爱好/新闻等社交闲聊话题",                  "sub": "speaking", "diff": 3, "type": "practice", "tags": ["社交"], "ms": False},
    {"id": "cross-cultural-comm",   "name": "跨文化交际",       "desc": "不同文化背景下的沟通注意事项",                  "sub": "speaking", "diff": 5, "type": "theory",   "tags": ["文化"], "ms": False},

    # ── idioms-culture (18 concepts) ──
    {"id": "common-idioms",         "name": "常见习语",         "desc": "break the ice/a piece of cake等50个核心习语",   "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": True},
    {"id": "proverbs",              "name": "谚语",             "desc": "Actions speak louder than words等经典谚语",      "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["核心"], "ms": False},
    {"id": "slang-informal",        "name": "俚语与非正式表达", "desc": "当代英语口语中的常见俚语",                      "sub": "idioms-culture", "diff": 4, "type": "theory",   "tags": ["口语"], "ms": False},
    {"id": "body-language-idioms",  "name": "身体语言习语",     "desc": "cold shoulder/keep an eye on等身体相关习语",     "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["趣味"], "ms": False},
    {"id": "color-idioms",          "name": "颜色习语",         "desc": "feeling blue/green with envy等颜色相关习语",    "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["趣味"], "ms": False},
    {"id": "food-idioms",           "name": "食物习语",         "desc": "spill the beans/cool as cucumber等食物习语",    "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["趣味"], "ms": False},
    {"id": "british-vs-american",   "name": "英式与美式差异",   "desc": "拼写、词汇、表达的英美差异",                    "sub": "idioms-culture", "diff": 4, "type": "theory",   "tags": ["文化"], "ms": True},
    {"id": "english-humor",         "name": "英语幽默",         "desc": "双关语、讽刺、英式/美式幽默风格",               "sub": "idioms-culture", "diff": 5, "type": "theory",   "tags": ["文化"], "ms": False},
    {"id": "politeness-norms",      "name": "礼貌规范",         "desc": "英语世界的礼貌策略与禁忌",                      "sub": "idioms-culture", "diff": 4, "type": "theory",   "tags": ["文化"], "ms": False},
    {"id": "holiday-culture",       "name": "节日文化",         "desc": "Christmas/Thanksgiving/Halloween等文化背景",    "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["文化"], "ms": False},
    {"id": "english-literature",    "name": "英语文学简介",     "desc": "莎士比亚到当代的英语文学概览",                  "sub": "idioms-culture", "diff": 5, "type": "theory",   "tags": ["文学"], "ms": False},
    {"id": "media-entertainment",   "name": "影视与流行文化",   "desc": "通过影视剧学习地道表达",                        "sub": "idioms-culture", "diff": 3, "type": "practice", "tags": ["趣味"], "ms": False},
    {"id": "figurative-language",   "name": "修辞手法",         "desc": "比喻/拟人/夸张/反讽等表达手法",                 "sub": "idioms-culture", "diff": 5, "type": "theory",   "tags": ["文学"], "ms": False},
    {"id": "euphemisms",            "name": "委婉语",           "desc": "避免直接表达不愉快话题的方式",                  "sub": "idioms-culture", "diff": 4, "type": "theory",   "tags": ["文化"], "ms": False},
    {"id": "internet-english",      "name": "网络英语",         "desc": "LOL/BTW/ASAP等缩写与网络用语",                 "sub": "idioms-culture", "diff": 3, "type": "theory",   "tags": ["现代"], "ms": False},
    {"id": "english-word-origins",  "name": "英语词源",         "desc": "英语借词的历史：拉丁/法语/日耳曼",             "sub": "idioms-culture", "diff": 5, "type": "theory",   "tags": ["文化"], "ms": False},
    {"id": "global-english",        "name": "世界英语",         "desc": "英语作为全球语言的变体与未来",                  "sub": "idioms-culture", "diff": 5, "type": "theory",   "tags": ["拓展"], "ms": False},
    {"id": "idiom-usage-practice",  "name": "习语运用练习",     "desc": "在写作和口语中恰当使用习语",                    "sub": "idioms-culture", "diff": 4, "type": "practice", "tags": ["练习"], "ms": False},
]
# fmt: on

# ── Edge definitions ──
# Format: (source_id, target_id, relation_type, strength)
EDGES = [
    # phonetics internal
    ("vowel-sounds", "ipa-basics", "prerequisite", 0.9),
    ("consonant-sounds", "ipa-basics", "prerequisite", 0.9),
    ("ipa-basics", "syllable-structure", "prerequisite", 0.8),
    ("ipa-basics", "phonemic-transcription", "prerequisite", 0.8),
    ("ipa-basics", "minimal-pairs", "related", 0.7),
    ("syllable-structure", "word-stress", "prerequisite", 0.8),
    ("word-stress", "sentence-stress", "prerequisite", 0.8),
    ("sentence-stress", "intonation-patterns", "prerequisite", 0.8),
    ("sentence-stress", "rhythm-timing", "prerequisite", 0.7),
    ("intonation-patterns", "thought-groups", "related", 0.7),
    ("consonant-sounds", "consonant-clusters", "prerequisite", 0.7),
    ("consonant-sounds", "linking-sounds", "prerequisite", 0.7),
    ("linking-sounds", "reduction-elision", "prerequisite", 0.7),
    ("reduction-elision", "assimilation", "related", 0.7),
    ("vowel-sounds", "schwa-sound", "related", 0.7),
    ("phonics-rules", "vowel-sounds", "related", 0.6),
    ("phonics-rules", "consonant-sounds", "related", 0.6),
    ("vowel-sounds", "am-vs-br-pronunciation", "related", 0.5),
    ("consonant-sounds", "tongue-twisters", "related", 0.5),
    ("rhythm-timing", "pronunciation-practice", "related", 0.6),
    ("intonation-patterns", "pronunciation-practice", "related", 0.6),

    # basic-grammar internal
    ("parts-of-speech", "nouns", "prerequisite", 0.9),
    ("parts-of-speech", "pronouns", "prerequisite", 0.9),
    ("parts-of-speech", "adjectives", "prerequisite", 0.9),
    ("parts-of-speech", "adverbs", "prerequisite", 0.8),
    ("parts-of-speech", "prepositions", "prerequisite", 0.8),
    ("parts-of-speech", "conjunctions", "prerequisite", 0.8),
    ("nouns", "articles", "prerequisite", 0.8),
    ("nouns", "possessives", "prerequisite", 0.7),
    ("nouns", "quantifiers", "prerequisite", 0.7),
    ("nouns", "determiners", "prerequisite", 0.7),
    ("pronouns", "possessives", "related", 0.6),
    ("basic-sentence-order", "be-verb", "prerequisite", 0.8),
    ("be-verb", "have-do-auxiliary", "prerequisite", 0.7),
    ("have-do-auxiliary", "modal-verbs", "prerequisite", 0.7),
    ("basic-sentence-order", "questions", "prerequisite", 0.7),
    ("basic-sentence-order", "negation", "prerequisite", 0.7),
    ("basic-sentence-order", "imperative", "related", 0.6),
    ("basic-sentence-order", "exclamatory", "related", 0.5),
    ("be-verb", "there-be", "prerequisite", 0.7),
    ("pronouns", "it-usage", "prerequisite", 0.6),
    ("nouns", "subject-verb-agreement", "prerequisite", 0.7),
    ("be-verb", "subject-verb-agreement", "prerequisite", 0.7),

    # vocabulary internal
    ("word-formation", "common-prefixes", "prerequisite", 0.9),
    ("word-formation", "common-suffixes", "prerequisite", 0.9),
    ("common-prefixes", "latin-greek-roots", "prerequisite", 0.7),
    ("common-suffixes", "latin-greek-roots", "prerequisite", 0.7),
    ("word-formation", "word-families", "prerequisite", 0.7),
    ("synonyms-antonyms", "collocations", "related", 0.6),
    ("collocations", "phrasal-verbs", "related", 0.7),
    ("context-clues", "vocabulary-strategies", "related", 0.6),
    ("register-formality", "academic-vocabulary", "related", 0.6),
    ("register-formality", "business-vocabulary", "related", 0.6),
    ("synonyms-antonyms", "confusing-words", "related", 0.6),
    ("synonyms-antonyms", "connotation-denotation", "related", 0.6),
    ("collocations", "word-usage-practice", "related", 0.6),
    ("academic-vocabulary", "technical-vocabulary", "related", 0.5),
    ("confusing-words", "false-friends", "related", 0.6),

    # tenses internal
    ("simple-present", "present-continuous", "prerequisite", 0.8),
    ("simple-present", "simple-past", "prerequisite", 0.8),
    ("simple-present", "simple-future", "prerequisite", 0.7),
    ("simple-past", "past-continuous", "prerequisite", 0.8),
    ("simple-past", "irregular-verbs", "prerequisite", 0.8),
    ("simple-present", "stative-verbs", "related", 0.6),
    ("present-continuous", "present-perfect", "prerequisite", 0.7),
    ("simple-past", "present-perfect", "prerequisite", 0.8),
    ("present-perfect", "present-perfect-cont", "prerequisite", 0.8),
    ("simple-past", "past-perfect", "prerequisite", 0.7),
    ("past-continuous", "past-perfect-cont", "prerequisite", 0.7),
    ("past-perfect", "past-perfect-cont", "prerequisite", 0.8),
    ("simple-future", "future-continuous", "prerequisite", 0.7),
    ("simple-future", "future-perfect", "prerequisite", 0.7),
    ("present-perfect", "tense-timeline", "prerequisite", 0.7),
    ("past-perfect", "tense-timeline", "prerequisite", 0.7),
    ("simple-past", "passive-voice", "prerequisite", 0.7),
    ("present-perfect", "passive-voice", "prerequisite", 0.6),
    ("past-perfect", "reported-speech", "prerequisite", 0.7),
    ("tense-timeline", "tense-consistency", "related", 0.7),
    ("simple-past", "used-to-would", "related", 0.6),
    ("simple-present", "present-for-future", "related", 0.6),
    ("tense-timeline", "tense-review-exercise", "related", 0.7),

    # sentence-patterns internal
    ("five-basic-patterns", "compound-sentences", "prerequisite", 0.8),
    ("compound-sentences", "complex-sentences", "prerequisite", 0.8),
    ("complex-sentences", "noun-clauses", "prerequisite", 0.8),
    ("complex-sentences", "adjective-clauses", "prerequisite", 0.8),
    ("complex-sentences", "adverb-clauses", "prerequisite", 0.8),
    ("adjective-clauses", "relative-pronouns", "prerequisite", 0.9),
    ("adjective-clauses", "restrictive-vs-non", "prerequisite", 0.8),
    ("five-basic-patterns", "infinitive-phrases", "prerequisite", 0.6),
    ("five-basic-patterns", "gerund-phrases", "prerequisite", 0.6),
    ("infinitive-phrases", "participle-phrases", "related", 0.7),
    ("gerund-phrases", "participle-phrases", "related", 0.7),
    ("adverb-clauses", "conditional-sentences", "prerequisite", 0.7),
    ("conditional-sentences", "wish-subjunctive", "prerequisite", 0.7),
    ("complex-sentences", "inversion", "related", 0.5),
    ("five-basic-patterns", "emphasis-cleft", "related", 0.5),
    ("compound-sentences", "parallel-structure", "related", 0.7),
    ("compound-sentences", "sentence-combining", "related", 0.6),
    ("five-basic-patterns", "run-on-fragments", "related", 0.5),
    ("noun-clauses", "appositive-phrases", "related", 0.6),
    ("complex-sentences", "ellipsis-substitution", "related", 0.5),

    # advanced-grammar internal
    ("modal-verbs", "advanced-modals", "prerequisite", 0.8),
    ("five-basic-patterns", "causative-verbs", "prerequisite", 0.6),
    ("conditional-sentences", "subjunctive-mood", "prerequisite", 0.8),
    ("wish-subjunctive", "subjunctive-mood", "prerequisite", 0.8),
    ("conjunctions", "discourse-markers", "prerequisite", 0.6),
    ("reported-speech", "reported-speech-adv", "prerequisite", 0.8),
    ("articles", "articles-advanced", "prerequisite", 0.8),
    ("adjectives", "noun-modifiers", "prerequisite", 0.6),
    ("adverbs", "adverb-placement", "prerequisite", 0.7),
    ("participle-phrases", "dangling-modifiers", "prerequisite", 0.7),
    ("discourse-markers", "hedging-language", "related", 0.6),
    ("ellipsis-substitution", "ellipsis-advanced", "prerequisite", 0.7),
    ("inversion", "fronting-theme", "related", 0.5),
    ("conditional-sentences", "mixed-conditionals", "prerequisite", 0.7),
    ("noun-clauses", "nominal-relative", "prerequisite", 0.7),
    ("participle-phrases", "reduced-clauses", "prerequisite", 0.7),
    ("adverb-clauses", "concession-contrast", "prerequisite", 0.6),
    ("prepositions", "complex-prepositions", "prerequisite", 0.6),
    ("present-perfect-cont", "aspect-nuances", "related", 0.5),
    ("error-analysis", "grammar-in-context", "related", 0.6),

    # reading internal
    ("skimming", "scanning", "related", 0.8),
    ("skimming", "intensive-reading", "prerequisite", 0.7),
    ("main-idea", "supporting-details", "prerequisite", 0.8),
    ("supporting-details", "inference", "prerequisite", 0.7),
    ("main-idea", "text-structure", "prerequisite", 0.7),
    ("text-structure", "cohesion-coherence", "prerequisite", 0.7),
    ("inference", "authors-purpose", "prerequisite", 0.6),
    ("authors-purpose", "tone-mood", "related", 0.7),
    ("main-idea", "fact-vs-opinion", "related", 0.6),
    ("inference", "critical-reading", "prerequisite", 0.7),
    ("tone-mood", "critical-reading", "prerequisite", 0.6),
    ("text-structure", "narrative-reading", "related", 0.6),
    ("text-structure", "expository-reading", "related", 0.6),
    ("critical-reading", "argumentative-reading", "prerequisite", 0.6),
    ("skimming", "news-media-reading", "related", 0.5),
    ("cohesion-coherence", "academic-reading", "prerequisite", 0.6),
    ("skimming", "reading-speed", "related", 0.7),
    ("main-idea", "summarizing", "prerequisite", 0.7),
    ("expository-reading", "graphic-information", "related", 0.5),

    # writing-en internal
    ("sentence-writing", "paragraph-structure", "prerequisite", 0.9),
    ("paragraph-structure", "topic-sentences", "prerequisite", 0.8),
    ("paragraph-structure", "coherence-transitions", "prerequisite", 0.8),
    ("coherence-transitions", "essay-structure", "prerequisite", 0.8),
    ("essay-structure", "narrative-writing", "prerequisite", 0.6),
    ("essay-structure", "descriptive-writing", "prerequisite", 0.6),
    ("essay-structure", "expository-writing", "prerequisite", 0.7),
    ("essay-structure", "argumentative-writing", "prerequisite", 0.7),
    ("sentence-writing", "email-writing", "prerequisite", 0.5),
    ("summarizing", "summary-writing", "prerequisite", 0.7),
    ("summary-writing", "paraphrasing", "related", 0.7),
    ("sentence-writing", "punctuation", "prerequisite", 0.7),
    ("paragraph-structure", "sentence-variety", "related", 0.6),
    ("sentence-variety", "word-choice", "related", 0.7),
    ("essay-structure", "editing-proofreading", "related", 0.6),
    ("argumentative-writing", "academic-writing", "prerequisite", 0.6),
    ("academic-writing", "citation-referencing", "prerequisite", 0.8),
    ("descriptive-writing", "creative-writing", "related", 0.6),
    ("expository-writing", "report-writing", "related", 0.6),
    ("critical-reading", "review-writing", "prerequisite", 0.5),
    ("essay-structure", "writing-process", "related", 0.7),

    # speaking internal
    ("self-introduction", "daily-conversations", "prerequisite", 0.8),
    ("daily-conversations", "asking-directions", "related", 0.6),
    ("daily-conversations", "expressing-opinions", "prerequisite", 0.7),
    ("daily-conversations", "describing-things", "prerequisite", 0.7),
    ("describing-things", "storytelling-oral", "prerequisite", 0.7),
    ("expressing-opinions", "discussion-skills", "prerequisite", 0.7),
    ("discussion-skills", "presentation-skills", "prerequisite", 0.7),
    ("presentation-skills", "debate-skills", "prerequisite", 0.7),
    ("daily-conversations", "telephone-english", "related", 0.6),
    ("presentation-skills", "interview-english", "related", 0.6),
    ("daily-conversations", "fillers-hesitation", "related", 0.5),
    ("discussion-skills", "turn-taking", "related", 0.7),
    ("expressing-opinions", "pragmatic-competence", "prerequisite", 0.5),
    ("debate-skills", "negotiation-english", "prerequisite", 0.6),
    ("daily-conversations", "fluency-strategies", "related", 0.6),
    ("fluency-strategies", "accuracy-practice", "related", 0.7),
    ("pronunciation-practice", "shadowing-technique", "related", 0.7),
    ("daily-conversations", "small-talk", "related", 0.7),
    ("pragmatic-competence", "cross-cultural-comm", "related", 0.7),

    # idioms-culture internal
    ("common-idioms", "proverbs", "related", 0.7),
    ("common-idioms", "body-language-idioms", "related", 0.7),
    ("common-idioms", "color-idioms", "related", 0.7),
    ("common-idioms", "food-idioms", "related", 0.7),
    ("common-idioms", "slang-informal", "related", 0.5),
    ("british-vs-american", "am-vs-br-pronunciation", "related", 0.6),
    ("slang-informal", "english-humor", "related", 0.5),
    ("politeness-norms", "cross-cultural-comm", "related", 0.7),
    ("holiday-culture", "british-vs-american", "related", 0.5),
    ("english-literature", "figurative-language", "related", 0.7),
    ("figurative-language", "euphemisms", "related", 0.6),
    ("slang-informal", "internet-english", "related", 0.6),
    ("latin-greek-roots", "english-word-origins", "related", 0.6),
    ("british-vs-american", "global-english", "related", 0.5),
    ("common-idioms", "idiom-usage-practice", "related", 0.6),
    ("media-entertainment", "slang-informal", "related", 0.5),

    # cross-subdomain edges
    ("ipa-basics", "parts-of-speech", "related", 0.4),
    ("word-stress", "vocabulary-strategies", "related", 0.4),
    ("parts-of-speech", "word-formation", "prerequisite", 0.5),
    ("nouns", "word-families", "related", 0.4),
    ("modal-verbs", "simple-present", "prerequisite", 0.5),
    ("have-do-auxiliary", "present-perfect", "prerequisite", 0.7),
    ("be-verb", "passive-voice", "prerequisite", 0.7),
    ("subject-verb-agreement", "tense-consistency", "related", 0.5),
    ("conjunctions", "compound-sentences", "prerequisite", 0.7),
    ("prepositions", "infinitive-phrases", "related", 0.4),
    ("collocations", "sentence-writing", "related", 0.5),
    ("phrasal-verbs", "daily-conversations", "related", 0.5),
    ("register-formality", "word-choice", "related", 0.6),
    ("register-formality", "hedging-language", "related", 0.5),
    ("discourse-markers", "coherence-transitions", "prerequisite", 0.7),
    ("discourse-markers", "essay-structure", "related", 0.5),
    ("text-structure", "essay-structure", "related", 0.6),
    ("main-idea", "topic-sentences", "related", 0.6),
    ("inference", "pragmatic-competence", "related", 0.4),
    ("critical-reading", "argumentative-writing", "related", 0.5),
    ("cohesion-coherence", "coherence-transitions", "related", 0.6),
    ("sentence-variety", "grammar-in-context", "related", 0.5),
    ("error-analysis", "editing-proofreading", "related", 0.5),
    ("intonation-patterns", "expressing-opinions", "related", 0.4),
    ("thought-groups", "presentation-skills", "related", 0.4),
    ("common-idioms", "phrasal-verbs", "related", 0.4),
    ("figurative-language", "creative-writing", "related", 0.5),
    ("politeness-norms", "email-writing", "related", 0.4),
    ("euphemisms", "pragmatic-competence", "related", 0.4),
    ("academic-vocabulary", "academic-writing", "related", 0.5),
    ("academic-vocabulary", "academic-reading", "related", 0.5),
    ("business-vocabulary", "interview-english", "related", 0.4),
    ("business-vocabulary", "negotiation-english", "related", 0.4),
]


def build_seed():
    """Build the complete seed graph JSON."""
    concept_ids = {c["id"] for c in CONCEPTS}
    nodes = []
    for c in CONCEPTS:
        nodes.append({
            "id": c["id"],
            "name": c["name"],
            "description": c["desc"],
            "domain_id": "english",
            "subdomain_id": c["sub"],
            "difficulty": c["diff"],
            "estimated_minutes": 20,
            "content_type": c["type"],
            "tags": c["tags"],
            "is_milestone": c["ms"],
            "created_at": NOW,
        })

    edges = []
    for src, tgt, rel, strength in EDGES:
        assert src in concept_ids, f"Unknown source: {src}"
        assert tgt in concept_ids, f"Unknown target: {tgt}"
        edges.append({
            "source_id": src,
            "target_id": tgt,
            "relation_type": rel,
            "strength": strength,
        })

    # Build meta stats
    sub_counts = {}
    diff_dist = {}
    ms_count = 0
    for n in nodes:
        sub_counts[n["subdomain_id"]] = sub_counts.get(n["subdomain_id"], 0) + 1
        d = str(n["difficulty"])
        diff_dist[d] = diff_dist.get(d, 0) + 1
        if n["is_milestone"]:
            ms_count += 1

    meta = {
        "generated_at": NOW,
        "total_concepts": len(nodes),
        "total_edges": len(edges),
        "total_milestones": ms_count,
        "subdomain_counts": dict(sorted(sub_counts.items())),
        "difficulty_distribution": dict(sorted(diff_dist.items())),
        "last_updated": NOW,
    }

    return {
        "domain": DOMAIN,
        "subdomains": SUBDOMAINS,
        "concepts": nodes,
        "nodes": nodes,   # alias for backend compatibility
        "edges": edges,
        "meta": meta,
    }


def verify(data):
    """Run integrity checks."""
    nodes_by_id = {n["id"]: n for n in data["nodes"]}
    sub_ids = {s["id"] for s in data["subdomains"]}
    edge_set = set()
    issues = []

    # Check subdomains
    for n in data["nodes"]:
        if n["subdomain_id"] not in sub_ids:
            issues.append(f"Node {n['id']} has unknown subdomain {n['subdomain_id']}")

    # Check edges
    for e in data["edges"]:
        if e["source_id"] not in nodes_by_id:
            issues.append(f"Edge source {e['source_id']} not found")
        if e["target_id"] not in nodes_by_id:
            issues.append(f"Edge target {e['target_id']} not found")
        key = (e["source_id"], e["target_id"])
        if key in edge_set:
            issues.append(f"Duplicate edge: {key}")
        edge_set.add(key)

    # Check orphans
    connected = set()
    for e in data["edges"]:
        connected.add(e["source_id"])
        connected.add(e["target_id"])
    orphans = set(nodes_by_id.keys()) - connected
    if orphans:
        issues.append(f"Orphan nodes: {orphans}")

    # Milestone coverage
    subs_with_ms = set()
    for n in data["nodes"]:
        if n["is_milestone"]:
            subs_with_ms.add(n["subdomain_id"])
    missing_ms = sub_ids - subs_with_ms
    if missing_ms:
        issues.append(f"Subdomains without milestones: {missing_ms}")

    # Stats
    ms_count = sum(1 for n in data["nodes"] if n["is_milestone"])
    sub_counts = {}
    for n in data["nodes"]:
        sub_counts[n["subdomain_id"]] = sub_counts.get(n["subdomain_id"], 0) + 1

    print(f"Concepts: {len(data['nodes'])}")
    print(f"Edges: {len(data['edges'])}")
    print(f"Subdomains: {len(data['subdomains'])}")
    print(f"Milestones: {ms_count}")
    print(f"Per-subdomain: {dict(sorted(sub_counts.items(), key=lambda x: x[1], reverse=True))}")

    if issues:
        print(f"\n❌ {len(issues)} issues found:")
        for i in issues:
            print(f"  - {i}")
        return False
    else:
        print("\n✅ All integrity checks passed")
        return True


def main():
    data = build_seed()
    out = Path(__file__).parent / "seed_graph.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")

    if "--verify" in sys.argv:
        ok = verify(data)
        sys.exit(0 if ok else 1)
    else:
        verify(data)


if __name__ == "__main__":
    main()
