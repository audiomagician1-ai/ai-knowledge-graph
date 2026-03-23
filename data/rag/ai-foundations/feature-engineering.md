---
id: "feature-engineering"
concept: "特征工程"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 6
is_milestone: false
tags: ["ML"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 特征工程

## 概述

特征工程（Feature Engineering）是指从原始数据中提取、构造、转换和选择对机器学习模型最有用的输入变量的系统化过程。这一术语由Pedro Domingos在2012年的论文《A Few Useful Things to Know about Machine Learning》[Domingos, 2012]中系统化表述，他指出"Applied machine learning is basically feature engineering"——即应用机器学习的本质就是特征工程。在原始数据转化为模型可用的数值向量的过程中，特征工程直接决定了模型的性能上限：一个线性模型配合精心设计的特征，往往能超越一个使用原始特征的深度神经网络。

特征工程之所以在AI工程中占有独特地位，根本原因在于"垃圾进、垃圾出"（Garbage In, Garbage Out）原则。以Kaggle竞赛为例，2014年Otto Group产品分类大赛的冠军方案并非依赖最复杂的模型，而是通过构造频率编码、目标编码等手工特征获得决定性优势。在工业界，Facebook 2014年发布的GBDT+LR广告点击率预测系统，用梯度提升树自动生成离散化特征再输入逻辑回归，这一架构本质上也是特征工程自动化的产物。

---

## 核心原理

### 特征变换：数值型数据的标准化与归一化

对数值特征进行变换是特征工程最基础的操作。**标准化（Z-score Normalization）**将特征转换为均值为0、标准差为1的分布：

$$z = \frac{x - \mu}{\sigma}$$

**Min-Max归一化**将特征压缩到 $[0, 1]$ 区间：

$$x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

两者的选择并非任意：SVM、PCA、K-Means等基于距离或梯度的算法对量纲差异高度敏感，必须先做标准化；而树模型（GBDT、随机森林）对特征尺度不敏感，可跳过此步。此外，对于右偏分布（如收入、访问量），对数变换 $x' = \log(1+x)$ 能将峰度从数十降低至接近正态分布，显著改善线性模型的拟合效果。

### 特征编码：类别型数据的数值化

类别变量无法直接输入大多数算法，必须经过编码。**One-Hot编码**将含 $k$ 个类别的特征展开为 $k$ 维稀疏向量，当 $k > 1000$ 时（如用户ID、商品ID），会导致维度爆炸。此时应使用**目标编码（Target Encoding）**，将类别替换为该类别对应的目标变量均值：

$$\text{TargetEnc}(c) = \frac{\sum_{i: x_i=c} y_i + \alpha \cdot \bar{y}}{n_c + \alpha}$$

其中 $\alpha$ 为平滑系数，$n_c$ 为类别 $c$ 的样本数，$\bar{y}$ 为全局均值。平滑项的引入是为了防止低频类别过拟合——若某类别只出现一次且对应正样本，未加平滑的编码值将为1.0，严重泄露标签信息。Micci-Barreca在2001年提出的这一平滑目标编码方案[Micci-Barreca, 2001]至今仍是工业推荐系统的标准做法。

### 特征构造与交叉特征

特征构造（Feature Construction）是在已有特征基础上通过数学运算生成新特征。多项式特征通过引入 $x_1 \cdot x_2$、$x_1^2$ 等交叉项，使线性模型能拟合非线性边界。以CTR预估为例，"用户年龄"×"商品类别"的二阶交叉特征能捕捉"年轻用户偏好3C电子"这类协同效应。

在时序数据中，滑动窗口统计特征（如过去7天的均值、标准差、最大值）是电商销量预测、金融风控的核心手段：

```python
import pandas as pd

# 构造用户过去7天的行为统计特征
df['user_click_7d_mean'] = df.groupby('user_id')['click'].transform(
    lambda x: x.rolling(window=7, min_periods=1).mean()
)
df['user_click_7d_std'] = df.groupby('user_id')['click'].transform(
    lambda x: x.rolling(window=7, min_periods=1).std().fillna(0)
)
```

### 特征选择：过滤冗余与噪声

特征选择方法分三类：**过滤法（Filter）**独立于模型，计算互信息 $I(X;Y) = \sum_{x,y} p(x,y)\log\frac{p(x,y)}{p(x)p(y)}$ 或方差阈值筛除低信息量特征；**包裹法（Wrapper）**使用目标模型递归消除特征（RFE），以交叉验证AUC为指标；**嵌入法（Embedded）**通过LASSO回归（L1正则化 $\lambda\|w\|_1$ 使权重稀疏化）或GBDT的特征重要性在训练过程中自动完成选择。《Feature Engineering for Machine Learning》[Zheng & Casari, 2018]系统对比了三类方法：过滤法速度最快，包裹法效果最好但计算代价高，嵌入法是工业界最常用的折衷方案。

---

## 实际应用

**金融风控中的特征工程**：在信贷违约预测场景中，原始数据仅有申请人的基本信息和历史还款记录。实践中需要构造"近3个月逾期次数"、"授信额度使用率"（$\text{utilization} = \frac{\text{已用额度}}{\text{授信上限}}$）、"最长连续逾期天数"等行为特征。这些衍生特征往往将AUC从0.72提升至0.81以上，远超更换复杂模型带来的收益。

**自然语言处理中的词袋特征**：在深度学习普及之前，TF-IDF（词频-逆文档频率）是文本分类的核心特征工程手段：$\text{TF-IDF}(t,d) = \text{tf}(t,d) \times \log\frac{N}{df(t)}$，其中 $N$ 为总文档数，$df(t)$ 为包含词 $t$ 的文档数。即便在2023年的混合检索系统中，TF-IDF稀疏向量仍与BERT稠密向量并用，构成BM25+Dense的双塔召回架构。

**推荐系统的Embedding特征**：Netflix Prize竞赛（2006-2009）中，Simon Funk提出SVD矩阵分解将用户和物品映射为低维隐向量，本质上是自动学习用户-物品的Embedding特征。现代推荐系统在此基础上引入用户历史行为序列的统计特征（平均评分、点击类目分布），与Embedding拼接后输入精排模型。

---

## 常见误区

**误区一：One-Hot编码适用于所有类别变量。** One-Hot编码默认类别间无序且互斥，但对于具有自然顺序的变量（如学历：初中<高中<本科<硕士），应使用有序编码（Ordinal Encoding），保留序数信息；对于树模型，直接使用标签编码（Label Encoding）即可，因为树的分裂操作能自动处理无序类别，不会错误地引入大小关系的偏差。

**误区二：特征越多模型越好。** 加入100个随机噪声特征会使KNN分类器在MNIST上的准确率从97%下降至91%以下，这一现象被称为"维度诅咒"（Curse of Dimensionality）。特征数量超过 $O(\sqrt{n})$（$n$ 为样本量）时，许多算法开始出现性能退化，此时特征选择比添加更多特征更为关键。

**误区三：特征标准化会泄露测试集信息。** 大量初学者在整个数据集上计算均值和标准差后再做分割，导致测试集的统计信息"渗漏"进训练过程。正确做法是：仅在训练集上`fit`（计算均值、方差），再用相同参数`transform`验证集和测试集。在sklearn的Pipeline中，`StandardScaler`自动遵循这一原则，但手动实现时此错误极为普遍。

---

## 思考题

1. 在构造目标编码时，若某类别仅出现1次，未加平滑的编码值等于该样本的标签（0或1）。请分析这种情况下模型在训练集和测试集上的表现会出现什么差异，并推导平滑系数 $\alpha$ 的合理取值范围与样本量的关系。

2. 对于一个包含10万用户、100万商品的电商CTR预估任务，用户ID和商品ID能否直接做One-Hot编码？如果不能，请设计一套特征工程方案，说明每种编码方式解决了什么具体问题，以及它们的计算和存储开销。

3. 假设你发现在训练集上增加交叉特征后，GBDT的AUC从0.80提升至0.88，但测试集AUC仅提升至0.81。请从特征工程的角度分析此现象的三种可能原因，并各提出一种对应的解决策略。
