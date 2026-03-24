---
id: "db-locking"
concept: "数据库锁机制"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["lock", "pessimistic", "optimistic"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 数据库锁机制

## 概述

数据库锁机制是通过对数据资源加锁来协调多个并发事务之间读写冲突的技术手段。当两个事务同时尝试修改同一行数据时，锁机制确保只有一个事务能够持有写权限，其余事务必须等待或回滚，从而保证数据的一致性与隔离性。

锁机制的概念伴随关系数据库的早期发展而形成。IBM System R 在1970年代的研究中首次系统化地提出了两阶段锁协议（2PL，Two-Phase Locking），规定事务必须在"加锁阶段"申请所有锁，在"解锁阶段"释放所有锁，两个阶段不能交叉。这一协议至今仍是 MySQL InnoDB、PostgreSQL 等主流数据库引擎的底层锁调度基础。

在 AI 工程的数据库场景中，特征存储、模型版本表、在线推理日志表往往面临极高的并发读写压力。错误选择锁策略会导致锁等待超时（Lock Wait Timeout）或死锁（Deadlock），直接造成推理服务的 P99 延迟飙升。因此，理解不同锁粒度和锁类型的代价，是数据库性能调优的必要前提。

---

## 核心原理

### 锁粒度：行锁与表锁

**表锁（Table Lock）**作用于整张表，加锁开销极低（无需维护行级元数据），但并发性差。MyISAM 存储引擎默认使用表锁；InnoDB 在执行 `LOCK TABLES` 或无法命中索引的 `UPDATE`/`DELETE` 时也会退化为表锁。表锁分为读锁（S 锁，共享）和写锁（X 锁，排他），同一张表的写锁与任何其他锁都不兼容。

**行锁（Row Lock）**作用于单条记录，InnoDB 通过给索引叶节点打标记实现行锁，而非锁定物理行。这意味着**若 WHERE 条件列上没有索引，InnoDB 将扫描全表并对每一条记录加行锁，等效退化为表锁**。行锁的内存开销约为每把锁 40～80 字节，百万级并发场景下需关注锁内存总量。

行锁与表锁之间存在**意向锁（Intention Lock）**，分为意向共享锁（IS）和意向排他锁（IX）。事务在对某行加行级 X 锁之前，必须先对该表加 IX 锁。意向锁使得表级锁请求无需逐行检查是否有冲突的行锁，将兼容性判断的时间复杂度从 O(n) 降为 O(1)。

### 悲观锁与乐观锁

**悲观锁（Pessimistic Locking）**假设冲突必然发生，在读取数据时立刻加排他锁，阻止其他事务修改。SQL 层面通过 `SELECT ... FOR UPDATE` 实现，该语句会对命中的行加 X 锁，直到当前事务提交或回滚。悲观锁适用于写冲突概率较高（>30%）的场景，如金融账户扣款，但会显著降低并发吞吐量。

**乐观锁（Optimistic Locking）**假设冲突极少发生，在读取时不加锁，在提交更新时才检查数据是否被他人修改。最常见实现是在表中增加 `version` 整型列，更新时执行：

```sql
UPDATE feature_store
SET value = :new_value, version = version + 1
WHERE id = :id AND version = :old_version;
```

若返回的受影响行数（`affected rows`）为 0，说明期间有其他事务已修改该行，当前事务必须重试。乐观锁无需数据库层面的锁等待，适合读多写少、冲突概率低于 5% 的特征读写场景。但在高冲突下，频繁重试反而比悲观锁消耗更多 CPU。

### 间隙锁与 Next-Key Lock

InnoDB 在**可重复读（Repeatable Read）**隔离级别下，为解决幻读问题引入了**间隙锁（Gap Lock）**和 **Next-Key Lock**。Next-Key Lock = 行锁 + 该行前方间隙的间隙锁，其锁定范围是一个左开右闭区间 `(prev_key, current_key]`。

例如，索引中存在值 10、20、30，执行 `SELECT * FROM t WHERE id BETWEEN 15 AND 25 FOR UPDATE` 时，InnoDB 会对 `(10, 20]` 和 `(20, 30]` 加 Next-Key Lock，阻止其他事务在此范围内插入 id=18 或 id=25 的新行。这是 InnoDB 防止幻读的核心手段，但也是造成插入并发性下降的常见原因。

### 死锁检测

InnoDB 维护一张等待图（Wait-for Graph），通过深度优先搜索检测环路，一旦发现死锁，将选择**回滚代价最小**（通常是已修改行数最少）的事务作为牺牲者（Victim）并抛出错误码 `ERROR 1213`。死锁检测的时间复杂度为 O(n²)（n 为活跃事务数），可通过 `innodb_deadlock_detect=OFF` 并改用锁等待超时来规避高并发下的检测开销，但需谨慎评估业务容忍度。

---

## 实际应用

**AI 特征存储的并发写入**：多个特征计算 Worker 同时更新同一用户的特征向量时，推荐使用乐观锁（version 列）而非 `SELECT FOR UPDATE`。原因是特征写入的冲突率通常极低（不同 Worker 写不同特征列），乐观锁避免了锁等待队列的堆积。

**模型版本管理表**：在更新"当前生产模型版本"这类全局唯一记录时，应使用悲观锁（`FOR UPDATE`），因为并发部署操作导致版本号乱序的代价远高于锁等待的代价。

**批量导入训练数据**：大批量 `INSERT` 操作若与在线查询并发，建议使用 `INSERT INTO ... ON DUPLICATE KEY UPDATE` 配合行锁，而非先 `SELECT` 再决定是否 `INSERT`（后者会在间隙上加更多 Next-Key Lock，阻塞并发插入）。

---

## 常见误区

**误区一：InnoDB 的行锁总是只锁一行**
实际上，只有通过索引访问的行才会精确加行锁。执行 `UPDATE orders SET status=1 WHERE remark='VIP'`，若 `remark` 列无索引，InnoDB 会对全表所有行加行级 X 锁，并发性与表锁无异，且因行锁数量巨大，内存开销远超表锁。

**误区二：乐观锁不占用任何数据库资源**
乐观锁的 version 检查发生在事务提交阶段，在此之前该事务已经占用了 undo log 空间和 redo log 缓冲。高冲突场景下，大量事务冲突回滚会导致 undo log 膨胀，同样影响数据库性能。

**误区三：`SELECT FOR UPDATE` 可以锁住不存在的行**
在 READ COMMITTED 隔离级别下，`SELECT ... FOR UPDATE WHERE id=999`（id=999 不存在）不会加任何锁，另一个事务可以立即插入 id=999 的行。若需防止并发插入同一 id，必须切换到 REPEATABLE READ 并依赖间隙锁，或在应用层使用分布式锁。

---

## 知识关联

**前置概念**：理解锁机制必须先掌握**事务（ACID）**中的隔离性（Isolation），因为行锁、间隙锁的行为都随隔离级别变化——READ COMMITTED 不产生间隙锁，SERIALIZABLE 则会将普通 SELECT 也升级为加锁读。**索引原理**同样是前提：行锁的"退化为表锁"现象本质是 InnoDB 无法通过 B+ 树叶节点精确定位行时的兜底策略。

**后续概念**：锁机制是理解 **MVCC（多版本并发控制）**的基础。MVCC 通过为每行数据保存多个历史版本（基于 undo log 链和 `DB_TRX_ID`、`DB_ROLL_PTR` 隐藏列），让普通 `SELECT` 读取数据的快照版本而无需加任何锁，从而实现"读写不阻塞"。可以说，MVCC 是对悲观锁的读侧替代方案，而行锁依然负责写-写冲突的仲裁。两者协同工作，构成 InnoDB 高并发架构的完整图景。
