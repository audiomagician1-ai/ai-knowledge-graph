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

# 数据库锁机制

## 概述

数据库锁机制是一种通过限制对共享数据的并发访问来保证事务隔离性和数据一致性的手段。其核心目标是解决多个事务同时操作同一数据时产生的**丢失更新（Lost Update）**、**脏读（Dirty Read）**和**不可重复读（Non-repeatable Read）**三类并发异常。没有锁机制，并发执行的事务会相互覆盖彼此的写操作，最终导致数据库进入不一致状态。

锁机制最早随关系数据库的商业化而标准化。IBM System R 在1970年代的研究中首次系统性地实现了两阶段锁协议（2PL，Two-Phase Locking），该协议规定事务必须先完成所有加锁操作（扩展阶段）再开始释放锁（收缩阶段），之后成为数据库并发控制的理论基础。现代主流数据库如 MySQL InnoDB、PostgreSQL 均在此基础上演进出各自的锁实现。

锁机制对 AI 工程中的数据管道尤其重要。在特征工程流水线中，多个训练任务可能同时向特征存储（Feature Store）写入更新版本的特征值；在模型推理服务中，在线学习场景下参数的实时更新与读取也构成并发竞争。正确配置锁策略可直接影响吞吐量和端到端延迟。

---

## 核心原理

### 锁的粒度：行锁与表锁

锁粒度描述了一把锁所保护的数据范围。**表锁（Table Lock）**一次锁定整张表，加锁开销极小（仅一个锁对象），但并发度极低——对表中任一行的写操作都会阻塞其他事务对整张表的读写。MyISAM 引擎默认使用表锁，适合读多写少的批量分析场景。

**行锁（Row Lock）**仅锁定被访问的具体行，MySQL InnoDB 通过索引实现行锁。这里有一个关键细节：**InnoDB 的行锁加在索引记录上，而非数据行本身**。若查询条件不走索引，InnoDB 会退化为全表扫描并对所有索引记录加锁，实际效果等同于表锁。行锁并发度高，但锁对象多时内存开销显著增大，InnoDB 的锁结构每条大约占用 64 字节内存。

介于两者之间的还有**页锁（Page Lock）**，BerkeleyDB 等引擎使用，以 B+ 树中的一个页（通常 16KB）为单位加锁，在实践中已较少见。

### 悲观锁与乐观锁

**悲观锁（Pessimistic Locking）**假设并发冲突必然发生，因此在读取数据时立即加排他锁，阻止其他事务修改。SQL 语法层面使用 `SELECT ... FOR UPDATE` 实现，该语句会对结果集中的每一行加 X 锁（排他锁）直到事务提交。适用于写操作频繁、冲突概率高的场景，如银行转账、库存扣减。其代价是持锁时间长，容易引发锁等待甚至死锁。

**乐观锁（Optimistic Locking）**假设冲突罕见，读取数据时不加任何数据库锁，而是在提交更新时验证数据是否被其他事务修改过。最常见实现是**版本号（version）字段**：读取时记录 `version=5`，提交时执行 `UPDATE ... SET version=6 WHERE id=X AND version=5`，若影响行数为 0，则说明已被并发修改，应用层需重试。乐观锁在读多写少场景下吞吐量可达悲观锁的数倍，但高冲突场景下重试风暴会导致性能急剧下降。

### 共享锁、排他锁与意向锁

InnoDB 将锁分为两种基本类型：
- **共享锁 S（Shared Lock）**：允许持有者读取行，多个事务可同时持有同一行的 S 锁。
- **排他锁 X（Exclusive Lock）**：允许持有者修改或删除行，与任何其他锁不兼容。

兼容矩阵如下：

| | S锁 | X锁 |
|---|---|---|
| **S锁** | 兼容 ✓ | 冲突 ✗ |
| **X锁** | 冲突 ✗ | 冲突 ✗ |

为了在行锁与表锁之间实现高效的兼容性检测，InnoDB 引入**意向锁（Intention Lock）**：事务对某行加 X 锁前，必须先对该行所在的表加意向排他锁 IX。这样，当另一个事务申请表级 S 锁时，只需检查表上是否存在 IX 锁，而无需逐行扫描，将检测时间复杂度从 O(n) 降至 O(1)。

