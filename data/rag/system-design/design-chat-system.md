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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 设计聊天系统

## 概述

聊天系统是一类支持用户实时或异步文字消息传递的分布式应用，按规模可分为1对1私聊、群聊和频道广播三种模式。其设计难点在于需要同时保证消息的强一致性（不丢消息、不乱序）、低延迟（端到端 P99 延迟通常要求 < 500ms）以及对亿级并发连接的水平扩展能力。

聊天系统的工业化起点可追溯到1988年芬兰大学生 Jarkko Oikarinen 发明的 IRC（Internet Relay Chat）协议。此后，2000年代 MSN Messenger 和 QQ 将服务推向大众；2013年 WhatsApp 对外披露其单服务器处理 **200万 TCP 连接**的实践（Beam VM + Erlang/OTP 架构），彻底刷新了工程师对聊天系统可扩展性的认知边界。微信、Slack、Discord 等现代系统则进一步将消息队列、分布式 ID 生成、多端同步等机制标准化。

掌握聊天系统设计对 AI 工程师尤为重要：大型语言模型（LLM）的对话接口（如 ChatGPT、Claude API）本质上是一套流式聊天系统——服务端通过 Server-Sent Events（SSE）逐 token 推送响应，客户端需维护 session 状态并支持多轮历史回放，这与传统聊天系统的核心架构高度同构。本文架构参考 Alex Xu《System Design Interview》(Alex Xu, 2020, ByteByteGo) 第12章，并结合微信、Slack 等公开工程博客进行扩展。

---

## 核心原理

### 1. 连接层协议选型

聊天系统通常在以下三种协议中做权衡：

| 协议 | 方向 | 典型延迟 | 适用场景 |
|------|------|----------|----------|
| HTTP 长轮询（Long Polling） | 客户端驱动 | 1～30s | 兼容老旧浏览器，低频通知 |
| WebSocket（RFC 6455） | 全双工 | < 100ms | 主流实时聊天 |
| SSE（Server-Sent Events） | 服务端单向推送 | < 200ms | LLM 流式输出、只读通知 |

WebSocket 在握手阶段通过 HTTP `Upgrade: websocket` 头完成协议升级，之后数据以帧（Frame）格式传输，帧头部最小仅 **2 字节**，相比 HTTP 请求头（通常 500～800 字节）节省约 **95%** 的协议开销。每台聊天服务器（Chat Server）维持大量长连接，通常使用基于 `epoll`（Linux）或 `kqueue`（macOS/BSD）的 I/O 多路复用模型（如 Netty 4.x、Node.js libuv），单机可承载 **10 万～100 万**并发连接，核心原因是连接本身在内核态仅占用约 **3.5KB** 内存（socket 缓冲区 + file descriptor）。

### 2. 消息 ID 生成与排序保证

消息乱序是聊天系统最常见的线上故障。工业界主要采用两类方案：

- **Snowflake ID（雪花算法）**：由 Twitter 于2010年开源，64位整数，结构为：

$$\text{ID} = \underbrace{0}_{1\text{位符号}} \| \underbrace{t - t_0}_{41\text{位毫秒时间戳}} \| \underbrace{m}_{10\text{位机器ID}} \| \underbrace{s}_{12\text{位序列号}}$$

其中 $t_0$ 为自定义纪元（epoch），41 位时间戳可支持约 **69 年**不溢出（$2^{41} \approx 2.2 \times 10^{12}$ 毫秒），单机每毫秒最多生成 $2^{12} = 4096$ 个有序 ID。

- **数据库自增序列**：在单聊场景中，可为每个会话（Conversation）维护一个独立的单调递增 `seq_id`，由 Redis `INCR` 命令生成（单线程原子操作，吞吐量 > 10万 QPS），保证会话内消息的严格顺序。

对于群聊，若使用 Snowflake，需注意不同机器产生的 ID 在毫秒边界因时钟偏差（通常 < 10ms）可能出现微小乱序，客户端需在展示前按 ID 进行二次排序。

### 3. 消息存储模型：扇出策略（Fan-out）

聊天系统有两种核心存储模型，选择依据是读写比和群组规模：

**写扩散（Fan-out on Write）**：消息发送时立即写入每个接收者的消息收件箱（Inbox）。读取时只查询自己的 Inbox，速度极快，但若群组有 N 个成员，写入放大系数为 **N 倍**。微信早期群聊上限 500 人，使用写扩散；超过此规模切换策略。

**读扩散（Fan-out on Read）**：消息只写入一份全局存储，每个用户读取时拉取自己有权限的所有会话消息。写入成本为 **O(1)**，但读取时需合并多个数据源，延迟较高。适用于 Slack 频道（频道成员可达数万人）。

**混合策略（Hybrid）**：Facebook Messenger 和微信均采用混合策略——普通群（< 500 人）用写扩散，超大群/广播频道用读扩散，以 500 人为阈值动态切换。

---

## 关键公式与存储估算

在系统设计面试中，存储容量估算是必考环节。以一个 **DAU = 5000 万**的聊天应用为例：

- 每用户每天发送 **40 条**消息，消息平均大小 **100 字节**（纯文本）
- 每日新增消息数：$5000万 \times 40 = 2 \times 10^9$ 条
- 每日文本消息存储：$2 \times 10^9 \times 100B = 200GB/\text{天}$
- 多媒体消息（图片）占比约 10%，每张平均 **300KB**，则每日图片存储：

