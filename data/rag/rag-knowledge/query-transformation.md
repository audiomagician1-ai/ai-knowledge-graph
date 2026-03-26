---
id: "query-transformation"
concept: "查询转换"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 4
is_milestone: false
tags: ["query-rewrite", "decomposition", "step-back"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 查询转换

## 概述

查询转换（Query Transformation）是RAG系统中对用户原始输入进行重写、分解或抽象化处理的一组技术，目的是弥合"用户表达方式"与"知识库索引方式"之间的语义鸿沟。原始查询往往含糊、口语化或缺乏上下文，直接用于向量检索时召回率通常低于60%，而经过转换的查询能将相关文档的召回率提升20%~40%。

查询转换技术的系统性研究兴起于2022年前后，随着LLM能力的增强，研究者开始利用大模型本身来改写用于检索的查询。2023年Langchain和LlamaIndex相继将Query Rewriting、HyDE（Hypothetical Document Embedding）、Multi-Query等技术纳入标准RAG工具链，标志着查询转换从学术概念走向工程实践。

查询转换之所以重要，是因为向量数据库的余弦相似度检索对措辞高度敏感——"如何降低变压器推理成本"与"transformer inference optimization方法"在嵌入空间中的距离可能大于0.3，导致本应命中的文档被遗漏。通过转换层，系统可在不修改索引的前提下显著提升检索质量。

---

## 核心原理

### 查询重写（Query Rewriting）

Query Rewriting的基本思路是用LLM将用户的原始问题改写为更适合检索的形式。最简单的Prompt模板如下：

> "将以下问题改写为一个清晰、完整、适合文档检索的查询，去除口语化表达，补全隐含主语：{original_query}"

该技术对多轮对话场景尤为关键。例如用户在第3轮说"那它的价格呢？"，重写模块需要结合对话历史将其还原为"GPT-4 API的调用价格是多少？"，再进入检索流程。重写前后的查询均保存在上下文中，检索结果合并去重后送入生成模块。

HyDE（Hypothetical Document Embeddings，2022年由Gao等人提出）是一种特殊的重写策略：先让LLM根据问题生成一段假设性的答案文本，再用该文本的嵌入向量去检索真实文档。其逻辑在于，假设答案的嵌入向量与真实相关文档的嵌入向量在语义空间中比原始问题更近。论文实验显示，HyDE在TREC DL 2019数据集上的nDCG@10比直接查询提升约3~5个百分点。

### 查询分解（Query Decomposition）

Query Decomposition将一个复杂的复合问题拆分为若干个单一子问题，分别检索后聚合答案。例如：

**原始查询**："对比RAG和微调在领域适配上的成本和效果差异"

**分解后**：
1. RAG在领域适配中的实施成本是多少？
2. 微调在领域适配中的实施成本是多少？
3. RAG在领域适配中的效果评估指标有哪些？
4. 微调在领域适配中的效果评估指标有哪些？

这4个子查询各自独立检索，获得4组文档片段，再由LLM综合生成对比性答案。LlamaIndex的`SubQuestionQueryEngine`实现了该流程，内部使用结构化输出解析来提取子问题列表。分解策略特别适合需要多跳推理（Multi-hop Reasoning）的问题，即答案分散在多个文档中、需要逐步推导的场景。

### Step-back Prompting（后退提问）

Step-back Prompting由Google DeepMind在2023年论文《Take a Step Back》中提出，核心是将具体问题抽象化为更高层次的原则性问题，先检索原理，再用原理指导具体问题的回答。

**转换示例**：
- 具体问题："为什么BERT在长文本上表现差？"
- Step-back问题："Transformer架构在处理长序列时存在哪些基本限制？"

系统同时用两个查询检索文档：Step-back查询负责召回背景原理文档，原始查询负责召回具体案例文档，两类文档共同构成生成上下文。论文在MMLU和TimeQA等基准上报告该方法将准确率提升约4%。

### Multi-Query 并行扩展

Multi-Query技术让LLM从不同角度为同一问题生成3~5个等价变体，并行发起检索，结果取并集后用互反排名融合（Reciprocal Rank Fusion，RRF）重新排序。RRF的公式为：

$$RRF(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

其中 $r(d)$ 是文档 $d$ 在某次检索结果中的排名，$k$ 通常取60，$R$ 是所有检索结果列表的集合。该方法不依赖相关性分数的绝对值，对不同嵌入模型的输出具有较强的鲁棒性。

---

## 实际应用

**企业知识库问答**：某金融机构的内部合规问答系统，用户常以"这个条款能这么做吗？"的口语方式提问。部署Query Rewriting后，系统先将问题扩展为"根据XX监管法规第X条，以下操作是否合规：[操作描述]"，再进入检索，误召回率从18%降至7%。

**代码文档检索**：开发者常问"这个函数怎么用？"，Query Decomposition将其拆为"函数签名与参数说明"、"使用示例"、"常见错误处理"三个子查询，分别检索API文档的不同段落，显著减少了因单一查询导致的信息遗漏。

**学术研究助手**：对于"量子纠错与经典纠错有何本质区别"这类需要背景知识的问题，Step-back查询先检索"量子信息的基本原理"和"经典信息论基础"，为生成模型提供原理框架，避免直接检索时因术语不匹配漏掉关键文献。

---

## 常见误区

**误区一：查询转换越多越好**
多次转换会叠加LLM调用延迟，每次Rewriting或Decomposition都增加约200~800ms的额外耗时（取决于模型规模）。对于简单的事实性问题（如"OpenAI成立于哪一年？"），过度分解反而引入噪声，应通过查询分类器判断是否需要转换，而非对所有查询统一处理。

**误区二：HyDE生成的假设文本等同于真实答案**
HyDE的假设文本仅用于计算嵌入向量以改善检索，其内容可能包含LLM幻觉，绝不能直接作为答案返回给用户。系统必须严格区分"用于检索的假设文本"和"基于检索结果生成的最终答案"这两个独立步骤。

**误区三：Step-back Prompting适用于所有领域**
Step-back的效果高度依赖知识库是否包含足够的原理性内容。若知识库仅包含操作手册和FAQ文档，Step-back查询生成的抽象原则性问题将无法命中任何相关片段，反而降低检索覆盖率。在知识库内容以程序性知识为主时，Multi-Query扩展通常优于Step-back。

---

## 知识关联

查询转换模块位于RAG管道的查询处理层，在用户输入被路由至具体检索器之前执行。它依赖**RAG管道架构**中已定义的文档分块策略——例如，如果文档按章节分块，Decomposition生成的子查询需要与章节粒度匹配，过细的分块会导致子查询无法获得完整的上下文片段。

从**RAG查询路由**的视角看，路由决策本身可以与转换类型绑定：简单检索型问题走直接查询路径，多跳推理型问题触发Decomposition，知识密集型问题触发Step-back+Multi-Query组合。查询转换的输出——一个或多个经过优化的查询——直接决定了向量检索、关键词检索或混合检索阶段能够召回的文档质量，是整个RAG系统答案准确性的重要上游因素。