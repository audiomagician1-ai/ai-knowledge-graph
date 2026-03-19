---
id: "embedding-models"
name: "Embedding Models"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 6
tags: ["LLM", "NLP", "Embedding"]
generated_at: "2026-03-19T18:00:00"
---

# Embedding Models

## 概述

Embedding Models（嵌入模型）是将文本、图像等非结构化数据映射为稠密向量（dense vectors）的神经网络模型，难度等级 6/9。这些向量捕获了语义信息，使得语义相似的内容在向量空间中距离更近，是现代搜索、推荐、RAG 系统的基石。

本概念建立在 Transformer 架构和自注意力机制之上，与 RAG 管道、向量数据库、相似度搜索密切关联。

## 核心原理

### 从稀疏到稠密

```
稀疏表示 (Bag-of-Words / TF-IDF):
  "机器学习" → [0, 0, 1, 0, 0, 1, 0, ..., 0]   维度 ~50,000
  - 无法捕获语义相似性
  - "机器学习" 和 "深度学习" 完全正交

稠密表示 (Embedding):
  "机器学习" → [0.23, -0.51, 0.87, ..., 0.14]   维度 ~768
  "深度学习" → [0.21, -0.48, 0.85, ..., 0.16]   维度 ~768
  cos_similarity ≈ 0.95  ← 语义相近!
```

### 主流架构演进

| 阶段 | 代表模型 | 维度 | 特点 |
|:---|:---|:---:|:---|
| Word2Vec 时代 | Word2Vec, GloVe | 300 | 词级别，无上下文感知 |
| Sentence-BERT | SBERT (2019) | 768 | 首个高效句子级别 Embedding |
| E5 系列 | E5-base/large (2022) | 768/1024 | 统一 query/passage 前缀 |
| Instructor | Instructor-XL (2022) | 768 | 任务指令驱动 Embedding |
| 开源之巅 | BGE-M3 (2024) | 1024 | 多语言 + 多粒度 + 多功能 |
| API 级 | OpenAI text-embedding-3 | 256~3072 | 可变维度 (Matryoshka) |

### 训练范式

```python
# 对比学习 (Contrastive Learning) 核心训练范式
# 1. 正样本对: (query, relevant_doc)
# 2. 负样本: batch 内其他 doc (in-batch negatives) + hard negatives
# 3. 损失函数: InfoNCE Loss

def info_nce_loss(query_emb, pos_emb, neg_embs, temperature=0.05):
    """InfoNCE 对比学习损失"""
    pos_sim = cos_sim(query_emb, pos_emb) / temperature
    neg_sims = [cos_sim(query_emb, n) / temperature for n in neg_embs]
    
    # softmax 归一化: 正样本相似度 / (正 + 所有负)
    logits = [pos_sim] + neg_sims
    loss = -log(exp(pos_sim) / sum(exp(l) for l in logits))
    return loss
```

### Hard Negative Mining

普通负采样（随机文档）太容易区分，模型学不到细微差异。Hard negatives（难负样本）是与 query 语义接近但不相关的文档：

```
Query: "Python GIL 是什么"
Easy Negative: "今日天气预报"          ← 太简单
Hard Negative: "Python 多线程编程教程"  ← 相关但不直接回答
Positive:      "GIL 是 Global Interpreter Lock 的缩写..." ← 正确答案
```

## 关键技术

### Matryoshka Representation Learning (MRL)

```
传统模型: 固定 768 维输出，无法压缩
MRL 模型: 前 N 维也能用！

[d1, d2, ..., d256, ..., d512, ..., d768]
 ├── 256维: 适用于速度优先场景 (精度 ~95%)
 ├── 512维: 平衡方案 (精度 ~98%)
 └── 768维: 最高精度 (100% baseline)

训练时同时在 256/512/768 维度上计算 loss，
确保前缀子向量也是有意义的表示。
```

### 双编码器 vs 交叉编码器

```
双编码器 (Bi-Encoder):
  Query → Encoder → q_emb ─┐
                            ├→ cos_sim(q, d) → score
  Doc   → Encoder → d_emb ─┘
  优点: doc 可预计算/索引, 毫秒级检索
  缺点: 无 token 级交互, 精度有上限

交叉编码器 (Cross-Encoder):
  [CLS] Query [SEP] Doc [SEP] → Encoder → score
  优点: token 级深度交互, 精度最高
  缺点: 无法预计算, 每对都要过模型, 仅适合 Reranking
```

## 实际应用

### 选型指南

```python
# 使用 sentence-transformers 加载模型
from sentence_transformers import SentenceTransformer

# 中文场景推荐
model = SentenceTransformer('BAAI/bge-m3')  # 多语言首选

# 英文场景推荐
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# 轻量级场景
model = SentenceTransformer('all-MiniLM-L6-v2')  # 仅 80MB

# 编码
embeddings = model.encode(
    ["什么是机器学习", "深度学习入门"],
    normalize_embeddings=True  # 归一化后 cos_sim = dot product
)
```

### 评估指标

| 指标 | 含义 |
|:---|:---|
| MTEB (Massive Text Embedding Benchmark) | 56 个数据集综合排名 |
| NDCG@10 | 检索任务排序质量 |
| MAP | 检索任务平均精度 |
| Spearman Correlation | 语义相似度任务相关性 |

## 常见误区

1. **维度越高越好**：768 维和 3072 维在多数场景差异 <2%，但存储和计算成本翻倍
2. **忽略领域适配**：通用模型在垂直领域（法律/医疗）效果可能骤降，需要 fine-tune
3. **混用不同模型的向量**：不同模型的向量空间不兼容，不能混合检索
4. **忽略归一化**：不做 L2 归一化时，cos_sim 和 dot product 结果不同

## 与相邻概念关联

- **前置**: Transformer 架构、自注意力机制 — 理解 Encoder 的工作原理
- **下游**: 向量数据库 — 存储和检索 embedding 向量
- **应用**: RAG 管道 — embedding 是检索阶段的核心
- **互补**: Reranking — 双编码器粗筛 + 交叉编码器精排
- **进阶**: Fine-tuning — 领域适配 embedding 模型
