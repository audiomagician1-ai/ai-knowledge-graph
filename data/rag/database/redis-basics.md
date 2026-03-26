---
id: "redis-basics"
concept: "Redis基础"
domain: "ai-engineering"
subdomain: "database"
subdomain_name: "数据库"
difficulty: 4
is_milestone: false
tags: ["缓存"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Redis基础

## 概述

Redis（Remote Dictionary Server）是由 Salvatore Sanfilippo 于2009年首次发布的开源内存数据库，以BSD许可证授权。它以键值对（key-value）为基本存储单位，但与简单的键值存储不同，Redis原生支持字符串（String）、哈希（Hash）、列表（List）、集合（Set）、有序集合（Sorted Set）等多种复杂数据结构。Redis将所有数据存储在内存中，使其读写延迟可以低至微秒级别——官方基准测试显示，单节点每秒可处理超过100,000次读写操作（QPS）。

Redis在AI工程中的独特价值在于其多重角色：既可以作为高速缓存层减轻数据库压力，又可以作为消息中间件协调分布式任务队列，还可以存储机器学习模型的推理结果或特征向量。理解Redis的工作机制，是构建高性能AI推理服务、实时特征存储和在线学习系统的前提。

## 核心原理

### 内存存储与持久化机制

Redis默认将全量数据存储在内存中，这是其高性能的根本原因。但内存是易失性存储，Redis通过两种持久化方式保证数据安全：**RDB（Redis Database Backup）**和**AOF（Append Only File）**。RDB是按指定时间间隔对内存数据集做快照（snapshot），生成一个紧凑的二进制`.rdb`文件；AOF则以追加方式记录每一条写命令，类似数据库的WAL日志。两者可同时启用，Redis宕机重启后优先使用AOF文件恢复，因为AOF通常比RDB包含更完整的数据。配置`appendfsync everysec`时，AOF每秒刷盘一次，兼顾性能与数据安全。

### 核心数据结构与内部编码

Redis的每种数据类型在不同数据量和元素大小下会自动切换内部编码以节省内存：

- **String**：底层使用`int`（整数）、`embstr`（≤44字节短字符串）或`raw`（长字符串）编码。`INCR`、`DECR`命令依赖`int`编码实现原子计数。
- **Hash**：元素数量少于`hash-max-ziplist-entries`（默认128）且值小于64字节时，使用`ziplist`（压缩列表）；超过阈值转为`hashtable`。
- **Sorted Set**：元素数少于128且元素长度小于64字节时使用`ziplist`，否则使用`skiplist`（跳跃表）加`dict`双索引结构。跳跃表的平均时间复杂度为O(log N)，支持范围查询，这是普通哈希表无法实现的。
- **List**：3.2版本之前使用`ziplist`+`linkedlist`，之后统一使用`quicklist`（多个ziplist节点组成的双向链表）。

### 单线程事件循环与原子性

Redis的命令执行采用**单线程模型**（I/O多路复用 + 事件循环），6.0版本后虽然引入多线程处理网络I/O，但命令执行本身仍是单线程。这个设计使得所有Redis命令天然具有原子性，无需加锁。基于这一特性，`INCR`可以作为无竞争的全局计数器，`SETNX`（Set if Not eXists）可以实现分布式锁的基本语义。需要执行多条原子命令时，Redis提供`MULTI/EXEC`事务块和`Lua`脚本两种方式，Lua脚本在服务端整体执行，保证操作的原子性和隔离性。

### 过期策略与内存淘汰

Redis通过`EXPIRE key seconds`或`PEXPIRE key milliseconds`为键设置TTL（Time To Live）。过期键的删除采用**惰性删除**（访问时检查是否过期）加**定期删除**（每100毫秒随机采样若干键清理过期键）的组合策略。当内存使用达到`maxmemory`上限时，Redis按`maxmemory-policy`配置执行淘汰，常见策略包括`allkeys-lru`（对全部键使用LRU算法淘汰）、`volatile-lru`（仅淘汰设置了过期时间的键）和`noeviction`（拒绝写入，适合不允许数据丢失的场景）。

## 实际应用

**AI推理结果缓存**：在图像分类服务中，将模型推理结果以`SETEX result:{image_hash} 3600 {label}`的形式缓存，TTL设为3600秒。相同图片的第二次请求直接命中Redis，将推理延迟从100ms+降至1ms以内。

**实时特征存储**：用`HSET user:{uid} age 28 city beijing last_active 1700000000`存储用户特征，推荐系统在线服务通过`HGETALL`一次获取全部特征字段，单次操作时间复杂度为O(N)（N为字段数量）。

**任务队列（AI训练调度）**：用`LPUSH task_queue {task_json}`写入训练任务，Worker通过`BRPOP task_queue 0`阻塞等待新任务，实现分布式训练任务的生产者-消费者模式，无需额外消息中间件。

**排行榜与在线评估**：Sorted Set的`ZADD leaderboard {score} {model_id}`记录模型评分，`ZREVRANGE leaderboard 0 9 WITHSCORES`即可获取Top10模型，利用跳跃表O(log N)的插入与范围查询特性实现毫秒级实时排行。

## 常见误区

**误区一：Redis只是简单的缓存，不需要关注数据持久化**。实际上，在AI系统中Redis常作为特征存储的主要存储层，一旦宕机丢失数据将导致在线服务降级。应根据业务容忍度合理配置RDB+AOF双持久化，并定期将RDB文件备份至对象存储。

**误区二：Redis单线程处理命令意味着性能瓶颈**。这一误解忽略了Redis操作的特点——大量命令本身时间复杂度为O(1)，纯内存操作不涉及磁盘I/O，CPU几乎不会成为瓶颈。真正的风险是执行`KEYS *`、`SMEMBERS`大集合等O(N)命令，这些命令会阻塞整个服务器。生产环境中应使用`SCAN`代替`KEYS *`进行渐进式遍历。

**误区三：`MULTI/EXEC`事务与关系型数据库事务等价**。Redis事务没有回滚机制：若事务块内某条命令执行失败（如对String类型执行`LPUSH`），其他命令仍会继续执行，已修改的数据不会撤销。这与MySQL的ACID事务语义有本质区别，需要通过Lua脚本或应用层逻辑自行保证数据一致性。

## 知识关联

**前置知识衔接**：从NoSQL概述进入Redis时，需要将NoSQL的"放弃强一致性换取高性能"这一原则具体化——Redis的单节点模型提供强一致性（单线程原子操作），但主从复制默认是异步的，切换到集群场景时一致性保证会弱化。Redis是NoSQL家族中键值存储（Key-Value Store）这一子类的典型代表，区别于文档数据库（MongoDB）和宽列数据库（Cassandra）。

**后续概念延伸**：掌握Redis单节点的数据结构和内存管理后，学习**分布式缓存**时将直接面对Redis Cluster的数据分片机制：Redis Cluster将键空间划分为16384个哈希槽（hash slot），通过`CRC16(key) mod 16384`计算键所属槽，理解这一机制需要以单节点Redis的键操作模型为基础。此外，分布式缓存中的缓存穿透、缓存雪崩等问题，其解决方案（布隆过滤器`BF.ADD/BF.EXISTS`、随机化TTL）也都构建在Redis单节点能力之上。