---
id: "text-embedding"
concept: "文本嵌入(Embedding)"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 6
is_milestone: false
tags: ["NLP", "RAG"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 文本嵌入（Embedding）

## 概述

文本嵌入是将离散的文本符号（单词、句子、段落或整篇文档）映射为连续高维向量空间中的稠密数值向量的技术。该向量空间中，语义相近的文本在欧氏距离或余弦相似度上也相近——例如"猫"和"猫咪"的向量距离远小于"猫"和"汽车"的距离。与传统的 One-Hot 编码（词汇表大小可达数十万维，每个向量仅有一个维度为1）相比，Embedding 通常使用 128 到 4096 维的稠密向量，以极低的空间代价编码丰富的语义信息。

Embedding 技术的奠基性工作可追溯至 2013 年 Google 发布的 Word2Vec 模型，它首次证明了词向量可以捕获类比关系（"king - man + woman ≈ queen"）。此后，2018 年的 BERT 引入了上下文相关嵌入，同一词在不同句子中产生不同向量，解决了多义词问题。2019 年至今，以 Sentence-BERT（SBERT）为代表的句子级 Embedding 模型将嵌入单元从词提升至整段文本，使其直接适用于 RAG 系统的语义检索任务。

在 RAG 系统中，Embedding 是连接用户查询与知识库文档的桥梁。知识库中每个文本块（Chunk）被预先编码为向量存入向量数据库；用户提问时，问题也被同一模型编码为查询向量；系统通过向量相似度找出最相关的文档块，再交给大语言模型生成回答。若 Embedding 质量低劣，即便后续检索算法再精良，召回的文档也会偏离主题，导致生成结果幻觉增多。

---

## 核心原理

### 向量空间与语义几何

文本 Embedding 的本质是学习一个函数 $f: \text{文本} \rightarrow \mathbb{R}^d$，其中 $d$ 是向量维度。优质的 Embedding 满足**语义保持性**：若文本 $A$ 和 $B$ 语义相似，则 $\cos(f(A), f(B))$ 接近 1。余弦相似度公式为：

$$\text{sim}(A, B) = \frac{f(A) \cdot f(B)}{\|f(A)\| \cdot \|f(B)\|}$$

该公式忽略向量模长，仅关注方向差异，因此适合长短不一的文本比较。除余弦相似度外，内积相似度（dot product）在归一化向量的情况下与余弦相似度等价，Pinecone 等向量数据库默认采用此方式加速检索。

### Embedding 模型的训练目标

主流 Embedding 模型使用**对比学习**训练：给定一对正样本（语义相关的文本对），模型被训练拉近其向量距离，同时推远负样本（语义无关文本对）的距离。具体使用的损失函数为 **InfoNCE（Noise-Contrastive Estimation）**：

$$\mathcal{L} = -\log \frac{\exp(\text{sim}(q, k^+)/\tau)}{\exp(\text{sim}(q, k^+)/\tau) + \sum_{i=1}^{N}\exp(\text{sim}(q, k_i^-)/\tau)}$$

其中 $q$ 为查询向量，$k^+$ 为正样本向量，$k_i^-$ 为第 $i$ 个负样本向量，$\tau$ 为温度系数（典型值 0.05～0.1）。温度越低，模型对相似度差异越敏感，但训练也更不稳定。

### 主流 Embedding 模型的维度与性能对比

| 模型 | 向量维度 | MTEB 均分（2024） | 适用场景 |
|---|---|---|---|
| text-embedding-3-small (OpenAI) | 1536 | 62.3 | 高并发低成本 |
| text-embedding-3-large (OpenAI) | 3072 | 64.6 | 高精度检索 |
| bge-large-zh-v1.5 (BAAI) | 1024 | 中文最优 | 中文RAG |
| E5-mistral-7b-instruct | 4096 | 66.6 | 多语言复杂任务 |

BAAI（北京智源人工智能研究院）发布的 BGE 系列专为中文语料优化，在 MTEB 中文子集上表现优于 OpenAI 模型，是中文 RAG 系统的首选。

### 分块策略对 Embedding 质量的影响

Embedding 的输入长度有严格上限——大多数模型支持 512 Token，超长文本会被截断导致后半段信息丢失。因此，在对文档进行 Embedding 之前必须进行文本分块（Chunking）。Chunk 过短（如 50 字）会使单个向量语义不完整；Chunk 过长（如 2000 字）会使向量被均值化，降低检索精度。实践中，512～1024 字符的 Chunk 配合 10%～20% 的滑动窗口重叠是常见的平衡点。

---

## 实际应用

**企业知识库 QA 系统**：某法律科技公司将 5000 份合同文本按条款分块后使用 bge-large-zh-v1.5 编码，存入 Milvus 向量数据库。律师输入"违约金条款适用条件"后，系统在 50ms 内检索到语义最近的 5 个条款片段，再由 GPT-4 综合回答，准确率达 89%，远高于关键词检索的 62%。

**多模态 Embedding 扩展**：OpenAI 的 CLIP 模型将图像和文本映射到同一 512 维向量空间，使得"一只红色的猫"的文字向量与对应图片的向量相近，可直接进行文图跨模态检索，而无需文字描述图片内容。这一特性在电商图文混合知识库中已有大规模应用。

**增量更新场景**：由于 Embedding 模型版本迭代（如 OpenAI 从 Ada-002 升级至 text-embedding-3），旧版本向量与新版本查询向量处于不同几何空间，**不可混用**。企业需在模型升级时对全量知识库重新向量化，这是运维成本的重要考量，通常需要提前规划批量嵌入的 API 成本与时间窗口。

---

## 常见误区

**误区一：Embedding 向量可以跨模型直接比较**

不同模型训练目标、词表和归一化方式各异，其输出向量处于完全不同的空间中。用 bge-large-zh 编码的文档向量与用 text-embedding-3-small 编码的查询向量做余弦相似度，其结果无任何语义意义。RAG 系统中，**索引阶段和查询阶段必须使用完全相同的 Embedding 模型**，包括版本号。

**误区二：向量维度越高，检索效果越好**

4096 维的 E5-mistral 在通用 MTEB 上均分优于 1536 维的 text-embedding-3-small，但在特定垂直领域（如中文医疗）未经领域微调的高维通用模型可能反而不如低维领域专用模型。更高维度还意味着更高的存储成本和检索延迟——向量维度翻倍，最近邻搜索的计算量接近翻倍。

**误区三：Embedding 模型能直接处理表格和代码**

大多数 Embedding 模型在训练时以自然语言句子为主，对 Markdown 表格、SQL 代码或 JSON 结构的编码效果差。例如将一张 10 列的 CSV 表格作为字符串输入，模型往往无法区分列名与数值的语义关系。对结构化数据应先转为自然语言描述（"第三季度收入为 120 万元"），再进行 Embedding。

---

## 知识关联

学习文本 Embedding 需要具备 RAG 检索增强生成的整体架构认知，才能理解为何需要将文档预先向量化以及查询向量如何触发检索流程。

掌握 Embedding 原理后，**向量数据库（Pinecone/Milvus）**是自然的下一步：这些数据库提供了 HNSW、IVF-PQ 等近似最近邻（ANN）算法，使十亿级向量的检索延迟控制在毫秒量级。**相似度搜索与重排**在 Embedding 检索的基础上引入 Cross-Encoder 对召回结果重新打分，弥补 Bi-Encoder（即 Embedding 模型）在精排阶段的准确率损失。**Embedding Models** 专题将深入对比不同训练范式（MLM、SimCSE、RetroMAE）对下游检索任务的影响。**HyDE Retrieval**（Hypothetical Document Embeddings）则利用 Embedding 的几何特性，先让 LLM 生成一段假设性答案，再将该假设答案的向量用于检索，在零样本场景下显著提升召回率。