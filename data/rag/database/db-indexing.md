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
---
# 索引原理与优化

## 概述

数据库索引是一种单独存储的数据结构，其目的是将表中指定列的键值与对应行的物理存储位置（或主键）关联起来，从而将全表扫描（$O(n)$）转化为树形或哈希查找（$O(\log n)$ 或 $O(1)$）。索引的概念最早在1970年代的关系型数据库系统中系统化，IBM研究员 Rudolf Bayer 于1972年在论文 *Organization and Maintenance of Large Ordered Indices* 中正式提出了 B-树（B-Tree）结构，该结构至今仍是 MySQL InnoDB、PostgreSQL 等主流数据库的默认索引类型。

索引的存在使得百亿行级别的数据库能在毫秒内返回查询结果，但代价是每次写入（INSERT/UPDATE/DELETE）都需要同步维护索引结构，导致写入放大（Write Amplification）问题。正确理解索引的物理实现方式——而非仅停留在"索引使查询变快"这一层面——是数据库调优工程师区分 B-Tree 索引、Hash 索引、全文索引、空间索引适用场景的前提。

## 核心原理

### B-Tree 与 B+Tree 的物理结构差异

MySQL InnoDB 实际使用的是 B+Tree，而非原始 B-Tree。两者的关键区别在于：B-Tree 的每个节点（包括内部节点）都同时存储键值和数据指针；B+Tree 中内部节点仅存储键值用于路由，**所有数据指针只存在于叶子节点**，且叶子节点之间通过双向链表相连。这一设计使得范围查询（如 `WHERE age BETWEEN 20 AND 30`）只需找到起始叶子节点后沿链表顺序扫描，无需回溯树根，I/O 次数显著减少。

对于一个页大小为 16KB、键值为 8 字节 bigint、子节点指针为 6 字节的 InnoDB B+Tree，单个内部节点可以存放约 $\lfloor 16384 / (8+6) \rfloor = 1170$ 个索引项。一棵高度为 3 的树可以索引 $1170 \times 1170 \times 16 \approx 2190$ 万行数据，这解释了为什么 InnoDB 推荐主键使用自增整型——随机 UUID 主键会导致频繁的页分裂（Page Split），破坏 B+Tree 的有序性并产生大量碎片。

### 聚簇索引与非聚簇索引（回表问题）

InnoDB 中每张表有且只有一个聚簇索引（Clustered Index），默认为主键索引。聚簇索引的叶子节点直接存储完整的行数据，因此按主键查询无需额外 I/O。非聚簇索引（又称二级索引）的叶子节点存储的是**主键值**而非行数据地址，这意味着通过二级索引查找非索引列时必须先获取主键，再用主键到聚簇索引中检索完整行，这一过程称为**回表（Double Read）**。

回表的性能代价在高选择性查询中尤为明显。假设表有 1000 万行，通过二级索引查到 10000 个主键，每次回表都可能触发随机 I/O，最坏情况下需要 10000 次磁盘读取。解决方案是**覆盖索引（Covering Index）**：将查询所需的所有列都包含在索引中，使查询在遍历索引叶子节点时即可获取全部数据，`EXPLAIN` 输出的 `Extra` 列会显示 `Using index`。

### 索引选择性与基数

索引的有效性由**选择性（Selectivity）**决定，定义为 $S = \frac{N_{distinct}}{N_{total}}$，取值范围 $(0, 1]$。选择性越接近 1，索引过滤效果越好。Ramakrishnan 和 Gehrke 在《数据库管理系统》（*Database Management Systems*, 第三版）中指出，当索引列的选择性低于 0.2 时，查询优化器通常会放弃使用该索引而改用全表扫描，因为随机 I/O 的成本可能高于顺序全表扫描。

对于布尔列（gender: M/F）或低基数枚举列（status: 仅4个值），单列索引几乎无效。此时可考虑**复合索引（Composite Index）**，将低选择性列与高选择性列组合，如 `INDEX(status, user_id)` 可在 status 过滤后获得更高选择性。复合索引遵循**最左前缀原则**：索引 `(a, b, c)` 可以被查询 `WHERE a=1`、`WHERE a=1 AND b=2` 使用，但 `WHERE b=2 AND c=3` 无法利用该索引，因为跳过了最左列 a。

## 实际应用

### 慢查询分析与索引诊断

