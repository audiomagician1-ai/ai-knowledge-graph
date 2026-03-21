---
id: "expectation-variance"
concept: "期望与方差"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 42.4
generation_method: "ai-batch-v1"
unique_content_ratio: 0.75
last_scored: "2026-03-21"
sources: []
---
# 期望与方差

## 概述

期望与方差是概率论领域中的里程碑概念，难度等级为 6/9。

E(X)和Var(X)的计算与性质

## 核心内容

**数学期望**(均值)：
- 离散：$E(X) = \sum_i x_i P(X = x_i)$
- 连续：$E(X) = \int_{-\infty}^{\infty} x f(x)\,dx$

**方差**: 衡量随机变量偏离均值的程度：
$$\text{Var}(X) = E[(X - \mu)^2] = E(X^2) - [E(X)]^2$$

**性质**：
- $E(aX + b) = aE(X) + b$
- $\text{Var}(aX + b) = a^2\text{Var}(X)$

## 例题与练习

**例**: 掷骰子 $X \in \{1,2,3,4,5,6\}$，各 $P = \frac{1}{6}$

$E(X) = 3.5$，$\text{Var}(X) = \frac{35}{12} \approx 2.917$

## 关联知识

- **先修概念**: 离散分布、连续分布
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 大数定律、矩母函数、切比雪夫不等式、条件期望、描述性统计
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(离散分布、连续分布)，然后系统学习期望与方差的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(6/9)，预计需要 18-30 小时
