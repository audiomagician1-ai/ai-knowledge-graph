---
id: "unsupervised-learning"
concept: "无监督学习"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 6
is_milestone: false
tags: ["ML"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 无监督学习

## 概述

无监督学习（Unsupervised Learning）是机器学习的一大分支，其本质特征是从**无标签数据**中自动发现隐藏结构，无需人工为每个样本提供类别或数值标注。与监督学习中最小化预测误差的目标不同，无监督学习的优化目标通常是数据的重构误差、对数似然、或类内紧密度等内部指标。这一思路最早可追溯至1950年代统计学中的因子分析（Factor Analysis）和主成分分析（PCA），后者由 Karl Pearson 于1901年正式提出，用于将高维数据投影至方差最大的低维子空间。

无监督学习之所以在当今AI工程中具有不可替代的地位，核心原因在于**现实世界中带标签数据极度稀缺**。ImageNet 的完整标注耗费了超过2.5万名工人约三年时间，而互联网每天产生的文本、图像数据量远超任何标注团队的处理能力。Bengio、Courville 和 LeCun 在深度学习综述 [Bengio et al., 2013] 中明确指出，无监督预训练是突破有限标签瓶颈的关键路径。典型的无监督学习任务包括聚类（Clustering）、降维（Dimensionality Reduction）和密度估计（Density Estimation）三大类别。

## 核心原理

### 聚类算法：K-Means 与 DBSCAN 的对比

K-Means 算法由 MacQueen 于1967年命名，其目标是最小化所有样本到其所属聚类中心的平方距离之和，即：

$$J = \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2$$

其中 $\mu_k$ 为第 $k$ 个聚类的质心，$C_k$ 为该聚类的样本集合。K-Means 的时间复杂度为 $O(nKdt)$，其中 $n$ 为样本数，$d$ 为维度，$t$ 为迭代次数，对于球状、各向同性的聚类表现优秀，但对非凸形状的簇完全失效。

相比之下，DBSCAN（Density-Based Spatial Clustering of Applications with Noise）通过定义 $\epsilon$-邻域密度来发现任意形状的簇，并自动将稀疏区域的点标记为噪声。其核心参数 `minPts` 和 `epsilon` 共同决定密度核心点的判定，无需预先指定簇的数量 $K$，是 K-Means 无法替代的场景下的首选方案。

### 降维：PCA 与 t-SNE 的数学本质

PCA 的核心操作是对数据协方差矩阵 $\Sigma = \frac{1}{n} X^T X$ 进行特征值分解，取前 $d'$ 个最大特征值对应的特征向量构成投影矩阵 $W \in \mathbb{R}^{d \times d'}$，降维后的表示为 $Z = XW$。PCA 保留的是全局线性方差结构，对非线性流形数据（如手写数字卷曲的流形）的可视化效果有限。

t-SNE（t-distributed Stochastic Neighbor Embedding）由 van der Maaten 和 Hinton 于2008年提出 [van der Maaten & Hinton, 2008]，其核心思想是在高维空间中用高斯核定义点对相似度 $p_{ij}$，在低维空间中用 Student-t 分布定义 $q_{ij}$，然后最小化两个分布之间的 KL 散度：

$$\text{Loss} = \text{KL}(P \| Q) = \sum_{i \neq j} p_{ij} \log \frac{p_{ij}}{q_{ij}}$$

t-SNE 使用 Student-t 分布而非高斯分布的原因在于，t 分布具有更厚的尾部，能缓解高维空间中所有点距离趋于相等的"维度诅咒"。

### 生成模型：高斯混合模型与 EM 算法

高斯混合模型（GMM）假设数据由 $K$ 个高斯分布混合生成，其概率密度为：

$$p(x) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x \mid \mu_k, \Sigma_k)$$

其中 $\pi_k$ 为混合权重，满足 $\sum_k \pi_k = 1$。由于隐变量（每个样本所属的高斯成分）未知，直接最大化对数似然无法得到解析解，因此使用 EM 算法交替进行 E 步（计算后验概率 $\gamma_{ik}$）和 M 步（更新 $\mu_k, \Sigma_k, \pi_k$）。GMM 可以看作 K-Means 的"软分配"概率版本，当所有 $\Sigma_k = \sigma^2 I$ 且 $\sigma \to 0$ 时，GMM 的 EM 算法退化为 K-Means。

## 实际应用

