---
id: "db-indexing"
concept: "索引原理与优化"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 6
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.364
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 索引原理与优化

## 概述

索引（Index）是数据库中用于加速数据检索的辅助数据结构，本质上是对表中一列或多列数据值的有序副本，并维护从索引值到实际行物理位置的映射。数据库在执行查询时，若无索引则需全表扫描（Full Table Scan），时间复杂度为 O(n)；而 B+Tree 索引将查找复杂度降至 O(log n)，对千万级数据表的查询可从秒级降至毫秒级。

索引最早随关系型数据库的发展而出现。1970 年 Edgar Codd 提出关系模型后，IBM System R 项目（1974–1979）便引入了 B-Tree 索引实现以支持 SQL 查询优化。现代主流数据库（MySQL InnoDB、PostgreSQL、Oracle）均以 B+Tree 为默认索引结构，同时支持哈希索引、GiST、GIN 等特殊类型。

索引对于 AI 工程中的数据库访问层至关重要：推荐系统的特征检索、向量数据库的近似最近邻查询、训练日志的时间范围扫描，都依赖正确的索引策略来满足低延迟要求。错误的索引设计会导致写入吞吐量崩溃或查询计划走错路径，因此索引优化是数据库调优中收益最高的单点工作。

---

## 核心原理

### B+Tree 索引的物理结构

MySQL InnoDB 的 B+Tree 索引由根节点、若干层内部节点和叶子节点组成。叶子节点按索引键值升序排列，并通过双向链表相连，这一结构使范围查询（`BETWEEN`、`>`、`<`）可以在定位到起始叶子节点后顺序扫描，无需回溯。内部节点只存储键值和子节点指针，不存储行数据，因此单个内部页（默认 16KB）可容纳数百个指针，使树高通常仅为 3–4 层，即查找任意行最多需要 3–4 次磁盘 I/O。

InnoDB 的**聚簇索引（Clustered Index）**将主键与实际行数据存储在同一棵 B+Tree 的叶子节点中，每张表仅有一个聚簇索引。**二级索引（Secondary Index）**的叶子节点存储的是索引列值加主键值，而非完整行数据，因此二级索引查询通常需要"回表"——用主键再次查询聚簇索引以获取完整行，产生两次 B+Tree 遍历。

### 覆盖索引与索引下推

**覆盖索引（Covering Index）**指查询所需的所有列均包含在索引本身中，无需回表。例如查询 `SELECT user_id, created_at FROM orders WHERE status = 'paid'`，若在 `(status, user_id, created_at)` 上建立复合索引，则该查询可直接从索引叶子节点返回结果，`EXPLAIN` 输出的 `Extra` 列会显示 `Using index`。覆盖索引在高频只读查询中可将 I/O 减少 50%–90%。

**索引条件下推（Index Condition Pushdown，ICP）**是 MySQL 5.6 引入的优化：存储引擎层在遍历索引时直接过滤不符合 WHERE 条件的行，避免将所有候选行回表后再在 Server 层过滤。对于选择性低的复合索引，ICP 可显著减少回表次数。

### 最左前缀原则与索引选择性

复合索引 `(a, b, c)` 遵循**最左前缀原则**：查询条件必须从最左列开始连续匹配，才能利用该索引。`WHERE a=1 AND b=2` 可用前两列；`WHERE b=2` 则完全无法使用此索引。设计复合索引时应将**选择性（Selectivity）**高的列放在前面，选择性 = `COUNT(DISTINCT col) / COUNT(*)`，取值越接近 1 说明区分度越高，索引过滤效果越好。性别列选择性约为 0.5，不适合单独建索引；用户 ID 选择性接近 1，非常适合。

### 哈希索引与 B+Tree 索引的场景差异

