---
id: "central-limit-theorem"
concept: "中心极限定理"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 48.2
generation_method: "ai-batch-v1"
unique_content_ratio: 0.786
last_scored: "2026-03-21"
sources: []
---
# 中心极限定理

## 概述

中心极限定理是概率论领域中的里程碑概念，难度等级为 7/9。

独立同分布的和趋向正态

## 核心内容

**中心极限定理**(CLT): 设 $X_1, X_2, \ldots, X_n$ 独立同分布，$E(X_i) = \mu$，$\text{Var}(X_i) = \sigma^2$，则
$$\frac{\bar{X}_n - \mu}{\sigma/\sqrt{n}} \xrightarrow{d} N(0,1) \quad (n \to \infty)$$

或等价地：$\bar{X}_n \approx N(\mu, \sigma^2/n)$。

**意义**: 无论原始分布形状如何，样本均值的分布在样本量足够大时趋向正态分布。这是统计推断的理论基础。

## 例题与练习

**例**: 某工厂产品重量 $\mu=500g$, $\sigma=10g$

抽 $n=100$ 件样本：$\bar{X} \sim N(500, 1)$

$P(498 < \bar{X} < 502) = P(-2 < Z < 2) \approx 0.9544$

## 关联知识

- **先修概念**: 正态分布、大数定律
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 抽样分布
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(正态分布、大数定律)，然后系统学习中心极限定理的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(7/9)，预计需要 21-35 小时
