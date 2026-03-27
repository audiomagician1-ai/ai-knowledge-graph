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

全文搜索（Full-Text Search）是一种在文档集合中检索包含特定词语或短语的技术，其核心在于**倒排索引（Inverted Index）**——将文档中每个词映射到包含该词的文档列表，而非像传统B树索引那样以行为单位存储数据。这种结构使得"找出所有包含'机器学习'的文档"从全表扫描O(n)降低到索引查询O(log n + k)，其中k是匹配文档数量。

全文搜索技术的工业化起点可以追溯到1999年Lucene项目的诞生（作者Doug Cutting），随后2004年Solr、2010年Elasticsearch相继出现，将倒排索引封装为分布式服务。与此同时，PostgreSQL在8.3版本（2008年）引入了内置的`tsvector`/`tsquery`类型，使关系型数据库也能原生支持全文检索，无需引入额外中间件。

在AI工程的向量数据库场景出现之前，全文搜索长期是语义检索的主要手段。即便今天向量检索大行其道，BM25算法（全文搜索的经典排序函数）与向量相似度的混合检索（Hybrid Search）仍是RAG系统中提升召回率的标准做法。

---

## 核心原理

### 倒排索引的构建过程

倒排索引由两部分组成：**词典（Dictionary）**和**倒排列表（Posting List）**。构建时，每篇文档经过以下文本分析流水线：

1. **分词（Tokenization）**：将"自然语言处理很有趣"切分为`["自然语言", "处理", "很", "有趣"]`
2. **归一化（Normalization）**：大小写统一、去除标点
3. **停用词过滤（Stop Word Removal）**：移除"的""是""很"等高频无意义词
4. **词干提取/词形还原（Stemming/Lemmatization）**：英文中将"running"→"run"

最终词典中每个词条对应一条倒排列表，格式为`词 → [(文档ID, 词频, 位置列表), ...]`。例如：

```
"机器学习" → [(doc3, 5, [12,45,78,102,134]), (doc7, 2, [3,29])]
```

### BM25排序算法

全文搜索不仅要找到匹配文档，还要按相关性排序。BM25（Best Match 25）是目前最主流的排序公式，定义如下：

$$\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$$

其中：
- $f(q_i, D)$：词$q_i$在文档$D$中的词频
- $|D|$：文档$D$的长度（词数）
- $\text{avgdl}$：语料库平均文档长度
- $k_1$：词频饱和参数，通常取**1.2**，控制词频增益的上限
- $b$：长度惩罚参数，通常取**0.75**，防止长文档因词多而占优
- $\text{IDF}(q_i)$：逆文档频率，惩罚过于普遍的词

BM25在2000年代取代了早期的TF-IDF，Elasticsearch 5.0（2016年）将默认相似度算法从TF-IDF切换至BM25。

### PostgreSQL全文检索实现

PostgreSQL使用`tsvector`存储已分析的文档向量，用`tsquery`表达查询条件。典型用法如下：

```sql
-- 创建tsvector列并建立GIN索引
ALTER TABLE articles ADD COLUMN search_vector tsvector;
UPDATE articles SET search_vector = to_tsvector('chinese', content);
CREATE INDEX idx_articles_fts ON articles USING GIN(search_vector);

-- 执行全文搜索并按相关性排序
SELECT title, ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('chinese', '机器学习 & 神经网络') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

PostgreSQL的GIN（Generalized Inverted Index）正是倒排索引的关系型数据库实现。`@@`操作符在内部将`tsquery`与`tsvector`进行交集查询，时间复杂度取决于GIN树的深度而非表行数。

### Elasticsearch的分布式全文搜索

Elasticsearch基于Lucene，将索引分片（Shard）分布在多个节点。每个分片是一个独立的Lucene索引，包含完整的倒排索引结构。查询时采用**scatter-gather**模式：协调节点将查询广播到所有相关分片，各分片返回本地Top-K结果，协调节点再做全局归并排序。

Elasticsearch的分析器（Analyzer）由三部分组成：Character Filters → Tokenizer → Token Filters，中文场景通常使用`ik_max_word`分析器（IK Analyzer），支持细粒度分词，将"中华人民共和国"切分为`["中华人民共和国","中华人民","中华","华人","人民共和国","人民","共和国","共和","国"]`。

---

## 实际应用

**RAG系统中的混合检索**：在构建检索增强生成（RAG）管道时，单纯向量检索会漏掉精确关键词匹配（如产品型号"GPT-4o"、专有名词），而纯全文搜索无法处理语义近似。实践中使用RRF（Reciprocal Rank Fusion）算法合并两路结果：`RRF_score = 1/(k+rank_vector) + 1/(k+rank_bm25)`，其中k通常取60，平衡两路排名贡献。

**电商商品搜索**：对商品标题、描述、规格建立多字段全文索引。Elasticsearch的`multi_match`查询可对不同字段设置权重提升（boost），例如标题字段boost=3，描述字段boost=1，使标题中出现搜索词的商品排名更靠前。

**日志分析**：将Nginx/应用日志写入Elasticsearch，对`message`字段建立全文索引，通过`match_phrase`查询精确匹配错误堆栈信息，比正则表达式扫描原始日志快3-10倍。

---

## 常见误区

**误区一：`LIKE '%keyword%'`等同于全文搜索**

`LIKE '%keyword%'`无法利用任何索引（前导通配符导致全表扫描），时间复杂度为O(n×m)，其中m为关键词长度。全文搜索通过倒排索引将检索复杂度与表大小解耦。在一个1000万行的文章表上，`LIKE`查询可能耗时数十秒，而GIN索引的全文查询通常在100毫秒内完成。

**误区二：中文不需要配置分词器**

英文可以按空格分词，但中文字符之间无分隔符，PostgreSQL默认的`english`配置无法正确处理中文，会将整段中文视为单一词元，导致索引形同虚设。必须安装中文分词扩展（如`zhparser`对应PostgreSQL，`ik_analyzer`对应Elasticsearch）并在创建索引时显式指定，否则`to_tsvector('chinese', '机器学习')`会退化为字符级索引。

**误区三：全文搜索能替代向量搜索处理语义查询**

BM25本质是统计词频匹配，无法处理同义词（"汽车"≠"轿车"）和语义近似（"手机发热"≠"手机温度过高"）。全文搜索擅长精确词汇匹配、速度快、资源消耗低；向量搜索擅长语义理解但延迟较高。两者互补而非替代关系。

---

## 知识关联

**与索引原理的衔接**：学习B树索引和哈希索引后，倒排索引是第三种核心索引结构，专为文本多值映射设计。GIN索引是PostgreSQL中倒排索引的通用实现，理解B树索引的页分裂机制有助于理解GIN索引为何写入成本更高（需维护更多倒排列表项）。

**与SQL基础的衔接**：PostgreSQL全文搜索通过`@@`操作符和`to_tsvector()`/`to_tsquery()`函数嵌入标准SQL查询，`ts_rank()`用于ORDER BY子句中的相关性排序，这些都是SQL函数和操作符的直接应用。掌握`CREATE INDEX`语法后，`CREATE INDEX ... USING GIN`是其参数扩展。

**向量数据库的前置背景**：理解BM25的词频统计局限性，是理解为何需要将文本转化为稠密向量（Dense Embedding）的动机所在。Elasticsearch 8.0引入的`knn`向量字段和全文搜索字段共存于同一索引，正是混合检索架构在工程上的体现。