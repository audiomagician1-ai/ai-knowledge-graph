---
id: "full-text-search"
concept: "全文搜索"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["inverted-index", "elasticsearch", "tsvector"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
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


# 全文搜索

## 概述

全文搜索（Full-Text Search）是一种在文档集合中对任意词汇进行快速匹配和相关性排序的技术，区别于精确值查找（如 `WHERE status = 'active'`），它能处理自然语言中的模糊匹配、词形变化和相关性评分。全文搜索的本质问题是：在数百万文档中，如何在毫秒级别找到包含特定词汇的所有文档，并按相关程度排列结果。

全文搜索技术的工业化起点可追溯到 1990 年代，Doug Cutting 于 2000 年发布的 Apache Lucene 奠定了现代全文搜索引擎的核心架构基础。Elasticsearch 基于 Lucene 构建，于 2010 年发布，将分布式搜索能力封装为 REST API。PostgreSQL 则从 8.3 版本（2008年）开始内置 `tsvector` 和 `tsquery` 类型，支持本地全文检索而无需外部服务。

在 AI 工程场景中，全文搜索常用于 RAG（检索增强生成）系统的关键词检索环节，与向量相似度搜索形成互补——向量搜索擅长语义相似，全文搜索擅长精确词汇命中。两者混合的"混合检索"（Hybrid Search）是当前工程实践中的主流方案。

## 核心原理

### 倒排索引（Inverted Index）结构

倒排索引是全文搜索的核心数据结构，其构造逻辑与普通 B-Tree 索引完全不同。普通索引是"文档 → 词汇"的映射（给定一行数据，找到它的索引值），而倒排索引是"词汇 → 文档列表"的映射：

```
词汇       文档ID列表（Posting List）
"机器学习" → [doc3, doc7, doc12, doc45]
"深度学习" → [doc3, doc9, doc12]
"神经网络" → [doc1, doc9, doc45]
```

每条 Posting List 除文档 ID 外，还存储词频（Term Frequency, TF）和词在文档中的位置信息（用于短语匹配）。索引构建时，文本先经过分词器（Tokenizer）和过滤器（Filter）处理，例如英文文本会经历小写化、去除停用词（the/a/is）、词干提取（running → run）。

### TF-IDF 与 BM25 相关性评分

全文搜索返回结果需要按"相关性"排序，最基础的公式是 TF-IDF：

$$\text{score}(d,q) = \sum_{t \in q} \text{TF}(t,d) \times \text{IDF}(t)$$

其中 TF（词频）= 词 t 在文档 d 中出现的次数，IDF（逆文档频率）= $\log\frac{N}{df(t)}$，N 为总文档数，df(t) 为包含词 t 的文档数。常见词（如"的""是"）IDF 接近 0，罕见专业词汇 IDF 值高，自然获得更高权重。

Elasticsearch 7.0 起默认改用 BM25 算法，它修正了 TF-IDF 对长文档的偏向问题，引入了文档长度归一化参数 b（默认 0.75）和词频饱和参数 k1（默认 1.2）：

$$\text{BM25}(d,q) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{\text{TF}(t,d) \cdot (k_1+1)}{\text{TF}(t,d) + k_1 \cdot (1-b+b \cdot \frac{|d|}{\text{avgdl}})}$$

### 中文分词的特殊性

英文以空格天然分词，中文则需要专用分词器。Elasticsearch 中文环境需安装 `analysis-ik` 插件，提供两种分词模式：`ik_max_word`（最细粒度切分，"中华人民共和国"切成7个词）和 `ik_smart`（最粗粒度，保留"中华人民共和国"整体）。PostgreSQL 原生不支持中文分词，需借助 `zhparser` 扩展或在应用层预处理后存储 `tsvector`。分词质量直接决定召回率，错误的分词会导致用户搜索某词却无法找到包含该词的文档。

## 实际应用

### PostgreSQL 全文检索实践

PostgreSQL 使用 `tsvector` 存储预处理后的文档向量，`tsquery` 表示查询条件：

```sql
-- 创建文章表并添加全文搜索列
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- 更新向量（english 为分词配置）
UPDATE articles SET search_vector = to_tsvector('english', title || ' ' || body);

-- 创建 GIN 索引（适合全文搜索，比 GiST 更快）
CREATE INDEX articles_search_idx ON articles USING GIN(search_vector);

-- 执行搜索，@@ 为匹配操作符
SELECT title, ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'machine & learning') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

`GIN`（Generalized Inverted Index）是 PostgreSQL 内置的倒排索引实现，构建较慢但查询极快，适合写少读多的搜索场景。

### Elasticsearch 全文检索实践

```json
// 创建索引时定义中文分词映射
PUT /articles
{
  "mappings": {
    "properties": {
      "title": { "type": "text", "analyzer": "ik_max_word" },
      "body":  { "type": "text", "analyzer": "ik_smart" }
    }
  }
}

// 多字段全文检索，boost 提升 title 权重为 body 的2倍
GET /articles/_search
{
  "query": {
    "multi_match": {
      "query": "机器学习应用",
      "fields": ["title^2", "body"]
    }
  }
}
```

### RAG 系统中的混合检索

在 RAG 系统中，全文搜索负责精确关键词命中（如产品型号"GPT-4o"、人名、专有名词），向量搜索负责语义相似性。常用 RRF（Reciprocal Rank Fusion）算法合并两个结果列表：最终得分 = $\sum \frac{1}{k + r_i}$，其中 k=60 是常数，$r_i$ 是文档在各列表中的排名。Elasticsearch 8.9 版本起原生支持 `knn` 与 `query` 混合搜索。

## 常见误区

**误区1：用 LIKE 查询替代全文搜索**  
`WHERE content LIKE '%机器学习%'` 无法使用任何索引（除非使用 trigram 索引），在百万行数据上会触发全表扫描，查询时间从毫秒级退化到秒级。此外 LIKE 无相关性排序，无法处理词形变化（"run"无法匹配"running"）。全文搜索的倒排索引将这类查询降至 O(log N + output size) 复杂度。

**误区2：误以为 GIN 索引更新代价可忽略**  
GIN 索引写入时需要将新文档的每个词插入对应的 Posting List，更新一篇包含 500 个唯一词的文档会触发 500 次索引更新操作，写入放大显著。PostgreSQL 提供 `fastupdate` 参数（默认开启）通过缓冲区批量合并减少即时写入代价，但 `VACUUM` 时会有延迟合并开销。高频写入场景应评估是否改用 Elasticsearch 的 segment-based 架构。

**误区3：相关性评分等同于准确性**  
BM25 评分高的文档未必是用户真正需要的答案。例如一篇多次重复某词的低质量文章可能评分高于权威文档。工程实践中需结合业务信号（点击率、时间衰减、文档权威性）对原始 BM25 分数做重排（Re-ranking），Elasticsearch 提供 `function_score` 查询支持自定义评分函数。

## 知识关联

**依赖的前置概念**：本文的 GIN 索引构建逻辑直接扩展了**索引原理与优化**中的 B-Tree 和 Hash 索引知识——GIN 本质是对多值列的倒排索引，与普通单值列索引的存储结构完全不同。**SQL基础（CRUD）** 中的 `SELECT` 查询语法是理解 `@@` 操作符和 `ts_rank` 函数的基础，PostgreSQL 全文搜索语法在标准 SQL 之上扩展了专属操作符。

**横向关联**：全文搜索与向量数据库（pgvector、Pinecone）是 RAG 系统中并列的两条检索路径，理解全文搜索的词频相关性评分，有助于对比向量相似度（余弦相似度）的语义评分方式，两者在准确率与召回率上各有侧重，混合检索是工程中平衡两者的标准做法。