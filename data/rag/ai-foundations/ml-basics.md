---
id: "ml-basics"
concept: "机器学习基础"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["ML"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 机器学习基础

## 概述

机器学习（Machine Learning）这一术语由Arthur Samuel于1959年在IBM工作期间首次正式提出，他将其定义为"让计算机无需显式编程便能自主学习的研究领域"。与传统编程中人工编写规则不同，机器学习系统通过从数据中归纳统计模式来构建预测模型。Tom Mitchell在1997年出版的《Machine Learning》中给出了更为精确的形式化定义：对于任务T和性能度量P，若计算机程序在经验E的积累后在T上的P得到提升，则称该程序从E中学习 [Mitchell, 1997]。

机器学习的本质是**统计估计问题**：给定训练数据集 $\mathcal{D} = \{(x_1, y_1), (x_2, y_2), \ldots, (x_n, y_n)\}$，目标是学习一个从输入空间 $\mathcal{X}$ 到输出空间 $\mathcal{Y}$ 的映射函数 $f: \mathcal{X} \to \mathcal{Y}$，使其在未见过的新数据上也具有良好的泛化能力。这一泛化能力的理论基础来自于Vladimir Vapnik与Alexey Chervonenkis在1971年建立的VC理论（Vapnik-Chervonenkis Theory），该理论量化了模型复杂度与泛化误差之间的关系。

## 核心原理

### 三大学习范式的本质区别

机器学习根据训练信号的性质分为三类范式，每类在数学结构上截然不同。**监督学习**（Supervised Learning）要求每个训练样本都配有标签 $y_i$，算法目标是最小化经验风险 $\hat{R}(f) = \frac{1}{n}\sum_{i=1}^{n} L(f(x_i), y_i)$，其中 $L$ 为损失函数。**无监督学习**（Unsupervised Learning）仅有输入数据 $\{x_1, \ldots, x_n\}$，目标是发现数据内在结构，如聚类（K-Means）或降维（PCA）。**强化学习**（Reinforcement Learning）则不存在静态数据集，智能体通过与环境交互获得奖励信号 $r_t$，目标是最大化累积折扣奖励 $G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k}$，其中折扣因子 $\gamma \in [0,1)$。

### 偏差-方差分解：模型选择的核心数学框架

任何监督学习模型的泛化误差都可以精确分解为三个独立项。对于回归问题，期望均方误差（Expected MSE）满足：

$$\mathbb{E}[(y - \hat{f}(x))^2] = \underbrace{\text{Bias}[\hat{f}(x)]^2}_{\text{偏差}^2} + \underbrace{\text{Var}[\hat{f}(x)]}_{\text{方差}} + \underbrace{\sigma^2}_{\text{不可约误差}}$$

其中偏差（Bias）衡量模型平均预测与真实值的系统性偏离，方差（Variance）衡量模型对训练集变化的敏感程度，不可约误差 $\sigma^2$ 来自数据本身的噪声无法消除。一个深度为3的决策树通常表现为高偏差（因为模型过于简单），而深度为20的决策树则表现为高方差（过拟合训练数据），这就是著名的**偏差-方差权衡**（Bias-Variance Tradeoff）。Hastie等人在《The Elements of Statistical Learning》第二版中对该分解进行了严格的数学推导 [Hastie et al., 2009]。

### 梯度下降：参数优化的核心算法

绝大多数机器学习模型的训练过程都归结为一个优化问题：找到使损失函数 $J(\theta)$ 最小的参数向量 $\theta^*$。**批量梯度下降**（Batch Gradient Descent）的参数更新规则为：

$$\theta_{t+1} = \theta_t - \eta \cdot \nabla_\theta J(\theta_t)$$

其中 $\eta$ 为学习率（Learning Rate），是对优化速度影响最大的超参数之一。当 $\eta$ 过大时（如 $\eta = 0.9$），参数在最小值附近震荡甚至发散；当 $\eta$ 过小时（如 $\eta = 0.0001$），收敛极其缓慢。实践中常用的**随机梯度下降**（SGD）每次仅用单个样本更新，而**小批量梯度下降**（Mini-batch GD）使用大小为 $m$（通常 $m \in \{32, 64, 128\}$）的子集，在计算效率与梯度估计精度之间取得平衡。以下是Mini-batch梯度下降的基本实现：

```python
import numpy as np

def mini_batch_gradient_descent(X, y, theta, learning_rate=0.01, 
                                 batch_size=32, epochs=100):
    n_samples = X.shape[0]
    loss_history = []
    
    for epoch in range(epochs):
        # 每个epoch随机打乱数据
        indices = np.random.permutation(n_samples)
        X_shuffled, y_shuffled = X[indices], y[indices]
        
        for start in range(0, n_samples, batch_size):
            X_batch = X_shuffled[start:start + batch_size]
            y_batch = y_shuffled[start:start + batch_size]
            
            # 计算预测值与梯度（以线性回归MSE损失为例）
            predictions = X_batch @ theta
            errors = predictions - y_batch
            gradient = (2 / len(X_batch)) * X_batch.T @ errors
            
            theta -= learning_rate * gradient
        
        # 记录全局损失
        full_loss = np.mean((X @ theta - y) ** 2)
        loss_history.append(full_loss)
    
    return theta, loss_history
```

