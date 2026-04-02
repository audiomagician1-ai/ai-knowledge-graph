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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 设计聊天系统

## 概述

聊天系统是一类支持用户实时或异步文字消息传递的分布式应用，按规模可分为1对1私聊、群聊和频道广播三种模式。其设计难点在于需要同时保证消息的强一致性（不丢消息、不乱序）、低延迟（端到端 P99 延迟通常要求 < 500ms）以及对亿级并发连接的水平扩展能力。

聊天系统的工业化起点可追溯到1988年芬兰大学生 Jarkko Oikarinen 发明的 IRC（Internet Relay Chat）协议。此后，2000年代 MSN Messenger 和 QQ 将服务推向大众；2013年 WhatsApp 对外披露其单服务器处理 200万 TCP 连接的实践，彻底刷新了工程师对聊天系统可扩展性的认知边界。微信、Slack、Discord 等现代系统则进一步将消息队列、分布式 ID 生成、多端同步等机制标准化。

掌握聊天系统设计对 AI 工程师尤为重要：大型语言模型（LLM）的对话接口（如 ChatGPT、Claude API）本质上就是一套流式聊天系统——服务端通过 Server-Sent Events（SSE）逐 token 推送响应，客户端需维护 session 状态并支持多轮历史回放，这与传统聊天系统的核心架构高度同构。

---

## 核心原理

### 1. 连接层协议选型

聊天系统通常在以下三种协议中做权衡：

| 协议 | 方向 | 适用场景 |
|------|------|----------|
| HTTP 长轮询（Long Polling） | 客户端驱动 | 兼容老旧浏览器，延迟可达秒级 |
| WebSocket | 全双工 | 主流实时聊天，延迟 < 100ms |
| SSE（Server-Sent Events） | 服务端单向推送 | LLM 流式输出、通知系统 |

WebSocket 在握手阶段通过 HTTP Upgrade 头完成协议升级，此后帧（Frame）的头部最小仅 2 字节，比 HTTP 请求头节省约 95% 的开销。每台聊天服务器（Chat Server）维持大量长连接，通常使用基于 epoll/kqueue 的 I/O 多路复用模型（如 Netty、Node.js libuv），单机可承载 10万～100万 并发连接。

### 2. 消息 ID 生成与排序保证

消息乱序是聊天系统最常见的线上故障之一。工业界主要采用两类方案：

- **Snowflake ID（雪花算法）**：由 Twitter 于2010年开源，64位整数，结构为 `1位符号位 + 41位毫秒时间戳 + 10位机器ID + 12位序列号`。同一毫秒内单机可生成 4096 个有序 ID，天然支持按 ID 排序即等价于按时间排序。
- **数据库自增序列**：在单聊场景中，可为每个会话（Conversation）维护一个独立的单调递增 `seq_id`，由数据库的 `AUTO_INCREMENT` 或 Redis `INCR` 命令生成，保证会话内消息的严格顺序。

对于群聊，若使用 Snowflake，需注意不同机器产生的 ID 在毫秒边界可能存在微小乱序（取决于机器时钟偏差，通常 < 10ms），客户端需按 ID 进行二次排序。

### 3. 消息存储模型：Inbox 扇出（Fan-out）

聊天系统有两种核心存储模型：

**写扩散（Push/Fan-out on Write）**：消息发送时立即写入每个接收者的消息收件箱（Inbox）。读取时只需查询自己的 Inbox，速度极快（O(1)读），但写放大严重——若一个群有 1000 人，每条消息产生 1000 次写入。微信群（上限 500人）、Discord 小服务器适合此模式。

**读扩散（Pull/Fan-out on Read）**：消息只写一份到公共时间线（Timeline），用户读取时再聚合相关频道的消息。写入廉价（O(1)写），但读取时需合并多个来源，适合 Slack 频道或 Twitter 早期 Feed 流。

Facebook Messenger 采用混合策略：单聊使用读扩散（只存一份），群聊根据成员数量动态切换——成员数 < 150 使用写扩散，超过 150 切换为读扩散，以平衡读写放大。

### 4. 在线状态服务（Presence Service）

