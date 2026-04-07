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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 数据库复制

## 概述

数据库复制（Database Replication）是指将一个数据库（称为主库，Primary/Master）的数据变更自动同步到一个或多个其他数据库（称为从库，Replica/Slave）的技术机制。复制的本质是将主库上发生的写操作（INSERT、UPDATE、DELETE）以某种格式记录下来，再在从库上重放（replay）这些操作，使从库的数据状态与主库保持一致或接近一致。

数据库复制技术最早在1990年代随着互联网应用的规模扩张而成熟。MySQL在3.23版本（2001年）引入了基于二进制日志（binlog）的异步复制，这一设计奠定了此后二十年关系型数据库复制架构的基础。PostgreSQL则在9.0版本（2010年）引入了基于WAL（Write-Ahead Log）的流式复制（Streaming Replication），支持物理级别的字节精确同步。

数据库复制在AI工程中具有特殊的重要性：训练数据读取、特征工程查询等读操作的流量往往比写操作高出数十倍，通过复制将读压力分散到多个从库，可以使单一数据库集群支撑数百倍于单机的读吞吐量。同时，从库可以充当热备份，主库宕机时可在秒级或分钟级内切换，保障在线推理服务的连续性。

---

## 核心原理

### 二进制日志与WAL：复制的数据源

MySQL的异步复制依赖**binlog**（Binary Log）。主库上每一条成功提交的事务都会被写入binlog，格式分为三种：
- **Statement格式**：记录SQL语句本身（如 `UPDATE orders SET status=1 WHERE id=42`），体积小但对非确定性函数（如`NOW()`）不安全。
- **Row格式**：记录每一行修改前后的完整数据，从库回放时不依赖SQL解析，一致性最高，是MySQL 5.7.7起的默认格式。
- **Mixed格式**：系统自动在两者间切换。

PostgreSQL的流式复制使用**WAL段文件**（每段默认16MB），从库的WAL接收进程（WAL Receiver）通过TCP连接实时拉取主库WAL Sender进程产生的WAL字节流，直接应用于从库的数据页，实现物理级别的精确复制，从库与主库的物理文件字节完全相同。

### 同步模式：三种一致性与延迟的权衡

复制按同步时序分为三种模式，其差异直接决定了数据丢失风险（RPO）与写延迟。

| 模式 | 主库提交时机 | 数据丢失风险 | 写延迟影响 |
|------|------------|------------|----------|
| **异步复制（Async）** | 写入本地binlog后立即提交，不等从库确认 | 主库宕机时丢失未同步事务（通常< 1秒） | 几乎无额外延迟 |
| **半同步复制（Semi-sync）** | 至少1个从库确认收到（非应用）后提交 | 从库收到但未应用的场景可能有短暂不一致 | 增加1次网络RTT |
| **同步复制（Sync）** | 所有从库应用事务后才向客户端确认 | 零数据丢失（RPO=0） | 受最慢从库和网络延迟制约 |

MySQL的半同步复制通过`rpl_semi_sync_master_wait_for_slave_count`参数控制需要等待的从库数量，默认为1。PostgreSQL通过`synchronous_standby_names`参数指定同步从库列表，支持`FIRST N`和`ANY N`两种语义。

### 复制拓扑：主从、链式与多主

**主从复制（Primary-Replica）** 是最常见的拓扑：一个主库负责所有写操作，多个从库承接读请求。这种模式的读写分离要求应用层在连接池层面（如ProxySQL或MyCat）识别SQL类型并路由到正确节点。

**链式复制（Chained Replication）** 中，从库A同时作为从库B的主库，形成主→从A→从B的链式结构。这减少了主库的复制线程压力，但链条越长，末端节点的复制延迟越大，从库B的延迟 ≥ 从库A的延迟。

**多主复制（Multi-Primary）** 允许多个节点同时接受写入，例如MySQL Group Replication和Galera Cluster（基于wsrep API）。多主模式必须解决**写冲突**问题：Galera采用乐观并发控制（OCC），在事务认证阶段检测同一行的并发写入，冲突的后提交事务回滚并报错。

---

## 实际应用

**AI特征存储的读扩展**：某推荐系统的特征查询QPS高达50万，单台MySQL实例极限约为2万QPS。通过部署1主8从的异步复制集群，并由ProxySQL进行读流量的轮询（round-robin）分发，将读QPS均摊至每个从库约5.6万，整体集群可支撑45万QPS的读请求，主库仅承载约5万QPS的写操作（模型预测结果回写）。

**在线模型服务的高可用切换**：使用Orchestrator（MySQL拓扑管理工具）监控主库心跳，当主库连续3次（默认3秒间隔，即9秒）未响应时，Orchestrator自动触发故障转移（failover），将延迟最低的从库提升为新主库，并更新其他从库的复制指向，整个过程可在30秒内完成，满足大多数在线推理服务的SLA要求。

**HTAP场景中的实时分析**：将一个从库配置为列式存储引擎（如MySQL的NDB Cluster或TiDB的TiFlash），主库执行OLTP事务写入，分析查询（如训练数据统计）路由到列式从库，避免大范围全表扫描影响主库的OLTP性能。

---

## 常见误区

**误区一：从库可以直接用于ACID事务的一致性读**

由于异步复制存在复制延迟（通常为毫秒到秒级，网络抖动时可达数秒），从库读到的数据不是主库的最新状态。如果业务逻辑要求"写后立即读到自己写入的数据"（Read-Your-Writes一致性），直接从从库读取会产生错误。正确做法是对此类操作强制路由到主库，或使用MySQL Router的`--read-only-targets=secondary`配合会话级`@@session.transaction_read_only`来控制路由。

**误区二：复制延迟为零意味着从库数据与主库完全一致**

`Seconds_Behind_Master=0`（MySQL）或`pg_stat_replication`中`replay_lag=0`只表明从库已应用了它所接收到的所有日志，并不代表网络传输和日志传输本身没有延迟。即使显示为0，仍可能存在主库刚提交但binlog尚未发送到从库的毫秒级窗口，称为**传播延迟（propagation lag）**。

**误区三：增加从库数量可以线性提升写性能**

复制本身不拆分写操作，所有写入仍然全部发生在主库。增加从库只分散了读压力，但同时主库需要为每个从库维护一个独立的binlog dump线程，当从库数量超过20个时，主库在binlog同步上的CPU和网络开销会显著上升。如需扩展写能力，需要使用分库分表而非增加复制副本数量。

---

## 知识关联

**前置概念：事务（ACID）** 数据库复制的正确性建立在事务原子性之上：binlog中记录的是已提交事务的变更，未提交或回滚的事务不会进入复制流，这保证了从库不会应用主库上未完成的事务，即复制不会破坏原子性语义。半同步复制通过等待从库确认来加强持久性（Durability）保证。

**后续概念：分库分表** 复制解决的是单库读扩展和高可用问题，但单库写容量和单表数据量仍存在上限（单表超过5000万行后B+Tree索引效率明显下降）。分库分表在复制的基础上将写操作水平分散到多个独立的数据库实例，每个分片内部仍然可以运行主从复制，两者是互补关系。

**后续概念：数据库备份恢复** 从库天然可以作为在线热备份的数据来源：使用`mysqldump --single-transaction`或`xtrabackup`对从库进行物理备份，不会对主库产生锁等待影响，这是生产环境备份的标准实践。但从库备份的数据只能保证一致性截止到备份时刻，完整的灾难恢复方案还需要结合binlog的时间点恢复（PITR）能力。