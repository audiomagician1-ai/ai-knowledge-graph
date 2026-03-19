---
id: "llm-serving"
name: "LLM Serving (vLLM/TGI)"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
tags: ["LLM", "Serving", "Deployment"]
generated_at: "2026-03-19T18:00:00"
---

# LLM Serving (vLLM/TGI)

## 概述

LLM Serving 是将大语言模型部署为高并发、低延迟推理服务的工程实践，难度等级 7/9。核心挑战在于：LLM 推理是 memory-bound 的自回归过程，每生成一个 token 都需要加载模型全部权重，如何在有限 GPU 显存下最大化吞吐量和最小化延迟是关键问题。

本概念建立在 LLM 推理、KV Cache、FlashAttention 等基础之上，与量化、模型蒸馏密切相关。

## 核心挑战

### 推理延迟分解

```
一次 LLM 请求的延迟组成:

┌─────────────┬─────────────────────┐
│  Prefill    │     Decode          │
│  (预填充)    │     (解码)           │
├─────────────┼─────────────────────┤
│ 处理 prompt │ 自回归生成每个 token  │
│ 全量计算     │ 逐 token 计算        │
│ compute-    │ memory-bound        │
│ bound       │ (加载 KV Cache)      │
│ 一次完成     │ 循环 N 次           │
├─────────────┼─────────────────────┤
│ ~100ms      │ ~20ms × N tokens    │
│ (512 tokens │ (生成 200 tokens     │
│  prompt)    │  ≈ 4s)              │
└─────────────┴─────────────────────┘

核心优化方向:
  Prefill → 并行化/FlashAttention/Chunked Prefill
  Decode  → 批处理/KV Cache复用/Speculative Decoding
```

### 显存分配

```
以 LLaMA-7B (FP16) 为例:

模型权重:     ~14 GB (70亿参数 × 2 bytes)
KV Cache:     ~2 GB/请求 (seq_len=2048, 32层)
激活值:       ~1 GB
CUDA 开销:    ~1 GB
─────────────────────
单请求合计:   ~18 GB → 需要 24GB GPU (A5000/4090)

瓶颈: batch_size 增大 → KV Cache 线性增长 → OOM
```

## 主流 Serving 框架

### vLLM

```python
# vLLM — 最流行的开源 LLM Serving 框架
# 核心创新: PagedAttention

from vllm import LLM, SamplingParams

# 加载模型
llm = LLM(
    model="meta-llama/Llama-3-8B-Instruct",
    tensor_parallel_size=2,        # 2 GPU 张量并行
    gpu_memory_utilization=0.9,    # 使用 90% GPU 显存
    max_model_len=4096,
    quantization="awq"             # AWQ 量化
)

# 批量推理
params = SamplingParams(temperature=0.7, max_tokens=512)
outputs = llm.generate(["Hello, who are you?"] * 10, params)
```

**PagedAttention 核心思想**:

```
传统方式: 为每个请求预分配最大 KV Cache → 显存碎片严重
  请求A: [█████░░░░░░░░░░░]  已用5块，预留16块
  请求B: [███░░░░░░░░░░░░░]  已用3块，预留16块
  显存利用率: 8/32 = 25%

PagedAttention: 按需分配，类似操作系统虚拟内存分页
  物理块: [A][A][B][A][B][A][B][A]  按需分配
  请求A 逻辑页表: page0→物理块0, page1→物理块1, ...
  请求B 逻辑页表: page0→物理块2, page1→物理块4, ...
  显存利用率: 接近 100%，支持 2~4x 更多并发请求!
```

### Text Generation Inference (TGI)

```bash
# Hugging Face TGI — 生产级 Serving
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Llama-3-8B-Instruct \
  --max-batch-prefill-tokens 4096 \
  --max-total-tokens 8192 \
  --quantize gptq

# 特色:
# - Continuous batching (连续批处理)
# - Flash Attention 2 集成
# - Tensor parallelism
# - GPTQ/AWQ/EETQ 量化支持
# - Prometheus metrics 内建
```

### 框架对比

| 特性 | vLLM | TGI | SGLang | Ollama |
|:---|:---:|:---:|:---:|:---:|
| PagedAttention | ✅ | ❌ | ✅ | ❌ |
| Continuous Batching | ✅ | ✅ | ✅ | ❌ |
| Tensor Parallel | ✅ | ✅ | ✅ | ❌ |
| 量化支持 | AWQ/GPTQ/FP8 | GPTQ/AWQ | AWQ/GPTQ | GGUF |
| OpenAI 兼容 API | ✅ | ✅ | ✅ | ✅ |
| 适用场景 | 高吞吐生产 | HF 生态 | 复杂推理 | 本地开发 |

## 关键优化技术

### Continuous Batching

```
静态批处理: 等凑满一批 → 所有请求同时开始同时结束 → 短请求等长请求
  时间 →  ████████████
          ████░░░░░░░░  (短请求早完成，GPU空等)
          ████████████

连续批处理: 请求完成立即腾位，新请求随时插入
  时间 →  ████████████
          ████ 新请求███
          ████████ 新██
  GPU 利用率: ~100%
```

### Prefix Caching

```
多个请求共享相同的 system prompt:
  "You are a helpful assistant..." (500 tokens)

无 Prefix Cache: 每个请求都重新计算这 500 tokens 的 KV Cache
有 Prefix Cache: 计算一次，所有请求复用 → Prefill 速度 2~5x 提升
```

## 常见误区

1. **只关注 tokens/s**: 需要同时关注 TTFT (Time to First Token) 和 TPS
2. **忽略排队延迟**: 高并发下排队等 GPU 的时间可能远超推理时间
3. **盲目追求最大 batch_size**: batch 太大会导致单请求延迟上升
4. **忽视量化收益**: INT4 量化可将显存需求降低 75%，精度损失通常 <1%

## 与相邻概念关联

- **前置**: KV Cache、FlashAttention — 理解推理加速的基础机制
- **前置**: 量化 — 降低显存需求的关键技术
- **关联**: Speculative Decoding — 在 Serving 层面加速自回归解码
- **应用**: Agent 系统 — Agent 的实时响应依赖高效 Serving
- **进阶**: 分布式推理 — 超大模型的多机多卡部署