用户的在线/离线状态需要以低延迟广播给联系人。具体机制：

1. 客户端与 Presence Server 维持 WebSocket 心跳，每隔 **5秒** 发送一次 heartbeat。
2. 若 Presence Server 连续 **30秒**（即6次心跳）未收到 heartbeat，则将用户标记为离线，并通过发布/订阅（Pub/Sub）频道向其好友的连接服务器广播状态变更事件。
3. 在线状态存储于 Redis，键格式通常为 `presence:{user_id}`，TTL 设置为 35秒（略大于30秒超时阈值），由每次 heartbeat 刷新 TTL。

对于拥有亿级用户的系统，不可能对每个状态变更进行全量广播。常见优化是仅在用户打开聊天窗口时订阅对方状态，关闭窗口后取消订阅，将 Presence 事件流量降低约 90%。

### 5. 消息可靠投递与重试机制

端到端可靠投递依赖客户端的**临时消息ID（Client-side Message ID，CMID）** 机制：

1. 客户端生成唯一 CMID（通常为 UUID v4），将消息连同 CMID 发送给服务端。
2. 服务端落库后返回服务端生成的 `server_msg_id`，客户端用 `server_msg_id` 替换 CMID。
3. 若网络超时，客户端重试时携带相同 CMID，服务端通过 CMID 去重，防止消息重复入库（幂等写入）。

这一机制保证了**至少一次投递（At-Least-Once Delivery）**语义，结合服务端去重达到**恰好一次（Exactly-Once）**的用户体验。

---

## 实际应用

**WhatsApp 的单服务器 200万连接实践**：WhatsApp 早期基于 Erlang 语言和 BEAM 虚拟机构建，利用 Erlang 轻量级进程（每进程约 300 字节内存）为每个 WebSocket 连接创建独立进程，实现单台服务器 200万并发连接，远超当时 Java/C++ 方案的典型值（约 10万～20万）。

**Discord 从 MongoDB 迁移到 Cassandra 再到 ScyllaDB**：Discord 在消息量达到 1亿条时，MongoDB 因 B-Tree 索引的随机写入导致 CPU spike。2017年迁移到 Cassandra 后，利用其 LSM-Tree 结构的顺序写入优化了写吞吐。2023年再次迁移到 ScyllaDB（Cassandra 的 C++ 重写版），将消息读取的 P99 延迟从 40ms 降至 15ms，同时将服务器数量从 177台减少到 72台。

**微信红包的消息顺序难题**：微信在2015年春晚期间处理了10.1亿次红包交互，其核心挑战是在高并发下保证红包"抢"操作的事务性与消息顺序性。技术方案是将同一红包的所有操作路由到同一 MySQL 分片（按红包ID取模），在单分片内用数据库事务保证强一致性，牺牲了跨分片的水平扩展换取操作的原子性。

---

## 常见误区

**误区1：以为 WebSocket 连接可以无限水平扩展而不需要路由层**

很多初学者认为增加 Chat Server 就能线性扩展。实际上，当用户 A 连接在 Server-1，用户 B 连接在 Server-2 时，A 发给 B 的消息无法直接投递。必须引入**消息路由层**，通常是 Redis Pub/Sub 或 Kafka：Server-1 将消息发布到 `channel:{user_B_id}` 主题，Server-2 订阅该主题后投递给 B。忽略路由层会导致跨服务器消息丢失，这是聊天系统设计中最常见的架构缺陷。

**误区2：在线状态应该实时同步给所有好友**

直觉上，用户上线应立即通知所有好友。但若用户有 3000 个好友（LinkedIn 常见情况），每次上下线产生 3000 条 Presence 事件，系统中有 100万 用户频繁切换网络时，Presence 服务会成为瓶颈。正确做法是**懒加载+TTL缓存**：只在好友打开聊天窗口时拉取一次状态，并缓存 30秒，避免对每次心跳都进行全量推送。

**误区3：单聊和群聊可以用同一套存储和推送逻辑**

单聊消息量小、参与方固定（2人），可以用写扩散+强一致存储（如 MySQL）；群聊尤其是万人大群，写扩散会产生万倍写放大，且群成员在线率通常低于 10%，大量写入