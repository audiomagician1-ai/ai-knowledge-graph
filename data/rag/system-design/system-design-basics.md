---
id: "system-design-basics"
concept: "系统设计入门"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 6
is_milestone: false
tags: ["设计"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.364
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 系统设计入门

## 概述

系统设计（System Design）是指在给定功能需求和非功能需求的约束下，规划软件系统的架构、组件、接口与数据流动方式的工程过程。这一领域在2010年代随着互联网公司大规模招聘进入技术面试主流，Alex Xu的《System Design Interview》（2020）将其系统化整理，使"系统设计面试"成为Google、Meta、Amazon等公司工程师评估的标准环节。系统设计不同于算法设计——算法设计强调时间复杂度和空间复杂度的最优化，而系统设计关注的是在真实工程约束下（网络延迟、硬件成本、团队规模）协调多个分布式组件完成业务目标。

系统设计的核心挑战在于同时满足两类需求：**功能需求**（Functional Requirements，如"用户能发布140字的推文"）和**非功能需求**（Non-Functional Requirements，如"系统的读写比为100:1，需支持每秒10万次读请求"）。Martin Fowler在《Patterns of Enterprise Application Architecture》（2002）中指出，大多数系统失败并非因为功能缺失，而是因为在扩展阶段无法应对真实流量模式。掌握系统设计入门意味着能够从一个模糊的业务需求出发，完成从估算规模、选择存储方案、设计API接口到拆分服务的完整链路。

---

## 核心原理

### 容量估算（Back-of-the-Envelope Estimation）

系统设计的第一步是建立数量级认知。以下是工程师必须熟记的基础数字，源自Jeff Dean的著名演讲"Numbers Every Engineer Should Know"[Dean, 2012]：

| 操作 | 延迟 |
|------|------|
| L1 缓存访问 | 0.5 ns |
| 内存读取 | 100 ns |
| SSD随机读取 | 100,000 ns（0.1 ms） |
| 机械硬盘寻道 | 10,000,000 ns（10 ms） |
| 同数据中心网络往返 | 500,000 ns（0.5 ms） |

以设计一个类Twitter系统为例，容量估算过程如下：假设月活用户3亿，日活用户1.5亿，每用户每天发2条推文，则写入QPS（Queries Per Second）为：

$$QPS_{write} = \frac{1.5 \times 10^8 \times 2}{86400} \approx 3472 \text{ TPS}$$

若读写比为100:1，则：

$$QPS_{read} = 3472 \times 100 \approx 347{,}200 \text{ TPS}$$

这意味着单台MySQL服务器（约1000 TPS读取上限）完全无法支撑，必须引入读写分离和缓存层。

### 四层架构模型与数据存储选型

入门级系统设计通常围绕四个层次展开：客户端层、负载均衡层、应用服务层、数据持久层。其中数据存储选型是最关键的决策点：

**关系型数据库（SQL）** 适用于需要ACID事务的场景，如金融转账。PostgreSQL在写入密集场景下默认使用WAL（Write-Ahead Log）保证持久性，单机写入吞吐约1000-5000 TPS。

**非关系型数据库（NoSQL）** 分为四类：
- 键值存储（Redis）：内存级别，读写延迟<1ms，适合会话缓存
- 文档数据库（MongoDB）：适合用户Profile等半结构化数据
- 列族数据库（Cassandra）：写入吞吐极高，LinkedIn使用Cassandra每天处理超过1万亿次写操作
- 图数据库（Neo4j）：适合社交关系图谱，六度分隔查询效率远高于SQL JOIN

选择依据可用CAP定理描述[Brewer, 2000]：在网络分区（P）不可避免的分布式系统中，一致性（C）和可用性（A）只能二选一。Cassandra选择AP，HBase选择CP。

### 水平扩展与缓存策略

**水平扩展（Scale Out）** 指通过增加服务器节点来分担负载，与**垂直扩展（Scale Up，增加单机CPU/内存）** 相对。前者是互联网系统的主流方案，因为垂直扩展存在物理上限且成本呈指数增长。

缓存是降低数据库压力的核心手段。以旁路缓存（Cache-Aside Pattern）为例，工作流程如下：

```python
def get_user(user_id: str) -> dict:
    # 1. 先查缓存（Redis）
    cache_key = f"user:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 2. 缓存未命中，查数据库
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    
    # 3. 写入缓存，TTL设为3600秒
    redis_client.setex(cache_key, 3600, json.dumps(user))
    return user
```

缓存命中率（Cache Hit Rate）是衡量缓存效果的关键指标：

$$\text{命中率} = \frac{\text{缓存命中次数}}{\text{总请求次数}} \times 100\%$$

Facebook的Memcached集群在高峰期缓存命中率维持在99%以上，将数据库读取压力降低了约100倍[Nishtala et al., 2013]。

### 数据库分片（Sharding）

当单台数据库无法存储全量数据时，需要对数据水平切分。常见的分片键（Shard Key）策略包括：

- **哈希分片**：$\text{shard\_id} = \text{hash}(user\_id) \mod N$，数据分布均匀但范围查询困难
- **范围分片**：按user_id区间（0-1M, 1M-2M...）划分，支持范围查询但可能导致热点
- **地理分片**：按用户所在地区划分，降低跨大洲延迟

哈希分片最大的问题是**再哈希问题**：当N变化时需迁移大量数据。**一致性哈希（Consistent Hashing）** 是解方案，节点变化时只需迁移相邻数据，平均迁移比例为 $\frac{1}{N}$，而非 $\frac{N-1}{N}$。

---

## 实际应用

**设计URL短链接系统（如bit.ly）** 是系统设计入门的经典练习题。核心问题是：如何将`https://verylongurl.com/path?param=value`映射到`https://bit.ly/abc123`？解决方案是用62进制（a-z, A-Z, 0-9）编码数字ID，6位62进制字符可表示 $62^6 \approx 568$ 亿个URL，支撑bit.ly类服务运行数十年。存储层选择KV数据库（shortCode → originalURL），读写比极高（约1000:1），因此Redis缓存热门短链接是标配。

**设计通知推送系统（如App Push Notification）** 涉及与设备平台的对接：iOS使用APNs（Apple Push Notification service），Android使用FCM（Firebase Cloud Messaging）。每条推送消息的payload大小有严格限制——APNs限制4KB，FCM限制4KB，超出需截断或使用"静默推送+拉取"模式。每天全球推送量达数千亿条，系统架构必须支持异步消息队列（如Kafka）解耦发送端和渠道网关。

**CDN内容分发网络** 是静态资源加速的标准方案。Cloudflare在全球300+个PoP（Point of Presence）节点缓存静态文件，使欧洲用户访问美国源站的延迟从200ms降至20ms以内。设计包含CDN的系统时，需要设置合理的Cache-Control头（如`max-age=86400`），并在内容更新时通过URL版本号（`/style.v3.css`）实现缓存失效。

---

## 常见误区

**误区一：认为"加缓存"可以解决所有性能问题。** 缓存只对读多写少的数据有效。对于写频繁的数据（如实时计数器），频繁失效缓存反而增加了系统复杂度和延迟。正确做法是用Redis的INCR原子命令直接维护计数，而非缓存MySQL的COUNT结果。

**误区二：过早使用微服务架构。** 初学者往往认为系统设计"越分布式越好"。然而Netflix将单体应用迁移至微服务历时数年，前提是已有数千万规模用户和成熟的运维能力。对于日活100万以下的系统，单体应用（Monolith）配合读写分离往往是最优解，微服务引入的服务发现、链路追踪、分布式事务等复杂度不可低估。

**误区三：混淆延迟（Latency）和吞吐量（Throughput）的优化目标。** 这两者有时相互冲突：批处理（Batch Processing）可以提升吞吐量，但会增加单次请求延迟；而并发数减少可以降低P99延迟，但会降低整体吞吐量。系统设计时必须根据业务场景明确优先级——支付系统优先保证P99延迟<500ms，日志分析系统则优先最大化吞吐量。

---

## 思考题

1. 假设你在设计一个全球用户的图片分享平台，预估每天上传图片1000万张，每张平均3MB。请计算每年所需存储容量，并说明为什么需要对象存储（如Amazon S3）而非MySQL BLOB字段来存储图片二进制数据？

2. 一个新闻网站在某热点事件爆发时流量突增100倍（从1000 QPS到100,000 QPS），现有架构是单台Nginx + 单台MySQL。你会按什么优先级逐步引入哪些组件来应对这次流量冲击？请给出至少三个步骤并解释每步解决的瓶颈。

3. 设计一个"已读回执"功能（类似微信的"已读"标记），需要在消息发送后，当接收方打开会话时，发送方能看到"已读"标记。假设系统有5000万日活用户，每人每天发送50条消息，请描述数据模型设计和消息状态更新的技术方案，特别说明如何避免对数据库产生每秒250万次的写入冲击。
