---
id: "linear-regression"
concept: "线性回归"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 43.8
generation_method: "ai-batch-v1"
unique_content_ratio: 0.714
last_scored: "2026-03-21"
sources: []
---
# 线性回归

## 概述

线性回归是数理统计领域中的里程碑概念，难度等级为 6/9。

一元/多元线性回归、R²

## 核心内容

**线性回归**模型：$Y = \beta_0 + \beta_1 X + \varepsilon$，其中 $\varepsilon \sim N(0, \sigma^2)$。

**最小二乘估计**: 最小化残差平方和
$$\min_{\beta_0, \beta_1} \sum_{i=1}^n (y_i - \beta_0 - \beta_1 x_i)^2$$

**解**：
$$\hat{\beta}_1 = \frac{\sum(x_i - \bar{x})(y_i - \bar{y})}{\sum(x_i - \bar{x})^2}$$
$$\hat{\beta}_0 = \bar{y} - \hat{\beta}_1\bar{x}$$

**$R^2$ 决定系数**: $R^2 = 1 - \frac{SS_{res}}{SS_{tot}}$，衡量模型解释的方差比例。

## 例题与练习

**例**: 数据 $(1,2), (2,4), (3,5), (4,4), (5,5)$

$\bar{x}=3, \bar{y}=4, \hat{\beta}_1 = 0.7, \hat{\beta}_0 = 1.9$

## 关联知识

- **先修概念**: 最小二乘法、相关性分析
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 逻辑回归
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(最小二乘法、相关性分析)，然后系统学习线性回归的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(6/9)，预计需要 18-30 小时
