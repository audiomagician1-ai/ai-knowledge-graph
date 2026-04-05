---
id: "quantization"
concept: "模型量化(GPTQ/AWQ)"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM", "部署"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 模型量化（GPTQ/AWQ）

## 概述

模型量化是将神经网络权重和/或激活值从高精度浮点数（如FP32或FP16）压缩为低比特整数表示（如INT8、INT4甚至INT2）的技术。对于一个70亿参数的LLM，FP16格式需要约14GB显存，而INT4量化后仅需约3.5GB，压缩比达到4倍，使消费级GPU（如RTX 3090）可以部署原本需要A100级别硬件的模型。

GPTQ（Generative Pre-trained Transformer Quantization）由Frantar等人于2022年10月发表在论文《GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers》中，基于OBQ（Optimal Brain Quantization）方法发展而来，专为Transformer架构的逐层量化设计。AWQ（Activation-aware Weight Quantization）由MIT和上海交通大学团队于2023年发布，其核心洞察是：权重中只有约1%的通道对激活值具有显著影响，保护这些关键通道可以大幅降低量化误差。

这两种方法都属于**Post-Training Quantization（PTQ，训练后量化）**，无需重新训练模型，只需少量校准数据（通常128至512个样本）即可完成量化，与QAT（Quantization-Aware Training）相比，工程成本极低，是当前大模型部署的主流方案。

---

## 核心原理

### GPTQ：基于Hessian矩阵的逐层最优化量化

GPTQ的核心思想来自OBQ框架：将量化视为最优化问题，对每一层权重矩阵 $W$，寻找量化后的 $\hat{W}$ 使得输出误差最小。其目标函数为：

$$\arg\min_{\hat{W}} \|WX - \hat{W}X\|_F^2$$

其中 $X$ 是该层的输入激活矩阵，$\|\cdot\|_F$ 为Frobenius范数。GPTQ通过近似Hessian矩阵 $H = 2XX^T$ 来指导量化误差的补偿：当某个权重被量化（引入误差）后，利用Hessian信息将误差传播补偿到同行的其余未量化权重上。具体实现中采用**Cholesky分解**对Hessian逆矩阵进行数值稳定计算，并将权重按列分组（通常每128列一组）进行并行处理，使得对单个175B参数的GPT模型量化时间约为4小时（在单张A100上）。

### AWQ：激活感知的显著权重保护机制

AWQ的关键发现是：在权重矩阵中，对应输入激活值较大通道（即激活值幅度处于top-1%）的权重列对模型输出影响远超其他列。直接对这些显著权重进行INT4量化会引入不可接受的误差。AWQ的解决方案不是为这些权重保留FP16精度（这会破坏硬件的SIMD并行性），而是引入**逐通道缩放因子** $s$：

$$Q(w \cdot s) \cdot \frac{x}{s}$$

通过将权重在量化前乘以 $s > 1$，使其幅度更大、量化精度更高；对应地，激活值除以 $s$ 进行补偿，等效变换不改变输出。$s$ 的最优值通过网格搜索在校准集上确定，AWQ全程**不需要反向传播**，只需前向推理即可完成。

### 量化粒度与分组量化（Group Quantization）

实际部署中，GPTQ和AWQ都采用**分组量化**策略：将权重矩阵按输入维度切分为若干组（group size通常为128），每组独立计算缩放因子（scale）和零点（zero-point）。以LLaMA-2-7B为例，INT4+group128配置下，存储scale和zero-point的开销约为模型总大小的3%-5%，可接受。分组越小，精度越高，但overhead越大；INT4+group32比INT4+group128在困惑度（perplexity）上可降低约0.2-0.5个点。

---

## 实际应用

**使用AutoGPTQ量化LLaMA-2-13B**：在一台A100-40GB服务器上，准备128条WikiText2校准文本，运行GPTQ量化（4bit，group_size=128）约需25分钟。量化后模型从原始FP16的26GB压缩至约7GB，在相同硬件上的批量推理吞吐量提升约2.5倍，PPL（perplexity on WikiText2）从5.47上升至5.65，精度损失约3.3%。

**AWQ在vLLM中的集成**：vLLM从0.2.2版本起原生支持AWQ格式（`--quantization awq`参数），AWQ量化的Mistral-7B模型在A10G GPU上的token生成速度约为60 tokens/second，而FP16版本因显存容量限制无法在该GPU上运行。

**GGUF与llama.cpp的关系**：在CPU推理场景中，GPTQ量化的模型通常需要转换为GGUF格式才能被llama.cpp加载；GGUF支持Q4_K_M等混合精度方案，对Attention层权重保留更高精度，比纯INT4在推理质量上有约0.1 PPL的改善。

---

## 常见误区

**误区1：量化比特数越低，推理速度一定越快**。INT4量化能减少显存占用，但实际计算速度取决于硬件是否支持INT4 GEMM内核。NVIDIA Ampere架构（A100）的INT8 Tensor Core吞吐量是FP16的2倍，但其INT4支持有限；而Ada Lovelace架构（RTX 4090）对INT4有更好的原生支持。在没有对应硬件内核优化的设备上，INT4权重在计算前需要反量化回FP16，此时推理速度反而可能慢于直接FP16推理。

**误区2：GPTQ和AWQ量化结果可以互换使用**。两者的量化格式、存储布局和推理内核完全不同。GPTQ依赖`exllamav2`或`triton`内核，AWQ依赖`awq`专用GEMM内核。混用会导致加载失败或精度崩溃，Hugging Face上的模型卡会明确标注`gptq`或`awq`格式，必须配合对应库使用。

**误区3：增加校准数据集大小能无限提升量化质量**。GPTQ和AWQ的量化质量对校准数据分布敏感，但对数量超过512条后的增益极为有限。MIT团队的AWQ论文实验表明，使用128条与1024条校准数据的PPL差异不超过0.05，但将通用WikiText2校准数据换为特定领域数据（如代码），可对代码生成任务的精度提升约1-2个百分点。

---

## 知识关联

**前置概念——LLM推理优化**：理解KV Cache和张量并行等推理优化手段后，量化可被视为进一步降低显存带宽瓶颈的工具。LLM推理的性能瓶颈通常是内存带宽而非计算量（arithmetic intensity较低），INT4量化将权重传输量减少4倍，直接缓解这一瓶颈。

**后继概念——LLM Serving（vLLM/TGI）**：vLLM的PagedAttention机制与AWQ/GPTQ量化正交，可叠加使用。TGI（Text Generation Inference）从1.0版本起同时支持GPTQ（通过exllama/exllamav2后端）和AWQ量化，部署时需在`--quantize gptq`或`--quantize awq`之间明确选择，因为两者调用的CUDA内核完全不同，且对最小批量大小的性能特征也有差异——AWQ在小批量（batch size=1）时延迟更低，GPTQ+exllamav2在大批量吞吐场景更具优势。