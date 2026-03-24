---
id: "db-replication"
concept: "数据库复制"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 7
is_milestone: false
tags: ["分布式"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 数据库复制

## 概述

数据库复制（Database Replication）是指将数据从一个数据库服务器（主节点，Primary/Master）自动同步到一个或多个其他数据库服务器（从节点，Replica/Slave）的机制。复制的本质是通过持续传输数据变更日志，使多个物理节点维护相同数据的一致副本，从而支撑高可用和读扩展两大核心需求。

数据库复制技术的工业化应用始于1990年代，MySQL在3.23版本（2000年）引入了基于二进制日志（Binary Log，binlog）的主从复制，奠定了现代关系型数据库复制的基础架构。PostgreSQL则在9.0版本（2010年）引入了流复制（Streaming Replication），以WAL（Write-Ahead Log）为传输载体，实现了更低延迟的物理复制。

在AI工程场景中，数据库复制的重要性体现在两个方面：其一，训练数据管道往往需要高频读取特征存储（Feature Store），复制架构允许多个从库分担读压力，避免单点成为I/O瓶颈；其二，在线推理服务要求数据库99.9%以上的可用性，主节点故障时从节点可以在秒级完成故障切换（Failover），保障服务连续性。

---

## 核心原理

### 复制日志的类型与传输机制

MySQL binlog记录的是已提交事务对数据的修改，以三种格式存在：**Statement**（记录SQL语句本身）、**Row**（记录行级数据变更，含before/after镜像）和**Mixed**（混合模式）。生产环境推荐使用Row格式，因为它对非确定性函数（如`NOW()`、`UUID()`）的复制是幂等的，不会产生主从数据不一致。

PostgreSQL的流复制使用WAL日志，主节点上的WAL Sender进程将WAL段（每段默认16MB）实时流式发送给从节点的WAL Receiver进程。从节点通过回放WAL日志完成数据同步，整个过程在物理块级别操作，与应用层SQL无关，因此复制延迟通常可控制在100ms以内。

### 同步复制 vs 异步复制

**异步复制**（Asynchronous Replication）是默认模式：主节点将事务写入本地日志后立即向客户端返回提交成功，不等待从节点确认。这意味着主节点崩溃时，最近已提交的部分事务可能**尚未传输到从节点**，造成数据丢失（RPO > 0）。

**同步复制**（Synchronous Replication）要求主节点等待至少一个从节点确认WAL已持久化后，才向客户端返回提交成功。PostgreSQL通过`synchronous_commit = on`开启此模式，MySQL通过`rpl_semi_sync_master_enabled`开启半同步（Semi-sync）复制。同步复制保证RPO = 0，但每次写操作的延迟会增加一次网络往返时间（通常增加1-5ms）。

选择依据：金融交易类数据需用同步复制保障零数据丢失；AI模型训练日志、用户行为埋点等允许少量丢失的场景可用异步复制换取写入吞吐。

### 复制延迟的成因与度量

复制延迟（Replication Lag）是指从节点比主节点落后的时间差，可用以下公式估算：

```
Lag ≈ (主节点写入速率 × 网络传输时间) + 从节点回放时间
```

MySQL通过`SHOW SLAVE STATUS`中的`Seconds_Behind_Master`字段度量延迟，但此值仅反映SQL线程的回放进度，当网络拥塞时会低估真实延迟。更精确的方式是在主库插入心跳时间戳，在从库读取后计算差值。

造成延迟的常见原因是**从节点单线程回放**（MySQL 5.6以前的默认行为）。从5.7版本起，MySQL引入了基于逻辑时钟（Logical Clock）的**并行复制**（MTS，Multi-Threaded Slave），允许不同数据库（Schema）或不同事务组的变更并发回放，可将复制延迟从秒级降低到毫秒级。

### 主从切换与数据一致性保障

故障切换时，若选出的新主节点复制延迟不为零，会产生**脑裂（Split-Brain）** 或**数据丢失**风险。GTID（Global Transaction Identifier，MySQL 5.6引入）通过为每个已提交事务分配全局唯一ID（格式：`server_uuid:transaction_id`），使新主节点能精确计算出自己比原主节点少了哪些事务，并通知其他从节点从正确位点重新同步，避免数据错乱。

---

## 实际应用

**读写分离架构**：电商平台的商品详情页查询量通常是写入量的10倍以上。通过在应用层或中间件（如ProxySQL、MyCat）配置读写分离规则，将`SELECT`路由到从库集群，将`INSERT/UPDATE/DELETE`路由到主库，可将主库CPU利用率从80%降低到20%以下。但需注意，对于"下单后立即查询订单状态"的场景，应强制将该查询路由到主库，避免因复制延迟导致用户看不到刚提交的订单。

**AI特征存储的多区域复制**：在跨地域部署的推荐系统中，模型推理服务需要低延迟读取用户实时特征。可将特征写入美国东区的主库，通过跨区域异步复制同步到亚太区从库，亚太区推理服务就近读取从库，将特征读取延迟从200ms（跨洋）降低到5ms（本地）。此场景下需接受最终一致性，容忍特征数据短暂落后主库数秒。

**灰度发布前的从库验证**：在数据库大版本升级（如MySQL 5.7升级到8.0）前，可先将一个从节点单独升级到新版本，观察其复制状态和查询性能，验证新版本兼容性，而不影响生产主库。

---

## 常见误区

**误区一：从库可随时用于数据备份**。从库虽然拥有与主库相同的数据，但它是一个实时变更的活动节点，直接对从库执行`mysqldump`时，若不加`--single-transaction`参数，备份期间的数据仍在变化，无法保证备份集的时间点一致性。正确做法是对从库加一致性锁（`FLUSH TABLES WITH READ LOCK`）或借助XtraBackup进行物理热备份，再结合数据库备份恢复流程使用。

**误区二：复制延迟=0意味着主从数据完全一致**。`Seconds_Behind_Master = 0`仅表示从库已赶上主库的binlog位点，但如果从库上存在人为执行的写操作，或者binlog格式为Statement模式下遇到非确定性函数，主从数据仍可能出现逻辑不一致。生产系统应定期使用`pt-table-checksum`工具对主从行数据进行校验，不一致时用`pt-table-sync`修复。

**误区三：增加从库数量可线性扩展写入能力**。从库仅能扩展读能力。所有从库都回放同一份主库产生的binlog，主库的写入吞吐上限不会因添加从库而提升。若需扩展写入能力，需引入分库分表或分布式数据库架构。

---

## 知识关联

**依赖前置概念**：数据库复制建立在ACID事务基础之上——复制单元是**已提交事务**（Committed Transaction），未提交的事务不会写入binlog或WAL，因此不会被传播到从节点。理解事务隔离级别（特别是`READ COMMITTED`与`REPEATABLE READ`对binlog格式的影响）是调优复制一致性的必要条件。

**衔接后续概念**：
- **分库分表**：单主库复制架构的写入扩展性受限于单节点CPU和磁盘，当写入QPS超过主库承载上限（通常为数万TPS）时，需要通过分库分表将数据水平拆分到多个独立的复制组（Shard），每个Shard内部仍使用主从复制保障高可用。
- **数据库备份恢复**：binlog本身是复制的传输媒介，同时也是时间点恢复（Point-in-Time Recovery，PITR）的关键依据。全量备份结合binlog增量回放，可将数据库恢复到任意精确的时间点，这是复制技术在灾难恢复领域的直接延伸。
