---
id: "llm-distillation"
name: "Model Distillation"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
tags: ["LLM", "Distillation", "Compression"]
generated_at: "2026-03-19T18:00:00"
---

# Model Distillation

## 概述

Model Distillation（模型蒸馏）是将大型 Teacher 模型的能力迁移到小型 Student 模型的训练技术，难度等级 7/9。核心思想是让 Student 学习 Teacher 的"软标签"（概率分布），而非训练数据的"硬标签"（one-hot），从而以更少的参数量获得接近 Teacher 的性能。这是 LLM 工程化落地的关键技术——在成本和延迟受限场景中部署轻量级模型。

本概念建立在 LLM 预训练和 Fine-tuning 基础之上，与量化、LLM Serving 互为补充的模型压缩方案。

## 核心原理

### 知识蒸馏框架

```
                Teacher Model (405B)
                      │
              推理 N 万条数据
                      │
                      ▼
              软标签 (Soft Labels)
              P_t = softmax(z_t / T)
              T = temperature (温度)
                      │
                      ▼
┌──────────────────────────────────┐
│          Student Model (8B)       │
│                                   │
│  Loss = α × KL(P_t ∥ P_s)       │  ← 蒸馏损失 (学习 Teacher 分布)
│        + (1-α) × CE(y, P_s)      │  ← 任务损失 (学习真实标签)
│                                   │
│  P_s = softmax(z_s / T)          │
└──────────────────────────────────┘
```

### 温度参数的作用

```python
import torch.nn.functional as F

# 硬标签 (T=1): 信息集中在正确答案
logits = [5.0, 2.0, 0.1, -1.0]
softmax_T1 = F.softmax(torch.tensor(logits) / 1.0)
# → [0.93, 0.046, 0.007, 0.002]  ← 几乎只有第一个有值

# 软标签 (T=3): 暴露类间相似性
softmax_T3 = F.softmax(torch.tensor(logits) / 3.0)
# → [0.51, 0.21, 0.15, 0.13]  ← "猫" 比 "狗" 更像 "狮子"
#                                  这种暗知识(dark knowledge)是蒸馏的精髓
```

### LLM 蒸馏的三种范式

| 范式 | 方法 | Teacher 信号 | 典型案例 |
|:---|:---|:---|:---|
| **Logit 蒸馏** | KL 散度匹配 | token 级概率分布 | DistilBERT |
| **合成数据蒸馏** | 用 Teacher 生成训练数据 | 文本输出 | Alpaca, Vicuna |
| **Chain-of-Thought 蒸馏** | 蒸馏推理过程 | 推理链 + 答案 | Orca, WizardLM |

## 关键技术

### 合成数据蒸馏（最常用于 LLM）

```python
# Step 1: 用 Teacher 生成高质量训练数据
teacher_model = "gpt-4o"
prompts = [
    "Explain quantum computing in simple terms",
    "Write a Python function to detect palindromes",
    # ... 数万条 diverse prompts
]

# Step 2: 收集 Teacher 的输出
training_data = []
for prompt in prompts:
    response = call_teacher(teacher_model, prompt)
    training_data.append({
        "instruction": prompt,
        "output": response
    })

# Step 3: 用合成数据 Fine-tune Student
# student_model = "Llama-3-8B"
# SFT on training_data
```

### 实际案例

```
LLaMA 3.1 405B (Teacher) → LLaMA 3.2 1B/3B (Student)
  - Meta 官方蒸馏，保留了大部分 reasoning 能力
  - 3B 模型在手机端运行，延迟 <100ms/token

DeepSeek-R1 671B (Teacher) → DeepSeek-R1-Distill-Qwen-7B (Student)
  - 蒸馏推理链 (Chain-of-Thought)
  - 7B 模型在数学推理上接近 GPT-4o

Phi-3 (Microsoft):
  - 使用"教科书质量"合成数据训练
  - 3.8B 参数超越 LLaMA-2 13B
```

### 蒸馏 vs 其他压缩技术

```
蒸馏 (Distillation):
  405B Teacher → 8B Student
  优点: 架构灵活，可以完全不同的模型
  缺点: 需要重新训练
  
量化 (Quantization):
  8B FP16 → 8B INT4
  优点: 无需训练，即时压缩
  缺点: 参数量不变，只减少位宽

剪枝 (Pruning):
  8B → 6B (移除不重要的权重/层)
  优点: 保持架构相似
  缺点: 效果不如蒸馏

实践中常组合使用:
  405B → 蒸馏 → 8B → 量化 → 8B-INT4 (2GB显存)
```

## 常见误区

1. **Student 越小越好**: Student 太小会导致 capacity gap，无法学习 Teacher 的复杂模式
2. **蒸馏 = 简单 Fine-tune**: 忽略温度、损失权重、数据多样性等关键超参数
3. **只用 Teacher 输出**: 最佳实践是混合真实数据和 Teacher 合成数据
4. **忽略评估偏差**: Student 可能在基准上接近 Teacher，但在 edge case 上明显退化

## 与相邻概念关联

- **前置**: LLM 预训练、Fine-tuning — 理解模型训练基础
- **互补**: 量化 — 蒸馏减参数量，量化减位宽，可叠加使用
- **关联**: LoRA/PEFT — 低成本 fine-tune Student 模型的方法
- **下游**: LLM Serving — 蒸馏后的小模型更适合高效部署
- **关联**: LLM Benchmarks — 评估蒸馏效果的标准工具
