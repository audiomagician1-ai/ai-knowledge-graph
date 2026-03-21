---
id: "point-estimation"
concept: "点估计"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 40.5
generation_method: "ai-batch-v1"
unique_content_ratio: 0.714
last_scored: "2026-03-21"
sources: []
---
# 点估计

## 概述

点估计是数理统计领域中的里程碑概念，难度等级为 6/9。

矩估计法、最大似然估计

## 核心内容

**点估计**: 用样本统计量估计总体参数。

**矩估计法**: 令样本矩 = 总体矩，解方程得到参数估计。

**最大似然估计**(MLE): 选择使似然函数最大的参数值：
$$\hat{\theta}_{MLE} = \arg\max_\theta \prod_{i=1}^n f(x_i; \theta)$$

实际操作中常用对数似然：$\ell(\theta) = \sum_{i=1}^n \ln f(x_i; \theta)$

## 例题与练习

**例**: 正态分布 $N(\mu, \sigma^2)$ 的 MLE

$\hat{\mu} = \bar{X} = \frac{1}{n}\sum x_i$，$\hat{\sigma}^2 = \frac{1}{n}\sum (x_i - \bar{X})^2$

## 关联知识

- **先修概念**: 抽样分布
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 贝叶斯统计、充分统计量、最大似然估计详解
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(抽样分布)，然后系统学习点估计的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(6/9)，预计需要 18-30 小时
