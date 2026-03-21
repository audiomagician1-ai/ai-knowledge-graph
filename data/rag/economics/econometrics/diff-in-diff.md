---
id: "diff-in-diff"
concept: "双重差分法"
domain: "economics"
subdomain: "econometrics"
subdomain_name: "计量经济学"
difficulty: 3
is_milestone: false
tags: ["因果"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "C"
quality_score: 13.0
generation_method: "template-v1"
unique_content_ratio: 0.091
last_scored: "2026-03-21"
sources: []
---
# 双重差分法

## 核心内容

DID设计、平行趋势假设与政策效果评估

计量经济学将统计学方法应用于经济数据分析。回归分析、因果推断和时间序列是现代经济学实证研究的核心工具。

## 关键要点

### 核心方法
- **回归分析**: OLS（最小二乘法）估计变量间的线性关系
- **因果推断**: 工具变量、双重差分、断点回归识别因果效应
- **面板数据**: 结合截面和时间维度，控制不可观测的个体异质性

### 方法论挑战
- 内生性：遗漏变量、反向因果、测量误差导致估计偏误
- 异方差和自相关：违反OLS经典假设需要修正
- 大数据时代：机器学习方法进入经济学（LASSO、随机森林）

## 常见误区

1. **相关=因果**: 没有适当的识别策略，回归系数不能解释为因果效应
2. **显著=重要**: 统计显著性不等于经济显著性，需关注效应大小
3. **更多控制变量更好**: 过度控制可能引入坏控制变量偏误

## 与相关概念的联系

双重差分法是计量经济学知识体系的重要组成部分。掌握这一概念有助于进行严谨的经济学实证研究。
