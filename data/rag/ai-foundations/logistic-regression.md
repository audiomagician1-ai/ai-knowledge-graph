---
id: "logistic-regression"
concept: "逻辑回归"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 7
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
updated_at: "2026-03-26"
---
# 逻辑回归

## 概述

逻辑回归（Logistic Regression）是一种用于**二分类**或多分类任务的监督学习算法，尽管名称中含有"回归"二字，其本质是分类模型。它通过 Sigmoid 函数将线性组合的输入映射到 (0, 1) 区间内的概率值，再以 0.5 为默认决策阈值判断类别归属。

该算法最早由统计学家 David Cox 于 1958 年正式提出，发表于《Journal of the Royal Statistical Society》。其理论根基来自统计学中的对数几率模型（log-odds model），最初用于流行病学领域（如分析某种疾病是否发生的概率），后被机器学习领域广泛采用。

逻辑回归之所以在 AI 工程实践中仍具有重要地位，原因有三：模型输出直接是概率值，具备天然的可解释性；计算代价低，在特征数量达到百万级的大规模稀疏数据（如 CTR 预估）上仍能高效训练；权重系数可直接量化各特征对分类结果的贡献方向与幅度，满足金融、医疗等对模型透明度要求严格的场景。

---

## 核心原理

### Sigmoid 函数与概率输出

逻辑回归的核心变换是 Sigmoid 函数：

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

其中 $z = \mathbf{w}^\top \mathbf{x} + b$，$\mathbf{w}$ 为权重向量，$\mathbf{x}$ 为输入特征向量，$b$ 为偏置项。当 $z \to +\infty$ 时 $\sigma(z) \to 1$，当 $z \to -\infty$ 时 $\sigma(z) \to 0$，$z=0$ 时恰好输出 0.5。模型预测的是正类的条件概率：

$$P(y=1 \mid \mathbf{x}) = \sigma(\mathbf{w}^\top \mathbf{x} + b)$$

### 对数几率与线性决策边界

逻辑回归对**对数几率（log-odds）**建立线性模型：

$$\ln \frac{P(y=1)}{P(y=0)} = \mathbf{w}^\top \mathbf{x} + b$$

这意味着逻辑回归在特征空间中划定的是**线性决策边界**（超平面 $\mathbf{w}^\top \mathbf{x} + b = 0$）。若数据线性不可分，则必须通过特征工程（如多项式特征扩展）或替换为非线性模型来解决，这与逻辑回归本身的结构限制直接相关。

### 损失函数与参数优化

逻辑回归使用**二元交叉熵（Binary Cross-Entropy）**作为损失函数，该损失由最大似然估计推导而来：

$$\mathcal{L}(\mathbf{w}, b) = -\frac{1}{N} \sum_{i=1}^{N} \left[ y_i \ln \hat{p}_i + (1 - y_i) \ln(1 - \hat{p}_i) \right]$$

其中 $\hat{p}_i = \sigma(\mathbf{w}^\top \mathbf{x}_i + b)$，$N$ 为样本数量，$y_i \in \{0, 1\}$。该损失函数是关于参数的**凸函数**，因此梯度下降保证收敛到全局最优（不存在局部最优陷阱）。参数更新的梯度为：

$$\frac{\partial \mathcal{L}}{\partial \mathbf{w}} = \frac{1}{N} \sum_{i=1}^{N} (\hat{p}_i - y_i) \mathbf{x}_i$$

### 正则化

为防止过拟合，逻辑回归常加入 L1（Lasso）或 L2（Ridge）正则项。L1 正则化（$\lambda \|\mathbf{w}\|_1$）会使部分权重精确归零，实现稀疏特征选择；L2 正则化（$\frac{\lambda}{2} \|\mathbf{w}\|_2^2$）则使权重趋向均匀缩小而不至于归零。在 scikit-learn 中，正则化强度由参数 `C = 1/λ` 控制，默认值 `C=1.0`。

---

## 实际应用

**信用风险评分**：银行用逻辑回归判断贷款申请人是否违约。模型输出的概率值（如 0.73）可直接转换为"拒绝"决策，且权重系数可向监管机构说明拒贷理由，满足《欧盟通用数据保护条例（GDPR）》中的算法可解释性要求。

**广告点击率（CTR）预估**：以 Facebook 2014 年发表的 GBDT+LR 方案为例，先用梯度提升树做特征变换，再将树的叶节点编码为离散特征输入逻辑回归，最终在工业级亿级样本下实现高效在线更新。

**医学诊断辅助**：逻辑回归广泛用于肿瘤良恶性二分类。此场景下决策阈值通常设置低于 0.5（如 0.3），以牺牲精确率换取更高的召回率（Recall），减少漏诊风险，这是逻辑回归输出概率值而非硬标签的关键优势。

---

## 常见误区

**误区一：将输出概率视为"真实概率"**
逻辑回归的输出是校准概率，但若训练集存在类别不平衡（如正类仅占 1%），模型输出的 0.3 并不等于"该样本有 30% 概率为正类"。需使用 Platt Scaling 或 Isotonic Regression 进行概率校准后方可作为真实概率解读。

**误区二：认为逻辑回归等同于线性回归加阈值**
线性回归直接拟合目标值，用均方误差（MSE）优化，对分类问题会高估远离边界点的影响；逻辑回归用 Sigmoid+交叉熵，梯度仅由预测概率与真实标签之差驱动，两者在参数优化目标和统计假设上有本质区别，混用会导致梯度爆炸或结果不稳定。

**误区三：默认阈值 0.5 总是最优选择**
0.5 只是在精确率与召回率同等重要时的对称选择。实际工程中应根据业务代价矩阵（cost matrix）调整阈值，或通过绘制 PR 曲线和 ROC 曲线选择最优操作点（operating point），而非直接沿用默认值。

---

## 知识关联

**与监督学习的联系**：逻辑回归是监督学习框架的直接实例——需要带标签的训练数据，通过最小化经验损失学习参数。其训练流程（前向计算→损失计算→梯度反传→权重更新）与神经网络的单层感知机完全等价，因此逻辑回归可视为不含隐藏层的最浅神经网络。

**与多分类的扩展**：通过 Softmax 函数将 Sigmoid 推广，逻辑回归可扩展为**多项逻辑回归（Multinomial Logistic Regression）**，对 $K$ 个类别分别建模，输出各类概率之和为 1。这一结构是深度学习分类任务最后一层的直接原型。

**作为基线模型的工程价值**：在实际 AI 工程项目中，逻辑回归因训练速度快、超参数少（主要只有正则化系数 `C` 和求解器 `solver`），常作为新任务的**基线模型（Baseline）**，用于快速验证特征工程效果和数据质量，为后续引入复杂模型（如梯度提升树、深度网络）提供性能参照标准。
