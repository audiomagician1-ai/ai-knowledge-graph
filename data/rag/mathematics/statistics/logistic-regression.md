---
id: "logistic-regression"
concept: "逻辑回归"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 7
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---



# 逻辑回归

## 概述

逻辑回归（Logistic Regression）是一种用于解决**二分类问题**的统计学习方法，其输出值被约束在 (0, 1) 区间内，直接表示事件发生的条件概率。尽管名称中含有"回归"二字，逻辑回归本质上是一种分类方法：它通过对线性组合 $z = \mathbf{w}^\top \mathbf{x} + b$ 施加 Sigmoid 函数，将实数域压缩为概率值，再以 0.5 为默认决策阈值进行类别判定。

逻辑回归的理论根源可追溯至 1838 年比利时数学家 Pierre François Verhulst 提出的 Logistic 增长模型，该模型原用于描述种群受资源约束时的增长规律。将其引入二分类统计建模的奠基性工作由 David Cox 于 1958 年完成，他在论文 *The Regression Analysis of Binary Sequences* 中系统地提出了将对数几率（log-odds）对自变量作线性回归的框架，使该方法在生物医学、流行病学领域迅速普及。

逻辑回归之所以在现代机器学习中仍具重要地位，原因在于它的参数具有直接可解释的**几率比（Odds Ratio）**含义：特征 $x_j$ 每增加 1 个单位，事件发生的几率乘以 $e^{w_j}$。这一性质使其在医学临床预测、信用评分等需要解释模型决策的场景中不可替代，同时也是深度神经网络中分类输出层的直接前身。

---

## 核心原理

### Sigmoid 函数与概率映射

Sigmoid 函数定义为：

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

其中 $z = \mathbf{w}^\top \mathbf{x} + b$ 是输入特征的线性组合。Sigmoid 的导数具有优美的自反性：$\sigma'(z) = \sigma(z)(1 - \sigma(z))$，这一性质直接决定了反向传播时梯度的计算效率。当 $z=0$ 时 $\sigma(z)=0.5$，函数在 $z \in (-\infty, +\infty)$ 上单调递增，值域严格限于 $(0, 1)$，从而保证模型输出可被解释为概率 $P(Y=1 \mid \mathbf{x})$。

值得注意的是，Sigmoid 在 $|z| > 5$ 的区域梯度接近于零，这正是神经网络深层训练中"梯度消失"问题的直接诱因。在二分类逻辑回归的参数估计中，该问题不明显，但在多层网络中需用 ReLU 等函数替代。

### 对数几率与线性性

逻辑回归对目标变量的假设等价于：

$$\ln \frac{P(Y=1|\mathbf{x})}{P(Y=0|\mathbf{x})} = \mathbf{w}^\top \mathbf{x} + b$$