$$200GB \times 10\% \div 100B \times 300KB \approx 60TB/\text{天}$$

因此对象存储（如 AWS S3）的容量规划远超数据库。消息数据库选型通常使用 **HBase** 或 **Cassandra**，其列族（Column Family）模型天然支持按 `(conversation_id, message_id)` 的范围查询，Facebook Messenger 使用 HBase 存储消息，单集群写入吞吐量可达 **数百万 QPS**（参见 Facebook Engineering Blog, 2010）。

```python
# 消息表示例：Cassandra 数据模型（CQL）
CREATE TABLE messages (
    conversation_id  UUID,
    message_id       BIGINT,    -- Snowflake ID，天然有序
    sender_id        BIGINT,
    content          TEXT,
    msg_type         TINYINT,   -- 0=文本, 1=图片, 2=文件
    created_at       TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC)
  AND default_time_to_live = 31536000;  -- 消息默认保留1年（秒）
```

上述设计中，`conversation_id` 作为分区键（Partition Key），`message_id` 作为聚簇键（Clustering Key）并按降序排列，支持 O(1) 写入和按时间倒序的高效分页查询。

---

## 实际应用

### 4.1 多端同步与已读回执

现代聊天应用（微信、iMessage）通常需要在手机、PC、Web 多端同步消息。核心机制是**游标同步（Cursor-based Sync）**：每个设备维护一个 `last_delivered_msg_id`，重新上线时向服务器请求 `message_id > last_delivered_msg_id` 的所有消息，批量拉取后更新游标。

已读回执（Read Receipt）的实现：接收方 App 进入会话界面时，客户端发送 ACK 消息 `{conversation_id, last_read_msg_id}` 给服务器，服务器更新 `read_status` 表并通过 WebSocket 将已读状态推送给发送方。WhatsApp 的单勾（已送达）、双勾（已读）状态正是基于此机制，延迟通常 < **200ms**。

### 4.2 LLM 对话系统中的聊天架构

ChatGPT 和 Claude 的 API 流式输出本质上是 SSE 协议的应用。服务端每生成一个 token（约 4 个英文字符）立即推送，格式为：

```
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"你好"},"index":0}]}

data: [DONE]
```

客户端通过 `EventSource` API 监听 `data` 事件，将 token 拼接渲染到界面。相较于等待完整响应的非流式接口（通常需要 5～30s），SSE 流式输出可将**首字延迟（Time-to-First-Token, TTFT）**压缩到 < **500ms**，显著改善用户体验。会话历史需在客户端缓存并在每次请求时携带完整上下文（Prompt），这要求系统设计时预留对话历史的存储与截断策略（超过模型上下文窗口时，保留最近 N 轮或使用摘要压缩）。

### 4.3 水平扩展与服务发现

单台 Chat Server 宕机时，其上所有 WebSocket 连接断开。解决方案是引入**无状态网关层**：客户端连接到负载均衡器（如 Nginx），网关层通过一致性哈希（Consistent Hashing）将同一 `user_id` 路由到固定的 Chat Server 节点，保证同一用户的消息路由稳定。Chat Server 之间通过消息队列（Kafka）解耦：A 服务器上的用户发消息→写入 Kafka Topic→B 服务器消费→推送给 B 上的接收方，跨节点消息延迟约 **10～50ms**。

---

## 常见误区

**误区一：WebSocket 连接数 = 服务器压力**
WebSocket 连接本身是轻量的（内核态约 3.5KB/连接），真正的压力来自**消息处理吞吐量**。一台 8 核服务器空载可维持 100 万连接，但若每秒有 10 万条消息需路由处理，CPU 才会成为瓶颈。因此扩容策略应区分"连接数瓶颈"和"计算瓶颈"。

**误区二：用 MySQL 存储聊天消息**
关系型数据库的行级锁和 B+ 树索引在高并发写入场景下性能急剧下降（通常 > 5000 TPS 即出现明显延迟）。聊天消息的访问模式是**追加写（Append-only）+ 范围读（Range Read）**，与 LSM-Tree 存储引擎（HBase、Cassandra、RocksDB）的特性完美匹配，写入吞吐量可比 MySQL 高出 **5～10 倍**。

**误区三：忽略消息幂等性**
网络重传导致同一条消息被服务器处理多次，会产生重复消息。正确做法是客户端为每条消息生成唯一的 `client_msg_id`（UUID），服务器在写入前检查是否已存在该 ID，实现**幂等写入**。Redis `SET NX`（Set if Not Exists）可在 O(1) 时间内完成去重检查，有效期设置为 **7 天**（覆盖网络抖动的最大重试窗口）。

**误区四：群聊无脑使用写扩散**
当群组规模超过 **1000 人**时，写扩散的放大效应极其严重：1 条消息需写入 1000 个 Inbox，若每秒有 100 条群消息，写入 QPS 瞬间放大到 **10 万 QPS**，数据库极易过载。此时必须切换至读扩散或混合策略。

---

## 知识关联

| 关联概念 | 与本主题的连接点 |
|----------|-----------------|
| **一致性哈希（Consistent Hashing）** | Chat Server 集群扩缩容时，用于最小化连接迁移数量，仅影响 $\frac{1}{N}$ 的用户连接 |
| **Kafka 消息队列** | 解耦跨 Chat Server 的消息路由，保证消息至少一次（At-Least-Once）投递，与 Snowflake ID 配合实现消费端去重 |
| **Redis 发布/订阅（Pub/Sub）** | 