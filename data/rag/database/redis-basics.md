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
quality_tier: "A"
quality_score: 79.6
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


# Redis基础

## 概述

Redis（Remote Dictionary Server）是由意大利工程师Salvatore Sanfilippo于2009年创建的开源内存数据结构存储系统，最初是为了解决其创业项目中实时日志处理的性能瓶颈而诞生。与传统关系型数据库将数据写入磁盘不同，Redis默认将所有数据存储在内存中，使其读写延迟可低至微秒级别，单机吞吐量可达每秒100万次操作（1,000,000 ops/sec）。

Redis并非单纯的键值存储，而是支持字符串（String）、列表（List）、集合（Set）、有序集合（Sorted Set）、哈希（Hash）等五种基础数据结构，以及Bitmap、HyperLogLog、Geospatial等扩展结构。这种多数据结构特性使得Redis能够在不借助应用层转换逻辑的前提下，直接支持计数器、排行榜、消息队列等多种业务场景。在AI工程领域，Redis常被用于特征向量缓存、模型推理结果存储以及实时推荐系统的在线数据层。

Redis在2015年被Redis Labs（现更名为Redis Inc.）接管商业化运营，并于Redis 7.0版本（2022年4月发布）引入了多部分AOF（Multi-Part AOF）机制，大幅降低了持久化的内存开销。理解Redis的内存管理机制、持久化策略和数据淘汰策略，是在AI系统中正确使用Redis的关键前提。

## 核心原理

### 单线程事件循环与IO多路复用

Redis 6.0之前的版本使用严格的单线程模型处理所有命令请求，这意味着所有命令串行执行，天然避免了多线程竞争条件（race condition）。Redis通过`epoll`（Linux）或`kqueue`（macOS）实现IO多路复用，单个线程可同时监听数千个客户端连接的读写事件。这一设计使得Redis的性能瓶颈不在CPU，而在网络带宽和内存容量。Redis 6.0引入了多线程网络IO（threaded I/O），但命令执行本身仍保持单线程，将网络读写线程数量与CPU核心数匹配可提升约2倍吞吐。

### 五种核心数据结构与底层编码

Redis对每种数据类型根据数据量自动选择底层编码格式以节省内存：

- **String**：当值为整数时使用`int`编码，当字符串长度≤44字节时使用`embstr`（紧凑内存布局），更长则使用`raw`（独立SDS，Simple Dynamic String）。
- **List**：元素数量≤128且每个元素≤64字节时使用`listpack`（Redis 7.0前为`ziplist`），否则升级为`quicklist`（由多个`listpack`节点组成的双向链表）。
- **Hash**：小哈希使用`listpack`，超过`hash-max-listpack-entries`（默认128）或字段值超过`hash-max-listpack-value`（默认64字节）时转为`hashtable`。
- **Sorted Set（ZSet）**：小数据集使用`listpack`，大数据集使用`skiplist`（跳表）+ `hashtable`双索引结构，跳表支持O(log N)的范围查询，哈希表支持O(1)的成员查询。
- **Set**：元素全为整数且数量≤512时使用`intset`（有序整数数组），否则使用`hashtable`。

### 持久化机制：RDB与AOF

Redis提供两种持久化方式，可单独使用也可混合使用：

**RDB（Redis Database Snapshot）**：按照配置的`save`规则（例如`save 900 1`表示900秒内至少1次写操作则触发快照），Redis使用`fork()`系统调用创建子进程，子进程将内存数据序列化为紧凑的二进制`.rdb`文件。RDB恢复速度快，但最多丢失最近一次快照之后的数据。

**AOF（Append Only File）**：将每条写命令追加到`.aof`文件，`fsync`策略支持`always`（每次写后同步，最安全）、`everysec`（每秒同步，最多丢失1秒数据，默认）、`no`（由OS决定）。AOF文件会随时间增长，Redis通过`BGREWRITEAOF`命令进行重写压缩，将冗余命令合并为最小等效命令集。

Redis 4.0引入了**混合持久化**（`aof-use-rdb-preamble yes`），AOF文件头部嵌入RDB快照，尾部追加增量AOF日志，兼顾了RDB的快速恢复和AOF的数据安全性。

