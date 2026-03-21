---
id: "hypothesis-testing"
concept: "假设检验"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 7
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 44.8
generation_method: "ai-batch-v1"
unique_content_ratio: 0.8
last_scored: "2026-03-21"
sources: []
---
# 假设检验

## 概述

假设检验是数理统计领域中的里程碑概念，难度等级为 7/9。

原假设/备择假设、p值、I/II类错误

## 核心内容

**假设检验**基本框架：

1. 建立假设：$H_0$(原假设) vs $H_1$(备择假设)
2. 选择检验统计量和显著性水平 $\alpha$(通常 $0.05$ 或 $0.01$)
3. 计算检验统计量的值和 $p$ 值
4. 决策：$p < \alpha$ 则拒绝 $H_0$

**两类错误**：
- I 类错误($\alpha$)：$H_0$ 为真时拒绝 $H_0$
- II 类错误($\beta$)：$H_0$ 为假时未拒绝 $H_0$
- 检验功效 = $1 - \beta$

## 例题与练习

**例**: 检验总体均值是否为 $\mu_0$

$H_0: \mu = \mu_0$ vs $H_1: \mu \neq \mu_0$

$Z = \frac{\bar{X} - \mu_0}{\sigma/\sqrt{n}}$，若 $|Z| > z_{\alpha/2}$ 则拒绝 $H_0$

## 关联知识

- **先修概念**: 置信区间
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: t检验、卡方检验、方差分析、非参数检验
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(置信区间)，然后系统学习假设检验的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(7/9)，预计需要 21-35 小时
