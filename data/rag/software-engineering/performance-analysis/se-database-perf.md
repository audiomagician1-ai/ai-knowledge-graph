---
id: "se-database-perf"
concept: "数据库性能"
domain: "software-engineering"
subdomain: "performance-analysis"
subdomain_name: "性能分析"
difficulty: 3
is_milestone: false
tags: ["数据库"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 数据库性能

## 概述

数据库性能是指数据库管理系统（DBMS）在执行查询、插入、更新、删除等操作时的速度与资源利用效率，通常以查询响应时间（毫秒级）、每秒事务数（TPS）和吞吐量（QPS）作为核心度量指标。数据库性能瓶颈是生产系统中最常见的性能问题来源之一——据统计，超过70%的应用程序慢查询根源在于缺失索引或低效SQL。

现代关系型数据库（如MySQL 5.7+、PostgreSQL 14、Oracle 21c）都内置了查询优化器（Query Optimizer），其工作原理是在SQL执行前将用户提交的查询语句转化为代价最低的执行计划。1970年代IBM的System R项目首次引入了基于成本的查询优化（Cost-Based Optimization, CBO），奠定了此后五十年关系型数据库性能优化的理论基础。

数据库性能直接影响用户体验与系统可用性。一条没有索引支撑的全表扫描（Full Table Scan）在千万行数据规模下可能耗时数十秒，而添加合适的B+树索引后同一查询往往可缩短至毫秒级别。理解索引结构、执行计划和查询重写，是开发者进行有效数据库调优的基础技能。

---

## 核心原理

### 索引结构与B+树

关系型数据库最常用的索引结构是**B+树（B+ Tree）**，其中所有实际数据记录存储在叶子节点，内部节点只存储键值用于导航。B+树的高度通常为3～4层，即使面对亿级数据也只需3～4次磁盘I/O即可定位目标记录。对比之下，无索引的全表扫描对于1000万行、每行100字节的表，需要读取约1GB数据。

MySQL InnoDB引擎使用**聚簇索引（Clustered Index）**，表数据按主键顺序物理存储，主键查找无需额外回表（Table Lookup）。非主键列创建的**二级索引（Secondary Index）**的叶子节点存储的是主键值而非完整行数据，因此二级索引查询往往需要一次额外的主键回表操作，这是"覆盖索引（Covering Index）"优化的出发点——当SELECT字段全部包含在索引列中时，可以避免回表，极大提升查询效率。

索引并非越多越好。每个写入操作（INSERT/UPDATE/DELETE）都需要同步维护所有索引，索引数量过多会显著降低写入吞吐量。一般建议单表索引不超过6个，并优先为高选择性（Cardinality高）的列创建索引。

### 执行计划分析

执行计划（Execution Plan）是数据库查询优化器为某条SQL生成的具体操作步骤序列。在MySQL中使用 `EXPLAIN` 或 `EXPLAIN ANALYZE` 命令查看，PostgreSQL同样支持 `EXPLAIN (ANALYZE, BUFFERS)` 输出详细的实际执行统计。

执行计划中最关键的字段是：

- **type**（MySQL）：访问类型，从最优到最差依次为 `const` → `ref` → `range` → `index` → `ALL`。出现 `ALL` 表示全表扫描，是性能预警信号。
- **rows**：优化器估算需要扫描的行数，与实际行数偏差过大说明统计信息（Statistics）过时，需执行 `ANALYZE TABLE` 更新。
- **Extra**：包含 `Using index`（覆盖索引）、`Using filesort`（需要额外排序，可能很慢）、`Using temporary`（使用临时表）等重要提示。

当优化器选择了非预期的执行计划时，可能原因是统计信息不准确或索引选择性不足。PostgreSQL提供 `pg_stats` 视图查看列的统计直方图，MySQL可通过 `SHOW INDEX` 查看各索引的 Cardinality 值。

### 查询优化技术

**查询重写**是在不改变结果语义的前提下，将低效SQL转化为高效SQL。常见的重写场景包括：

1. 将 `SELECT *` 改为只查询需要的列，减少网络传输和内存占用。
2. 避免在WHERE条件的索引列上使用函数，例如 `WHERE YEAR(create_time) = 2023` 会导致索引失效，应改为 `WHERE create_time BETWEEN '2023-01-01' AND '2023-12-31'`。
3. 用 `EXISTS` 替代 `IN` 处理大子查询，因为 `EXISTS` 在找到第一条匹配记录后即停止扫描。

**联合索引（Composite Index）**遵循**最左前缀原则**：索引 `(a, b, c)` 可以支持 `WHERE a=1`、`WHERE a=1 AND b=2` 的查找，但无法支持单独 `WHERE b=2` 的索引扫描。设计联合索引时，应将等值查询列放在前面，范围查询列放在最后。

**慢查询日志（Slow Query Log）**是发现性能问题的主要入口。MySQL通过设置 `long_query_time=1`（秒）记录超过阈值的查询，配合 `pt-query-digest` 工具可以按查询频率和累计耗时排序，快速定位Top-N慢SQL。

---

## 实际应用

**电商订单查询场景**：假设订单表（orders）有5000万行，需要查询某用户的最近100条订单。未优化的SQL `SELECT * FROM orders WHERE user_id=12345 ORDER BY create_time DESC LIMIT 100` 若无索引，`EXPLAIN` 将显示 `type=ALL, rows=50000000`。添加联合索引 `(user_id, create_time)` 后，执行计划变为 `type=ref, rows=约100`，查询时间从8秒降至2毫秒。

**分页查询深翻页问题**：`LIMIT 1000000, 20` 这类深翻页SQL即使有索引也会扫描100万行再丢弃，性能极差。优化方案是使用"游标分页"——记录上一页最后一条记录的主键ID，改写为 `WHERE id > last_id LIMIT 20`，将扫描行数从百万降至20行。

**数据库连接池**：在高并发场景下，每次查询新建TCP连接的开销可达10～50ms，使用连接池（如HikariCP的最大连接数设置为 `maximumPoolSize=10`）复用连接，可将连接获取时间降至微秒级。

---

## 常见误区

**误区一：索引越多，查询越快。** 很多开发者为每个查询条件单独创建索引，导致单表索引达到十几个。实际上，写操作（如高频INSERT的日志表）需要维护所有索引，索引过多会使写入TPS下降50%以上。正确做法是分析查询模式，用联合索引替代多个单列索引。

**误区二：EXPLAIN显示"Using index"就说明查询很快。** `Using index` 表示使用了覆盖索引，但如果 `rows` 估算值仍然很大（例如范围扫描50万行），查询依然可能很慢。需要结合 `rows` 和实际查询时间综合评估，`EXPLAIN ANALYZE` 可以显示实际扫描行数与估算值的对比。

**误区三：加了索引后立刻生效且统计信息准确。** 在MySQL和PostgreSQL中，新建索引后优化器依赖统计信息决定是否使用该索引。当表数据发生大量变化（如批量导入数据）后，旧的统计信息可能导致优化器做出错误决策，此时需手动执行 `ANALYZE TABLE tablename`（MySQL）或 `VACUUM ANALYZE tablename`（PostgreSQL）强制更新统计信息。

---

## 知识关联

**与操作系统I/O的关系**：数据库性能本质上受限于磁盘随机I/O速度。机械硬盘（HDD）的随机读IOPS约为100～200，而NVMe SSD可达50万IOPS。B+树索引减少I/O次数的设计，正是针对磁盘随机访问的高延迟特性。

**与SQL语言的关联**：SQL的 `JOIN`、`GROUP BY`、`ORDER BY` 等操作直接映射为执行计划中的哈希连接（Hash Join）、聚合（Aggregation）、排序（Sort）等算子，理解这些SQL语句的执行代价，有助于在编写SQL时主动规避高代价操作。

**通向分布式数据库**：单机数据库性能优化学会后，可进一步学习分库分表（Sharding）和分布式SQL（如TiDB、CockroachDB），这些系统在单机查询优化基础上引入了分布式执行计划，涉及数据本地性（Data Locality）和跨节点数据传输代价的新维度。