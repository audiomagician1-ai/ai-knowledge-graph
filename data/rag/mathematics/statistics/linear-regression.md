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
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "An Introduction to Statistical Learning"
    authors: ["Gareth James", "Daniela Witten", "Trevor Hastie", "Robert Tibshirani"]
    year: 2021
    isbn: "978-1071614174"
  - type: "textbook"
    title: "The Elements of Statistical Learning"
    authors: ["Trevor Hastie", "Robert Tibshirani", "Jerome Friedman"]
    year: 2009
    isbn: "978-0387848570"
  - type: "textbook"
    title: "Pattern Recognition and Machine Learning"
    author: "Christopher M. Bishop"
    year: 2006
    isbn: "978-0387310732"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---



# 线性回归

## 概述

线性回归是通过建立因变量 $y$ 与一个或多个自变量 $x$ 之间的线性函数关系，来对连续型数值进行预测和推断的统计方法。其核心假设是：因变量与自变量之间存在**线性关系**，且误差项 $\varepsilon$ 满足独立同分布、均值为零、方差齐次的条件（即高斯-马尔可夫假设）。

线性回归的理论基础可追溯到19世纪初。1805年，法国数学家勒让德（Adrien-Marie Legendre）在研究行星轨道时首次发表了最小二乘法；1809年，高斯在《天体运动理论》中进一步阐明了该方法与正态误差分布之间的联系，证明了在高斯-马尔可夫条件下，最小二乘估计量是最优线性无偏估计量（BLUE, Best Linear Unbiased Estimator）。

线性回归在计量经济学、生物统计学、机器学习中均具有基础性地位。它不仅能够量化自变量对因变量的边际影响（回归系数），还提供了统计显著性检验、置信区间和拟合优度等诊断工具，使结果具有可解释性——这一点使得线性回归在需要因果推断的场景中远比复杂黑箱模型更具优势。

---

## 核心原理

### 一元线性回归模型

一元线性回归的总体模型写作：

$$y = \beta_0 + \beta_1 x + \varepsilon$$

其中 $\beta_0$ 为截距，$\beta_1$ 为斜率（即 $x$ 每增加一个单位，$y$ 的期望变化量），$\varepsilon$ 为随机误差项。通过最小二乘法（OLS），对 $n$ 组观测数据 $(x_i, y_i)$ 最小化残差平方和 $\text{RSS} = \sum_{i=1}^n (y_i - \hat{y}_i)^2$，可得到 $\beta_1$ 的估计量：

$$\hat{\beta}_1 = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^n (x_i - \bar{x})^2} = \frac{S_{xy}}{S_{xx}}$$

该公式表明，$\hat{\beta}_1$ 本质上等于 $x$ 与 $y$ 的协方差除以 $x$ 的方差，与相关性分析中皮尔逊相关系数的计算密切相关。

### 拟合优度 $R^2$

判定系数 $R^2$（R-squared）衡量模型对因变量变异的解释比例，定义为：

$$R^2 = 1 - \frac{\text{RSS}}{\text{TSS}} = 1 - \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{\sum_{i=1}^n (y_i - \bar{y})^2}$$

其中 TSS 为总平方和，RSS 为残差平方和，ESS（回归平方和）= TSS − RSS。$R^2$ 取值范围为 $[0, 1]$，值越接近 1 表示模型拟合越好。在一元线性回归中，$R^2$ 恰好等于 $x$ 与 $y$ 之间皮尔逊相关系数的平方，即 $R^2 = r_{xy}^2$。然而在多元回归中，增加任何新变量必然导致 $R^2$ 不减，因此引入**调整 $R^2$**（Adjusted $R^2$）以对变量数量进行惩罚：

$$\bar{R}^2 = 1 - \frac{\text{RSS}/(n-k-1)}{\text{TSS}/(n-1)}$$

其中 $k$ 为自变量个数，$n$ 为样本量。当新增变量对模型的贡献不足以抵消自由度的损失时，调整 $R^2$ 会下降。

### 多元线性回归与矩阵形式

当自变量个数为 $k$ 时，多元线性回归模型可写成矩阵形式：

$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\varepsilon}$$

