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
quality_score: 62.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.531
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# LLM 高性能服务框架（vLLM / TGI）

## 概述

LLM Serving 框架是专为大语言模型在线推理场景设计的高吞吐量服务系统，其核心挑战在于 GPU 显存的碎片化利用率极低（传统静态分配方式下 KV Cache 显存利用率仅约 20%–40%）以及多并发请求下的批处理调度效率。vLLM（由 UC Berkeley 于 2023 年发布，论文《Efficient Memory Management for Large Language Model Serving with PagedAttention》）和 HuggingFace TGI（Text Generation Inference）是目前生产环境中最广泛部署的两大框架，分别代表了学术驱动的创新路径与工程导向的全栈集成路径。

vLLM 的核心贡献是 PagedAttention 机制，将 KV Cache 的显存管理从连续块改为类似操作系统虚拟内存的分页机制，每个 page 默认存储 16 个 token 的键值对，显存利用率可提升至 96% 以上。TGI 则以对 HuggingFace 模型生态的深度兼容性著称，内建 Tensor Parallelism、量化加载（GPTQ/AWQ/EETQ）以及 Continuous Batching 支持，并通过 gRPC 与 REST 双协议暴露服务端点。两者在实际基准测试中，处理并发 100+ 请求时的吞吐量相比 naive 逐请求推理提升可达 **10–24 倍**。

## 核心原理

### PagedAttention 与显存分页管理（vLLM）

PagedAttention 将每个请求的 KV Cache 切分为固定大小的 **logical block**（默认 block_size=16 tokens），每个 block 映射到一个 **physical block**，由 Block Manager 维护逻辑块到物理块的映射表（类似页表）。当两个请求共享相同的系统提示词（system prompt）时，物理块可以被 **Copy-on-Write** 方式共享，无需复制显存，这在 prefix caching 场景下可节省大量显存。调度器采用 **FCFS + 抢占** 策略：当显存不足时，可将低优先级请求的 KV Cache 换出到 CPU 内存（swap），或直接重新计算（recompute），保证高优先级请求不被饿死。

### Continuous Batching（连续批处理）

传统静态批处理（static batching）要求批内所有请求同时开始、同时结束，导致短请求必须等待最长请求完成才能释放槽位，GPU 利用率低。Continuous Batching（又称 iteration-level scheduling）在**每个解码步骤**后动态检查已完成的序列并插入新请求，将批次填充率从约 30% 提升到接近满载。vLLM 的调度器以 `scheduler_config.max_num_seqs`（默认 256）为并发上限，TGI 通过 `--max-batch-total-tokens` 控制批内 token 总量上限，两者均在迭代粒度而非请求粒度做调度决策。

### 张量并行与流水线并行

在多 GPU 部署中，vLLM 通过 **Megatron-LM 风格的张量并行**将每个 Attention 头和 FFN 的权重矩阵按列/行切分到不同 GPU，每个 Tensor Parallel rank 只持有 `num_heads / tp_size` 个注意力头，通过 `AllReduce` 同步激活值。TGI 的张量并行实现依赖 `safetensors` 格式的预切分权重，启动时通过 `--num-shard` 参数指定 GPU 数量。对于超过单节点显存的超大模型（如 LLaMA-3 405B），还需结合 **Pipeline Parallelism** 将 Transformer 层按深度切分到不同节点，此时需要额外处理 micro-batch 流水线气泡（bubble）带来的效率损失，通常使用 1F1B 调度策略将气泡比率压缩到 `1 / (pipeline_stages)` 以下。

### 量化与精度混合推理

vLLM 原生支持 AWQ（4-bit）、GPTQ（4/8-bit）、FP8（通过 `--dtype fp8`）以及 bitsandbytes 的 NF4 量化格式，在 H100 GPU 上使用 FP8 推理 LLaMA-3 70B 模型时，吞吐量相比 BF16 提升约 **1.8 倍**，显存占用下降 50%。TGI 额外支持 **EETQ**（Efficient Engine for Transformers Quantization），可在不预量化权重文件的情况下实时 INT8 量化，适用于快速部署场景。两者均通过 **CUDA kernel fusion** 将量化反量化操作与矩阵乘法融合，避免额外的显存读写往返。