### 间隙锁与 Next-Key Lock

InnoDB 在可重复读（REPEATABLE READ）隔离级别下使用 **Next-Key Lock** 防止幻读。Next-Key Lock = 行锁 + 间隙锁（Gap Lock）的组合，锁定的是一个**左开右闭的区间**，例如 `(3, 7]`。若事务查询 `WHERE id BETWEEN 4 AND 6`，InnoDB 不仅锁定 id=4、5、6 的记录，还锁定这些记录之间及边界外的间隙，阻止其他事务在该区间内插入新行。间隙锁的存在是 InnoDB 死锁发生频率高于纯行锁系统的重要原因之一。

---

## 实际应用

**场景一：AI 模型版本管理表的并发写入**

多个训练任务同时向 `model_versions` 表插入记录并更新 `latest_version` 标志位时，若使用乐观锁（version 字段），低冲突时每次提交只需一次额外的 `UPDATE ... WHERE version=N` 检查。但若多个 GPU 节点同时完成训练并争抢更新，可改用 `SELECT ... FOR UPDATE` 的悲观锁，配合事务将"读取当前最新版本→写入新版本"原子化。

**场景二：特征存储的高并发读写**

Redis 常与关系型数据库配合用于特征存储。对于热点特征键，可使用乐观锁的 `WATCH/MULTI/EXEC` 机制：`WATCH feature_key` 后开始事务，若在 `EXEC` 执行前 `feature_key` 被其他客户端修改，事务自动失败并返回 `nil`，客户端重试。该机制等价于关系型数据库的乐观锁语义。

**场景三：死锁的检测与预防**

InnoDB 内置死锁检测器，默认每隔约 50ms 运行一次等待图（Wait-for Graph）遍历。当检测到循环依赖时，自动回滚**代价最小的事务**（通常是修改行数最少的那个）。在 AI 工程的批量数据加载脚本中，若两个进程以相反顺序锁定同一批行，就会产生死锁。预防方法是**统一锁定顺序**：所有进程按主键升序访问数据行。

---

## 常见误区

**误区一：乐观锁比悲观锁"更先进"因此应默认选用**

乐观锁本质上是将冲突检测推迟到提交阶段，在冲突率超过约 20%～30% 的场景下，大量重试反而导致总 CPU 消耗和平均延迟高于悲观锁。决策标准是实际冲突概率，而非哲学偏好。

**误区二：`SELECT ... FOR UPDATE` 一定能锁住目标行**

若 `WHERE` 子句中的列没有索引，InnoDB 无法精确定位行，会对所有扫描到的索引记录加锁，退化为接近表锁的行为。在 AI 数据管道调试中，若发现 `FOR UPDATE` 查询意外阻塞了无关事务，首先应用 `EXPLAIN` 检查执行计划是否走了全表扫描。

**误区三：表锁一定比行锁性能差**

对于批量全表操作（如 `LOAD DATA INFILE` 导入百万级训练样本），使用表锁只需维护 1 个锁对象，而行锁需要维护数百万个锁对象，内存和 CPU 开销远高于表锁。MyISAM 的表锁在离线批量写入场景下总吞吐量可高于 InnoDB 行锁。

---

## 知识关联

锁机制建立在**事务 ACID 属性**之上：隔离性（Isolation）正是通过锁或其等价机制来实现的，不同的锁策略对应不同的隔离级别——读未提交不加读锁，可重复读加 Next-Key Lock，串行化使用范围锁。理解 ACID 中隔离性的四个级别（READ UNCOMMITTED / READ COMMITTED / REPEATABLE READ / SERIALIZABLE）是判断应选何种锁粒度的前提。

**索引原理**直接决定了行锁的有效性：InnoDB 行锁必须依赖 B+ 树索引才能精准定位加锁目标，二级索引加锁时还会同时锁定对应的聚簇索引记录（即回表加锁），因此同一行数据上可能同时存在二级索引锁和主键索引锁两个锁对象。

后续的 **MVCC（多版本并发控制）**是对锁机制的重要补充：MV