在 MySQL 中，通过 `EXPLAIN FORMAT=JSON` 可获得查询执行计划的详细 JSON 输出，关键字段包括 `access_type`（ALL=全表扫描，ref=索引查找，range=范围扫描）、`rows`（估算扫描行数）和 `filtered`（索引过滤后的行比例）。一个典型的优化场景：电商订单表有 5000 万行，查询 `SELECT * FROM orders WHERE user_id=123 AND status='paid' ORDER BY created_at DESC LIMIT 10` 在无索引时扫描全表耗时 8 秒，添加复合索引 `INDEX(user_id, status, created_at)` 后，因覆盖最左前缀并支持 ORDER BY 方向，查询耗时降至 2 毫秒。

```sql
-- 查看现有索引的使用情况（MySQL 5.7+）
SELECT 
    s.table_name,
    s.index_name,
    s.rows_selected,
    s.rows_inserted + s.rows_updated + s.rows_deleted AS write_ops
FROM performance_schema.table_io_waits_summary_by_index_usage s
WHERE s.object_schema = 'your_db'
  AND s.rows_selected = 0  -- 从未被SELECT使用过的索引
  AND s.index_name IS NOT NULL
ORDER BY write_ops DESC;
```

上述查询可以识别出"僵尸索引"——那些消耗写入性能却从未被读取利用的索引，是索引清理优化的第一步。

### PostgreSQL 中的部分索引与函数索引

PostgreSQL 支持**部分索引（Partial Index）**，即仅对满足特定条件的行建立索引。例如，订单表中 99% 的行状态为 `completed`，而业务查询几乎只针对 `status='pending'` 的行：

```sql
-- 仅对 pending 状态建立部分索引，索引体积缩小约 99%
CREATE INDEX idx_orders_pending 
ON orders(created_at) 
WHERE status = 'pending';
```

此索引体积约为全量索引的 1%，不仅节省存储，还因索引更小而能完整载入内存缓冲区，查询速度提升数倍。PostgreSQL 还支持**函数索引（Expression Index）**，如 `CREATE INDEX ON users(lower(email))` 使不区分大小写的邮箱查询可以走索引，而 MySQL 在 8.0 版本之前不支持函数索引，这是选型时的重要差异。

## 常见误区

**误区一：索引越多越好。** 每个索引都需要在磁盘上单独维护一棵 B+Tree，每次 INSERT 操作需要更新所有相关索引，在一个拥有 10 个索引的表上批量插入 100 万行数据的性能，可能比仅有主键索引时慢 5-10 倍。高写入场景下（如日志表、埋点表），冗余索引是常见的性能瓶颈来源。

**误区二：LIKE '%keyword%' 可以被索引加速。** B+Tree 索引依赖键值的有序性进行范围定位，前缀通配符 `%keyword%` 破坏了这一有序定位能力，优化器无法确定从哪个叶子节点开始扫描，因此退化为全索引扫描甚至全表扫描。仅有 `LIKE 'keyword%'`（后缀通配）才能利用 B+Tree 索引的前缀匹配，而 `%keyword%` 的搜索需要全文索引（如 MySQL 的 FULLTEXT 或 Elasticsearch）。

**误区三：查询条件中对索引列做函数运算，索引仍然有效。** `WHERE YEAR(created_at) = 2024` 会使 created_at 上的索引完全失效，因为数据库需要对每一行计算 `YEAR()` 后才能比较，相当于隐式破坏了索引列的原始顺序。正确写法是 `WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'`，保持索引列裸露（sargable 条件）。

## 思考题

1. 一张用户表有 `(id, age, city, score)` 四列，现有查询 `WHERE city='Beijing' AND age > 25 ORDER BY score DESC`。如果只能创建一个复合索引，你会选择 `(city, age, score)` 还是 `(city, score, age)`？请根据 B+Tree 的最左前缀原则和 ORDER BY 排序优化逻辑分析两者的执行计划差异。

2. InnoDB 的主键推荐使用自增 INT 而非 UUID，但分布式系统中自增主键会造成热点写入问题（所有写入集中在最右侧叶子节点）。Twitter 的 Snowflake 算法通过在 ID 高位嵌入时间戳来保持单调递增，同时避免全局锁。请思考：Snowflake ID 与纯随机 UUID 相比，在 B+Tree 页分裂频率上有何本质差异？

3. 已知某表有复合索引 `INDEX(a, b)`，查询 `SELECT b FROM t WHERE a = 1` 的 EXPLAIN 显示 `Extra: Using index`，而查询 `SELECT a, b, c FROM t WHERE a = 1` 显示 `Extra: NULL`（无覆盖索引）。如果将索引改为 `INDEX(a, b, c)`，两个查询的执行计划将如何变化？在实际生产环境中，为覆盖索引而额外添加列的决策应如何权衡维护成本与查询收益？
