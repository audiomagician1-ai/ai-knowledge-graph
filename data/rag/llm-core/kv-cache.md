---
id: "kv-cache"
concept: "KV Cache"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 91.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.966
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# KV Cache（键值缓存）

## 概述

KV Cache是Transformer自回归生成中的核心加速机制，通过缓存每一层注意力计算中的Key矩阵和Value矩阵，避免在生成新token时对历史token重复计算注意力权重。在没有KV Cache的情况下，生成第n个token需要对前n-1个token重新执行一次完整的前向传播，时间复杂度为O(n²)；启用KV Cache后，每步仅需计算当前新token的Q/K/V并追加到缓存，将生成阶段的复杂度降至O(n)。

KV Cache的实践根源来自2017年"Attention is All You Need"中提出的多头注意力机制。在原始训练阶段，所有token并行处理，无需缓存；但GPT系列模型的自回归推理（逐token生成）天然引入了时序依赖性。随着GPT-2（2019年）和GPT-3（2020年）的部署需求急剧上升，KV Cache作为工程优化手段被系统化提出并广泛采用，成为任何生产级LLM推理引擎的标配组件。

KV Cache的重要性体现在具体数字上：以GPT-3（175B参数，96层，96头，d_model=12288）为例，在序列长度2048时，单个请求的KV Cache占用约为96层 × 2（K+V）× 2048 × 12288 × 2字节（fp16）≈ 48 GB，与模型权重本身量级相当。这说明KV Cache的内存管理直接决定了推理系统的吞吐量上限。

---

## 核心原理

### 注意力计算中的K/V复用逻辑

标准多头注意力的计算公式为：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

在自回归生成中，第t步生成token时，Query只有1个向量（当前token），但Key和Value来自所有前t个token。由于历史token的输入嵌入在生成阶段不变，其对应的K和V向量也不变。KV Cache的本质是将第1到t-1步已计算的$K_1, K_2, ..., K_{t-1}$和$V_1, V_2, ..., V_{t-1}$保存在显存中，第t步仅计算新token的$K_t$和$V_t$后追加，再用当前Q对完整缓存做一次attention。

需要注意的是，**每一层（layer）和每一头（head）都有独立的KV Cache**，不能跨层共享，因为不同层的线性投影矩阵$W_K$、$W_V$不同，同一输入在不同层产生不同的K/V表示。

### 两阶段推理：Prefill与Decode

使用KV Cache的LLM推理分为两个截然不同的阶段：

- **Prefill阶段**：对输入的prompt（设长度为L）并行计算所有token的K和V，填充Cache。该阶段是计算密集型（compute-bound），GPU利用率高，耗时约与L成正比。
- **Decode阶段**：逐token生成，每步只计算1个新token的K/V并追加，然后用其Q对完整Cache做attention。该阶段是**内存带宽密集型（memory-bound）**，因为每步都需要将整个KV Cache从显存搬运到计算单元，GPU的Tensor Core实际利用率极低（通常低于10%）。

这一"compute-bound + memory-bound"的分离特性，直接催生了连续批处理（Continuous Batching）等优化策略。

### KV Cache的内存占用公式

对于单个请求，KV Cache的总内存占用为：

$$\text{Memory}_{KV} = 2 \times n_{layers} \times n_{heads} \times d_{head} \times L_{seq} \times \text{dtype\_size}$$

其中系数2来自K和V两个矩阵，$d_{head} = d_{model} / n_{heads}$，$L_{seq}$为当前序列总长度，dtype\_size对于fp16为2字节。以LLaMA-2 7B（32层，32头，d\_model=4096，d\_head=128）、序列长度4096为例，KV Cache约为：

$$2 \times 32 \times 32 \times 128 \times 4096 \times 2 \approx 2 \text{ GB}$$

---

## 实际应用

### 多查询注意力（MQA）与分组查询注意力（GQA）