**客户细分（Customer Segmentation）**：电商平台 Amazon 和 Netflix 的推荐系统早期阶段均使用 K-Means 或层次聚类对用户购买行为向量进行分组，将数千万用户压缩为数十至数百个细分群体，再针对每个群体设计差异化的推荐策略。Spotify 的音乐推荐系统使用 GMM 对用户收听行为建模，每个高斯成分对应一种听音乐习惯（如"健身时听"或"工作时听"）。

**异常检测（Anomaly Detection）**：信用卡欺诈检测场景中，正常交易占比超过99.9%，标注欺诈样本极为昂贵。通过 Isolation Forest 或基于 PCA 的重构误差方法，可以在无标签数据上学习正常模式，将重构误差超过阈值的样本识别为异常。PayPal 曾公开报告其基于无监督方法的欺诈检测系统将误报率降低了约50%。

**NLP 词向量预训练**：Word2Vec（Mikolov et al., 2013）的 Skip-gram 和 CBOW 模型本质上是无监督学习，从大规模无标注语料中通过上下文预测任务学习词的分布式表示。在 Google News 的1000亿词语料上训练的词向量能捕捉到 $\vec{\text{king}} - \vec{\text{man}} + \vec{\text{woman}} \approx \vec{\text{queen}}$ 这样的语义代数关系，证明了无监督学习能从原始数据中提取丰富的语义结构。

## 常见误区

**误区一：聚类结果的簇数就是真实类别数**。K-Means 要求用户预先指定 $K$，但"最优" $K$ 的选择依赖于评估标准。轮廓系数（Silhouette Score）和肘部法则（Elbow Method）给出的最优 $K$ 可能不一致，且都不等价于数据的真实类别数。例如在 MNIST 数字数据集上运行 K-Means 时，即便设定 $K=10$，各簇与0-9数字的对应也远非完美，因为"8"在像素空间中具有高度非凸的子流形结构。

**误区二：降维一定会损失信息**。PCA 确实通过丢弃低方差主成分来实现降维，存在信息损失。但自编码器（Autoencoder）通过瓶颈层学习的低维表示，若重构损失趋近于零，理论上可以做到无损压缩（对于训练集）。更重要的是，某些"丢失"的方差维度实际上是噪声，降维后在下游任务上的性能反而优于原始高维特征，这一现象在人脸识别的 Eigenfaces 方法中得到了充分验证。

**误区三：无监督学习完全不需要任何先验知识**。实际上，K-Means 中的 $K$、DBSCAN 中的 $\epsilon$ 和 `minPts`、GMM 中的 $K$ 以及 PCA 中保留的主成分数量，都是需要领域知识或交叉验证来确定的超参数。无监督学习只是不需要**样本级标签**，并不意味着不需要人类知识的注入。若在金融风控场景中盲目使用默认超参数的 K-Means，可能将高风险客户与正常客户归入同一簇，导致严重决策失误。

## 代码示例：Scikit-learn 中的 K-Means 聚类

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np

# 数据标准化：K-Means 对尺度敏感，必须先归一化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # X 为原始特征矩阵 (n_samples, n_features)

# 用肘部法则选择最优 K
inertias = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    km.fit(X_scaled)
    inertias.append(km.inertia_)  # inertia_ 即目标函数 J

# 计算轮廓系数评估聚类质量（取值范围 [-1, 1]，越大越好）
km_best = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
labels = km_best.fit_predict(X_scaled)
score = silhouette_score(X_scaled, labels)
print(f"Silhouette Score: {score:.4f}")
```

注意 `init='k-means++'` 使用 Arthur & Vassilvitskii（2007）提出的改进初始化方案，将簇中心按距离概率分散初始化，可使最终 $J$ 值比随机初始化降低10%~30%。

## 思考题

1. 在对10万条用户行为日志进行聚类时，你选择了 $K=8$ 的 K-Means。但业务团队反馈聚类结果中某一个"超级大簇"包含了70%的用户，几乎没有可操作的差异性。从 K-Means 的目标函数 $J$ 和数据分布的角度，分析产生这一现象的数学原因，以及你会如何改进聚类方案？

2. PCA 和 t-SNE 都能将高维数据降至2维进行可视化，但 t-SNE 降维后的坐标不能用于训练下游分类器，而 PCA 的投影可以。结合两者的数学目标函数，解释为什么 t-SNE 的低维表示不具备 PCA 那样的线性可迁移性？

3. Word2Vec 的 Skip-gram 任务（给定中心词预测上下文词）与有监督分类任务在形式上非常相似，都是通过 softmax 输出概率分布。从数据标签的来源角度，解释为什么 Word2Vec 被归类为无监督学习，而不是监督学习？这对"监督/无监督"的定义边界有何启发？
