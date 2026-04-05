---
id: "fine-tuning-overview"
concept: "微调概述(SFT/RLHF)"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 微调概述（SFT/RLHF）

## 概述

大型语言模型的微调（Fine-tuning）是指在已完成预训练的基础模型之上，使用特定任务数据继续训练，使模型从"知识百科"转变为"实用助手"的过程。预训练阶段（如GPT-3用了约45TB文本数据）赋予模型广博的世界知识，但原始预训练模型只会预测下一个词，并不会遵循指令、进行对话或拒绝有害请求。微调正是弥合这一差距的关键技术手段。

微调的发展轨迹与大模型产业化紧密相连。2022年初，InstructGPT论文（Ouyang et al., 2022）首次系统性地将有监督微调（Supervised Fine-Tuning，SFT）与基于人类反馈的强化学习（Reinforcement Learning from Human Feedback，RLHF）结合，将GPT-3从一个文本补全引擎改造成了能够遵循复杂指令的对话系统。该论文报告：经过1.3B参数的InstructGPT微调后，人工评估者有71%的概率更偏好其输出，而非175B参数的原始GPT-3——这说明微调的质量效益远超单纯的参数规模扩张。

微调之所以重要，在于它以极低的数据和计算成本（相比预训练节省99%以上的算力），将通用语言能力定向校准至特定行为规范。现代主流的微调流程包含两个串联阶段：SFT阶段负责教会模型"如何回答"，RLHF阶段负责对齐模型"应该如何回答"，两者分工明确、缺一不可。

## 核心原理

### 有监督微调（SFT）

SFT使用人工构建的"指令-回答"配对数据集对模型进行标准的交叉熵损失训练。数据格式通常为 `<system prompt> + <user instruction> + <assistant response>`，模型仅对assistant部分的token计算损失，即：

$$\mathcal{L}_{SFT} = -\sum_{t=1}^{T} \log P_\theta(y_t \mid x, y_{<t})$$

其中 $x$ 为输入指令，$y_t$ 为第 $t$ 个目标token，$\theta$ 为模型参数。SFT数据集规模通常在数千至数万条之间，如Alpaca数据集包含52,000条由GPT-3.5自动生成的指令数据，OpenAssistant数据集包含约161,000条人工标注对话。SFT的核心挑战是数据质量而非数量——10,000条精标数据往往优于100,000条噪声数据，LIMA论文（2023）用仅1,000条精选样本便在多项评测中媲美更大数据集的微调效果，验证了这一规律。

### 奖励模型训练（Reward Model）

RLHF的第一步是训练一个奖励模型（Reward Model，RM），它将"哪个回答更好"的人类偏好判断转化为可微的标量信号。训练数据来自人工标注者对同一指令下多个模型回答的排序（如：回答A > 回答C > 回答B）。奖励模型的训练目标基于Bradley-Terry偏好模型：

$$\mathcal{L}_{RM} = -\mathbb{E}_{(x, y_w, y_l)} \left[ \log \sigma(r_\theta(x, y_w) - r_\theta(x, y_l)) \right]$$

其中 $y_w$ 为偏好答案（winner），$y_l$ 为劣质答案（loser），$r_\theta$ 为奖励模型输出的标量分数，$\sigma$ 为sigmoid函数。InstructGPT的奖励模型从6B参数的GPT-3初始化，由约33,000条比较数据训练而成。

### PPO强化学习优化阶段

RLHF的第二步使用近端策略优化（Proximal Policy Optimization，PPO）算法，以奖励模型的评分为反馈信号微调语言模型。为防止模型在优化奖励时偏离原始SFT模型太远（即"奖励黑客"问题），损失函数中加入KL散度惩罚项：

$$\mathcal{L}_{PPO} = \mathbb{E}\left[ r_\theta(x, y) - \beta \cdot \text{KL}\left(\pi_{RL}(\cdot|x) \| \pi_{SFT}(\cdot|x)\right) \right]$$

