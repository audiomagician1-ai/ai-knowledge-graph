---
id: "gpt-model"
concept: "GPT与解码器模型"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# GPT与解码器模型

## 概述

GPT（Generative Pre-trained Transformer）是OpenAI于2018年发布的纯解码器架构语言模型，其核心创新在于将Transformer的解码器部分单独提取，结合**因果语言建模（Causal Language Modeling, CLM）**目标进行自监督预训练。与BERT的双向注意力不同，GPT的每个token只能"看到"它左侧的上下文，这种单向自回归结构天然适合文本生成任务。

从GPT-1（1.17亿参数，2018年）到GPT-2（15亿参数，2019年）、GPT-3（1750亿参数，2020年），再到GPT-4（2023年），模型参数规模呈指数级增长。这一演进揭示了一条核心规律：在相同架构下，参数量与数据量的扩大能够涌现出意想不到的推理、少样本学习能力，这正是"Scaling Law"（缩放定律）所描述的现象。

GPT系列的重要性不仅在于文本生成性能，更在于它确立了"预训练 + 提示（Prompting）"的现代LLM使用范式。GPT-3展示的In-Context Learning能力——无需梯度更新，仅靠上下文中的示例即可完成新任务——彻底改变了NLP的应用逻辑，使得微调不再是唯一的下游适配手段。

---

## 核心原理

### 因果自注意力掩码（Causal Masking）

解码器模型的标志性机制是**因果掩码（Causal Mask）**，在计算自注意力时使用一个下三角矩阵将未来位置的注意力权重强制置为负无穷（softmax后趋近于0）。具体地，对于序列中位置 $i$ 的token，其注意力分数计算为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + M\right)V$$

其中掩码矩阵 $M$ 满足：当 $j > i$ 时 $M_{ij} = -\infty$，否则 $M_{ij} = 0$。这保证了训练时所有位置可以并行计算，而推理时仍模拟严格的从左到右生成过程。与BERT的双向注意力相比，因果掩码使得解码器天然具备序列生成能力，但代价是每个token无法利用右侧的上下文信息。

### 自回归生成与KV缓存

推理阶段，GPT逐token进行自回归生成：每次将已生成的完整序列输入模型，预测下一个token的概率分布，再通过采样策略（贪婪、Top-k、Top-p/Nucleus采样）选取输出。这种机制导致推理时每生成一个新token就需要对整个前缀重新计算注意力，计算复杂度为 $O(n^2)$。

**KV缓存（KV Cache）**是解决该效率问题的工程手段：将每一层的Key和Value矩阵缓存起来，新token生成时只需计算其自身的Query与缓存的K、V做注意力，将每步生成的计算量从 $O(n^2)$ 降至 $O(n)$。代价是显存占用随序列长度线性增长——对于GPT-3规模的模型，长序列下KV Cache可占据数GB显存，这是上下文窗口扩展的核心工程瓶颈。

### 纯解码器架构与位置编码

GPT原始版本使用**可学习的绝对位置编码**（Learned Absolute Positional Embedding），每个位置对应一个独立的嵌入向量。GPT-2和GPT-3延续了这一设计，但其上下文窗口受限于预训练时的最大位置数（GPT-2为1024，GPT-3为2048）。后续模型如LLaMA、Qwen等改用**旋转位置编码（RoPE）**，使得模型对序列长度具有更好的外推能力。

解码器模型通常不包含编码器-解码器之间的交叉注意力（Cross-Attention）层——这是它区别于原始Transformer解码器的关键结构差异。原始Transformer解码器有三个子层（自注意力、交叉注意力、前馈网络），而GPT型解码器只有两个子层（因果自注意力、前馈网络），结构更简洁。

---

## 实际应用

**代码生成（Codex/GitHub Copilot）**：OpenAI基于GPT-3在大量代码数据上微调得到Codex，参数量120亿，训练数据包含来自GitHub的1590亿token代码。其自回归特性使得模型可以逐行生成符合语法和语义的代码，并能根据注释推断函数实现。这是纯解码器架构在结构化文本生成上的典型成功案例。

**对话系统（ChatGPT）**：GPT-3.5-turbo通过SFT（监督微调）+ RLHF（人类反馈强化学习）调整后用于对话，其多轮对话能力依赖于将整个对话历史拼接成单一序列输入——这正是因果语言模型的上下文连续性所支撑的。对话轮数越多，占用的上下文窗口越长，这直接促使了后续4k→8k→128k上下文窗口的持续扩展需求。

**文档补全与RAG中的生成端**：在检索增强生成（RAG）系统中，解码器模型扮演"生成器"角色，接收检索到的文档片段与用户问题的拼接，生成有据可查的回答。此场景要求模型能够忠实利用上下文而非依赖参数记忆，是评估解码器模型"接地气"能力的重要应用场景。

---

## 常见误区

**误区一：解码器模型只能做生成，不能做分类**。实际上，GPT可以通过在序列末尾添加特殊分类token，取该位置的隐藏状态接分类头来完成判别任务。GPT-1论文本身就展示了在文本分类、蕴含、相似度等任务上的有竞争力结果。但由于每个token只能看到左侧上下文，对于需要双向理解的任务（如NLI），解码器模型在同等参数量下通常弱于BERT类编码器。

**误区二：因果掩码导致"看不到未来"是模型的弱点**。恰恰相反，这一约束使得自回归训练目标极为自然——不需要任何额外标注，模型直接以"预测下一个token"为目标，从而能够从海量无标注文本中学习。这与BERT的掩码语言建模（需要随机掩盖15%的token）不同，CLM目标利用了序列中每一个位置的监督信号，数据利用率更高。

**误区三：解码器模型推理速度随序列长度线性增长**。在未使用KV Cache的情况下，每生成一个token都需要对全部前缀重新计算，时间复杂度是 $O(n^2)$。即使使用KV Cache，显存占用仍以 $O(n \cdot L \cdot d)$ 增长（$L$ 为层数，$d$ 为隐藏维度），这使得批量处理长文本请求时显存成为主要瓶颈，而非计算量。

---

## 知识关联

从**Transformer架构**的视角看，GPT选择性地继承了解码器的因果掩码机制，丢弃了交叉注意力，这一结构选择决定了其自回归生成能力；而**BERT与编码器模型**的对比是理解GPT设计取舍的必要参照——编码器获取双向上下文但不擅长生成，解码器牺牲双向感知但天然支持序列续写。

掌握GPT架构后，**LLM预训练**将进一步探讨如何在万亿token量级数据上稳定训练解码器模型，包括混合精度训练、梯度检查点等工程实践。**上下文窗口与长文本**主题将深入KV Cache显存瓶颈与RoPE位置外推的解决方案。**开源LLM生态（Llama/Qwen/DeepSeek）**中的模型均采用GPT式纯解码器架构，它们在分组查询注意力（GQA）、SwiGLU激活函数等细节上对原始GPT进行了改进，是学习GPT原理后自然延伸的工程实践对象。