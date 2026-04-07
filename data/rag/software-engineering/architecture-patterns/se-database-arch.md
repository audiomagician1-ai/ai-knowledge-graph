---
id: "se-database-arch"
concept: "数据库架构"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 3
is_milestone: false
tags: ["数据"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 数据库架构

## 概述

数据库架构是指在软件系统中组织、存储和访问数据的整体方案，具体涵盖数据库类型选择（SQL 或 NoSQL）、数据模型设计、以及在高并发/大数据场景下的分库分表策略。一个数据库架构决策的错误往往是系统性的，在业务规模扩大后极难回滚，因此比大多数代码层面的决策影响更深远。

关系型数据库（RDBMS）的历史可追溯到 1970 年 Edgar Codd 在 IBM 发表的论文《A Relational Model of Data for Large Shared Data Banks》，奠定了以表、行、列为基础的 SQL 体系。NoSQL 概念则在 2009 年前后随着 Google Bigtable（2006）和 Amazon Dynamo（2007）论文的公开而进入主流，直接催生了 Cassandra、MongoDB、Redis 等产品，用以应对关系型数据库在水平扩展上的局限。

数据库架构的重要性体现在：单表数据超过 1000 万行时，MySQL 的 B+ 树索引层数增加会导致查询时间显著上升；不合理的 NoSQL 选型会带来事务一致性缺失；而不合理的分表策略会让跨分片查询的性能比单库更差。因此理解不同方案的适用边界是系统设计的基础能力。

---

## 核心原理

### SQL 与 NoSQL 的本质区别

SQL 数据库以 ACID（原子性 Atomicity、一致性 Consistency、隔离性 Isolation、持久性 Durability）为设计目标，使用预定义 Schema，通过外键和 JOIN 操作维护数据关系。典型代表 MySQL、PostgreSQL、Oracle。

NoSQL 数据库按数据模型分为四大类：
- **文档型**（MongoDB）：以 JSON/BSON 文档存储，适合结构频繁变更的业务数据；
- **键值型**（Redis）：O(1) 时间复杂度的查找，适合缓存和会话数据；
- **宽列型**（Cassandra、HBase）：以列族组织数据，写入吞吐量极高，适合时序或日志数据；
- **图数据库**（Neo4j）：以节点和边表示关系，适合社交网络、推荐系统等强关系场景。

NoSQL 普遍遵循 BASE 理论（基本可用 Basically Available、软状态 Soft state、最终一致性 Eventually consistent），以牺牲强一致性换取水平扩展能力。CAP 定理（Consistency、Availability、Partition tolerance 三者只能同时满足两项）是 NoSQL 选型的核心理论依据。

### SQL/NoSQL 选型决策框架

选型时需要回答以下几个具体问题：

1. **事务需求**：业务涉及资金、订单等多表联动操作，必须选择支持 ACID 的 SQL 数据库。电商订单扣减库存 + 创建订单 + 扣减余额三步必须原子完成，MongoDB 的多文档事务虽在 4.0 版本后支持，但性能开销明显高于 MySQL InnoDB 引擎的原生事务。

2. **数据结构稳定性**：用户行为日志、商品 SPU 属性等字段差异极大的数据，使用 MongoDB 的动态 Schema 比在 MySQL 中频繁执行 `ALTER TABLE` 添加字段的代价更低（MySQL 大表 `ALTER TABLE` 可能导致数秒至数分钟的锁表）。

3. **读写比例与延迟要求**：读多写少且对延迟敏感（<1ms）的场景用 Redis；写多读少的日志归档场景用 Cassandra，其写入吞吐量可达单节点每秒数万次。

4. **数据规模预期**：预计未来 3 年内数据量不超过 5000 万行的业务，MySQL 单库可完全胜任，无需引入 NoSQL 增加运维成本。

### 分库分表策略

当 MySQL 单表行数超过 **2000 万行**，或单库 QPS 超过 **5000** 时，通常需要考虑分库分表。

**垂直分库**：按业务模块将不同的表拆分到独立数据库，例如将用户库（user_db）、订单库（order_db）、商品库（product_db）分别部署。垂直分库降低了单库的连接数压力，但不解决单表数据量过大的问题。

**水平分表（Sharding）**：将同一张表的数据按某个字段值分散到多个物理表中。常见的分片键选择策略：
- **Hash 取模**：`shard_id = user_id % N`，数据分布均匀，但扩容时需要重新 rehash，迁移成本高；
- **Range 分片**：按时间或 ID 范围划分，如每月一个分片，扩容简单，但可能存在热点（最新月份的写入集中在一个分片）；
- **一致性哈希**：在扩容时只需迁移约 `1/N` 的数据，Cassandra 和 DynamoDB 均采用此方案。

分库分表的代价包括：跨分片 JOIN 不可用（需在应用层聚合）、全局唯一 ID 不能再依赖数据库自增主键（需引入雪花算法 Snowflake 或 UUID）、分布式事务复杂度显著增加。

---

## 实际应用

**电商平台订单系统**：订单表按 `user_id` 进行 Hash 分表，分为 1024 个逻辑表，分布在 8 个物理数据库实例中，每个实例 128 张表。用户查询自己的订单列表走 `user_id` 路由直达单分片，性能与单表一致。但"按商家查询所有订单"这类运营需求，因为商家 ID 不是分片键，需要扫描所有分片后汇总，通常通过异步同步到 Elasticsearch 来解决。

**社交平台用户 Feed 流**：用户发布的内容存 MySQL（需要事务保障），Feed 流的关注关系存 Redis 的 Sorted Set（以时间戳为 score），用户刷新 Feed 时直接从 Redis 读取最近 200 条，延迟控制在 5ms 以内。历史数据冷归档至 HBase 按时间范围查询。

**实时日志分析**：Kafka 接收每秒百万级日志写入后，由 Flink 消费写入 Cassandra（利用其高写入吞吐）；离线分析需求走 Hive/Spark 查询 HDFS 上的归档数据，而非直接查 Cassandra，避免分析查询影响线上写入性能。

---

## 常见误区

**误区一：NoSQL 比 SQL 更"先进"，新项目应默认选 NoSQL**
MongoDB 和 Redis 解决的是特定问题，不是 MySQL 的升级版。许多初创项目在业务模型尚未稳定时选择 MongoDB，反而因为缺乏 Schema 约束导致数据质量混乱。PostgreSQL 的 JSONB 类型支持既保留了事务能力，也支持半结构化数据存储，在数据量不超过 1 亿行的场景下常常是更务实的选择。

**误区二：分库分表越早做越好**
分表会引入全局 ID 生成、分布式事务、跨分片查询等一系列复杂性，且中间件（如 ShardingSphere）本身有学习和运维成本。MySQL 单表在有合理索引的情况下，支撑 5000 万行、每秒数千次 QPS 是完全可行的。过早分表是典型的过度设计，会将一个简单系统变得难以调试。

**误区三：分表的分片键可以随意选择**
分片键一旦确定几乎无法更改，因为现有数据的物理位置与分片键强绑定。以 `created_at` 时间戳作为分片键会导致所有新写入永远集中在最新分片（热点问题），造成各分片负载严重不均衡。分片键应选择基数（Cardinality）高、分布均匀、且业务查询必须携带的字段，通常是用户 ID 或租户 ID。

---

## 知识关联

**与缓存架构的关系**：Redis 在数据库架构中通常作为 MySQL 的缓存层使用，而非替代品。常见的 Cache-Aside 模式是：读请求先查 Redis，Miss 后查 MySQL 并回填缓存；写请求先更新 MySQL，再删除 Redis 缓存（而非更新，以避免并发写导致的缓存与数据库不一致）。

**与微服务架构的关系**：微服务要求每个服务拥有独立数据库（Database per Service 模式），这天然对应垂直分库的思路。但跨服务的数据一致性不能依赖数据库事务，需要使用 Saga 模式或最终一致性消息方案替代。

**与读写分离的关系**：读写分离是在分库分表之前优先考虑的扩展手段，通过 MySQL 主从复制，将读流量路由至从库，在读多写少（读写比超过 4:1）的场景下，可以将数据库读取 QPS 线性扩展，且架构复杂度远低于分库分表。