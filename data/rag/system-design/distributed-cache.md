---
id: "distributed-cache"
concept: "分布式缓存"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 7
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 分布式缓存

## 概述

分布式缓存是将缓存数据分散存储在多个物理节点上的系统架构，与单机缓存（如进程内缓存 Caffeine）的根本区别在于：数据通过一致性哈希或分片算法分布在网络中的多台服务器上，任意客户端均可通过网络访问完整的缓存空间。典型的分布式缓存系统包括 Redis Cluster、Memcached 集群和 Apache Ignite，它们可以将缓存容量从单机的数十 GB 扩展到集群的数十 TB。

分布式缓存的工程价值在于两个可量化的指标：**读吞吐量的水平扩展**和**单点故障的消除**。以 Redis Cluster 为例，单节点 QPS 约为 10 万次/秒，6 节点集群可线性扩展至 60 万次/秒读操作。在 AI 工程场景中，模型推理服务需要频繁读取特征向量、Embedding 结果和预计算分数，分布式缓存可将这些高频读请求的延迟从数据库的 50-200ms 压缩至 0.5-2ms。

该领域在 2010 年前后随着互联网规模应用的爆发而成熟——Facebook 在 2013 年发表的论文《Scaling Memcache at Facebook》揭示了其使用数千台 Memcached 服务器支撑每秒数十亿请求的架构细节，成为业界分布式缓存设计的重要参考基准。

## 核心原理

### 数据分片与一致性哈希

分布式缓存的核心挑战是决定某个 Key 存储在哪个节点上。简单取模（`node = hash(key) % N`）在节点数 N 变化时会导致几乎所有 Key 的映射改变，引发缓存雪崩。**一致性哈希**（Consistent Hashing）将哈希空间构造为 0 到 2³²-1 的环形结构，增减节点时只影响相邻区间的 Key，平均迁移比例为 1/N。

Redis Cluster 使用另一种方案——**哈希槽（Hash Slot）**：将 key 空间划分为固定的 16384 个槽，计算公式为 `slot = CRC16(key) % 16384`，每个节点负责管理一定范围的槽。这使得槽的迁移可以细粒度控制，且槽到节点的映射表存储在集群内所有节点上，客户端可通过 `CLUSTER SLOTS` 命令获取完整路由信息。

### 缓存一致性与失效策略

分布式缓存面临**写后一致性**问题：当数据库数据更新时，缓存中的旧数据需要在一定时间窗口内失效或更新。常见的处理模式有三种：

- **Cache-Aside（旁路缓存）**：应用程序先写数据库，再删除缓存，由下次读取重新填充。这是 AI 推荐系统中最常用的模式，适合读多写少场景。
- **Write-Through**：写操作同步更新数据库和缓存，保证强一致性，但写延迟翻倍。
- **Write-Behind（Write-Back）**：先写缓存，异步批量刷入数据库，写性能最高但存在数据丢失风险，适合用户行为日志等允许短暂丢失的场景。

设置合理的 TTL（Time To Live）是防止缓存击穿的关键。为避免大量 Key 在同一时刻集中过期（缓存雪崩），工程上通常在基准 TTL 上增加随机抖动：`actual_ttl = base_ttl + random(0, base_ttl * 0.2)`。

### 分布式缓存的三大故障模式

**缓存穿透**：请求的 Key 在缓存和数据库中均不存在，每次都会打穿到数据库。解决方案是使用布隆过滤器（Bloom Filter）在缓存层前置拦截，或对不存在的 Key 缓存空值并设置短暂 TTL（如 30 秒）。

**缓存击穿**：某个热点 Key 在高并发时恰好过期，导致大量请求同时穿透到数据库。解决方案是使用 Redis 的 `SET key value NX PX milliseconds` 命令实现分布式互斥锁，保证同一时刻只有一个请求去重建缓存。

