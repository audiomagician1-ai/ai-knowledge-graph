---
id: "llm-watermarking"
concept: "LLM水印技术"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM", "安全"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 70.2
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
﻿# LLM水印技术

## 概述
LLM水印(LLM Watermarking)是在模型生成的文本中嵌入不可见标记的技术, 用于检测和追溯AI生成的内容。

## 核心原理

### 生成时水印(Generation-time Watermarking)
最经典的方案(Kirchenbauer et al., 2023):
1. 根据前文token生成伪随机"绿色列表"
2. 在采样时偏向绿色列表中的token
3. 检测时统计绿色token比例

### 关键参数
- **γ (Green List Ratio)**: 绿色列表占词表比例(通常0.25-0.5)
- **δ (Bias)**: 绿色token的logit偏移量
- **水印强度**: δ越大水印越强, 但文本质量下降越多

## 检测方法
- **Z-test**: 统计绿色token比例是否显著高于随机
- **窗口检测**: 滑动窗口检测部分水印文本
- **无需模型访问**: 检测只需要水印密钥

## 攻击与鲁棒性
### 常见攻击
- **释义攻击**: 用另一个LLM改写文本
- **替换攻击**: 替换部分词汇
- **翻译攻击**: 翻译成其他语言再翻回
- **混合攻击**: 混合水印和非水印文本

### 鲁棒性增强
- 多bit水印编码
- 语义级水印(基于含义而非具体词)
- 对抗训练增强鲁棒性

## 应用场景
- AI生成内容检测(学术/新闻)
- 模型版权保护
- 内容溯源和责任归属

## 局限性
- 短文本检测准确率低
- 不可避免地影响生成质量
- 开源模型无法强制水印
- 理论上可通过足够的改写消除
