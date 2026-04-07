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
updated_at: 2026-03-31
---

# 分布式缓存

## 概述

分布式缓存是将缓存数据分散存储在多个独立节点上的系统架构，通过一致性哈希（Consistent Hashing）等算法将键空间均匀映射到各节点，从而突破单机内存容量上限并提供横向扩展能力。与单机缓存（如进程内的 Guava Cache）不同，分布式缓存的所有应用实例共享同一份数据视图，避免了各节点之间缓存数据不一致的问题。

分布式缓存的工程实践兴起于 2000 年代中期。Memcached 由 Brad Fitzpatrick 于 2003 年为 LiveJournal 开发，是最早被大规模采用的开源分布式缓存系统；Redis 则于 2009 年由 Salvatore Sanfilippo 发布，在 Memcached 的基础上增加了持久化、多数据结构和主从复制能力。如今 Redis Cluster 已成为 AI 推理服务、推荐系统特征存储等场景的标准组件。

在 AI 工程场景中，分布式缓存承担着两类关键职责：一是缓存模型推理结果（如 Embedding 向量、分类标签），将重复请求的延迟从数百毫秒降低到 1 毫秒以内；二是作为特征存储（Feature Store）的在线服务层，为实时推理提供低延迟的特征查询，替代每次查询数据库带来的高延迟。

---

## 核心原理

### 一致性哈希与数据分片

分布式缓存使用一致性哈希将键映射到特定节点，核心公式为：

```
node = hash(key) mod 2^32
```

将值域 [0, 2³²-1] 排列成一个虚拟环，每个物理节点占据环上若干虚拟节点（virtual node，通常每个物理节点配置 150～200 个虚拟节点）。当新增或删除一个节点时，只需迁移约 `K/N` 比例的键（K 为总键数，N 为节点数），而非重新哈希全部数据。Redis Cluster 采用的是固定 16384 个哈希槽（hash slot）的简化方案：`slot = CRC16(key) mod 16384`，每个主节点负责一段连续槽范围。

### 缓存一致性与失效策略

分布式环境下缓存失效是最复杂的问题。常见策略包括：

- **TTL 过期**：为每个键设置生存时间（如 `SET feature:user:123 ... EX 300`），到期后由 Redis 的惰性删除（访问时检查）和周期性扫描共同回收；Redis 每 100ms 随机采样 20 个带 TTL 的键，若过期比例超过 25% 则继续扫描。
- **Write-Through**：写操作同时更新数据库和缓存，保证强一致性，代价是写延迟增加。
- **Cache-Aside（旁路缓存）**：应用层负责先查缓存、未命中再查 DB 并回填，是 AI 推荐系统中最常见的模式，但存在"先删缓存还是先更新 DB"的竞态窗口。

解决缓存与数据库双写不一致的工程方案是"延迟双删"：先删缓存 → 更新 DB → 等待约 500ms → 再次删缓存，将不一致窗口压缩到毫秒级。

### 缓存击穿、穿透与雪崩

这三种故障模式在分布式场景下危害更大：

| 故障类型 | 触发条件 | 工程解法 |
|---|---|---|
| 缓存击穿 | 热点键恰好过期，大量并发请求同时打到 DB | 互斥锁（setnx）或逻辑过期（不设 TTL，在 value 中存储过期时间） |
| 缓存穿透 | 查询不存在的键，缓存永远未命中 | 布隆过滤器（Bloom Filter，误判率通常设为 0.01%）或缓存空值 |
| 缓存雪崩 | 大量键同时过期或节点宕机 | TTL 加随机抖动（如 `300 + random(60)` 秒）、Redis Cluster 多副本 |

### 数据结构选择对 AI 系统的影响

Redis 提供的 Hash、Sorted Set、String 等原生数据结构直接影响 AI 系统的特征查询效率：

- **Hash**：`HGETALL feature:user:123` 一次性取回用户全量特征，时间复杂度 O(N)，适合特征维度固定的场景。
- **Sorted Set**：以用户行为分数为权重，`ZREVRANGE feed:user:123 0 49` 获取 Top-50 候选集，是 Feed 流预计算的基础操作，时间复杂度 O(log N + M)。
- **String + MessagePack/Protobuf**：序列化 Embedding 向量后存储，相比 JSON 序列化节省 40%～60% 的内存占用。

---

## 实际应用

**AI 推荐系统特征存储**：某电商平台将用户实时行为特征（近 1 小时点击序列、购物车状态）存入 Redis Cluster，TTL 设为 3600 秒。模型推理服务每次请求通过 `pipeline` 批量获取 50 个用户的特征，将特征查询 P99 延迟从原来 MySQL 查询的 80ms 降至 2ms，满足在线推理 <10ms 的 SLA 要求。

**LLM 推理结果缓存（Semantic Cache）**：对完全相同的 Prompt 进行 MD5 哈希后作为键，将 GPT-4 的输出缓存 24 小时，可将重复查询（如 FAQ 类问题）的 API 调用成本降低约 30%。更进一步的语义缓存方案将 Prompt 的 Embedding 向量存入 Redis Stack 的向量索引，对余弦相似度 >0.95 的请求复用缓存结果。

**模型预热（Cache Warming）**：在推理服务上线前，离线任务预先将高频用户的特征批量写入 Redis，避免冷启动阶段缓存命中率为 0 导致的流量全部压到 DB 的风险，这一过程通常在流量切换前 30 分钟完成。

---

## 常见误区

**误区一：认为分布式缓存天然支持事务**。Redis 的 `MULTI/EXEC` 提供的是乐观锁机制，而非 ACID 事务。在 Redis Cluster 模式下，`MULTI/EXEC` 只能在同一个哈希槽内的键上执行，跨槽操作会直接报错（`CROSSSLOT Keys in request don't hash to the same slot`）。解决方案是使用 HashTag（如 `{user:123}:feature` 和 `{user:123}:score`）强制同一用户的键落在同一槽。

**误区二：缓存容量越大命中率越高**。命中率由访问模式的热度分布（Zipf 分布）决定，而非单纯由容量决定。实测中 Redis 使用 `allkeys-lru` 淘汰策略时，将内存从 8GB 扩大到 32GB，若热点键集中在头部 5% 的数据，命中率提升往往不足 3%，而成本增加了 4 倍。正确做法是先用 `redis-cli --hotkeys` 分析热点分布，再决定是否扩容。

**误区三：以为删除缓存能立即保证一致性**。在主从复制架构下，Redis 主节点删除键后，同步到从节点存在 1～10ms 的复制延迟。若应用读请求路由到从节点，仍可能读到旧值。对于强一致性要求的场景（如秒杀库存），必须将读写都路由到主节点，或使用 `WAIT numreplicas timeout` 命令等待副本确认。

---

## 知识关联

**前置知识衔接**：Redis 基础中的单机数据结构操作（GET/SET/HGETALL/ZADD）和缓存策略（LRU/LFU/TTL）是分布式缓存的操作基础，但分布式场景额外引入了网络分区（Network Partition）和节点故障处理逻辑，CAP 定理在此直接适用——Redis Cluster 默认选择 AP（可用性优先），在网络分区时允许读到旧数据。

**下一阶段应用**：设计 Feed 流系统时，分布式缓存承担着 Timeline 预计算结果存储的核心角色。推（Push）模型将博主发帖时将内容 Fan-out 写入所有关注者的 Feed 队列（Redis List 或 Sorted Set），拉（Pull）模型则在用户请求时实时聚合并缓存合并结果，两种模型对 Redis 的写放大和读放大特性有截然不同的要求，需要结合本文的数据结构选择原则进行设计取舍。