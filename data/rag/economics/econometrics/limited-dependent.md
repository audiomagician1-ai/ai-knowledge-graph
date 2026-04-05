---
id: "limited-dependent"
concept: "有限因变量模型"
domain: "economics"
subdomain: "econometrics"
subdomain_name: "计量经济学"
difficulty: 3
is_milestone: false
tags: ["模型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 有限因变量模型

## 概述

有限因变量模型（Limited Dependent Variable Models）是处理因变量取值受到限制或离散化情形的计量经济学方法族群。与普通最小二乘法（OLS）假设因变量可在实数轴上连续取值不同，有限因变量模型专门针对因变量只能取0或1、只能取非负整数、或被截断在某个范围内的数据结构。该方法族由Tobin（1958年）、McFadden（1974年）等经济学家系统发展，McFadden因离散选择分析贡献于2000年获得诺贝尔经济学奖。

有限因变量模型在经济学中的必要性源于现实决策的离散性。消费者是否购买房屋（是/否）、求职者是否找到工作（是/否）、家庭收入能否超越贫困线——这些结果无法用线性概率模型准确刻画，因为OLS预测值可能超出[0,1]区间，违背概率的基本定义。将连续因变量模型强行应用于0-1因变量会导致异方差和不一致估计量。

本文聚焦两种最主要的二元选择模型：Logit模型和Probit模型，并延伸至多元离散选择框架，如多项Logit（Multinomial Logit）和条件Logit（Conditional Logit）。

---

## 核心原理

### 潜变量框架与二元响应

Logit与Probit模型共享同一个潜变量（latent variable）理论基础。假设存在不可观测的连续潜变量 $y^*$，满足：

$$y^* = \mathbf{x}'\boldsymbol{\beta} + \varepsilon$$

观测到的二元因变量 $y$ 由以下规则生成：

$$y = \begin{cases} 1 & \text{若 } y^* > 0 \\ 0 & \text{若 } y^* \leq 0 \end{cases}$$

因此，$P(y=1|\mathbf{x}) = P(\varepsilon > -\mathbf{x}'\boldsymbol{\beta}) = F(\mathbf{x}'\boldsymbol{\beta})$，其中 $F(\cdot)$ 是误差项 $\varepsilon$ 的累积分布函数（CDF）。Logit模型假设 $\varepsilon$ 服从标准逻辑分布（方差为 $\pi^2/3$），Probit模型假设 $\varepsilon$ 服从标准正态分布 $N(0,1)$。

### Logit模型：逻辑函数的形式

Logit模型中，$F(\cdot)$ 为逻辑函数：

$$P(y=1|\mathbf{x}) = \Lambda(\mathbf{x}'\boldsymbol{\beta}) = \frac{e^{\mathbf{x}'\boldsymbol{\beta}}}{1 + e^{\mathbf{x}'\boldsymbol{\beta}}} = \frac{1}{1+e^{-\mathbf{x}'\boldsymbol{\beta}}}$$

Logit模型的一个独特性质是其系数可以通过**胜率比（Odds Ratio）**直接解读：$\text{Odds} = P/(1-P) = e^{\mathbf{x}'\boldsymbol{\beta}}$，因此 $\log[\text{Odds}] = \mathbf{x}'\boldsymbol{\beta}$，某解释变量 $x_k$ 增加1单位，对数胜率线性增加 $\beta_k$，而胜率本身乘以 $e^{\beta_k}$。这一解读方式与Probit模型不同，是Logit模型在医学和流行病学中更为流行的原因之一。

### Probit模型：正态分布的形式

Probit模型中：

$$P(y=1|\mathbf{x}) = \Phi(\mathbf{x}'\boldsymbol{\beta}) = \int_{-\infty}^{\mathbf{x}'\boldsymbol{\beta}} \frac{1}{\sqrt{2\pi}} e^{-t^2/2} \, dt$$

Probit的系数 $\beta_k$ 本身不直接具备概率含义，需要计算**边际效应（Marginal Effect）**：

$$\frac{\partial P(y=1|\mathbf{x})}{\partial x_k} = \phi(\mathbf{x}'\boldsymbol{\beta}) \cdot \beta_k$$

其中 $\phi(\cdot)$ 是标准正态密度函数。由于 $\phi$ 依赖于 $\mathbf{x}$ 的取值，边际效应不是常数，通常计算**样本均值处的边际效应（MEM）**或**平均边际效应（AME）**。Logit模型同理，边际效应为 $\Lambda(\mathbf{x}'\boldsymbol{\beta})[1-\Lambda(\mathbf{x}'\boldsymbol{\beta})] \cdot \beta_k$。

### 最大似然估计与模型检验

两种模型均通过最大似然估计（MLE）求解，无封闭解，需用数值优化方法（如Newton-Raphson迭代）。对数似然函数为：

$$\ln L(\boldsymbol{\beta}) = \sum_{i=1}^{n} \left[ y_i \ln F(\mathbf{x}_i'\boldsymbol{\beta}) + (1-y_i) \ln(1-F(\mathbf{x}_i'\boldsymbol{\beta})) \right]$$

