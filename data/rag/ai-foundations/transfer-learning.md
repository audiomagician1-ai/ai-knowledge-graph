---
id: "transfer-learning"
concept: "迁移学习"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["AI", "实践"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 64.6
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 迁移学习

## 核心概念

迁移学习（Transfer Learning）是将在一个任务（源任务）上学到的知识应用到另一个相关任务（目标任务）上的方法。核心思想：不从零开始训练，而是复用已有模型的知识。

## 为什么有效

深度神经网络的浅层学习通用特征（如边缘、纹理、语法结构），深层学习任务特定特征。浅层特征在不同任务间高度可迁移。

```
Layer 1: 通用特征 (边缘/纹理)     ← 高度可迁移
Layer 2: 中级特征 (形状/模式)     ← 中等可迁移
Layer 3: 高级特征 (物体部件)      ← 部分可迁移
Layer 4: 任务特定 (分类/检测)     ← 通常需要重训练
```

## 迁移策略

### 1. 特征提取（Feature Extraction）
冻结预训练模型的所有层，只训练新的分类头：
- 适用场景：目标数据很少
- 计算成本低
- 风险：可能欠拟合

### 2. 微调（Fine-tuning）
冻结预训练模型的浅层，解冻和训练深层+分类头：
- 适用场景：目标数据中等
- 需要更小的学习率（防止破坏预训练知识）
- 风险：过拟合

### 3. 全量微调（Full Fine-tuning）
所有层都参与训练：
- 适用场景：目标数据充足
- 效果最好但计算成本最高
- LLM fine-tuning属于此类

## 在NLP/LLM中的应用

迁移学习彻底改变了NLP领域：

1. **预训练语言模型**: GPT、BERT在大规模语料上预训练
2. **下游任务微调**: 在特定任务数据上fine-tune
3. **Prompt-based**: 不微调模型，通过prompt引导
4. **LoRA/QLoRA**: 参数高效微调（只训练少量额外参数）

演进路线：
```
Word2Vec(2013) → ELMo(2018) → BERT(2018) → GPT-3(2020) → ChatGPT(2022)
   词向量迁移      上下文迁移      深度微调      少样本/零样本学习
```

## 迁移学习的条件

迁移有效的前提：
- **领域相关性**: 源任务和目标任务有相关性
- **数据质量**: 源任务的训练数据质量要好
- **模型适配**: 模型架构适合目标任务

负迁移：当源和目标差异太大时，迁移反而降低性能。

## 与深度学习的关系

迁移学习的成功很大程度上依赖于深度学习——深度网络的层次化特征学习天然支持知识迁移。理解深度网络的训练和表征学习是理解迁移学习的基础。
