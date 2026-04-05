---
id: "agent-planning"
concept: "Agent规划与分解"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 7
is_milestone: false
tags: ["Agent"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 100.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# Agent规划与分解

## 概述

Agent规划与分解（Agent Planning & Decomposition）是指让AI Agent将复杂的高层目标拆解为可执行的子任务序列，并通过动态调度这些子任务逐步完成原始目标的技术体系。与单次推理（Single-Shot Inference）不同，规划与分解赋予Agent跨多个时间步骤协调行动的能力，使其能处理需要数十乃至数百次工具调用才能完成的长程任务（Long-Horizon Tasks）。

这一概念的技术根源可追溯到1959年由Newell、Shaw与Simon提出的通用问题求解器（General Problem Solver, GPS），以及1971年Fikes与Nilsson在斯坦福研究院发布的STRIPS（Stanford Research Institute Problem Solver）规划系统——后者首次引入了"前置条件/效果"（Precondition/Effect）的形式化任务表示。现代版本在2022年后随大语言模型崛起而重新焕发活力：2022年11月Yao等人发表的ReAct论文（Reason + Act, arXiv:2210.03629）和2023年4月Shen等人发布的HuggingGPT（arXiv:2303.17580），分别从"推理交织行动"与"模型即工具"两个维度奠定了现代Agent规划的技术范式。Agent规划能力直接决定了系统能否突破单次上下文窗口的限制，处理真实业务中的端到端自动化场景，例如自主完成"从需求分析到代码提交"的完整软件开发流程。

---

## 核心原理

### 任务分解的三种主要策略

**自顶向下分解（Top-Down Decomposition）** 是最常见的策略：Agent首先生成一个高层执行计划，再对每个步骤递归细化。典型实现是HuggingGPT的四阶段流程——任务规划（Task Planning）、模型选择（Model Selection）、任务执行（Task Execution）、结果汇总（Response Generation）。该策略适用于目标明确、结构化程度高的任务，但面对中途出现新信息时计划调整成本较高。

**动态规划（Dynamic/Reactive Planning）** 允许Agent在执行过程中根据工具调用的反馈实时修改后续步骤。ReAct框架将每轮循环建模为一个$(Thought_t, Action_t, Observation_t)$三元组：当$Observation_t$与预期不符时，$Thought_{t+1}$会显式修正对当前状态的判断并生成新的$Action_{t+1}$，而非盲目继续原计划。这种方式的本质是将规划（Planning）与执行（Execution）交织在同一个循环中，实现了"边做边想"的自适应能力。

**并行分解（Parallel Decomposition）** 将相互独立的子任务识别出来并发执行，显著缩短端到端完成时间。LangGraph框架通过有向无环图（DAG）建模任务依赖关系，对图执行拓扑排序后，所有入度为零的节点可以同步启动。例如在竞争情报分析任务中，"调用Bing Search API获取竞品新闻"与"查询内部数据库获取历史销售数据"这两个子任务无依赖关系，可并发执行，将总耗时从串行的约12秒压缩至约6秒。

### 规划提示工程的结构设计

现代基于LLM的规划器通常要求模型输出结构化JSON任务列表，每个任务包含四个关键字段：`id`（全局唯一标识符）、`task`（自然语言任务描述）、`depends_on`（前置任务id数组，建模依赖关系）、`tool`（调用的工具名称）。`depends_on`字段为空数组`[]`时，表示该任务可以立即触发执行，无需等待。这种格式由OpenAI 2023年11月发布的Assistants API Tool Use规范所推广，并在LangChain的`create_openai_tools_agent`和AutoGPT的任务队列中广泛采用。

规划提示中通常还需要注入以下约束，以防止LLM生成不可执行的幻想计划：
1. **工具白名单**：明确列出所有可用工具的函数签名，禁止规划器引用未定义工具；
2. **任务粒度要求**：要求每个子任务能在"单次LLM推理 + 最多3次工具调用"内完成（来源：LangChain官方最佳实践文档）；
3. **可验证完成条件**：每个任务描述须包含明确的输出格式，例如"返回含`revenue`和`growth_rate`字段的JSON对象"，而非模糊的"获取财务数据"。

### 子任务粒度控制与粒度陷阱

分解粒度存在两种失效模式：粒度过粗时，单步操作的复杂度超过LLM单次上下文处理能力，导致中间步骤失败率上升；粒度过细时，大量冗余的LLM推理调用（每次调用OpenAI GPT-4o约需150～400ms）会使总延迟膨胀，同时Token消耗成本呈线性增长。

经验法则是：子任务描述的Token长度控制在20～80个Token之间，且每个子任务对应且仅对应一个工具调用。若某步骤需要调用超过一个工具，应将其再次拆分。

---

## 关键公式与算法

### 任务依赖图的形式化表示

将分解后的任务集合建模为有向无环图 $G = (V, E)$，其中：

$$V = \{t_1, t_2, \ldots, t_n\}$$

表示所有子任务节点，有向边 $e_{ij} \in E$ 表示任务 $t_i$ 必须在 $t_j$ 开始之前完成（即 $t_j$ 依赖 $t_i$）。

任务 $t_j$ 的**最早开始时间（Earliest Start Time, EST）**定义为：

$$EST(t_j) = \max_{t_i \in \text{pred}(t_j)} \left( EST(t_i) + d_i \right)$$

其中 $d_i$ 为任务 $t_i$ 的预估执行时长，$\text{pred}(t_j)$ 为 $t_j$ 的所有前驱任务集合。当 $\text{pred}(t_j) = \emptyset$ 时，$EST(t_j) = 0$，可立即并行启动。这一公式与经典项目管理中的关键路径法（Critical Path Method, CPM）同构，说明Agent调度问题本质上是一个受依赖约束的并行调度优化问题（参见《人工智能：一种现代方法》第四版，Russell & Norvig, 2020，第11章）。

### 规划输出的JSON Schema示例

```json
{
  "plan": [
    {
      "id": "t1",
      "task": "使用Bing Search API搜索关键词'Tesla Q3 2024 revenue'，返回前5条结果的URL和摘要",
      "depends_on": [],
      "tool": "bing_search",
      "estimated_tokens": 300
    },
    {
      "id": "t2",
      "task": "抓取t1返回的第一个URL页面全文，提取revenue数值和同比增长率",
      "depends_on": ["t1"],
      "tool": "web_scraper",
      "estimated_tokens": 800
    },
    {
      "id": "t3",
      "task": "查询内部数据库表`competitor_financials`，获取同期竞品营收数据",
      "depends_on": [],
      "tool": "sql_query",
      "estimated_tokens": 200
    },
    {
      "id": "t4",
      "task": "综合t2和t3的结果，生成包含revenue、growth_rate、competitor_gap字段的对比分析JSON",
      "depends_on": ["t2", "t3"],
      "tool": "llm_synthesize",
      "estimated_tokens": 1200
    }
  ]
}
```

注意 `t1` 与 `t3` 的 `depends_on` 均为空数组，可并行触发；`t4` 依赖 `t2` 和 `t3`，须在两者均完成后才能启动。整个计划的关键路径为 $t_1 \to t_2 \to t_4$，其理论最短完成时间由这条路径上各任务的 $d_i$ 之和决定。

---

## 主流框架的规划实现对比

### ReAct：推理与行动交织

ReAct（Yao et al., 2022）不预先生成完整计划，而是在每一步生成一段自然语言思考（Thought），再决定调用哪个工具（Action），然后将工具返回结果（Observation）追加到上下文，进入下一轮。这种方式天然支持动态规划，但缺点是整个轨迹完全串行，无法并发执行任何子任务，在需要20+步工具调用的任务中延迟显著。

### Plan-and-Execute：两阶段分离

由Harrison Chase在LangChain 0.0.200版本（2023年7月）引入的Plan-and-Execute架构将规划器（Planner LLM）与执行器（Executor Agent）完全分离：规划器一次性生成完整的步骤列表（通常使用GPT-4生成高质量计划），执行器对每个步骤独立调用更小、更快的模型（如GPT-3.5-turbo）完成具体操作。这种分离的优势是降低执行阶段的Token成本，实测在10步任务中Token消耗比纯ReAct降低约40%。

### LLM Compiler：任务图编译执行

Kim等人在2023年发表的LLM Compiler（arXiv:2312.04511）将规划问题类比为编译器的中间表示优化：规划器生成带依赖关系的任务图（类似汇编指令的DAG表示），调度器识别可并发的任务并行派发，最后将所有结果汇聚给总结器。在128步并行任务测试中，LLM Compiler相比纯串行ReAct实现了约3.6倍的速度提升，Token消耗降低约44%（Kim et al., 2023）。

---

## 实际应用场景

### 案例：自动化代码审查流水线

**场景描述**：用户提交一个包含15个Python文件的代码库，要求Agent自动完成安全审查、代码风格检查、单元测试生成和PR摘要撰写。

**分解过程**：
1. **并行层一**（4个独立任务同时触发）：分别对15个文件运行`bandit`安全扫描工具、`flake8`风格检查工具、`pylint`质量评分工具，以及提取函数签名列表用于测试生成。
2. **串行层二**（依赖层一结果）：根据提取的函数签名，调用LLM批量生成`pytest`单元测试用例，目标覆盖率≥80%。
3. **串行层三**（依赖层一和层二结果）：汇总三类扫描报告和新生成的测试用例，撰写结构化PR审查摘要，包含"严重问题/普通问题/建议"三级分类。

整个流水线在实际部署中从串行执行的约180秒压缩至并行执行的约55秒，效率提升约3.3倍。

### 案例：多步骤数据分析报告生成

某金融数据平台使用Plan-and-Execute架构处理用户自然语言查询"生成本季度A股半导体板块的资金流向分析报告"：规划器生成8步执行计划（含3组可并行步骤），执行器依次完成数据拉取→清洗→统计计算→图表生成→报告撰写，全程无需人工干预，端到端耗时约45秒。

---

## 常见误区

**误区一：将规划等同于思维链（CoT）**
思维链（Chain-of-Thought）是单次推理过程中的内部推理路径，输出仍是一次性答案；而Agent规划产生的是跨多步骤、涉及真实外部工具调用的可执行任务序列。CoT是规划的必要工具（用于生成每步的Thought），但两者不等价。将两者混淆会导致开发者误以为"给LLM加上CoT提示就能完成复杂多步任务"，忽视了工具调用、状态管理和错误恢复等工程实现的复杂性。

**误区二：分解层数越多越好**
递归分解超过3层后，叶子任务的执行结果在向上汇聚时存在误差累积效应：若每个子任务的成功率为90%，则10个串行子任务构成的计划整体成功率仅为 $0.9^{10} \approx 34.9\%$。因此，在系统设计阶段必须评估每个子任务的失败概率，并为关键节点设计重试（Retry）和回退（