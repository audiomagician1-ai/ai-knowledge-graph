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
updated_at: 2026-03-27
---


# 线性回归

## 概述

线性回归是一种通过拟合自变量（预测变量）与因变量（响应变量）之间线性关系来进行预测和推断的统计建模方法。其核心假设是因变量 $Y$ 可以被表达为一个或多个自变量 $X$ 的**线性函数**加上随机误差项 $\varepsilon$，即 $Y = \beta_0 + \beta_1 X_1 + \cdots + \beta_p X_p + \varepsilon$。这里的"线性"指参数 $\beta$ 的线性，而非自变量本身必须是线性的（例如多项式回归中 $X^2$ 也可作为特征输入）。

线性回归的历史可追溯至19世纪初。1805年，法国数学家**阿德里安-马里·勒让德（Legendre）**首次发表最小二乘法，将其用于天文轨道计算；高斯（Gauss）声称自己在1795年已独立发现该方法，并在1809年给出了基于正态误差假设的概率论证。弗朗西斯·高尔顿（Francis Galton）于1886年在研究父子身高遗传关系时正式引入"回归（regression）"一词，描述子代身高向均值"回归"的现象。

线性回归之所以在数理统计中占有基础地位，是因为它同时具备**可解释性**和**可计算性**：参数 $\beta_j$ 的估计值直接量化了第 $j$ 个自变量对 $Y$ 的边际影响，而最小二乘估计量存在封闭解，无需迭代优化。即便在深度学习盛行的今天，线性回归仍是判断特征与目标变量关系强度的首选基准模型。

---

## 核心原理

### 一元线性回归与参数估计

一元线性回归模型为 $Y_i = \beta_0 + \beta_1 X_i + \varepsilon_i$，其中 $\varepsilon_i \sim \mathcal{N}(0, \sigma^2)$ 是独立同分布的误差项。利用**普通最小二乘法（OLS）**最小化残差平方和 $\text{RSS} = \sum_{i=1}^{n}(Y_i - \hat{Y}_i)^2$，可以得到参数的封闭解：

$$\hat{\beta}_1 = \frac{\sum_{i=1}^n (X_i - \bar{X})(Y_i - \bar{Y})}{\sum_{i=1}^n (X_i - \bar{X})^2} = \frac{S_{XY}}{S_{XX}}, \quad \hat{\beta}_0 = \bar{Y} - \hat{\beta}_1 \bar{X}$$

这两个估计量是**最佳线性无偏估计量（BLUE）**——这是由高斯-马尔可夫定理保证的，其成立前提是误差满足零均值、等方差（homoscedasticity）、无自相关三个条件。

### 多元线性回归与矩阵形式

含 $p$ 个预测变量的多元线性回归写成矩阵形式为 $\mathbf{Y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\varepsilon}$，其中 $\mathbf{X}$ 是 $n \times (p+1)$ 的设计矩阵（第一列全为1对应截距）。OLS估计的矩阵解为：

$$\hat{\boldsymbol{\beta}} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{Y}$$

该解存在的必要条件是 $\mathbf{X}^T\mathbf{X}$ 可逆，即设计矩阵列满秩，不存在**完全多重共线性**。当自变量之间相关性较高时（如VIF > 10通常视为严重问题），$(\mathbf{X}^T\mathbf{X})^{-1}$ 数值不稳定，导致参数估计方差膨胀，此时需考虑岭回归（Ridge）等正则化手段。

### 拟合优度 $R^2$

$R^2$（决定系数）衡量回归模型对因变量总变异的解释比例，定义为：

$$R^2 = 1 - \frac{\text{RSS}}{\text{TSS}} = 1 - \frac{\sum_{i=1}^n (Y_i - \hat{Y}_i)^2}{\sum_{i=1}^n (Y_i - \bar{Y})^2}$$

其中 $\text{TSS}$ 是总平方和，$\text{ESS} = \text{TSS} - \text{RSS}$ 是回归平方和。$R^2 \in [0,1]$，值越接近1说明线性拟合越好。然而，多元回归中每增加一个预测变量，$R^2$ 必然不减——即使该变量与 $Y$ 毫无真实关联。因此通常使用**调整后 $\bar{R}^2$**：