标准多头注意力中每个头都有独立的K/V投影，KV Cache随头数线性增长。**多查询注意力（Multi-Query Attention, MQA）**（Shazeer, 2019）让所有头共享同一组K/V，将KV Cache压缩至原来的$1/n_{heads}$，代价是模型表达能力略有下降。**分组查询注意力（Grouped Query Attention, GQA）**（Ainslie et al., 2023）是折中方案：将$n_{heads}$个Q头分为G组，每组共享一对K/V，LLaMA-2 70B和Mistral 7B均采用GQA（G=8），在几乎不损失精度的前提下将KV Cache降至MHA的1/4到1/8。

### vLLM的PagedAttention

传统KV Cache预分配连续显存块（如预留最大序列长度的空间），导致严重的内部碎片（平均浪费约60-80%显存）。vLLM（2023年）提出**PagedAttention**，借鉴操作系统虚拟内存分页思想：将KV Cache分割为固定大小的Block（如16个token/block），按需动态分配，并通过Block Table记录逻辑页到物理页的映射。这使得vLLM的吞吐量相比基线HuggingFace实现提升约24倍，同时支持多序列间的KV Cache共享（用于Beam Search和prefix caching）。

### Prefix Caching（系统提示缓存）

对于使用固定system prompt的应用（如客服机器人），每次请求都重复计算相同前缀的KV是极大浪费。Prefix Caching将固定前缀的KV Cache持久化保存，新请求直接复用，将prefill时间从O(L_prefix + L_input)降至O(L_input)。SGLang框架将此扩展为RadixAttention，用基数树（Radix Tree）管理所有历史请求的KV Cache前缀，实现跨请求的最大化复用。

---

## 常见误区

### 误区一：KV Cache加速了Prefill阶段

KV Cache对prefill阶段**没有加速效果**。Prefill本就是并行计算所有prompt token，不存在重复计算问题。KV Cache的加速只体现在Decode阶段——避免对已生成token重新计算K/V。将KV Cache等同于"整体推理加速"是不准确的，更准确的说法是"KV Cache消除了Decode阶段的冗余计算"。

### 误区二：KV Cache越大越好，应尽量预留最大序列长度

预分配最大序列长度的KV Cache（如4096个token）会导致大量显存浪费，因为绝大多数请求实际长度远短于最大值。更严重的是，固定预分配会使系统无法同时处理更多并发请求，吞吐量反而下降。正确做法是采用动态分配策略（如PagedAttention），按实际生成的token数动态增长KV Cache，最大化批处理大小。

### 误区三：KV Cache对所有注意力变体均适用

KV Cache依赖于"历史token的K/V不随新token生成而改变"这一前提。某些注意力变体打破了此前提：例如**ALiBi**位置编码在计算attention时动态修改注意力分数（而非K/V本身），理论上可兼容KV Cache；但**相对位置编码（如T5的Relative Bias）**若直接修改K矩阵的计算，则KV Cache实现需要特殊处理。RoPE（旋转位置编码）通过对Q和K施加旋转变换来注入位置信息，K的值依赖于其绝对位置，但由于每个token的位置固定不变，RoPE与KV Cache完全兼容，这也是LLaMA系列选择RoPE的工程原因之一。

---

## 知识关联

**前置知识承接**：KV Cache直接建立在多头注意力的Q/K/V分解之上——若不理解$W_Q, W_K, W_V$三个投影矩阵的作用，就无法理解为何只缓存K和V而非Q（Q是当前查询token独有的，每步都不同）。LLM推理优化的基础分析框架（Roofline模型，区分compute-bound与memory-bound）为理解KV Cache为何将Decode阶段变为内存带宽瓶颈提供了量化依据。

**后续知识延伸**：理解KV Cache的内存占用公式和碎片问题，是学习**vLLM、TGI等推理框架**的必要基础。PagedAttention的Block管理、Continuous Batching的序列调度、Tensor Parallelism下的KV Cache分片策略，都是在KV Cache的内存模型之上构建的。此外，**长上下文推理**（如支持128K token的Claude 3）的核心挑战之一正是KV Cache的显存占用随序列长度线性增长，催生了StreamingLLM的attention sink概念以及各种KV Cache压缩（量化至int4/int8、驱逐低重要性token的KV等）技术路线。