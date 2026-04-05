---
id: "sparse-attention"
concept: "稀疏注意力"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM", "架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# 稀疏注意力

## 概述

稀疏注意力（Sparse Attention）是一类通过限制每个token仅与序列中**部分**其他token计算注意力权重，将标准自注意力的计算复杂度从O(n²)降低至O(n·k)（其中k为每个token实际参与计算的token数量，远小于序列长度n）的机制。标准Transformer中，一个长度为4096的序列需要计算约1680万个注意力分数对，而采用稀疏注意力后，这一数字可缩减至仅需序列长度的线性倍数。

稀疏注意力的思想起源于2019年OpenAI发布的**Sparse Transformer**（Child等人），该工作首次系统性地证明：只要稀疏模式能覆盖足够的信息传播路径，模型可以在语言建模和图像生成任务上保持与密集注意力相当的效果。随后，2020年的Longformer（Beltagy等人）和2021年的BigBird（Zaheer等人）将这一思路推进到实用级别，后者更提供了理论证明：满足特定条件的稀疏注意力模式是图灵完备的，即具备与全注意力相同的表达能力上界。

稀疏注意力的工程价值在于使Transformer处理超长文档成为可行——Longformer将可处理序列长度从BERT的512个token扩展至4096乃至16384个token，而显存占用仅线性增长，使单卡训练长文档模型成为可能。

---

## 核心原理

### 三种基础稀疏模式

稀疏注意力的所有变体均基于三种基本稀疏模式的组合：

**局部窗口注意力（Local Window Attention）**：每个token仅与其前后各w/2个token计算注意力，形成一个滑动窗口。Longformer默认窗口大小为512，BigBird采用3的块大小（block size）进行分块稀疏计算。窗口注意力擅长捕获局部语法和短程依赖，是稀疏模式的主干。

**全局注意力（Global Attention）**：指定少量特殊token（如[CLS]、任务相关的问题token）与序列中**所有**位置双向计算注意力。Longformer在分类任务中给[CLS]赋予全局注意力，在QA任务中给问题tokens赋予全局注意力。全局token充当"信息枢纽"，将远距离信息聚合后再分发。

**随机注意力（Random Attention）**：每个token额外随机选择r个位置计算注意力（BigBird中r=1）。这一设计源自随机图的直径理论——即使每个节点只有少量随机连接，整张图的平均最短路径长度也会大幅压缩，使信息在O(log n)步内能跨越全序列。

### BigBird的理论保证

BigBird将上述三种模式组合后证明了两个关键性质：一是其注意力图构成一个**扩张图（Expander Graph）**，任意两个token之间的信息传播路径长度不超过O(log n)步；二是该稀疏注意力是**图灵完备**的（定理3.5，Zaheer等2021），即存在一组BigBird注意力权重，可以模拟任意有界计算。这是稀疏注意力相比早期局部注意力方案（如仅使用滑动窗口）的本质进步。

BigBird的总稀疏度公式为：每个query的参与key数量 = **g（全局token数）+ w（窗口大小）+ r（随机数量）**，三者独立可调，典型设置为g=2, w=3 blocks, r=1 block。

### Longformer的注意力矩阵实现

Longformer在实现层面采用**分块稀疏矩阵乘法**（基于CUDA自定义算子），将注意力矩阵存储为若干稀疏带状结构而非完整n×n矩阵。关键实现细节是：局部窗口注意力通过将Q、K矩阵进行对角滑动排列后执行批量矩阵乘法（bmm）实现，全局注意力则单独维护两个额外的注意力矩阵（全局→所有，所有→全局），三部分结果求和后经softmax归一化。这种实现在序列长度4096时，显存占用约为全注意力的**1/8**。

---

## 实际应用

**长文档问答（Longformer-QA）**：在TriviaQA数据集上，Longformer-base（1.4亿参数，最大序列长度4096）的F1分数达到75.2，优于RoBERTa-large的仅能截断到512 token的74.0，证明稀疏注意力在保留完整文档上下文方面的有效性。

**基因组序列建模（BigBird-Genomics）**：BigBird将序列长度扩展至4096个核苷酸碱基，用于预测启动子区域和剪接位点，在ENCODEdb数据集上的AUROC较Transformer基线提升约3个百分点。这一场景中不存在自然的"CLS token"，研究者改用序列首尾各一个sentinel token作为全局节点。

**代码理解任务**：StarCoder等代码大模型在推理阶段引入稀疏注意力（结合滑动窗口与关键token全局注意力），使16K token的代码文件上下文处理在单张A100（80GB）上成为可能，而标准全注意力在同等硬件上的上限约为8K token。

**生产级部署中的混合策略**：GPT-4等闭源模型的技术报告暗示使用了稀疏+密集的混合注意力层——底层少数层使用全密集注意力捕获细粒度局部特征，中高层使用稀疏注意力处理长程依赖，这一策略在保持模型质量的同时将推理FLOPs降低约30-40%。

---

## 常见误区

**误区一：稀疏注意力=放弃远距离依赖**
许多人误认为局部窗口注意力无法捕获相距超过窗口大小的两个token之间的关系。实际上，经过多层堆叠后，感受野（receptive field）以窗口大小为公比呈层数次幂增长——对于窗口大小w=512、12层的模型，理论上最大感受野覆盖512¹²个位置，远超任何实际序列长度。全局注意力机制进一步确保了关键信息的全局流通。

**误区二：稀疏注意力一定比FlashAttention快**
FlashAttention是一种**IO感知的全注意力算法**，通过分块计算避免显存带宽瓶颈，在序列长度≤8K时，其实际延迟往往低于稀疏注意力——后者的稀疏矩阵操作存在较高的CUDA kernel启动开销和不规则内存访问模式。只有当序列长度超过约16K token时，稀疏注意力的O(n)复杂度优势才能超过FlashAttention的O(n²)实现的常数项优势。两者并非替代关系，FlashAttention v2已支持对稀疏注意力模式的加速。

**误区三：稀疏模式可以任意设计**
随意的稀疏模式可能导致注意力图的**连通分量断裂**，即序列被分割为无法相互通信的子图，引发信息孤岛。例如，纯粹的固定步长注意力（Sparse Transformer的strided pattern，步长s=√n时仅连接位置i与i+s的倍数）在某些序列长度下存在联通性缺陷，这也是BigBird引入随机注意力分量的核心动机。

---

## 知识关联

稀疏注意力建立在**标准自注意力**（Q·Kᵀ/√d_k后接softmax·V）的基础上，将其注意力矩阵从全连接替换为结构化稀疏矩阵；理解注意力分数的计算方式和多头机制是分析各种稀疏模式效果的前提。

与**FlashAttention**的关系是互补而非竞争：FlashAttention解决了注意力计算中的显存带宽问题，而稀疏注意力解决的是计算量和序列长度的根本限制；在实际系统中两者经常叠加使用，如FlashAttention-2的块状稀疏注意力（block-sparse flash attention）接口允许传入自定义稀疏掩码矩阵。

**上下文窗口**的极限直接决定了何时需要引入稀疏注意力：当所需处理的文本长度超过模型密集注意力显存承受的上限（通常对于7B模型在A100-80GB上约为16-32K token的全注意力），稀疏注意力成为在不增加硬件的前提下扩展有效上下文的首选工程路径。