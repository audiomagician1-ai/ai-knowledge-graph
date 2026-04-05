---
id: "llm-serving"
concept: "LLM Serving (vLLM/TGI)"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# LLM 高性能服务框架（vLLM / TGI）

## 概述

LLM Serving 框架专为大语言模型在线推理场景设计，核心挑战有两点：一是 GPU 显存的碎片化问题——传统静态分配方式下 KV Cache 显存利用率仅约 20%–40%，大量显存因请求序列长度不确定而被预留浪费；二是多并发请求下的批处理调度效率，naive 逐请求串行推理的 GPU 利用率通常低于 15%。

vLLM（由 UC Berkeley RISE Lab 于 2023 年 6 月发布，论文 "Efficient Memory Management for Large Language Model Serving with PagedAttention"，作者 Kwon 等，发表于 SOSP 2023）和 HuggingFace TGI（Text Generation Inference，首个生产版本 v0.9 发布于 2023 年初）是目前生产环境中最广泛部署的两大框架。vLLM 代表学术驱动的创新路径，以 PagedAttention 为核心突破；TGI 代表工程导向的全栈集成路径，以对 HuggingFace 模型生态的深度兼容性著称。在 A100-80GB 单卡上，使用 LLaMA-2-13B 模型处理 128 并发请求时，vLLM 相比 Hugging Face 原生 `generate()` 方法吞吐量提升达 **24 倍**（Kwon et al., SOSP 2023）。

## 核心原理

### PagedAttention 与显存分页管理（vLLM）

PagedAttention 的灵感直接来源于操作系统的虚拟内存与分页机制。每个请求的 KV Cache 被切分为固定大小的 **logical block**（默认 `block_size=16` tokens），每个 logical block 映射到一个 **physical block**，由 `BlockSpaceManager` 维护逻辑块到物理块的映射表，其结构类似 CPU 的页表（page table）。

Physical block 的大小计算公式如下：

$$\text{block\_memory} = 2 \times \text{num\_layers} \times \text{num\_heads} \times \text{head\_dim} \times \text{block\_size} \times \text{dtype\_bytes}$$

以 LLaMA-2-7B（32 层，32 头，head\_dim=128，block\_size=16，FP16）为例：

$$\text{block\_memory} = 2 \times 32 \times 32 \times 128 \times 16 \times 2 = 8{,}388{,}608 \text{ bytes} \approx 8 \text{ MB}$$

一张 40GB A100 扣除模型权重（约 14GB for FP16）后，剩余约 26GB 可分配约 **3250 个 physical block**，对应最多容纳约 52,000 个 token 的 KV Cache。

当两个请求共享相同的系统提示词（system prompt）时，对应的 physical block 以 **Copy-on-Write（COW）** 方式共享，仅当某请求需要写入新 token 时才触发复制。这在 prefix caching 场景下（例如大量用户请求共享同一段 RAG 检索文本）可节省 30%–60% 的 KV Cache 显存。

调度器采用 **FCFS + 抢占（preemption）** 策略：当显存不足时，可将低优先级请求的 KV Cache 换出到 CPU 内存（swap out），或直接丢弃并重新计算（recompute），保证高优先级请求不被饿死。vLLM v0.3 之后引入了 `chunked prefill`，将长 prefill 请求拆分为多个 chunk 与 decode 请求交错执行，进一步降低 prefill 阶段对 decode 请求的延迟干扰（即降低 time-to-first-token，TTFT）。

### Continuous Batching（连续批处理）

传统静态批处理（static batching）要求批内所有请求同时开始、同时结束，短请求必须等待批内最长请求完成才能释放槽位，GPU 实际利用率仅约 30%。Continuous Batching（又称 **iteration-level scheduling**，由 Yu et al. 在论文 "Orca: A Distributed Serving System for Transformer-Based Generative Models"，OSDI 2022 首次提出）在**每个解码迭代步骤后**动态检查已完成的序列并立即插入新等待请求，将批次填充率提升到接近满载。

vLLM 的调度器关键参数：
- `max_num_seqs`：同时处于运行状态的最大序列数，默认 256
- `max_num_batched_tokens`：单次迭代最大 token 数，默认值等于 `max_model_len`（通常 4096 或 8192）
- `max_paddings`：允许的最大 padding token 数，控制批内碎片

TGI 对应参数为 `--max-batch-total-tokens`（通常设为显存允许的最大值，如 A100-80G 上跑 LLaMA-2-13B 可设为 32000）和 `--max-concurrent-requests`。

### 张量并行与流水线并行

在多 GPU 部署中，vLLM 采用 **Megatron-LM 风格的张量并行（Tensor Parallelism, TP）**：每个 Transformer 层中 Attention 的 Q/K/V 投影矩阵按 `num_heads / tp_size` 列切分分布到不同 GPU，输出投影矩阵按行切分，FFN 的第一个线性层按列切分，第二个按行切分，每个 TP 步骤末尾通过 `AllReduce` 合并结果，通信量为 $2 \times \text{sequence\_length} \times \text{hidden\_size} \times \text{dtype\_bytes}$。

**流水线并行（Pipeline Parallelism, PP）** 将模型层按组切分到不同 GPU（如 LLaMA-2-70B 的 80 层可 4 卡 PP，每卡 20 层），适合显存容量瓶颈场景，但会引入气泡（pipeline bubble）开销，通常 PP 优先于 TP 仅在单机多卡显存不足时使用。vLLM 从 v0.2 开始支持 TP，从 v0.4 开始支持 PP，可通过 `tensor_parallel_size` 和 `pipeline_parallel_size` 参数控制。

