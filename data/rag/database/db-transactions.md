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
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.424
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 事务（ACID）

## 概述

数据库事务（Transaction）是一组作为单一逻辑工作单元执行的数据库操作序列，这组操作要么全部成功提交，要么全部回滚撤销，不存在中间状态。1970年代，IBM研究员Jim Gray在研究IMS数据库系统时，首次系统性地定义了事务的概念，并于1981年在论文《The Transaction Concept: Virtues and Limitations》中明确阐述了其基本属性。

ACID是四个英文单词的首字母缩写：原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation）、持久性（Durability）。这四个属性由Andreas Reuter和Theo Härder于1983年在论文《Principles of Transaction-Oriented Database Recovery》中正式命名为"ACID"。在银行转账、电商下单、库存扣减等场景中，违反任意一条ACID属性都可能导致资金损失或数据腐化，因此ACID是关系型数据库区别于早期文件系统的根本性技术保障。

## 核心原理

### 原子性（Atomicity）

原子性要求一个事务中的所有操作不可分割，必须作为一个整体执行。数据库通过**undo log（回滚日志）**实现原子性：在修改数据前，先将原始值写入undo log；如果事务中途失败，系统读取undo log将数据恢复到事务开始前的状态。以银行转账为例，"从账户A扣减100元"和"向账户B增加100元"是同一事务的两条SQL语句，若第二条执行时系统崩溃，undo log机制会自动撤销第一条的扣款操作，绝不会出现A扣款成功而B未收款的半完成状态。

### 一致性（Consistency）

一致性要求事务执行前后，数据库必须从一个合法状态转换到另一个合法状态，所有业务规则和约束（如外键约束、唯一性约束、CHECK约束）均不被违反。一致性是ACID中唯一一个由**应用层语义**定义的属性，其余三个属性都是由数据库引擎技术保证的。例如，某账户余额有`CHECK (balance >= 0)`约束，若事务试图将余额扣为负数，数据库会拒绝提交并回滚整个事务，从而维持数据的业务一致性。

### 隔离性（Isolation）与隔离级别

隔离性规定并发执行的多个事务之间互不干扰，每个事务的中间状态对其他事务不可见。SQL标准（SQL-92）定义了四种隔离级别，隔离程度从低到高依次为：

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|---|---|---|---|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ | 不可能 | 不可能 | 可能 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

MySQL InnoDB引擎的默认隔离级别是**REPEATABLE READ**，并通过Next-Key Lock（间隙锁+行锁）额外解决了幻读问题，而PostgreSQL的默认级别是**READ COMMITTED**。隔离级别越高，并发性能越低，因为需要更多的锁或版本控制开销。

### 持久性（Durability）

持久性保证已提交的事务即使系统崩溃也不会丢失，其核心实现机制是**redo log（重做日志）**，即WAL（Write-Ahead Logging，预写日志）技术。InnoDB在事务提交时，先将redo log刷写到磁盘（`innodb_flush_log_at_trx_commit=1`配置），再异步更新数据页缓存（Buffer Pool）。即使提交后立即断电，数据库重启时也能通过重放redo log来恢复已提交的数据变更。redo log与undo log是持久性和原子性的技术基石，二者共同构成InnoDB的崩溃恢复（Crash Recovery）体系。

## 实际应用

**电商库存扣减场景**：用户下单时需要在同一事务中执行"校验库存 → 扣减库存 → 创建订单 → 扣除余额"四步操作。若使用READ UNCOMMITTED级别，可能读到另一个未提交事务的库存扣减结果，导致超卖。实践中通常在REPEATABLE READ级别下配合`SELECT ... FOR UPDATE`行级锁，锁住库存行后再进行扣减。

**Python中的事务控制**：使用`psycopg2`操作PostgreSQL时，连接默认处于自动提交关闭（`autocommit=False`）状态，需显式调用`conn.commit()`提交或`conn.rollback()`回滚。在SQLAlchemy ORM框架中，`session.begin()`开启事务上下文，所有操作在`session.commit()`前均处于未提交状态，任何异常会触发`session.rollback()`。

**长事务的危害**：在MySQL中，长时间未提交的事务会持续持有行锁，同时阻止InnoDB清理undo log（因为其他事务可能还需要读取历史版本），导致undo log无限增大，严重时可撑满磁盘。因此在AI系统的批量数据导入场景中，通常采用分批次提交（每1000条提交一次）而非单个巨型事务。

## 常见误区

**误区一：认为一致性完全由数据库保证**。实际上，ACID中的C（一致性）是唯一依赖**应用程序逻辑**的属性。数据库只能保证显式定义的约束（如外键、唯一索引）不被违反；但业务规则如"转账双方余额之和不变"需要开发者自行在事务代码中正确实现——如果转账代码只写了扣款而忘写加款，数据库不会自动发现这个业务逻辑错误。

**误区二：SERIALIZABLE级别就是最佳选择**。SERIALIZABLE通过强制事务串行执行（或使用谓词锁）消除所有并发异常，但在高并发系统下性能损耗极大。以TPC-C基准测试数据为例，从READ COMMITTED升级到SERIALIZABLE，吞吐量可下降60%至80%。实际生产环境中绝大多数业务在READ COMMITTED或REPEATABLE READ级别下结合乐观锁即可满足需求。

**误区三：混淆事务的原子性与持久性**。原子性的实现者是undo log，负责"失败回滚"；持久性的实现者是redo log，负责"成功不丢"。二者解决的是相反方向的问题：undo log应对事务失败，redo log应对系统崩溃。将二者混淆会导致在分析数据丢失或数据不一致故障时定位方向错误。

## 知识关联

理解ACID是进入后续高级数据库主题的必要前提。**数据库锁机制**（行锁、表锁、意向锁）是实现隔离性的底层手段，隔离级别本质上是通过不同粒度的锁策略权衡并发与一致性。**MVCC多版本并发控制**则是InnoDB等引擎为减少锁竞争而设计的读写不阻塞技术，它通过维护数据行的多个历史版本来实现无锁的一致性读，是REPEATABLE READ级别的核心实现机制。

在分布式系统方向，**CAP定理**指出在分布式环境下，网络分区时系统无法同时保证一致性（C）和可用性（A）——这里的C与ACID中的C含义不同，前者指分布式节点间的数据副本一致，后者指单节点的业务数据约束合法性。而**数据库复制**（主从同步）正是在放弃强一致性的前提下换取高可用性的典型权衡。ORM框架（如Django ORM、SQLAlchemy）的高级用法则在ACID基础上提供了事务嵌套（Savepoint）、懒加载与事务边界管理等抽象，是ACID原理在应用层的工程化体现。
