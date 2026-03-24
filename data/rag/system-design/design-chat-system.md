---
id: "design-chat-system"
concept: "设计聊天系统"
domain: "ai-engineering"
subdomain: "system-design"
subdomain_name: "系统设计"
difficulty: 8
is_milestone: false
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 设计聊天系统

## 概述

聊天系统是支持用户之间实时或近实时文字（及富媒体）交换的网络服务，其设计需同时满足低延迟消息投递、海量并发连接管理与消息持久化三大目标。与普通请求-响应式API不同，聊天系统要求服务端主动向客户端推送消息，因此连接管理模型与传统HTTP服务有本质区别。

现代大规模聊天系统以2011年Facebook Chat迁移为重要技术节点——Facebook将聊天后端从轮询架构迁移至基于Erlang的长连接集群，支撑了超过7亿用户的并发在线。WhatsApp在2014年被收购时，仅用约50台服务器处理每天180亿条消息，依靠的是FreeBSD + Erlang/OTP的高并发模型。这些工程实践确立了聊天系统设计中"连接层与消息存储层分离"的主流架构范式。

聊天系统在AI工程领域的重要性在于：LLM驱动的对话产品（如ChatGPT、Claude Web）本质上是聊天系统的特例，但额外引入了流式Token推送（Server-Sent Events / WebSocket streaming）和会话上下文管理需求，使得传统聊天系统的设计决策直接影响AI产品的用户体验。

---

## 核心原理

### 1. 消息投递模型：推拉模式选择

聊天系统消息投递存在三种基础模式：

- **客户端轮询（Short Polling）**：客户端每隔固定时间（如500ms）向服务器请求新消息。实现简单但浪费带宽，不适合大规模场景。
- **长轮询（Long Polling）**：客户端发起请求后服务器挂起连接直到有新消息或超时（通常20–30秒）。减少了无效请求，但每条消息仍需重新建立HTTP连接。
- **WebSocket全双工连接**：客户端与服务器通过HTTP Upgrade握手建立持久双向通道，服务器可主动推送，延迟可低至10–50ms。这是微信、Slack、Discord等主流产品的选择。

消息投递的可靠性依赖**消息确认（ACK）机制**：发送方将消息存入服务器后返回服务器端消息ID（`server_msg_id`），接收方客户端收到消息后回发ACK，服务器将该消息标记为"已投递"。若超时未收到ACK，服务器重试投递。为避免客户端重复展示，消息需携带幂等标识，通常由客户端生成UUID（`client_msg_id`），服务端据此去重。

### 2. 消息存储与数据模型

聊天系统的读写比例决定了存储方案选择。单聊（1:1）场景写多读少；群聊（Group Chat）写少读多（一条消息需推送给N个接收方）。

**单聊消息表**典型结构：

```
message_id   BIGINT       -- 全局唯一，通常用Snowflake算法生成
channel_id   BIGINT       -- 由两个用户ID排序后哈希生成
sender_id    BIGINT
content      TEXT
created_at   TIMESTAMP
status       TINYINT      -- 0=发送中, 1=已发送, 2=已读
```

消息ID生成推荐使用**Snowflake算法**（Twitter，2010年开源）：64位整数，由41位毫秒时间戳 + 10位机器ID + 12位序列号组成，单机每毫秒可生成4096个唯一ID，天然有序，适合按时间分页查询。

存储选型上，Facebook Messenger早期使用HBase（LSM树结构）存储消息，利用其顺序写性能；Discord在2023年将消息存储从Cassandra迁移至ScyllaDB，将P99延迟从40ms降至15ms。对于AI聊天产品，会话（Session）表还需存储`system_prompt`字段和`token_count`以控制上下文窗口。

### 3. 连接层架构：Chat Server设计

由于WebSocket连接是有状态的，聊天服务无法像无状态HTTP服务那样简单水平扩展。典型架构采用**专用连接服务器（Chat Server）集群 + 消息队列**解耦：

```
Client A → [WebSocket] → Chat Server 1 ─┐
                                         ├→ Message Queue (Kafka/RabbitMQ) → Notification Service
Client B → [WebSocket] → Chat Server 2 ─┘
                                         ↓
                                    Message DB
```

