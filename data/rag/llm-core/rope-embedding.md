---
id: "rope-embedding"
name: "RoPE Rotary Position Embedding"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
tags: ["LLM", "Position Encoding", "Math"]
generated_at: "2026-03-19T12:00:00"
---

# RoPE（旋转位置编码）

## 概述

RoPE（Rotary Position Embedding）是当前主流大模型（Llama、Qwen、Mistral等）采用的位置编码方案，难度等级 8/9。它通过对 Query 和 Key 向量施加与位置相关的旋转变换，使得内积自然包含相对位置信息，兼具绝对位置编码的简洁性和相对位置编码的泛化能力。

本概念建立在位置编码（Positional Encoding）的基础之上。

## 核心原理

### 动机：为什么不用原始位置编码？

| 方案 | 问题 |
|:---|:---|
| **正弦绝对位置编码**（原始Transformer） | 无法直接编码相对位置；长度外推能力差 |
| **可学习绝对位置编码**（BERT/GPT-2） | 最大长度固定；无法泛化到训练长度之外 |
| **ALiBi** | 线性偏置简单但表达能力有限 |
| **RoPE** | ✅ 内积自然包含相对位置 + 理论上支持任意长度 |

### 数学原理

RoPE 的核心思想：将位置编码转化为向量在复数平面上的旋转。

```
对于位置 m 处的 d 维向量 x，RoPE 将相邻两个维度视为一个复数:

  (x_{2i}, x_{2i+1}) → 旋转角度 θ_i = m × base^(-2i/d)

旋转矩阵:
  RoPE(x, m) = [x_{2i}·cos(mθ_i) - x_{2i+1}·sin(mθ_i),
                x_{2i}·sin(mθ_i) + x_{2i+1}·cos(mθ_i)]

关键性质: <RoPE(q, m), RoPE(k, n)> = f(q, k, m-n)
  → Q和K的内积只依赖于相对位置 (m-n)，而非绝对位置
```

### 长上下文扩展

RoPE 的 base 频率（默认10000）限制了有效上下文长度。扩展方法：

- **NTK-aware Scaling**: 调整 base 值（如 10000→500000），低频分量获得更大外推范围
- **YaRN**: 结合NTK缩放 + 注意力温度调节
- **Dynamic NTK**: 根据实际序列长度动态调整 base

## 实际应用

### PyTorch 实现

```python
import torch

def apply_rope(x: torch.Tensor, positions: torch.Tensor, base: float = 10000.0):
    """Apply RoPE to input tensor. x shape: (batch, seq_len, num_heads, head_dim)"""
    d = x.shape[-1]
    # 计算频率: θ_i = base^(-2i/d)
    freqs = 1.0 / (base ** (torch.arange(0, d, 2, device=x.device).float() / d))
    # 位置 × 频率 → 旋转角度
    angles = positions.unsqueeze(-1) * freqs.unsqueeze(0)  # (seq_len, d/2)
    cos_val = angles.cos()
    sin_val = angles.sin()
    # 拆分偶数/奇数维度并旋转
    x_even, x_odd = x[..., ::2], x[..., 1::2]
    x_rotated_even = x_even * cos_val - x_odd * sin_val
    x_rotated_odd  = x_even * sin_val + x_odd * cos_val
    return torch.stack([x_rotated_even, x_rotated_odd], dim=-1).flatten(-2)
```

## 关联知识

- **先修概念**: 位置编码（positional-encoding）— 理解为什么Transformer需要位置信息
- **后续应用**: RoPE 是理解长上下文模型（128K+）的基础
- **对比概念**: ALiBi（另一种流行的位置编码方案）

## 常见误区

1. **认为RoPE直接加到embedding上**: RoPE 施加在 Q 和 K 上（Attention计算前），而非输入embedding上
2. **混淆绝对/相对**: RoPE 表面上是对每个位置独立操作（像绝对编码），但内积结果只依赖相对位置
3. **忽略长上下文需要额外适配**: 直接将训练时 4K 上下文的 RoPE 模型用于 32K 输入，效果会严重退化，需要 NTK/YaRN 等扩展

## 学习建议

- 先复习复数乘法和旋转矩阵的几何意义
- 手推 2D 情况下 RoPE 的内积公式，验证相对位置性质
- 对比 Llama 和 Mistral 的 RoPE 配置参数差异
- 预计学习时间: 20-32 小时