**缓存雪崩**：大量 Key 同时过期或缓存节点宕机，导致请求涌入数据库。除 TTL 抖动外，还需配合**熔断限流**（如 Sentinel 框架）和**主从复制**（Redis Sentinel 模式或 Cluster 模式）双重保障。

## 实际应用

**AI 推荐系统的特征缓存**：用户实时特征（如最近30分钟的点击序列）存储在 Redis Hash 结构中，Key 为 `user_feature:{user_id}`，TTL 设置为 1800 秒。模型服务批量使用 `MGET` 或 Pipeline 一次性获取多个用户的特征，将 N 次网络往返压缩为 1 次，延迟从 N×1ms 降至约 2ms。

**Embedding 向量缓存**：文本 Embedding（如 1536 维的 OpenAI text-embedding-ada-002 输出）计算代价高昂，将相同文本的 Embedding 结果以二进制格式（`numpy.tobytes()`）存入 Redis String，可节省 60-80% 的重复推理开销。Key 设计为 `emb:{model_version}:{md5(text)}`，通过引入 model_version 前缀确保模型升级后自动失效旧缓存。

**Session 级对话上下文**：LLM 应用中，用户的多轮对话历史需要在无状态的推理节点之间共享。使用 Redis List 结构存储对话消息，`LPUSH` 写入新消息，`LRANGE key 0 19` 取最近20轮，TTL 设置为 3600 秒，实现了水平扩展的对话状态管理。

## 常见误区

**误区一：分布式缓存可以替代数据库的持久化**。Redis 的 RDB（定期快照）和 AOF（追加日志）持久化机制虽然存在，但分布式缓存的设计目标是**加速读取**而非**持久存储**。在 Redis Cluster 中，即使启用了 AOF，主节点宕机到从节点选举完成之间（通常需要 15-30 秒的故障检测时间）仍可能丢失这段时间内的写入数据，所以不能用缓存替代数据库作为业务数据的单一来源。

**误区二：缓存节点越多性能越高**。分布式缓存的性能瓶颈往往在于**客户端到集群的网络跳数**和**连接池管理**，而非节点数量。Redis Cluster 要求客户端在 MOVED 重定向时重新建立连接，若客户端未缓存槽位路由表，频繁的 MOVED 重定向会将延迟从 1ms 推高至 10ms 以上。实践中应使用支持**智能路由**的客户端库（如 Java 的 Lettuce 或 Python 的 redis-py-cluster）来本地缓存槽位映射。

**误区三：对所有数据设置相同的 TTL**。不同业务数据的时效性差异极大——用户实时行为特征可能只需缓存 5 分钟，而商品基础信息可以缓存 24 小时。统一 TTL 会导致高频变更数据的一致性问题或低频变更数据的无效缓存重建开销。应根据数据的**写入频率**和**一致性容忍度**分层设置 TTL。

## 知识关联

分布式缓存建立在**缓存策略**（LRU、LFU 等淘汰算法）和 **Redis 基础**（数据结构、持久化、主从复制）的知识之上。理解 Redis 的单线程事件循环模型（Redis 6.0 以前的 I/O 线程和命令执行均为单线程）是解释为何 Redis 在高并发下仍能保持低延迟的关键——避免了多线程锁竞争，但也意味着单个慢命令（如 `KEYS *` 或对百万成员的 `SMEMBERS`）会阻塞整个实例。

掌握分布式缓存后，下一个学习目标是**设计 Feed 流系统**。Feed 流的核心挑战——推模式（Fan-out on Write）还是拉模式（Fan-out on Read）——本质上是缓存预计算与实时聚合的权衡。推模式需要将内容预先写入每个关注者的 Redis List（`LPUSH timeline:{user_id} post_id`），对于拥有数百万粉丝的大V账号会产生严重的写放大问题（1条内容 × 1,000,000 个关注者 = 100万次 Redis 写操作），这正是分布式缓存扩展性问题在真实系统中的典型体现。