其中 $\mathbf{y}$ 为 $n \times 1$ 的因变量向量，$\mathbf{X}$ 为 $n \times (k+1)$ 的设计矩阵（第一列全为1对应截距项），$\boldsymbol{\beta}$ 为 $(k+1) \times 1$ 的参数向量。OLS 的封闭解为：

$$\hat{\boldsymbol{\beta}} = (\mathbf{X}^\top \mathbf{X})^{-1} \mathbf{X}^\top \mathbf{y}$$

该解存在的前提是 $\mathbf{X}^\top \mathbf{X}$ 可逆，即设计矩阵满秩、各自变量之间不存在完全多重共线性。

---

## 实际应用

**房价预测（多元线性回归案例）**：以波士顿房价数据集为例，以房屋面积 $x_1$（平方英尺）、卧室数量 $x_2$、距市中心距离 $x_3$（英里）为自变量，建立多元线性回归模型后，若 $\hat{\beta}_1 = 150$，则表示在其余变量不变的条件下，面积每增加1平方英尺，预期房价上涨150美元——这是线性回归"偏效应"解释的标准方式。

**医学研究中的剂量-反应关系**：在药理学研究中，研究者常用一元线性回归分析药物剂量（mg/kg）与血压降低幅度（mmHg）之间的关系。若 $\hat{\beta}_1 = 2.3$，$R^2 = 0.87$，则可报告：剂量每增加 1 mg/kg，血压平均降低 2.3 mmHg，且该线性模型解释了血压变异的87%。

**机器学习中的正则化线性回归**：当特征维度极高或存在多重共线性时，标准OLS估计会产生方差膨胀。岭回归（Ridge Regression）在目标函数中加入 $L_2$ 惩罚项 $\lambda \|\boldsymbol{\beta}\|_2^2$，LASSO回归加入 $L_1$ 惩罚项 $\lambda \|\boldsymbol{\beta}\|_1$（可产生稀疏解），两者均是线性回归框架的直接延伸。

---

## 常见误区

**误区一：$R^2$ 高就意味着模型好**。$R^2 = 0.95$ 的模型未必具有预测价值。若模型存在过拟合、残差呈现系统性模式（如异方差或自相关），或者数据中含有离群点驱动了高 $R^2$，模型仍然无效。安斯库姆四重奏（Anscombe's Quartet，1973年）中四组数据集有几乎相同的 $R^2 \approx 0.67$，但散点图形态截然不同，充分说明仅凭 $R^2$ 无法判断回归模型的质量。

**误区二：线性回归系数代表因果关系**。线性回归给出的是条件期望的线性近似，而非因果效应。若模型存在遗漏变量（Omitted Variable Bias），则 $\hat{\beta}_1$ 会产生偏误，偏差方向取决于遗漏变量与 $x$ 的相关性及其对 $y$ 的效应方向。例如，在不控制教育程度的情况下回归收入对工作年限，所得系数会混入教育的正向效应。

**误区三：线性回归只能处理线性关系**。通过对变量进行对数变换（$\ln y = \beta_0 + \beta_1 \ln x$，即双对数模型，$\beta_1$ 解释为弹性系数）、多项式扩展（加入 $x^2, x^3$）或交互项（$x_1 \cdot x_2$），线性回归可以拟合非线性的变量关系——"线性"指的是参数 $\boldsymbol{\beta}$ 的线性，而非变量本身的线性。

---

## 知识关联

线性回归建立在**最小二乘法**的代数推导和**相关性分析**提供的变量关系衡量工具之上：皮尔逊相关系数决定了一元线性回归中 $R^2$ 的大小，而协方差矩阵是多元回归 OLS 解的几何基础。来自**计量经济学**的高斯-马尔可夫定理为线性回归提供了最优性保证，而违反假设时的修正方法（加权最小二乘、广义最小二乘等）是计量经济学的进阶内容。

向后延伸，线性回归是**逻辑回归**的直接前驱——逻辑回归将线性预测量 $\mathbf{x}^\top \boldsymbol{\beta}$ 经过 sigmoid 函数映射到概率空间，将回归问题扩展至分类任务。**最大似然估计**能够从概率角度重新推导线性回归：在误差项正态分布假设下，OLS 估计量与最大似然估计量完全等价，这一联系是理解广义线性模型的关键一步。此外，线性回归的矩阵运算框架和梯度下降优化思路，是**神经网络**中全连接层和反向传播算法的原型雏形。