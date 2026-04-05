---
id: "mvcc"
concept: "MVCC多版本并发控制"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 5
is_milestone: false
tags: ["mvcc", "snapshot", "isolation"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# MVCC多版本并发控制

## 概述

MVCC（Multi-Version Concurrency Control，多版本并发控制）是一种通过保存数据的多个历史版本来实现并发读写操作互不阻塞的数据库并发控制机制。与传统的基于锁的并发控制不同，MVCC允许读操作访问数据的某个历史快照，从而避免了读写锁争用——**读操作不阻塞写操作，写操作不阻塞读操作**。

MVCC的思想最早可追溯至1978年David Reed在MIT的博士论文，后被Oracle、PostgreSQL、MySQL InnoDB等主流数据库广泛采用。PostgreSQL从1.0版本起即使用MVCC，而MySQL InnoDB引擎则在5.0版本后将MVCC作为默认并发策略。在OLTP（在线事务处理）场景下，读操作往往占总操作量的70%~80%，MVCC通过消除读锁显著提升了系统吞吐量。

MVCC的核心价值在于它直接决定了数据库能实现哪些事务隔离级别。可重复读（Repeatable Read）和读已提交（Read Committed）这两种最常用的隔离级别，在InnoDB中完全依赖MVCC的快照读机制实现，而非依赖行级锁。

## 核心原理

### 版本链与隐藏字段

InnoDB为每行数据在物理层面添加三个隐藏字段来支撑MVCC：
- **DB_TRX_ID**（6字节）：最近一次修改该行的事务ID
- **DB_ROLL_PTR**（7字节）：回滚指针，指向undo log中该行的上一个版本
- **DB_ROW_ID**（6字节）：行ID，在无主键时作为隐式主键

每次对某行进行UPDATE或DELETE时，数据库不会原地覆盖，而是将旧版本写入undo log，并通过DB_ROLL_PTR将新旧版本串联成一条**版本链**。例如，事务100将某行的值从"A"改为"B"，事务200再将其改为"C"，则该行版本链为：`C(TRX_ID=200) → B(TRX_ID=100) → A(TRX_ID=...)`，每个节点都存储于undo log中。

### ReadView快照机制

读操作通过创建**ReadView**来决定应当读取版本链中的哪个版本。ReadView包含四个关键数据结构：

- `m_ids`：创建ReadView时，系统中所有**活跃（未提交）**事务的ID集合
- `min_trx_id`：`m_ids`中的最小值
- `max_trx_id`：系统已分配的最大事务ID + 1（即下一个将分配的ID）
- `creator_trx_id`：创建本ReadView的事务自身ID

版本可见性判断规则如下（按顺序检查版本链中每个版本的DB_TRX_ID，记为`trx_id`）：
1. 若`trx_id == creator_trx_id`：该版本是当前事务自己修改的，**可见**
2. 若`trx_id < min_trx_id`：该版本在ReadView创建前已提交，**可见**
3. 若`trx_id >= max_trx_id`：该版本在ReadView创建后才开始，**不可见**
4. 若`min_trx_id <= trx_id < max_trx_id`：检查`trx_id`是否在`m_ids`中——在则**不可见**（未提交），不在则**可见**（已提交）

沿版本链向旧版本回溯，直到找到第一个可见版本即为最终读取结果。

### 隔离级别与ReadView创建时机

MVCC实现不同事务隔离级别的关键在于**何时创建ReadView**：

- **读已提交（Read Committed）**：每次执行SELECT语句都重新创建一个新的ReadView。这意味着在同一事务内，两次相同的SELECT可能看到不同结果——第一次执行时某并发事务未提交（不可见），第二次执行时该事务已提交（可见），这正是**不可重复读**现象的来源。

- **可重复读（Repeatable Read）**：仅在事务内**第一次执行SELECT时**创建ReadView，后续所有SELECT复用同一个ReadView。由于`m_ids`固定不变，并发事务提交前后对本事务的可见性不变，从而消除了不可重复读。InnoDB在可重复读级别下还通过间隙锁（Gap Lock）配合MVCC来防止幻读。

需要注意的是，MVCC仅对**快照读**（普通SELECT）生效。当使用`SELECT ... FOR UPDATE`或`SELECT ... LOCK IN SHARE MODE`时，触发的是**当前读**，会直接读取最新版本并加锁，绕过MVCC版本链。

## 实际应用

**AI训练数据管理平台**：在特征存储（Feature Store）系统中，多个训练任务并发读取特征数据，同时数据工程师在更新特征值。借助MVCC，训练任务可以基于任务启动时的快照读取一致的特征版本，不会因为工程师的写操作而中断或读到中间状态。Feast等开源Feature Store的离线存储层即利用了数据库MVCC特性保证特征一致性。

**模型版本管理数据库**：MLflow等工具在PostgreSQL中记录实验运行记录时，并发写入多个实验结果（INSERT）的同时，分析师进行聚合查询（SELECT AVG(metrics)）。由于PostgreSQL的MVCC采用与InnoDB类似的快照隔离，聚合查询基于快照执行，不会读到尚未提交的半完整实验记录，确保统计结果的准确性。

**高并发推荐系统的用户行为记录**：以每秒数万次并发写入用户点击行为为场景，MySQL InnoDB利用MVCC使读操作（模型推理时读取用户画像）与写操作（记录新行为）完全并行，实测显示开启MVCC的InnoDB在读写混合负载下比纯锁机制的吞吐量高出3~5倍。

## 常见误区

**误区一：MVCC可以解决所有幻读问题**

许多人认为InnoDB可重复读级别下MVCC完全防止了幻读。实际上，MVCC只对快照读（普通SELECT）防止幻读——因为读取的是固定快照，不会看到新插入的行。但若在同一事务内先执行快照读再执行当前读（如`SELECT ... FOR UPDATE`），当前读会读取最新数据，此时确实可能看到其他事务新插入的行，出现幻读。InnoDB针对此场景需要通过间隙锁来补充防护。

**误区二：MVCC不占用额外存储空间**

MVCC的历史版本存储在undo log中，这部分空间不会因事务提交而立刻释放。只有当系统中所有活跃ReadView都不再需要某个版本时，后台的**Purge线程**才会异步清理。若存在长事务（如一个事务持续30分钟未提交），其ReadView会阻止所有早于该事务的undo log被回收，导致undo log段急剧膨胀，这是MySQL生产环境中undo tablespace异常增大的主要原因之一。

**误区三：MVCC下写操作之间不存在冲突**

MVCC消除的是读写冲突，写写冲突依然存在且依然通过锁来解决。当两个事务同时UPDATE同一行时，后到的事务需要等待前一个事务释放行锁（X锁），MVCC在此过程中不起作用。MVCC与锁机制是互补关系：前者处理读写并发，后者处理写写并发。

## 知识关联

**与ACID事务的关系**：MVCC是实现ACID中"隔离性（Isolation）"的核心手段。事务的原子性仍依赖undo log（MVCC为undo log的建立提供了基础设施，两者共享同一套undo段），持久性依赖redo log，而隔离性中的可重复读和读已提交级别正是通过本文描述的ReadView机制实现的。

**与数据库锁机制的协同**：MVCC并非取代锁，而是与行锁、间隙锁共同构成InnoDB的并发控制体系。理解了MVCC后，可以更准确地判断哪些SQL触发快照读（走MVCC）、哪些触发当前读（走锁），从而在设计高并发数据库应用时精确控制并发行为，避免不必要的锁等待和死锁。