$$\bar{R}^2 = 1 - \frac{\text{RSS}/(n-p-1)}{\text{TSS}/(n-1)}$$

通过对自由度的修正，$\bar{R}^2$ 会对增加无效变量进行"惩罚"，可用于比较含不同变量数量的模型。

### Gauss-Markov条件与违反后果

线性回归的六个经典假设中，**异方差性（heteroscedasticity）**和**自相关（autocorrelation）**是实际数据中最常见的违反情形。前者导致OLS标准误估计偏误（可用White稳健标准误纠正），后者在时间序列数据中尤为突出（需用Newey-West标准误或GLS处理）。误差的**正态性假设**主要影响小样本下的假设检验，根据中心极限定理，在大样本下即使误差非正态，$\hat{\beta}$ 的抽样分布仍近似正态。

---

## 实际应用

**房价预测（多元线性回归典型案例）**：以波士顿房价数据集（506个样本，13个特征）为例，将每平方英尺面积、犯罪率、学区评分等作为 $X$，房屋中位数价格作为 $Y$，拟合多元线性回归后可得各特征的偏回归系数，定量说明"在控制其他变量不变的前提下，每增加1个房间，房价平均上涨约X千美元"。

**计量经济学中的工资方程**：明赛收入方程（Mincer Earnings Function）是经济学中最著名的线性回归应用之一，其形式为 $\ln(W_i) = \beta_0 + \beta_1 S_i + \beta_2 X_i + \beta_3 X_i^2 + \varepsilon_i$，其中 $W$ 为工资，$S$ 为受教育年限，$X$ 为工作经验。对数线性化处理使得系数 $\hat{\beta}_1 \approx 0.10$ 可解读为"多受一年教育，收入平均提高10%"，这是线性回归在因果推断领域的经典范例。

**A/B测试后的回归控制**：在互联网实验中，线性回归常被用来在分析实验效果时控制协变量（如用户年龄、历史消费），从而降低估计误差方差、提升检验功效（CUPED方法的理论基础即为线性回归的方差缩减原理）。

---

## 常见误区

**误区1：$R^2$ 高就代表模型好**
$R^2 = 0.95$ 既可能代表真实的高度线性关系，也可能源于过拟合（尤其当样本量 $n$ 接近参数个数 $p+1$ 时）或数据中存在时间趋势导致的伪相关。安斯库姆四重奏（Anscombe's Quartet）中四组数据的 $R^2$ 和回归方程完全相同，但散点图形状截然不同，说明 $R^2$ 不能替代残差图分析。

**误区2：相关性强则线性回归系数可靠**
两个变量的皮尔逊相关系数 $r$ 和简单线性回归斜率 $\hat{\beta}_1$ 之间的关系是 $\hat{\beta}_1 = r \cdot (S_Y / S_X)$，故 $r$ 仅衡量方向和相对强度，实际斜率还取决于两者的标准差比。更重要的是，高相关性不意味着因果关系，也不意味着关系是线性的——对 $Y = X^2$ 类型的关系，线性回归会严重低估拟合能力，且残差图会呈现明显的抛物线形。

**误区3：多元回归中系数可像一元回归一样直接解读**
在多元回归中，$\hat{\beta}_j$ 是**偏回归系数**，代表在控制所有其他自变量不变时 $X_j$ 对 $Y$ 的独立影响。当自变量之间存在相关性时，单独将某一 $\hat{\beta}_j$ 拿出来与对应一元回归的系数比较是错误的——辛普森悖论（Simpson's Paradox）就是此类混淆的典型体现，方向甚至可能完全相反。

---

## 知识关联

线性回归建立在**最小二乘法**的优化原理之上，后者提供了 $\hat{\beta}$ 的求解机制；而**相关性分析**（皮尔逊 $r$）是判断是否值得建立线性回归模型的初步工具，两者在数学上通过 $R^2 = r^2$（一元情形）紧密相连。从**监督学习**框架