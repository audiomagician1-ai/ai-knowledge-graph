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
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# ReAct推理+行动

## 概述

ReAct（Reasoning + Acting）是由Yao等人于2022年在论文《ReAct: Synergizing Reasoning and Acting in Language Models》中提出的提示框架，其核心创新在于将语言模型的**推理轨迹**（reasoning traces）与**外部工具调用动作**（actions）交织在同一生成序列中。与思维链（CoT）只产生内部推理步骤不同，ReAct允许模型在推理过程中暂停，向搜索引擎、数据库、计算器等外部环境发出查询请求，并将返回的观测结果（observations）纳入后续推理，形成"思考→行动→观测"的循环。

ReAct的提出源于一个实际痛点：纯CoT推理在需要最新信息或精确计算的任务上会产生幻觉，因为模型只能依赖训练时冻结的参数知识。ReAct通过"接地"（grounding）机制解决了这一问题——每次行动后获取的真实观测结果会锚定后续推理，防止模型在多步推理中漂移。原始论文在HotpotQA、Fever等基准测试上验证了ReAct比单纯CoT的事实准确率提升3.4%至7.3%，同时错误传播率显著降低。

理解ReAct的关键在于认识它不是简单的"先想再做"，而是推理与行动**实时交替**——每次行动的结果都可能改变推理方向，而推理又决定下一步执行什么行动。这种动态反馈循环使ReAct成为构建自主AI Agent的基础技术之一。

## 核心原理

### Thought-Action-Observation三元组结构

ReAct的运作单元是严格格式化的三元组序列，每个循环包含三个标记前缀：

```
Thought: [模型对当前状态的内部推理]
Action: [调用的工具名称及参数，如 Search[量子计算]]
Observation: [外部环境返回的结果，由系统填充]
```

其中`Thought`步骤是模型生成的，`Action`步骤同样由模型生成但会被代码解析执行，`Observation`则是真实外部结果注入回上下文。这三个标签将一个不可分割的上下文窗口切分成了语义明确的片段，使模型在下一个`Thought`时能正确区分"我自己的推断"和"外部事实"。

### 停止词触发与工具解析机制

ReAct在技术实现上依赖**停止词（stop token）**机制。当语言模型生成`\nObservation:`字符串时，推理过程被暂停，控制权交还给宿主程序。程序解析上一行`Action:`的内容，提取工具名称与参数，调用对应API，将结果拼接为`Observation: [结果内容]`后重新输入模型继续生成。这意味着ReAct不需要对模型本身做任何微调，完全通过提示格式与推理循环的工程实现即可工作，这正是它在GPT-3.5、GPT-4等通用模型上能直接部署的原因。

### Few-Shot示例的构造规范

ReAct提示中的少样本示例（few-shot demonstrations）需要展示完整的多轮交替轨迹，通常包含3至5个已标注的`Thought/Action/Observation`链条。原始论文的HotpotQA实验使用了6个示例，每个示例平均包含4.7个完整三元组循环。构造这些示例时，`Action`类型必须来自预定义的工具集（如`Search[]`、`Lookup[]`、`Finish[]`），否则模型生成的动作无法被程序正确解析。`Finish[答案]`是终止动作，触发后程序停止循环并返回最终答案。

### ReAct与纯CoT的形式化区别

如果定义模型输出序列为 $S = \{s_1, s_2, ..., s_n\}$，CoT中每个 $s_i$ 均为模型生成的文本Token，而ReAct中序列形如 $S = \{t_1, a_1, o_1, t_2, a_2, o_2, ...\}$，其中 $t_i$ 为模型生成的Thought，$a_i$ 为模型生成的Action，$o_i$ 为**外部环境注入**的Observation。$o_i$ 不在模型的预测损失计算范围内，它是上下文中的"外来证据"，这正是ReAct能够突破模型参数知识边界的数学本质。

## 实际应用

**多跳问答（Multi-hop QA）**：对于"奥巴马的出生城市的市长是谁"这类需要串联多个事实的问题，ReAct会先`Search[Barack Obama birthplace]`获得"檀香山"，再`Search[Mayor of Honolulu 2024]`获得当前市长姓名，每一跳都以真实搜索结果为依据，避免CoT直接从参数记忆中拼凑错误答案。

**代码调试与执行验证**：在编程辅助场景中，模型可以生成代码片段后执行`Execute[代码]`动作，将实际运行输出作为Observation，再根据报错信息在下一个Thought中分析原因并修正，形成真正的"写→测→修"循环，而不是仅凭推理猜测代码是否正确。

**LangChain中的ReAct实现**：LangChain框架将ReAct封装为`create_react_agent()`函数，开发者只需提供工具列表（`tools`参数）和基础模型，框架自动处理停止词注入、动作解析、Observation拼接等工程细节，将原始论文的实验方法转化为可生产部署的Agent骨架。实际工程中工具集通常包含`DuckDuckGoSearch`、`PythonREPLTool`、`WikipediaAPIWrapper`等标准组件。

## 常见误区

**误区一：认为Observation是模型"想象"出来的**。初学者常误以为`Observation:`后的内容也是模型生成的，从而认为ReAct只是一种特殊的CoT格式。实际上，`Observation:`之后的内容**必须由外部程序注入**，如果允许模型自由生成Observation，则ReAct退化为角色扮演，丧失了所有事实接地能力。检查实现是否正确的标准就是：程序代码中必须存在一个显式的停止词拦截与结果注入逻辑。

**误区二：认为ReAct等同于函数调用（Function Calling）**。OpenAI的Function Calling通过结构化JSON输出触发工具，绕过了自然语言`Action:`格式的解析不稳定性，在精确性上优于原始ReAct。但ReAct的`Thought:`步骤在每次工具调用前都显式生成推理，这使中间推理轨迹完全可检查和可调试；而Function Calling默认不暴露调用前的推理过程。两者解决问题的层次不同，ReAct是提示范式，Function Calling是模型能力接口。

**误区三：认为循环轮次越多结果越好**。ReAct的每次循环都消耗上下文长度和API调用次数，且Observation内容会快速填充上下文窗口。原始论文设置最大循环次数为7，超过后强制终止。实际工程中，超过5次仍未得到`Finish[]`动作通常意味着工具返回结果质量差或任务分解有误，应优先检查工具设计而非增加循环上限。

## 知识关联

**与思维链（CoT）的关系**：ReAct以CoT为基础，继承了其"显式中间步骤"的核心思想，但将CoT中封闭的内部推理扩展为开放的环境交互循环。掌握CoT的`step-by-step`格式化思维是理解ReAct`Thought:`步骤书写规范的前提。

**通向AI Agent概述**：ReAct是从提示工程迈向Agent系统的关键桥梁。ReAct中的"工具调用+观测反馈"机制直接对应Agent架构中的"行动+感知"模块；理解ReAct的停止词拦截与循环控制逻辑，是理解完整Agent循环（感知-推理-行动）中任务调度器（orchestrator）职责的具体案例。

**通向提示链**：当ReAct的单次循环无法解决复杂任务时，需要将多个ReAct实例串联为提示链，前一个ReAct的`Finish[]`结果作为下一个实例的初始上下文输入。这种级联设计是构建多Agent协作系统的基础模式。
