---
id: "design-search-engine"
concept: "设计搜索引擎"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 5
is_milestone: false
tags: ["search", "inverted-index", "relevance"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.375
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 设计搜索引擎

## 概述

搜索引擎是一类接收用户查询词（Query），在海量文档集合中快速找出相关结果并按相关性排序返回的系统。其核心挑战在于：互联网文档规模可达数千亿页，单次搜索必须在200毫秒以内完成响应，这要求系统在存储、索引、查询三个维度同时做出高度专项的工程决策，而非通用数据库方案所能覆盖。

搜索引擎的工业化雏形可追溯至1990年代的Archie和AltaVista，但现代搜索引擎架构的奠基文献是2003年Google发布的《The Anatomy of a Large-Scale Hypertensive Web Search Engine》论文（通常称为"Google Architecture Paper"）。论文中描述的PageRank算法与分布式爬虫架构，确立了至今仍被广泛使用的搜索引擎三层结构：爬取层、索引层、查询服务层。

理解搜索引擎的设计价值在于：它集中体现了分布式系统中"写路径重、读路径快"的设计哲学——建索引可以耗费数小时乃至数天，但每次检索必须极速完成。这与通用数据库的OLTP设计目标截然不同，是一类专为高频读、低延迟场景深度优化的系统架构。

---

## 核心原理

### 1. 倒排索引（Inverted Index）

倒排索引是搜索引擎实现快速全文检索的基础数据结构。与正向索引（文档→词语列表）相反，倒排索引维护的是**词语→文档列表**的映射关系。具体结构包含两部分：

- **词典（Lexicon / Dictionary）**：存储所有出现过的词项（Term），通常使用哈希表或B树实现，支持O(1)或O(log n)查找。
- **倒排列表（Posting List）**：每个词项对应一条倒排列表，记录包含该词项的所有文档ID（DocID）以及词项在该文档中的出现频次（TF，Term Frequency）和位置信息。

例如，对于两个文档：
- Doc1: "机器学习系统设计"
- Doc2: "系统设计入门"

词项"系统设计"的倒排列表为：`{Doc1: [pos=3], Doc2: [pos=1]}`

在工程实现上，倒排列表通常以**Delta编码（差分编码）**压缩DocID序列，再用VByte（Variable Byte Encoding）进一步压缩，可将存储空间缩减至原始大小的10%~20%。Lucene（Elasticsearch的底层引擎）使用的是跳表（Skip List）结构加速多个倒排列表的归并操作（AND/OR查询）。

### 2. 分词（Tokenization）与文本预处理

分词将原始文本分割为可索引的词项单元。中文分词因缺乏天然空格分隔符，需要专用算法：

- **正向最大匹配（Forward Maximum Matching）**：从左到右贪婪匹配词典中最长词汇，时间复杂度O(n×max_word_len)。
- **基于统计的分词（如HMM、CRF）**：将分词建模为序列标注问题，在歧义消解上优于规则方法。jieba分词库使用的是基于前缀词典的有向无环图（DAG）结合动态规划求最大概率路径。

文本预处理流水线通常包括：去除停用词（如"的"、"了"、"是"，约200~500个高频无意义词）→词干提取或词形还原（英文场景用Porter Stemmer，将"running"归一化为"run"）→大小写归一化→同义词扩展。

这些预处理操作在**建索引时**和**查询时**均需对称执行，否则查询词与索引词项无法匹配。

### 3. 相关性排序：TF-IDF与BM25

经典相关性评分公式**TF-IDF**定义如下：

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\frac{|D|}{\text{DF}(t)}$$

其中，TF(t,d)为词项t在文档d中的出现次数，|D|为语料库总文档数，DF(t)为包含词项t的文档数。IDF部分惩罚高频通用词（如"的"），奖励低频专有词（如"BM25"）。

现代搜索引擎普遍使用**BM25**（Best Match 25）替代纯TF-IDF，其评分公式为：

$$\text{BM25}(t, d) = \text{IDF}(t) \times \frac{\text{TF}(t,d) \times (k_1 + 1)}{\text{TF}(t,d) + k_1 \times (1 - b + b \times \frac{|d|}{\text{avgdl}})}$$

其中超参数通常取 $k_1 \in [1.2, 2.0]$，$b = 0.75$；|d|为文档长度，avgdl为语料库平均文档长度。BM25对文档长度做了归一化处理，避免长文档仅因词项重复次数多而虚高评分。

除文本相关性外，Google的**PageRank**算法通过链接图的随机游走计算页面权威性得分：$PR(A) = \frac{1-d}{N} + d \sum_{i} \frac{PR(T_i)}{C(T_i)}$，其中d为阻尼系数（取0.85），N为总页面数，C(Ti)为页面Ti的出站链接数。

### 4. 网络爬虫架构

爬虫（Crawler）负责持续抓取互联网页面，是搜索引擎数据来源层。其核心组件包括：

- **URL Frontier（URL前沿队列）**：使用优先队列管理待抓取URL，按域名限速（Politeness Policy），通常对同一域名的请求间隔不少于1秒，遵循robots.txt协议。
- **去重模块**：已抓取URL去重使用**Bloom Filter**（布隆过滤器），以极低内存代价（每个URL约10 bits）实现约1%误判率的集合成员测试，避免重复抓取数十亿已见URL。
- **分布式调度**：工业级爬虫（如Googlebot）将URL空间按域名或URL哈希值分片，分配给数千台爬虫Worker节点并行抓取，每天可新抓取数十亿页面。
- **内容去重**：使用**SimHash**算法计算页面指纹（64位哈希），汉明距离小于3的页面视为近似重复，防止镜像站污染索引。

---

## 实际应用

**构建电商商品搜索系统**是搜索引擎设计的典型落地场景。以某电商平台为例，商品库存量约5000万条SKU，要求按用户查询返回相关商品并支持价格、品牌等多维过滤。

在索引设计上，需对商品标题、品牌、类目、用户评价分别建立字段级倒排索引，并在评分公式中引入**商品销量**和**点击率（CTR）**作为额外信号，与BM25文本得分加权融合：$\text{Final Score} = \alpha \cdot \text{BM25} + \beta \cdot \log(\text{sales}+1) + \gamma \cdot \text{CTR}$。参数α、β、γ通过线下A/B实验或Learning to Rank（LambdaMART等）模型自动学习。

在架构层面，查询流量通过**分片索引（Sharded Index）**分散到多个节点，每个节点负责总商品库的1/N子集；**副本（Replica）**节点承担读流量，实现高可用。索引更新（新商品上架）通过增量索引而非全量重建，保证近实时可见（延迟通常在1~5分钟级别）。

---

## 常见误区

**误区一：将搜索引擎当成数据库的全文检索功能的等价物**

MySQL的FULLTEXT索引与专用搜索引擎（Elasticsearch）之间存在本质差距。MySQL FULLTEXT在数千万行数据时查询延迟可达秒级，且不支持BM25、分片扩展、自定义分析器等特性。搜索引擎通过倒排索引的离线构建与查询时的候选集剪枝（Early Termination），将百亿文档的检索压缩到毫秒级——这是关系数据库行存储结构无法复制的能力。

**误区二：认为索引越新鲜越好，应追求实时全量索引更新**

实时全量重建索引的代价极高。工业实践中，搜索引擎通常采用**分层索引策略**：高频变化内容（如新闻）使用增量索引（分钟级刷新），主体内容使用每日或每周全量合并（Segment Merge）。Elasticsearch的`refresh_interval`默认为1秒，但在批量写入场景下建议调整为30s甚至-1（手动刷新），以避免频繁段合并拖慢写入吞吐。

**误区三：相关性排序等同于关键词命中次数排序**

单纯按关键词出现频次排序会导致"关键词堆砌"作弊（Keyword Stuffing）问题。BM25通过文档长度归一化抑制了TF饱和效应，PageRank从链接图引入了权威性信号，而现代搜索引擎还会融合**用户行为信号**（点击率、停留时长、跳出率）和**语义相似度**（BERT等向量检索）。这些多路