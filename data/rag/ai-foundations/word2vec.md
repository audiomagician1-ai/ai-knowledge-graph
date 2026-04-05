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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

Word2Vec是Google于2013年由Tomas Mikolov等人提出的词向量训练框架，发表于论文《Efficient Estimation of Word Representations in Vector Space》。它的核心思想来自分布式假说（Distributional Hypothesis）：**语义相似的词往往出现在相似的上下文中**。Word2Vec将词汇表中的每个词映射到一个低维稠密的实数向量空间（通常为100至300维），使得向量的几何关系能反映词语的语义关系。

Word2Vec之所以在NLP领域产生革命性影响，在于它能从无标注的大规模语料中高效地学习词语语义。最著名的验证案例是："king - man + woman ≈ queen"，即词向量支持语义加减运算。在Word2Vec出现之前，词语通常用One-Hot向量表示，词汇表有V个词就需要V维向量，且任意两个词的余弦相似度均为0，完全丢失语义信息。Word2Vec将这一问题转化为一个浅层神经网络的预测任务，副产品恰好是高质量的词嵌入。

Word2Vec包含两种模型架构：**Skip-gram**和**CBOW（Continuous Bag of Words）**。两者的结构互为镜像，但训练目标和适用场景有所不同。

---

## 核心原理

### CBOW模型

CBOW的训练目标是：**给定上下文词，预测中心词**。具体来说，设定一个窗口大小 $c$（例如 $c=2$），则对于句子中的目标词 $w_t$，其上下文为 $\{w_{t-c}, \ldots, w_{t-1}, w_{t+1}, \ldots, w_{t+c}\}$，共 $2c$ 个词。

CBOW将这 $2c$ 个上下文词的嵌入向量取**平均值**，作为隐层的输入：

$$\mathbf{h} = \frac{1}{2c} \sum_{j \in \text{context}} \mathbf{v}_{w_j}$$

然后通过输出权重矩阵 $W'$ 计算每个词作为目标词的得分，再经Softmax归一化得到概率分布。训练目标是最大化正确中心词的对数似然。CBOW对于高频词的处理效果更好，训练速度更快。

### Skip-gram模型

Skip-gram的训练目标与CBOW相反：**给定中心词，预测上下文词**。对于中心词 $w_t$，模型需要预测其窗口范围内所有 $2c$ 个上下文词。

Skip-gram对每个上下文位置独立做一次预测，因此每个训练样本会产生 $2c$ 个（输入, 输出）词对。例如，句子"the quick brown fox jumps"，以"brown"为中心词，窗口 $c=2$，则训练对为：(brown, the)、(brown, quick)、(brown, fox)、(brown, jumps)。

Skip-gram的完整目标函数（对语料中每个位置 $t$）为：

$$\mathcal{L} = \frac{1}{T} \sum_{t=1}^{T} \sum_{-c \leq j \leq c, j \neq 0} \log P(w_{t+j} | w_t)$$

Skip-gram对低频词和罕见词的表示效果优于CBOW，因为每个低频词被单独用作预测源，能积累更多梯度更新。

### 两种加速训练的技巧

原始Softmax计算量为 $O(V)$（$V$ 通常高达数十万），训练极慢。Word2Vec提出两种解决方案：

**负采样（Negative Sampling, NEG）**：对于每个正样本 $(w, c)$，随机采样 $k$ 个负样本（通常 $k=5$～$20$），将多分类问题转化为 $k+1$ 个二分类问题。词 $w_i$ 被选为负样本的概率正比于 $f(w_i)^{3/4}$，其中 $f(w_i)$ 是词频，指数 $3/4$ 经实验验证能平衡高频词和低频词的采样比例。

**层次Softmax（Hierarchical Softmax）**：将词汇表组织为一棵哈夫曼树（Huffman Tree），高频词对应更短的路径。预测一个词只需遍历从根到叶节点的路径，计算量降至 $O(\log V)$，树的深度约为 $\log_2 V \approx 17$（对于 $V=100000$ 的词汇表）。

---

## 实际应用

**文本相似度计算**：将句子中所有词向量取均值得到句向量，用余弦相似度衡量两段文本的语义距离。例如在电商搜索中，"手机壳"和"手机保护套"的词向量余弦相似度会显著高于随机词对。

**下游NLP任务的预训练初始化**：命名实体识别（NER）、情感分析等任务，可用预训练好的Word2Vec向量初始化Embedding层，而非随机初始化，通常能提升模型在小数据集上的收敛速度和最终精度。Google发布的预训练模型基于Google News语料（约1000亿词）训练，包含300万个词汇，每个词用300维向量表示，文件大小约3.6GB。

**词语类比推理**：通过向量运算评估模型质量。标准评测集包含Mikolov提出的"语义类比"和"句法类比"两类题目，共8869个语义类比题和10675个句法类比题。在该测试集上，Skip-gram配合负采样的准确率可达约65%（语义）和约75%（句法）。

---

## 常见误区

**误区一：CBOW和Skip-gram只是训练方向相反，效果没有区别。**
实际上两者的适用场景有明显差异。CBOW通过平均上下文向量来预测目标词，平均操作会平滑噪声，更适合高频词和大语料场景，训练速度快约3倍。而Skip-gram为每个上下文词对单独优化，低频词和专业术语的向量质量通常优于CBOW，因此在语料规模较小或领域词汇丰富的场景（如医学、法律文本）中更推荐使用Skip-gram。

**误区二：Word2Vec能捕获一词多义（Polysemy）。**
Word2Vec为每个词类型（word type）只分配一个固定向量，因此"bank"（银行/河岸）这类多义词只能得到一个融合了所有含义的"折中向量"，无法区分具体语境中的含义。这一局限直到ELMo（2018）和BERT（2018）引入上下文相关的动态词向量才得到根本解决。

**误区三：Word2Vec的隐层有非线性激活函数。**
Word2Vec的网络结构极为简单，隐层没有激活函数（或者说使用恒等激活），这与常规神经网络不同。模型只有两个权重矩阵：输入嵌入矩阵 $W \in \mathbb{R}^{V \times d}$ 和输出嵌入矩阵 $W' \in \mathbb{R}^{d \times V}$，其中 $d$ 为嵌入维度。词向量实际上就是 $W$ 的行向量（训练完成后丢弃 $W'$）。

---

## 知识关联

**依赖的前置知识**：Word2Vec的训练本质上是一个浅层神经网络的反向传播过程，需要理解梯度下降和链式法则（神经网络基础）。同时，Softmax函数、交叉熵损失函数和随机梯度下降（SGD）均是机器学习基础中的核心内容，直接用于Word2Vec的参数更新。负采样的推导还涉及最大似然估计的概念。

**延伸方向**：Word2Vec是静态词向量的代表。其直接后继是2014年斯坦福提出的**GloVe**（Global Vectors），它结合了全局词频共现矩阵与局部窗口方法，在词语类比任务上与Word2Vec性能相当但训练更稳定。更进一步的演进是基于Transformer的**BERT**和**GPT**系列，它们用多层自注意力机制生成上下文相关的动态词向量，彻底替代了Word2Vec在大多数NLP任务中的地位。理解Word2Vec的目标函数设计和负采样思想，也有助于理解后续**对比学习**（Contrastive Learning）中InfoNCE损失的设计逻辑。