## 关键配置与部署示例

### vLLM 快速部署

```python
# 安装: pip install vllm>=0.4.0
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-2-13b-chat-hf",
    tensor_parallel_size=2,       # 2 GPU 张量并行
    gpu_memory_utilization=0.90,  # 使用 90% GPU 显存分配 KV Cache
    max_model_len=4096,
    quantization="awq",           # 加载 AWQ 量化权重
    block_size=16,                # PagedAttention block size
    enable_prefix_caching=True,   # 开启 prefix KV Cache 共享
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    repetition_penalty=1.1,
)

outputs = llm.generate(["请介绍 PagedAttention 的原理", "什么是 Continuous Batching？"], sampling_params)
for output in outputs:
    print(output.outputs[0].text)
```

### TGI 部署命令

```bash
# 使用 Docker 部署 TGI，适合 LLaMA-2-13B on 2xA100-40GB
docker run --gpus all --shm-size 1g \
  -p 8080:80 \
  -v /data/models:/data \
  ghcr.io/huggingface/text-generation-inference:2.0 \
  --model-id meta-llama/Llama-2-13b-chat-hf \
  --num-shard 2 \
  --max-batch-total-tokens 32000 \
  --max-input-length 2048 \
  --max-total-tokens 4096 \
  --quantize awq \
  --rope-scaling dynamic \
  --rope-factor 2.0
```

TGI 的 `/generate` REST 端点返回 JSON，`/generate_stream` 支持 SSE 流式输出；同时暴露 `/metrics` Prometheus 端点，可直接对接 Grafana 监控 `tgi_request_duration_seconds` 等指标。

## 实际应用与性能调优

### 吞吐量 vs 延迟的权衡

LLM Serving 存在根本性的吞吐量与延迟权衡：增大批次大小（batch size）可显著提升每秒生成 token 数（tokens/s），但同时增加每个请求的排队延迟和 time-to-first-token（TTFT）。

实践调优经验：
- **在线服务（chatbot）**：优先控制 P99 TTFT < 1s，设置 `max_num_seqs=64`，`max_num_batched_tokens=8192`，避免超长 prefill 抢占 decode。
- **离线批量推理**：最大化吞吐量，设置 `gpu_memory_utilization=0.95`，`max_num_seqs=512`，开启 `chunked_prefill`。
- **混合负载**：使用 vLLM 的 `priority scheduling`（v0.5 引入）按请求优先级分配 KV Cache 槽位。

以 LLaMA-2-70B（4xA100-80GB，TP=4，AWQ 4bit 量化）为例，TGI 在 `max-batch-total-tokens=20000` 配置下可达到约 **1200 tokens/s** 的生成吞吐量，而 naive 单请求推理仅约 **55 tokens/s**，差距约 22 倍。

### 量化集成对显存与速度的影响

| 量化方式 | LLaMA-2-70B 显存占用 | 相对 FP16 速度 | 精度损失（PPL 增量） |
|----------|----------------------|---------------|----------------------|
| FP16     | ~140 GB              | 1.0×          | 0                    |
| GPTQ-4bit | ~38 GB             | 1.3×–1.8×     | +0.3–0.8             |
| AWQ-4bit  | ~38 GB             | 1.5×–2.0×     | +0.2–0.5             |
| EETQ-8bit | ~75 GB             | 0.95×         | +0.05–0.1            |

vLLM 通过 `quantization="awq"` 或 `"gptq"` 参数直接加载量化权重，使用 `AutoAWQ` 或 `auto-gptq` 内核；TGI 通过 `--quantize awq/gptq/eetq` 选项实现相同功能，内部调用同一套 CUDA 内核。

## 常见误区

**误区一：`gpu_memory_utilization=1.0` 可以最大化吞吐量。**  
实际上，将显存利用率设为 100% 会导致 CUDA OOM 因为 vLLM 在运行时还需要少量显存用于 CUDA 图（CUDA Graph）缓存和激活值，推荐值为 0.88–0.92。A100-80GB 上跑 LLaMA-2-13B FP16，`gpu_memory_utilization=0.90` 可分配约 4800 个 KV block，而设为 1.0 则极大概率在首批大请求时 OOM 崩溃。

**误区二：PagedAttention 必然优于静态 KV Cache。**  
在极短序列（< 64 tokens）且并发极低（< 4 请求）的场景下，PagedAttention 的 block 映射表维护开销（每个 token 生成步骤需查询块表）反而可能引入 5%–10% 的额外延迟。这种场景更适合直接使用 `transformers` 库的 `generate()` 配合 `static_cache`（v4.39 引入）。

**误区三：Tensor Parallelism 越大越快。**  
TP=8 相比 TP=4 需要额外的 `AllReduce` 通信，在 NVLink 带宽充足时（A100/H100 NVLink 600 GB/s）TP=8 仍有加速，但在 PCIe 连接的多卡环境（带宽 ~64 GB/s）下，TP 超过 2 时通信开销可能抵消并行收益，实测 LLaMA-2-13B on 4xA100-PCIe 时 TP=2 比 TP=4 吞吐量高约 18%。

**误区四：vLLM 和 TGI 功能完全等价。**  
截至 2024 年，vLLM 支持更多量化格式（包括 `marlin`、`squeezellm`）和实验性多模态推理（LLaVA、InternVL），而 TGI 对 PEFT/LoRA 的动态切换支持（`--adapter-id`）更成熟，可在单个基础模型上热切换多个 LoRA adapter，vLLM 的多 LoRA 支持（`enable_l