模型拟合优度常用**McFadden伪R²**：$\tilde{R}^2 = 1 - \ln\hat{L}/\ln\hat{L}_0$，其中 $\ln\hat{L}_0$ 是仅含截距的模型对数似然值。$\tilde{R}^2$ 介于0和1之间，但通常远小于OLS中的 $R^2$，取值0.2~0.4即被认为拟合良好。变量联合显著性检验使用**似然比检验（LR test）**：$LR = -2(\ln\hat{L}_{\text{restricted}} - \ln\hat{L}_{\text{unrestricted}}) \sim \chi^2(q)$，其中 $q$ 为限制条件数量。

### 多项Logit与IIA假设

当因变量有三个或更多无序类别时，使用**多项Logit模型（MNL）**。McFadden（1974）推导出：

$$P(y=j|\mathbf{x}) = \frac{e^{\mathbf{x}'\boldsymbol{\beta}_j}}{\sum_{k=0}^{J} e^{\mathbf{x}'\boldsymbol{\beta}_k}}$$

MNL有一个关键且严格的假设：**无关选项的独立性（Independence of Irrelevant Alternatives, IIA）**。IIA指任意两个选项之间的概率比与第三个选项无关。经典反例是"红色公交-蓝色公交-小汽车"问题：若去掉蓝色公交，红色公交概率不应该恰好翻倍，但MNL预测它会。可用**Hausman-McFadden检验**或**Small-Hsiao检验**来检验IIA是否成立。

---

## 实际应用

**劳动力参与决策**：Mroz（1987）用Probit模型估计已婚女性劳动力参与率，以教育年限、子女数、丈夫收入为解释变量。结果显示，丈夫工资每增加1000美元，女性参与劳动市场的概率下降约1.8个百分点（在均值处的边际效应）。

**交通工具选择**：McFadden（1974）研究旧金山BART（湾区快速交通系统）的引入对通勤方式选择的影响，用条件Logit模型（Conditional Logit）将选项特征（票价、时间）与个体特征同时纳入，开创了离散选择分析在交通经济学中的应用范式。

**信用违约预测**：银行业广泛使用Logit模型预测贷款违约概率，模型输出直接作为违约概率 $P(\text{default}=1|\mathbf{x})$，并设定概率阈值（如0.5）进行信用评级分类。

---

## 常见误区

**误区一：将Logit/Probit系数大小直接比较**。由于Logit误差项方差为 $\pi^2/3 \approx 3.29$，而Probit方差为1，两者系数不可直接比大小。换算关系近似为 $\hat{\beta}_{\text{Logit}} \approx 1.6 \times \hat{\beta}_{\text{Probit}}$，比较应基于边际效应而非原始系数。

**误区二：以为边际效应是常数**。许多学习者错误地将 $\beta_k$ 直接解读为"$x_k$ 增加1单位，概率增加 $\beta_k$"。这仅在线性概率模型（LPM）中成立。在Logit/Probit中，边际效应随 $\mathbf{x}$ 的取值变化而变化——在概率接近0或1时边际效应趋近于0，在概率接近0.5时边际效应最大。

**误区三：忽视完全分离（Perfect Separation）问题**。当某个解释变量能完美区分 $y=0$ 和 $y=1$ 时，MLE估计量发散至无穷大，标准误爆炸，模型不收敛。这在样本量小或变量与结果高度相关时频繁发生，OLS则不会出现此问题。解决方法包括Firth惩罚似然或贝叶斯Logit。

---

## 知识关联

**前置概念——最大似然估计**：Logit和Probit的参数求解完全依赖MLE原理。对数似然函数的构造、评分函数（Score Function）的一阶条件、信息矩阵（Fisher Information）与标准误的计算，都是MLE理论的直接