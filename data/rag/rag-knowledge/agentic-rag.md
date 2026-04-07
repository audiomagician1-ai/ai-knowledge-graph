---
id: "agentic-rag"
concept: "Agentic RAG"
domain: "ai-engineering"
subdomain: "rag-knowledge"
subdomain_name: "RAG与知识库"
difficulty: 8
is_milestone: false
tags: ["RAG", "Agent"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Agentic RAG

## 概述

Agentic RAG 是在标准检索增强生成（RAG）管道基础上引入 Agent 决策循环的系统架构。与传统 RAG 的"单次检索→单次生成"线性流程不同，Agentic RAG 允许 LLM 作为控制器（Controller）动态决定是否检索、检索什么、检索几次，以及如何将多轮检索结果综合推理以生成最终答案。系统不再是被动执行检索指令，而是主动规划信息获取策略。

该概念在 2023 年下半年随 LangChain 的 Agent 模块和 LlamaIndex 的 `OpenAIAgent` 集成普及开来，并在 2024 年的多篇论文（如 Self-RAG、FLARE、Corrective RAG）中被正式系统化。与早期 ReAct（Reasoning + Acting）框架结合后，Agentic RAG 得以在复杂多跳问题上显著超越静态 RAG——在 HotpotQA 数据集上，多步 Agentic RAG 方案的精确匹配分数比单次 RAG 高出约 15~20 个百分点。

Agentic RAG 之所以值得专门研究，是因为它将 RAG 系统的性能天花板从"知识库质量"扩展到"推理策略质量"。当用户提问需要跨越多个知识域或需要验证中间结论时，静态 RAG 的一次性检索窗口会产生不可恢复的信息截断，而 Agentic RAG 的迭代循环机制能够主动填补这一缺口。

---

## 核心原理

### 1. 决策循环与工具调用

Agentic RAG 的基本运行单元是 **Observe → Think → Act** 循环，其伪代码结构如下：

```
while not terminal_condition:
    observation = current_context + retrieved_docs
    thought = LLM.reason(observation, query)
    action = LLM.choose_tool(thought)  # 可为 retrieve / rewrite / answer / stop
    observation = tool_executor.run(action)
```

LLM 在每一步可调用的工具通常包括：向量检索器（Vector Retriever）、关键词检索器（BM25）、计算器、代码执行器、网络搜索 API 等。系统通过工具描述（Tool Description）让 LLM 自主选择何时调用哪个工具，这与标准 RAG 中固定调用向量检索的方式形成本质区别。

### 2. 查询改写与子问题分解

Agentic RAG 的关键能力之一是 **查询改写（Query Rewriting）** 和 **子问题分解（Sub-question Decomposition）**。对于复杂问题如"比较 GPT-4 和 Claude 3 在代码生成任务上的评测结果"，系统会自动分解为至少两个子检索任务，分别获取两个模型的基准数据后再做对比推理。LlamaIndex 的 `SubQuestionQueryEngine` 即实现了这一机制，每个子问题独立调度检索链，最终由合成层（Synthesis Layer）聚合答案。

### 3. 自我反思与纠错机制

**Corrective RAG（CRAG）** 和 **Self-RAG** 两篇论文将自我反思引入 Agentic RAG 流程。Self-RAG 引入了四类特殊反思 Token：`[Retrieve]`、`[ISREL]`（是否相关）、`[ISSUP]`（是否有文档支持）、`[ISUSE]`（是否有用），LLM 在生成过程中实时预测这些 Token 来决定是否触发新一轮检索或丢弃当前段落。CRAG 则对每段检索文档打置信度分（低于阈值 0.5 时触发网络搜索补充），两种机制都使系统具备了对检索质量的内生评估能力。

### 4. 路由与多知识源编排

生产级 Agentic RAG 通常需要管理多个异构知识源（结构化数据库、向量库、图数据库、实时 API）。**路由层（Router）** 负责根据问题类型将查询分发到最合适的数据源。例如，LlamaIndex 的 `RouterQueryEngine` 使用 LLM 选择器在 SQL 引擎和向量引擎之间动态切换。这种多源编排使 Agentic RAG 的知识覆盖范围远超任何单一向量库。

---

## 实际应用

**法律文档分析**：用户提问"A 公司是否违反了合同第三条款中的保密义务"需要先检索合同正文第三条，再检索相关法律解释，最后对照案例数据库推理。Agentic RAG 系统会自动执行三步检索并在中间步骤验证"保密义务"的具体定义，而静态 RAG 仅能返回与问题表面文字最近邻的段落，极易遗漏法律定义细节。

**企业知识库问答**：某头部电商使用 Agentic RAG 构建内部运营助手，系统在 Confluence 文档库（向量检索）和内部 MySQL 报表库（SQL 工具）之间动态切换。当问题涉及"上个季度退款率超过 5% 的 SKU 的退款原因"时，系统先通过 SQL 工具查出 SKU 列表，再对每个 SKU 检索用户投诉文档，最终合成有数据支撑的原因分析，整个流程自动完成约 4~6 次工具调用。

**科研文献综述辅助**：研究人员使用基于 GPT-4 + arXiv 检索工具的 Agentic RAG 系统，系统通过迭代检索在约 8 轮内完成对某子领域的引用图谱追踪，比人工检索节省约 70% 的时间，同时覆盖到第三层引用关系（即引用的引用的引用），这是单次 RAG 无法实现的深度。

---

## 常见误区

**误区一：认为 Agentic RAG 就是"多次调用标准 RAG"**。多次调用只是表象，真正的 Agentic RAG 要求每次检索的查询是根据上一步的中间结果动态生成的，而非预先固定的多条查询并行执行。如果缺少"基于中间观察重新规划"这一环节，只是 Multi-Query RAG，而非 Agentic RAG。

**误区二：认为 Agent 循环越多越好**。无限制的迭代会导致延迟爆炸和成本激增。生产系统必须设置最大步数上限（通常为 5~10 步）和终止条件（如置信度阈值或无新信息检出）。LangGraph 的 `recursion_limit` 参数和 Self-RAG 的 `[ISUSE]` Token 都是控制循环深度的具体机制，忽略终止条件会使 P99 延迟比单次 RAG 高出 10 倍以上。

**误区三：认为 Agentic RAG 不需要设计 RAG 管道基础设施**。Agent 层面的推理能力无法弥补底层检索质量的不足。如果向量库的切块（Chunking）策略不当导致语义边界断裂，Agent 即使多次检索也只能获取碎片化的上下文，自我反思机制会因为缺乏完整信息而持续触发无效检索循环。

---

## 知识关联

**前置知识——RAG 管道架构**：Agentic RAG 的检索工具本质上是封装好的标准 RAG 管道（文档加载→切块→嵌入→向量存储→检索→重排序）。没有对嵌入模型选型、混合检索策略和重排序模型的理解，无法设计出 Agent 可以可靠调用的检索工具接口，更无法诊断 Agent 循环中因检索质量导致的失败。

**后续方向——自主 Agent 前沿**：Agentic RAG 是通往完全自主 Agent 的过渡形态：它已具备工具调用和自我反思能力，但知识来源仍局限于预建知识库。自主 Agent 前沿进一步引入持久记忆（Persistent Memory）、跨会话学习和主动知识更新机制，使系统不再依赖静态知识库而能自主扩展知识边界。理解 Agentic RAG 中 `Observe→Think→Act` 循环的设计约束，有助于理解为何自主 Agent 需要引入更复杂的记忆和规划架构来克服这些限制。