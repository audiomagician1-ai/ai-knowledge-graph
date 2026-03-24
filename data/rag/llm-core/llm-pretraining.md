---
id: "llm-pretraining"
concept: "LLM预训练"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# LLM预训练

## 概述

LLM预训练（Large Language Model Pre-training）是指在海量无标注文本语料上，通过自监督学习目标训练一个参数规模达到数十亿乃至数万亿的神经网络语言模型的过程。其核心任务是让模型从原始文本中学习语言的统计规律、语义结构和世界知识，为后续微调或直接推理奠定参数基础。预训练阶段消耗的算力占整个LLM生命周期算力的绝大部分——GPT-3的单次预训练估计耗费约3640 petaflop/s-days，训练成本超过460万美元。

预训练的概念在2018年随BERT和GPT-1的发布正式确立为NLP主流范式。在此之前，语言模型只在小规模数据上训练特定任务。BERT（2018年10月发布）证明了双向预训练配合MLM目标可以在11项NLP基准上刷新记录；GPT系列则沿因果语言建模路线发展，最终在2020年的GPT-3（1750亿参数）上验证了少样本能力的涌现。预训练之所以重要，在于它将知识获取与任务适配解耦：一次预训练的参数可以服务于问答、摘要、代码生成等数百种下游任务。

## 核心原理

### 训练目标：因果语言建模（CLM）与掩码语言建模（MLM）

解码器架构LLM（如GPT系列、LLaMA）使用**因果语言建模**目标，即最大化序列的自回归对数似然：

$$\mathcal{L}_{CLM} = -\sum_{t=1}^{T} \log P(x_t \mid x_1, x_2, \ldots, x_{t-1}; \theta)$$

其中 $x_t$ 是第 $t$ 个token，$\theta$ 是模型参数。该目标天然对齐生成任务，且无需人工标注。编码器架构（如BERT）则使用**掩码语言建模**，随机遮蔽15%的token并预测被遮蔽内容，同时配合下一句预测（NSP）任务。现代大型生成模型几乎全部采用CLM目标，因为CLM在参数规模扩大后表现出更稳定的涌现能力。

### 数据配方：语料构成与Token数量

预训练语料的质量与规模对最终模型能力有决定性影响。LLaMA-1（2023年2月）使用1.4万亿token训练700亿参数模型；LLaMA-2将数据量扩充至2万亿token。典型的数据混合配方包括：Common Crawl爬取网页（占比约67%）、GitHub代码（约4.5%）、维基百科（约4.5%）、书籍（约4.5%）以及学术论文等。数据去重是关键步骤——MinHash LSH去重可将CommonCrawl体积减少约70%，同时显著提升模型在下游任务的泛化能力。Chinchilla定律（2022年DeepMind）指出，最优训练token数约为模型参数量的20倍，颠覆了此前"参数越多越好、数据固定"的假设。

### 分布式训练策略：3D并行

训练千亿参数模型需要将单机无法容纳的参数和计算分布到数千块GPU上，主要采用三种并行方式的组合：

- **数据并行（Data Parallelism）**：每个GPU持有完整模型副本，处理不同mini-batch，通过AllReduce同步梯度。PyTorch DDP和DeepSpeed ZeRO均属此类。
- **张量并行（Tensor Parallelism）**：将单个矩阵运算（如Self-Attention的QKV投影和FFN层）切分到多个GPU，Megatron-LM的列并行和行并行分割将通信量控制在每层两次AllReduce。
- **流水线并行（Pipeline Parallelism）**：将模型按Transformer层分段分配到不同GPU节点，使用GPipe或1F1B调度减少流水线气泡（bubble ratio）至约 $\frac{p-1}{2m+p-1}$，其中 $p$ 为流水线级数，$m$ 为micro-batch数量。

GPT-4的训练据报道使用了约25000块A100，训练时长超过90天，体现了3D并行在极限规模下的工程复杂度。

### 训练稳定性技术

预训练过程中的**损失尖峰（loss spike）**是影响训练稳定性的主要挑战。常用应对措施包括：梯度裁剪（gradient clipping，阈值通常设为1.0）、权重衰减（weight decay，典型值0.1）、学习率预热（warmup步数通常为总步数的0.1%~1%）以及余弦衰减调度。PaLM（2022年）在训练过程中遭遇了6次损失尖峰，均通过从尖峰前的检查点重新开始并跳过相关数据批次解决。混合精度训练（BF16 + FP32主权重）已成为标准做法，BF16相较FP16具有更大的指数位范围，可避免数值溢出。

## 实际应用

**代码LLM的领域特化预训练**：Code Llama（2023年8月）在LLaMA-2基础上用5000亿token的代码数据继续预训练（continual pre-training），并引入长上下文微调将上下文窗口扩展至100K token，用于处理完整代码库级别的补全任务。

**多模态预训练数据构建**：LLaVA等视觉-语言模型在语言预训练之后，用图文对齐数据对视觉编码器与LLM进行联合预训练，图像token通过线性投影层映射到文本token空间，使模型能够在同一注意力机制下处理视觉和文字信息。

**续训与领域适配**：医疗LLM（如Med-PaLM 2）在通用LLM预训练基础上，追加注入经过去重和质量过滤的医学文献、临床指南和医学教科书进行持续预训练，以解决通用语料中专业知识稀缺问题，而无需从头训练。

## 常见误区

**误区1：预训练token数越多模型一定越好。** Chinchilla定律揭示，在固定算力预算下存在参数量与训练token数的最优权衡比约为1:20。LLaMA系列选择用更多数据训练更小的模型（例如用1万亿token训练70亿参数模型），其推理效率和下游性能均优于参数更多但数据不足的模型。单纯堆砌token而不控制数据质量，实际上会导致模型在高质量基准（如MMLU）上性能下降。

**误区2：预训练完成后模型已具备指令遵循能力。** 原始预训练仅优化下一个token的预测，模型的输出是对训练分布的延续，而非对用户指令的响应。GPT-3在预训练完成后，在少样本提示下可以完成任务，但会生成大量无关延续文本，直到InstructGPT（2022年1月）通过SFT+RLHF才解决了指令对齐问题。预训练和对齐是功能上相互独立的两个阶段。

**误区3：更大批量大小（batch size）总是能加速预训练收敛。** 研究表明存在临界批量大小（critical batch size），超过该值后增大batch size不再线性加速收敛，而是浪费计算资源。GPT-3使用的批量大小为320万token（约3.2M tokens per batch），这是经过梯度噪声规模（gradient noise scale）测量后确定的，而非随意设定。

## 知识关联

LLM预训练直接建立在GPT与解码器模型的架构基础之上——Transformer的多头注意力和因果掩码是CLM预训练得以高效实现的前提。完成预训练后，模型能力的规律性由**LLM缩放定律**刻画，包括Chinchilla定律对最优参数-数据配比的精确描述。预训练参数的存储和计算效率由**LLM推理优化**技术（如KV Cache、量化）解决，而模型的实际价值则通过**微调（SFT/RLHF）**释放——预训练提供知识，微调提供行为对齐。**Model Distillation**则是将大规模预训练模型的能力压缩到更小模型的核心技术路线，蒸馏的质量上界由教师模型预训练的充分程度决定。