### 过拟合与正则化：控制模型复杂度

当模型在训练集上损失极低（如 $J_{train} = 0.02$）但在测试集上损失远高（如 $J_{test} = 0.48$）时，即发生过拟合。正则化通过在损失函数中引入惩罚项抑制模型参数量级。**L2正则化**（也称Ridge回归或权重衰减）的目标函数为：

$$J_{L2}(\theta) = \frac{1}{n}\sum_{i=1}^n L(f_\theta(x_i), y_i) + \frac{\lambda}{2}\|\theta\|_2^2$$

**L1正则化**（Lasso回归）使用 $\lambda\|\theta\|_1$，其几何特性会将部分参数精确压缩至零，从而产生稀疏解，具有自动特征选择功能。正则化强度 $\lambda$ 是需要通过交叉验证调整的关键超参数。

## 实际应用

**垃圾邮件过滤**是监督学习最经典的应用案例之一。Google Gmail使用基于机器学习的过滤系统，将训练集中数百万封人工标注的邮件（特征包括词频TF-IDF向量、发件人信誉分、链接数量等）输入朴素贝叶斯或梯度提升树模型，最终实现超过99.9%的垃圾邮件拦截率，而误报率低于0.05%。其核心是学习从高维稀疏特征向量（通常维度超过50万）到二元标签的映射。

**推荐系统中的协同过滤**是无监督与监督学习结合的典型场景。Netflix在2009年举办的Netflix Prize竞赛中，获胜方BellKor's Pragmatic Chaos团队使用矩阵分解（Matrix Factorization）将用户-物品评分矩阵 $R \in \mathbb{R}^{m \times n}$ 分解为低秩矩阵 $R \approx U V^T$（其中 $U \in \mathbb{R}^{m \times k}$，$V \in \mathbb{R}^{n \times k}$，$k$ 通常取50-200），在测试集上将RMSE从0.9525降低至0.8567，提升幅度超过10%，赢得100万美元奖金。

**医学影像诊断**中，基于卷积神经网络的机器学习模型展示了监督学习的强大潜力。2017年斯坦福大学发表在《Nature》上的研究表明，训练于12.9万张皮肤病变图像的深度学习分类器，在区分恶性黑色素瘤与良性痣的任务上，AUC达到0.96，与21位委员会认证的皮肤科专家的平均水平（AUC 0.91）相比甚至更优。

## 常见误区

**误区一：样本量越大，模型一定越好。** 许多初学者认为收集更多数据是解决所有问题的万能方案。实际上，当数据存在系统性偏差（Systematic Bias）时，增加样本量只会放大这种偏差。Amazon在2018年废弃的招聘AI系统就是典型案例：该系统训练于10年间的简历数据，由于历史雇员以男性为主，模型学会了对女性候选人降分，数据量越大反而使歧视越严重。正确做法是优先检查数据分布是否与目标场景一致，而非盲目扩充数量。

**误区二：训练准确率高即代表模型优秀。** 一个将所有样本都预测为多数类的"哑模型"（Dummy Classifier），在正负样本比例为95:5的不平衡数据集上，训练准确率可达95%，但该模型对正类（如罕见疾病患者）的召回率（Recall）为0，完全没有实用价值。正确的做法是根据任务性质选用AUC-ROC、F1-Score、PR曲线等专门针对不平衡场景设计的评估指标，而非仅依赖准确率。

**误区三：特征越多，模型性能越好（"维度越高越好"）。** 这与Bellman在1957年提出的**维数灾难**（Curse of Dimensionality）直接矛盾。在高维空间中，数据点变得极度稀疏——若每个维度需要10个样本点才能充分覆盖，那么10维空间就需要 $10^{10}$ 个样本。不相关特征会引入额外噪声，导致模型方差增大，在测试集上性能反而下降。Sklearn的`SelectKBest`或基于随机森林的特征重要性评分可用于识别并删除无信息特征。

## 思考题

1. 假设你训练了一个线性回归模型预测房价，发现训练集MSE为 $5.2 \times 10^4$，验证集MSE为 $5.1 \times 10^4$，两者均远高于业务需求的 $1.0 \times 10^4$。根据偏差-方差分解，请判断此时主要问题是高偏差还是高方差？应该增加训练样本量、增大模型复杂度还是引入更强的正则化来解决？请结合具体数学公式说明你的判断依据。

2. 在小批量梯度下降中，若将 `batch_size` 从32增大到完整数据集大小 $n$（即退化为批量梯度下降），理论上梯度估计更精确，为何在深度学习实践中反而批量梯度下降的泛化性能通常不如小批量下降？请从梯度噪声与逃离鞍点的角度分析。

3. L1正则化（Lasso）与L2正则化（Ridge）均能抑制过拟合，但Lasso能产生稀疏解而Ridge不能。请从两者的约束域几何形状（L1为菱形，L2为圆形）角度，解释为何在高维特征空间中，Lasso更适合用于自动特征选择的场景，并举出一个具体的实际案例。
