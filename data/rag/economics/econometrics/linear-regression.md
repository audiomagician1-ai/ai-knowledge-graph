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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 38.8
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.355
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 线性回归

## 概述

线性回归是计量经济学中用于量化两个或多个变量之间线性关系的统计方法。其最简单的形式——简单线性回归——描述一个因变量（被解释变量）$Y$ 如何随一个自变量（解释变量）$X$ 的变化而线性变动，模型表达式为 $Y_i = \beta_0 + \beta_1 X_i + \varepsilon_i$，其中 $\beta_0$ 为截距，$\beta_1$ 为斜率系数，$\varepsilon_i$ 为随机误差项。

线性回归的理论根基可追溯至19世纪初。卡尔·弗里德里希·高斯（Carl Friedrich Gauss）于1809年首次提出最小二乘法，弗朗西斯·高尔顿（Francis Galton）于1886年在研究父子身高遗传规律时正式引入"回归"一词，发现子代身高会向总体均值"回归"。在经济学领域，线性回归是实证分析的基础工具，无论是估计需求弹性、评估政策效果，还是预测GDP增速，都离不开这一方法。

## 核心原理

### 普通最小二乘估计（OLS）

OLS（Ordinary Least Squares）是线性回归最常用的参数估计方法。其核心思想是寻找一组参数 $\hat{\beta}_0$ 和 $\hat{\beta}_1$，使所有观测点的残差平方和（RSS）最小：

$$\min_{\hat{\beta}_0, \hat{\beta}_1} \sum_{i=1}^{n} \hat{\varepsilon}_i^2 = \sum_{i=1}^{n} (Y_i - \hat{\beta}_0 - \hat{\beta}_1 X_i)^2$$

对上式分别对 $\hat{\beta}_0$ 和 $\hat{\beta}_1$ 求偏导并令其为零，可得OLS估计量的解析解：

$$\hat{\beta}_1 = \frac{\sum_{i=1}^{n}(X_i - \bar{X})(Y_i - \bar{Y})}{\sum_{i=1}^{n}(X_i - \bar{X})^2} = \frac{S_{XY}}{S_{XX}}$$

$$\hat{\beta}_0 = \bar{Y} - \hat{\beta}_1 \bar{X}$$

这说明回归直线必然通过样本均值点 $(\bar{X}, \bar{Y})$，这是OLS估计的一个重要几何性质。

### 高斯-马尔可夫定理与经典假设

OLS估计量的优良性依赖于以下经典线性回归假设（CLRM）：
- **零均值误差**：$E(\varepsilon_i | X_i) = 0$
- **同方差性**：$\text{Var}(\varepsilon_i | X_i) = \sigma^2$（常数）
- **无自相关**：$\text{Cov}(\varepsilon_i, \varepsilon_j) = 0$，$i \neq j$
- **解释变量非随机且无多重共线性**

在满足上述假设的条件下，高斯-马尔可夫定理保证OLS估计量是**BLUE**（Best Linear Unbiased Estimator，最优线性无偏估计量），即在所有线性无偏估计量中方差最小。若进一步假设 $\varepsilon_i \sim N(0, \sigma^2)$，则OLS估计量也具有最小方差无偏性（MVUE）。

### 拟合优度与回归结果解读

**判定系数 $R^2$** 衡量回归方程对因变量变异的解释程度：

$$R^2 = 1 - \frac{RSS}{TSS} = 1 - \frac{\sum \hat{\varepsilon}_i^2}{\sum (Y_i - \bar{Y})^2}$$

$R^2$ 取值范围为 $[0, 1]$，越接近1说明拟合越好。但需注意，在简单线性回归中，$R^2$ 恰好等于 $X$ 与 $Y$ 之间皮尔逊相关系数的平方，即 $R^2 = r_{XY}^2$。

斜率系数 $\hat{\beta}_1$ 的经济解释为：在其他条件不变时，$X$ 每增加一个单位，$Y$ 平均变动 $\hat{\beta}_1$ 个单位。例如，若用收入（万元）回归消费（万元），$\hat{\beta}_1 = 0.75$ 表示边际消费倾向为0.75，即收入每增加1万元，消费平均增加0.75万元。

