---
id: "ftc"
concept: "微积分基本定理"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
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
# 微积分基本定理

## 概述

微积分基本定理是微积分领域中的里程碑概念，难度等级为 6/9。

Newton-Leibniz公式、FTC I和II

## 核心内容

**微积分基本定理**连接了微分与积分。

**FTC I**(积分上限函数可导): 若 $f$ 在 $[a,b]$ 上连续，令 $F(x) = \int_a^x f(t)\,dt$，则
$$F'(x) = f(x)$$

**FTC II**(Newton-Leibniz公式): 若 $F'(x) = f(x)$，则
$$\int_a^b f(x)\,dx = F(b) - F(a)$$

这意味着求定积分可以通过找原函数来完成，不需要求极限。

## 例题与练习

**例**: 计算 $\int_1^e \frac{1}{x}\,dx$

$\frac{1}{x}$ 的原函数是 $\ln x$

$\int_1^e \frac{1}{x}\,dx = \ln e - \ln 1 = 1 - 0 = 1$

## 关联知识

- **先修概念**: 定积分、导数概念
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 不定积分
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(定积分、导数概念)，然后系统学习微积分基本定理的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(6/9)，预计需要 18-30 小时
