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
quality_tier: "B"
quality_score: 47.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.469
last_scored: "2026-03-22"
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

模型量化是将神经网络权重和激活值从高精度浮点数（如FP32或FP16）压缩为低比特整数表示（如INT8、INT4甚至INT2）的技术。对于拥有数十亿参数的大型语言模型，量化能将内存占用减少2至4倍，同时在专用硬件上显著提升推理吞吐量。以LLaMA-2-70B为例，FP16格式需要约140GB显存，而4-bit量化后仅需约35GB，使单机双卡A100即可完成推理。

GPTQ（Generative Pre-trained Transformer Quantization）由Frantar等人于2022年提出，是专为大型生成式语言模型设计的训练后量化（PTQ）方法。AWQ（Activation-Aware Weight Quantization）则由MIT韩松团队于2023年提出，其核心洞察是模型权重并非同等重要——少数"显著权重"对输出质量贡献极大，需要优先保护。这两种方法代表了当前生产环境中大模型量化的主流技术路线。

量化技术的工程意义在于它打破了大模型部署的显存壁垒。没有有效量化方法，70B以上规模的模型实际上无法在消费级或中等规模服务器硬件上运行，而量化使得在单张RTX 3090（24GB）上运行13B模型成为可能，极大降低了大模型应用的硬件门槛。

## 核心原理

### GPTQ：基于二阶信息的逐层量化

GPTQ的理论基础来源于最优脑外科（Optimal Brain Surgeon，OBS）框架，核心思想是用Hessian矩阵的逆来补偿量化误差。对于每一层权重矩阵 $W$，量化目标是最小化输出误差：

$$\min_{\hat{W}} \|WX - \hat{W}X\|_2^2$$

GPTQ以列为单位逐一量化权重，量化第 $q$ 列后，通过以下更新公式补偿剩余未量化列：

$$\delta_F = -\frac{w_q - \text{quant}(w_q)}{[H_F^{-1}]_{qq}} \cdot (H_F^{-1})_{:,q}$$

其中 $H_F$ 是对应子矩阵的Hessian，$w_q$ 是被量化的权重标量。这个补偿步骤使GPTQ在4-bit条件下能将困惑度损失控制在接近FP16的范围内。实践中GPTQ量化一个175B的GPT-3规模模型仅需约4小时（在单张A100上），相比早期方法提速超过10倍。

### AWQ：激活感知的显著权重保护

AWQ发现约1%的权重（对应输入激活值较大的通道）对模型输出的影响远超其余99%。直接量化这些显著权重会引起不可接受的精度损失。AWQ的解决方案不是对显著权重使用高比特，而是通过**逐通道缩放**来降低量化误差：

对于权重 $w$ 和激活 $x$，引入可学习的缩放因子 $s$：

$$\text{quant}(w \cdot s) \cdot (x / s) \approx wx$$

缩放因子 $s$ 通过在少量校准数据上搜索最优值获得，搜索目标是最小化输出均方误差。关键在于 $s$ 的乘法被折叠进相邻的LayerNorm层，**推理时无额外计算开销**。AWQ在相同bit宽度下通常比GPTQ在代码生成、数学推理等任务上多保留0.5-2个百分点的精度。

### 量化粒度与分组量化

两种方法都支持**分组量化（Group Quantization）**，即将权重矩阵按128或64个元素为一组，每组独立计算缩放因子和零点。分组大小（group size）是关键超参数：group_size=128是常见平衡点，更小的分组（如32）提升精度但增加额外参数开销（每组需存储scale和zero_point），更大的分组节省内存但精度下降更明显。典型4-bit + group_size=128的配置下，额外开销约为权重体积的3%。

## 实际应用

**模型量化工具链**：GPTQ量化可通过`AutoGPTQ`库实现，AWQ量化使用`AutoAWQ`库。以AWQ量化Mistral-7B为例，核心代码仅需指定`w_bit=4, q_group_size=128, zero_point=True`三个参数，并提供128条校准文本（通常取自Pile或C4数据集），整个量化过程在单张A100上约15分钟完成。

**vLLM的量化集成**：vLLM原生支持GPTQ和AWQ格式，加载量化模型只需在`LLM()`初始化时指定`quantization="awq"`参数。量化模型在vLLM的PagedAttention机制下，吞吐量相比未量化模型在INT4精度下可提升1.5至2倍，因为KV Cache和权重传输的带宽瓶颈同时得到缓解。

**Hugging Face生态中的量化模型**：TheBloke等社区贡献者在Hugging Face Hub上发布了数千个预量化模型，格式命名通常为`模型名-GPTQ`或`模型名-AWQ`。工程师可直接下载使用，无需自行量化，大幅简化了生产部署流程。对延迟敏感的场景（如实时对话）通常选择AWQ，对吞吐量优先的批处理场景两者差异不显著。

## 常见误区

**误区一：量化比特数越低精度损失越大，INT4必然不可用**。实际上GPTQ和AWQ的4-bit量化在多数任务上与FP16的差距小于1%，而INT4的显存节省（4x vs FP16）在工程上价值极大。真正不可接受的精度损失通常在INT2或INT3时才明显出现。需要根据具体评测指标（如MMLU、HumanEval分数）而非直觉判断可接受性。

**误区二：GPTQ和AWQ的量化模型可以互换使用**。两种格式的权重存储方式和反量化内核实现完全不同，GPTQ使用基于Cholesky分解的重打包格式，AWQ使用专用的`gemm`/`gemv`内核（来自`llm-awq`项目）。混用格式会导致推理结果错误或直接报错，必须确认推理框架（如vLLM、llama.cpp、TGI）对具体量化格式的支持版本。

**误区三：量化可以完全替代更高精度的微调**。量化是推理阶段的压缩技术，在量化模型上进行LoRA等微调（即QLoRA）时，前向传播用量化权重，反向传播的梯度仍需要高精度适配器参数。若直接对AWQ/GPTQ格式模型做全量微调，量化误差会在训练中累积导致模型损坏。

## 知识关联

**前置知识**：LLM推理优化的基础知识（显存带宽瓶颈分析、Roofline模型）是理解为什么量化有效的关键——LLM推理在decode阶段是内存带宽受限而非计算受限，INT4权重将每次权重加载的数据量减少4倍，直接缓解这一瓶颈。掌握Transformer的LayerNorm和线性层结构有助于理解AWQ缩放因子折叠的实现位置。

**后续方向**：学习LLM Serving（vLLM/TGI）时，量化模型的加载、批处理调度与PagedAttention的协同是重要工程细节。进阶可研究**量化感知训练（QAT）**（如LLM-QAT）和**GGUF格式**（llama.cpp使用，支持混合精度量化，对CPU推理有独特优化）以及**SmoothQuant**（专注于激活值量化的W8A8方案，与GPTQ/AWQ的纯权重量化路线互补）。