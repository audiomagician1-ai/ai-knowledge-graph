---
id: "sparse-attention"
concept: "稀疏注意力"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM", "架构"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 57.8
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
﻿# 稀疏注意力

## 概述
稀疏注意力(Sparse Attention)通过限制每个token关注的范围来降低标准注意力O(n²)的计算复杂度, 使模型能处理更长的序列。

## 标准注意力的瓶颈
- 全注意力: 每个token attend所有其他token → O(n²)复杂度
- 128K上下文窗口: 128K × 128K = ~16B次注意力计算
- 显存消耗: KV-cache随序列长度线性增长

## 核心方法

### 固定模式稀疏注意力
1. **局部注意力(Local/Sliding Window)**
   - 每个token只关注周围固定窗口内的token
   - 复杂度: O(n × w), w为窗口大小
   - 代表: Mistral的Sliding Window Attention

2. **扩张注意力(Dilated Attention)**
   - 间隔采样的注意力模式
   - 类似CNN的空洞卷积思想

3. **全局+局部混合(Global + Local)**
   - 少量全局token(如[CLS]) attend所有位置
   - 其余token使用局部注意力
   - 代表: Longformer、BigBird

### 学习型稀疏注意力
- **Reformer**: LSH(局部敏感哈希)找近似最近邻
- **Routing Transformer**: 学习注意力路由策略

### 分层注意力
- **Ring Attention**: 跨设备环形分布长序列
- **Striped Attention**: 条纹模式平衡计算负载

## 代表模型
| 模型 | 方法 | 最大长度 |
|------|------|---------|
| Longformer | Global + Sliding Window | 4K |
| BigBird | Random + Window + Global | 4K |
| Mistral | Sliding Window + GQA | 32K |
| Gemini 1.5 | 多尺度稀疏 | 1M+ |

## 与FlashAttention的关系
- FlashAttention: 不改变注意力模式, 优化IO效率
- 稀疏注意力: 改变注意力模式, 降低计算量
- 可以组合使用
