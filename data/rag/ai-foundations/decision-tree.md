---
id: "decision-tree"
concept: "决策树"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["ML"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 决策树

## 概述

决策树（Decision Tree）是一种模拟人类决策过程的监督学习算法，其核心结构由根节点（Root Node）、内部节点（Internal Node）、分支（Branch）和叶节点（Leaf Node）构成。每个内部节点对应一个特征属性的测试条件，每条分支对应该测试的一个可能结果，每个叶节点存储最终的分类标签或回归预测值。这种树形结构的预测逻辑对人类完全可解释，因此决策树被誉为"白盒模型"，与神经网络等黑盒模型形成鲜明对比。

决策树的系统性研究始于1963年，Morgan和Sonquist在《美国统计协会杂志》发表了自动交互检测（AID）算法，这是最早的树形分割方法之一。1979年，Ross Quinlan开发了ID3（Iterative Dichotomiser 3）算法，随后在1993年出版的《C4.5: Programs for Machine Learning》中提出了更完善的C4.5算法 [Quinlan, 1993]，将ID3扩展至支持连续属性、缺失值处理和剪枝操作，成为该领域的经典参考实现。1984年，Breiman等人在《Classification and Regression Trees》中提出CART（Classification and Regression Trees）算法 [Breiman et al., 1984]，该算法使用二叉树结构并支持回归任务，至今仍是scikit-learn库中`DecisionTreeClassifier`的默认实现基础。

## 核心原理

### 特征分裂准则

决策树的构建本质是一个贪心的递归分裂过程，每次选择使"杂质度"下降最大的特征和阈值进行节点分裂。ID3和C4.5使用**信息增益**（Information Gain）和**信息增益率**作为分裂准则，CART则使用**基尼不纯度**（Gini Impurity）。

信息熵（Entropy）定义为：

$$H(S) = -\sum_{k=1}^{K} p_k \log_2 p_k$$

其中 $p_k$ 是样本集合 $S$ 中第 $k$ 类样本的比例。信息增益计算为：

$$\text{IG}(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} H(S_v)$$

基尼不纯度则定义为：

$$\text{Gini}(S) = 1 - \sum_{k=1}^{K} p_k^2$$

在二分类问题中，当节点完全纯净（只含一类样本）时 $\text{Gini}=0$，最大值为 $0.5$（两类各占50%）。CART在每次分裂时遍历所有特征的所有可能阈值，选择使加权基尼不纯度下降最大的切割点，这使得CART的时间复杂度为 $O(n \cdot d \log d)$，其中 $n$ 为样本数，$d$ 为特征维度。

### 树的构建与终止条件

决策树采用自顶向下的递归分裂策略（Top-Down Induction of Decision Trees，TDIDT）。分裂终止的条件包括：当前节点样本数低于预设阈值`min_samples_split`；节点深度达到`max_depth`上限；节点内所有样本属于同一类别；所有特征的信息增益均为零。叶节点的输出在分类任务中为多数类标签，在回归任务中为该节点所有样本的目标值均值。

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# 加载鸢尾花数据集（150样本，4特征，3类）
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# CART算法，基尼准则，最大深度为3
clf = DecisionTreeClassifier(
    criterion='gini',
    max_depth=3,
    min_samples_split=5,
    random_state=42
)
clf.fit(X_train, y_train)
print(f"测试集准确率: {clf.score(X_test, y_test):.4f}")
# 典型输出: 测试集准确率: 0.9667

# 查看特征重要性（基于加权基尼不纯度下降之和）
for name, imp in zip(iris.feature_names, clf.feature_importances_):
    print(f"{name}: {imp:.4f}")
```

### 剪枝策略

未剪枝的决策树极易过拟合，因为它会持续分裂直至每个叶节点仅包含一个训练样本。剪枝分为**预剪枝**（Pre-Pruning）和**后剪枝**（Post-Pruning）两类。预剪枝通过提前设置`max_depth`、`min_samples_leaf`等超参数限制树的生长。后剪枝中最常用的是CART的**代价复杂度剪枝**（Cost-Complexity Pruning，CCP），其目标函数为：

$$R_\alpha(T) = R(T) + \alpha \cdot |T_\text{leaf}|$$

其中 $R(T)$ 是决策树在训练集上的误分类率，$|T_\text{leaf}|$ 是叶节点数量，$\alpha \geq 0$ 是控制剪枝强度的正则化参数。当 $\alpha = 0$ 时保留完整树；随着 $\alpha$ 增大，树被逐步剪枝。scikit-learn通过`ccp_alpha`参数暴露该功能，实践中建议用交叉验证选择最优 $\alpha$。

## 实际应用

**信用风险评估**：金融机构大量使用决策树进行贷款违约预测。以UCI German Credit数据集为例（1000条记录，20个特征），CART决策树可在测试集上达到约72-75%的准确率，而其可解释性使得银行合规部门能够向监管机构和客户解释拒贷原因——例如"申请金额>5000欧元 AND 工龄<2年 → 高风险"。

**医疗诊断辅助**：决策树在医疗领域的应用尤为广泛，因为医生需要可解释的推理链条。著名的CART应用案例是1980年代心脏病研究中，医生用9个二元问题组成的决策树对心肌梗死患者进行风险分层，该树在独立验证集上的AUC达到0.80，与逻辑回归相比差异不显著但解释性更强。

**特征工程中的重要性筛选**：利用`feature_importances_`属性（即所有节点中某特征贡献的基尼不纯度下降量的归一化求和），决策树可以快速识别高价值特征。在Kaggle的房价预测竞赛中，常见做法是先训练一棵浅层决策树（`max_depth=5`），筛选出重要性排名前20的特征，再送入更复杂的集成模型，这一管道可将特征工程时间减少40%以上。

## 常见误区

**误区一：决策树深度越大，预测越准确。** 这忽略了决策树的方差特性。以iris数据集为例，将`max_depth`从3增加到20，训练集准确率从95%升至100%，但测试集准确率反而从96.7%降至90%以下，这是典型的高方差过拟合。决策树属于高方差低偏差的模型族，叶节点越细分，对训练噪声的记忆越深。随机森林和梯度提升树（如XGBoost）正是通过集成多棵浅树来显式降低这种方差。

**误区二：信息增益和基尼不纯度选哪个对准确率影响巨大。** 大量实证研究（包括Mingers在1989年的系统对比实验）表明，在大多数数据集上两者产生的决策树结构高度相似，测试集精度差异通常低于1%。两者的真实区别在于计算效率和对类别数的敏感性：基尼不纯度无需计算对数，速度更快；信息增益对类别数多的特征存在天然偏好，这正是C4.5引入增益率来修正ID3缺陷的原因。

**误区三：决策树能自动处理特征尺度差异，所以不需要任何预处理。** 决策树确实对特征缩放不敏感（因为分裂只比较同一特征内的相对大小），但对**类别不平衡**极为敏感。当正负样本比例为1:99时，若不设置`class_weight='balanced'`，决策树会倾向于将所有样本预测为负类，准确率看似高达99%，但召回率（Recall）为0，AUC接近0.5，完全失去判别能力。

## 思考题

1. 在一个二分类数据集中，某特征将100个样本分成两组：左子节点60个样本（50正20负），右子节点40个样本（10正30负）。请手动计算以该特征分裂前后的加权基尼不纯度，并判断这次分裂是否值得执行（分裂前整体基尼不纯度约为多少？下降了多少？）

2. 假设你正在构建一个医疗诊断决策树，目标是检测某种发病率仅为2%的罕见病。你会选择什么损失函数或评估指标来训练和验证模型？仅用准确率会带来什么具体后果？如何通过调整`class_weight`参数来缓解这个问题？

3. 决策树的分裂边界始终与坐标轴平行（即每次只按一个特征阈值分割）。请思考：对于一个真实决策边界为 $x_1 + x_2 = 1$（对角线）的二分类问题，决策树需要多少层才能近似拟合这条边界？这与支持向量机（SVM）使用线性核相比有何本质局限？