左侧称为**对数几率（log-odds 或 logit）**，它是 Sigmoid 的反函数 $\text{logit}(p) = \ln\frac{p}{1-p}$。这一变换表明逻辑回归实际上是在对事件发生的对数几率做线性建模，而非对概率本身做线性建模——这解释了为何直接对概率做线性回归（线性概率模型）会导致预测值越界 ($p < 0$ 或 $p > 1$）的问题。

### 最大似然估计与交叉熵损失

给定 $n$ 个独立同分布样本 $\{(\mathbf{x}_i, y_i)\}$，$y_i \in \{0, 1\}$，对数似然函数为：

$$\ell(\mathbf{w}, b) = \sum_{i=1}^{n} \left[ y_i \ln \hat{p}_i + (1 - y_i) \ln(1 - \hat{p}_i) \right]$$

其中 $\hat{p}_i = \sigma(\mathbf{w}^\top \mathbf{x}_i + b)$。最大化对数似然等价于最小化**二元交叉熵损失**（取负号）。与线性回归的均方误差损失不同，交叉熵损失在逻辑回归中是关于参数 $\mathbf{w}$ 的**凸函数**，这保证了梯度下降收敛到全局最优解，不存在局部极小值问题。

对参数求偏导可得：

$$\frac{\partial \ell}{\partial \mathbf{w}} = \sum_{i=1}^{n} (y_i - \hat{p}_i)\mathbf{x}_i$$

梯度形式与线性回归的残差梯度在形式上完全一致，但 $\hat{p}_i$ 的计算路径不同。实践中通常使用**拟牛顿法（L-BFGS）**或小批量随机梯度下降（mini-batch SGD）进行优化，scikit-learn 的逻辑回归默认使用 L-BFGS 求解器。

### 正则化

为防止过拟合，逻辑回归常加入 L1（Lasso）或 L2（Ridge）正则项。L2 正则化目标函数为：

$$\min_{\mathbf{w}} -\ell(\mathbf{w}) + \frac{\lambda}{2}\|\mathbf{w}\|^2$$

L1 正则化则会产生**稀疏解**，自动将不重要特征的系数压缩至零，常用于高维基因表达数据的特征筛选。scikit-learn 中对应参数 `C = 1/λ`，默认值 `C=1.0`。

---

## 实际应用

**医学诊断**：在弗雷明汉心脏研究（Framingham Heart Study）中，逻辑回归被用于预测患者10年内发生冠心病的概率，预测变量包括年龄、血压、血清胆固醇等。模型输出的 Odds Ratio 直接为临床医生提供"该危险因素使患病风险增加多少倍"的解释。

**信用评分**：银行业的 FICO 评分底层模型大量使用逻辑回归。特征工程后，每个变量的 $e^{w_j}$ 被转化为"评分卡"中某区间的加分/减分项，满足监管机构对模型可解释性的要求。

**自然语言处理**：在文本情感分类的基线系统中，将词袋（Bag-of-Words）特征接入逻辑回归，是验证特征有效性的标准做法。斯坦福 CS224N 课程中明确指出，逻辑回归在情感二分类任务上往往能达到神经网络 90% 以上的性能，且训练速度快数个量级。

---

## 常见误区

**误区一：认为逻辑回归假设特征与因变量呈线性关系**。逻辑回归的线性假设是针对**对数几率**而非概率本身。对于明显非线性的决策边界，可通过添加多项式特征（如 $x_1^2, x_1 x_2$）或使用核方法来处理，而无需放弃逻辑回归框架。

**误区二：默认阈值 0.5 是最优决策边界**。在类别严重不平衡的场景（如欺诈检测，正样本比例可能低于 1%）中，以 0.5 为阈值会导致模型几乎从不预测正类。正确做法是在 ROC 曲线上根据业务目标（如最大化 F1 分数或满足特定召回率约束）重新选择阈值，或使用 PR 曲线（Precision-Recall Curve）评估。

**误区三：混淆逻辑回归与线性判别分析（LDA）的假设体系**。LDA 假设各类别的特征服从协方差矩阵相同的多元正态分布，从先验到后验用贝叶斯定理推导。逻辑回归则是**判别式模型**，直接对条件概率 $P(Y|\mathbf{X})$ 建模，不对特征分布做任何参数假设，因此在特征分布非正态时通常比 LDA 更鲁棒。

---

## 知识关联

**前置概念**：学习逻辑回归需要掌握**线性回归**中的参数向量化表示 $\mathbf{w}^\top\mathbf{x}$ 和梯度下降优化思路；同时需要**监督学习**框架中的训练集/测试集划分、损失函数最小化范式。逻辑回归将线性回归的实数输出套上 Sigmoid 函数，是从回归到分类的关键过渡。

**后续概念**：**生存分析初步**中的 Cox 比例风险模型（Cox Proportional Hazards Model）与逻辑回归共享对数线性结构：$\ln h(t|\mathbf{x}) = \ln h_0(t) + \mathbf{w}^\top\mathbf{x}$，其中风险函数 $h(t)$ 替代了逻辑回归中的对数几率。理解逻辑回归的最大偏似然估计与凸优化性质，是推导 Cox 模型参数估计方法的直接基础。此外，多项逻辑回归（Softmax 回归）将二分类推广至 $K$ 类，构成深度神经网络分类头的标准形式。