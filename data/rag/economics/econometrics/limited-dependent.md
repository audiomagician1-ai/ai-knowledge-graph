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
quality_tier: "B"
quality_score: 47.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
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

有限因变量模型（Limited Dependent Variable Models）专门处理因变量取值受到限制的回归问题。最典型的情况是因变量只能取0或1两个离散值，例如消费者是否购买某商品、个人是否参与劳动力市场、申请贷款是否获批——这类二元结果无法用普通最小二乘法（OLS）建模，因为OLS预测值可能超出[0,1]区间，且会产生异方差问题。

"有限"一词指因变量的取值空间受到约束，区别于无限制的连续变量。这一领域的奠基性工作包括：Berkson（1944年）将Logit函数引入生物剂量反应分析，Finney（1947年）系统化Probit模型的应用，而Daniel McFadden因发展离散选择理论荣获2000年诺贝尔经济学奖。

有限因变量模型在政策评估、消费行为研究和劳动经济学中不可或缺。若强行用OLS拟合二元因变量（称为线性概率模型，LPM），理论上预测的购买概率可能为1.3或−0.2，完全失去经济意义。有限因变量模型通过引入连接函数，将线性预测值映射到合法的概率区间，从根本上解决这一问题。

## 核心原理

### 潜变量框架

Logit和Probit模型均建立在**潜变量（Latent Variable）**思想之上。设存在一个无法直接观测的连续变量 $y^*$，满足：

$$y^* = \mathbf{x}'\boldsymbol{\beta} + \varepsilon$$

观测到的二元变量 $y$ 由阈值规则决定：

$$y = \begin{cases} 1 & \text{若 } y^* > 0 \\ 0 & \text{若 } y^* \leq 0 \end{cases}$$

因此，$P(y=1|\mathbf{x}) = P(\varepsilon > -\mathbf{x}'\boldsymbol{\beta}) = F(\mathbf{x}'\boldsymbol{\beta})$，其中 $F(\cdot)$ 是误差项 $\varepsilon$ 的累积分布函数（CDF）。这一框架将模型选择问题转化为对误差项分布的假设问题。

### Logit模型：逻辑分布假设

Logit模型假设 $\varepsilon$ 服从标准Logistic分布，其CDF为：

$$P(y=1|\mathbf{x}) = \Lambda(\mathbf{x}'\boldsymbol{\beta}) = \frac{e^{\mathbf{x}'\boldsymbol{\beta}}}{1 + e^{\mathbf{x}'\boldsymbol{\beta}}} = \frac{1}{1+e^{-\mathbf{x}'\boldsymbol{\beta}}}$$

Logistic分布的方差固定为 $\pi^2/3 \approx 3.29$。Logit模型有一个独特优势：**胜算比（Odds Ratio）**具有直观解释。定义胜算（Odds）为 $P/(1-P)$，则对数胜算（Log-Odds）为：

$$\ln\left(\frac{P}{1-P}\right) = \mathbf{x}'\boldsymbol{\beta}$$

这意味着某连续自变量 $x_k$ 增加1单位，对数胜算线性增加 $\beta_k$，胜算乘以 $e^{\beta_k}$。这一性质使Logit系数在医学和经济学中广泛以"胜算比"形式报告。

### Probit模型：正态分布假设

Probit模型假设 $\varepsilon \sim N(0,1)$（标准正态，方差为1），故：

$$P(y=1|\mathbf{x}) = \Phi(\mathbf{x}'\boldsymbol{\beta}) = \int_{-\infty}^{\mathbf{x}'\boldsymbol{\beta}} \frac{1}{\sqrt{2\pi}} e^{-t^2/2} \, dt$$

其中 $\Phi(\cdot)$ 是标准正态CDF。由于正态分布无闭合形式CDF，Probit模型的概率计算依赖数值积分。Logistic分布尾部比正态分布稍厚，但两者形状高度相似——经验法则是**Logit系数约等于Probit系数的1.6至1.8倍**（$\pi/\sqrt{3} \approx 1.814$），这正是两个分布标准差之比。

### 最大似然估计与边际效应

两个模型均通过最大似然估计（MLE）求参数，对数似然函数为：

