---
id: "speculative-decoding"
name: "Speculative Decoding"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
tags: ["LLM", "Inference", "Optimization"]
generated_at: "2026-03-19T12:00:00"
---

# Speculative Decoding（推测解码）

## 概述

Speculative Decoding 是一种加速大语言模型自回归推理的技术，难度等级 8/9。其核心思想是：用一个小而快的"草稿模型"（Draft Model）先推测生成多个候选token，再由大模型并行验证，从而将串行逐token生成变为批量并行验证，显著降低推理延迟而不牺牲输出质量。

本概念建立在 LLM 推理和 Transformer 架构的基础之上，与 LLM Serving、KV Cache 等推理优化技术密切相关。

## 核心原理

### 为什么自回归推理慢？

标准自回归生成每步只产出1个token，且每步都需要完整的forward pass。对于百亿参数模型，每个token需要数十毫秒，生成100个token就需要数秒。瓶颈在于**内存带宽**而非计算量——GPU算力大量闲置。

### Speculative Decoding 的两阶段流程

```
阶段1 — 草稿生成（Draft）:
  小模型（如7B）快速自回归生成 K 个候选token: [t1, t2, ..., tK]

阶段2 — 并行验证（Verify）:
  大模型（如70B）对 [prefix, t1, t2, ..., tK] 做一次forward pass
  逐位比较大模型概率分布 vs 小模型概率分布
  接受匹配的前缀 [t1, ..., tn]，在第一个不匹配位置用大模型重新采样

关键保证: 输出分布与直接用大模型生成完全一致（无损加速）
```

### 接受率与加速比

- **接受率 α**: 草稿token被大模型接受的概率，取决于Draft/Target模型的对齐程度
- **加速比**: 理论上 `1/(1-α)` 倍；实践中 α=0.7~0.85 时可获得 2~3x 加速
- **草稿长度 K**: 通常 K=4~8，太长会降低接受率

## 实际应用

### 常见实现方案

| 方案 | Draft Model | 特点 |
|:---|:---|:---|
| **独立小模型** | 同系列小号模型（如 Llama-7B → Llama-70B） | 最通用，需额外显存 |
| **Self-Speculative** | 跳过大模型部分层 | 无需额外模型，但加速比较低 |
| **Medusa** | 在大模型上加多个预测头 | 训练成本高，但推理时无需小模型 |
| **Eagle** | 特征级草稿（非token级） | 更高接受率 |

### 框架支持

```python
# vLLM 中使用 Speculative Decoding
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-70B",
    speculative_model="meta-llama/Llama-3-8B",  # Draft model
    num_speculative_tokens=5,                     # K=5
)
output = llm.generate("Explain quantum computing", SamplingParams(temperature=0.7))
```

## 关联知识

- **先修概念**: LLM推理（llm-inference）、Transformer架构（transformer-architecture）
- **相关概念**: LLM Serving（llm-serving）— 推测解码是serving优化的重要组成部分
- **互补技术**: KV Cache（减少重复计算）、FlashAttention（加速attention计算）、量化（减少模型体积）

## 常见误区

1. **误以为会降低生成质量**: Speculative Decoding 的数学保证是输出分布与原模型完全一致，是无损加速
2. **忽略Draft模型选择的重要性**: Draft模型与Target模型越相似，接受率越高；随意选择小模型可能导致加速比很低
3. **不适用于所有场景**: 当batch size很大时，GPU计算已饱和，推测解码的收益会下降

## 学习建议

- 先理解自回归生成的内存带宽瓶颈，再学习推测解码为什么有效
- 阅读原始论文: "Fast Inference from Transformers via Speculative Decoding" (Leviathan et al., 2023)
- 在 vLLM 或 HuggingFace TGI 中实际配置推测解码并对比延迟
- 预计学习时间: 16-24 小时