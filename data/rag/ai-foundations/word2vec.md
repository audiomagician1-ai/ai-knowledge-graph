---
id: "word2vec"
concept: "Word2Vec"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 4
is_milestone: false
tags: ["embedding", "skip-gram", "cbow", "nlp"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Word2Vec

## 概述

Word2Vec是由Google研究员Tomas Mikolov等人于2013年提出的词向量训练框架，发表于论文《Efficient Estimation of Word Representations in Vector Space》。其核心思想是将词汇表中的每个词映射为固定维度的稠密实数向量（通常为50至300维），使得语义相近的词在向量空间中距离更近。例如，"国王"与"王后"的向量差，近似等于"男人"与"女人"的向量差，即`vec("国王") - vec("男人") ≈ vec("王后") - vec("女人")`，这种线性关系是Word2Vec最具说服力的特性之一。

在Word2Vec之前，NLP领域主要使用One-Hot编码表示词汇，导致词与词之间的余弦相似度永远为0，无法捕捉语义关系，且向量维度等于词汇表大小（常达数万至数十万），极为稀疏低效。Word2Vec通过浅层神经网络（仅含一个隐藏层）将高维稀疏表示压缩为低维稠密向量，同时将语义信息编码进向量几何关系中，极大推动了下游NLP任务的表现。

## 核心原理

### Skip-gram模型

Skip-gram模型的目标是：给定中心词，预测其上下文窗口内的周围词。对于语料中每个位置 $t$ 的中心词 $w_t$，模型尝试最大化以下对数似然：

$$\mathcal{L} = \frac{1}{T} \sum_{t=1}^{T} \sum_{-c \leq j \leq c, j \neq 0} \log P(w_{t+j} \mid w_t)$$

其中 $T$ 为语料总词数，$c$ 为窗口半径（常取2至5）。条件概率使用Softmax计算：

$$P(o \mid c) = \frac{\exp(\mathbf{u}_o^\top \mathbf{v}_c)}{\sum_{w=1}^{W} \exp(\mathbf{u}_w^\top \mathbf{v}_c)}$$

这里 $\mathbf{v}_c$ 是中心词的输入向量，$\mathbf{u}_o$ 是目标上下文词的输出向量，$W$ 为词汇表大小。Skip-gram对低频词的学习效果优于CBOW，因为每个中心词会产生多个独立训练样本。

### CBOW模型

CBOW（Continuous Bag of Words）与Skip-gram方向相反：给定上下文词，预测中心词。CBOW将窗口内所有上下文词的向量取平均后，输入Softmax层预测中心词：

$$\hat{\mathbf{v}} = \frac{1}{2c} \sum_{-c \leq j \leq c, j \neq 0} \mathbf{v}_{t+j}$$

CBOW的训练速度比Skip-gram快约3至5倍，因为每个窗口只产生一次预测，对高频词的学习效果更好，适合大规模语料场景。

### 两种加速训练的技巧

**负采样（Negative Sampling）**是Word2Vec实际训练中最常用的优化手段。原始Softmax分母需对全部词汇表求和，计算代价为 $O(W)$，当词汇表达10万词时代价极大。负采样将问题转化为二分类：对每个正样本词对 $(w_t, w_{t+j})$，随机采样 $k$ 个"噪声词"（$k$ 通常取5至20），目标变为最大化正样本得分、最小化负样本得分：

$$\mathcal{L}_{\text{NS}} = \log \sigma(\mathbf{u}_o^\top \mathbf{v}_c) + \sum_{i=1}^{k} \mathbb{E}_{w_i \sim P_n} [\log \sigma(-\mathbf{u}_{w_i}^\top \mathbf{v}_c)]$$

噪声词按词频的3/4次幂比例采样，即 $P_n(w) \propto f(w)^{3/4}$，这一指数选择经实验证明能平衡高低频词的采样概率。

**高频词下采样**：词频超过阈值 $t$（默认为 $10^{-5}$）的词以概率 $P(w_i) = 1 - \sqrt{t/f(w_i)}$ 被丢弃，避免"的""了"等高频虚词主导训练。

## 实际应用

**文本相似度计算**：训练好的Word2Vec向量通过对句子中所有词向量取平均，得到句子向量，再用余弦相似度衡量语义距离。例如电商平台用此方法匹配用户搜索词与商品标题，实践中300维向量已能捕捉大多数语义关系。

**下游任务特征初始化**：在命名实体识别（NER）、情感分析等任务中，将Word2Vec预训练向量作为Embedding层的初始权重，而非随机初始化，可显著加快收敛并提升模型在小样本上的表现。Google在2013年发布的预训练模型使用1000亿词的Google News语料训练了300维的300万词词向量，这一资源至今仍被广泛用于基线对比实验。

**知识图谱与类比推理**：Word2Vec的向量算术特性使其可用于词语类比任务，如`vec("巴黎") - vec("法国") + vec("日本") ≈ vec("东京")`。在知识图谱补全任务中，这一特性被用于推断实体间关系。

## 常见误区

**误区一：认为Word2Vec的词向量是唯一确定的**。实际上，Word2Vec每次训练由于随机初始化和负采样的随机性，会产生不同的向量，但它们的相对几何关系保持稳定。同时，Word2Vec为每个词维护两套向量（输入矩阵 $V$ 和输出矩阵 $U$），通常取输入矩阵的行向量作为最终词向量，两者不可混用。

**误区二：词窗口越大越好**。窗口大小 $c$ 直接影响捕捉的语义类型：小窗口（1至3）倾向于捕捉句法关系（如形容词-名词搭配），大窗口（5至10）倾向于捕捉主题相关性（如同领域词汇）。盲目增大窗口会引入大量不相关上下文词，稀释局部语义信号。

**误区三：Word2Vec能处理多义词**。Word2Vec为每个词形分配一个固定向量，"苹果"（水果/公司）在所有上下文中共享同一向量，这是其本质局限。这一问题直到ELMo（2018）和BERT（2018）通过动态上下文向量才得到解决，而Word2Vec奠定了这一演进路径的起点。

## 知识关联

**与神经网络基础的关系**：Word2Vec的训练过程本质是对一个两层神经网络（输入层→隐藏层→输出层）进行反向传播，隐藏层权重矩阵即为最终词向量。理解矩阵乘法、梯度下降和Sigmoid/Softmax激活函数是读懂Word2Vec推导的前提。

**与机器学习基础的关系**：负采样将语言建模转化为逻辑回归二分类问题，最大似然估计的目标函数设计直接沿用了监督学习的损失函数框架。

**向后延伸至GloVe与BERT**：2014年斯坦福提出的GloVe在Word2Vec基础上显式引入全局词共现矩阵，而2018年Google的BERT则用双向Transformer替代浅层网络，生成上下文相关的动态词向量，彻底解决了Word2Vec的多义词局限。Word2Vec的负采样思想也影响了后来对比学习（Contrastive Learning）的设计哲学。