$$\ell(\boldsymbol{\beta}) = \sum_{i=1}^{n} \left[ y_i \ln F(\mathbf{x}_i'\boldsymbol{\beta}) + (1-y_i)\ln(1 - F(\mathbf{x}_i'\boldsymbol{\beta})) \right]$$

**关键注意**：Logit/Probit的系数 $\beta_k$ 本身不等于边际效应。连续变量 $x_k$ 对概率的偏效应为：

$$\frac{\partial P(y=1|\mathbf{x})}{\partial x_k} = f(\mathbf{x}'\boldsymbol{\beta}) \cdot \beta_k$$

其中 $f(\cdot)$ 是对应分布的概率密度函数（PDF）。由于 $f(\cdot)$ 随 $\mathbf{x}$ 变化，边际效应在每个观测点不同，实践中通常报告**平均边际效应（Average Marginal Effect, AME）**，即对所有样本点边际效应取平均值。

## 实际应用

**劳动参与率研究**：Mroz（1987年）用Probit模型分析美国已婚女性是否参与劳动力市场，样本包含753名女性，结果发现丈夫收入的边际效应为−0.0034，即丈夫收入增加1000美元，妻子参与劳动的概率下降约0.34个百分点，体现收入效应。

**信用违约预测**：银行用Logit模型预测贷款违约概率。以借款人收入、负债率、信用历史为自变量，输出值直接作为违约概率估计，并设定如0.5为决策阈值。Logit系数可转化为胜算比，便于向非技术决策者解释，例如"负债率每提高10%，违约胜算增加1.8倍"。

**离散选择模型扩展**：McFadden的条件Logit模型（Conditional Logit）将二元选择扩展到多选项情形，用于分析交通方式选择（汽车、公交、地铁）。该模型引入独立不相关选项（IIA）假设，即任意两种交通方式之间的选择概率之比与其他方式无关——这是一个有时不合实际的强假设，后续嵌套Logit模型正是为放松此假设而发展出来的。

## 常见误区

**误区一：直接用OLS估计二元因变量（线性概率模型）**  
线性概率模型（LPM）将 $y=0/1$ 直接对自变量回归，虽系数可解释为概率边际效应，但预测值不受[0,1]约束，且误差项 $\varepsilon = y - \mathbf{x}'\boldsymbol{\beta}$ 只能取两个值，必然异方差。在大样本、自变量远离均值的情形下预测效果尤差。Logit/Probit正是解决这一问题的专门工具。

**误区二：把Logit/Probit系数直接当边际效应**  
许多初学者看到 $\hat{\beta}_k = 0.5$，便认为 $x_k$ 增加1单位，概率增加0.5。这是错误的。系数0.5仅表示线性预测指数 $\mathbf{x}'\boldsymbol{\beta}$ 变化0.5，真实概率变化须乘以当前点的PDF值 $f(\mathbf{x}'\boldsymbol{\beta})$。正态/Logistic PDF在中心处约为0.4/0.25，因此真实边际效应远小于系数值。

**误区三：混淆Logit与Probit的适用场景**  
Logit因能给出胜算比、计算更快而在经济学实证中更常用；Probit因基于正态分布、与多方程联立模型兼容性更好（如Heckman选择模型）而在特定场合更优。两者在大多数情况下预测结果高度相似，但若关心系数的结构解释（如潜变量的正态性假定），则需选择Probit。

## 知识关联

有限因变量模型的估计完全依赖**最大似然估计（MLE）**：其对数似然函数对 $\boldsymbol{\beta}$ 不存在闭合解，必须用牛顿-拉夫森（Newton-Raphson）或BFGS算法迭代求解。MLE的大样本性质（一致性、渐近正态性）直接保证了Logit/Probit估计量的统计推断有效性，系数的标准误基于信息矩阵的逆矩阵计算。

在后续扩展方向上，二元Logit/Probit向多值方向延伸为多项Logit（Multinomial Logit）、有序Probit（Ordered Probit，用于有序评级如债券评级AAA/AA/A）；向截断和审查数据延伸为Tobit模型（处理因变量在某阈值以下全部记为0的情形，如消费支出数据中大量零值观测）；与样本选择问题结合则发展为Heckman两步估计法。这些模型均共享"潜变量+误差分布假设+MLE"的核心框架，掌握