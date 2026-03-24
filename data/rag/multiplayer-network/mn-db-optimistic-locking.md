---
id: "mn-db-optimistic-locking"
concept: "乐观锁机制"
domain: "multiplayer-network"
subdomain: "database-design"
subdomain_name: "数据库设计"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 乐观锁机制

## 概述

乐观锁机制是一种基于版本号（或时间戳）的并发控制策略，其核心假设是"冲突很少发生"——因此不在读取数据时加锁，而是在提交修改时验证数据自读取以来是否被他人修改过。与悲观锁（SELECT ... FOR UPDATE）不同，乐观锁在整个业务逻辑处理期间不持有任何数据库行锁，只在最终UPDATE时做一次版本核对。

乐观锁的概念最早由Jim Gray等数据库研究者在20世纪70年代末提出，与悲观并发控制相对应，被称为"Optimistic Concurrency Control（OCC）"。在多人游戏场景中，玩家数据的读多写少特征（典型比例约为10:1的读写比）使乐观锁成为比行锁更高效的选择，因为行锁会在玩家查询背包、查看排行榜等高频只读操作中造成不必要的等待。

在网络多人游戏数据库中，乐观锁最常用于保护玩家背包、货币余额、角色属性等"一人独占写"但可能被多个游戏服务节点并发更新的数据。它有效防止了"先读后写"竞态条件（Read-Modify-Write Race），例如两个游戏服务器节点同时读到玩家金币为1000，各自扣除200，最终只扣了一次而不是两次的经典丢失更新（Lost Update）问题。

## 核心原理

### 版本号字段与SQL实现

乐观锁的数据库实现需要在目标表中增加一个版本号字段，通常命名为 `version` 或 `row_version`，数据类型为 `INT UNSIGNED`，初始值为0。完整的更新语句模板如下：

```sql
UPDATE player_inventory
SET gold = gold - 200, version = version + 1
WHERE player_id = 12345 AND version = 7;
```

执行后必须检查 `affected_rows` 的返回值：若为1，表示版本匹配，更新成功；若为0，表示在本次读取之后已有其他事务修改了该行（version已从7变为8），本次更新被拒绝。这个"版本核对+原子更新"过程在单条SQL语句内完成，利用数据库自身的行级原子性保证不会出现判断与写入之间的间隙。

### 冲突检测与重试策略

乐观锁失败后的标准处理流程是**重新读取最新数据并重试整个业务逻辑**，而不是简单地重发原来的UPDATE。重试次数需要设定上限，游戏服务通常设置3到5次重试，超出后向客户端返回"操作繁忙，请稍后重试"。重试间隔可采用指数退避（Exponential Backoff）：第1次立即重试，第2次等待10ms，第3次等待20ms，避免多个节点同时重试时产生竞争风暴（Retry Storm）。

判断适用乐观锁的关键指标是**冲突率**。当并发写入同一行的概率低于5%时，乐观锁的总体开销（读+版本校验写）远低于悲观锁（加锁+写+解锁+锁等待）。若冲突率持续高于20%，应考虑改用悲观锁或引入队列串行化写入。

### 时间戳版本的变体

除整型版本号外，部分游戏数据库使用 `TIMESTAMP(6)`（精度到微秒）作为版本标记，更新条件改为 `WHERE player_id = ? AND updated_at = ?`。时间戳版本的优势是无需额外维护单调递增逻辑，劣势是在同一微秒内发生的两次更新会产生假性通过——因此高并发游戏场景更推荐整型版本号，其单调递增保证绝对不会发生版本碰撞误判。

## 实际应用

**玩家背包物品合并**：当玩家从副本掉落拾取道具时，游戏服务器A读取背包版本号为42，同时服务器B也因玩家主动购买物品读取了版本42。服务器A先提交，version变为43；服务器B提交时WHERE version = 42不匹配，affected_rows = 0，服务器B重新读取version = 43后重试，确保两次物品变更都被正确写入，背包不会丢失任何一件物品。

**竞技场匹配扣除门票**：匹配服务在为玩家配对时需扣除竞技场门票，若同一玩家被两个匹配节点同时选中，乐观锁保证只有一个节点能成功扣票（version匹配），另一个节点收到affected_rows = 0后将玩家移回匹配队列并提示"正在处理中"。

**排行榜分数更新**：玩家击杀BOSS后同步更新积分，UPDATE score SET points = 5800, version = version + 1 WHERE uid = 9876 AND version = 15，在高并发赛季结束结算时，乐观锁确保每次有效击杀的积分都被串行写入，不会因并发丢失任何一次得分。

## 常见误区

**误区一：认为检查affected_rows不必要**。部分开发者在执行乐观锁UPDATE后不验证影响行数，仅凭SQL执行无报错即认为成功。但MySQL/PostgreSQL在WHERE条件不匹配时不会抛出异常，只静默返回affected_rows = 0。不检查这个返回值会导致冲突完全被忽略，退化为无任何并发保护的裸写操作，Lost Update问题依然存在。

**误区二：在同一事务内多次UPDATE才能保证一致性**。有开发者认为需要先 `SELECT ... FOR UPDATE` 再用乐观锁，实际上乐观锁的设计初衷正是**避免使用行锁**。如果已经SELECT FOR UPDATE，就应走悲观锁路线，混用两种机制会增加死锁风险，并且让乐观锁失去减少锁竞争的意义。

**误区三：版本号可以由应用层而非数据库层自增**。若version = version + 1在UPDATE语句中执行，则版本递增与行写入是原子的；若应用层先计算new_version = old_version + 1再传入SQL，在极少数情况下（如应用层重复请求）可能写入错误版本值。版本号的递增逻辑必须放在SQL语句内部，绝不能依赖应用层计算。

## 知识关联

乐观锁建立在**事务设计**的原子性（Atomicity）基础之上——正是单条UPDATE语句的原子执行，使得版本校验与数据写入之间不存在可被插入的间隙。掌握事务的ACID属性、理解InnoDB行级锁与MVCC的工作方式，是正确实施乐观锁的前提，因为乐观锁的WHERE版本校验利用了InnoDB在UPDATE时对目标行施加的短暂排他锁（X Lock），确保两个并发UPDATE不会同时通过版本检查。

在游戏数据库的整体架构中，乐观锁通常与**写入队列**、**幂等性设计**配合使用：写入队列将同一玩家的写操作串行化，从根本上消除冲突；幂等性设计保证重试操作不会产生副作用。三者共同构成多人游戏后端处理并发玩家数据修改的完整防护体系。
