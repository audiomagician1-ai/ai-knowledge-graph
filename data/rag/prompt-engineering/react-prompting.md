---
id: "react-prompting"
concept: "ReAct推理+行动"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 6
is_milestone: false
tags: ["Prompt", "Agent"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# ReAct推理+行动

## 概述

ReAct（**Re**asoning + **Act**ing）是由Google Research和普林斯顿大学于2022年提出的提示工程框架，核心思想是让语言模型在单次交互过程中交替生成"思考轨迹"（Thought）和"可执行动作"（Action），而非仅输出最终答案。与思维链（CoT）只做内部推理不同，ReAct允许模型向外部环境发出动作请求并接收观察结果（Observation），形成"思考→动作→观察"的循环序列。

该框架发表于论文《ReAct: Synergizing Reasoning and Acting in Language Models》（Yao et al., 2022），在HotpotQA多跳问答任务上相比单独的CoT提示，ReAct将幻觉率降低了约34%。其核心价值在于：模型不再依赖训练时冻结的参数知识，而是通过动作（如搜索引擎查询、代码执行、数据库查询）实时获取外部信息，将推理与事实获取解耦。

ReAct之所以在AI工程领域受到重视，是因为它为构建可靠的工具调用Agent提供了一个可解释、可调试的执行轨迹格式。每一步的Thought对人类工程师可见，使得追踪模型决策链路成为可能，而不是面对一个黑盒式的动作输出。

---

## 核心原理

### Thought-Action-Observation三元组结构

ReAct的执行序列由重复出现的三元组组成：

```
Thought: [模型的推理过程，说明下一步意图]
Action: [具体动作及其参数，如 Search["量子纠缠定义"]]
Observation: [外部环境返回的真实结果]
```

这三个元素在提示模板中显式标注，模型通过In-context Learning从少样本示例中学习这种格式。关键约束是：Action必须是预定义工具集中的合法调用，常见类型包括`Search`、`Lookup`、`Calculate`、`Finish`等，`Finish[答案]`表示终止并返回最终结果。

### 与纯CoT的本质区别

思维链（CoT）的推理链完全在模型内部闭合，格式为"Question → Let's think step by step → Answer"，中间步骤无法引入新信息。ReAct在每次Thought之后可以插入真实的外部查询，Observation的内容不在模型训练数据中，因此可以处理实时信息或超出上下文长度的知识库。实验数据表明，在Fever事实核查任务上，ReAct的准确率比单纯CoT高出**5.9个百分点**，且幻觉性推理步骤更少。

### 停止条件与最大步数控制

ReAct并非无限循环：工程实践中必须设置`max_steps`参数（通常为5~15步）防止无限递归。当模型生成`Action: Finish[...]`时循环终止；若达到最大步数仍未完成，通常强制取最后一个Thought作为答案。提示模板中需要明确写出"如果你认为已经获得足够信息，使用Finish动作"这一指令，否则模型容易进入冗余搜索循环。

### 少样本示例设计要求

ReAct的少样本示例（few-shot examples）需要同时展示推理轨迹和动作格式，每个示例长度通常达到200~400 tokens，远长于标准问答示例。原始论文为HotpotQA任务设计了6个示例，每个包含3~7个完整的Thought-Action-Observation循环。示例中的Observation必须是真实或高度仿真的工具输出，若使用伪造Observation，模型会学习不切实际的工具使用模式。

---

## 实际应用

**多跳知识问答**：查询"《哈利·波特》作者的出生城市的人口"时，模型先`Search["J.K.罗琳出生城市"]`得到"叶特"，再`Search["叶特人口"]`得到具体数字，最后`Finish["约29,000人"]`。单次模型调用无法完成此任务，因为需要两步顺序信息获取。

**代码调试Agent**：在代码执行环境中，Thought描述预期行为，Action为`Execute[代码片段]`，Observation为实际运行输出（含报错信息）。模型可根据观察到的TypeError或NameError调整下一步修复策略，而非盲目猜测错误原因。

**LangChain中的ReAct实现**：LangChain框架的`AgentType.REACT_DOCSTORE`和`AgentType.ZERO_SHOT_REACT_DESCRIPTION`直接实现了ReAct格式，工程师通过`Tool`对象注册可调用工具，框架自动解析模型输出中的`Action:`和`Action Input:`字段并路由到对应工具函数。

---

## 常见误区

**误区一：认为Thought只是装饰性输出**
Thought步骤不是可选的可读性注释，而是功能性推理支架。论文消融实验显示，去除Thought步骤（仅保留Action-Observation循环）在HotpotQA上准确率下降约12%，因为模型依赖Thought步骤来整合上一轮Observation并规划下一个动作。

**误区二：Observation可以由模型自己生成**
Observation必须来自真实外部工具调用的结果，若让模型在推理时自行"想象"Observation（即不实际调用工具），则整个ReAct框架退化为带格式标签的CoT，失去获取外部事实的能力，且因格式冗余而性能不如纯CoT。

**误区三：ReAct适合所有任务类型**
对于不需要外部信息检索的纯数学推理任务（如GSM8K数学题），ReAct因引入了不必要的Action步骤而比CoT效率更低，延迟增加15%~40%（因工具调用I/O开销）。ReAct的优势场景是知识密集型、事实核查型或需要代码执行的任务。

---

## 知识关联

**前置概念——思维链（CoT）**：ReAct的Thought步骤本质上是CoT在受约束环境中的应用，理解CoT如何通过中间步骤提升推理准确性，是理解为何Thought步骤有效的基础。ReAct可视为CoT向开放环境的扩展：CoT在封闭上下文中推理，ReAct在开放工具环境中推理。

**后续概念——AI Agent概述与Agent循环**：ReAct定义了最基础的Agent执行格式，"感知-推理-行动"循环（Perceive-Reason-Act）是对Observation-Thought-Action三元组的抽象提升。学习Agent架构时，ReAct轨迹是理解规划模块与工具调用模块如何协同工作的具体参照。

**后续概念——提示链（Prompt Chaining）**：提示链将ReAct的单轮工具循环扩展为跨多个独立LLM调用的信息传递流水线，两者的区别在于提示链中每个节点是独立的模型调用，而ReAct在同一个上下文窗口内完成多轮推理与动作；复杂的Agent系统往往同时使用两种模式。