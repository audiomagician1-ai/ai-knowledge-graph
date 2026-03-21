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
content_version: 1
quality_tier: "S"
quality_score: 97.9
generation_method: "hand-crafted"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# KV Cache（键值缓存）

## 概述

KV Cache 是大模型自回归推理中最基础也最重要的优化技术，难度等级 7/9。在逐token生成过程中，每一步的 Attention 计算都需要用到之前所有token的 Key 和 Value 向量。KV Cache 将这些已计算的 K/V 向量缓存起来，避免重复计算，将推理复杂度从 O(n²) 降至 O(n)。

本概念建立在自注意力机制和 LLM 推理基础之上。

## 核心原理

### 为什么需要 KV Cache？

在 Self-Attention 中：`Attention(Q, K, V) = softmax(QK^T/√d) × V`

自回归生成第 t 个token时，需要：
- Q: 只有当前token的query（1×d）
- K: 所有前 t 个token的key（t×d）
- V: 所有前 t 个token的value（t×d）

**没有KV Cache**: 每步重新计算所有token的K和V → 大量冗余计算
**有KV Cache**: 只计算新token的K和V，拼接到缓存 → 增量计算

### 显存占用计算

```
KV Cache 显存 = 2 × num_layers × num_heads × head_dim × seq_len × batch_size × dtype_bytes

示例（Llama-3-70B, FP16）:
  = 2 × 80 × 64 × 128 × 4096 × 1 × 2 bytes
  = ~10.7 GB（单条4K上下文）

问题: 长上下文（128K）+ 大batch时，KV Cache可能超过模型权重本身的显存
```

### KV Cache 优化技术

| 技术 | 原理 | 节省比例 |
|:---|:---|:---|
| **Multi-Query Attention (MQA)** | 所有head共享同一组K/V | ~8x |
| **Grouped-Query Attention (GQA)** | K/V head数 < Q head数（如8组） | ~4x |
| **PagedAttention (vLLM)** | 类似OS虚拟内存，按页管理KV Cache | 减少碎片浪费 |
| **KV Cache量化** | 将K/V从FP16量化到INT8/INT4 | 2~4x |
| **滑动窗口** | 只保留最近W个token的KV（如Mistral） | W/seq_len |

## 实际应用

### PagedAttention 示例（vLLM）

```python
# vLLM 自动管理 PagedAttention KV Cache
from vllm import LLM, SamplingParams

# PagedAttention 将 KV Cache 分成固定大小的 block（如16 tokens/block）
# 类似操作系统的分页内存管理，消除内存碎片
llm = LLM(model="meta-llama/Llama-3-8B", gpu_memory_utilization=0.9)

# KV Cache 在请求间自动复用和回收
outputs = llm.generate(["Hello, "], SamplingParams(max_tokens=100))
```

### GQA 配置（HuggingFace）

```python
# Llama 3 使用 GQA: 32 Q heads, 8 KV heads
from transformers import LlamaConfig
config = LlamaConfig(
    num_attention_heads=32,       # Q heads
    num_key_value_heads=8,        # KV heads (GQA: 32/8=4 Q heads share 1 KV)
)
# KV Cache 显存减少 4x 相比标准 MHA
```

## 关联知识

- **先修概念**: 自注意力机制（self-attention）、LLM推理（llm-inference）
- **相关概念**: LLM Serving（llm-serving）— KV Cache管理是serving系统的核心挑战
- **互补技术**: FlashAttention（加速attention计算本身）、Speculative Decoding（利用KV Cache批量验证）

## 常见误区

1. **忽略KV Cache的显存开销**: 长上下文场景下KV Cache可能是显存瓶颈，需要提前估算
2. **混淆Prefill和Decode阶段**: Prefill阶段填充整个prompt的KV Cache（计算密集），Decode阶段逐token追加（内存密集），两阶段特性完全不同
3. **认为KV Cache只是简单缓存**: 现代KV Cache管理涉及内存分页、量化、驱逐策略等复杂系统设计

## 学习建议

- 先手动推导一次无KV Cache和有KV Cache的Attention计算对比
- 阅读 vLLM 论文理解 PagedAttention 的设计思想
- 计算自己常用模型在不同上下文长度下的KV Cache显存需求
- 预计学习时间: 12-20 小时