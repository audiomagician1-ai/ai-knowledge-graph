---
id: "tokenization"
concept: "分词与Tokenization"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 5
is_milestone: false
tags: ["NLP"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 分词与Tokenization

## 概述

Tokenization（分词/词元化）是将原始文本转换为模型可处理的离散单元（Token）的过程。在大语言模型中，输入文本并非以字符串形式直接送入Transformer，而是先被切分为一系列整数ID序列，每个ID对应词表（Vocabulary）中的一个Token。GPT-2的词表大小为50,257，GPT-4所使用的cl100k_base词表包含100,277个Token，LLaMA 3则采用128,256大小的词表——词表规模的扩大直接影响模型对多语言和代码的覆盖能力。

Tokenization的发展经历了从词级（Word-level）到字符级（Character-level）再到子词（Subword）的演进。早期NLP模型使用整词作为基本单元，词表动辄数十万，且无法处理未登录词（OOV）。2016年前后，字节对编码（Byte Pair Encoding，BPE）被引入NLP领域，2018年Google的SentencePiece库将其标准化，成为BERT、GPT系列的主流方案。

Tokenization在工程层面直接决定了模型的上下文窗口利用率、推理成本和跨语言公平性。中文被切成的Token数量通常是英文同等语义内容的1.5至3倍，这意味着相同的context window能存储的中文信息量更少，API调用成本也更高——这是每个使用大模型处理中文任务的工程师必须理解的现实。

## 核心原理

### 字节对编码（BPE）算法

BPE最初是1994年由Philip Gage提出的数据压缩算法，被Sennrich等人于2016年的ACL论文中引入神经机器翻译。算法从字符级词表出发，迭代地合并语料中出现频率最高的相邻符号对。

具体流程：初始词表包含所有单字符；统计语料中所有相邻符号对的共现频次；将频次最高的符号对合并为新符号，加入词表；重复此过程直至达到预设词表大小（如32,000或50,000）。最终词表同时包含高频完整词（如"the"）和低频词的子词碎片（如"ing"、"##tion"）。

### WordPiece与Unigram Language Model

BERT使用的WordPiece与BPE相似，但合并标准不同：WordPiece选择合并后使语言模型似然度提升最大的符号对，而非单纯频次最高的对。子词前缀"##"标记该片段不是词的开头（如"playing"可能被切为"play"+"##ing"）。

Unigram Language Model（T5、SentencePiece默认方案）则反其道而行之：从一个大词表出发，用EM算法迭代移除使语料对数似然下降最少的Token，直至达到目标词表大小。此方法天然支持多种分割可能，能在训练时进行分割正则化（Subword Regularization），增强模型鲁棒性。

### Byte-Level BPE与tiktoken

GPT-2引入了Byte-Level BPE：将所有文本先转换为UTF-8字节序列（256个基础符号），再在字节级别执行BPE。这彻底消除了OOV问题——任何Unicode字符都能被表示，因为最坏情况下每个字节单独作为一个Token。

OpenAI的tiktoken库实现了高效的Byte-Level BPE，其cl100k_base编码器在英文单词边界、数字、标点和空格的处理上有精细的正则预切分规则。例如，数字会被切为最多3位一组（"1234"→["123","4"]），空格通常与后续词合并（" hello"是单个Token而非两个）。这些细节对于理解模型为何在数字运算上表现欠佳至关重要。

### Token ID映射与特殊Token

每个Token在词表中对应唯一整数ID。除常规Token外，模型词表中存在具有特殊语义的控制Token：`<|endoftext|>`（ID 50256，GPT系列）用于标记文档边界；BERT使用`[CLS]`（ID 101）和`[SEP]`（ID 102）；LLaMA 3使用`<|begin_of_text|>`（ID 128000）。这些特殊Token在预训练阶段赋予了特定的注意力模式，错误地在用户输入中注入这些Token可能导致模型行为异常。

## 实际应用

**成本计算与窗口规划**：GPT-4o的定价基于Token数量。一段1000汉字的中文文本约消耗700-1000个Token（因标点和换行而异），而同等语义的英文约400-600个Token。工程师在设计RAG系统的chunk策略时，必须以Token数而非字符数作为切分依据，避免超出模型的最大输入长度（如GPT-4的128K Token上下文）。

**Prompt注入与安全**：攻击者可以构造包含特殊Token序列的输入，例如在用户提交的文本中嵌入`<|im_end|>`（ChatML格式的对话结束符），欺骗模型认为系统Prompt已结束，从而绕过安全指令。防御方案包括在将用户输入传入模型前，检测并转义这些特殊Token ID。

**代码与多语言场景**：Python代码中的缩进（多个空格）在tiktoken中被高效编码——4个空格是一个Token（"    "→单个ID），这使得代码的Token密度接近英文散文。相反，中文代码注释、日文、阿拉伯文的Token效率明显低于英文，开源模型需要专门在多语言语料上扩展词表以提升效率（如在LLaMA基础上训练中文增强模型时，通常将词表扩充至65,000甚至更大）。

## 常见误区

**误区一：Token等于词或字**。许多初学者认为一个Token对应一个中文字或英文单词。实际上，"tokenization"这个英文词在cl100k_base中是一个单一Token，而"ChatGPT"可能被切为["Chat","G","PT"]三个Token。单个汉字可能对应一个Token，也可能与相邻汉字合并，或被切为多个UTF-8字节Token。不能用字符数除以某个固定系数来估算Token数，必须实际编码才能准确计算。

**误区二：所有模型使用相同的Tokenizer**。BERT的WordPiece与GPT的BPE产生完全不同的切分结果，且两者词表互不兼容。用BERT的Tokenizer处理输入再喂给GPT模型，会产生错误的ID序列。每个预训练模型都绑定了专属的Tokenizer配置（vocab.json + merges.txt），这是模型文件的必要组成部分，不可替换。

**误区三：Tokenization是可逆的无损变换**。对于规范的UTF-8文本，BPE确实是可逆的（Token序列可完整还原原始文本）。然而，某些Tokenizer在处理非规范Unicode（如单独的代理对、非法UTF-8序列）时会静默替换或丢失字节，导致decode后的文本与原始输入不完全一致。在构建需要精确文本还原的系统（如文档编辑器、代码生成后的执行）时，这一点需要特别注意。

## 知识关联

理解Tokenization需要先掌握Transformer架构：Transformer的Embedding层本质上是一个形状为`[vocab_size, d_model]`的查找矩阵，输入的Token ID序列通过此矩阵映射为稠密向量——这正是Embedding Models的起点。词表大小（vocab_size）直接决定了Embedding层的参数量，GPT-3的50,257×12,288参数Embedding矩阵占总参数量的约20%。

Tokenization与LLM水印技术的关联体现在：Token概率分布是施加水印信号的天然位置。绿色Token（Green Token）水印方案（Kirchenbauer等，2023）在每次采样前将词表随机分为"绿色"和"红色"两组，强制提高绿色Token的生成概率，使生成文本在统计上可被检测。这一方案的粒度完全依赖于Tokenizer的切分方式——词表越大，水印信号越精细，但同时也更难被人工察觉。