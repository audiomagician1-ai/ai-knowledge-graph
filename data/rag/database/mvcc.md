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
quality_tier: "B"
quality_score: 45.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
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

MVCC（Multi-Version Concurrency Control，多版本并发控制）是一种通过保存数据的多个历史版本来实现事务并发访问的机制。其核心思想是：读操作访问数据的历史快照版本，而不是当前最新版本，从而避免读写操作之间相互阻塞。这与基于锁的并发控制形成鲜明对比——锁机制中读操作需要等待写操作释放锁，而MVCC让读写操作在大多数情况下可以并行执行。

MVCC的概念最早在1979年由David Reed在其博士论文中提出，后来在PostgreSQL（1987年首次实现）和Oracle中得到广泛采用。MySQL的InnoDB存储引擎在其5.0版本后也完整实现了MVCC。Oracle使用Undo段来存储旧版本，PostgreSQL将所有版本存储在堆表中（称为"heap tuple"），InnoDB则通过回滚日志（Undo Log）构建版本链。三种实现路径各有取舍，但核心逻辑一致。

MVCC在AI工程的数据库场景中至关重要。训练数据管道、特征存储系统往往存在大量并发读取需求（如批量数据加载）与少量写入操作（如特征更新）并存的情况。若使用悲观锁，读操作将因等待写锁而产生严重延迟；MVCC允许读操作读取写操作提交前的稳定快照，吞吐量可提升数倍。

---

## 核心原理

### 版本链与隐藏字段

InnoDB中每行数据包含两个对用户不可见的隐藏字段：`DB_TRX_ID`（最近修改该行的事务ID，6字节）和`DB_ROLL_PTR`（回滚指针，7字节，指向Undo Log中的旧版本）。当事务修改某行时，InnoDB不会直接覆盖旧数据，而是将旧版本写入Undo Log，并让新版本的`DB_ROLL_PTR`指向旧版本。多次修改后，各版本通过回滚指针串联成一条**版本链**（Version Chain）。

例如：事务T1将某行值从A改为B，事务T2再将其从B改为C，则版本链为：`C(T2) → B(T1) → A(初始)`。读操作需要沿版本链回溯，找到对当前事务可见的版本。

### ReadView与可见性判断

MVCC通过**ReadView（读视图）**决定当前事务能看到哪个版本。ReadView包含以下关键信息：
- `m_ids`：创建ReadView时，所有**活跃未提交**事务的ID列表
- `min_trx_id`：`m_ids`中的最小值
- `max_trx_id`：创建ReadView时，系统即将分配的下一个事务ID（即已分配最大事务ID+1）
- `creator_trx_id`：创建此ReadView的当前事务ID

可见性判断规则如下：对于版本链中某版本的事务ID `trx_id`：
1. 若 `trx_id == creator_trx_id`：该版本是当前事务自己修改的，**可见**
2. 若 `trx_id < min_trx_id`：该事务在ReadView创建前已提交，**可见**
3. 若 `trx_id >= max_trx_id`：该事务在ReadView创建后才开始，**不可见**
4. 若 `min_trx_id <= trx_id < max_trx_id`：检查`trx_id`是否在`m_ids`中——在则**不可见**（未提交），不在则**可见**（已提交）

### MVCC与事务隔离级别的绑定关系

MVCC的行为直接由事务隔离级别控制，关键差异在于**ReadView的创建时机**：

- **READ COMMITTED（读已提交）**：每次执行`SELECT`语句时都创建一个新的ReadView。因此，同一事务中两次读取可能看到不同结果——第一次读后若另一事务提交了修改，第二次读会看到新值，产生**不可重复读**问题。

- **REPEATABLE READ（可重复读，InnoDB默认）**：只在事务第一次执行`SELECT`时创建ReadView，此后整个事务期间复用同一个ReadView。无论其他事务如何提交，当前事务始终读取同一快照，解决了不可重复读问题。InnoDB还通过Gap Lock（间隙锁）配合MVCC解决了幻读问题，这是标准REPEATABLE READ定义之外的额外保证。

- **SERIALIZABLE**：InnoDB在此级别会对所有读操作加共享锁，退化为锁机制，不再使用MVCC的快照读。

