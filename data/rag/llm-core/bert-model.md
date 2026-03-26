---
id: "bert-model"
concept: "BERT与编码器模型"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["NLP"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# BERT与编码器模型

## 概述

BERT（Bidirectional Encoder Representations from Transformers）由Google研究员Jacob Devlin等人于2018年10月发布，论文标题为《BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding》。它是第一个证明双向预训练语言模型可以在11项NLP任务上同时取得最优成绩的模型，发布时在GLUE、SQuAD v1.1、SQuAD v2.0、SWAG四个基准测试上全部刷新了当时的最高分。

BERT的革命性在于它只使用Transformer架构中的**编码器（Encoder）部分**，完全抛弃了解码器。这种设计选择意味着模型可以在处理每个词元时同时关注输入序列的左侧和右侧上下文，而不像GPT那样只能从左到右单向处理。BERT-Base版本包含12层Transformer编码器、12个注意力头、768维隐藏层，共1.1亿参数；BERT-Large则包含24层、16个注意力头、1024维隐藏层，共3.4亿参数。

编码器模型这一类别（也称"自编码模型"或"掩码语言模型"）的核心价值在于生成**上下文相关的双向表示（contextual bidirectional representations）**，这使其特别适合需要理解完整输入语义的任务，如文本分类、命名实体识别、阅读理解等判别式任务，而非生成式任务。

---

## 核心原理

### 双向注意力机制与编码器堆叠

BERT的编码器层每层包含两个子模块：多头自注意力（Multi-Head Self-Attention）和前馈网络（Feed-Forward Network），每个子模块后接层归一化（LayerNorm）和残差连接。在自注意力计算中，注意力分数公式为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中 $d_k$ 为键向量维度（BERT-Base中为64，即768/12）。**关键区别**在于：BERT的自注意力在计算时没有任何因果掩码（causal mask），每个位置的词元可以完整地关注序列中所有其他位置，因此同一句子中"苹果很好吃"与"苹果发布新品"里的"苹果"会产生完全不同的向量表示。

### 预训练任务：MLM与NSP

BERT使用两个创新的预训练任务联合训练：

**掩码语言模型（Masked Language Model, MLM）**：随机遮蔽输入序列中15%的词元，其中80%替换为`[MASK]`标记，10%替换为随机词元，10%保持原词不变。模型需要从双向上下文预测被遮蔽的原始词元。这一设计解决了传统语言模型只能单向预测的限制，但也引入了预训练与微调的分布偏差（`[MASK]`标记在下游任务中不存在）。

**下一句预测（Next Sentence Prediction, NSP）**：输入两句话A和B，50%概率B是A的真实后续句，50%是随机抽取的句子，模型需二分类判断。NSP旨在让模型学习句间关系，用于问答和自然语言推理任务，但后来的研究（如RoBERTa，2019年）证明NSP任务实际上对性能提升作用有限甚至有害，去掉NSP后效果更好。

### 特殊词元与输入表示

BERT的输入向量是三种嵌入的逐元素相加：
1. **词元嵌入（Token Embeddings）**：来自30,522词大小的WordPiece词表
2. **位置嵌入（Position Embeddings）**：最大支持512个位置的可学习嵌入（非正弦固定编码）
3. **句子段落嵌入（Segment Embeddings）**：区分句子A和句子B，值为0或1

输入序列必须以`[CLS]`（Classification）标记开头，句子间及末尾以`[SEP]`（Separator）标记分隔。`[CLS]`对应的最终隐藏状态被用作整个序列的聚合表示，专门用于分类任务的微调。

---

## 实际应用

**文本分类微调**：在`[CLS]`向量上接一个线性分类层 $W \in \mathbb{R}^{H \times K}$（H为隐藏维度768，K为类别数），仅需标注数据即可在3-5个epoch内完成微调。使用BERT-Base在SST-2情感分类数据集上微调后准确率可达93.5%。

**命名实体识别（NER）**：对每个词元的输出隐藏状态接序列标注层（通常配合CRF），BERT在CoNLL-2003英文NER数据集上F1达到92.8%，超越之前最优方法约0.4个百分点。注意WordPiece分词会将一个词拆分为多个子词，NER中通常只取每个词第一个子词的表示用于标注。

**阅读理解（抽取式问答）**：以`[CLS] 问题 [SEP] 段落 [SEP]`格式输入，对段落中每个词元预测两个概率：是答案起始位置的概率和是答案终止位置的概率，使用两个独立的线性层。在SQuAD v1.1上BERT-Large的F1分数达到93.2%，首次超越人类水平（91.2%）。

**语义相似度**：将两个句子通过`[CLS] 句A [SEP] 句B [SEP]`格式输入，利用`[CLS]`输出向量判断两句是否语义等价（如微软释义语料库MRPC任务，BERT准确率88.9%）。

---

## 常见误区

**误区一：认为BERT可以直接用于文本生成任务**。由于BERT只有编码器、无自回归解码能力，它无法自然地逐词生成文本。强行用BERT做生成时需要借助特殊的`[MASK]`填充策略（如BERT-gen），效果远不如GPT类解码器模型。BERT擅长的是将完整输入映射为固定表示，而非自回归地产生输出序列。

**误区二：认为`[CLS]`向量天然是优质的句子语义表示**。直接用未经微调的BERT的`[CLS]`向量做句子相似度计算，效果往往很差，甚至不如简单平均词向量。这是因为BERT预训练时`[CLS]`专为NSP任务优化，而非通用语义相似度。Sentence-BERT（SBERT，2019年）专门针对此问题，用孪生网络结构和对比学习对BERT进行有监督微调，才获得高质量句子嵌入。

**误区三：混淆MLM中15%遮蔽比例的具体操作细节**。许多人只记得"遮蔽15%"，忘记其中80/10/10的三元分配（`[MASK]`/随机词/原词）。保留10%原词的目的是给模型提供真实词元的表示偏置，避免模型在微调时遇到从不出现`[MASK]`的输入时产生表示漂移；替换10%为随机词则迫使模型不能仅依赖当前词元自身，必须利用上下文。

---

## 知识关联

**依赖Transformer编码器架构**：理解BERT需要熟悉Transformer中的多头注意力计算、残差连接、LayerNorm和前馈网络的具体结构。BERT本质上是将Transformer编码器堆叠12或24层并以大规模语料（BookCorpus + 英文维基百科，共约33亿词）进行预训练的结果。

**后续演进与改进**：RoBERTa（Facebook，2019年）去除NSP、增大批次（从256增至8000）、动态掩码，在相同参数规模下显著优于原始BERT；ALBERT（Google，2019年）引入参数共享和嵌入分解将参数量降低18倍；DistilBERT（Hugging Face，2019年）通过知识蒸馏保留97%性能同时减少40%参数和60%推理时间。这些改进模型均属于"编码器模型"家族。

**与GPT解码器模型的对比关系**：BERT使用双向注意力、适合判别任务、以微调（fine-tuning）范式为主；GPT使用单向因果注意力、适合生成任务、以提示（prompting）范式为主。两类模型的设计哲学差异直接催生了后续编码器-解码器融合模型（如T5、BART）的探索，是理解大模型发展路径的核心分叉点。