---
id: "continual-pretraining"
concept: "持续预训练"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM", "训练"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 73.5
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
﻿# 持续预训练

## 概述
持续预训练(Continual Pre-training / Domain-Adaptive Pre-training)是在已有基座模型上使用特定领域语料继续预训练的技术, 使模型获得领域专业知识而不完全遗忘通用能力。

## 核心概念

### 与微调的区别
| 特征 | 持续预训练 | 微调(Fine-tuning) |
|------|----------|------------------|
| 数据量 | 大(GB~TB) | 小(MB~GB) |
| 目标 | 注入领域知识 | 学习特定任务格式 |
| 训练方式 | 自回归/MLM | 指令跟随 |
| 学习率 | 较高 | 较低 |

### 灾难性遗忘
- 模型在学习新知识时倾向于遗忘旧知识
- 缓解策略: 混合通用数据(5-20%)、弹性权重巩固(EWC)、渐进式学习率

### 数据准备
1. **领域语料收集**: 教材/论文/文档/代码
2. **数据清洗**: 去重、过滤低质量内容
3. **分词器适配**: 必要时扩展tokenizer词表
4. **数据配比**: 领域数据与通用数据的混合比例

### 训练策略
- **学习率调度**: 较小的peak lr(基座模型lr的10-50%)
- **Warmup**: 长warmup防止早期知识破坏
- **混合训练**: 交替领域数据和通用数据
- **课程学习**: 从易到难的数据组织

## 典型应用
- 医学LLM(PubMed语料)
- 法律LLM(法律文书/判例)
- 金融LLM(财报/研报)
- 代码LLM(GitHub代码库)

## 评估
- 领域知识测试(领域QA基准)
- 通用能力保持测试(MMLU等通用基准)
- 困惑度(Perplexity)变化追踪
