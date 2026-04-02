---
id: "temperature-sampling"
concept: "Temperature与采样策略"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 5
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 54.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.469
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Temperature与采样策略

## 概述

Temperature（温度）是控制大型语言模型输出随机性的关键超参数，本质上是在模型的softmax输出层对logit值进行缩放的一个系数。具体而言，模型在生成每个token时会计算词汇表中所有候选词的概率分布，Temperature通过除以这个参数值来"拉伸"或"压缩"该分布，从而影响最终采样结果的确定性程度。

Temperature的概念源自统计力学中的玻尔兹曼分布（Boltzmann Distribution），物理学中温度越高，粒子能量分布越均匀；类比到语言模型中，Temperature越高，候选token的概率分布越趋于均匀，模型越倾向于选择低概率词汇。OpenAI在2020年发布GPT-3时正式将Temperature作为API参数对外暴露，此后成为所有主流LLM推理接口的标配参数，取值范围通常为0到2之间。

理解Temperature的意义在于它直接决定了模型输出的创造性与确定性之间的权衡。代码生成任务需要Temperature接近0以确保语法正确性；创意写作任务则需要0.8至1.2的较高值来产生多样化表达。错误配置Temperature会导致代码任务输出语法错误、创意任务输出重复内容等实际工程问题。

## 核心原理

### Softmax温度缩放的数学机制

模型输出层产生的原始logit向量记为 $z = [z_1, z_2, ..., z_n]$，标准softmax计算为：

$$P(x_i) = \frac{e^{z_i}}{\sum_j e^{z_j}}$$

引入Temperature参数 $T$ 后，公式变为：

$$P(x_i | T) = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}$$

当 $T \to 0$ 时，概率质量集中于logit最大的token（等价于贪心解码，greedy decoding）；当 $T = 1$ 时，使用模型训练时的原始概率分布；当 $T \to \infty$ 时，所有token概率趋向于均等的 $1/n$。这一机制意味着Temperature并不改变tokens的相对排名，只改变概率质量的集中程度。

### Top-p（Nucleus Sampling）采样策略

Top-p采样由Holtzman等人在2020年论文《The Curious Case of Neural Text Degeneration》中提出，是与Temperature配合使用的核心采样策略。其工作方式为：按概率从高到低排列所有候选tokens，累加概率直到总和达到阈值 $p$，然后仅从这个"核"（nucleus）中采样。

例如设定 $p = 0.9$，模型会找到最小的token集合使其概率之和 ≥ 0.9，再从该集合中按归一化概率采样。这种方式的优势在于候选集合的大小随上下文动态变化：当模型非常确定时（如句子开头填写冠词"the"），候选集合可能只有3-5个词；当模型不确定时，候选集合自动扩大。OpenAI API中该参数名为`top_p`，Claude API中同名，默认值通常为1（即不限制）。

### Top-k采样策略

Top-k采样是一种固定候选集合大小的策略：每次只从概率最高的 $k$ 个tokens中采样。Google的GPT-2复现工作以及许多早期语言模型广泛使用 $k = 40$ 作为默认值。Top-k的局限性在于 $k$ 是固定数量，无法自适应模型的当前不确定性——在模型高度确定的情况下，强制从40个候选中采样会引入不必要的噪声；在模型高度不确定的情况下，限制40个候选又可能截断合理选项。

OpenAI的GPT-4 API不直接暴露top-k参数，而Anthropic的Claude API和Google的Gemini API均提供该参数。实践中，top-p通常优于top-k，但两者可叠加使用（先top-k再top-p）。

### Temperature与采样策略的交互效应

Temperature和top-p是相互作用的参数，同时调高两者会产生极度随机的输出。OpenAI官方文档明确建议"只修改其中一个，而非同时修改两个"。常见工程实践是：固定 $T = 1$，调节top-p；或固定top-p = 1，调节Temperature。当Temperature设为0时，top-p的设置实际上失效，因为贪心解码总是选择概率最高的单个token。

## 实际应用

**代码生成场景**：调用OpenAI Codex或GPT-4生成Python函数时，推荐设置`temperature=0`或`temperature=0.2`，`top_p=1`。过高的Temperature（如1.5）会导致变量名拼写变体、括号不匹配等语法错误，这在单元测试中会直接报错。

**对话系统场景**：客服机器人需要一致性和准确性，通常使用`temperature=0.3`至`0.5`；开放域闲聊机器人则使用`temperature=0.8`至`1.0`以避免重复性回复。实验表明，temperature低于0.3时，对话机器人在多轮对话中会高频重复相同措辞。

**创意写作与头脑风暴**：生成广告文案变体时，设置`temperature=1.2`、`top_p=0.95`，并通过`n=5`参数一次生成5个候选，再由人工筛选。这种"过度采样后筛选"的工程模式比单次低温采样产出的最终质量更高。

**数学推理与事实问答**：Temperature必须设为0，使用贪心解码。微软研究院2023年对GPT-4的测试显示，在数学解题任务中Temperature从0升至0.7会使准确率下降约15个百分点。

## 常见误区

**误区一：Temperature=0等于"关闭随机性"**。Temperature=0在实现上等价于argmax（贪心解码），选择每步概率最高的token。然而，当两个tokens的logit值极为接近时，浮点运算的舍入误差可能导致不同硬件或批次大小下产生不同结果。因此Temperature=0并不保证跨平台的完全可复现性，严格可复现需要额外固定随机种子（seed参数）。

**误区二：Temperature越高输出质量越好**。Temperature高于1.5后，模型会大量采样到训练数据中极低频的token序列，这些序列往往在语义上不连贯。Holtzman等人的研究正是发现了高Temperature会导致"退化文本"（degenerate text）——包括无意义的重复和语法混乱，这也是nucleus sampling被提出的直接动因。

**误区三：Top-p=0.9意味着每次从"90%的词汇"中采样**。实际上top-p=0.9是从累计概率达到90%的最小token集合中采样，这个集合的实际大小可能只有5个词（模型高度确定时）或数千个词（模型高度不确定时）。将其误解为"词汇表的90%"会导致对模型行为的错误预判。

## 知识关联

掌握LLM API调用（OpenAI/Claude）是理解本主题的基础，Temperature和top-p均通过API参数直接控制，需要熟悉`chat.completions.create()`接口中`temperature`、`top_p`、`top_k`、`seed`等参数的传递方式。理解tokenization机制有助于更直观地理解概率分布作用于token而非字符层面的本质。

在Prompt工程的完整链路中，Temperature策略与few-shot示例设计、系统提示词（system prompt）共同构成输出质量的三个可调维度：few-shot示例影响模型的"意图理解"，system prompt设定输出格式约束，而Temperature策略则控制在满足约束后的随机性程度。对于需要多次调用LLM进行自我批评或链式思考（Chain-of-Thought）的高级应用场景，通常在初始生成阶段使用较高Temperature产生多样候选，在验证/评分阶段使用Temperature=0以确保评判一致性。