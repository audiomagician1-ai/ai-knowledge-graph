---
id: "endogeneity"
concept: "内生性问题"
domain: "economics"
subdomain: "econometrics"
subdomain_name: "计量经济学"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.364
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 内生性问题

## 概述

内生性问题（Endogeneity）是指计量经济模型中解释变量与误差项之间存在相关性，导致OLS估计量产生系统性偏误、不再具有一致性的现象。数学上，当 $\text{Cov}(X_i, \varepsilon_i) \neq 0$ 时，即可判定存在内生性。这一条件违反了OLS无偏一致估计的核心假设，使得回归系数 $\hat{\beta}$ 无法收敛到真实参数 $\beta$，无论样本量增加到多大，偏误都不会消失。

内生性问题在1943年由经济学家Tjalling Koopmans在研究供求联立方程组时首次被系统讨论，他指出价格与产量互相决定，使得单方程OLS估计天然失效。此后，这一问题成为计量经济学中最重要的识别挑战，直接推动了工具变量法、两阶段最小二乘法（2SLS）等一系列解决方案的发展。

内生性问题的实质危害在于方向不确定：根据 $\text{plim}(\hat{\beta}) = \beta + \frac{\text{Cov}(X, \varepsilon)}{\text{Var}(X)}$，估计偏误的方向取决于 $X$ 与 $\varepsilon$ 协方差的符号，可能使真实正效应看起来为负，或将零效应夸大为显著正效应，从而导致政策判断的根本性错误。

## 核心原理

### 遗漏变量偏误（Omitted Variable Bias）

遗漏变量偏误是内生性最常见的来源。当真实模型为 $Y = \beta_0 + \beta_1 X + \beta_2 Z + \varepsilon$，但研究者遗漏了变量 $Z$，此时若 $Z$ 同时与 $X$ 相关且影响 $Y$，则OLS对 $\beta_1$ 的估计偏误公式为：

$$\text{Bias}(\hat{\beta}_1) = \beta_2 \cdot \frac{\text{Cov}(X, Z)}{\text{Var}(X)}$$

经典案例是教育回报率研究：若不控制个人能力（ability），则教育年限的系数会吸收部分能力溢价，导致教育回报率被高估。Card（1995）使用距离大学远近作为工具变量，估计出的教育回报率反而高于OLS结果，显示OLS受到了能力负向选择效应的向下偏误。

### 测量误差（Measurement Error）

当解释变量 $X^*$ 无法精确观测，只能观测到含误差版本 $X = X^* + \eta$（其中 $\eta$ 为测量误差），若 $\eta$ 与真实值独立（经典测量误差假设），则OLS系数会向零偏移，称为**衰减偏误（Attenuation Bias）**。衰减因子为：

$$\text{plim}(\hat{\beta}) = \beta \cdot \frac{\text{Var}(X^*)}{\text{Var}(X^*) + \text{Var}(\eta)}$$

由于 $\text{Var}(\eta) > 0$，衰减因子必然小于1，意味着测量误差总是使系数绝对值偏小。在劳动经济学中，用回忆数据测量工资或工作经验时，测量误差普遍存在，会低估工资方程中经验的边际回报。

### 联立性偏误（Simultaneity Bias）

联立性偏误源于 $Y$ 与 $X$ 互为因果。最典型的例子是供需方程：价格 $P$ 决定需求量 $Q$，但需求量同样通过市场均衡机制影响价格，二者由以下联立方程组共同确定：

$$Q^d = \alpha_0 + \alpha_1 P + u_1, \quad Q^s = \gamma_0 + \gamma_1 P + u_2, \quad Q^d = Q^s$$

从均衡条件解出 $P = \frac{\alpha_0 - \gamma_0 + u_1 - u_2}{\gamma_1 - \alpha_1}$，可见 $P$ 与需求方程误差项 $u_1$ 不可避免地相关，单方程OLS估计需求弹性将产生偏误。Haavelmo（1943）因系统性分析联立性偏误而获1989年诺贝尔经济学奖。

## 实际应用

**警察数量与犯罪率**：Levitt（1997）在《美国经济评论》研究中指出，警察数量越多的城市犯罪率也越高，但这并非警察增加了犯罪——而是犯罪率高的城市招募了更多警察，存在反向因果（联立性偏误）。他使用市长和州长选举年作为工具变量，解决内生性后发现警察增加显著降低犯罪率，弹性约为 -0.3 至 -0.5。

**教育与收入**：直接用受教育年限对收入回归时，能力、家庭背景等遗漏变量同时影响二者，OLS估计的教育回报率介于6%-13%，偏误方向与大小均不确定。Angrist和Krueger（1991）利用出生季度作为工具变量（因义务教育入学年龄规定，不同出生季度者辍学年龄时积累的受教育年限不同），剥离遗漏变量干扰，这一研究成为工具变量法的标志性应用。

**医疗支出与健康**：更健康的人医疗支出反而更少（反向因果），直接回归会错误估计医疗支出对健康的效果，需要利用随机医疗保险分配（如RAND健康保险实验）来消除内生性。

## 常见误区

**误区一：控制更多变量就能消除内生性**。部分研究者认为在回归中加入足够多的控制变量就能解决问题，但若关键遗漏变量无法观测（如能力、偏好），增加可观测控制变量并不能解决 $\text{Cov}(X, \varepsilon) \neq 0$ 的根本问题。固定效应模型能控制不随时间变化的不可观测个体特征，但无法处理随时间变化的不可观测因素。

**误区二：内生性问题只影响显著性，不影响方向**。实际上，根据偏误公式 $\beta_2 \cdot \frac{\text{Cov}(X,Z)}{\text{Var}(X)}$，当遗漏变量 $Z$ 与 $X$ 负相关但正向影响 $Y$ 时（$\beta_2 > 0, \text{Cov}(X,Z) < 0$），OLS估计值会低于真实值，甚至可能从正值变为负值，完全逆转因果方向的判断。

**误区三：Hausman检验通过意味着不存在内生性**。Hausman检验（1978年提出）本质上比较OLS与2SLS的系数差异是否显著，但其功效（power）依赖于工具变量的强度和样本量。弱工具变量情形下，即便存在内生性，Hausman检验也可能无法拒绝零假设，产生假阴性结论。

## 知识关联

内生性问题建立在多元回归的Gauss-Markov假设框架之上——正是对"解释变量与误差项不相关"这一假设的系统违反，才定义了内生性的三种来源。理解OLS偏误公式 $\text{plim}(\hat{\beta}) = \beta + \frac{\text{Cov}(X,\varepsilon)}{\text{Var}(X)}$ 需要掌握概率极限和OLS代数推导。

识别内生性的存在直接引出工具变量法（IV）：一个有效工具变量 $Z$ 必须满足相关性（$\text{Cov}(Z, X) \neq 0$）和外生性（$\text{Cov}(Z, \varepsilon) = 0$）两个条件，本质上是用 $Z$ 中与 $\varepsilon$ 无关的 $X$ 变异来识别因果效应。双重差分法（DID）通过平行趋势假设差分掉时间固定效应，处理的是特定形式的遗漏变量（不随时间变化的组间差异与共同时间趋势）。倾向得分匹配则通过构造可比对照组来控制可观测遗漏变量，但对不可观测遗漏变量无能为力，三种方法分别针对内生性的不同类型和场景。