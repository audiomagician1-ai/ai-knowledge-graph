---
id: "mean-value-theorems"
concept: "中值定理"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 44.3
generation_method: "ai-batch-v1"
unique_content_ratio: 0.769
last_scored: "2026-03-21"
sources: []
---
# 中值定理

## 概述

中值定理是微积分领域中的里程碑概念，难度等级为 7/9。

Rolle定理、Lagrange中值定理、Cauchy中值定理

## 核心内容

**中值定理**是微积分的核心定理族。

**Rolle定理**: 若 $f$ 在 $[a,b]$ 连续、$(a,b)$ 可导、$f(a)=f(b)$，则存在 $\xi \in (a,b)$ 使 $f'(\xi) = 0$。

**Lagrange中值定理**: 若 $f$ 在 $[a,b]$ 连续、$(a,b)$ 可导，则存在 $\xi \in (a,b)$ 使
$$f'(\xi) = \frac{f(b) - f(a)}{b - a}$$

**Cauchy中值定理**: 若 $f, g$ 满足类似条件且 $g'(x) \neq 0$，则
$$\frac{f'(\xi)}{g'(\xi)} = \frac{f(b) - f(a)}{g(b) - g(a)}$$

## 例题与练习

**例**: $f(x) = x^2$ 在 $[1,3]$ 上：$f'(\xi) = \frac{9-1}{3-1} = 4$

$2\xi = 4 \Rightarrow \xi = 2 \in (1,3)$ ✓

## 关联知识

- **先修概念**: 导数概念、连续性
  - 学习本概念前，建议先掌握以上概念

## 学习建议

- **推荐学习路径**: 先回顾先修概念(导数概念、连续性)，然后系统学习中值定理的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(7/9)，预计需要 21-35 小时