### 数据淘汰策略

当内存使用超过`maxmemory`配置值时，Redis根据`maxmemory-policy`参数选择淘汰策略，共8种：
- `noeviction`：拒绝写入，返回错误（默认）
- `allkeys-lru`：从所有键中淘汰最近最少使用的键
- `volatile-lru`：仅从设置了过期时间的键中执行LRU淘汰
- `allkeys-lfu`（Redis 4.0+）：基于访问频率（LFU算法）淘汰全局键

在AI推理缓存场景中，`allkeys-lfu`通常优于`allkeys-lru`，因为热点特征向量的访问模式呈现长尾分布，LFU能更准确地保留高频访问的特征缓存。

## 实际应用

**实时特征缓存**：在AI推荐系统中，用户行为特征（如最近点击商品列表）以Redis Hash结构存储，键为`feature:user:{user_id}`，字段为特征名，值为特征值。利用Redis的`HGETALL`命令可在1毫秒内获取用户的全部特征向量，相比从MySQL查询提速约100倍。

**模型推理结果缓存**：将相同输入的模型预测结果存入Redis String，并设置TTL（Time To Live）过期时间（例如`SET result:{input_hash} {prediction} EX 3600`），避免对相同输入重复执行昂贵的神经网络前向传播。

**排行榜与计数器**：利用Sorted Set的`ZADD`和`ZREVRANGE`命令，可在O(log N)时间内维护实时用户活跃度排行榜。Redis的`INCR`命令利用单线程特性实现原子性自增，无需加锁即可安全统计API调用次数或模型推理请求量。

**消息队列（轻量级）**：使用Redis List的`LPUSH`/`BRPOP`组合可实现阻塞式消息队列，Redis 5.0引入的Stream数据结构（`XADD`/`XREAD`）进一步支持消费者组（Consumer Group）和消息ACK机制，适合AI pipeline中的任务分发。

## 常见误区

**误区一：Redis是纯粹的缓存，不能作为主数据存储**
这一认知源于Redis早期定位，但实际上启用AOF+RDB混合持久化后，Redis的数据持久性完全满足许多业务场景需求。Redis Enterprise甚至提供了CRDT（无冲突复制数据类型）支持，可作为地理分布式的主数据库使用。问题不在于"能否持久化"，而在于具体业务对数据容量（内存成本高）和一致性模型的要求是否匹配。

**误区二：单线程模型意味着Redis性能差**
单线程避免了锁竞争和上下文切换开销，配合内存操作和高效的IO多路复用，Redis单实例的实测QPS通常在8万~12万之间（以`SET`/`GET`基准测试为例），远超多数应用的单机并发需求。性能瓶颈往往出现在网络带宽而非CPU，这也是为何Redis 6.0的多线程IO仅处理网络收发而非命令执行。

**误区三：`KEYS *`命令可以在生产环境中使用**
`KEYS pattern`命令的时间复杂度为O(N)，N为数据库中键的总数量，在键数量达到百万级时会阻塞Redis事件循环数百毫秒，导致其他命令全部超时。正确做法是使用`SCAN`命令进行游标分批迭代（时间复杂度仍为O(N)但分散到多次调用），或通过Redis的`keyspace notifications`机制监听特定键的变化。

## 知识关联

**与NoSQL概述的关联**：NoSQL概述中介绍了键值存储（Key-Value Store）作为NoSQL的四大类型之一，Redis是该类型最典型的工程实现，但Redis通过多数据结构突破了纯键值存储的限制，其Sorted Set的跳表结构也是理解Redis高性能范围查询的基础。

**通向分布式缓存的桥梁**：掌握单机Redis的数据结构和持久化原理后，分布式缓存的学习聚焦于Redis Cluster如何通过一致性哈希（实际使用16384个哈希槽CRC16分片）将数据分布在多个节点，以及主从复制（Replication）和哨兵（Sentinel）机制如何保障高可用性。单机Redis的`maxmemory`和淘汰策略直接对应分布式场景下的容量规划决策。