其中 $\beta$ 为KL惩罚系数（InstructGPT设置为0.02），$\pi_{RL}$ 为当前策略，$\pi_{SFT}$ 为SFT参考策略。PPO阶段需要同时在显存中维护策略模型、参考模型、奖励模型和价值模型四个模型，这使RLHF的工程实施成本显著高于SFT。

### SFT与RLHF的分工与衔接

SFT和RLHF在功能上存在本质区别：SFT解决格式对齐（模型学会以对话格式输出），RLHF解决价值对齐（模型学会输出人类偏好的内容）。直接跳过SFT进行RLHF通常效果极差，因为PPO的探索效率依赖模型已具备基础的指令遵循能力。Llama 2的技术报告（2023）详细记录了Meta的微调流程：首先用27,540条高质量SFT样本完成指令微调，再经过多轮RLHF迭代，其中每轮RLHF收集约数十万条人类偏好标注。

## 实际应用

**ChatGPT/GPT-4的对话能力构建**：OpenAI在GPT-3.5基础模型上首先执行SFT（训练数据包含多轮对话、代码生成、数学推理等多种类型），再通过RLHF使模型拒绝有害请求并提升回答有用性，最终形成了面向消费者的ChatGPT产品。这一流程已成为行业标准范式，被Anthropic（Claude）、Google（Gemini）等主流厂商普遍采用。

**垂直领域专业化微调**：医疗领域的MedAlpaca项目在LLaMA-7B基础上使用医学问答数据集（包含约160,000条USMLE考题和医学文献摘要）执行SFT，使模型在医学专业问答任务上的表现从通用模型的32%准确率提升至52%（USMLE Step 1测试集）。此类垂直SFT通常仅需数千到数万条领域数据，训练时间在单张A100 GPU上为数小时至数天。

**代码生成能力增强**：GitHub Copilot的底层模型Codex（2021）是在GPT-3基础上使用1,590亿token的代码数据进行全参数微调的典型案例，该模型在HumanEval基准上的pass@1指标达到28.8%，而原始GPT-3仅为0%，证明了领域SFT的显著效果。

## 常见误区

**误区一：SFT数据越多越好**。许多工程师在初期倾向于堆砌大量SFT数据，但实际上SFT数据质量的影响远大于数量。混入低质量的爬虫数据会导致模型输出风格退化，出现重复、语无伦次等现象，这被称为"灾难性遗忘"（Catastrophic Forgetting）中的特殊表现形式。最优实践是在多样性覆盖充分的前提下，严格控制每条数据的回答质量，而非盲目扩大数量。

**误区二：RLHF是SFT的替代品**。部分团队认为可以直接在基础预训练模型上应用RLHF跳过SFT阶段。但PPO算法在优化一个尚未具备基本指令遵循格式的模型时，信号极为稀疏，策略梯度方差极大，训练极不稳定。SFT是RLHF的必要前置步骤，为强化学习提供一个质量合理的初始策略。

**误区三：奖励模型分数越高代表回答越好**。在RLHF实践中，存在"奖励黑客"（Reward Hacking）现象——模型会学会"讨好"奖励模型的特定模式（如冗长的开场白、过度肯定的语气），但实际有用性并未提升。这是KL惩罚系数 $\beta$ 存在的原因，也是为什么需要不断收集新的人类偏好数据重新训练奖励模型的根本动力。

## 知识关联

从LLM预训练承接来看，微调的前提是预训练模型已通过大规模无监督语料学习到充分的语言表征能力；若基础模型的预训练数据覆盖不足（如缺乏中文语料），SFT无法"凭空"注入语言能力，只能在已有知识上进行行为调整。迁移学习的参数微调理论解释了为何少量下游数据即可有效调整大规模模型：预训练权重提供了高质量的特征空间初始化，梯度更新只需在此基础上进行小幅校正。

本概念向前延伸至LoRA与参数高效微调，LoRA通过低秩矩阵分解将SFT的可训练参数从数十亿降至数百万，使单卡微调大模型成为可能。RLHF人类反馈强化学习是本文PPO阶段的深入展开，涉及更复杂的奖励建模方法（如DPO