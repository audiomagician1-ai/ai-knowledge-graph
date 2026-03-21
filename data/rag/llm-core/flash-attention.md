---
id: "flash-attention"
concept: "FlashAttention"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "S"
quality_score: 95.7
generation_method: "hand-crafted"
unique_content_ratio: 0.978
last_scored: "2026-03-21"
sources: []
---
# FlashAttention

## 概述

FlashAttention 是一种 IO-aware 的精确注意力算法，难度等级 8/9。它通过分块计算（tiling）和核融合（kernel fusion）技术，将注意力计算的显存复杂度从 O(N²) 降到 O(N)，同时因减少 GPU HBM 访问次数而获得 2~4x 的实际速度提升。关键点：FlashAttention 不是近似算法，其输出与标准注意力数学上完全一致。

本概念建立在自注意力机制基础之上，与 LLM Serving 优化密切相关。

## 核心原理

### GPU 内存层级

```
┌─────────────────────────────┐
│   SRAM (片上缓存)            │  ~20MB, ~19TB/s 带宽
│   ↕ 极快                     │
├─────────────────────────────┤
│   HBM (高带宽显存)           │  ~80GB, ~2TB/s 带宽
│   ↕ 相对较慢                 │
├─────────────────────────────┤
│   CPU DRAM                   │  ~1TB, ~50GB/s 带宽
└─────────────────────────────┘

标准Attention: Q,K,V 从 HBM 读取 → 计算 S=QK^T → 写回 HBM → 
              读取 S → softmax → 写回 HBM → 读取 × V → 写回 HBM
              多次 HBM 读写成为瓶颈!

FlashAttention: 分块加载到 SRAM → 在 SRAM 内完成全部计算 → 一次写回 HBM
```

### 分块计算 + Online Softmax

FlashAttention 的技术核心是将 N×N 的注意力矩阵分成小块处理：

```
for each Q block (size B_r):
    初始化 running max m = -inf, running sum l = 0, output O = 0
    for each K,V block (size B_c):
        计算 S_block = Q_block × K_block^T          # 在 SRAM 中
        更新 running max: m_new = max(m, rowmax(S_block))
        更新 running sum: l_new = l × exp(m-m_new) + rowsum(exp(S_block-m_new))
        更新 output: O = O × (l×exp(m-m_new)/l_new) + exp(S_block-m_new)/l_new × V_block
        m, l = m_new, l_new
    写回 O block 到 HBM

关键: Online Softmax 使得分块处理得到与全量 softmax 完全相同的结果
```

### 性能对比

| 指标 | 标准Attention | FlashAttention-2 |
|:---|:---|:---|
| 显存 | O(N²) | O(N) |
| HBM 读写 | O(N² + Nd) | O(N²d/M), M=SRAM大小 |
| A100 实测 (seq=2K) | ~120 TFLOPS | ~230 TFLOPS |
| 速度提升 | 1x | 2~4x |

## 实际应用

```python
# PyTorch 2.0+ 原生支持 (sdpa)
import torch
import torch.nn.functional as F

q = torch.randn(1, 32, 4096, 128, device='cuda', dtype=torch.float16)
k = torch.randn(1, 32, 4096, 128, device='cuda', dtype=torch.float16)
v = torch.randn(1, 32, 4096, 128, device='cuda', dtype=torch.float16)

# 自动选择最优后端 (FlashAttention / Memory-Efficient / Math)
output = F.scaled_dot_product_attention(q, k, v, is_causal=True)

# 强制使用 FlashAttention 后端
with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
    output = F.scaled_dot_product_attention(q, k, v, is_causal=True)
```

## 关联知识

- **先修概念**: 自注意力机制（self-attention）— 理解 QK^T softmax V 的标准计算
- **相关概念**: LLM Serving（llm-serving）— FlashAttention 是推理加速的标配
- **互补技术**: KV Cache（减少重复计算）、Speculative Decoding（减少推理步数）

## 常见误区

1. **以为是近似注意力**: FlashAttention 是精确算法，输出bit-level与标准实现一致（float精度内）
2. **认为只影响训练**: FlashAttention 对推理同样重要，尤其是长上下文场景
3. **忽视硬件依赖**: FlashAttention-2 需要 Ampere+ GPU (A100/H100)，部分硬件可能不支持

## 学习建议

- 先理解 GPU SRAM/HBM 层级和 IO 瓶颈的概念
- 学习 Online Softmax（Milakov & Gimelshein, 2018）的推导
- 阅读 FlashAttention 论文（Dao et al., 2022）的 Algorithm 1
- 预计学习时间: 20-32 小时