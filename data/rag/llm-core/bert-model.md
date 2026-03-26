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

BERT（Bidirectional Encoder Representations from Transformers）由Google于2018年10月发布，是首个将Transformer编码器堆叠应用于预训练语言模型的里程碑式工作。与此前单向语言模型不同，BERT通过同时利用句子左右两侧的上下文信息生成词表示，将当时11项NLP基准任务的最优成绩全面刷新，在GLUE基准测试中将综合得分从80.5分提升至82.1分。

BERT的命名中"双向"二字是其核心特征。传统GPT等模型只能从左到右逐词预测，ELMo虽然使用了双向LSTM但仅是简单拼接两个方向的表示，而BERT通过Masked Language Model任务在同一个Transformer编码器中真正实现了双向上下文融合。这种设计使得BERT在需要理解全局语义的任务（如阅读理解、情感分析、命名实体识别）上表现出色，成为当时预训练-微调范式的代表性架构。

编码器模型的本质是：给定完整输入序列，为序列中每个位置生成包含全局上下文信息的稠密向量表示。这与解码器模型的自回归生成逻辑截然不同——编码器不需要逐步生成输出，而是"一次看完全文"，因此更擅长分类、匹配、抽取等理解型任务，而非文本生成型任务。

---

## 核心原理

### 双向Transformer编码器堆叠结构

BERT的基础版（BERT-Base）由12层Transformer编码器堆叠而成，每层包含768维隐层、12个注意力头，总参数量约1.1亿；大版本（BERT-Large）则有24层、1024维隐层、16个注意力头，总参数量约3.4亿。每个编码器层执行多头自注意力（Multi-Head Self-Attention）操作，注意力权重计算公式为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中 $d_k$ 为每个注意力头的维度（BERT-Base中 $d_k = 64$），除以 $\sqrt{d_k}$ 是为了防止点积值过大导致softmax梯度消失。编码器中不存在掩码（Mask）对未来位置的屏蔽，因此每个位置可以自由关注序列中所有其他位置，这正是双向性的实现机制。

### 预训练任务：MLM与NSP

BERT使用两个自监督预训练任务。**Masked Language Model（MLM）**随机将输入token中的15%进行遮蔽处理：其中80%替换为`[MASK]`标记，10%替换为词表中的随机词，10%保持原词不变。这种混合策略避免了模型只学会预测`[MASK]`标记而忽略真实词汇的分布。模型需要根据被遮蔽位置的上下文预测原始token，从而迫使编码器学习深层语义表示。

**Next Sentence Prediction（NSP）**任务输入两个句子A和B，50%概率B是A的真实后续句，50%概率B是随机采样句，模型通过`[CLS]`位置的向量预测二者是否连续。NSP任务使BERT能够理解句间关系，这对问答（QA）和自然语言推理（NLI）任务至关重要。值得注意的是，后续研究（如RoBERTa，2019年）证明NSP任务效果存疑，去掉后性能不降反升。

### 输入表示：三种Embedding的叠加

BERT的输入向量由三部分相加构成：**Token Embedding**（词向量，词表大小约30,000词）、**Segment Embedding**（区分句子A/B的标记，仅有两个向量EA和EB）以及**Position Embedding**（位置编码，支持最长512个token，采用可学习参数而非正弦函数）。三者相加后经过Layer Normalization输入第一层编码器。`[CLS]`token始终位于输入序列首位，其最终隐层向量用于序列级分类任务；`[SEP]`token用于分隔句子A和B。

---

## 实际应用

**文本分类与情感分析**：将`[CLS]`位置的768维向量接一个线性分类层，在SST-2（斯坦福情感树库）上微调后准确率达到93.5%，超越此前最优方法约1个百分点。

**命名实体识别（NER）**：将BERT每个token位置的输出向量接CRF层或简单线性层，在CoNLL-2003英文NER数据集上F1达到92.8%，相比BiLSTM-CRF提升约1.5%。这类任务直接利用了编码器对每个token的上下文表示优势。

**抽取式问答（SQuAD）**：给定文章和问题，BERT将问题和文章拼接后输入，通过预测每个文章token是"答案起始位置"或"答案终止位置"的概率来抽取答案。在SQuAD 1.1测试集上F1达到93.2分，首次在部分指标上超越人类（91.2分）。

**语义相似度与句对匹配**：将两个句子以`[CLS] 句A [SEP] 句B [SEP]`格式输入，利用`[CLS]`向量判断语义相似性。在MNLI任务上准确率达到86.7%（matched）。

---

## 常见误区

**误区一：BERT可以直接用于文本生成**。BERT是纯编码器架构，在预训练时看到的是完整句子，不具备自回归逐词生成能力。如果强行用MLM方式生成文本，需要多轮迭代且质量极差。文本生成应使用GPT等解码器模型，或使用T5、BART等编码器-解码器架构。

**误区二：BERT输入长度可以任意扩展**。BERT的Position Embedding最多支持512个token，这是预训练时固定的可学习参数矩阵。超过512个token的文本无法直接输入，必须截断或使用滑动窗口策略。Longformer（2020年）通过稀疏注意力机制将这一限制扩展到4096个token，专门解决长文档问题。

**误区三：微调BERT时只需训练分类头**。实验证明，在下游任务微调时同步更新BERT全部参数（而不是冻结底层）通常效果更好。Google原始论文推荐的学习率为2e-5到5e-5，批大小为16或32，训练轮数为3至4轮。仅训练分类头相当于将BERT作为固定特征提取器，在大多数任务上会损失1-3个百分点的性能。

---

## 知识关联

**与Transformer架构的关系**：BERT直接继承了Transformer中的多头自注意力、前馈网络、残差连接和Layer Normalization结构，但仅使用了Transformer的编码器部分（原始Transformer论文中的左半部分），完全舍弃了解码器及其交叉注意力机制。理解编码器中自注意力不设因果掩码这一点，是区分BERT与GPT系列架构的关键差异所在。

**衍生的编码器模型家族**：RoBERTa（2019年，Meta）通过更大批次（8192）、更多数据（160GB文本）、动态MLM掩码和去除NSP任务对BERT进行改进；ALBERT（2019年，Google）通过参数共享和嵌入矩阵分解将BERT-Large参数量压缩至1800万；DistilBERT（2019年，HuggingFace）通过知识蒸馏将BERT-Base压缩为6层，保留97%性能的同时速度提升60%。

**通往GPT与解码器模型的对比**：编码器（BERT）与解码器（GPT）的根本差异在于注意力掩码策略和预训练目标——编码器使用双向注意力和MLM目标，适合理解任务；解码器使用因果掩码和自回归语言建模目标（预测下一个token），适合生成任务。理解这一对比，是掌握Encoder-Decoder架构（如T5）设计动机的前提。