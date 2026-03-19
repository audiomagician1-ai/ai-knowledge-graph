---
id: "definite-integrals"
name: "定积分"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: true
tags: ["里程碑"]
generated_at: "2026-03-19T08:00:26"
---

# 定积分

## 概述

定积分是微积分领域中的里程碑概念，难度等级为 6/9。

Riemann和与定积分的定义

## 核心内容

**定积分**的 Riemann 定义：将区间 $[a,b]$ 分成 $n$ 等份，取样本点求和：
$$\int_a^b f(x)\,dx = \lim_{n \to \infty} \sum_{i=1}^n f(x_i^*) \Delta x$$

其中 $\Delta x = \frac{b-a}{n}$。

**几何意义**: $\int_a^b f(x)\,dx$ 等于曲线 $y = f(x)$ 与 $x$ 轴在 $[a,b]$ 上围成的有向面积。

**基本性质**：
- 线性：$\int_a^b [\alpha f + \beta g]\,dx = \alpha\int_a^b f\,dx + \beta\int_a^b g\,dx$
- 区间可加：$\int_a^c f\,dx = \int_a^b f\,dx + \int_b^c f\,dx$

## 例题与练习

**例**: $\int_0^1 x^2\,dx = \left[\frac{x^3}{3}\right]_0^1 = \frac{1}{3}$

## 关联知识

- **先修概念**: 不定积分
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 微积分基本定理、曲线围面积、旋转体体积、弧长公式、广义积分
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(不定积分)，然后系统学习定积分的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(6/9)，预计需要 18-30 小时
