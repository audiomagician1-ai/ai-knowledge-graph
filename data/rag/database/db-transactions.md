---
id: "db-transactions"
concept: "事务(ACID)"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 5
is_milestone: false
tags: ["一致性"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 事务（ACID）

## 概述

数据库事务（Transaction）是指将一组数据库操作作为一个不可分割的逻辑单元执行的机制。1970年代，IBM研究员Jim Gray在研究数据库并发控制时正式提出了事务的概念，并于1981年在论文《The Transaction Concept: Virtues and Limitations》中系统阐述了事务的理论基础。ACID是描述事务四个核心性质的缩写：原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）。

ACID事务解决的核心问题是多用户并发操作和系统故障两类场景下的数据安全问题。以银行转账为例：从账户A扣款100元、向账户B入账100元，这两步操作必须同时成功或同时失败，否则银行系统的账目将产生差错。没有事务保障，任何在操作中间发生的系统崩溃都可能导致金融数据永久性损坏。正因如此，关系型数据库（如PostgreSQL、MySQL InnoDB引擎）将ACID合规性视为最基本的数据可靠性承诺。

## 核心原理

### 原子性（Atomicity）

原子性要求事务内的所有操作要么全部提交（COMMIT），要么全部回滚（ROLLBACK），不存在部分执行的中间状态。数据库通过**撤销日志（Undo Log）**实现原子性：每次修改数据前，先将旧值写入Undo Log，若事务失败则依据Undo Log逐步恢复原始数据。MySQL InnoDB的Undo Log存储在共享表空间中，记录格式为`(transaction_id, row_id, old_value)`，确保任意时刻都能将数据还原至事务开始前的状态。

### 一致性（Consistency）

一致性要求事务执行完毕后，数据库必须从一个合法状态转换到另一个合法状态，即所有已定义的约束（主键约束、外键约束、CHECK约束、触发器规则）不被违反。一致性在某种意义上是其余三个属性共同保障的**目标**，而非独立的技术机制。例如，若表中定义`balance >= 0`的CHECK约束，任何试图将余额写为负数的事务都会被数据库引擎拒绝并自动回滚，即使原子性本身没有被违反。

### 隔离性（Isolation）与四种隔离级别

隔离性解决多个事务并发执行时相互干扰的问题。SQL标准（ISO/IEC 9075）定义了四种隔离级别，从低到高为：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

MySQL InnoDB的默认隔离级别是**REPEATABLE READ**，并通过间隙锁（Gap Lock）额外解决了幻读问题，这是InnoDB超越SQL标准规定的特殊实现。PostgreSQL的默认级别是**READ COMMITTED**。隔离级别越高，并发性能越低，需根据业务场景权衡选择。

### 持久性（Durability）

持久性保证已提交的事务即使在随后发生系统崩溃的情况下也不会丢失。数据库通过**重做日志（Redo Log / WAL：Write-Ahead Logging）**实现持久性：事务提交前，必须先将变更记录顺序写入磁盘上的WAL文件，再修改实际数据页。PostgreSQL的WAL文件默认每个段大小为16MB，存储于`pg_wal`目录。崩溃恢复时，数据库重放WAL中已提交但未同步到数据页的记录，确保数据完整性。`fsync=off`配置虽可提升写入速度，但会牺牲持久性保证，生产环境中极少使用。

## 实际应用

**电商订单系统**：用户下单时需在同一事务内执行：① 在`orders`表插入订单记录；② 在`inventory`表扣减库存；③ 在`payments`表创建支付记录。若库存扣减后支付记录创建失败，整个事务回滚，避免出现已扣库存但无支付记录的僵尸订单。

**Python中使用事务（以psycopg2为例）**：
```python
import psycopg2
conn = psycopg2.connect(dsn)
conn.autocommit = False  # 显式开启事务控制
try:
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.commit()   # 两步均成功才提交
except Exception:
    conn.rollback() # 任一失败则回滚
```

**长事务的性能陷阱**：事务执行期间，InnoDB需持续保留该事务开始时的Undo Log版本用于MVCC读取，若一个事务运行时间超过数分钟，会导致`history list length`（历史链表长度）急剧增长，严重时可使整个数据库性能下降50%以上。生产中应将大批量操作拆分为多个小事务，每批处理1000~5000行。

## 常见误区

**误区一：一致性由数据库自动保证，应用层无需关注**
事实上，数据库只能强制执行已声明的约束（如NOT NULL、FOREIGN KEY），而业务逻辑层面的一致性规则（如"VIP用户单次转账不超过10万元"）必须由应用代码或数据库触发器显式实现。若应用层漏掉业务规则校验，仅依赖数据库原子性，一致性仍可能被破坏。

**误区二：SERIALIZABLE隔离级别是万能的**
SERIALIZABLE级别虽然消除了所有并发异常，但其代价是显著的性能损耗。PostgreSQL使用SSI（Serializable Snapshot Isolation）算法实现SERIALIZABLE，该算法在事务冲突检测上的开销使高并发场景下的吞吐量可降低40%~60%。大多数OLTP应用使用READ COMMITTED配合应用层乐观锁已足够满足需求。

**误区三：事务提交即数据落盘**
COMMIT成功仅表示WAL日志已持久化，数据实际写入数据文件（Checkpoint）是异步完成的。这不违反持久性，因为崩溃恢复时WAL会重放未落盘的已提交数据，但开发者不应假设COMMIT后立即能在数据文件中找到对应的物理写入记录。

## 知识关联

理解ACID事务是掌握后续数据库概念的必要前提。**数据库锁机制**（行锁、表锁、间隙锁）是数据库实现隔离性的底层手段，了解锁的粒度和类型有助于诊断事务死锁问题。**MVCC多版本并发控制**是InnoDB和PostgreSQL在不依赖大量锁的情况下实现读一致性的关键技术，与Undo Log直接相关。**CAP定理**将ACID的"一致性"延伸到分布式系统语境，揭示分布式事务为何无法同时满足一致性与可用性。**数据库复制**场景中，主从异步复制会引入事务持久性的分布式风险——主库已提交的事务在主库崩溃前可能尚未复制到从库，这是ACID在单机层面无法解决的问题，需通过同步复制或Raft等共识协议补充保障。**ORM高级用法**中的`session.begin()`、`@transactional`注解等功能均是对数据库事务API的封装，理解ACID有助于正确配置ORM的事务传播行为（如Spring的`PROPAGATION_REQUIRES_NEW`）。