### Speculative Decoding 集成

vLLM 从 v0.3.0 起支持 **Draft Model + Target Model** 的 Speculative Decoding，使用小模型（如 68M 参数的 Eagle draft）并行生成 `k`（默认 k=5）个候选 token，再由大模型一次性验证，接受率 β 通常在 0.7–0.85 之间，使实际生成速度（tokens/s）提升 2–3 倍。TGI 通过 `--speculate` 参数开启 Medusa 头（在目标模型顶层添加多个并行预测头），无需额外 draft 模型，在 CodeLLaMA-34B 等代码生成任务上加速比约为 **1.9×**。

## 实际应用

**OpenAI 兼容 API 服务部署**：vLLM 提供 `vllm serve meta-llama/Llama-3-70B-Instruct --tensor-parallel-size 4 --quantization awq` 命令，即可在 4× A100 80GB 上以 OpenAI Chat Completion 格式对外提供服务，内建的 `/metrics` 端点输出 Prometheus 格式指标，包括 `vllm:gpu_cache_usage_perc`（显存块使用率）和 `vllm:num_requests_running` 等关键 SLO 监控指标。

**Prefix Caching 加速 RAG 场景**：当系统提示词（system prompt）长度固定时，vLLM 的 automatic prefix caching（APC）功能可将重复 prefix 的 KV Cache 物理块标记为已缓存，后续请求直接复用。在 context length 为 8192、system prompt 占 2048 tokens 的典型 RAG 场景中，首次生成延迟（TTFT，Time to First Token）可降低约 **40%**。

**TGI 在 HuggingFace Inference Endpoints 中的生产应用**：HuggingFace 的托管推理服务 Inference Endpoints 底层使用 TGI，通过 `--trust-remote-code --max-input-length 4096 --max-total-tokens 8192` 等参数组合实现对 Mistral、Falcon、CodeLLaMA 等数十种架构的零配置部署，其内部 token streaming 通过 SSE（Server-Sent Events）推送，P99 首 token 延迟在单 A10G GPU 部署 7B 模型时约为 **200–400ms**。

## 常见误区

**误区一：吞吐量越高，延迟一定越低**。Continuous Batching 提高了系统吞吐量（tokens/second/GPU），但单请求的平均生成延迟（inter-token latency）会因批次变大而上升。在 vLLM 中，`--max-num-seqs=256` 时单请求延迟可能是 `--max-num-seqs=1` 时的 3–5 倍，需根据 SLO 要求（延迟 vs. 吞吐量）在 `max_num_seqs` 和 `max_tokens_in_batch` 上做出权衡，而非无脑最大化批次大小。

**误区二：PagedAttention 适用于所有模型架构**。PagedAttention 依赖对 Attention 计算的 block-wise 重构，对于使用 Sliding Window Attention（如 Mistral）的模型，window 边界处的 block 切分可能导致跨 block 的注意力计算额外开销。此外，对 MoE 模型（如 Mixtral 8×7B）的路由专家调度与 block 管理存在交互复杂性，vLLM 的 MoE 支持需要额外启用 `--enable-expert-tensor-parallelism` 才能获得最优性能。

**误区三：TGI 和 vLLM 的量化格式完全互换**。vLLM 的 AWQ 实现使用 `llm-awq` 的 CUDA kernel，而 TGI 使用自己维护的 `text-generation-inference` 版本的 AWQ kernel，两者对同一 AWQ 量化权重文件的推理精度和速度存在差异（在 LLaMA-2 7B AWQ 4-bit 上测试，TGI 吞吐量约比 vLLM 低 8%，但 TTFT 更稳定）。直接将为 vLLM 优化的量化配置迁移到 TGI 可能无法获得预期性能。

## 知识关联

**依赖 KV Cache 与 FlashAttention**：PagedAttention 本质上是对 KV Cache 显存分配策略的重构，其物理 block 内的注意力计算直接调用 FlashAttention-2 kernel（`flash_attn_varlen_func`），因此 FlashAttention 的 IO-aware tiling 算法是 PagedAttention 性能的底层保障。理解 KV Cache 的 `[batch, num_heads, seq_len, head_dim]` 张量结构，是理解 block_size 选择对显