对于对数线性模型 $\ln Y_i = \beta_0 + \beta_1 \ln X_i + \varepsilon_i$，斜率系数 $\beta_1$ 的解释变为弹性：$X$ 变动1%，$Y$ 平均变动 $\beta_1$%。

### $t$ 检验与回归系数的统计显著性

在正态误差假设下，对 $\beta_1$ 的显著性检验构造 $t$ 统计量：

$$t = \frac{\hat{\beta}_1 - \beta_1^0}{SE(\hat{\beta}_1)} \sim t(n-2)$$

其中 $SE(\hat{\beta}_1) = \sqrt{\hat{\sigma}^2 / S_{XX}}$，$\hat{\sigma}^2 = RSS/(n-2)$ 为残差均方。自由度为 $n-2$ 而非 $n-1$，因为估计截距和斜率各消耗一个自由度。通常检验原假设 $H_0: \beta_1 = 0$（即 $X$ 对 $Y$ 无线性影响），若 $|t| > t_{\alpha/2}(n-2)$，则拒绝原假设，认为系数显著不为零。

## 实际应用

**消费函数估计**：凯恩斯消费理论认为居民消费 $C$ 与可支配收入 $Y_d$ 存在线性关系。使用中国1990—2020年时间序列数据对 $C_t = \beta_0 + \beta_1 Y_{d,t} + \varepsilon_t$ 进行OLS估计，可直接获得边际消费倾向（MPC）的数值估计，并通过 $t$ 检验验证其统计显著性。

**劳动经济学中的明瑟方程**：明瑟（Mincer，1974）提出的工资方程 $\ln W_i = \beta_0 + \beta_1 S_i + \beta_2 \text{EXP}_i + \beta_3 \text{EXP}_i^2 + \varepsilon_i$（其中 $S_i$ 为受教育年限，$\text{EXP}_i$ 为工作经验）是简单线性回归扩展为多元回归的经典案例，$\hat{\beta}_1$ 估计教育回报率，大量实证研究发现该值在7%—10%之间。

**事件研究**：金融经济学用线性回归估计股票的市场模型 $R_{i,t} = \alpha_i + \beta_i R_{m,t} + \varepsilon_{i,t}$，其中斜率 $\beta_i$ 即为衡量系统性风险的贝塔系数，可用OLS对历史收益率数据直接估计。

## 常见误区

**误区一：$R^2$ 高意味着模型好、回归系数可靠**。在时间序列数据中，两个均随时间增长的变量（如中国历年GDP与巧克力产量）往往产生极高的 $R^2$（可能超过0.95），但这是伪回归现象，二者并无真实因果或经济关联。高 $R^2$ 无法替代对误差项假设的检验（如DW检验自相关）。

**误区二：线性回归只能处理"直线"关系**。线性回归中的"线性"指参数的线性，而非变量的线性。模型 $Y_i = \beta_0 + \beta_1 X_i + \beta_2 X_i^2 + \varepsilon_i$ 关于参数 $\beta_0, \beta_1, \beta_2$ 仍是线性的，可以直接用OLS估计，但它在变量空间中是一条抛物线。

**误区三：OLS系数估计的是因果效应**。OLS估计的是条件期望函数的线性近似，即 $\hat{\beta}_1$ 反映 $X$ 与 $Y$ 的偏相关关系。若存在遗漏变量（如用教育年限回归工资但忽略个人能力），则 $\hat{\beta}_1$ 是有偏的，不能解释为教育对工资的因果影响。识别因果效应需要进一步的内生性处理方法（如工具变量法）。

## 知识关联

学习线性回归之前，需要掌握计量经济学概述中介绍的基本概念，包括总体与样本的区分、期望与方差的性质，以及计量研究的基本逻辑框架，这些是理解OLS无偏性证明的直接前提。

线性回归是**多元回归**的起点。从一个解释变量扩展到 $k$ 个解释变量时，OLS估计量的矩阵形式为 $\hat{\boldsymbol{\beta}} = (\mathbf{X}'\mathbf{X})^{-1}\mathbf{X}'\mathbf{Y}$，高斯-马尔可夫定理同样适用，但需额外处理多重共线性问题。在**假设检验**专题中，$F$ 检验用于联合检验多个回归系数是否同时为零，是对简单线性回归 $t$ 检验的推广。**极大似然估计**在误差项正态分布假设下与OLS等价，但在误差非正态（如二元因变量的Probit/Logit