**快照读（Snapshot Read）**与**当前读（Current Read）**的区别也至关重要：普通`SELECT`使用快照读，依赖MVCC；而`SELECT ... FOR UPDATE`、`SELECT ... LOCK IN SHARE MODE`以及`INSERT/UPDATE/DELETE`使用当前读，读取最新版本并加锁，绕过MVCC版本链。

---

## 实际应用

**特征存储的并发更新场景**：在机器学习特征平台（如Feast）中，特征值每隔几分钟批量写入数据库，同时在线推理服务持续高频读取特征。在REPEATABLE READ隔离级别下，推理服务的读操作获取一个稳定的ReadView快照，批量写入事务不会阻塞任何读操作。写入完成提交后，新的读事务自然看到最新特征值。这使得特征写入的平均耗时不受读并发量影响。

**长事务导致Undo Log膨胀**：一个常见的生产问题——若某个数据分析查询开启了一个持续30分钟的长事务（即使只读），InnoDB无法清理该ReadView创建时刻之后的所有Undo Log版本，因为长事务的ReadView可能需要回溯到这些旧版本。结果是Undo表空间急剧膨胀，版本链变长导致读操作变慢。监控`information_schema.INNODB_TRX`表中的`trx_started`字段可发现此类长事务。

**MVCC在分布式数据库中的扩展**：TiDB使用全局授时服务（PD的TSO，Timestamp Oracle）生成单调递增的时间戳作为事务版本号，替代InnoDB的自增事务ID，以此在分布式节点间实现一致的快照读。CockroachDB采用HLC（Hybrid Logical Clock）实现类似功能。这说明MVCC的版本编号机制可以被替换，但可见性判断的逻辑框架保持不变。

---

## 常见误区

**误区一：MVCC完全消除了锁的需求**

MVCC只让**读-写**之间不阻塞，但**写-写**冲突仍然需要锁来解决。两个事务同时修改同一行时，后到的写操作必须等待先到的写操作提交或回滚后才能继续。此外，InnoDB在REPEATABLE READ下对写操作使用Next-Key Lock，防止幻读，这些锁与MVCC是并存而非互斥的关系。

**误区二：REPEATABLE READ完全消除了幻读**

标准SQL规范中，REPEATABLE READ隔离级别不要求解决幻读。InnoDB的实现通过Gap Lock额外解决了**快照读场景**下的幻读，但在**混合当前读与快照读**的场景下仍可能出现幻读。例如：事务A先用快照读确认某范围无数据，事务B插入并提交，事务A再用`SELECT ... FOR UPDATE`（当前读）查询，此时会看到事务B新插入的行——这是实际存在的幻读场景。

**误区三：旧版本数据会立即被清理**

Undo Log中的旧版本不会在事务提交后立即删除。InnoDB的后台**Purge线程**负责清理不再被任何ReadView引用的旧版本。若系统中存在活跃的长事务，Purge线程无法推进清理进度，导致旧版本数据长期占用磁盘空间，这是高并发写入场景中磁盘空间异常增长的常见原因。

---

## 知识关联

**依赖事务ACID特性**：MVCC是实现事务**隔离性（Isolation）**的具体技术手段。理解事务的ACID属性，特别是原子性如何通过Undo Log实现，是理解MVCC版本链构建方式的前提——Undo Log既服务于事务回滚（原子性），也服务于历史版本存储（隔离性）。

**依赖数据库锁机制**：MVCC并不替代锁，而是与锁机制分工协作。锁机制中的行锁（Record Lock）和间隙锁（Gap Lock）解决写-写冲突与幻读，MVCC解决读-写并发问题。彻底理解InnoDB的并发控制，需要同时掌握这两套机制的边界：快照读走MVCC版本链，当前读走加锁路径。

**向分布式事务延伸**：单机MVCC的版本号基于本地自增事务ID，而分布式数据库需要全局一致的版本号（如TiDB的TSO、Google Spanner的TrueTime API）。掌握单机MVCC原理后，分布式MVCC的核心挑战从"如何判断可见性"变为"如何在多节点间生成全局单调时间戳"，两者的可见性判断逻辑本质相同。