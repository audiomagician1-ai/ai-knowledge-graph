---
id: "reranking"
concept: "Reranking"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 6
is_milestone: false
tags: ["RAG"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Reranking（重排序）

## 概述

Reranking（重排序）是RAG管道中在初步检索之后、生成之前插入的一个精化阶段：系统先用向量相似度从知识库中捞出候选文档（通常50～200条），再用计算成本更高但精度更高的模型对这批候选文档重新打分排序，最终只将排名最靠前的K条（通常3～10条）送入LLM生成答案。这一"粗检索＋精排"的两阶段策略，直接来自信息检索领域的Learning to Rank（L2R）传统，并在2019年随BERT类Cross-Encoder模型的普及而被引入神经检索系统。

从历史渊源看，早期的Reranking依赖BM25等词频统计模型做重排，但这类方法无法捕捉语义相关性。2019年Nogueira与Cho发表的论文《Passage Re-ranking with BERT》证明，将查询和文档拼接后输入BERT（`[CLS] query [SEP] doc [SEP]`）所得的相关性分数，比双塔向量内积精度高出约8～12个MRR@10百分点。这一发现确立了Cross-Encoder作为Reranking骨干模型的地位，也成为现代RAG系统普遍采用的范式。

Reranking对RAG质量的提升是可量化的：在标准检索基准BEIR上，单纯向量检索的NDCG@10约为0.42～0.48，加入Cross-Encoder Reranking后可提升至0.55～0.63。对于生成质量，Reranking能显著降低"幻觉率"——因为送入LLM的上下文噪声减少，模型不再被低相关文档误导。

---

## 核心原理

### Bi-Encoder与Cross-Encoder的本质差异

向量检索阶段使用的是**Bi-Encoder**：查询和文档分别独立编码为向量，相关性通过内积或余弦相似度计算。这种方式可预先计算所有文档向量并做ANN（近似最近邻）搜索，延迟极低，但查询和文档之间没有直接的token级交互，导致细粒度语义判断不准确。

Reranking阶段使用的是**Cross-Encoder**：查询和文档拼接为单一序列 `[CLS] q_1...q_n [SEP] d_1...d_m [SEP]` 后输入Transformer，`[CLS]`位置的输出经线性层映射为一个相关性分数 `s = W·h_[CLS] + b`。由于每一层的自注意力机制都同时看到查询和文档的所有token，模型可以建立精确的词级交互关系——例如识别出查询中的"苹果公司"和文档中的"Apple Inc."指向同一实体。代价是：Cross-Encoder无法预计算，每次推理必须将查询与每个候选文档单独拼对，延迟随候选数量线性增长。

### 常用Reranking模型

**ms-marco-MiniLM-L-6-v2** 是目前RAG工程中最常用的轻量级Reranking模型之一，基于MiniLM（6层、384维）在MS MARCO段落排序数据集上微调，在CPU上对100个候选文档的重排延迟约为200～400ms。**Cohere Rerank API**提供托管服务，其`rerank-english-v3.0`模型在BEIR的平均NDCG@10上达到0.596，适合快速集成。**BGE-Reranker-Large**（BAAI发布，2023年）是中文场景下性能最强的开源选项，在CMTEB排序任务上NDCG@10约为0.72。

### 分数归一化与截断策略

Cross-Encoder输出的原始分数是未归一化的logit，不同模型的量纲差异很大。常见的处理方式有两种：

- **Sigmoid归一化**：`score = 1 / (1 + exp(-logit))`，将分数压缩到(0,1)区间，便于设置阈值过滤（如丢弃score < 0.3的文档）。
- **Top-K截断**：无论绝对分数如何，只保留重排后前K条。K的选择直接影响LLM的上下文长度使用率；GPT-4o的128k上下文并不意味着K越大越好——实验表明K=5时答案质量往往优于K=20，因为无关文档的稀释效应（"Lost in the Middle"现象，Liu et al., 2023）会降低模型对关键信息的注意力权重。

### 混合Reranking（Reciprocal Rank Fusion）

当系统同时存在向量检索和BM25检索两条候选列表时，可先用**RRF（Reciprocal Rank Fusion）**融合：

```
RRF_score(d) = Σ_r 1 / (k + rank_r(d))
```

其中k通常取60，`rank_r(d)`是文档d在第r个检索列表中的排名。RRF融合后再送入Cross-Encoder做最终重排，这种三阶段策略（稀疏检索＋密集检索→RRF→Cross-Encoder Reranking）在多个RAG评测中效果优于任何单一方法。

---

## 实际应用

**LangChain中的Cohere Reranking集成**：

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

compressor = CohereRerank(model="rerank-english-v3.0", top_n=5)
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_store.as_retriever(search_kwargs={"k": 50})
)
```

这段代码中，向量库先返回50个候选，Cohere Rerank重排后只保留top-5送入链路。

**医疗问答场景**：某医疗RAG系统中，用户询问"二甲双胍的禁忌症"，向量检索返回的top-1文档是关于二甲双胍的"适应症"（余弦相似度0.87），因为两个词在语义空间接近。Cross-Encoder重排后，明确描述"肾功能不全（eGFR < 30）禁用"的文档升至top-1，直接避免了潜在的生成错误。

**延迟预算分配**：在要求端到端响应时间 ≤ 2秒的生产环境中，典型分配为：向量检索（ANN）≤ 50ms，Reranking（MiniLM，候选数=100）≤ 400ms，LLM生成 ≤ 1500ms。若Reranking成为瓶颈，可将候选数压缩至30或改用量化版模型（INT8量化可将MiniLM推理速度提升约1.7倍）。

---

## 常见误区

**误区一：向量相似度高等于相关性高，Reranking可有可无。**
余弦相似度衡量的是向量空间中的几何距离，而非语义相关性的完整度量。文档可能因为包含大量与查询词汇重叠的无关内容而获得高余弦分数（称为"词汇陷阱"）。实验数据表明，在MS MARCO数据集上，Bi-Encoder检索的top-1准确率（MRR@10）约为0.33，加入Cross-Encoder重排后提升至0.39，提升幅度约18%——这在生产系统中是显著差异。

**误区二：Reranking模型直接从头训练，或用通用BERT微调即可达到最佳效果。**
高质量的Reranking模型依赖大规模的**查询-文档相关性标注对**，而非简单的文本分类数据。MS MARCO拥有约500万条人工标注的查询-段落相关性对，这种规模的数据决定了Reranking模型的下限。用少量领域数据从头训练的Cross-Encoder往往不如在MS MARCO预训练后做领域微调（fine-tuning）的版本，因为通用相关性判断能力需要海量数据才能建立。

**误区三：Reranking必然改善最终生成质量，分数越高越好。**
Reranking优化的是**文档级相关性**，但LLM生成质量还受上下文组合效应影响。若5条高相关文档中包含相互矛盾的信息，LLM可能产生混乱的答案——此时需要配合上下文压缩或冲突检测策略。另外，Reranking分数是针对单个查询-文档对的局部判断，无法保证多文档组合后信息互补性最大化。

---

## 知识关联

**前置概念：相似度搜索与重排** 提供了向量内积和余弦相似度作为粗召回的基础，Reranking正是针对这一粗召回阶段精度不足的直接补救措施；理解ANN索引（HNSW、IVF）的召回率限制，有助于确定Reranking的候选集大小。**RAG管道架构**定义了检索器与生成器之间的接口规范，Reranking模块插入在`retriever.invoke()`和`llm.invoke()`之间，需要理解整体数据流才能正确集成。

**后续概念：RAG评估（Ragas）**可以量化Reranking的实际收益——Ragas框架中的`context_precision`和`context_recall`指标直接反映重排后上下文质量，是调整候选数K和截断阈值的核心依据。**上下文压缩**是Reranking的自然延伸：Reranking在文档级别筛选，上下文压缩则在句子/段落级别进一步裁剪每个文档内部的冗余内容，两者串联使用