当Client A（连接Chat Server 1）发消息给Client B（连接Chat Server 2）时，Server 1将消息写入数据库并发布到消息队列，Server 2消费队列事件后通过WebSocket推送给Client B。**服务发现层**（通常是Redis）维护`user_id → server_id`的映射，每次用户建立连接时写入，断线时删除。

群聊场景下，若群组有5000人同时在线，一条消息需要扇出（Fan-out）到5000个连接。Discord采用"写时扩散"模型：消息写入后异步任务并行推送，而非同步等待所有接收方确认，以牺牲少量实时性换取系统吞吐量。

### 4. 在线状态（Presence）服务

用户在线状态是聊天系统中独立的高频读写服务。每个用户的心跳包（通常每5秒一次）更新Redis中的`user:{id}:last_heartbeat`时间戳，TTL设为10秒。读取时若TTL已过期则判定为离线。

Presence服务不能与Chat Server合并，因为其读写量级不同：10万在线用户每5秒产生2万次写操作，但"查看某联系人是否在线"的读操作频率更高，需独立缓存层承载。

---

## 实际应用

**场景一：设计一个支持100万并发用户的单聊系统**

- 假设每个WebSocket连接占用约50KB内存（含读写缓冲区），100万连接需要约50GB内存，因此需要约10–20台Chat Server（每台32GB可用内存）。
- 消息写入QPS估算：假设每用户每分钟发2条消息，则峰值写入约33,000 QPS，需使用MySQL分库分表或Cassandra多节点集群。
- Kafka分区数量设置为`Chat Server数量 × 2`，确保每个Chat Server至少有一个独立分区消费，避免消费竞争。

**场景二：AI流式对话系统**

ChatGPT Web使用Server-Sent Events（SSE）而非WebSocket实现Token流式输出。SSE是单向HTTP长连接，服务端以`data: {token}\n\n`格式逐Token推送，客户端无需维护双向通道，架构更简单。但用户发送消息仍是普通POST请求，形成"POST请求 + SSE流式响应"的混合模式。上下文管理需在每次请求时将历史消息截断至模型的最大上下文长度（如GPT-4的128K tokens），截断策略通常保留最新消息并丢弃早期消息。

---

## 常见误区

**误区一：WebSocket可以直接部署在传统HTTP负载均衡器后面**

WebSocket连接是长连接，若使用按请求轮询的L7负载均衡（如Nginx默认配置），同一用户的不同消息可能被路由到不同Chat Server，导致消息乱序或丢失。正确做法是在WebSocket握手阶段使用**基于`user_id`的一致性哈希（Consistent Hashing）**路由，确保同一用户始终连接到同一Chat Server，或将服务发现逻辑下沉到客户端（客户端查询接入层后直连指定Chat Server IP）。

**误区二：群聊消息存储应与单聊相同，为每个接收方存一份消息副本（Fanout on Write）**

对于大型群聊（如500人群组），写时扇出意味着一条消息产生500条数据库写入，在消息量大时会造成写入风暴。业界普遍采用"消息存一份 + 维护每用户的已读指针（Read Pointer）"模式：消息表只存一条记录，`user_last_read`表记录每个用户在该群组中已读到的最新`message_id`，读取时按时间戳范围查询消息表，客户端本地比对已读指针渲染已读/未读状态。

**误区三：消息ID直接使用数据库自增主键即可**

数据库自增ID在分布式环境下需要全局锁，严重影响写入吞吐。更重要的是，自增ID在多数据中心部署时会产生冲突。应使用Snowflake或ULIDv的方案：ULID（Universally Unique Lexicographically Sortable Identifier）是一个26字符的字符串，包含48位时间戳 + 80位随机数，兼顾唯一性与字典序排序，适合需要跨数据中心消息排序的场景。

---

## 知识关联

本主题直接建立在**WebSocket实时通信**的基础上——WebSocket的握手协议（HTTP 101 Switching Protocols）、帧格式（最大帧大小125字节控制帧 / 64KB数据帧）和心跳机制（Ping/Pong帧）是聊天系统连接层的底层机制，必须理解才能排查连接断线和消息丢失问题。

**系统设计入门**中的CAP定理在聊天场景中有具体体现：消息投递要求AP（可用性 + 分区容错），即使数据库发生分区，用户仍应能发送消息（消息先缓存于发送方客户端，网络恢复后补发），而非因追求强一致性
