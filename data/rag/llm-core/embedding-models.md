---
id: "embedding-models"
concept: "Embedding Models"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 6
is_milestone: false
tags: ["LLM", "NLP"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 嵌入模型（Embedding Models）

## 概述

嵌入模型是一类专门将离散符号（词、句子、文档、图像等）映射到连续稠密向量空间的神经网络。与生成式大模型不同，嵌入模型的输出不是文字序列，而是一个固定维度的实值向量（如768维或1536维），该向量在语义空间中的几何位置编码了输入内容的含义，语义相近的输入在空间中彼此靠近。

嵌入模型的思想可追溯至2013年Google发布的Word2Vec，它首次证明了"国王 - 男人 + 女人 ≈ 王后"这类向量运算的语义有效性。2018年BERT（Bidirectional Encoder Representations from Transformers）的出现将嵌入质量提升到全新层次——通过双向Transformer编码器和遮蔽语言模型（MLM）预训练，BERT生成的上下文感知嵌入远优于静态词向量。2022年后，以`text-embedding-ada-002`和`E5`系列为代表的大规模句子嵌入模型在检索增强生成（RAG）场景中成为基础设施级别的组件。

嵌入模型在工程中至关重要，因为它将语义相似性问题转化为可计算的几何距离问题：余弦相似度、点积或欧氏距离均可在毫秒级别完成对百万条记录的检索，而这是关键词匹配无法实现的语义泛化能力。

## 核心原理

### 编码器架构与池化策略

嵌入模型通常使用Transformer编码器（而非解码器）作为骨干网络。输入文本经过Tokenization后，送入多层自注意力层，每个Token获得一个上下文表示向量。问题在于：如何将变长的Token序列压缩成单一固定维向量？

主流池化策略有三种：
- **[CLS]Token池化**：取第0个位置`[CLS]`对应的输出向量，BERT原始设计采用此方案。
- **均值池化（Mean Pooling）**：对所有Token向量取算术平均，`sentence-transformers`库中大多数模型默认使用此策略，实验表明它在语义检索任务上优于CLS池化。
- **加权均值池化**：按Token的注意力权重或位置权重进行加权平均，对长文档效果更好。

### 训练目标：对比学习与三元组损失

现代嵌入模型的训练核心是**对比学习（Contrastive Learning）**。最广泛使用的损失函数是**InfoNCE损失**：

$$\mathcal{L} = -\log \frac{\exp(\text{sim}(q, k^+)/\tau)}{\exp(\text{sim}(q, k^+)/\tau) + \sum_{i=1}^{N}\exp(\text{sim}(q, k_i^-)/\tau)}$$

其中 $q$ 为查询向量，$k^+$ 为正样本向量，$k_i^-$ 为负样本向量，$\tau$ 为温度超参数（通常取0.05~0.1），$N$ 为批内负样本数量。增大批次大小（如SimCSE使用256或更大批次）能引入更多难负样本，显著提升模型质量。

另一种经典方案是**三元组损失（Triplet Loss）**：
$$\mathcal{L} = \max(0, \|f(a)-f(p)\|_2 - \|f(a)-f(n)\|_2 + \alpha)$$
其中 $\alpha$ 是安全边距（margin），通常设为0.1~0.5。

### 领域特定微调方法

通用嵌入模型在医疗、法律、代码等垂直领域往往表现欠佳，需要领域微调。主要范式如下：

**有监督对比微调**：收集领域内的（查询, 正文档）正样本对，使用上述InfoNCE损失在预训练嵌入模型上继续训练。`BGE-large-zh`中文嵌入模型即采用此路径，在C-MTEB基准上超越了OpenAI的`text-embedding-ada-002`。

**硬负样本挖掘（Hard Negative Mining）**：随机负样本往往过于简单，模型无法从中学到精细区分能力。具体做法是先用弱模型检索出Top-K候选，从中选取与正样本相似但不相关的文档作为难负样本。`E5-mistral-7b-instruct`模型就使用了专门的难负样本挖掘流程，在BEIR基准上取得了显著提升。

**LoRA参数高效微调**：当基础模型规模较大（如7B参数的LLM用作编码器）时，全量微调成本极高。LoRA将可训练矩阵分解为两个低秩矩阵 $W = W_0 + BA$（其中 $r \ll \min(d_{in}, d_{out})$），通常仅需训练原参数量的0.1%~1%即可达到接近全量微调的效果。

## 实际应用

**RAG系统中的向量检索**：在检索增强生成中，嵌入模型承担将用户查询和知识库文档映射到同一语义空间的任务。典型部署流程是：离线用嵌入模型对所有文档分块（Chunk，通常512Token以内）编码，存入Faiss或Milvus向量数据库；在线对用户查询编码后执行近似最近邻（ANN）搜索，返回Top-K相关文档块。

**双编码器 vs 交叉编码器**：嵌入模型属于**双编码器（Bi-Encoder）**架构——查询和文档分别独立编码，可提前离线计算文档嵌入。这与**交叉编码器（Cross-Encoder）**形成对比，后者将查询和文档拼接后联合计算相关性分数，精度更高但无法离线缓存，速度慢100倍以上。实际工程中常用"双编码器粗排 + 交叉编码器精排"的两阶段架构。

**多模态嵌入**：OpenAI的CLIP模型将图像和文字映射到同一384维向量空间，使得文字查询可以直接检索图片。其训练使用4亿（图像, 文字）对，对比学习目标与文本嵌入模型完全一致。

## 常见误区

**误区一：嵌入维度越高，质量越好**。维度是模型架构的固有属性，不是调节质量的旋钮。`text-embedding-3-small`（1536维）与`text-embedding-ada-002`（1536维）维度相同，但前者在MTEB基准上平均得分高出约5%，差异来自训练数据和目标函数，而非维度。此外，OpenAI的`text-embedding-3`系列支持维度截断（Matryoshka Representation Learning，MRL），可将1536维嵌入截断到256维而仅损失极小精度，说明维度与质量并非线性关系。

**误区二：直接用生成式大模型（如GPT-4）的最后一层隐状态作嵌入**。自回归解码器的每个Token只能"看到"其左侧内容，导致最后一个Token的隐状态严重依赖序列长度和结尾词汇，语义表示质量较差。实验证明，未经对比学习微调的LLM解码器嵌入在语义检索任务上甚至不如`bert-base`。真正要用LLM做嵌入，需使用`E5-mistral-7b`这类专门在解码器上叠加对比学习训练的模型。

**误区三：领域微调总是比通用模型好**。若领域标注数据量不足（少于数千对），微调反而可能导致灾难性遗忘（Catastrophic Forgetting），模型在目标领域小幅提升的同时，在通用场景下性能大幅下降。此时应优先考虑改进提示工程或使用指令型嵌入模型（如`E5-instruct`系列），通过在查询前添加任务描述指令（如"Represent this sentence for searching relevant passages:"）来激活模型中已有的语义区分能力。

## 知识关联

嵌入模型的质量直接依赖**分词与Tokenization**：BPE分词的词表大小决定了嵌入层的规模，而子词切分策略影响模型对罕见词和领域术语的表示能力。中文嵌入模型（如`BGE`系列）通常使用字粒度或字词混合词表，以应对中文无空格的特性。

从**文本嵌入（Embedding）**的基础概念来看，嵌入模型是将静态词向量（Word2Vec、GloVe）进化为动态上下文感知表示的关键工程实体。Word2Vec中"苹果"在所有语境下只有一个向量，而BERT类嵌入模型在"苹果手机"和"苹果树"两种语境下会生成截然不同的向量，这是句子嵌入模型在实际检索任务中能大幅超越词袋模型的根本原因。

在AI工程实践中，嵌入模型的选型需要在**检索延迟、嵌入维度、领域适配性和许可证**四个维度综合权衡：开源的`BGE-m3`支持8192Token长文档嵌入，可处理整篇合同文本；而`text-embedding-3-small`通过API调用无需自行部署，适合快速原型验证。