MySQL Memory 引擎和 PostgreSQL 支持哈希索引，查找时间复杂度为 O(1)，但哈希索引不支持范围查询、排序和前缀匹配，仅适合等值查询。Redis 内部的 Hash 表、向量数据库中的 HNSW（Hierarchical Navigable Small World）图索引均借鉴了哈希与图结构的优势，后者专门用于高维向量的近似最近邻检索，在 1 亿向量规模下可实现毫秒级响应，但牺牲了精确召回率（通常 recall@10 约 95%）。

---

## 实际应用

**AI 训练日志查询优化**：训练平台存储每个 step 的 loss、accuracy 等指标，查询模式为 `WHERE experiment_id = ? AND step BETWEEN ? AND ?`。正确做法是建立复合索引 `(experiment_id, step)`，利用最左前缀原则和 B+Tree 范围扫描特性，避免对 step 列单独建索引（因为 experiment_id 的过滤选择性更高）。

**推荐系统特征表的慢查询**：某推荐系统 `user_features` 表有 2 亿行，查询 `SELECT * FROM user_features WHERE city='Beijing' AND age_group='25-34'` 耗时 8 秒。分析发现 `city` 列仅有 300 个不同值，选择性极低。优化方案：改用 `(age_group, city)` 复合索引（`age_group` 有 10 个值，`city` 有 300 个值，组合选择性约为 3000 分之一），配合覆盖索引只取推荐所需列，查询降至 12 毫秒。

**写多读少场景的索引取舍**：实时竞价（RTB）系统的 bid_log 表每秒写入 10 万条记录，索引过多会导致每次 INSERT 需要更新多棵 B+Tree，写入延迟从 0.5ms 上升到 5ms。此类场景通常只保留主键索引和 1–2 个最关键的查询索引，并配合分区表或 LSM-Tree 引擎（如 TiKV、RocksDB）减轻写放大问题。

---

## 常见误区

**误区一：索引越多越好**。每个非聚簇索引都是独立的 B+Tree 结构，INSERT/UPDATE/DELETE 时数据库必须同步维护所有相关索引，导致写入成本随索引数量线性增加。InnoDB 对一张表建议不超过 16 个索引，超过会导致优化器在制定执行计划时评估成本过高。

**误区二：对 WHERE 中所有列都建单列索引可以替代复合索引**。当查询条件为 `WHERE a=1 AND b=2` 时，两个单列索引 `(a)` 和 `(b)` 最多触发 MySQL 的 Index Merge 优化，但 Index Merge 涉及两次索引扫描和位图合并，实际性能通常不如单个复合索引 `(a, b)`。`EXPLAIN` 中 `Extra` 显示 `Using intersect` 是 Index Merge 的标志，出现时应考虑改为复合索引。

**误区三：索引对 LIKE 查询总是有效**。B+Tree 索引对 `LIKE 'abc%'`（前缀匹配）有效，但对 `LIKE '%abc'`（后缀匹配）和 `LIKE '%abc%'`（中缀匹配）完全失效，因为后者无法利用 B+Tree 的有序性确定扫描起点，必须退化为全表扫描或改用全文索引（FULLTEXT Index）。

---

## 知识关联

索引原理依赖**数据库基本概念**中对页（Page）、Buffer Pool 缓冲池以及事务存储引擎的理解——例如 InnoDB 以 16KB 页为单位管理 B+Tree 节点，Buffer Pool 命中率直接影响索引扫描是否触发磁盘 I/O。

掌握索引后，**数据库锁机制**将变得更加清晰：InnoDB 的行锁实际上锁的是索引记录而非数据行本身，若查询条件列无索引，行锁会退化为表锁，并发性能骤降。**游标分页**替代 `LIMIT offset` 的核心也依赖索引的有序性，用 `WHERE id > last_id` 配合主键索引可将深翻页的 O(offset) 成本降至 O(1)。**全文搜索**则是 B+Tree 索引无法处理非结构化文本时的补充方案，使用倒排索引（Inverted Index）结构，与 B+Tree 的设计思路形成鲜明对比。